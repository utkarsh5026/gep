import asyncio
from pathlib import Path
from typing import Any, Optional

from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

from .base import BaseVectorStore, VectorStoreRegistry


@VectorStoreRegistry.register("faiss")
class FAISSVectorStore(BaseVectorStore):
    """Vector store using FAISS."""

    def __init__(self,
                 store_path: str,
                 embedding_model: Optional[Embeddings] = None,
                 **kwargs):
        """Initialize the FAISS vector store."""

        self.embedding_model = embedding_model or OpenAIEmbeddings()
        self.store_path = Path(store_path)
        self.store_path.parent.mkdir(parents=True, exist_ok=True)
        self.kwargs = kwargs
        self.store: Optional[FAISS] = None

    async def _ensure_store_loaded(self):
        """Ensure the store is loaded."""
        if self.store is not None:
            return

        if self.store_path.exists():
            load_path = str(self.store_path)
            self.store = await FAISS.aload_local(load_path, self.embedding_model)

        else:
            dummy_doc = [
                Document(
                    page_content="initialization document",
                    metadata={"dummy": True})
            ]
            self.store = await FAISS.afrom_documents(dummy_doc, self.embedding_model)
            if hasattr(self.store, "delete") and hasattr(self.store, "index_to_docstore_id"):
                dummy_id = list(self.store.index_to_docstore_id.values())[0]
                await self.store.adelete(ids=[dummy_id])

    async def similarity_search_with_score(self, query: str, k: int = 4, filter: dict[str, Any] | None = None) -> list[tuple[Document, float]]:
        """Search for documents similar to the query string."""
        await self._ensure_store_loaded()
        return await self.store.asimilarity_search_with_score(query, k=k, filter=filter)

    async def add_documents(self, documents: list[Document]) -> list[str]:
        """Add documents to the vector store."""
        await self._ensure_store_loaded()
        return await self.store.aadd_documents(documents)

    async def delete(self, ids: list[str]) -> None:
        """Delete documents by ID."""
        await self._ensure_store_loaded()
        await self.store.adelete(ids=ids)

    async def persist(self) -> None:
        """Persist the vector store to disk."""
        await self._ensure_store_loaded()
        await asyncio.to_thread(self.store.save_local, str(self.store_path))

    async def clear(self) -> None:
        """Clear all documents from the store."""
        await self._ensure_store_loaded()
        await self.store.aclose()
        self.store = None

    async def get_stats(self) -> dict[str, Any]:
        """Get statistics about the vector store."""
        await self._ensure_store_loaded()
        return {
            "type": "faiss",
            "document_count": len(self.store.index_to_docstore_id) if hasattr(self.store, "index_to_docstore_id") else 0,
            "dimension": self.store.index.d if hasattr(self.store, "index") and hasattr(self.store.index, "d") else None,
            "path": str(self.store_path)
        }

    async def similarity_search(self,
                                query: str,
                                k: int = 4,
                                filter: Optional[dict[str, Any]] = None) -> list[Document]:
        """Search for documents similar to the query string."""
        await self._ensure_store_loaded()
        return await self.store.asimilarity_search(query, k=k, filter=filter)
