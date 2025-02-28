import os
import fnmatch
import aiofiles
from pathlib import Path
from typing import Optional


class GitIgnoreParseError(Exception):
    """
    Exception raised when there is an error parsing a .gitignore file.
    """

    def __init__(self, path: Path, message: str):
        super().__init__(
            f"Error parsing .gitignore file at {path.as_posix()}: {message}")


class GitignorePattern:
    """
    Represents a pattern from a .gitignore file with context about its location.

    This class encapsulates both the pattern itself and information about where
    it was defined, enabling proper path-relative pattern matching.
    """

    @classmethod
    def from_line(cls, line: str, base_dir: str) -> "GitignorePattern":
        """
        Create a GitignorePattern from a line of a .gitignore file.

        Args:
            line: A line from a .gitignore file
            base_dir: The directory path (relative to repo root) where this pattern was defined

        Returns:
            A GitignorePattern object
        """
        is_negated = line.startswith('!')
        pattern = line[1:].strip() if is_negated else line
        return cls(pattern, is_negated, base_dir)

    def __init__(self, pattern: str, is_negated: bool, base_dir: str = ""):
        """
        Initialize a gitignore pattern.

        Args:
            pattern: The actual gitignore pattern string
            is_negated: Whether this is a negation pattern (starts with !)
            base_dir: The directory path (relative to repo root) where this pattern was defined
        """
        self.pattern = pattern
        self.is_negated = is_negated
        self.base_dir = base_dir

        if self.base_dir and not self.base_dir.endswith('/'):
            self.base_dir += '/'

        self.is_anchored = self.pattern.startswith('/')
        if self.is_anchored:
            self.pattern = self.pattern[1:]

        self.is_dir_only = self.pattern.endswith('/')
        if self.is_dir_only:
            self.pattern = self.pattern[:-1]

    def __repr__(self):
        """String representation of the pattern for debugging."""
        prefix = "!" if self.is_negated else ""
        suffix = "/" if self.is_dir_only else ""
        prefix2 = "/" if self.is_anchored else ""
        return f"<GitignorePattern '{prefix}{prefix2}{self.pattern}{suffix}' in {self.base_dir or 'root'}>"


class GitignorePatternMatcher:
    """
    A class dedicated to handling gitignore pattern matching logic.

    This class is responsible for:
    1. Parsing .gitignore files
    2. Managing collections of patterns from multiple .gitignore files
    3. Checking if paths match patterns according to Git's rules
    """

    GITIGNORE_FILE_NAME = '.gitignore'

    def __init__(self, repo_path: Path):
        """Initialize the pattern matcher with empty pattern collection."""
        self.patterns = []
        self.gitignore_locations = set()
        self.repo_path = repo_path

    def find_all_gitignore_files(self) -> set[str]:
        """
        Find all .gitignore files in a repository.

        Returns:
            A set of directory paths (relative to repo root) containing .gitignore files
        """
        locations = set()
        self._scan_directory_for_gitignores(self.repo_path, "", locations)
        self.gitignore_locations = locations
        return locations

    def _scan_directory_for_gitignores(self, directory: Path, rel_dir: str, locations: set) -> None:
        """
        Helper method to recursively scan directories for .gitignore files.

        Args:
            directory: Current directory to scan
            rel_dir: Relative path from repo root to current directory
            locations: Set to collect paths containing .gitignore files
        """
        try:
            for item in directory.iterdir():
                if item.is_dir() and item.name != '.git':
                    next_rel_dir = os.path.join(
                        rel_dir, item.name) if rel_dir else item.name
                    self._scan_directory_for_gitignores(
                        item, next_rel_dir, locations)
                elif item.is_file() and item.name == self.GITIGNORE_FILE_NAME:
                    locations.add(rel_dir)
        except PermissionError:
            print(f"Warning: Permission denied accessing {directory}")
        except Exception as e:
            print(f"Warning: Error scanning directory {directory}: {e}")

    @classmethod
    async def load_patterns_from_gitignore(cls, gitignore_path: Path, base_dir: str = "") -> list[GitignorePattern]:
        """
        Load and parse patterns from a .gitignore file.

        Args:
            gitignore_path: Path to the .gitignore file
            base_dir: Relative directory where this .gitignore is located

        Returns:
            List of GitignorePattern objects parsed from the file
        """

        def _parse_gitignore(_content: str, _base_dir: str) -> list[GitignorePattern]:
            patterns = []
            for line in _content.splitlines():
                line = line.strip()
                if not line or line.startswith('#'):
                    continue

                pattern = GitignorePattern.from_line(line, _base_dir)
                patterns.append(pattern)

            return patterns

        try:
            async with aiofiles.open(gitignore_path, 'r', encoding='utf-8') as f:
                content = await f.read()
                return _parse_gitignore(content, base_dir)

        except UnicodeDecodeError:
            try:
                async with aiofiles.open(gitignore_path, 'r', encoding='latin-1') as f:
                    content = await f.read()
                    return _parse_gitignore(content, base_dir)

            except Exception as e:
                raise GitIgnoreParseError(gitignore_path, str(e)) from e
        except Exception as e:
            raise GitIgnoreParseError(gitignore_path, str(e)) from e

    async def load_all_patterns(self) -> list[GitignorePattern]:
        """
        Load patterns from all .gitignore files in the repository.

        Returns:
            A list of all GitignorePattern objects from all .gitignore files
        """
        if not self.gitignore_locations:
            self.find_all_gitignore_files()

        all_patterns: list[GitignorePattern] = []
        root_gitignore = self.repo_path / self.GITIGNORE_FILE_NAME

        if root_gitignore.exists() and root_gitignore.is_file():
            root_patterns = await self.load_patterns_from_gitignore(root_gitignore)
            all_patterns.extend(root_patterns)

        for rel_dir in self.gitignore_locations:
            if not rel_dir:
                continue

            gitignore_path = self.repo_path / rel_dir / self.GITIGNORE_FILE_NAME
            if gitignore_path.exists() and gitignore_path.is_file():
                patterns = await self.load_patterns_from_gitignore(gitignore_path, rel_dir)
                all_patterns.extend(patterns)

        all_patterns.sort(key=lambda p: p.base_dir.count('/'))
        self.patterns = all_patterns
        return all_patterns

    @classmethod
    def is_pattern_applicable(cls, path: str, pattern: GitignorePattern) -> bool:
        """
        Determine if a pattern is applicable to a path based on their locations.

        Args:
            path: Path to check, relative to repo root
            pattern: GitignorePattern object

        Returns:
            True if the pattern should be considered for this path
        """
        path = path.replace('\\', '/')
        if not pattern.base_dir:
            return True

        return path == pattern.base_dir or path.startswith(pattern.base_dir)

    def does_pattern_match(self, path: str, pattern: GitignorePattern) -> bool:
        """
        Check if a specific gitignore pattern matches a path.

        This method handles the actual pattern matching, considering anchored patterns,
        directory-only patterns, wildcards, and other gitignore syntax.

        Args:
            path: Path to check, relative to the repo root
            pattern: GitignorePattern object

        Returns:
            True if the pattern matches the path
        """
        path = path.replace('\\', '/')
        if not self.is_pattern_applicable(path, pattern):
            return False

        rel_path = self._get_relative_path(path, pattern)
        if rel_path is None:
            return False

        # If anchored pattern, match from the start relative to base dir
        if pattern.is_anchored:
            return fnmatch.fnmatch(rel_path, pattern.pattern)

        return self._match_unanchored_pattern(rel_path, pattern.pattern)

    @classmethod
    def _get_relative_path(cls, path: str, pattern: GitignorePattern) -> Optional[str]:
        """Get the path relative to the pattern's base directory."""
        if pattern.base_dir:
            if not path.startswith(pattern.base_dir):
                return None

            rel_path = path[len(pattern.base_dir):]
            if rel_path.startswith('/'):
                rel_path = rel_path[1:]
            return rel_path
        return path

    @classmethod
    def _match_unanchored_pattern(cls, path: str, pattern_str: str) -> bool:
        """Match an unanchored pattern against a path."""
        # Handle patterns with directory separator
        if '/' in pattern_str:
            return fnmatch.fnmatch(path, pattern_str) or fnmatch.fnmatch(path, f"*/{pattern_str}")

        # Handle ** pattern (matches across directories)
        if '**' in pattern_str:
            parts = pattern_str.split('**')
            if len(parts) == 2:
                prefix, suffix = parts
                return (path.startswith(prefix) and path.endswith(suffix)) or \
                    any(segment.startswith(prefix) and segment.endswith(suffix)
                        for segment in path.split('/'))

        # Simple pattern without slash - matches any component in the path
        path_parts = path.split('/')
        return any(fnmatch.fnmatch(part, pattern_str) for part in path_parts)

    def is_path_ignored(self, path: str) -> bool:
        """
        Determine if a path should be ignored based on all loaded gitignore patterns.

        Args:
            path: Path to check, relative to the repo root

        Returns:
            True if the path should be ignored, False otherwise
        """
        path = path.replace('\\', '/')
        ignored = False

        for pattern in self.patterns:
            if self.does_pattern_match(path, pattern):
                ignored = not pattern.is_negated

        return ignored
