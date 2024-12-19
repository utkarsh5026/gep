import asyncio

from typing import AsyncGenerator, Any, Optional
from dataclasses import dataclass

from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.language_models.chat_models import BaseChatModel
from langchain.output_parsers import StructuredOutputParser


from src.vector import EmbeddingManager, SearchResult
from .query import QueryProcessor, QueryType
from .prompt import PromptType, PromptProviderType, get_prompt_function


@dataclass
class AnalysisBatch:
    """Represents a batch of code for analysis."""
    files: list[str]
    contents: list[str]
    total_chars: int
    metadata: dict[str, Any]


@dataclass
class CodeAnalysis:
    """Represents the semantic analysis of code."""
    file_path: str
    key_concepts: list[str]
    code_flow: list[str]
    dependencies: list[str]
    implementation_notes: list[str]


@dataclass
class StreamingResult:
    text: str
    source_file: str
    relevance_score: float


class StreamQueryProcessor(QueryProcessor):

    """
        Processes queries with streaming responses and early stopping.
        Builds on top of the existing embedding system but adds streaming capabilities.
    """

    def __init__(self, embedding_manager: EmbeddingManager, llm: BaseChatModel, max_results: int = 10, min_relevance_score: float = 0.5, max_batch_tokens: int = 5000):
        super().__init__(embedding_manager, llm, max_results, min_relevance_score)
        self.max_batch_tokens = max_batch_tokens

    def __create_batch(self, start_idx: int, processed_results: list[SearchResult]) -> AnalysisBatch | None:
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

        def process_result(result: SearchResult, curr_chars: int, force_add: bool = False) -> int:
            """
                Processes a result and adds it to the batch.
                Returns the number of characters added or -1 if the result is not added.
            """
            file_content = f"\nFile: {
                result.source_file}\nContent:\n{result.text}\n"

            if not force_add and curr_chars + len(file_content) > self.max_batch_tokens:
                return -1

            batch_files.append(result.source_file)
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

    async def stream_ananlysis(self, query: str,
                               prompt_type: Optional[PromptType] = PromptType.AGGREGATE, prompt_provider: Optional[PromptProviderType] = PromptProviderType.SEMANTIC):
        """
        Stream analysis results as they become available.
        Processes code in batches and returns structured analysis.
        """

        try:
            search_results = await self._get_similar_results(query)
            print(len(search_results))

            batch_index = 0
            curr_index = 0

            prompt_func = get_prompt_function(prompt_type, prompt_provider)
            while curr_index < len(search_results):
                print(curr_index, len(search_results))
                batch = self.__create_batch(curr_index, search_results)

                if not batch:
                    print("No batch found")
                    break

                prompt = prompt_func(
                    query=query,
                    code_context="".join(batch.contents))

                result = await self.llm.ainvoke(prompt)
                yield result

                curr_index = batch.metadata['end_index']
                batch_index += 1

            print(f"Streamed {curr_index} results and {batch_index} batches")
        except Exception as e:
            print(f"Error searching vector db: {e}")
            return
