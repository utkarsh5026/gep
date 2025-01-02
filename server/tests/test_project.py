import pytest
import yaml
import shutil

from unittest.mock import patch

from server.src.config.project import ProjectManager, APIProvider
from server.src.config.configs import ProjectConfig, EmbeddingConfig, LLMConfig, VectorConfig
from server.src.config.api import APIKeyManager, APIKeyNotFoundError


@pytest.fixture
def temp_project_dir(tmp_path):
    project_dir = tmp_path / "test_project"
    project_dir.mkdir()
    yield project_dir
    if project_dir.exists():
        shutil.rmtree(project_dir)


@pytest.fixture
def project_manager(temp_project_dir):
    return ProjectManager(temp_project_dir)


@pytest.fixture
def mock_api_key():
    with patch.object(APIKeyManager, 'get_api_key', return_value="test-key"):
        yield


class TestProjectManager:
    @pytest.mark.asyncio
    async def test_init_new_project(self, project_manager, mock_api_key):
        """Test initializing a new project"""
        embedding_manager = await project_manager.init(
            api_provider=APIProvider.OPENAI,
            api_key="test-key"
        )

        assert project_manager.aigrep_dir.exists()
        assert project_manager.config_file.exists()

        # Verify config file contents
        config = yaml.safe_load(project_manager.config_file.read_text())
        assert "embedding_config" in config
        assert "vector_config" in config

    @pytest.mark.asyncio
    async def test_init_with_missing_api_key(self, project_manager):
        """Test initialization fails properly with missing API key"""
        with patch.object(APIKeyManager, 'get_api_key', side_effect=APIKeyNotFoundError(APIProvider.OPENAI)):
            with pytest.raises(ValueError):
                await project_manager.init(
                    api_provider=APIProvider.OPENAI,
                    api_key=None
                )

    @pytest.mark.asyncio
    async def test_gitignore_collection(self, project_manager):
        """Test collecting gitignore patterns"""
        # Create test .gitignore files
        gitignore1 = project_manager.root_dir / ".gitignore"
        gitignore1.write_text("*.pyc\nnode_modules/\n")

        subdir = project_manager.root_dir / "subdir"
        subdir.mkdir()
        gitignore2 = subdir / ".gitignore"
        gitignore2.write_text("*.log\n")

        patterns = await project_manager._ProjectManager__collect_gitignore_patterns()

        assert "*.pyc" in patterns
        assert "node_modules/" in patterns
        assert "*.log" in patterns
        assert f"{ProjectManager.AIGREP_DIR_NAME}/**" in patterns

    @pytest.mark.asyncio
    async def test_load_save_config(self, project_manager, temp_project_dir):
        """Test loading and saving project configuration"""
        # Create minimal config
        config = ProjectConfig(
            root_dir=temp_project_dir,
            emb_config=EmbeddingConfig(
                embedding_type="openai",
                model_name="text-embedding-3-small"
            ),
            llm_config=LLMConfig(
                llm_type="openai",
                model_name="gpt-4-turbo-preview",
            ),
            vector_config=VectorConfig(
                store_type="faiss",
                persist_dir=temp_project_dir / "vectors",
                dimension=1536
            )
        )

        # Save and reload
        project_manager.aigrep_dir.mkdir()
        project_manager._ProjectManager__save_config(config)
        loaded_config = await project_manager._ProjectManager__load_config()

        assert loaded_config.emb_config.model_name == config.emb_config.model_name
        assert loaded_config.vector_config.dimension == config.vector_config.dimension

    @pytest.mark.asyncio
    async def test_update_ignore_patterns(self, project_manager):
        """Test updating ignore patterns"""
        # Initialize project
        await project_manager.init(api_provider=APIProvider.OPENAI, api_key="test-key")

        # Add new gitignore
        gitignore = project_manager.root_dir / ".gitignore"
        gitignore.write_text("*.new\n*.pattern\n")

        with patch('server.src.config.project._find_project_root', return_value=project_manager.root_dir):
            old_patterns, new_patterns = await ProjectManager.update_ignore()

        assert "*.new" in new_patterns
        assert "*.pattern" in new_patterns

    def test_find_project_root(self, project_manager):
        """Test finding project root directory"""
        # Create nested structure
        subdir = project_manager.root_dir / "a" / "b" / "c"
        subdir.mkdir(parents=True)
        project_manager.aigrep_dir.mkdir()

        # Test from various directories
        assert ProjectManager.find_project_root(
            subdir) == project_manager.root_dir
        assert ProjectManager.find_project_root(
            project_manager.root_dir) == project_manager.root_dir
        assert ProjectManager.find_project_root("/nonexistent") is None
