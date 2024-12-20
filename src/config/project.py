import yaml
from typing import Optional
from pathlib import Path

from .api import APIProvider, APIKeyManager
from .configs import ProjectConfig, EmbeddingConfig, LLMConfig, create_sample_config_file
from vector import EmbeddingProviderType
from query import LLMType


class ProjectManager:
    AIGREP_DIR_NAME = '.gep'
    CONFIG_FILE_NAME = 'config.yaml'
    VECTOR_STORE_DIR_NAME = 'vectorstore'

    def __init__(self, root_dir: Path):
        self.root_dir = root_dir.resolve()
        self.aigrep_dir = self.root_dir / self.AIGREP_DIR_NAME
        self.config_file = self.aigrep_dir / self.CONFIG_FILE_NAME
        self.vector_store_dir = self.aigrep_dir / self.VECTOR_STORE_DIR_NAME

    def load(self):
        self.__load_config()

    def init(self, api_provider: Optional[APIProvider] = None, api_key: Optional[str] = None, overwrite: bool = False):
        """
        Initialize a new project.
        """
        if self.aigrep_dir.exists() and not overwrite:
            print(
                "Project already initialized. Use --overwrite to overwrite existing project")
            return

        self.__set_api_key(api_provider, api_key)
        self.__create()

    def __create(self):
        self.aigrep_dir.mkdir(parents=True, exist_ok=True)
        create_sample_config_file(str(self.config_file))

    def __load(self, api_provider: Optional[APIProvider] = None, api_key: Optional[str] = None, embedding_config: Optional[EmbeddingConfig] = None, llm_config: Optional[LLMConfig] = None, load_gitignore: bool = True, accept_patterns: list[str] = []):
        """Initialize a new project with custom configurations.

        Args:
            api_provider (Optional[APIProvider]): The API provider to use for authentication. 
                If None, will use default provider. (OpenAI | Anthropic)
            api_key (Optional[str]): API key for authentication. If None, will attempt to load from environment.
            embedding_config (Optional[EmbeddingConfig]): Configuration for the embedding model.
                If None, will use default OpenAI config.
            llm_config (Optional[LLMConfig]): Configuration for the language model.
                If None, will use default OpenAI config.
            load_gitignore (bool): Whether to load ignore patterns from .gitignore files.
                Defaults to True.
            accept_patterns (list[str]): List of file patterns to explicitly include.
                Defaults to empty list.

        Raises:
            ValueError: If project is already initialized in the root directory.

        Returns:
            None
        """
        if self.aigrep_dir.exists():
            raise ValueError(f"Project already initialized in {self.root_dir}")

        self.aigrep_dir.mkdir(parents=True, exist_ok=True)
        self.__set_api_key(api_provider, api_key)

        emb_config, llm_config = self.__check_config(
            embedding_config, llm_config)

        ignore_patterns = []
        if load_gitignore:
            ignore_patterns = self.__get_ignore_patterns()

        config = ProjectConfig(
            root_dir=self.root_dir,
            emb_config=emb_config,
            llm_config=llm_config,
            ignore_patterns=ignore_patterns,
            accepted_patterns=accept_patterns,
        )

        self.__save_config(config)

    def __check_config(self, emb_config: Optional[EmbeddingConfig], llm_config: Optional[LLMConfig]):
        """Check and set default configurations if not provided"""
        if emb_config is None:
            emb_config = EmbeddingConfig(
                embedding_type=EmbeddingProviderType.OPENAI,
                model_name="text-embedding-3-small",
            )

        if llm_config is None:
            llm_config = LLMConfig(
                llm_type=LLMType.OPENAI,
                model_name="gpt-4o-mini",
            )

        return emb_config, llm_config

    def __get_ignore_patterns(self) -> list[str]:
        """
        Load ignore patterns from all .gitignore files in the project directory
        and return a list of patterns.
        """
        ignored_patterns = set()
        for gitignore_file in self.aigrep_dir.rglob('*.gitignore'):
            try:
                with open(gitignore_file, 'r') as file:
                    lines = file.readlines()
                    for line in lines:
                        if line.strip() and not line.startswith('#'):
                            ignored_patterns.add(line.strip())
            except Exception as e:
                print(f"Error reading {gitignore_file}: {e}")

        return list(ignored_patterns)

    def __load_config(self) -> ProjectConfig:
        """Load the project configuration from the config.yaml file"""

        if not self.config_file.exists():
            raise ValueError(
                f"No project configuration found at {self.root_dir}")

        with open(self.config_file, 'r') as file:
            config = yaml.safe_load(file)

        return ProjectConfig(**config)

    def __save_config(self, config: ProjectConfig):
        with open(self.config_file, 'w') as file:
            yaml.dump(config.model_dump(), file)

    def __set_api_key(self, api_provider: Optional[APIProvider], api_key: Optional[str]):
        """Set the API key for the given API provider"""
        if api_key is not None and APIKeyManager.get_api_key(api_provider) is None:
            raise ValueError(f"API key for {
                             api_provider} does not exist. Please provide it for initializing this project")

        if api_key is not None:
            APIKeyManager.set_api_key(api_provider, api_key)

    @staticmethod
    def load_from_yaml(root_dir: str, yaml_file_path: str):

        if not Path(yaml_file_path).exists():
            raise ValueError(f"No project configuration found at {
                             yaml_file_path}")

        with open(yaml_file_path, 'r') as file:
            config = yaml.safe_load(file)

        project_config = ProjectConfig.from_dict(config)
        manager = ProjectManager(project_config.root_dir)
        manager.create()


def find_project_root(start_dir: str = ".") -> Optional[Path]:
    """Find the root directory of a project by looking for .aigrep directory"""
    current_dir = Path(start_dir).resolve()
    while not (current_dir / ProjectManager.AIGREP_DIR_NAME).exists():
        if current_dir == Path("/"):
            return None
        current_dir = current_dir.parent
    return current_dir


def init_project(root_path: str, api_provider: Optional[APIProvider] = None, api_key: Optional[str] = None, overwrite: bool = False):
    """
    Initialize the project.
    """
    manager = ProjectManager(Path(root_path))
    manager.init(api_provider, api_key, overwrite)
    return manager
