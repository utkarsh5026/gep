import os
from pathlib import Path
from .models import FileInfo
from .scan import RepoScanner
from .loader import get_appropriate_loader, get_chunking_strategy


class Project:

    PROJECT_DIR_NAME = ".gep"

    @classmethod
    async def find_root_and_init(cls):
        """
        Find the root directory of the project and initialize the project
        """
        current_dir = Path.cwd().resolve()
        while not (current_dir / ".git").exists():
            if current_dir == current_dir.parent:
                raise ValueError("No git repository found")
            current_dir = current_dir.parent
        print(f"Found project root: {current_dir}")
        return cls(current_dir)

    @property
    def vector_db_path(self):
        return self.repo_path / self.PROJECT_DIR_NAME / "vector_db"

    def __init__(self, repo_path: Path):
        self.repo_scanner = RepoScanner(repo_path)

    async def vectorize(self):
        repo_struct = await self.repo_scanner.scan()
        structure_text = self.prepare_structure_for_llm(repo_struct)
        return structure_text

    @classmethod
    def prepare_structure_for_llm(cls, file_info: list[FileInfo]):
        """
        Prepare a user-friendly representation of the project structure for LLM processing.

        Args:
            file_info (list[FileInfo]): A list of FileInfo objects representing the files in the project.

        Returns:
            str: A formatted string that outlines the project structure, including directories and files.
                  The structure is represented in a hierarchical format, with indentation indicating 
                  the level of each directory. If a directory contains more than 10 files, only the 
                  first 5 and the last 4 files are shown, with an ellipsis in between to indicate 
                  omitted files.
        """
        files_by_directory = {}
        for file in file_info:
            dir_path = file.directory
            if dir_path not in files_by_directory:
                files_by_directory[dir_path] = []
            files_by_directory[dir_path].append(file.name)

        structure_text = ["# Project Structure\n"]
        sorted_dirs = sorted(files_by_directory.keys())
        for dir_path in sorted_dirs:
            if str(dir_path).count('/') > 4:
                continue

            indent = '  ' * str(dir_path).count('/')
            file_name = os.path.basename(dir_path) or 'root'
            structure_text.append(f"{indent}- {file_name}:")

            files = sorted(files_by_directory[dir_path])
            if len(files) > 10:
                shown_files = files[:5] + ["..."] + files[-4:]
            else:
                shown_files = files

            for file in shown_files:
                structure_text.append(f"{indent}  - {file}")

        return "\n".join(structure_text)
