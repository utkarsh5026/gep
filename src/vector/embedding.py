from abc import ABC, abstractmethod
from typing import Optional
from enum import Enum, auto

import logging
import asyncio

from langchain_openai import OpenAIEmbeddings
from tenacity import retry, stop_after_attempt, wait_exponential

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmbeddingProviderType(Enum):
    OPENAI = "openai"
    CLAUDE = "claude"
    GEMINI = "gemini"
    COHERE = "cohere"


class EmbeddingProviderConfig:
    """
    Configuration for embeddings.
    """

    def __init__(self, model_name: str, api_key: Optional[str] = None, batch_size: int = 100, **kwargs) -> None:
        self.model_name = model_name
        self.api_key = api_key
        self.batch_size = batch_size
        self.extra_config = kwargs


class EmbeddingProvider(ABC):
    """
    Abstract base class for embedding providers.
    """

    def __init__(self, config: EmbeddingProviderConfig) -> None:
        self.config = config

    @abstractmethod
    async def embed_documents(self, documents: list[str]) -> list[list[float]]:
        """
        Embed a list of documents.
        """
        pass

    @abstractmethod
    async def embed_query(self, query: str) -> list[float]:
        """
        Embed a single query.
        """
        pass


class OpenAIEmbeddingProvider(EmbeddingProvider):
    """
    OpenAI embedding provider.
    """

    def __init__(self, config: EmbeddingProviderConfig) -> None:
        super().__init__(config)
        self.client = OpenAIEmbeddings(
            model=config.model_name,
            openai_api_key=config.api_key,
            **config.extra_config,
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
    )
    async def embed_documents(self, documents: list[str]) -> list[list[float]]:
        """
        Embed a list of documents.
        """
        batch_size = self.config.batch_size
        all_embeddings = []
        try:
            for i in range(0, len(documents), batch_size):
                batch = documents[i: i + batch_size]
                embeddings = await self.client.aembed_documents(batch)
                all_embeddings.extend(embeddings)

                if i + batch_size < len(documents):
                    await asyncio.sleep(0.1)

        except Exception as e:
            logger.error(f"Error embedding documents: {e}")
            raise e

        return all_embeddings

    async def embed_query(self, text: str) -> list[float]:
        """
        Embed a single query.
        """
        try:
            return await self.client.aembed_query(text)
        except Exception as e:
            logger.error(f"Error generating query embedding: {str(e)}")
            raise


def create_embedding_provider(provider_type: EmbeddingProviderType,
                              config: EmbeddingProviderConfig) -> EmbeddingProvider:
    """
    Create an embedding provider.
    """
    if provider_type == EmbeddingProviderType.OPENAI:
        return OpenAIEmbeddingProvider(config)
    else:
        raise ValueError(f"Invalid embedding provider type: {provider_type}")
