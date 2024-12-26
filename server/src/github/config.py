import logging
import shutil
import os
import subprocess
import asyncio
import sys


from pathlib import Path
from typing import Optional
from tenacity import retry, stop_after_attempt, wait_exponential
from asyncio.subprocess import create_subprocess_exec
from pydantic import BaseModel


class CommandResult(BaseModel):
    """
    Result of a command
    """
    returncode: int
    stdout: str
    stderr: str


logger = logging.getLogger(__name__)


class GitNotInstalledError(Exception):
    def __init__(self):
        super().__init__("Git is not installed or not added in the PATH")


class GitCommandError(Exception):
    def __init__(self, command: str):
        super().__init__(f"Git command failed: {command}")


class GitConfig:
    def __init__(self):
        self.git_path = self.check_git_available()

    @staticmethod
    def check_git_available():
        git_path = shutil.which("git")
        if git_path is None:
            common_paths = [
                os.path.join("C:", "Program Files", "Git",
                             "bin", "git.exe"),
                os.path.join("C:", "Program Files (x86)", "Git",
                             "bin", "git.exe"),
                os.path.join("/", "usr", "bin", "git"),
                os.path.join("/", "usr", "local", "bin", "git")
            ]

            for path in common_paths:
                if Path(path).exists():
                    return path
        else:
            return git_path

        raise GitNotInstalledError()

    def check_git_url(self, url: str) -> bool:
        """
        Check if the git URL is valid
        """
        logger.info(f"Checking git URL: {url}")

        try:
            result = subprocess.run(
                ["git", "ls-remote", url],
                capture_output=True,
                text=True,
                check=False
            )

            return result.returncode == 0
        except Exception as e:
            print(f"Error checking git URL: {e}")
            return False

    @retry(stop=stop_after_attempt(3),
           wait=wait_exponential(multiplier=1, min=4, max=15))
    async def download_github_repo(self, url: str,
                                   target_path: Optional[str] = None,
                                   branch: str = "main"):
        """
        Download a github repository with automatic retries

        Args:
            url: Git repository URL
            target_path: Where to clone the repository (optional)
            branch: Which branch to clone (default: main)

        Returns:
            Path: Path to the cloned repository

        Raises:
            GitCommandError: If clone fails after all retries
            ValueError: If URL is invalid
        """
        self.check_git_url(url)
        if target_path is None:
            repo_name = url.rstrip('/').split('/')[-1].replace('.git', '')
            target_path = Path.home() / ".gep" / "repos" / repo_name

        if target_path.exists():
            shutil.rmtree(target_path)

        target_path.parent.mkdir(parents=True, exist_ok=True)
        command = [
            "git", "clone",
            "--depth", "1",
            "-b", branch,
            url,
            str(target_path)
        ]

        try:
            res = self.__run_command(command)
            if res.returncode != 0:
                raise GitCommandError(" ".join(command))

            return res

        except Exception as e:
            raise GitCommandError(" ".join(command)) from e

    def __run_command(self, command: list[str], check: bool = True) -> CommandResult:
        """
        Run a shell command with proper logging and error handling

        Args:
            command: List of command components to execute
            check: Whether to raise an exception on command failure

        Returns:
            subprocess.CompletedProcess: Result of the command

        Raises:
            subprocess.SubprocessError: If the command fails and check=True
        """
        try:
            result = subprocess.run(
                command,
                check=check,
                capture_output=True,
                text=True
            )

            if result.stdout:
                logger.debug(f"Command output: {result.stdout}")
            if result.stderr:
                logger.debug(f"Command stderr: {result.stderr}")

            return CommandResult(
                returncode=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr
            )

        except subprocess.SubprocessError as e:
            logger.error(f"Command failed: {
                         e.stdout if hasattr(e, 'stdout') else str(e)}")
            raise
        except Exception as e:
            raise GitCommandError(command) from e

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
                returncode=process.returncode,
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
