import asyncio
import logging
import time
import aiofiles
import hashlib
import pathlib
from dataclasses import dataclass, field

from .manager import EmbeddingManager
from watcher import AsyncFileWatcher, default_ignore_patterns, FileEvent, EventType
from langchain_text_splitters import RecursiveCharacterTextSplitter


@dataclass
class FileMetadata:
    """
    Metadata for a file.
    """
    file_path: str
    last_modified: float
    content_hash: str
    vector_ids: list[str]
    chunks: list[str]
    is_processed: bool = False


@dataclass
class FileManagerConfig:
    """
    Configuration for the FileManager.
    """

    batch_size: int = 10
    ignored_patterns: list[str] = field(
        default_factory=lambda: default_ignore_patterns)


class FileManager:
    """
    Manages file changes and updates embeddings accordingly.
    Coordinates between FileWatcher, FileProcessor, and EmbeddingManager.
    """

    def __init__(self, root_path: str, config: FileManagerConfig, embedding_manager: EmbeddingManager) -> None:
        self.root_path = pathlib.Path(root_path).resolve()
        self.config = config

        self.file_watcher = AsyncFileWatcher(
            root_path=str(self.root_path),
            ignored_patterns=self.config.ignored_patterns,
        )
        self.embedding_manager = embedding_manager

        self.processed_files: dict[str, FileMetadata] = {}
        self._process_lock = asyncio.Lock()
        self.is_running = False
        self.batch_queue: asyncio.Queue[str] = asyncio.Queue(maxsize=1000)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=200)

    async def __handle_file_event(self, event: FileEvent) -> None:
        """
        Handle a file event.
        """

        try:
            ev_type = event.event_type
            if ev_type == EventType.FILE_DELETED:
                if event.path in self.processed_files:
                    file_info = self.processed_files[event.path]

                    print(f"File deleted: {event.path}")
                    del self.processed_files[event.path]

            else:
                await self.batch_queue.put(event)
                logger.info(f"Queued file event: {event.path}")

        except Exception as e:
            logger.error(f"Error handling file event: {e}")

    async def start(self) -> None:

        if self.is_running:
            raise RuntimeError("File manager is already running")

        self.is_running = True
        try:
            await self.file_watcher.watch()
            await asyncio.create_task(self.__batch_processor())

            await self.__process_existing_files()

            async for event in self.file_watcher.get_event():
                await self.__handle_file_event(event)

        except Exception as e:
            logger.error(f"Error starting file manager: {e}")
            self.is_running = False

    async def stop(self) -> None:
        """
        Stop the system and clean up resources.
        """
        logger.info("Stopping integrated embedding manager...")
        self.is_running = False

        try:
            await self.file_watcher.stop()

            while not self.batch_queue.empty():
                file_path = await self.batch_queue.get()
                await self.__process_file(file_path)

            await self.batch_queue.join()
            logger.info("File manager stopped successfully")
        except Exception as e:
            logger.error(f"Error stopping file manager: {e}")

    async def __process_existing_files(self) -> None:
        """
        Process existing files.
        """
        logger.info("Processing existing files...")
        for file_path in self.root_path.rglob("*"):
            if file_path.is_file():
                await self.batch_queue.put(str(file_path))

    async def __batch_processor(self) -> None:
        """
        Processes the batch queue
        """

        while self.is_running:
            try:
                batch: list[str] = []

                while len(batch) < self.config.batch_size:
                    try:
                        file_path = await asyncio.wait_for(self.batch_queue.get(), timeout=1.0)
                        batch.append(file_path)
                    except asyncio.TimeoutError:
                        break

                if batch:
                    await asyncio.gather(*(self.__process_file(file_path) for file_path in batch))

            except Exception as e:
                logger.error(f"Error processing batch: {e}")
                await asyncio.sleep(1.0)

    @staticmethod
    async def __read_file(file_path: str) -> str:
        """
        Read a file.
        """
        async with aiofiles.open(file_path, "r", encoding="utf-8") as file:
            return await file.read()

    @staticmethod
    def __hash_content(content: str) -> str:
        """
        Hash the content of a file.
        """
        return hashlib.sha256(content.encode()).hexdigest()

    async def __process_file(self, file_path: str) -> None:
        """
        Process a single file, generating and storing its embeddings.
        Uses a lock to prevent concurrent processing of the same file.
        """

        async with self._process_lock:
            if file_path in self.processed_files:
                if self.processed_files[file_path].is_processed:
                    logger.info(f"File already processed: {file_path}")
                    return

            try:
                file_info = FileMetadata(
                    file_path=file_path,
                    last_modified=time.time(),
                    content_hash="",
                    is_processed=True,
                )

                content = await self.__read_file(file_path)
                content_hash = self.__hash_content(content)

                if (file_path in self.processed_files and
                        self.processed_files[file_path].content_hash == content_hash):
                    logger.debug(
                        f"File {file_path} content unchanged, skipping")
                    return

                vector_ids = await self.__embed(content, file_info)
                file_info.vector_ids = vector_ids
                file_info.content_hash = content_hash
                file_info.is_processed = False
                self.processed_files[file_path] = file_info

            except Exception as e:
                logger.error(f"Error processing file {file_path}: {e}")
                if file_path in self.processed_files:
                    del self.processed_files[file_path]

    def __chunk_content(self, content: str) -> list[str]:
        """
        Split the content of a file into chunks.
        """
        try:
            return self.text_splitter.split_text(content)
        except Exception as e:
            logger.error(f"Error splitting content: {e}")
            return [content]

    async def __embed(self, file_content: str, metadata: FileMetadata) -> list[str]:
        """
        Embed the content of a file and store the embeddings.
        """
        chunks = self.__chunk_content(file_content)
        file_path = metadata.file_path
        chunks_metadata = [{
            "source": file_path,
            "chunk_idx": i,
            "total_chunks": len(chunks),
            "timestamp": time.time(),
            "file_type": pathlib.Path(file_path).suffix,
            "relative_path": str(pathlib.Path(file_path).relative_to(self.root_path))
        } for i, chunk in enumerate(chunks)]

        if file_path in self.processed_files:
            old_vectors = self.processed_files[file_path].vector_ids
            if old_vectors:
                await self.embedding_manager.delete_vectors(old_vectors)

        return await self.embedding_manager.add_vectors(chunks, chunks_metadata)
