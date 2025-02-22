class GitError(Exception):
    """Base exception for all Git-related errors."""
    
    def __init__(self, message, cause=None):
        self.message = message
        self.cause = cause
        super().__init__(f"{message}" + (f" - Caused by: {cause}" if cause else ""))

class RepositoryError(GitError):
    """Exception class for repository-related errors."""
    pass


class CommitError(GitError):
    """Exception class for commit-related errors."""
    pass

class FileContentError(GitError):
    """Error accessing file content."""
    pass


class DiffError(GitError):
    """Error processing Git diffs."""
    pass