from src.config.configs import (
    ProjectConfig,
    EmbeddingConfig,
    VectorConfig,
    LLMConfig,
    EmbeddingProviderType,
    ConfigValidationError,
    LLMType,
    VectorStoreType
)
import pytest
from pathlib import Path
from pydantic import ValidationError
import sys

project_root = str(Path(__file__).parent.parent)
sys.path.append(project_root)


@pytest.fixture
def valid_embedding_config():
    return {
        'embedding_type': 'openai',
        'model_name': 'text-embedding-3-small',
        'batch_size': 100,
        'dimension': 1536
    }


@pytest.fixture
def valid_llm_config():
    return {
        'llm_type': 'openai',
        'model_name': 'gpt-4-turbo-preview',
        'temperature': 0.7,
        'max_tokens': 1000,
        'top_p': 1.0,
        'frequency_penalty': 0.0,
        'presence_penalty': 0.0
    }


@pytest.fixture
def valid_vector_config(tmp_path):
    return {
        'store_type': 'faiss',
        'persist_dir': str(tmp_path / 'vector_store'),
        'dimension': 1536
    }


class TestEmbeddingConfig:
    def test_valid_config(self, valid_embedding_config):
        config = EmbeddingConfig.from_dict(valid_embedding_config)
        assert config.embedding_type == EmbeddingProviderType.OPENAI
        assert config.model_name == 'text-embedding-3-small'
        assert config.batch_size == 100
        assert config.dimension == 1536

    def test_invalid_model_name(self, valid_embedding_config):
        valid_embedding_config['model_name'] = 'invalid-model'
        with pytest.raises(ConfigValidationError):
            EmbeddingConfig.from_dict(valid_embedding_config)

    def test_invalid_batch_size(self, valid_embedding_config):
        valid_embedding_config['batch_size'] = 0
        with pytest.raises(ValidationError):
            EmbeddingConfig.from_dict(valid_embedding_config)


class TestLLMConfig:
    def test_valid_config(self, valid_llm_config):
        config = LLMConfig.from_dict(valid_llm_config)
        assert config.llm_type == LLMType.OPENAI
        assert config.model_name == 'gpt-4-turbo-preview'
        assert config.temperature == 0.7

    def test_invalid_model_name(self, valid_llm_config):
        valid_llm_config['model_name'] = 'invalid-model'
        with pytest.raises(ConfigValidationError):
            LLMConfig.from_dict(valid_llm_config)

    def test_invalid_temperature(self, valid_llm_config):
        valid_llm_config['temperature'] = 3.0
        with pytest.raises(ValidationError):
            LLMConfig.from_dict(valid_llm_config)

    def test_claude_model_validation(self):
        config_dict = {
            'llm_type': 'claude',
            'model_name': 'claude-3-sonnet'
        }
        config = LLMConfig.from_dict(config_dict)
        assert config.model_name == 'claude-3-sonnet'


class TestVectorConfig:
    def test_valid_config(self, valid_vector_config, tmp_path):
        config = VectorConfig.from_dict(valid_vector_config)
        assert config.store_type == VectorStoreType.FAISS
        assert isinstance(config.persist_dir, Path)
        assert config.dimension == 1536

    def test_invalid_dimension(self, valid_vector_config):
        valid_vector_config['dimension'] = -1
        with pytest.raises(ValidationError):
            VectorConfig.from_dict(valid_vector_config)

    def test_creates_persist_dir(self, tmp_path):
        config = VectorConfig(
            store_type=VectorStoreType.FAISS,
            persist_dir=tmp_path / 'new_dir' / 'vector_store',
            dimension=1536
        )
        assert config.persist_dir.parent.exists()


class TestProjectConfig:
    def test_valid_config(self, valid_embedding_config, valid_llm_config, valid_vector_config, tmp_path):
        config_dict = {
            'root_dir': str(tmp_path),
            'embedding_config': valid_embedding_config,
            'llm_config': valid_llm_config,
            'vector_config': valid_vector_config,
            'ignore_patterns': ['*.pyc', '__pycache__']
        }
        config = ProjectConfig.from_dict(config_dict)
        assert isinstance(config.root_dir, Path)
        assert isinstance(config.emb_config, EmbeddingConfig)
        assert isinstance(config.llm_config, LLMConfig)
        assert isinstance(config.vector_config, VectorConfig)
        assert config.ignore_patterns == ['*.pyc', '__pycache__']
