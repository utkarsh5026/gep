import aiofiles
from pathlib import Path
from typing import Literal

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
