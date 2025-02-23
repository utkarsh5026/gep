from typing import Any, Callable, TypeVar

import rich_click as click
from functools import wraps
from pydantic import BaseModel

from llm import LLMProviderType


class LLMConfigOptions(BaseModel):
    llm_type: LLMProviderType

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
        llm_type = LLMProviderType.parse_type_from_string(kwargs.pop("llm_type"))
        llm_options = LLMConfigOptions(
            llm_type=llm_type,
        )
        kwargs["llm_options"] = llm_options
        return f(*args, **kwargs)
    return wrapper