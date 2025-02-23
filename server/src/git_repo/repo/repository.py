import git
from pathlib import Path
from datetime import datetime
from typing import Optional, Generator, List, Set
from git.exc import InvalidGitRepositoryError, NoSuchPathError

from .models import CommitDiff, CommitDescription, FileInfo, DiffResult
from .exceptions import GitError, RepositoryError, CommitError
from .file_utils import FileUtils as FileHandler
from .diff_utils import DiffUtils


class Repository:
    """
    A class that provides an interface to interact with Git repositories.
    
    This class wraps the GitPython library to provide high-level operations
    for working with Git repositories, including commit history retrieval
    and commit comparison functionality.

    Attributes:
        repo_path (Path): The resolved path to the Git repository
        _repo (git.Repo): The underlying GitPython repository object
    """

    def __init__(self, repo_path: str) -> None:
        """
        Initialize a new Repository instance.

        Args:
            repo_path (str): Path to the Git repository

        Raises:
            ValueError: If the repository path is invalid or not a Git repository
            GitOperationError: If there are issues initializing the repository
        """
        try:
            self.repo_path = Path(repo_path).resolve()

            if not self.repo_path.exists():
                raise RepositoryError(f"Repository path '{repo_path}' does not exist")

            if not self.repo_path.is_dir():
                raise RepositoryError(f"Repository path '{repo_path}' is not a directory")

            self._repo = git.Repo(self.repo_path)
            self.file_handler = FileHandler(self.repo_path, self._repo)

        except InvalidGitRepositoryError:
            raise RepositoryError(f"Path '{repo_path}' is not a valid Git repository")

        except NoSuchPathError:
            raise RepositoryError(f"Repository path '{repo_path}' does not exist")

        except Exception as e:
            raise RepositoryError(f"Failed to initialize repository at '{repo_path}'", cause=e)

    @property
    def repo(self) -> git.Repo:
        """
        Get the underlying GitPython repository object.

        Returns:
            git.Repo: The GitPython repository object

        Raises:
            GitOperationError: If the repository cannot be accessed
        """
        if self._repo is None:
            try:
                self._repo = git.Repo(self.repo_path)
            except Exception as e:
                raise RepositoryError(f"Cannot access repository: {e}")
        return self._repo

    @property
    def active_branch_name(self) -> str:
        """
        Get the name of the currently active branch.

        Returns:
            str: Name of the active branch

        Raises:
            GitOperationError: If the active branch cannot be determined
        """
        try:
            return self._repo.active_branch.name
        except Exception as e:
            raise RepositoryError(f"Cannot determine active branch: {e}")

    def get_commit_history(
            self,
            max_count: int = 50,
            branch_name: Optional[str] = None
    ) -> Generator[CommitDescription, None, None]:
        """
        Retrieve the commit history for a specified branch.

        Args:
            max_count (int, optional): Maximum number of commits to retrieve. Defaults to 50.
            branch_name (str, optional): Name of the branch to get history from. Defaults to "main".

        Yields:
            CommitDescription: Description of each commit in the history.

        Raises:
            GitOperationError: If commit history cannot be retrieved
            ValueError: If max_count is not positive
        """
        if max_count <= 0:
            raise ValueError("max_count must be positive")

        try:
            branch_name = branch_name or self.active_branch_name
            commits = self.repo.iter_commits(branch_name, max_count=max_count)
            for commit in commits:
                try:
                    yield self._parse_commit_info(commit)
                except Exception as e:
                    print(f"Warning: Failed to parse commit {commit.hexsha[:7]}: {e}")
                    continue

        except Exception as e:
            raise RepositoryError(f"Failed to get commit history for branch '{branch_name}'", cause=e)

    def _get_commit(self, commit_id: str) -> git.Commit:
        try:
            return self._repo.commit(commit_id)
        except Exception as e:
            raise CommitError(f"Failed to get commit '{commit_id}'", cause=e)

    def compare_commits(
            self,
            base: str,
            target: Optional[str] = None
    ) -> DiffResult:
        """
        Compare two commits or a commit with the working directory.

        This method provides a detailed comparison between two commits or between
        a commit and the working directory, including file changes, content differences,
        and metadata about the changes.

        Args:
            base (str): Base commit ID to compare from
            target (Optional[str], optional): Target commit ID. If None, compares with working directory.

        Returns:
            DiffResult: Object containing comparison results including base commit info,
                     target info, and list of file changes

        Raises:
            GitError: If comparison fails or commits cannot be found
        """
        try:
            base_commit = self._get_commit(base)
            target_commit = None

            if target is None:
                diffs = base_commit.diff(None)
                comparison_target = "Working Directory"
                comparison_date = datetime.now()
            else:
                target_commit = self._get_commit(target)
                diffs = base_commit.diff(target_commit)
                comparison_target = target_commit.hexsha[:7]
                comparison_date = datetime.fromtimestamp(target_commit.committed_date)

            changes = []
            for diff in diffs:
                try:
                    file_change = DiffUtils.process_diff(
                        diff=diff,
                        file_handler=self.file_handler,
                        base_commit=base_commit,
                        target_commit=target_commit
                    )
                    changes.append(file_change)
                except Exception as e:
                    path = diff.b_path if diff.b_path else diff.a_path
                    print(f"Warning: Error processing diff for file '{path}': {e}")

            base_info = self._parse_commit_info(base_commit)

            return DiffResult(
                base_commit=base_info,
                target_name=comparison_target,
                target_date=comparison_date,
                changes=changes
            )

        except GitError:
            raise

        except Exception as e:
            raise RepositoryError(f"Failed to compare commits: {e}")

    @classmethod
    def _parse_commit_info(cls, commit: git.Commit) -> CommitDescription:
        """
        Parse a git.Commit object into a CommitDescription model.

        Args:
            commit (git.Commit): The git commit object to parse

        Returns:
            CommitDescription: A structured representation of the commit
        """
        stats = CommitDiff(
            files_changed=commit.stats.total['files'],
            insertions=commit.stats.total['insertions'],
            deletions=commit.stats.total['deletions']
        )

        return CommitDescription(
            commit_id=commit.hexsha,
            short_commit_id=commit.hexsha[:7],
            author_name=commit.author.name or "",
            author_email=commit.author.email or "",
            date=datetime.fromtimestamp(commit.committed_date),
            message=str(commit.message).strip(),
            stats=stats
        )

    def get_staged_changes(self) -> List[FileInfo]:
        """
        Get information about all files that are currently staged for commit.
        Fixed to correctly handle diff direction for staged changes.
        """
        try:
            staged_files = []
            index_tree = self._repo.index.write_tree()
            for diff in self._repo.head.commit.diff(index_tree):
                try:
                    file_change = DiffUtils.process_diff(
                        diff=diff,
                        file_handler=self.file_handler,
                        base_commit=self._repo.head.commit
                    )
                    staged_files.append(file_change)
                except Exception as e:
                    path = diff.b_path if diff.b_path else diff.a_path
                    print(f"Warning: Error processing staged change for file '{path}': {e}")

            return staged_files
        except Exception as e:
            raise RepositoryError("Failed to get staged changes", cause=e)