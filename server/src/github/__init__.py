from .config import GitConfig, GitNotInstalledError

git_config = GitConfig()

__all__ = ["git_config", "GitNotInstalledError"]
