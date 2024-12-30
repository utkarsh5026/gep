import os
import aiofiles

from typing import Literal, Optional
from pathlib import Path
from pathspec import PathSpec
from pathspec.patterns import GitWildMatchPattern

from pydantic import BaseModel

from logger import logger


class FileNode(BaseModel):
    """
    Represents a node in a file system tree structure.

    Attributes:
        name (str): Name of the file or directory
        type (Literal["file", "directory"]): Type of the node
        children (Optional[list[FileNode]]): List of child nodes for directories, None for files
    """
    name: str
    type: Literal["file", "directory"]
    children: Optional[list["FileNode"]] = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "src",
                    "type": "directory",
                    "children": [
                            {"name": "main.py", "type": "file"}
                    ]
                }
            ]
        }
    }


def _read_gitignore(directory: Path) -> PathSpec:
    """
    Read and combine all .gitignore files in the directory tree.

    Args:
        directory (Path): Root directory to start searching for .gitignore files

    Returns:
        PathSpec: A compiled PathSpec object containing all gitignore patterns

    Note:
        Always includes '.git/' in the ignore patterns regardless of .gitignore contents
    """
    gitignore_patterns = ['.git/']  # Always ignore .git directory

    # Walk through directory to find all .gitignore files
    for root, dirs, files in os.walk(str(directory)):
        # Skip .git directory
        if '.git' in dirs:
            dirs.remove('.git')

        if '.gitignore' in files:
            gitignore_path = os.path.join(root, '.gitignore')
            with open(gitignore_path, 'r') as f:
                patterns = [line.strip() for line in f.readlines()]
                patterns = [p for p in patterns if p and not p.startswith('#')]
                gitignore_patterns.extend(patterns)

    return PathSpec.from_lines(GitWildMatchPattern, gitignore_patterns)


def list_files_recursively(directory: Path) -> list[str]:
    """
    Recursively list all files in a directory while respecting .gitignore rules.

    Args:
        directory (Path): Root directory to start the file search

    Returns:
        list[str]: Sorted list of file paths relative to the root directory

    Example:
        >>> list_files_recursively(Path("project/"))
        ['src/main.py', 'tests/test_main.py']
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


def create_file_tree(file_paths: list[str]) -> FileNode:
    """
    Create a hierarchical file tree structure from a list of file paths.

    Args:
        file_paths (list[str]): List of file paths to organize into a tree

    Returns:
        FileNode: Root node of the created file tree

    Example:
        >>> paths = ['src/main.py', 'src/utils/helper.py']
        >>> tree = create_file_tree(paths)
        >>> tree.children[0].name  # Returns 'src'
    """
    def insert_tree_node(parent_node: FileNode, node_name: str, is_leaf: bool) -> FileNode:
        """
        Insert a new node into the tree or return existing node if found.

        Args:
            parent_node (FileNode): Node to insert under
            node_name (str): Name of the new node
            is_leaf (bool): True if node represents a file, False for directory

        Returns:
            FileNode: The inserted or existing node
        """
        existing_children = parent_node.children or []
        for existing_node in existing_children:
            if existing_node.name == node_name:
                return existing_node

        new_node = FileNode(
            name=node_name,
            type="file" if is_leaf else "directory",
            children=[] if not is_leaf else None
        )
        existing_children.append(new_node)
        parent_node.children = existing_children
        return new_node

    def sort_tree(node: FileNode):
        """
        Recursively sort the tree with directories first, then files, alphabetically.
        """
        if node.children:
            # Sort children
            node.children.sort(key=lambda x: (
                x.type == "file", x.name.lower()))
            # Recursively sort each child's children
            for child in node.children:
                sort_tree(child)

    root_node = FileNode(name="project", type="directory", children=[])
    for file_path in file_paths:
        current_node = root_node
        path_segments = Path(file_path).parts
        for position, segment in enumerate(path_segments):
            current_node = insert_tree_node(
                current_node,
                segment,
                is_leaf=(position == len(path_segments) - 1)
            )

    # Sort the entire tree after creation
    sort_tree(root_node)
    return root_node


async def read_file(file_path: Path) -> str:
    """
    Read the content of a file asynchronously.

    Args:
        file_path (Path): Path to the file to read

    Returns:
        str: The content of the file
    """
    _verify_file_exists(file_path)
    try:
        async with aiofiles.open(file_path, mode='r', encoding='utf-8') as file:
            content = await file.read()
            return content
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {file_path}")



def _verify_file_exists(file_path: Path) -> None:
    """
    Verify that a file exists, raising an error if it does not.

    Args:
        file_path (Path): Path to the file to verify
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    if not file_path.is_file():
        raise ValueError(f"Path is not a file: {file_path}")