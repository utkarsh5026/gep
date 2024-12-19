from enum import Enum, auto
from abc import ABC, abstractmethod


class PromptType(Enum):
    FILE_WISE = auto()
    AGGREGATE = auto()


class PromptProviderType(Enum):
    SEMANTIC = auto()


class PromptProvider(ABC):
    """Abstract base class for prompt providers with parsing capabilities."""

    @abstractmethod
    def get_file_wise_prompt(self, code_context: str, query: str) -> str:
        """Generate a prompt for file-wise analysis."""
        pass

    @abstractmethod
    def get_aggregate_prompt(self, code_context: str, query: str) -> str:
        """Generate a prompt for aggregate system analysis."""
        pass
