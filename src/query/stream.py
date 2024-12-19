from typing import Optional
from dataclasses import dataclass

from langchain_core.language_models.chat_models import BaseChatModel

from src.vector import EmbeddingManager
from .query import QueryProcessor
from src.prompt import PromptType, PromptProviderType


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


class StreamQueryProcessor(QueryProcessor):
    """
        Processes queries with streaming responses and early stopping.
        Builds on top of the existing embedding system but adds streaming capabilities.
    """

    def __init__(self, embedding_manager: EmbeddingManager, llm: BaseChatModel, max_results: int = 10,
                 min_relevance_score: float = 0.5, max_batch_tokens: int = 5000):
        super().__init__(embedding_manager, llm, max_results, min_relevance_score)
        self.max_batch_tokens = max_batch_tokens

    async def stream_analysis(self, query: str,
                              prompt_type: Optional[PromptType] = PromptType.AGGREGATE,
                              prompt_provider: Optional[PromptProviderType] = PromptProviderType.SEMANTIC):
        """
        Performs streaming analysis of code based on a natural language query.

        This method searches for relevant code snippets using semantic search and processes them in batches,
        streaming the analysis results as they become available.

        Args:
            query (str): The natural language query to analyze code against
            prompt_type (Optional[PromptType]): The type of prompt to use for analysis. 
                Defaults to PromptType.AGGREGATE
            prompt_provider (Optional[PromptProviderType]): The provider of prompts to use.
                Defaults to PromptProviderType.SEMANTIC

        Yields:
            StreamingResult: Chunks of analysis text as they are generated

        Raises:
            Exception: If there is an error searching the vector database or processing results
        """
        try:
            search_results = await self._get_similar_results(query)

            batch_index = 0
            curr_index = 0

            while curr_index < len(search_results):
                print(curr_index, len(search_results))
                batch = self._create_batch(curr_index, search_results)

                if not batch:
                    print("No batch found")
                    break

                prompt = self.create_prompt(query, "".join(
                    batch.contents), prompt_type, prompt_provider)

                async for chunk in self.llm.astream(prompt):
                    yield StreamingResult(
                        text=chunk.content
                    )

                curr_index = batch.metadata['end_index']
                batch_index += 1

            print(f"Streamed {curr_index} results and {batch_index} batches")
        except Exception as e:
            print(f"Error searching vector db: {e}")
            return
