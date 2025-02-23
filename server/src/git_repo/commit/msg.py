from typing import AsyncGenerator, Dict, List, Optional
from dataclasses import dataclass
from pathlib import Path

from pydantic import Field, BaseModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from git_repo.repo import Repository
from llm import LLMProviderType


class CommitSuggestion(BaseModel):
    """Structure for holding a commit message suggestion with context."""
    subject: str    # The main commit message
    details: str    # Additional details about the changes
    reasoning: str  # The LLM's explanation of why it chose this message

class LLMCommitGenerator:
    """
    A commit message generator that uses an LLM to create meaningful
    commit messages based on the actual changes in the code.
    """
    
    def __init__(
        self,
        repo: Repository,
        model_name: str = "gpt-3.5-turbo",
        temperature: float = 0.7,
        llm_provider: Optional[LLMProviderType] = None
    ):
        """
        Initialize the commit message generator.
        
        Args:
            repo: GitPython repository object
            model_name: Name of the LLM model to use
            temperature: Temperature setting for the LLM (0.0 to 1.0)
        """
        self.repo = repo
        self.llm = LLMProviderType.get_llm(llm_provider)
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert developer writing clear, meaningful git commit messages.
            Given the changes made to files in a repository, create a commit message that:
            1. Follows conventional commit format when appropriate
            2. Clearly describes what changed and why
            3. Is concise but informative
            4. Includes relevant technical details
            5. Mentions breaking changes if present
            
            Your response should have three parts:
            1. Subject line (max 50 chars)
            2. Detailed description
            3. Brief explanation of your reasoning
            
            Separate each part with '---'"""),
            ("human", """Repository changes:
            
            Added files:
            {added_files}
            
            Modified files:
            {modified_files}
            
            Deleted files:
            {deleted_files}
            
            File content changes:
            {content_changes}
            """)
        ])
        
    def analyze_changes(self) -> Dict[str, List[str]]:
        """Analyze and categorize currently staged changes."""
        staged_files = self.repo.get_staged_changes()
        changes = {
            'added': [],
            'modified': [],
            'deleted': [],
            'content': [] 
        }
        
        for file_change in staged_files:
            path_str = str(file_change.path)
            if file_change.change_type == 'added':
                changes['added'].append(path_str)
                if hasattr(file_change, 'new_content') and file_change.new_content:
                    changes['content'].append(f"New file {path_str}:\n{file_change.new_content[:500]}...")
                    
            elif file_change.change_type == 'deleted':
                changes['deleted'].append(path_str)
                
            else:
                changes['modified'].append(path_str)
                if hasattr(file_change, 'content_diff') and file_change.diff_text:
                    changes['content'].append(f"Changes in {path_str}:\n{file_change.diff_text[:500]}...")
                
        return changes
    
    async def generate_message(self) -> AsyncGenerator[str, None]:
        """
        Generate a commit message using the LLM based on the analyzed changes.
        
        Returns:
            CommitSuggestion containing the generated message and explanation
        """
        changes = self.analyze_changes()
        prompt_variables = {
            'added_files': '\n'.join(changes['added']) or "None",
            'modified_files': '\n'.join(changes['modified']) or "None",
            'deleted_files': '\n'.join(changes['deleted']) or "None",
            'content_changes': '\n\n'.join(changes['content']) or "No content changes available"
        }

        with open("p.json", "w") as f:
            import json
            json.dump(prompt_variables, f, indent=4)
        chain = self.prompt | self.llm | StrOutputParser()
        async for result in chain.astream(prompt_variables):
            yield result
    
    def _get_file_content(self, file_path: str) -> Optional[str]:
        """
        Safely retrieve the content of a file, returning None if there's an error.
        
        This helper method handles reading file content while being mindful of:
        - Binary files
        - Large files
        - Encoding issues
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                # Read only the first 50KB to avoid memory issues
                return f.read(50 * 1024)
        except Exception:
            return None
