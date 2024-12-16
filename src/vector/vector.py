import os
import faiss
import numpy as np

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from langchain_core.embeddings import Embeddings
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma, FAISS, PGVector, Pinecone


@dataclass
class EmbeddingVector:
    """Represents an embedding vector with its metadata."""
    id: str
    vector: list[float]
    metadata: dict[str, Any]
    text: str


@dataclass
class SearchResult:
    """Represents a search result from the vector store."""
    text: str
    metadata: dict[str, Any]
    score: float
    vector_id: str


class VectorStoreType(Enum):
    """
    Enum for the type of vector store.
    """
    CHROMA = auto()
    PGVECTOR = auto()
    FAISS = auto()
    PINECONE = auto()


@dataclass
class VectorStoreConfig:
    """
    Configuration for a vector store.
    """
    store_type: VectorStoreType
    connection_params: dict[str, Any]
    embedding_model: Optional[Embeddings] = None

    def __post_init__(self):
        if self.embedding_model is None:
            self.embedding_model = OpenAIEmbeddings()


class VectorStore(ABC):
    """
    Abstract base class for a vector store.
    """

    @abstractmethod
    def add_vectors(self, vectors: list[EmbeddingVector]) -> None:
        """Add vectors to the vector store."""
        pass

    @abstractmethod
    def query(self, query_vector: list[float], k: int = 10, filter: Optional[dict] = None) -> list[SearchResult]:
        """Query the vector store."""
        pass

    @abstractmethod
    def delete(self, ids: list[str]) -> None:
        """Delete vectors from the vector store."""
        pass

    @abstractmethod
    def clear(self) -> None:
        """Clear all vectors from the store."""
        pass


class ChromaVectorStore(VectorStore):
    """
    Vector store using Chroma.
    """

    def __init__(self, persist_dir: str, embedding_model: Optional[Embeddings] = None):
        self.persist_dir = persist_dir
        self.embedding_model = embedding_model or OpenAIEmbeddings()
        self.store = Chroma(persist_directory=persist_dir,
                            embedding_function=self.embedding_model)

    def add_vectors(self, vectors: list[EmbeddingVector]) -> None:
        """Add vectors to the Chroma store."""
        try:
            documents = [v.text for v in vectors]
            metadatas = [v.metadata for v in vectors]
            embeddings = [v.vector for v in vectors]
            ids = [v.id for v in vectors]

            self.store.add_documents(
                documents=documents,
                metadatas=metadatas,
                embeddings=embeddings,
                ids=ids
            )
        except Exception as e:
            raise RuntimeError(f"Failed to add vectors to Chroma: {e}")

    def clear(self) -> None:
        """Clear all vectors from the Chroma store."""
        try:
            self.store.delete_collection()
        except Exception as e:
            raise RuntimeError(f"Failed to clear Chroma store: {e}")

    def delete(self, ids: list[str]) -> None:
        """Delete vectors from the Chroma store."""
        try:
            self.store.delete(ids)
        except Exception as e:
            raise RuntimeError(f"Failed to delete vectors from Chroma: {e}")


class FAISSVectorStore(VectorStore):
    """
    Vector store using FAISS.
    """

    def __init__(self, dimension: int, index_path: str, embedding_model: Optional[Embeddings] = None) -> None:
        self.dimension = dimension
        self.index_path = index_path
        self.embedding_model = embedding_model or OpenAIEmbeddings()

        self.index = faiss.IndexFlatL2(dimension)
        self.id_map: dict[str, int] = {}
        self.vectors: list[EmbeddingVector] = []
        self.__load_index()

    def query(self, query_vector: list[float], k: int = 10, filter: Optional[dict] = None) -> list[SearchResult]:
        """Query the FAISS store and return the top k results."""
        try:

            query_arr = np.array([query_vector], dtype=np.float32)
            distances, indices = self.index.search(query_arr, k)

            results = []
            for distance, idx in zip(distances[0], indices[0]):
                if idx < 0 or idx >= len(self.vectors):
                    continue

                vector = self.vectors[idx]

                results.append(SearchResult(
                    text=vector.text,
                    metadata=vector.metadata,
                    score=float(distance),
                    vector_id=vector.id
                ))

            return results
        except Exception as e:
            raise RuntimeError(f"Failed to query FAISS: {str(e)}") from e

    def __load_index(self) -> None:
        """Load the FAISS index from disk if it exists."""
        try:
            if os.path.exists(self.index_path):
                self.index = faiss.read_index(self.index_path)
        except Exception as e:
            print(f"Warning: Failed to load FAISS index: {e}")

    def __save_index(self) -> None:
        """Save the FAISS index to disk."""
        try:
            faiss.write_index(self.index, self.index_path)
        except Exception as e:
            print(f"Warning: Failed to save FAISS index: {e}")

    def add_vectors(self, vectors: list[EmbeddingVector]) -> None:
        """Add vectors to the FAISS store."""
        try:
            if not vectors:
                return

            vec_arr = np.array(
                [v.vector for v in vectors], dtype=np.float32)

            start_idx = len(self.vectors)
            self.index.add(vec_arr)

            for i, vector in enumerate(vectors):
                self.id_map[vector.id] = start_idx + i
                self.vectors.append(vector)

            self.__save_index()

        except Exception as e:
            raise RuntimeError(f"Failed to add vectors to FAISS: {e}")

    def delete(self, ids: list[str]) -> None:
        """Delete vectors from the FAISS store."""
        try:
            indices_to_delete = [self.id_map[id] for id in ids]
            if not indices_to_delete:
                return

            new_vectors = []
            new_id_map = {}

            for i, vector in enumerate(self.vectors):
                if i not in indices_to_delete:
                    new_id_map[vector.id] = len(new_vectors)
                    new_vectors.append(vector)

            # Rebuild the index with the new vectors
            self.index = faiss.IndexFlatL2(self.dimension)
            if new_vectors:
                vectors_array = np.array(
                    [v.vector for v in new_vectors], dtype=np.float32)
                self.index.add(vectors_array)

            self.vectors = new_vectors
            self.id_map = new_id_map

            self.__save_index()

        except Exception as e:
            raise RuntimeError(f"Failed to delete vectors from FAISS: {e}")

    def clear(self) -> None:
        """Clear all vectors from the FAISS store."""
        try:
            self.index = faiss.IndexFlatL2(self.dimension)
            self.id_map = {}
            self.vectors = []
            self.__save_index()
        except Exception as e:
            raise RuntimeError(f"Failed to clear FAISS store: {e}")


class PGVectorStore(VectorStore):
    """
    Vector store using PGVector.
    """

    def __init__(self, connection_str: str, table_name: str = "embeddings", embedding_model: Optional[Embeddings] = None):
        self.connection_str = connection_str
        self.table_name = table_name
        self.embedding_model = embedding_model or OpenAIEmbeddings()

        self.engine = create_engine(connection_str)
        self.session = sessionmaker(bind=self.engine)

        with self.engine.connect() as conn:

            # create table if not exists
            conn.execute(f"""
                CREATE TABLE IF NOT EXISTS {self.table_name} (
                    id TEXT PRIMARY KEY,
                    vector vector({self.embedding_model.dimension}),
                    text TEXT,
                    metadata JSONB,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.execute(f"""
                CREATE INDEX IF NOT EXISTS {self.table_name}_vector_idx
                ON {self.table_name}
                USING ivfflat (vector vector_cosine_ops)
            """)

    def _initialize_store(self) -> PGVector:
        return PGVector(embedding=self.config.embedding_model)