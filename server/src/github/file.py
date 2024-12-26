import os

from pathlib import Path
from pathspec import PathSpec
from pathspec.patterns import GitWildMatchPattern

from logger import logger


def _read_gitignore(directory: Path):
    """
    Read all .gitignore files in the directory tree and combine their rules.
    Returns a PathSpec object that can be used to match files.
    """
    gitignore_patterns = []

    # Walk through directory to find all .gitignore files
    for root, _, files in os.walk(str(directory)):
        if '.gitignore' in files:
            gitignore_path = os.path.join(root, '.gitignore')
            with open(gitignore_path, 'r') as f:
                # Read patterns and filter out empty lines and comments
                patterns = [line.strip() for line in f.readlines()]
                patterns = [p for p in patterns if p and not p.startswith('#')]
                gitignore_patterns.extend(patterns)

    return PathSpec.from_lines(GitWildMatchPattern, gitignore_patterns)


def list_files_recursively(directory: Path):
    """
    Recursively list all files in the given directory and its subdirectories,
    respecting .gitignore rules.
    Returns a list of file paths relative to the given directory.
    """
    # First, read all gitignore rules
    gitignore_spec = _read_gitignore(directory)
    file_list = []

    for root, _, files in os.walk(directory):
        # Get relative path from the starting directory
        relative_root = os.path.relpath(root, directory)

        for file in files:
            # Construct the relative file path
            if relative_root == '.':
                file_path = file
            else:
                file_path = os.path.join(relative_root, file)

            # Check if file should be ignored
            if not gitignore_spec.match_file(file_path):
                file_list.append(file_path)

    logger.info(f"Found {len(file_list)} files in {directory}")
    return sorted(file_list)
