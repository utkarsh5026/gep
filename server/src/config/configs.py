from typing import Optional, Any, ClassVar
from pydantic import BaseModel, Field, field_validator, ValidationInfo
from pathlib import Path

from vector import EmbeddingProviderType, VectorStoreType
from query import LLMType
from file_utils import write_file


class ConfigError(Exception):
    """Base exception for configuration errors"""
    pass


class ConfigValidationError(ConfigError):
    """Raised when configuration validation fails"""
    pass


class EmbeddingConfig(BaseModel):
    """Configuration for embeddings"""

    DEFAULT_BATCH_SIZE: ClassVar[int] = 100
    DEFAULT_DIMENSION: ClassVar[int] = 1536
    MIN_BATCH_SIZE: ClassVar[int] = 1
    MAX_BATCH_SIZE: ClassVar[int] = 2048

    embedding_type: EmbeddingProviderType
    model_name: str
    batch_size: int = Field(default=DEFAULT_BATCH_SIZE,
                            ge=MIN_BATCH_SIZE, le=MAX_BATCH_SIZE)
    dimension: int = Field(default=DEFAULT_DIMENSION, ge=0)
    additional_params: Optional[dict[str, Any]] = None

    @classmethod
    @field_validator('model_name', mode='after')
    def validate_model_name(cls, v: str, values: ValidationInfo) -> str:
        v = v.strip()
        embedding_type = values.data.get('embedding_type')

        if embedding_type == EmbeddingProviderType.OPENAI:
            if not v.startswith('text-embedding-'):
                raise ConfigValidationError(
                    "OpenAI embedding model must start with 'text-embedding-'")
        return v

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
    """Configuration for Language Model (LLM) settings.

    Attributes:
        llm_type: Type of LLM provider (e.g., OpenAI, HuggingFace)
        model_name: Specific model identifier
        temperature: Controls output randomness (0.0=deterministic, 2.0=most random)
        max_tokens: Maximum length of generated response (None=model's max)
        top_p: Nucleus sampling threshold for output diversity
        frequency_penalty: Reduces word repetition (-2.0 to 2.0)
        presence_penalty: Encourages topic diversity (-2.0 to 2.0)
        additional_params: Provider-specific parameters
    """
    llm_type: LLMType
    model_name: str
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=None, ge=0)
    top_p: float = Field(default=1.0, ge=0.0, le=1.0)
    frequency_penalty: float = Field(default=0.0, ge=-2.0, le=2.0)
    presence_penalty: float = Field(default=0.0, ge=-2.0, le=2.0)
    additional_params: Optional[dict[str, Any]] = None

    @field_validator('model_name')
    @classmethod
    def validate_model_name(cls, v: str, info: ValidationInfo) -> str:
        """Validates model name based on provider requirements."""
        v = v.strip()
        llm_type = info.data.get('llm_type')

        if llm_type == LLMType.OPENAI:
            valid_prefixes = ('gpt-4', 'gpt-3.5')
            if not any(v.startswith(prefix) for prefix in valid_prefixes):
                raise ConfigValidationError(
                    f"OpenAI model must start with one of: {', '.join(valid_prefixes)}")
        elif llm_type == LLMType.CLAUDE:
            if not v.startswith('claude-'):
                raise ConfigValidationError(
                    "Anthropic model must start with 'claude-'")
        return v

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
    store_type: VectorStoreType = Field(default=VectorStoreType.FAISS)
    persist_dir: Path
    dimension: int = Field(default=1536, ge=0)
    additional_params: Optional[dict[str, Any]] = Field(default_factory=dict)

    @classmethod
    @field_validator('persist_dir')
    def validate_persist_dir(cls, v: Path):
        v = v.resolve()
        try:
            v.parent.mkdir(parents=True, exist_ok=True)
            return v
        except Exception as e:
            raise ConfigValidationError(f"Invalid persist directory: {e}")

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

    @classmethod
    @field_validator('root_dir')
    def validate_root_dir(cls, v: Path) -> Path:
        v = v.resolve()
        if not v.exists():
            raise ConfigValidationError(f"Root directory does not exist: {v}")
        if not v.is_dir():
            raise ConfigValidationError(f"Root path is not a directory: {v}")
        return v

    @field_validator("vector_config")
    @classmethod
    def validate_dimensions(cls, v: VectorConfig, info: ValidationInfo) -> VectorConfig:
        emb_config = info.data.get("emb_config")
        print(emb_config.dimension, v.dimension)
        if emb_config and v.dimension != emb_config.dimension:
            raise ConfigValidationError(
                "Vector dimension must match embedding dimension")

        return v


def sample_config() -> str:
    """Creates a sample YAML configuration with detailed descriptions for all parameters"""
    return """# AI-Powered Code Search Configuration
# This configuration file controls how the code search tool processes and interacts with your codebase.

# Root directory of your project (required)
# Use absolute path or relative path from the config file location
root_dir: "./project"

# Embedding Configuration
embedding_config:
  # Type of embedding provider (required)
  # Supported providers: openai, huggingface, cohere
  embedding_type: "openai"
  
  # Model name for generating embeddings (required)
  # OpenAI options: 
  #   - text-embedding-3-small (1536 dimensions, recommended)
  #   - text-embedding-3-large (3072 dimensions)
  #   - text-embedding-ada-002 (legacy)
  # HuggingFace: Use model name from hub (e.g., "sentence-transformers/all-mpnet-base-v2")
  model_name: "text-embedding-3-small"
  
  # Processing batch size for embeddings (optional)
  # Larger values process more text at once but use more memory
  # Default: 100
  batch_size: 100 
  
  # Vector dimension (required)
  # Must match the output dimension of your chosen embedding model
  # Common values: 1536 (OpenAI), 768/1024 (HuggingFace)
  dimension: 1536
  
  # Provider-specific parameters (optional)
  # Example for HuggingFace:
  # additional_params:
  #   device: "cuda"  # Use GPU acceleration
  #   normalize_embeddings: true
  additional_params: null

# LLM (Language Model) Configuration
llm_config:
  # LLM provider type (required)
  # Supported: openai, anthropic, huggingface
  llm_type: "openai"
  
  # Model name (required)
  # OpenAI options: 
  #   - gpt-4-turbo-preview (recommended)
  #   - gpt-4
  #   - gpt-3.5-turbo
  #   - gpt-4o-mini
  # Anthropic options:
  #   - claude-3-opus
  #   - claude-3-sonnet
  #   - claude-2.1
  model_name: "gpt-4o-mini"
  
  # Response temperature (optional)
  # Range: 0.0 to 1.0
  # - 0.0: Focused, deterministic
  # - 0.7: Balanced creativity (default)
  # - 1.0: Maximum creativity
  temperature: 0.7
  
  # Maximum response length in tokens (optional)
  # Default: None (model maximum)
  # Set lower to control costs and response length
  max_tokens: 1000
  
  # Top-p sampling (optional)
  # Controls response diversity
  # Range: 0.0 to 1.0, Default: 1.0
  top_p: 1.0
  
  # Frequency penalty (optional)
  # Prevents word repetition
  # Range: -2.0 to 2.0, Default: 0.0
  frequency_penalty: 0.0
  
  # Presence penalty (optional)
  # Encourages topic diversity
  # Range: -2.0 to 2.0, Default: 0.0
  presence_penalty: 0.0
  
  # Provider-specific parameters (optional)
  additional_params: null

# Vector Store Configuration
vector_config:
  # Vector store type (required)
  # Supported: faiss (local), chroma (local), pinecone (cloud)
  store_type: "faiss"
  
  # Storage directory (required for local stores)
  # Relative to project root or absolute path
  persist_dir: "./vector_store"
  
  # Vector dimension (required)
  # Must match embedding dimension
  dimension: 1536
  
  # Store-specific parameters (optional)
  # Example for Pinecone:
  # additional_params:
  #   environment: "production"
  #   index_name: "code-search"
  additional_params: null

# File Pattern Configuration

# Patterns to ignore (glob format)
# Common defaults are provided, add project-specific patterns as needed
ignore_patterns:
  # Version Control
  - "**/.git/**"
  - "**/.svn/**"
  
  # Dependencies
  - "**/node_modules/**"
  - "**/venv/**"
  - "**/.env/**"
  
  # Build outputs
  - "**/dist/**"
  - "**/build/**"
  - "**/__pycache__/**"
  
  # IDE files
  - "**/.vscode/**"
  - "**/.idea/**"
  
  # Temporary files
  - "**/*.log"
  - "**/*.tmp"
  - "**/.DS_Store"

# Patterns to explicitly include (glob format)
# Override ignore patterns for specific files
accepted_patterns:
  - "**/*.py"    # Python files
  - "**/*.js"    # JavaScript files
  - "**/*.ts"    # TypeScript files
  - "**/*.java"  # Java files
  - "**/*.cpp"   # C++ files
  - "**/*.h"     # Header files
  - "**/*.go"    # Go files
  - "**/*.rs"    # Rust files
  - "**/*.rb"    # Ruby files
  - "**/*.php"   # PHP files
"""


async def create_sample_config_file(file_path: Optional[str]) -> None:
    """
    Creates a sample configuration file at the given path
    """
    if file_path is None:
        file_path = Path.cwd() / 'config.yaml'

    config = sample_config()
    await write_file(file_path, config)


def create_config_dict(config: ProjectConfig) -> dict[str, Any]:
    """
    Creates a dictionary from the given configuration
    """
    return {
        'root_dir': str(config.root_dir),
        'embedding_config': {
            'embedding_type': config.emb_config.embedding_type.value,
            'model_name': config.emb_config.model_name,
            'batch_size': config.emb_config.batch_size,
            'dimension': config.emb_config.dimension,
            'additional_params': config.emb_config.additional_params
        },
        'llm_config': {
            'llm_type': config.llm_config.llm_type.value,
            'model_name': config.llm_config.model_name,
            'temperature': config.llm_config.temperature,
            'max_tokens': config.llm_config.max_tokens,
            'top_p': config.llm_config.top_p,
            'frequency_penalty': config.llm_config.frequency_penalty,
            'presence_penalty': config.llm_config.presence_penalty,
            'additional_params': config.llm_config.additional_params
        },
        'vector_config': {
            'store_type': config.vector_config.store_type.value,
            'persist_dir': str(config.vector_config.persist_dir),
            'dimension': config.vector_config.dimension,
            'additional_params': config.vector_config.additional_params
        },
        'ignore_patterns': config.ignore_patterns,
        'accepted_patterns': config.accepted_patterns
    }
