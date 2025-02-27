from abc import ABC, abstractmethod
from typing import Any, Literal, Optional
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
                                filter: Optional[dict[str, Any]] = None) -> list[tuple[Document, float]]:
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

    @property
    def score_range(self) -> tuple[float, float]:
        """
        Return the theoretical min and max values for the similarity score.
        For example, cosine similarity typically ranges from -1 to 1.
        """
        return (0.0, 1.0)

    @property
    def similarity_metric(self) -> Literal["cosine", "l2", "dot_product", "custom"]:
        """
        Return the similarity metric used by this vector store.
        Should be one of: "cosine", "l2", "dot_product", or "custom"
        """
        return "custom"

    def normalize_score(self, raw_score: float) -> float:
        """
        Normalize the raw similarity score to a standard 0-100 scale where
        higher values always indicate better matches.

        Args:
            raw_score: The raw similarity score from the vector store

        Returns:
            Normalized score on a 0-100 scale (higher is better)
        """

        metric = self.similarity_metric
        min_score, max_score = self.score_range

        if metric == "cosine":
            # Cosine similarity: -1 to 1, higher is better
            # Scale to 0-100
            return ((raw_score - min_score) / (max_score - min_score)) * 100

        elif metric == "l2" or metric == "euclidean":
            # L2 distance: 0 to theoretically infinity, lower is better
            # Typical values are in the 0-2 range for normalized vectors
            # Invert and scale to 0-100
            max_typical_distance = 2.0
            inverted = max(0, 1 - (raw_score / max_typical_distance))
            return inverted * 100

        elif metric == "dot_product":
            # Dot product: varies based on vector magnitudes, higher is better
            # Assume typical range based on embedding model
            typical_max = max_score or 1.0
            return min(100, max(0, (raw_score / typical_max) * 100))

        else:  # custom
            # For custom metrics, subclasses should override this method
            return raw_score * 100


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
