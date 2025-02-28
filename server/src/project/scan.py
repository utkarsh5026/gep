import os
import asyncio
import aiofiles
import aiofiles.os
from typing import Optional
from pathlib import Path

from .models import FileInfo
from .pattern_matcher import GitignorePatternMatcher


class RepoScanner:
    """
    A class for scanning and accessing files in a repository while respecting gitignore patterns.

    This scanner provides functionality to:
    - Scan repository files ignoring patterns in .gitignore
    - Load specific files on demand while respecting gitignore rules
    - Detect project types and important metadata
    """

    GIT_DIR_NAME = '.git'

    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
        self._scanned_files: Optional[list[FileInfo]] = None
        self.pattern_matcher = GitignorePatternMatcher(repo_path)
        self._patterns_loaded = False

    @property
    def scanned_files(self) -> Optional[list[FileInfo]]:
        """
        Get the list of scanned files from the last scan which are not ignored by gitignore.
        """
        return self._scanned_files

    async def _ensure_patterns_loaded(self):
        """
        Make sure gitignore patterns are loaded before using them.
        """
        if not self._patterns_loaded:
            await self.pattern_matcher.load_all_patterns()
            self._patterns_loaded = True

    async def scan(self) -> list[FileInfo]:
        """
        Scan the repository and return information about all non-ignored files.

        This method caches the scan results for later use in file loading operations.

        Returns:
            A list of FileInfo objects for all non-ignored files
        """
        files = await self._find_all_non_ignored_files()

        async def process_file(file_path: Path):
            relative_path = os.path.relpath(file_path, self.repo_path)
            size = await aiofiles.os.path.getsize(file_path)
            return FileInfo(
                name=file_path.name,
                rel_file_path=relative_path,
                directory=file_path.parent,
                size=size
            )

        tasks = []
        for file in files:
            tasks.append(process_file(file))
        file_info_list = list(await asyncio.gather(*tasks))
        self._scanned_files = file_info_list
        return file_info_list

    async def sample_important_files(self, file_data: list[FileInfo]):
        important_files = [
            'README.md', 'package.json', 'pyproject.toml', 'requirements.txt',
            'docker-compose.yml', 'Dockerfile', '.env.example', 'settings.py'
        ]

        samples = {}
        for file in file_data:
            if file.name in important_files:
                try:
                    with open(os.path.join(self.repo_path, file.name), 'r') as f:
                        content = f.read()
                        if len(content) > 2000:
                            content = content[:2000] + "... [truncated]"
                        samples[file.rel_file_path] = content
                except Exception:
                    pass  # Silently skip files we can't read

        return samples

    async def _find_all_non_ignored_files(self) -> list[Path]:
        """
        Find all files that aren't ignored by any gitignore pattern.

        Returns:
            List[Path]: List of paths to non-ignored files
        """
        await self._ensure_patterns_loaded()
        all_files = []
        seen_dirs = set()

        self._collect_non_ignored_files(self.repo_path, all_files, seen_dirs)
        return all_files

    def _collect_non_ignored_files(self, directory: Path, all_files: list, seen_dirs: set):
        """
        Helper method to recursively collect all non-ignored files from a directory.

        Args:
            directory (Path): Directory to search in
            all_files (list): List to collect found files
            seen_dirs (set): Set of already processed directories
        """
        if directory in seen_dirs:
            return

        seen_dirs.add(directory)

        try:
            for item in directory.iterdir():
                try:
                    rel_path = str(item.relative_to(self.repo_path))
                except ValueError:
                    rel_path = str(item)

                if self.pattern_matcher.is_path_ignored(rel_path):
                    continue

                if item.is_file():
                    all_files.append(item)
                elif item.is_dir() and item.name != self.GIT_DIR_NAME:
                    self._collect_non_ignored_files(item, all_files, seen_dirs)
        except PermissionError:
            print(f"Warning: Permission denied accessing {directory}")
        except Exception as e:
            print(f"Warning: Error processing {directory}: {str(e)}")

    @classmethod
    def find_root_dir_and_initialize(cls) -> 'RepoScanner':
        """
        Find the root directory of the repository and initialize a RepoScanner.
        """
        curr_path = Path.cwd()
        while not (curr_path / cls.GIT_DIR_NAME).exists():
            curr_path = curr_path.parent
            if curr_path == Path('/'):
                raise ValueError("Not inside a Git repository")

        return cls(curr_path)
