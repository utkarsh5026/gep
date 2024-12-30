from pathlib import Path

from github import git_manager
from config import ProjectConfig, ProjectManager
from file_utils import read_file, write_file


class LLmRepoManager:
    """
    Manages LLM repositories
    """

    def __init__(self):
        self.repos: dict[str, ProjectConfig] = {}

    async def load_project(self, repo_url: str):
        """
        Load or create a project configuration for a repository.
        """
        repo_path = git_manager.get_repo_path(url=repo_url)
        if repo_path in self.repos:
            return self.repos[repo_path]

        repo = await git_manager.load_repo(repo_url)
        config = await _load_repo_config(repo_path)
        await _add_path_to_gitignore(repo_path)
        self.repos[repo_path] = config
        return repo

    async def query(self, repo_url: str, query: str) -> str:
        """
        Query a repository with a given query.
        """
        repo_path = str(git_manager.get_repo_path(url=repo_url))
        if repo_path not in self.repos or self.repos[repo_path] is None:
            raise ValueError(f"Repository not loaded: {repo_url}")

    @staticmethod
    async def get_file_content(repo_url: str, file_path: str):
        """
        Get the content of a file in a repository.
        """
        repo_path = git_manager.get_repo_path(url=repo_url)
        file_path = repo_path / file_path
        return await read_file(file_path)


async def _load_repo_config(repo_path: Path) -> ProjectConfig:
    """
    Load or create a project configuration for a repository.

    Args:
        repo_path (Path): Path to the repository root directory

    Returns:
        ProjectConfig: The loaded or initialized project configuration

    This function creates a ProjectManager instance for the given repository path
    and initializes a new configuration if one doesn't exist.
    """
    project_manager = ProjectManager(root_dir=repo_path)
    config = project_manager.init()
    return config


async def _add_path_to_gitignore(root_dir: Path):
    """
    Add Gep-specific entries to the repository's .gitignore file.

    Args:
        root_dir (Path): Path to the repository root directory

    This function:
    1. Checks if .gitignore exists in the repository
    2. If it exists, reads the current content
    3. Adds Gep-specific entries if they don't already exist:
       - "# Gep configs"
       - ".gep"
    4. Appends only the missing entries to avoid duplication
    """
    gitignore_path = root_dir / ".gitignore"
    entries_to_add = ["# Gep configs\n", ".gep\n"]
    existing_content = ""

    if gitignore_path.exists():
        existing_content = await read_file(gitignore_path)
        if all(entry in existing_content for entry in entries_to_add):
            return

    entries_to_write = [
        entry for entry in entries_to_add
        if entry not in existing_content
    ]

    await write_file(
        file_path=gitignore_path,
        content="".join(entries_to_write),
        mode='a'
    )
