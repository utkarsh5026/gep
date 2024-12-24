import os
from pathlib import Path
from multiprocessing import Pool


def create_file_content_map(root_dir: str, ignore_patterns: list[str] = [], accept_patterns: list[str] = []) -> dict[str, str]:
    """Read files from the root directory and create a map of file paths to their contents.
    if accept_patterns is provided, only files matching the patterns will be included.
    if ignore_patterns is provided, files matching the patterns will be ignored.
    """
    root_dir = Path(root_dir).resolve()

    valid_files = []
    for file in root_dir.rglob("*"):
        if file.is_dir():
            continue

        if _is_valid_file(file, ignore_patterns, accept_patterns):
            valid_files.append(file)

    print(f"Found {len(valid_files)} valid files")

    with Pool(processes=os.cpu_count()) as pool:
        results = pool.map(_read_file, valid_files)

    return dict(results)


def _read_file(file_path: Path) -> tuple[Path, str]:
    """Helper function to read a single file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return file_path, f.read()


def _is_valid_file(file: Path, ignore_patterns: list[str], accept_patterns: list[str]) -> bool:
    """
    Determine if a file should be included based on accept and ignore patterns.

    Args:
        file: Path object representing the file
        ignore_patterns: List of patterns to ignore
        accept_patterns: List of patterns to accept

    Returns:
        bool: True if file should be included, False otherwise
    """
    # First check accept patterns
    is_accepted = False
    if accept_patterns:
        is_accepted = any(file.match(pattern) for pattern in accept_patterns)
        if not is_accepted:
            return False

    # Then check ignore patterns
    if ignore_patterns and any(file.match(pattern) for pattern in ignore_patterns):
        return False

    return True
