from datetime import datetime
from typing import Optional, Literal, List
from pydantic import BaseModel, Field
from enum import IntEnum


class FileChange(IntEnum):
    ADDED = 1
    DELETED = 2
    RENAMED = 3
    MODIFIED = 4


class CommitDiff(BaseModel):
    """
    Represents a commit diff, which is a subset of a `git.Commit` object's properties.
    This model captures the statistical changes made in a commit.
    """
    files_changed: int = Field(
        description="The number of files changed in the commit"
    )
    insertions: int = Field(
        description="The number of insertions (lines added) in the commit"
    )
    deletions: int = Field(
        description="The number of deletions (lines removed) in the commit"
    )


class CommitDescription(BaseModel):
    """
    Represents a commit description, which is a subset of a `git.Commit` object's properties.
    This model provides a comprehensive view of a commits metadata.
    """
    commit_id: str
    """The full SHA1 commit hash."""

    short_commit_id: str
    """A shortened (7 characters) version of the commit hash."""

    author_name: str
    """The name of the commit author."""

    author_email: str
    """The email of the commit author."""

    date: datetime
    """The date and time when the commit was made."""

    message: str
    """The commit message."""

    stats: CommitDiff
    """Statistics about the commit, such as the number of files changed, insertions, and deletions."""


class StagedFileChanges(BaseModel):
    """
    Represents changes staged for commit in the Git repository.
    """
    file_path: str
    """Path to the changed file relative to repository root"""

    change_type: Literal['added', 'modified', 'deleted', 'renamed']
    """Type of change: 'added', 'modified', 'deleted', or 'renamed'"""

    diff_text: str
    """The actual diff text showing the changes"""

    old_content: Optional[str] = None
    """Previous content of the file, if available"""

    new_content: Optional[str] = None
    """New content of the file, if available"""


class FileInfo(BaseModel):
    """
        Represents a single file change in a Git repository.

        This can be a change in a commit, a diff between commits,
        or a change in the staging area.
    """
    path: str = Field(
        description="Path to the file relative to repository root"
    )
    old_path: Optional[str] = Field(
        default=None,
        description="Previous path if the file was renamed"
    )
    change_type: Literal['added', 'modified', 'deleted', 'renamed'] = Field(
        description="Type of change"
    )
    is_binary: bool = Field(
        description="Whether the file is binary"
    )
    diff_text: Optional[str] = Field(
        default=None,
        description="Diff text showing changes (for text files)"
    )
    old_content: Optional[str] = Field(
        default=None,
        description="Previous file content"
    )
    new_content: Optional[str] = Field(
        default=None,
        description="New file content"
    )


class DiffResult(BaseModel):
    """
    Result of comparing two Git commits or a commit with working directory.
    """
    base_commit: CommitDescription = Field(
        description="Base commit information"
    )
    target_name: str = Field(
        description="Target identifier (commit ID or 'Working Directory')"
    )
    target_date: datetime = Field(
        description="Date of target commit or current time for working directory"
    )
    changes: List[FileInfo] = Field(
        description="List of file changes"
    )
