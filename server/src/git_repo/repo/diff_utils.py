import git
from pathlib import Path
from typing import  Literal, Optional

from .models import FileChange, FileInfo
from .file_utils import FileUtils as FileHandler


class DiffUtils:

    @classmethod
    def determine_change_type(cls, diff_item: git.Diff) -> Literal['added', 'deleted', 'renamed', 'modified']:
        """
            Determine the type of change represented by a diff item.

            Args:
                diff_item (git.Diff): The diff item to analyze

            Returns:
                str: The type of change ('added', 'deleted', 'renamed', or 'modified')
        """
        if diff_item.new_file:
            return "added"
        elif diff_item.deleted_file:
            return "deleted"
        elif diff_item.renamed:
            return "renamed"
        else:
            return "modified"

    @classmethod
    def is_binary_file(cls, diff: git.Diff) -> bool:
        """
        Check if a diff represents a binary file.

        Args:
            diff: The Git diff to analyze

        Returns:
            True if the file is binary, False otherwise
        """
        if not diff.diff:
            return False

        try:
            if isinstance(diff.diff, str):
                return 'Binary files' in diff.diff
            else:
                return b'Binary files' in diff.diff
        except TypeError:
            # Fallback check
            return 'Binary files' in str(diff.diff)

    @classmethod
    def process_diff(
            cls,
            diff: git.Diff,
            file_handler: FileHandler,
            base_commit: Optional[git.Commit] = None,
            target_commit: Optional[git.Commit] = None
    ) -> FileInfo:
        """
        Process a Git diff into a FileChange model.

        Args:
            diff: The Git diff to process
            file_handler: Handler for retrieving file content
            base_commit: Base commit for comparison (source of old content)
            target_commit: Target commit for comparison (source of new content, None for working directory)

        Returns:
            FileChange model with information about the change
        """

        change_type = cls.determine_change_type(diff)
        is_binary = cls.is_binary_file(diff)

        diff_text = None
        if not is_binary and diff.diff:
            diff_text = diff.diff.decode('utf-8', errors='replace')

        file_info = FileInfo(
            path=diff.b_path if diff.b_path else diff.a_path,
            old_path=diff.a_path if change_type == 'renamed' else None,
            change_type=change_type,
            is_binary=is_binary,
            diff_text=f"{diff.diff}"
        )

        if is_binary:
            return file_info

        if change_type != "added" and base_commit:
            file_info.old_content = file_handler.get_file_content_from_commit(
                file_path=diff.a_path,
                commit=base_commit
            )

        if change_type != "deleted":
            if target_commit:
                file_info.new_content = file_handler.get_file_content_from_commit(
                    file_path=diff.b_path,
                    commit=target_commit
                )
            else:
                file_info.new_content = file_handler.get_working_file_content(diff.b_path)


        return file_info

    @classmethod
    def process_new_file(
            cls,    
            file_path: Path,
            file_handler: FileHandler
    ) -> Optional[FileInfo]:
        """
        Process an untracked file into a FileChange model.

        Args:
            file_path: Path to the untracked file
            file_handler: Handler for retrieving file content

        Returns:
            FileChange model for the new file, or None if processing fails
        """
        try:
            content = file_handler.get_working_file_content(file_path)
            
            return FileInfo(
                path=str(file_path),
                change_type="added",
                is_binary=content is None,  
                diff_text=None,
                new_content=content
            )
            
        except Exception as e:
            # Log the error but don't raise - allows processing to continue for other files
            print(f"Warning: Could not process new file '{file_path}': {e}")
            return None