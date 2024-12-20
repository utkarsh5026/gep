from typing import Optional, Any
from pydantic import BaseModel
from pathlib import Path

from vector import EmbeddingProviderType, VectorStoreType
from query import LLMType


class EmbeddingConfig(BaseModel):
    """Configuration for embeddings"""
    embedding_type: EmbeddingProviderType
    model_name: str
    batch_size: int = 100
    dimension: int = 1536
    additional_params: Optional[dict[str, Any]] = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]):
        return cls(
            embedding_type=EmbeddingProviderType(
                data.get('embedding_type', 'openai')),
            model_name=data.get('model_name', 'openai'),
            batch_size=data.get('batch_size', 100),
            dimension=data.get('dimension', 1536),
            additional_params=data.get('additional_params', None)
        )


class LLMConfig(BaseModel):
    """Configuration for LLM"""
    llm_type: LLMType
    model_name: str
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    additional_params: Optional[dict[str, Any]] = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]):
        return cls(
            llm_type=LLMType(data.get('llm_type', 'openai')),
            model_name=data.get('model_name', 'openai'),
            temperature=data.get('temperature', 0.7),
            max_tokens=data.get('max_tokens', None),
            top_p=data.get('top_p', 1.0),
            frequency_penalty=data.get('frequency_penalty', 0.0),
            presence_penalty=data.get('presence_penalty', 0.0),
            additional_params=data.get('additional_params', None)
        )


class VectorConfig(BaseModel):
    """Configuration for vector store"""
    store_type: VectorStoreType
    persist_dir: Path
    dimension: int = 1536
    additional_params: Optional[dict[str, Any]] = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]):
        return cls(
            store_type=VectorStoreType(data.get('store_type', 'faiss')),
            persist_dir=Path(data.get('persist_dir', './vector_store')),
            dimension=data.get('dimension', 1536),
            additional_params=data.get('additional_params', None)
        )


class ProjectConfig(BaseModel):
    """Configuration for a project"""

    root_dir: Path
    emb_config: EmbeddingConfig
    llm_config: LLMConfig
    vector_config: VectorConfig
    ignore_patterns: list[str] = []
    accepted_patterns: list[str] = []

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'ProjectConfig':
        return cls(
            root_dir=Path(data['root_dir']),
            emb_config=EmbeddingConfig.from_dict(
                data['embedding_config']),
            vector_config=VectorConfig.from_dict(data['vector_config']),
            llm_config=LLMConfig.from_dict(data['llm_config']),
            ignore_patterns=data.get('ignore_patterns', [])
        )


def sample_config() -> str:
    """Creates a sample YAML configuration with detailed descriptions for all parameters"""
    return """# Sample Configuration File with Descriptions

# Root directory of your project
root_dir: "./project"

# Embedding Configuration
embedding_config:
  # Type of embedding provider to use (options: openai, huggingface, cohere)
  embedding_type: "openai"
  
  # Name of the embedding model to use
  # - For OpenAI: "text-embedding-ada-002"
  # - For HuggingFace: Model name from HuggingFace hub
  model_name: "text-embedding-ada-002"
  
  # Number of items to process in a single batch
  batch_size: 100
  
  # Dimension of the embedding vectors
  dimension: 1536
  
  # Additional parameters specific to the embedding provider
  additional_params:
    # Add any provider-specific parameters here
    # key: value

# LLM (Language Model) Configuration
llm_config:
  # Type of LLM provider (options: openai, anthropic, huggingface)
  llm_type: "openai"
  
  # Name of the LLM model to use
  # - For OpenAI: "gpt-4", "gpt-3.5-turbo"
  # - For Anthropic: "claude-2", "claude-instant-1"
  model_name: "gpt-4"
  
  # Controls randomness in the output (0.0 to 1.0)
  # Lower values make the output more focused and deterministic
  temperature: 0.7
  
  # Maximum number of tokens in the response (optional)
  max_tokens: 1000
  
  # Controls diversity via nucleus sampling (0.0 to 1.0)
  top_p: 1.0
  
  # Reduces repetition of token sequences (-2.0 to 2.0)
  frequency_penalty: 0.0
  
  # Controls topic focus vs exploration (-2.0 to 2.0)
  presence_penalty: 0.0
  
  # Additional parameters specific to the LLM provider
  additional_params:
    # Add any provider-specific parameters here
    # key: value

# Vector Store Configuration
vector_config:
  # Type of vector store (options: faiss, chroma, pinecone)
  store_type: "faiss"
  
  # Directory to persist vector store
  persist_dir: "./vector_store"
  
  # Dimension of vectors to store (should match embedding dimension)
  dimension: 1536
  
  # Additional parameters specific to the vector store
  additional_params:
    # Add any vector store-specific parameters here
    # key: value

# Patterns to ignore during processing (glob patterns)
ignore_patterns:
  - "**/.git/**"
  - "**/node_modules/**"
  - "**/__pycache__/**"
  - "**/.env"

# Patterns to specifically include during processing (glob patterns)
accepted_patterns:
  - "**/*.py"
  - "**/*.js"
  - "**/*.java"
"""


def create_sample_config_file(file_path: Optional[str]) -> None:
    """
    Creates a sample configuration file at the given path
    """
    if file_path is None:
        file_path = Path.cwd() / 'config.yaml'

    with open(file_path, "w") as f:
        f.write(sample_config())
