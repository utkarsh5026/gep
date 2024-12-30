import yaml
import shutil

from typing import Optional
from pathlib import Path

from .api import APIProvider, APIKeyManager, verify_provider
from .configs import (
    ProjectConfig,
    create_sample_config_file,
    create_config_dict,
    EmbeddingConfig,
    VectorConfig
)
from vector import (
    EmbeddingProvider,
    EmbeddingManager,
    EmbeddingProviderConfig,
    create_embedding_provider,
    VectorStore,
    VectorStoreType,
    FAISSVectorStore
)
from file_utils import read_file


class ProjectManager:
    """
    Manages project configuration, initialization, and settings for the AI-powered grep tool.

    This class handles:
    - Project initialization and configuration management
    - API key management for different providers
    - Gitignore pattern collection and management
    - Vector store directory management for embeddings

    Attributes:
        AIGREP_DIR_NAME (str): Name of the directory storing project configuration ('.gep')
        CONFIG_FILE_NAME (str): Name of the configuration file ('config.yaml')
        VECTOR_STORE_DIR_NAME (str): Name of the directory storing vector embeddings ('vectorstore')
        root_dir (Path): Root directory of the project
        aigrep_dir (Path): Path to the .gep directory
        config_file (Path): Path to the config.yaml file
        vector_store_dir (Path): Path to the vector store directory

    Example:
        ```python
        # Initialize a new project
        manager = ProjectManager(Path("/path/to/project"))
        manager.init(api_provider=APIProvider.OPENAI, api_key="sk-...")

        # Load existing project configuration
        config = manager.load()
        ```
    """
    AIGREP_DIR_NAME = '.gep'
    CONFIG_FILE_NAME = 'config.yaml'
    VECTOR_STORE_DIR_NAME = 'vectorstore'

    def __init__(self, root_dir: Path):
        """
        Initialize a new ProjectManager instance.

        Args:
            root_dir (Path): The root directory of the project
        """
        self.root_dir = root_dir.resolve()
        self.aigrep_dir = self.root_dir / self.AIGREP_DIR_NAME
        self.config_file = self.aigrep_dir / self.CONFIG_FILE_NAME
        self.vector_store_dir = self.aigrep_dir / self.VECTOR_STORE_DIR_NAME

    async def init(self, api_provider: Optional[APIProvider] = None,
                   api_key: Optional[str] = None,
                   overwrite: bool = False) -> EmbeddingManager:
        """
        Initialize a new project.

        This method creates a new project configuration file and initializes the embedding manager.
        It also sets the API key for the specified provider.

        Args:
            api_provider (Optional[APIProvider]): The API provider to use for embeddings
            api_key (Optional[str]): The API key to use for embeddings
            overwrite (bool): Whether to overwrite an existing project

        Returns:
            EmbeddingManager: The embedding manager for the project
        """
        if self.aigrep_dir.exists() and not overwrite:
            print(
                "Project already initialized. Use --overwrite to overwrite existing project")
            config = await self.__load_config()
            return _create_embedding_manager(config)

        if self.aigrep_dir.exists() and overwrite:
            shutil.rmtree(self.aigrep_dir)

        self.aigrep_dir.mkdir(parents=True, exist_ok=True)
        await create_sample_config_file(str(self.config_file))

        _set_api_key(api_provider, api_key)
        config = await self.__load_config()
        return _create_embedding_manager(config)

    async def __collect_gitignore_patterns(self) -> list[str]:
        """
        Load and combine ignore patterns from all .gitignore files in the project directory.

        This method recursively searches for .gitignore files in the project directory and its
        subdirectories. For each file found, it:
        1. Reads the file contents
        2. Filters out comments and empty lines
        3. Adds the valid patterns to a set to remove duplicates
        4. Adds default ignore patterns for common directories

        Returns:
            list[str]: A deduplicated list of ignore patterns, including:
                - All valid patterns from .gitignore files
                - Default patterns for .gep/, .git/, and ignore/ directories

        Example patterns:
            - "*.pyc"  # Ignore Python bytecode files
            - "node_modules/**"  # Ignore node_modules directory
            - ".env"  # Ignore environment files
            - ".gep/**"  # Default ignore for project files
        """
        ignored_patterns = set()
        for gitignore_file in self.root_dir.rglob('*.gitignore'):
            try:
                content = await read_file(Path(gitignore_file).resolve())

                valid_patterns = [
                    line.strip()
                    for line in content.splitlines()
                    if line.strip() and not line.startswith('#')
                ]

                ignored_patterns.update(valid_patterns)

            except Exception as e:
                print(f"Error reading {gitignore_file}: {e}")

        default_ignores = [
            f"{self.AIGREP_DIR_NAME}/**",
            ".git/**",
            "**/ignore/**"
        ]
        ignored_patterns.update(default_ignores)
        return list(ignored_patterns)

    async def __load_config(self) -> ProjectConfig:
        """
        Load and parse the project configuration file.

        This method reads the project's config.yaml file and constructs a ProjectConfig object.
        The config file should be located at self.config_file path.

        Returns:
            ProjectConfig: The parsed project configuration object containing settings for:
                - Root directory
                - Embedding configuration 
                - LLM configuration
                - Vector store configuration
                - Ignore/accept patterns

        Raises:
            ValueError: If the config file does not exist at the expected location
            ValidationError: If the configuration is invalid or missing required fields
        """
        if not self.config_file.exists():
            raise ValueError(
                f"No project configuration found at {self.root_dir}")

        content = await read_file(self.config_file)
        config = yaml.safe_load(content)
        return ProjectConfig.from_dict(config)

    def __save_config(self, config: ProjectConfig):
        """
        Save the project configuration to disk.

        This method serializes the ProjectConfig object to YAML format and writes it
        to the project's config file at self.config_file.

        Args:
            config (ProjectConfig): The project configuration object to save

        The configuration is saved with human-readable formatting (no flow style) and
        preserves the original key ordering.
        """
        config_dict = create_config_dict(config)
        with open(self.config_file, 'w') as file:
            yaml.dump(config_dict,
                      file,
                      default_flow_style=False,
                      sort_keys=False)

    @staticmethod
    async def self_load() -> ProjectConfig:
        """
        Load the project configuration from the current directory.

        This method searches for a project configuration starting from the current directory
        and traversing up the directory tree until it finds a .aigrep directory containing
        a config.yaml file.

        Returns:
            ProjectConfig: The loaded project configuration object

        Raises:
            ValueError: If no project configuration is found in the current directory or any
                parent directories
        """
        root_dir = _find_project_root()
        if root_dir is None:
            raise ValueError("No project found in the current directory")

        manager = ProjectManager(root_dir)
        config = await manager.__load_config()
        config.root_dir = str(root_dir)
        return config

    @staticmethod
    async def update_ignore() -> tuple[list[str], list[str]]:
        """
        Update the project's ignore patterns by re-scanning gitignore files.

        This method scans the project directory for .gitignore files and updates the 
        project configuration with the new patterns. This is useful when gitignore 
        files have been modified, and you want to sync the project's ignore patterns.

        Returns:
            tuple[list[str], list[str]]: A tuple containing:
                - The old ignore patterns that were previously configured
                - The new ignore patterns that were discovered

        Raises:
            ValueError: If no project is found in the current directory
        """
        project_root = _find_project_root()
        if project_root is None:
            raise ValueError("No project found in the current directory")

        proj = ProjectManager(project_root)
        config = await proj.__load_config()

        old_ignore_patterns = config.ignore_patterns
        new_ignore_patterns = await proj.__collect_gitignore_patterns()

        config.ignore_patterns = new_ignore_patterns
        proj.__save_config(config)

        return old_ignore_patterns, new_ignore_patterns

    @staticmethod
    def find_project_root(start_dir: str = ".") -> Optional[Path]:
        """Find the root directory of a project by looking for .aigrep directory"""
        return _find_project_root(start_dir)


def _find_project_root(start_dir: str = ".") -> Optional[Path]:
    """
    Find the root directory of a project by looking for the .gep directory.

    Args:
        start_dir (str): Directory to start searching from. Defaults to current directory.

    Returns:
        Optional[Path]: Path to project root directory if found, None otherwise.

    The function traverses up the directory tree from start_dir, looking for a .gep
    directory that indicates the root of a project. If no such directory is found
    by the time it reaches the filesystem root, returns None.
    """
    current_dir = Path(start_dir).resolve()
    while not (current_dir / ProjectManager.AIGREP_DIR_NAME).exists():
        # Check if we've reached the root directory
        if current_dir == current_dir.parent:
            return None
        current_dir = current_dir.parent
    return current_dir


def _get_api_key(provider: str) -> str:
    """
    Get the API key for a provider.

    Args:
        provider (str): The name of the API provider to get the key for

    Returns:
        str: The API key for the specified provider

    Raises:
        InvalidProviderError: If the provider name is not valid
        APIKeyNotFoundError: If no API key is found for the provider
    """
    provider = verify_provider(provider)
    return APIKeyManager.get_api_key(provider)


def _set_api_key(api_provider: Optional[APIProvider], api_key: Optional[str]):
    """
    Set the API key for the given API provider.

    Args:
        api_provider (Optional[APIProvider]): The API provider to set the key for
        api_key (Optional[str]): The API key to set

    Raises:
        ValueError: If api_key is provided but no existing key is found for the provider
    """
    if api_key is not None and APIKeyManager.get_api_key(api_provider) is None:
        raise ValueError(f"API key for {api_provider} does not exist."
                         f" Please provide it for initializing this project")

    if api_key is not None:
        APIKeyManager.set_api_key(api_provider, api_key)


def _create_embedding_manager(config: ProjectConfig) -> EmbeddingManager:
    """
    Create an EmbeddingManager instance from a ProjectConfig.

    Args:
        config (ProjectConfig): Project configuration containing embedding and vector store settings

    Returns:
        EmbeddingManager: Configured embedding manager instance with embedding provider and vector store
    """
    emb_provider = _create_emb_provider(config.emb_config)
    vector_store = _create_vector_store(config.vector_config)
    return EmbeddingManager(
        embedding_provider=emb_provider,
        vector_store=vector_store
    )


def _create_emb_provider(config: EmbeddingConfig) -> EmbeddingProvider:
    """
    Create an EmbeddingProvider instance from an EmbeddingConfig.

    Args:
        config (EmbeddingConfig): Embedding configuration containing model and provider settings

    Returns:
        EmbeddingProvider: Configured embedding provider instance
    """
    provider = config.embedding_type
    emb_config = EmbeddingProviderConfig(
        model_name=config.model_name,
        api_key=_get_api_key(provider.value),
        batch_size=config.batch_size,
        **config.additional_params
    )
    return create_embedding_provider(provider, emb_config)


def _create_vector_store(config: VectorConfig) -> VectorStore:
    """
    Create a VectorStore instance from a VectorConfig.

    Args:
        config (VectorConfig): Vector store configuration containing store type and settings

    Returns:
        VectorStore: Configured vector store instance
    """
    vector_type = config.store_type
    if vector_type == VectorStoreType.FAISS:
        return FAISSVectorStore(dimension=config.dimension,
                                index_path=config.persist_dir)
