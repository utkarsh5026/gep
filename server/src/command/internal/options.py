from typing import Any, Callable, TypeVar

import rich_click as click
from functools import wraps
from pydantic import BaseModel

from llm import LLMProviderType


class LLMConfigOptions(BaseModel):
    llm_type: LLMProviderType


class FileOptions(BaseModel):
    file_path: str
    pattern: str
    recursive: bool


F = TypeVar('F', bound=Callable[..., Any])


def with_llm_options(f: Callable) -> Callable:
    """
    Decorator to add LLM-related options to a command.
    This combines with other Click options
    """
    @click.option(
        "--llm-type",
        type=click.Choice(LLMProviderType.list_names()),
        default="gpt-4o-mini",
        help="Type of LLM to use for analysis",
        show_default=True
    )
    @wraps(f)
    def wrapper(*args, **kwargs):
        llm_type = LLMProviderType.parse_type_from_string(
            kwargs.pop("llm_type"))
        llm_options = LLMConfigOptions(
            llm_type=llm_type,
        )
        kwargs["llm_options"] = llm_options
        return f(*args, **kwargs)
    return wrapper


def with_file_options(f: Callable) -> Callable:
    """
    Decorator to add file-related options to a command.
    This combines with other Click options
    """
    @click.option(
        "--file-path",
        "-f",
        type=click.Path(exists=True),
        help="The path to the file or the directory that you want to analyze"
    )
    @click.option(
        "--pattern",
        "-p",
        type=str,
        help="The pattern to use to match the files like *.py, *.md, etc."
    )
    @click.option(
        "--recursive",
        "-r",
        is_flag=True,
        help="If the file is a directory, analyze all files in the directory recursively"
    )
    @wraps(f)
    def wrapper(*args, **kwargs):
        file_path = kwargs.pop("file_path")
        pattern = kwargs.pop("pattern")
        recursive = kwargs.pop("recursive")
        file_options = FileOptions(
            file_path=file_path,
            pattern=pattern,
            recursive=recursive
        )
        kwargs["file_options"] = file_options
        return f(*args, **kwargs)
    return wrapper
