import aiofiles
from pathlib import Path
from typing import Literal, List
from pathspec import PathSpec

TextMode = Literal[
    'w', 'wt', 'tw',      # Write text
    'a', 'at', 'ta',      # Append text
    'x', 'xt', 'tx',      # Exclusive text
    'w+', 'wt+', 'tw+',   # Write and read text
    'a+', 'at+', 'ta+',   # Append and read text
    'x+', 'xt+', 'tx+'    # Exclusive and read text
]


async def read_file(
        file_path: Path,
        encoding: str = 'utf-8',
        errors: str = 'strict'
) -> str:
    """
    Read a file and return its content as a string

    Args:
        file_path (Path): Path to the file to read
        encoding (str, optional): File encoding. Defaults to 'utf-8'.
        errors (str, optional): How to handle encoding errors. Defaults to 'strict'.
                              Options: 'strict', 'ignore', 'replace'

    Returns:
        str: Content of the file

    Raises:
        FileNotFoundError: If the file doesn't exist
        PermissionError: If the file can't be accessed
        IOError: For other IO-related errors
    """
    try:
        async with aiofiles.open(
                file=file_path,
                mode='r',
                encoding=encoding,
                errors=errors
        ) as file:
            return await file.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {file_path}")
    except PermissionError:
        raise PermissionError(f"Permission denied: {file_path}")
    except IOError as e:
        raise IOError(f"Error reading file {file_path}: {str(e)}")


async def write_file(
        file_path: Path,
        content: str,
        encoding: str = 'utf-8',
        errors: str = 'strict',
        mode: TextMode = 'w'
) -> None:
    """
Write content to a file

    Args:
        file_path (Path): Path to the file to write
        content (str): Content to write to the file
        encoding (str, optional): File encoding. Defaults to 'utf-8'.
        errors (str, optional): How to handle encoding errors. Defaults to 'strict'.
                              Options: 'strict', 'ignore', 'replace'
        mode (str, optional): Write mode. Defaults to 'w'.
                            Options:
                            - 'w': Write (overwrite existing content)
                            - 'a': Append to existing content
                            - 'x': Exclusive creation (fail if file exists)

    Raises:
        FileExistsError: If mode is 'x' and file already exists
        PermissionError: If the file can't be accessed or created
        IOError: For other IO-related errors
        UnicodeEncodeError: If the content cannot be encoded with specified encoding
    """

    try:
        async with aiofiles.open(
                file=file_path,
                mode=mode,
                encoding=encoding,
                errors=errors
        ) as file:
            await file.write(content)

    except FileExistsError:
        raise FileExistsError(
            f"File already exists and mode is 'x' (exclusive creation): {
                file_path}"
        )
    except PermissionError:
        raise PermissionError(
            f"Permission denied: Cannot write to {file_path}"
        )
    except UnicodeEncodeError as e:
        raise UnicodeEncodeError(
            e.encoding,
            e.object,
            e.start,
            e.end,
            f"Failed to encode content for file {
                file_path} with encoding '{encoding}'. "
            f"Original error: {str(e)}")


async def parse_gitignore(root_dir: Path) -> List[str]:
    """
    Parse all .gitignore files in the given directory and its subdirectories.
    Returns a list of ignore patterns.

    Args:
        root_dir (Path): Root directory to start searching from

    Returns:
        list[str]: List of unique gitignore patterns

    Raises:
        FileNotFoundError: If root_dir doesn't exist
        PermissionError: If directories can't be accessed
    """
    if not root_dir.exists():
        raise FileNotFoundError(f"Directory not found: {root_dir}")
    if not root_dir.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {root_dir}")

    ignore_patterns = set()
    
    # Process all .gitignore files in the directory tree
    async def process_directory(directory: Path):
        try:
            gitignore_file = directory / '.gitignore'
            if gitignore_file.is_file():
                content = await read_file(gitignore_file)
                # Process each line in the .gitignore file
                for line in content.splitlines():
                    # Skip empty lines and comments
                    line = line.strip()
                    if line and not line.startswith('#'):
                        ignore_patterns.add(line)
            
            # Recursively process subdirectories
            for item in directory.iterdir():
                if item.is_dir() and not item.name.startswith('.'):
                    await process_directory(item)
        except PermissionError:
            print(f"Warning: Permission denied accessing {directory}")
        except Exception as e:
            print(f"Warning: Error processing {directory}: {str(e)}")
    
    await process_directory(root_dir)
    return sorted(list(ignore_patterns))
