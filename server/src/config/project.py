import yaml
from typing import Optional
from pathlib import Path

from .api import APIProvider, APIKeyManager
from .configs import ProjectConfig, create_sample_config_file, create_config_dict


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
        self.root_dir = root_dir.resolve()
        self.aigrep_dir = self.root_dir / self.AIGREP_DIR_NAME
        self.config_file = self.aigrep_dir / self.CONFIG_FILE_NAME
        self.vector_store_dir = self.aigrep_dir / self.VECTOR_STORE_DIR_NAME

    def load(self):
        return self.__load_config()

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

    def __collect_gitignore_patterns(self) -> list[str]:
        """
        Load ignore patterns from all .gitignore files in the project directory
        and return a list of patterns.
        """
        ignored_patterns = set()
        ignore_files = self.root_dir.rglob('*.gitignore')
        for gitignore_file in ignore_files:
            print(gitignore_file)
            try:
                with open(gitignore_file, 'r') as file:
                    lines = file.readlines()
                    for line in lines:
                        if line.strip() and not line.startswith('#'):
                            ignored_patterns.add(line.strip())
            except Exception as e:
                print(f"Error reading {gitignore_file}: {e}")

        ignored_patterns.add(f"{self.AIGREP_DIR_NAME}/**")
        ignored_patterns.add(".git/**")
        ignored_patterns.add("**/ignore/**")
        return list(ignored_patterns)

    def __load_config(self) -> ProjectConfig:
        """Load the project configuration from the config.yaml file"""

        if not self.config_file.exists():
            raise ValueError(
                f"No project configuration found at {self.root_dir}")

        with open(self.config_file, 'r') as file:
            config = yaml.safe_load(file)

        return ProjectConfig.from_dict(config)

    def __save_config(self, config: ProjectConfig):
        """Save the project configuration to the config.yaml file"""
        config_dict = create_config_dict(config)
        with open(self.config_file, 'w') as file:
            yaml.dump(config_dict, file,
                      default_flow_style=False, sort_keys=False)

    def __set_api_key(self, api_provider: Optional[APIProvider], api_key: Optional[str]):
        """Set the API key for the given API provider"""
        if api_key is not None and APIKeyManager.get_api_key(api_provider) is None:
            raise ValueError(f"API key for {
                             api_provider} does not exist. Please provide it for initializing this project")

        if api_key is not None:
            APIKeyManager.set_api_key(api_provider, api_key)

    @staticmethod
    def self_load() -> ProjectConfig:
        """
        Load the project from the current directory.
        """
        root_dir = find_project_root()
        if root_dir is None:
            raise ValueError("No project found in the current directory")

        manager = ProjectManager(root_dir)
        config = manager.__load_config()
        config.root_dir = str(root_dir)
        return config

    @staticmethod
    def load_from_yaml(yaml_file_path: str):

        if not Path(yaml_file_path).exists():
            raise ValueError(f"No project configuration found at {
                             yaml_file_path}")

        with open(yaml_file_path, 'r') as file:
            config = yaml.safe_load(file)

        project_config = ProjectConfig.from_dict(config)
        manager = ProjectManager(project_config.root_dir)
        manager.create()

    @staticmethod
    def update_ignore():
        """
        Update the files which we need to ignore.
        """
        project_root = find_project_root()
        if project_root is None:
            raise ValueError("No project found in the current directory")

        proj = ProjectManager(project_root)
        config = proj.__load_config()

        old_ignore_patterns = config.ignore_patterns
        new_ignore_patterns = proj.__collect_gitignore_patterns()

        config.ignore_patterns = new_ignore_patterns
        proj.__save_config(config)

        return old_ignore_patterns, new_ignore_patterns


def find_project_root(start_dir: str = ".") -> Optional[Path]:
    """Find the root directory of a project by looking for .aigrep directory"""
    current_dir = Path(start_dir).resolve()
    while not (current_dir / ProjectManager.AIGREP_DIR_NAME).exists():
        # Check if we've reached the root directory
        if current_dir == current_dir.parent:
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
