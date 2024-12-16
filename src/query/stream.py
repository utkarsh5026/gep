from typing import AsyncGenerator
from dataclasses import dataclass

from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.language_models.chat_models import BaseChatModel


from src.vector.manager import EmbeddingManager
from .query import QueryProcessor, QueryType


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

    def __init__(self, embedding_manager: EmbeddingManager, llm: BaseChatModel, max_results: int = 10, min_relevance_score: float = 0.5):
        super().__init__(embedding_manager, llm, max_results, min_relevance_score)

    async def stream_query_result(self, query: str, query_type: QueryType) -> AsyncGenerator[str, None]:
        """
        Process a query and stream results as they become available.
        Stops early if enough relevant results are found.
        """
        search_results = await self.search_vector_db(query)
        prompt = self.prompts[query_type]

        chain = (
            RunnablePassthrough() | prompt | self.llm.with_config(
                {"callbacks": []}) | StrOutputParser()
        )

        found_count = 0
        for result in search_results:
            if found_count >= self.max_results:
                break

            if result.score < self.min_relevance_score:
                continue

            context = {
                "query": query,
                "code_contexts": result.text,
                "file_path": result.metadata.get("source", "unknown"),
            }

            try:

                async for chunk in chain.astream(context):
                    streaming_result = StreamingResult(
                        text=chunk,
                        source_file=context["file_path"],
                        relevance_score=result.score
                    )
                    yield streaming_result

                found_count += 1
                if found_count >= self.max_results:
                    break

            except Exception as e:
                print(f"Error processing result: {e}")
                continue
