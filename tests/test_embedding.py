import pytest
import os
from src.vector.embedding import (
    EmbeddingConfig,
    OpenAIEmbeddingProvider,
    create_embedding_provider,
    EmbeddingProviderType,
)
from dotenv import load_dotenv

load_dotenv()


@pytest.mark.asyncio
async def test_openai_embedding_provider():
    api_key = os.getenv("OPENAI_API_KEY")
    config = EmbeddingConfig(
        model_name="text-embedding-ada-002",  # OpenAI's standard embedding model
        api_key=api_key,
        batch_size=10
    )

    provider = create_embedding_provider(EmbeddingProviderType.OPENAI, config)

    assert isinstance(provider, OpenAIEmbeddingProvider)
    documents = [
        "This is a test document",
        "This is another test document",
        "And a third test document"
    ]

    embeddings = await provider.embed_documents(documents)
    assert len(embeddings) == len(documents)
    assert all(isinstance(embedding, list) for embedding in embeddings)
    assert all(isinstance(value, float)
               for embedding in embeddings for value in embedding)

    query = "test query"
    query_embedding = await provider.embed_query(query)

    assert isinstance(query_embedding, list)
    assert all(isinstance(value, float) for value in query_embedding)
