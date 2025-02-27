import rich_click as click
from rich.console import Console
from rich.syntax import Syntax

from .base import BaseCommand
from command.internal.cli import cli, async_command
from project.proj import Project
from vectorstores import VectorStoreType, CreateVectorStoreConfig
from vectorstores.search_analyzer import SearchAnalyzer
from command.internal.options import with_llm_options, LLMConfigOptions


class ProjectCommand(BaseCommand):
    def __init__(self, console: Console):
        super().__init__(console)
        self.console = console

    def setup(self):
        @cli.group(name="project")
        def project():
            """
            Project Commands Here you can manage your project
            """

        @project.command(name="vectorize")
        @click.option(
            "--vector-store-type",
            "-vt",
            type=click.Choice(VectorStoreType.list_types()),
            default=VectorStoreType.FAISS.value,
            help="The type of vector store to use",
        )
        @async_command
        async def vectorize(vector_store_type: VectorStoreType):

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
        @click.option("--query", "-q", type=str, help="The query to search for in the project")
        @click.option("--limit",
                      "-l",
                      type=int, default=10, help="The number of results to return, default is 10")
        @async_command
        async def files(query: str, limit: int):
            """
            Search the project files for the given query

            Examples:

            ``git-repo project files --query "How auth is implemented in the project?"``

            ``git-repo project files --query "What is the main function in the project?" --limit 5``
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
