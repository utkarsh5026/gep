from langchain_core.prompts import PromptTemplate
from enum import Enum, auto
from abc import ABC, abstractmethod


class PromptType(Enum):
    FILE_WISE = auto()
    AGGREGATE = auto()


class PromptProviderType(Enum):
    SEMANTIC = auto()


class PromptProvider(ABC):

    @abstractmethod
    def get_file_wise_prompt(self, code_context: str, query: str) -> str:
        pass

    @abstractmethod
    def get_aggregate_prompt(self, code_context: str, query: str) -> str:
        pass


class SemanticPromptProvider(PromptProvider):

    def get_file_wise_prompt(self, code_context: str, query: str) -> str:
        return f"""
        Analyze each file in the following code independently to understand its specific purpose and implementation.

        Query Focus: {query}

        Code Context:
        {code_context}

        Provide a detailed analysis for each file using this structure:

        [FILE]
        File Path: [file path]

        Key Concepts:
        - Main programming concepts and patterns used in this file
        - Primary abstractions and data structures
        - Core algorithms and techniques implemented here

        Code Flow:
        - Step-by-step execution flow within this file
        - Important control structures and their purpose
        - Key function interactions within the file

        Dependencies:
        - External library dependencies used directly in this file
        - Internal module dependencies specific to this file
        - Interfaces implemented or used by this file

        Implementation Notes:
        - Notable implementation decisions in this file
        - File-specific optimizations or techniques
        - Error handling approaches used here
        [END_FILE]

        Focus on understanding each file's individual role and implementation details.
        Analyze each file completely before moving to the next one.
        """

    def get_aggregate_prompt(self, code_context: str, query: str) -> str:
        return f"""
        Analyze the following code as a complete system to understand its overall architecture and interactions.

        Query Focus: {query}

        Code Context:
        {code_context}

        Provide a comprehensive system analysis using this structure:

        [SYSTEM_ANALYSIS]
        Files Analyzed:
        - List all files being analyzed

        System Architecture:
        - Overall system design patterns
        - Main architectural components
        - System-wide design decisions

        Cross-file Patterns:
        - Common patterns used across files
        - Shared coding conventions
        - Consistent implementation approaches

        Component Interactions:
        - How different parts of the system work together
        - Data flow between components
        - Key integration points

        Shared Dependencies:
        - Common external dependencies
        - Shared internal utilities
        - Core interfaces used across the system

        System Insights:
        - Notable system-wide characteristics
        - Architectural strengths and considerations
        - Overall implementation approach
        [END_SYSTEM_ANALYSIS]

        Focus on how the components work together as a system rather than individual implementations.
        Emphasize relationships and interactions between different parts of the codebase.
        """


def get_provider(prompt_type: PromptProviderType) -> PromptProvider:
    if prompt_type == PromptProviderType.SEMANTIC:
        return SemanticPromptProvider()


def get_prompt_function(prompt_type: PromptType, prompt_provider: PromptProviderType):
    provider = get_provider(prompt_provider)
    if prompt_type == PromptType.FILE_WISE:
        return provider.get_file_wise_prompt
    elif prompt_type == PromptType.AGGREGATE:
        return provider.get_aggregate_prompt
