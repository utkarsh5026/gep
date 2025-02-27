from langchain_community.document_loaders import (
    TextLoader,
    CSVLoader,
    JSONLoader,
    PyPDFLoader,
    UnstructuredHTMLLoader,
    UnstructuredMarkdownLoader
)
from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
    MarkdownTextSplitter,
    Language
)

from .models import FileInfo


def get_appropriate_loader(file_info: FileInfo):
    """Select the appropriate document loader based on file extension."""
    file_path = file_info.rel_file_path
    extension = file_info.extension

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
        else:
            return loader_class(file_path)
    except Exception as e:
        print(f"Error creating loader for {file_path}: {e}")
        try:
            return TextLoader(file_path, encoding='utf-8')
        except:
            return None


def get_chunking_strategy(file_info: FileInfo):
    """Return appropriate chunking strategy based on file extension."""
    extension = file_info.extension

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
