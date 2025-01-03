from pathlib import Path
from tenacity import retry, stop_after_attempt, wait_exponential

from .internal import (
    check_git_available,
    GitCommandError,
    check_git_url,
    download_github_repo,
    repo_from_url,
    load_repo
)
from logger import logger


class GitManager:
    """
    Manages git repositories
    """

    def __init__(self):
        self.git_path = check_git_available()

    @property
    def repo_path(self):
        return Path.home() / ".gep" / "repos"

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=15)
    )
    async def check_git_url(self, url: str) -> bool:
        return check_git_url(url)

    def get_repo_path(self, url: str) -> Path:
        """
        Get the path to the repository

        Parameters:
            url (str): The URL of the repository

        Returns:
            Path: The path to the repository
        """
        return self.repo_path / repo_from_url(url)

    @retry(stop=stop_after_attempt(3),
           wait=wait_exponential(multiplier=1, min=4, max=15))
    async def download_github_repo(self, url: str, branch: str = "main"):
        """
        Download a GitHub repository with automatic retries
        """
        if not check_git_url(url):
            raise ValueError(f"Invalid git URL: {url}")

        target_path = self.get_repo_path(url)
        result = await download_github_repo(url, target_path, branch)

        if result.return_code == 0:
            logger.info(f"Downloaded repository: {url} to {target_path}")
            return target_path
        else:
            raise GitCommandError(result.stderr)

    async def load_repo(self, url: str):
        """
        Load a repository from a URL
        """
        target_path = self.get_repo_path(url)
        try:
            repo = await load_repo(target_path)
            return repo
        except FileNotFoundError:
            await self.download_github_repo(url)
            return await self.load_repo(url)
