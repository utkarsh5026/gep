import re
import asyncio

from dataclasses import dataclass
from typing import Any, Optional, AsyncGenerator
from enum import Enum, auto
from pathlib import Path

from langchain_core.language_models import BaseLanguageModel
from langchain_core.messages import BaseMessage

from src.vector import EmbeddingManager, SearchResult
from .pattern import COMMON_PATTERNS
from .prompt import PromptProviderType, PromptType, get_prompt_function


class QueryType(Enum):
    SEMANTIC = auto()
    CODE_PATTERN = auto()
    SECURITY = auto()
    CODE_CHANGE = auto()


@dataclass
class AnalysisBatch:
    """Represents a batch of code for analysis."""
    files: list[str]
    contents: list[str]
    total_chars: int
    metadata: dict[str, Any]


class QueryProcessor:
    """
    Handles query processing and analysis for the embedding system.
    Works with the IntegratedEmbeddingManager to search and analyze code.

    Query Text → Query Embedding → Vector Store Search → Filter Results → LLM Analysis
            (embedding model)   (similarity search)  (score-based)   (explanation)
    """

    def __init__(self, embedding_manager: EmbeddingManager,
                 llm: BaseLanguageModel,
                 max_results: int = 10,
                 min_relevance_score: float = 0.5,
                 max_batch_tokens: float = 5000) -> None:
        self.embedding_manager = embedding_manager
        self.llm = llm
        self.max_results = max_results
        self.min_relevance_score = min_relevance_score
        self.max_batch_tokens = max_batch_tokens

    async def process_query(self, query: str,
                            prompt_type: Optional[PromptType] = PromptType.AGGREGATE,
                            prompt_provider: Optional[PromptProviderType] = PromptProviderType.SEMANTIC,
                            filters: Optional[list[str]] = None) -> AsyncGenerator[BaseMessage | str, None]:
        """
        Process a query asynchronously and yield analysis results in batches.

        This method performs the following steps:
        1. Searches for similar code sections using the query
        2. Creates batches of code for analysis based on token limits
        3. Generates prompts using the specified prompt type and provider
        4. Invokes the LLM for analysis and yields results incrementally

        Args:
            query (str): The search query to find relevant code sections
            prompt_type (Optional[PromptType]): The type of prompt to use for analysis.
                Defaults to PromptType.AGGREGATE.
            prompt_provider (Optional[PromptProviderType]): The provider for prompt templates.
                Defaults to PromptProviderType.SEMANTIC.
            filters (Optional[list[str]]): Optional filters to apply when searching for code.
                Can include file paths, extensions, or other metadata filters.

        Yields:
            AsyncGenerator[BaseMessage | str, None]: Stream of analysis results from the LLM.
                Results can be either BaseMessage objects or strings depending on the LLM response type.

        Raises:
            Exception: If there are errors during search, batch processing, or LLM invocation.
                The original exception is re-raised after logging.
        """
        try:
            search_results = await self._get_similar_results(query, filters)

            batch_index = 0
            while batch_index < len(search_results):
                batch = self._create_batch(batch_index, search_results)
                if not batch:
                    break

                prompt = self.create_prompt(query, "".join(batch.contents), prompt_type, prompt_provider)

                llm_response = await self.llm.ainvoke(prompt)
                yield llm_response
                batch_index = batch.metadata['end_index']

        except Exception as e:
            print(f"Error processing query: {e}")
            raise e

    async def __search_vector_db(self, query: str, filters: Optional[list[str]] = None):
        """
        Search the vector database for relevant results.
        """

        return await self.embedding_manager.similarity_search(
            query=query,
            limit=self.max_results * 2,
            filter=filters,
        )

    async def _get_similar_results(self, query: str, filters: Optional[list[str]] = None):
        """
        Retrieves and processes similar code results for a given query.

        Args:
            query (str): The search query to find similar code sections
            filters (Optional[list[str]]): Optional list of filters to apply to the search results

        Returns:
            list[SearchResult]: List of processed and filtered search results that meet the
                              minimum relevance score threshold. Each result contains:
                              - text: The preprocessed code content
                              - source_file: Path to the source file
                              - score: Similarity score between 0 and 1

        The function performs the following steps:
        1. Searches the vector database for similar code sections
        2. Preprocesses each result's code content while preserving structure
        3. Filters out results below the minimum relevance score threshold
        4. Returns the processed and filtered results
        """
        search_results = await self.__search_vector_db(query, filters)

        async def process_result(result):
            code = result.text
            result.text = self.preprocess_code(code, result.source_file)
            return result if result.score >= self.min_relevance_score else None

        processed_results = await asyncio.gather(
            *[process_result(result) for result in search_results]
        )
        filtered_results = [r for r in processed_results if r is not None]

        return filtered_results

    def _create_batch(self, start_idx: int, processed_results: list[SearchResult]) -> AnalysisBatch | None:
        """
            Creates a batch of code for analysis.

            Parameters:
                start_idx: The index of the first result to include in the batch
                processed_results: List of processed search results

            Returns:
                AnalysisBatch: A batch of code for analysis or None if no results are left
        """
        if start_idx >= len(processed_results):
            print("No results left", start_idx, len(processed_results))
            return None

        batch_files: list[str] = []
        batch_contents: list[str] = []
        total_chars: int = 0
        curr_idx = start_idx

        def process_result(rs: SearchResult, curr_chars: int, force_add: bool = False) -> int:
            """
                Processes a result and adds it to the batch.
                Returns the number of characters added or -1 if the result is not added.
            """
            file_content = f"\nFile: {
            rs.source_file}\nContent:\n{rs.text}\n"

            if not force_add and curr_chars + len(file_content) > self.max_batch_tokens:
                return -1

            batch_files.append(rs.source_file)
            batch_contents.append(file_content)
            return len(file_content)

        while curr_idx < len(processed_results) and total_chars < self.max_batch_tokens:
            result = processed_results[curr_idx]
            chars_count = process_result(result, total_chars)
            if chars_count == -1:
                break
            total_chars += chars_count
            curr_idx += 1

        if not batch_files:
            result = processed_results[curr_idx]
            total_chars = process_result(result, total_chars, force_add=True)
            curr_idx += 1

        return AnalysisBatch(
            files=batch_files,
            contents=batch_contents,
            total_chars=total_chars,
            metadata={
                'end_index': curr_idx,
                'start_index': start_idx,
                'total_results': len(processed_results)
            }
        )

    @classmethod
    def detect_language(cls, file_path: str) -> str:
        """Detect the programming language based on file extension and content."""
        ext = Path(file_path).suffix.lower()
        ext_to_lang = {
            '.py': 'python',
            '.js': 'javascript',
            '.java': 'java',
            '.go': 'go',
            '.rs': 'rust',
            '.ts': 'javascript',
            '.jsx': 'javascript',
            '.tsx': 'javascript',
            '.c': 'c',
            '.cpp': 'cpp',
            '.h': 'c',
            '.hpp': 'cpp',
            '.cs': 'csharp',
            '.php': 'php',
            '.rb': 'ruby',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.ktm': 'kotlin',
            '.html': 'html',
            '.css': 'css',
            '.scss': 'css',
            '.sass': 'css',
            '.less': 'css'
        }
        return ext_to_lang.get(ext, 'unknown')

    @classmethod
    def preprocess_code(cls, code: str, file_path: str) -> str:
        """
        Preprocess code while preserving its essential structure and readability.
        Handles different programming languages appropriately.
        """
        if not code.strip():
            return code

        language = cls.detect_language(file_path)
        indent_pattern = re.compile(r'^[ \t]+', re.MULTILINE)
        indents = indent_pattern.findall(code)

        if language in COMMON_PATTERNS['block_comments']:
            code = re.sub(
                COMMON_PATTERNS['block_comments'][language],
                '',
                code
            )

        if language in COMMON_PATTERNS['inline_comments']:
            code = re.sub(
                COMMON_PATTERNS['inline_comments'][language],
                '',
                code
            )

        code = re.sub(COMMON_PATTERNS['empty_lines'], '\n', code)
        code = re.sub(
            COMMON_PATTERNS['trailing_whitespace'], '', code, flags=re.MULTILINE)
        code = re.sub(COMMON_PATTERNS['multiple_spaces'], ' ', code)

        lines = code.split('\n')
        for i, indent in enumerate(indents):
            if i < len(lines):
                lines[i] = indent + lines[i].lstrip()

        return '\n'.join(lines)

    @classmethod
    def create_prompt(cls, query: str, content: str, prompt_type: PromptType,
                      prompt_provider: PromptProviderType) -> str:
        """
        Create a prompt for the language model based on the query and code content.
        """
        prompt_func = get_prompt_function(prompt_type, prompt_provider)
        return prompt_func(query, content)
