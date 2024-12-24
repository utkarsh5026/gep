from dataclasses import dataclass

from .prompt import PromptProvider


class SemanticPromptProvider(PromptProvider):

    def get_file_wise_prompt(self, code_context: str, query: str) -> str:
        return f"""
        Analyze the code in each file to identify and explain important code sections.
        Focus on sections that are critical to understanding the system's functionality.

        Query Focus: {query}

        Code Context:
        {code_context}

        For each file, provide analysis in this format:

        [FILE_ANALYSIS]
        File Path: [file path]

        Summary:
        Brief overview of the file's purpose and role in the system.

        Key Concepts:
        - List the main programming concepts and patterns used
        - Focus on unique or notable implementations

        Important Code Sections:
        [SECTION]
        Code:
        ```
        <relevant code snippet>
        ```
        Explanation:
        Detailed explanation of what this code does and why it's important

        Importance Level: [CRITICAL/HIGH/MEDIUM]
        Related Components:
        - List of related components or files
        [END_SECTION]

        Dependencies:
        - External libraries and internal modules used
        - Why each dependency is needed

        Implementation Notes:
        - Notable implementation decisions
        - Potential areas for improvement
        [END_FILE_ANALYSIS]

        Focus on the most important sections of code that answer the query or are critical to system functionality.
        """

    def get_aggregate_prompt(self, code_context: str, query: str) -> str:
        return f"""
        Analyze the following code as a complete system, focusing on critical components and their interactions.

        Query Focus: {query}

        Code Context:
        {code_context}

        Provide analysis in this format:

        [SYSTEM_ANALYSIS]
        Files Analyzed:
        - List all analyzed files

        Critical Components:
        [COMPONENT]
        Location: [file path and location]
        Code:
        ```
        <critical code snippet>
        ```
        Purpose:
        Explanation of this component's role and importance

        Interactions:
        - How this component interacts with others
        - Key integration points
        [END_COMPONENT]

        System Architecture:
        - Overall design patterns used
        - Main architectural decisions
        - System-wide patterns

        Component Interactions:
        - Key interaction patterns
        - Data flow between components
        - Important interfaces

        Shared Dependencies:
        - Common external dependencies
        - Shared internal utilities
        - Core interfaces used across files
        [END_SYSTEM_ANALYSIS]

        Focus on identifying and explaining the most critical code sections that are essential to understanding the system.
        """
