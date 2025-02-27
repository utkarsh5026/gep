import os
import fnmatch
import asyncio
import aiofiles
import aiofiles.os
from pathlib import Path
from typing import List, Tuple

from file_utils import read_file
from .models import FileInfo


class RepoScanner:

    def __init__(self, repo_path: Path):
        self.repo_path = repo_path

    async def scan(self) -> list[FileInfo]:
        files = await self.find_all_non_ignored_files()

        async def process_file(file_path: Path):
            relative_path = os.path.relpath(file_path, self.repo_path)
            size = await aiofiles.os.path.getsize(file_path)
            return FileInfo(
                name=file_path.name,
                rel_file_path=relative_path,
                directory=file_path.parent,
                extension=os.path.splitext(file_path)[1].lower(),
                size=size
            )

        tasks = []
        for file in files:
            tasks.append(process_file(file))
        return list(await asyncio.gather(*tasks))

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
                except:
                    pass  # Silently skip files we can't read

        return samples

    async def _parse_gitignore(self) -> list[tuple[str, bool]]:
        """
        Parse the .gitignore file in the root directory.
        Returns a list of tuples with gitignore patterns and whether they're negated.

        Returns:
            List[Tuple[str, bool]]: List of (pattern, is_negated) tuples
        """
        gitignore_path = self.repo_path / '.gitignore'
        patterns = []

        if gitignore_path.exists() and gitignore_path.is_file():
            content = await read_file(gitignore_path)
            for line in content.splitlines():
                line = line.strip()
                if line and not line.startswith('#'):
                    is_negated = line.startswith('!')
                    pattern = line[1:].strip() if is_negated else line
                    patterns.append((pattern, is_negated))

        return patterns

    async def find_all_non_ignored_files(self) -> list[Path]:
        """
        Find all files that aren't ignored by any gitignore pattern.

        Returns:
            List[Path]: List of paths to non-ignored files
        """
        patterns = await self._parse_gitignore()
        all_files = []
        seen_dirs = set()

        async def collect_files(directory: Path):
            """
            Recursively collect all non-ignored files from a directory.

            Args:
                directory (Path): Directory to search in
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

                    if self.is_path_ignored(rel_path, patterns):
                        continue

                    if item.is_file():
                        all_files.append(item)
                    elif item.is_dir() and item.name != '.git':
                        await collect_files(item)
            except PermissionError:
                print(f"Warning: Permission denied accessing {directory}")
            except Exception as e:
                print(f"Warning: Error processing {directory}: {str(e)}")

        await collect_files(self.repo_path)
        return all_files

    @classmethod
    def match_gitignore_pattern(cls, pattern: str, path: str) -> bool:
        """
        Check if a path matches a gitignore pattern according to git's rules.

        Args:
            pattern (str): Gitignore pattern
            path (str): Path to check (relative to repository root)

        Returns:
            bool: True if the path matches the pattern, False otherwise
        """
        # Normalize paths (use forward slashes)
        path = path.replace('\\', '/')
        pattern = pattern.replace('\\', '/')

        # Handle directory-only patterns (ending with slash)
        is_dir_pattern = pattern.endswith('/')
        if is_dir_pattern:
            pattern = pattern[:-1]  # Remove trailing slash for matching

        # Handle anchored patterns (starting with slash)
        if pattern.startswith('/'):
            # Pattern is anchored to the root
            pattern = pattern[1:]  # Remove leading slash
            return fnmatch.fnmatch(path, pattern)

        # Handle patterns with directory separator
        if '/' in pattern:
            # Contains a path separator but not anchored
            return fnmatch.fnmatch(path, pattern) or fnmatch.fnmatch(path, f"*/{pattern}")

        # Handle ** pattern (matches across directories)
        if '**' in pattern:
            # Convert ** to a simpler pattern for fnmatch
            parts = pattern.split('**')
            if len(parts) == 2:
                prefix, suffix = parts
                # Match any part of the path that has this prefix and suffix
                return (path.startswith(prefix) and path.endswith(suffix)) or \
                    any(segment.startswith(prefix) and segment.endswith(suffix)
                        for segment in path.split('/'))

        # Simple pattern without slash - matches any component in the path
        path_parts = path.split('/')
        return any(fnmatch.fnmatch(part, pattern) for part in path_parts)

    @classmethod
    def is_path_ignored(cls, path: str, patterns: list[tuple[str, bool]]) -> bool:
        """
        Determine if a path should be ignored based on gitignore patterns.

        Args:
            path (str): Path to check, relative to the root directory
            patterns (List[Tuple[str, bool]]): List of gitignore patterns and negation flags

        Returns:
            bool: True if the path should be ignored, False otherwise
        """
        # Important: Initialize as NOT ignored
        ignored = False

        # Apply patterns in order, respecting negations
        for pattern, is_negated in patterns:
            if cls.match_gitignore_pattern(pattern, path):
                # If pattern matches, set ignored status based on negation
                ignored = not is_negated

        return ignored

    @classmethod
    def detect_project_type(cls, file_data: list[FileInfo]):
        # Create lookup dictionaries for quick checking
        files_by_name = {file.name: file for file in file_data}
        files_by_ext = {}
        for file in file_data:
            ext = file.extension
            if ext not in files_by_ext:
                files_by_ext[ext] = []
            files_by_ext[ext].append(file)

        # Check for signature files that indicate project types
        indicators = {
            'package.json': 'JavaScript/Node.js',
            'pyproject.toml': 'Python (modern)',
            'setup.py': 'Python',
            'pom.xml': 'Java (Maven)',
            'build.gradle': 'Java/Kotlin (Gradle)',
            'Cargo.toml': 'Rust',
            'Gemfile': 'Ruby',
            'composer.json': 'PHP',
            'angular.json': 'Angular',
            'webpack.config.js': 'JavaScript (webpack)',
            'tsconfig.json': 'TypeScript',
            'CMakeLists.txt': 'C/C++ (CMake)',
            'Dockerfile': 'Container-based',
            'docker-compose.yml': 'Multi-container application',
            'pubspec.yaml': 'Flutter/Dart'
        }

        detected_types = []
        for filename, project_type in indicators.items():
            if filename in files_by_name:
                detected_types.append(project_type)

        # Also assess by extension proportions
        lang_extensions = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.jsx': 'React',
            '.tsx': 'React with TypeScript',
            '.java': 'Java',
            '.rb': 'Ruby',
            '.php': 'PHP',
            '.go': 'Go',
            '.rs': 'Rust',
            '.c': 'C',
            '.cpp': 'C++',
            '.cs': 'C#',
            '.swift': 'Swift',
            '.kt': 'Kotlin',
            '.dart': 'Dart'
        }

        extension_counts = {ext: len(files)
                            for ext, files in files_by_ext.items()}
        total_source_files = sum(len(files) for ext, files in files_by_ext.items()
                                 if ext in lang_extensions)

        language_proportions = {}
        for ext, lang in lang_extensions.items():
            if ext in extension_counts:
                proportion = extension_counts[ext] / total_source_files
                language_proportions[lang] = language_proportions.get(
                    lang, 0) + proportion

        # Return project insights
        return {
            'detected_frameworks': detected_types,
            'language_distribution': language_proportions
        }

    @classmethod
    async def check_path_against_patterns(cls, file_path: str, patterns: list[tuple[str, bool]]) -> bool:
        """
        Check if a specific file path matches any of the given gitignore patterns.

        Args:
            file_path (str): Path to check
            patterns (List[Tuple[str, bool]]): List of gitignore patterns

        Returns:
            bool: True if the path should be ignored, False otherwise
        """
        return cls.is_path_ignored(file_path, patterns)
