import shutil
import os
import subprocess
import asyncio
import sys

from pathlib import Path
from tenacity import retry, stop_after_attempt, wait_exponential


from .internal import check_git_available, CommandResult, GitCommandError, run_command, check_git_url, download_github_repo
from logger import logger


class GitConfig:
    def __init__(self):
        self.git_path = check_git_available()
        self.repo_path = Path.home() / ".gep" / "repos"

    def check_git_url(self, url: str) -> bool:
        return check_git_url(url)

    @retry(stop=stop_after_attempt(3),
           wait=wait_exponential(multiplier=1, min=4, max=15))
    async def download_github_repo(self, url: str, branch: str = "main"):
        """
        Download a github repository with automatic retries
        """
        # Check if URL is valid first
        if not self.check_git_url(url):
            raise ValueError(f"Invalid git URL: {url}")

        repo_name = url.rstrip('/').split('/')[-1].replace('.git', '')
        target_path = self.repo_path / repo_name
        result = await download_github_repo(url, target_path, branch)

        if result.return_code == 0:
            logger.info(f"Downloaded repository: {url} to {target_path}")
            return target_path
        else:
            raise GitCommandError(result.stderr)

    async def __arun_command(self, command: list[str], check: bool = True) -> CommandResult:
        """
        Run a shell command asynchronously with proper logging and error handling

        Args:
            command: List of command components to execute
            check: Whether to raise an exception on command failure

        Returns:
            Process: Result of the command

        Raises:
            subprocess.SubprocessError: If the command fails and check=True
        """
        try:
            # Windows-specific settings
            if sys.platform == 'win32':
                process = await asyncio.create_subprocess_exec(
                    *command,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    creationflags=subprocess.CREATE_NO_WINDOW,  # Prevents console window popup
                )
            else:
                process = await asyncio.create_subprocess_exec(
                    *command,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )

            stdout_bytes, stderr_bytes = await process.communicate()

            if check and process.returncode != 0:
                raise subprocess.SubprocessError(
                    f"Command failed with return code {process.returncode}"
                )

            return CommandResult(
                return_code=process.returncode,
                stdout=stdout_bytes.decode(),
                stderr=stderr_bytes.decode()
            )

        except asyncio.CancelledError:
            if 'process' in locals():
                process.terminate()
                try:
                    await process.wait()
                except asyncio.CancelledError:
                    process.kill()
            raise

        except Exception as e:
            raise GitCommandError(" ".join(command)) from e

    def _handle_remove_readonly(self, func, path):
        """Handler for removing read-only files"""
        import stat
        if func in (os.rmdir, os.remove, os.unlink):
            os.chmod(path, stat.S_IWRITE)
            func(path)
