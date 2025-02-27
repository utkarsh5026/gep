import os
import uuid
from pathlib import Path
from typing import Callable
from loguru import logger


from .models import FileInfo
from .scan import RepoScanner
from .loader import FileLoader


from vectorstores import (
    create_vector_store,
    VectorStoreType,
    CreateVectorStoreConfig
)


class Project:

    PROJECT_DIR_NAME = ".gep"

    def __init__(self, repo_path: Path, vector_store_config: CreateVectorStoreConfig, update_callback: Callable[[str], None] | None = None):
        self._repo_path = repo_path
        self.repo_scanner = RepoScanner(repo_path)
        if not vector_store_config.store_path:
            vector_store_config.store_path = str(
                self.vector_db_path / "faiss_vector_store")

        self.vector_store = create_vector_store(vector_store_config)
        self.update_callback = update_callback if update_callback else lambda _: None

    @property
    def vector_db_path(self):
        return self._repo_path / self.PROJECT_DIR_NAME / "vector_db"

    async def vectorize(self):
        """
        Vectorize the project files and save them to the vector store.

        Args:
            status_callback: Optional callback function to report progress
        """

        self.update_callback("Scanning repository files...")
        repo_struct = await self.repo_scanner.scan()

        self.update_callback(f"Found {len(repo_struct)} files to process")
        await self._embed_proj_files(repo_struct)

        return f"Successfully vectorized {len(repo_struct)} files"

    @classmethod
    def prepare_structure_for_llm(cls, file_info: list[FileInfo]):
        """
        Prepare a user-friendly representation of the project structure for LLM processing.

        Args:
            file_info (list[FileInfo]): A list of FileInfo objects representing the files in the project.

        Returns:
            str: A formatted string that outlines the project structure, including directories and files.
                  The structure is represented in a hierarchical format, with indentation indicating 
                  the level of each directory. If a directory contains more than 10 files, only the 
                  first 5 and the last 4 files are shown, with an ellipsis in between to indicate 
                  omitted files.
        """
        files_by_directory = {}
        for file in file_info:
            dir_path = file.directory
            if dir_path not in files_by_directory:
                files_by_directory[dir_path] = []
            files_by_directory[dir_path].append(file.name)

        structure_text = ["# Project Structure\n"]
        sorted_dirs = sorted(files_by_directory.keys())
        for dir_path in sorted_dirs:
            if str(dir_path).count('/') > 4:
                continue

            indent = '  ' * str(dir_path).count('/')
            file_name = os.path.basename(dir_path) or 'root'
            structure_text.append(f"{indent}- {file_name}:")

            files = sorted(files_by_directory[dir_path])
            if len(files) > 10:
                shown_files = files[:5] + ["..."] + files[-4:]
            else:
                shown_files = files

            for file in shown_files:
                structure_text.append(f"{indent}  - {file}")

        return "\n".join(structure_text)

    async def _embed_proj_files(self, repo_files: list[FileInfo]):
        """
        Embed the project files and save them to the vector store.

        Args:
            repo_files: List of files to embed
        """
        if not self.vector_store:
            raise ValueError("Vector store not initialized")

        docs = []
        self.update_callback("Loading file contents...")

        for i, file in enumerate(repo_files):
            loader = FileLoader(file)
            file_docs = loader.load()
            docs.extend(file_docs)

            if i % 10 == 0:
                self.update_callback(
                    f"Loaded {i+1}/{len(repo_files)} files ({len(docs)} documents)")

        logger.info(f"Embedding {len(docs)} documents")
        self.update_callback(f"Embedding {len(docs)} documents...")

        # Track progress during embedding
        total_docs = len(docs)
        batch_size = 50  # Adjust based on your needs

        for i in range(0, total_docs, batch_size):
            end_idx = min(i + batch_size, total_docs)
            batch = docs[i:end_idx]

            self.update_callback(
                f"Embedding documents {i+1}-{end_idx} of {total_docs}...")

            await self.vector_store.add_documents(batch)

            progress_percent = int((end_idx / total_docs) * 100)
            self.update_callback(
                f"Embedding progress: {progress_percent}% ({end_idx}/{total_docs})")

        self.update_callback("Persisting vector store...")

        await self.vector_store.persist()

        self.update_callback(
            f"Vectorization complete! {total_docs} documents embedded.")

    async def search(self, query: str, limit: int = 10):
        """
        Search the project files for the given query
        """
        return await self.vector_store.similarity_search_with_score(query, k=limit)

    @classmethod
    async def find_root(cls):
        """
        Find the root directory of the project
            """
        current_dir = Path.cwd().resolve()
        while not (current_dir / ".git").exists():
            if current_dir == current_dir.parent:
                raise ValueError("No git repository found")
            current_dir = current_dir.parent
        return current_dir

    @classmethod
    async def find_root_and_init(cls, vector_store_config: CreateVectorStoreConfig, update_callback: Callable[[str], None] | None = None):
        """
        Find the root directory of the project and initialize the project
        """
        root_dir = await cls.find_root()
        logger.info(f"Found project root: {root_dir}")
        Path(root_dir / cls.PROJECT_DIR_NAME).mkdir(parents=True, exist_ok=True)
        return cls(root_dir, vector_store_config, update_callback)

    @classmethod
    async def load(cls, update_callback: Callable[[str], None] | None = None):
        """
        Load the project from the given path
        """
        root = await cls.find_root()
        vector_store_config = CreateVectorStoreConfig(
            store_type=VectorStoreType.FAISS,
            store_path=str(root / cls.PROJECT_DIR_NAME / "faiss_vector_store"),
        )
        return cls(root, vector_store_config, update_callback)
