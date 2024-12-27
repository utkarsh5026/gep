# internal.py - internal functions for github module

import os
import shutil
import subprocess
import asyncio
import sys


from pathlib import Path
from pydantic import BaseModel

from logger import logger
from .file import list_files_recursively, create_file_tree, FileNode


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


class RepoInfo(BaseModel):
    commit_diff: dict
    files: FileNode


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
        logger.info(f"Running command: {' '.join(command)}")
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
        cmd = _args("git", "ls-remote", url)
        result = run_command(cmd)
        return result.return_code == 0
    except Exception as e:
        logger.error(f"Error checking git URL: {e}")
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
    """
    try:
        # Fallback to synchronous execution if async fails
        try:
            if sys.platform == 'win32':
                process = await asyncio.create_subprocess_exec(
                    *command,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    creationflags=subprocess.CREATE_NO_WINDOW,
                )
            else:
                process = await asyncio.create_subprocess_exec(
                    *command,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
            stdout_bytes, stderr_bytes = await process.communicate()
            return_code = process.returncode

        except NotImplementedError:
            logger.warning(
                "Async execution not supported, falling back to synchronous execution")
            return run_command(command)

        if check and return_code != 0:
            raise subprocess.SubprocessError(
                f"Command failed with return code {return_code}"
            )

        stdout = stdout_bytes.decode() if stdout_bytes else ""
        stderr = stderr_bytes.decode() if stderr_bytes else ""

        return CommandResult(
            return_code=return_code,
            stdout=stdout,
            stderr=stderr
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
        logger.error(f"Error running command: {e}")
        raise e


async def load_repo(repo_path: Path) -> RepoInfo:
    """
    Load a repository
    """
    if not repo_path.exists():
        raise FileNotFoundError(f"Repository not found: {repo_path}")

    if not repo_path.is_dir():
        raise NotADirectoryError(f"Not a directory: {repo_path}")

    commit_diff = await _get_commit_difference(repo_path)
    files = create_file_tree(list_files_recursively(directory=repo_path))

    return RepoInfo(
        commit_diff=commit_diff,
        files=files
    )


async def _get_commit_difference(repo_path: Path) -> dict:
    """
    Get detailed information about how many commits ahead/behind the local repository is

    Args:
        repo_path: Path to the git repository

    Returns:
        dict containing:
            - needs_pull (bool): Whether the repo needs to be pulled
            - commits_behind (int): Number of commits behind remote
            - commits_ahead (int): Number of commits ahead of remote
            - current_branch (str): Name of the current branch
    """
    try:
        # Get the current branch name
        branch_result = await arun_command([
            "git", "-C", str(repo_path),
            "rev-parse", "--abbrev-ref", "HEAD"
        ])
        current_branch = branch_result.stdout.strip()

        # Get the commit difference
        diff_result = await arun_command([
            "git", "-C", str(repo_path),
            "rev-list", "--left-right", "--count",
            f"{current_branch}...origin/{current_branch}"
        ])

        ahead, behind = map(int, diff_result.stdout.strip().split('\t'))

        return {
            "needs_pull": behind > 0,
            "commits_behind": behind,
            "commits_ahead": ahead,
            "current_branch": current_branch
        }

    except GitCommandError as e:
        logger.error(f"Error getting commit difference: {e}")
        return {
            "needs_pull": False,
            "commits_behind": 0,
            "commits_ahead": 0,
            "current_branch": "unknown"
        }


def _args(*args) -> list[str]:
    return [str(arg) for arg in args]
