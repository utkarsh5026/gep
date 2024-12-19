import re
import asyncio

from dataclasses import dataclass
from typing import Any, Optional
from enum import Enum, auto
from pathlib import Path


from langchain_core.prompts import PromptTemplate
from langchain_core.language_models import BaseLanguageModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, Runnable

from src.vector import EmbeddingManager, SearchResult
from .pattern import COMMON_PATTERNS
from .prompt import PromptProviderType, get_provider


@dataclass
class QueryResult:
    source_files: list[str]
    relevant_texts: list[str]
    analysis: str | dict[str, str]
    relevance_scores: list[float]
    metadata: dict[str, Any]


class QueryType(Enum):
    SEMANTIC = auto()
    CODE_PATTERN = auto()
    SECURITY = auto()
    CODE_CHANGE = auto()


class AnalysisType(Enum):
    FILE_WISE = auto()
    AGGREGATE = auto()


class QueryProcessor:
    """
    Handles query processing and analysis for the embedding system.
    Works with the IntegratedEmbeddingManager to search and analyze code.

    Query Text → Query Embedding → Vector Store Search → Filter Results → LLM Analysis
            (embedding model)   (similarity search)  (score-based)   (explanation)
    """

    def __init__(self, embedding_manager: EmbeddingManager, llm: BaseLanguageModel, max_results: int = 10, min_relevance_score: float = 0.5) -> None:
        self.embedding_manager = embedding_manager
        self.llm = llm
        self.max_results = max_results
        self.min_relevance_score = min_relevance_score

    async def process_query(self, query: str, query_type: QueryType, filters: Optional[list[str]] = None) -> QueryResult:
        """
        Process a query and return analyzed results.

        This method coordinates between the vector store search and AI analysis
        to provide comprehensive results.
        """

        try:

            search_results = await self._get_similar_results(query, filters)
            code_contexts = self.__prepare_code_context(search_results)

            prompt = self.prompts[query_type]
            analysis_prompt = prompt.format(
                query=query,
                code_contexts=code_contexts
            )

            llm_response = await self.llm.ainvoke(analysis_prompt)

            return QueryResult(
                source_files=[],
                relevant_texts=[text for text, _, _ in search_results],
                analysis=llm_response,
                relevance_scores=[],
                metadata={},
            )

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

    def __prepare_code_context(self, search_results: list[SearchResult]) -> str:
        """
        Prepare code context for analysis.
        """

        return "\n\n".join([
            f"File: {source_file}\n"
            f"Content:\n{text}\n"
            for text, source_file, _ in search_results
        ])

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
