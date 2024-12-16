from dataclasses import dataclass
from typing import Any, Optional
from enum import Enum, auto
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

from src.vector import EmbeddingManager


@dataclass
class QueryResult:
    source_files: list[str]
    relevant_texts: list[str]
    analysis: str
    relevance_scores: list[float]
    metadata: dict[str, Any]


class QueryType(Enum):
    SEMANTIC = auto()
    CODE_PATTERN = auto()
    SECURITY = auto()
    CODE_CHANGE = auto()


class QueryProcessor:
    """
    Handles query processing and analysis for the embedding system.
    Works with the IntegratedEmbeddingManager to search and analyze code.

    Query Text → Query Embedding → Vector Store Search → Filter Results → LLM Analysis
            (embedding model)   (similarity search)  (score-based)   (explanation)
    """

    def __init__(self, embedding_manager: EmbeddingManager, llm: ChatOpenAI, max_results: int = 10, min_relevance_score: float = 0.5) -> None:
        self.embedding_manager = embedding_manager
        self.llm = llm
        self.max_results = max_results
        self.min_relevance_score = min_relevance_score
        self.prompts = self.__init_prompts()

    def __init_prompts(self) -> dict[QueryType, PromptTemplate]:
        """
        Creates specialized prompts for different types of queries.
        Each prompt is designed to guide the AI in analyzing code in a specific way.
        """

        return {
            QueryType.SEMANTIC: PromptTemplate(
                input_variables=["query", "code_contexts"],
                template="""
                Analyze these code sections for relevance to the query.
                Query: {query}
                
                Code Contexts:
                {code_contexts}
                
                Provide a detailed analysis including:
                1. How each section relates to the query
                2. Key implementation details
                3. Any notable patterns or practices
                4. Suggestions for understanding or using this code
                """
            ),
            QueryType.CODE_PATTERN: PromptTemplate(
                input_variables=["query", "code_contexts"],
                template="""
                Analyze these code implementations for the requested pattern.
                Query: {query}
                
                Code Contexts:
                {code_contexts}
                
                Provide a technical analysis covering:
                1. Implementation patterns used
                2. Function signatures and interfaces
                3. Error handling approaches
                4. Dependencies and coupling
                5. Potential optimizations
                """
            ),
        }

    async def process_query(self, query: str, query_type: QueryType, filters: Optional[list[str]] = None) -> QueryResult:
        """
        Process a query and return analyzed results.

        This method coordinates between the vector store search and AI analysis
        to provide comprehensive results.
        """

        try:

            search_results = await self.embedding_manager.similarity_search(
                query=query,
                limit=self.max_results,
                filter=filters,
            )

            filtered_results = [
                (search_result.text, search_result.score, search_result.metadata) for search_result in search_results if search_result.score >= self.min_relevance_score
            ]

            if not filtered_results:
                return QueryResult(
                    source_files=[],
                    relevant_texts=[],
                    analysis="No relevant results found.",
                    relevance_scores=[],
                    metadata={},
                )

            code_contexts = "\n\n".join([
                f"File: {meta['source']}\n"
                f"Content:\n{text}\n"
                for text, _, meta in filtered_results
            ])
            prompt = self.prompts[query_type]
            analysis_prompt = prompt.format(
                query=query,
                code_contexts=code_contexts
            )

            llm_response = await self.llm.ainvoke(analysis_prompt)

            return QueryResult(
                source_files=[],
                relevant_texts=[text for text, _, _ in filtered_results],
                analysis=llm_response,
                relevance_scores=[],
                metadata={},
            )

        except Exception as e:
            print(f"Error processing query: {e}")
            raise e
