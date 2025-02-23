import os

from typing import Optional
from pathlib import Path
import rich_click as click

from rich.console import Console
from git_repo.repo import Repository
from git_repo.commit import CommitHistoryAnalyzer, CommitOptions

from .base import BaseCommand
from .cli import cli, async_command, display_markdown_stream
from .options import with_llm_options, LLMConfigOptions


class RepoCommand(BaseCommand):
    def __init__(self, console: Console) -> None:
        super().__init__(console)

    def setup(self):
        """Set up the CLI"""

        @cli.group(name="repo")
        def repo():
            """
            Get Information about the Git Repository
            """

        @repo.command(name="history")
        @click.option('--commit-count',
                      '-c', required=False, type=click.IntRange(min=1), help="Number of commits to show (default: 5)")
        @click.option('--branch-name',
                      '-b', required=False, type=str, help="Name of the branch to analyze (default: current branch)")
        @click.option('--author',
                      '-a', required=False, type=str, help="Author of the commits")
        @with_llm_options
        @async_command
        async def show_history(
            llm_options: LLMConfigOptions,
            commit_count: int = 5,
            branch_name: Optional[str] = None,
            author: Optional[str]    = None
        ):
            opts = CommitOptions(
                commit_count=commit_count,
                branch_name=branch_name,
                author=author
            )
            await self._show_history(opts, llm_options)


        @repo.command(name="compare")
        @click.option('--base', '-b', required=True, type=str, help="Base commit ID to compare from")
        @click.option('--target', '-t', required=False, type=str, help="Target commit ID (optional, defaults to working directory)")
        @with_llm_options
        @async_command
        async def compare_commits(base: str, target: Optional[str] = None, llm_options: LLMConfigOptions = None):   
            """Compare two commits or a commit with working directory using named options.

            Examples:

                Compare two commits:
                ``git-repo repo compare --base <commit1> --target <commit2>``

                Compare a commit with the working directory:
                ``git-repo repo compare --base <commit>``

            """
            self._compare_commits(base, target)


    @classmethod
    def _get_repo(cls):
        """
        Get the Git repository at the current working directory.
        """
        current_dir = Path(os.getcwd())
        while current_dir != current_dir.parent:
            if (current_dir / '.git').is_dir():
                return Repository(str(current_dir))
            current_dir = current_dir.parent
            
        raise ValueError("Not inside a Git repository")


    async def _show_history(self, opts: CommitOptions, llm_options: LLMConfigOptions):
        """Show git commit history with typewriter-style output"""
        try:
            repo = self._get_repo()
            analyzer = CommitHistoryAnalyzer(repo)
            console = self.console
            generator = analyzer.analyze_commit_history(opts, llm_options.llm_type)
            await display_markdown_stream(console, generator)
        except Exception as e:
            self.console.print(f"[red]Error analyzing commit history: {str(e)}[/red]")
