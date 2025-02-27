from abc import ABC, abstractmethod
from typing import Any
from langchain_core.documents import Document

from abc import ABC, abstractmethod
from typing import Any, Optional
from langchain_core.documents import Document


class BaseVectorStore(ABC):
    """Abstract base class for all vector store implementations."""

    @abstractmethod
    async def add_documents(self, documents: list[Document]) -> list[str]:
        """Add documents to the vector store."""
        pass

    @abstractmethod
    async def similarity_search(self,
                                query: str,
                                k: int = 4,
                                filter: Optional[dict[str, Any]] = None) -> list[Document]:
        """Search for documents similar to the query string."""
        pass

    @abstractmethod
    async def similarity_search_with_score(self,
                                           query: str,
                                           k: int = 4,
                                           filter: Optional[dict[str, Any]] = None) -> list[tuple[Document, float]]:
        """Search for documents with similarity scores."""
        pass

    @abstractmethod
    async def delete(self, ids: list[str]) -> None:
        """Delete documents by ID."""
        pass

    @abstractmethod
    async def clear(self) -> None:
        """Clear all documents from the store."""
        pass

    @abstractmethod
    async def persist(self) -> None:
        """Persist the vector store to disk if applicable."""
        pass

    @abstractmethod
    async def get_stats(self) -> dict[str, Any]:
        """Get statistics about the vector store."""
        pass


class VectorStoreRegistry:
    """Registry for vector store implementations."""

    _implementations = {}

    @classmethod
    def register(cls, name: str):
        """Register a vector store implementation."""
        def decorator(store_class):
            cls._implementations[name] = store_class
            return store_class
        return decorator

    @classmethod
    def get_implementation(cls, name: str):
        """Get a vector store implementation by name."""
        if name not in cls._implementations:
            raise ValueError(
                f"Vector store implementation '{name}' not found.")
        return cls._implementations[name]

    @classmethod
    def list_implementations(cls):
        """List all registered implementations."""
        return list(cls._implementations.keys())
