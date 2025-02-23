from typing import Any, AsyncGenerator, Optional
from pydantic import BaseModel, Field, field_validator

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate

from git_repo.repo import Repository
from llm import  LLMProviderType

class CommitOptions(BaseModel):
    commit_count: int = Field(description="Number of commits to analyze")
    branch_name: Optional[str] = Field(description="Name of the branch to analyze")
    author: Optional[str] = Field(description="Author of the commits")


class CommitHistoryAnalyzer:
    """
    Analyzes Git commit history to provide insights about code evolution.
    
    This class uses LLM capabilities to analyze commit patterns, identify
    significant changes, and provide meaningful insights about how the
    codebase has evolved over time.
    """

    _history_analysis_template = PromptTemplate(
        input_variables=["commit_history"],
        template="""Analyze the provided commit history to provide insights about code evolution.

        Return your analysis in a single markdown bullet list.
        """
    )

    _commit_history_analysis = PromptTemplate(
            input_variables=["commit_messages"],
            template="""
            Analyze these commit messages:
            
            {commit_messages}
            
            Please identify:
            1. Common patterns in development workflow
            2. Quality of commit messages
            3. Adherence to commit message conventions
            4. Areas where commit practices could be improved
            """
        )

    def __init__(self, repo: Repository) -> None:
        self._repo = repo

    
    async def analyze_commit_history(self, options: CommitOptions, provider: LLMProviderType) -> AsyncGenerator[str, Any]:
        """
        Analyze a sequence of commits to understand code evolution patterns.
        """

        commit_history = [ch.message for ch in self._repo.get_commit_history(
            max_count=options.commit_count,
            branch_name=options.branch_name,
        )]


        llm = LLMProviderType.get_llm(provider)
        chain = self._commit_history_analysis | llm | StrOutputParser()
        async for result in chain.astream({"commit_messages": commit_history}):
            yield result



        