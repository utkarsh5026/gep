import git
from pathlib import Path
from typing import Optional, Union
from .exceptions import FileContentError


class FileUtils:
    """
    Utility class for file operations in Git repositories.
    
    This class contains methods to retrieve file content from various sources
    such as commits or the working directory.
    """

    def __init__(self, repo_path: Path, repo: git.Repo):
        """
        Initialize the FileUtils.
        
        arg:
            repo_path (Path): Path to the Git repository
            repo (git.Repo): GitPython repository object
        """
        self.repo_path = repo_path
        self.repo = repo

    @classmethod
    def get_file_content_from_commit(
            cls,
            file_path: Union[str, Path],
            commit: git.Commit
    ) -> Optional[str]:
        """
        Get the content of a file from a specific commit.

        Args:
            file_path (Union[str, Path]): Path to the file within the repository
            commit (git.Commit): The commit to get the file content from

        Returns:
            Optional[str]: The file content as a string, or None if the file
                          doesn't exist, is binary, or cannot be read

        Raises:
            GitOperationError: If there's an error accessing the file content
        """
        try:
            file_path_str = str(file_path)
            file_blob = commit.tree[file_path_str]
            return file_blob.data_stream.read().decode('utf-8', errors='replace')
        except (KeyError, UnicodeDecodeError, AttributeError):
            return None
        except Exception as e:
            raise FileContentError(f"Failed to get file content: {e}")

    def get_working_file_content(self, relative_file_path: Union[str, Path]) -> Optional[str]:
        """
        Get the content of a file from the working directory.

        Args:
            relative_file_path (Union[str, Path]): Path to the file relative to the repository root

        Returns:
            Optional[str]: The file content as a string, or None if the file
                          doesn't exist, is binary, or cannot be read

        Raises:
            GitOperationError: If there's an error accessing the file
        """
        try:
            rel_path = Path(relative_file_path)
            full_path = self.repo_path / rel_path
            with open(full_path, 'r', encoding='utf-8') as f:
                return f.read()
        except (FileNotFoundError, UnicodeDecodeError, IsADirectoryError):
            return None
        except Exception as e:
            raise FileContentError(f"Failed to read file: {e}")
