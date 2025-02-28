from pydantic import BaseModel, Field, computed_field
from pathlib import Path


class FileInfo(BaseModel):
    """
    A class representing information about a file in a repository.

    This model provides details about a file's name, relative path, directory, size,
    and computed properties such as file path, extension, and file name without extension.
    """

    name: str = Field(description="The name of the file")

    rel_file_path: str = Field(description="The relative path of the file")

    directory: Path = Field(description="The directory of the file")

    size: int = Field(description="The size of the file")

    @computed_field
    @property
    def file_path(self) -> Path:
        return self.directory / self.name

    @computed_field
    @property
    def extension(self) -> str:
        return self.file_path.suffix

    @computed_field
    @property
    def file_name_without_extension(self) -> str:
        return self.file_path.stem
