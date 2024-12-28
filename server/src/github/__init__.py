from .manager import GitManager
from .internal import run_command, CommandResult, GitNotInstalledError

git_manager = GitManager()

__all__ = ["git_manager", "run_command",
           "CommandResult", "GitNotInstalledError"]
