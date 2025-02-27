from loguru import logger
from langchain_community.document_loaders import (
    TextLoader,
    CSVLoader,
    JSONLoader,
    PyPDFLoader,
    UnstructuredHTMLLoader,
    UnstructuredMarkdownLoader
)
from langchain_community.document_loaders.base import BaseLoader
from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
    MarkdownTextSplitter,
    Language
)
from langchain_core.documents import Document

from .models import FileInfo


class FileLoader:
    def __init__(self, file_info: FileInfo):
        """
        Initialize the FileLoader with the given FileInfo

        Args:
            file_info (FileInfo): The FileInfo object containing the file information
        """
        self.file_info = file_info

    def load(self) -> list[Document]:
        """
        Load the file and return the chunks
        """
        loader = self.get_appropriate_loader()
        if not loader:
            raise ValueError(
                f"No loader found for file {self.file_info.file_path} {self.file_info.extension}"
            )

        docs = loader.load()
        for doc in docs:
            doc.metadata.update({
                "file_name": self.file_info.name,
                "rel_file_path": self.file_info.rel_file_path,
                "extension": self.file_info.extension,
                "file_size": self.file_info.size,
                "file_path": str(self.file_info.file_path),
            })

        text_splitter = self.get_chunking_strategy()
        chunks = text_splitter.split_documents(docs)
        return chunks

    def get_appropriate_loader(self) -> BaseLoader:
        """Select the appropriate document loader based on file extension."""
        file_path = str(self.file_info.file_path)
        extension = self.file_info.extension

        loaders = {
            '.py': TextLoader,
            '.js': TextLoader,
            '.jsx': TextLoader,
            '.ts': TextLoader,
            '.tsx': TextLoader,
            '.java': TextLoader,
            '.rb': TextLoader,
            '.go': TextLoader,
            '.php': TextLoader,
            '.c': TextLoader,
            '.cpp': TextLoader,
            '.cs': TextLoader,
            '.swift': TextLoader,
            '.kt': TextLoader,

            # Data files
            '.csv': CSVLoader,
            '.json': JSONLoader,

            # Document files
            '.md': UnstructuredMarkdownLoader,
            '.html': UnstructuredHTMLLoader,
            '.htm': UnstructuredHTMLLoader,
            '.pdf': PyPDFLoader,

            # Config files
            '.yaml': TextLoader,
            '.yml': TextLoader,
            '.toml': TextLoader,
            '.ini': TextLoader,
            '.cfg': TextLoader,

            # Default
            '': TextLoader
        }

        loader_class = loaders.get(extension, TextLoader)
        try:
            if loader_class == JSONLoader:
                return JSONLoader(file_path, jq_schema='.', text_content=False)
            elif loader_class == TextLoader:
                # Use utf-8 with error handling for text files
                return TextLoader(file_path, encoding='utf-8', autodetect_encoding=True)
            else:
                return loader_class(file_path)
        except Exception as e:
            logger.error(f"Error creating loader for {file_path}: {e}")
            try:
                # Fallback with more robust encoding handling
                return TextLoader(file_path, encoding='utf-8', errors='replace')
            except Exception as e2:
                logger.error(
                    f"Fallback loader also failed for {file_path}: {e2}")
                return None

    def get_chunking_strategy(self) -> RecursiveCharacterTextSplitter | MarkdownTextSplitter:
        """Return appropriate chunking strategy based on file extension."""
        extension = self.file_info.extension

        code_extensions = {
            '.py': Language.PYTHON,
            '.js': Language.JS,
            '.jsx': Language.JS,
            '.ts': Language.TS,
            '.tsx': Language.TS,
            '.java': Language.JAVA,
            '.go': Language.GO,
            '.rb': Language.RUBY,
            '.php': Language.PHP,
            '.cpp': Language.CPP,
            '.c': Language.CPP
        }

        if extension in code_extensions:
            language = code_extensions[extension]
            return RecursiveCharacterTextSplitter.from_language(
                language=language,
                chunk_size=1000,
                chunk_overlap=200
            )

        if extension in ['.md', '.markdown']:
            return MarkdownTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )

        return RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100,
            separators=["\n\n", "\n", " ", ""]
        )
