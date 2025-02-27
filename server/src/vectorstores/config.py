from enum import Enum
from typing import Optional
from langchain_core.embeddings import Embeddings
from pydantic import BaseModel
from .base import BaseVectorStore
from .faiss_store import FAISSVectorStore


class VectorStoreType(str, Enum):
    FAISS = "faiss"
    CHROMA = "chroma"
    WEAVIATE = "weaviate"
    PINECONE = "pinecone"
    QDRANT = "qdrant"
    REDIS = "redis"
    MILVUS = "milvus"
    ELASTICSEARCH = "elasticsearch"

    @classmethod
    def list_types(cls):
        return [t.value for t in cls]

    @classmethod
    def from_string(cls, value: str):
        try:
            return cls(value)
        except ValueError:
            raise ValueError(f"Invalid vector store type: {value}")


class CreateVectorStoreConfig(BaseModel):
    store_type: VectorStoreType
    store_path: Optional[str] = None
    embedding_model: Optional[str] = None


def create_vector_store(
    config: CreateVectorStoreConfig,
) -> BaseVectorStore:
    if config.store_type == VectorStoreType.FAISS:
        return FAISSVectorStore(
            store_path=config.store_path,
        )
    else:
        raise ValueError(f"Unsupported vector store type: {config.store_type}")
