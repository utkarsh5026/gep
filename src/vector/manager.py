import time
from typing import Optional


from .embedding import EmbeddingProvider
from .vector import VectorStore, EmbeddingVector, SearchResult


class EmbeddingManager:
    """
    Manages the coordination between vector stores and embedding providers.
    """

    def __init__(self, embedding_provider: EmbeddingProvider, vector_store: VectorStore, batch_size: int = 100) -> None:
        """
        Initialize the embedding manager.

        Parameters:
            embedding_provider (EmbeddingProvider): The embedding provider to use.
            vector_store (VectorStore): The vector store to use.
            batch_size (int): The batch size for embedding.
        """
        self.embedding_provider = embedding_provider
        self.batch_size = batch_size
        self.vector_store = vector_store

    async def add_texts(self, texts: list[str], metadatas: Optional[list[dict]] = None) -> None:
        """
        Add texts to the vector store.
        """

        try:
            embeddings = await self.embedding_provider.embed_documents(texts)
            vectors = []

            for i, (text, embedding) in enumerate(zip(texts, embeddings)):
                md = metadatas[i] if metadatas else {}
                vector = EmbeddingVector(
                    id=f"vector_{time.time()}_{i}",
                    vector=embedding,
                    metadata=md,
                    text=text,
                )

                vectors.append(vector)

            await self.vector_store.add_vectors(vectors)
        except Exception as e:
            print(f"Error adding texts to vector store: {e}")
            raise e

    async def delete_vectors(self, ids: list[str]) -> None:
        """
        Delete vectors from the vector store.
        """
        await self.vector_store.delete(ids)

    async def similarity_search(self, query: str, limit: int = 10, filter: Optional[dict] = None) -> list[SearchResult]:
        """
        Perform a similarity search on the vector store.
        """

        try:
            query_embedding = await self.embedding_provider.embed_query(query)
            return await self.vector_store.query(
                query_vector=query_embedding,
                k=limit,
                filter=filter,
            )
        except Exception as e:
            print(f"Error performing similarity search: {e}")
            raise e
