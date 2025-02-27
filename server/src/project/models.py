from pydantic import BaseModel, Field
from pathlib import Path


class FileInfo(BaseModel):
    name: str = Field(description="The name of the file")
    rel_file_path: str = Field(description="The relative path of the file")
    directory: Path = Field(description="The directory of the file")
    extension: str = Field(description="The extension of the file")
    size: int = Field(description="The size of the file")
