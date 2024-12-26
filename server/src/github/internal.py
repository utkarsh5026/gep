import os
import shutil
import subprocess
import asyncio
import sys


from pathlib import Path
from pydantic import BaseModel

from logger import logger


class GitNotInstalledError(Exception):
    def __init__(self):
        super().__init__("Git is not installed or not added in the PATH")


class GitCommandError(Exception):
    def __init__(self, command: str):
        super().__init__(f"Git command failed: {command}")


class CommandResult(BaseModel):
    """
    Result of a command
    """
    return_code: int
    stdout: str
    stderr: str


def check_git_available():
    """
    Check if git is available and return the path to it
    """
    logger.info("Checking if git is available")
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


def run_command(command: list[str], check: bool = True) -> CommandResult:
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
            return_code=result.returncode,
            stdout=result.stdout,
            stderr=result.stderr
        )

    except subprocess.SubprocessError as e:
        msg = f"Command failed: {e.stdout if hasattr(e, 'stdout') else str(e)}"
        logger.error(msg)
        raise GitCommandError(msg) from e
    except Exception as e:
        raise GitCommandError(" ".join(command)) from e


def check_git_url(url: str) -> bool:
    """
        Check if the git URL is valid
    """
    logger.info(f"Checking git URL: {url}")

    try:
        result = run_command(["git", "ls-remote", url])
        return result.return_code == 0
    except Exception as e:
        print(f"Error checking git URL: {e}")
        return False


async def download_github_repo(url: str, target_path: Path, branch: str = "main"):
    """
    Download a GitHub repository
    """
    if target_path.exists():
        logger.warning(f"Target path already exists: {target_path}")
        if target_path.is_dir():
            shutil.rmtree(target_path, onexc=_handle_remove_readonly)
        else:
            target_path.unlink()
        logger.info(f"Removed existing path: {target_path}")

    command = [
        "git", "clone",
        "--depth", "1",
        "-b", branch,
        url,
        str(target_path)
    ]

    return run_command(command)


def _handle_remove_readonly(func, path, exc):
    """Handler for removing read-only files on Windows"""
    import stat
    if isinstance(exc, PermissionError):
        logger.warning(f"Permission denied: {
                       path}, will try to remove readonly")
        os.chmod(path, stat.S_IWRITE)
        func(path)


def repo_from_url(url: str) -> str:
    """
    Get the repository name from the URL
    """
    return url.split("/")[-1].split(".")[0]


async def arun_command(command: list[str], check: bool = True) -> CommandResult:
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
