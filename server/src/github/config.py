from pathlib import Path
from tenacity import retry, stop_after_attempt, wait_exponential


from .internal import check_git_available, GitCommandError,  check_git_url, download_github_repo, repo_from_url
from logger import logger


class GitConfig:
    def __init__(self):
        self.git_path = check_git_available()
        self.repo_path = Path.home() / ".gep" / "repos"

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=15)
    )
    async def check_git_url(self, url: str) -> bool:
        return check_git_url(url)

    @retry(stop=stop_after_attempt(3),
           wait=wait_exponential(multiplier=1, min=4, max=15))
    async def download_github_repo(self, url: str, branch: str = "main"):
        """
        Download a GitHub repository with automatic retries
        """
        if not check_git_url(url):
            raise ValueError(f"Invalid git URL: {url}")

        target_path = self.repo_path / repo_from_url(url)
        result = await download_github_repo(url, target_path, branch)

        if result.return_code == 0:
            logger.info(f"Downloaded repository: {url} to {target_path}")
            return target_path
        else:
            raise GitCommandError(result.stderr)
