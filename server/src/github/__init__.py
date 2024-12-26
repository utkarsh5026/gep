from .config import GitConfig
from .internal import run_command, CommandResult, GitNotInstalledError

git_config = GitConfig()

__all__ = ["git_config", "run_command",
           "CommandResult", "GitNotInstalledError"]
