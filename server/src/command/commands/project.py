import rich_click as click
from rich.console import Console
from rich.syntax import Syntax

from .base import BaseCommand
from command.internal.cli import cli, async_command
from project.proj import Project
from vectorstores import VectorStoreType, CreateVectorStoreConfig
from vectorstores.search_analyzer import SearchAnalyzer


class ProjectCommand(BaseCommand):
    """
    Project Commands Here you can manage your project
    """

    def __init__(self, console: Console):
        super().__init__(console)
        self.console = console

    def setup(self):
        @cli.group(name="project")
        def project():
            """
            Project Commands - Manage your codebase, search, and analyze your project.

            This group contains commands for working with your project, including
            vectorizing your codebase for semantic search and searching through files.
            """

        @project.command(name="vectorize")
        @click.option(
            "--vector-store-type",
            "-vt",
            type=click.Choice(VectorStoreType.list_types()),
            default=VectorStoreType.FAISS.value,
            help="The type of vector store to use (faiss, chroma, qdrant, etc.)",
        )
        @click.option("--from-scratch", "-f", is_flag=True, help="Vectorize from scratch instead of incremental update", default=False)
        @async_command
        async def vectorize(vector_store_type: VectorStoreType, from_scratch: bool):
            """
            Vectorize your project's codebase for semantic search capabilities.

            This command analyzes your code and creates vector embeddings that enable
            semantic search through your project. By default, it performs an incremental
            update, only processing new or changed files.

            Options:
              --vector-store-type, -vt  Specify which vector database to use
                                        (default: faiss)
              --from-scratch, -f        Force complete re-indexing of all files

            Examples:
              ## Vectorize using Chroma and start from scratch
              git-repo project vectorize --vector-store-type chroma --from-scratch

              ## Incrementally update using Qdrant
              git-repo project vectorize --vector-store-type qdrant

              ## Quick update with default settings (FAISS)
              git-repo project vectorize
            """
            config = CreateVectorStoreConfig(
                store_type=vector_store_type,
            )

            with self.console.status("[bold green]Scanning repository...") as status:
                proj = await Project.find_root_and_init(config,
                                                        update_callback=lambda msg: status.update(
                                                            f"[bold green]{msg}")
                                                        )
                text = await proj.vectorize()

            self.console.print(text)

        @project.command(name="files")
        @click.option("--query", "-q", type=str, help="Natural language query to search for in the project")
        @click.option("--limit",
                      "-l",
                      type=int, default=10, help="Maximum number of results to return (default: 10)")
        @async_command
        async def files(query: str, limit: int):
            """
            Search your project files using natural language queries.

            This command performs semantic search across your codebase, finding
            relevant files and code snippets based on your natural language query.
            Results are ranked by relevance and displayed with syntax highlighting.

            The project must be vectorized first using the 'vectorize' command.

            Options:
              --query, -q    Your natural language search query
              --limit, -l    Maximum number of results to show (default: 10)

            Examples:
              ## Find code related to authentication
              git-repo project files --query "How is authentication implemented?"

              ## Look for the main entry point with fewer results
              git-repo project files --query "Where is the main function?" --limit 5

              ## Find error handling patterns
              git-repo project files --query "How are exceptions handled in this project?"
            """
            self.console.print(f"Searching {query}")
            config = CreateVectorStoreConfig(
                store_type=VectorStoreType.FAISS.value,
            )
            proj = await Project.find_root_and_init(config)

            with self.console.status("[bold green]Searching...") as status:
                results = await proj.search(query, limit)
                analyzer = SearchAnalyzer(results)
                analysis = analyzer.analyze()
                self.console.print(f"Found {len(results)} results:")

                for i, (result, interpretation) in enumerate(analysis, 1):
                    # Create a nice header with file path
                    self.console.print(f"\n[bold cyan]Result {i}[/bold cyan]")
                    self.console.print(
                        f"[bold white on blue] {result.metadata.get('source', 'Unknown source')} [/bold white on blue]")

                    # Create a metrics panel with relevance and confidence
                    self.console.print(f"[dim]{'─' * 50}[/dim]")
                    self.console.print(
                        f"[bold]Relevance:[/bold] [{interpretation.color}]{interpretation.relevance}[/{interpretation.color}] "
                        f"({interpretation.percentage}) {interpretation.star_display}")

                    self.console.print(
                        f"[bold]Confidence:[/bold] [{interpretation.color}]{interpretation.confidence}[/{interpretation.color}]")
                    self.console.print(f"[dim]{'─' * 50}[/dim]")

                    # Print the content with better formatting
                    self.console.print("[bold]Code Preview:[/bold]")
                    self.console.print(
                        Syntax(
                            # Show a bit more content
                            result.page_content,
                            "python",
                            theme="monokai",  # Add a nice theme
                            word_wrap=True,
                            padding=(1, 2, 1, 2)
                        )
                    )

                    # Add a clear separator between results
                    self.console.print(f"[dim]{'═' * 80}[/dim]\n")
