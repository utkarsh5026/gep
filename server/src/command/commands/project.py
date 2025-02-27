import rich_click as click
from rich.console import Console
from rich.syntax import Syntax

from .base import BaseCommand
from command.internal.cli import cli, async_command
from project.proj import Project
from vectorstores import VectorStoreType, CreateVectorStoreConfig
from vectorstores.search_analyzer import SearchAnalyzer, ScoreInterpretation
from command.internal.options import with_llm_options, LLMConfigOptions


class ProjectCommand(BaseCommand):
    def __init__(self, console: Console):
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
                project = await Project.find_root_and_init(config,
                                                           update_callback=lambda msg: status.update(
                                                               f"[bold green]{msg}")
                                                           )
                text = await project.vectorize()

            self.console.print(text)

        @project.command(name="files")
        @click.option("--query", "-q", type=str, help="The query to search for in the project")
        @click.option("--limit", "-l", type=int, default=10, help="The number of results to return, default is 10")
        @with_llm_options
        @async_command
        async def files(query: str, limit: int, llm_options: LLMConfigOptions):
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
            project = await Project.find_root_and_init(config)

            with self.console.status("[bold green]Searching...") as status:
                results = await project.search(query, limit)
                analyzer = SearchAnalyzer(results)
                analysis = analyzer.analyze()
                self.console.print(f"Found {len(results)} results:")
                for i, (result, interpretation) in enumerate(analysis, 1):
                    self.console.print(
                        f"\n[bold cyan]{i}.[/bold cyan] [bold]{result.metadata.get('source', 'Unknown source')}[/bold]")

                    # Display the score interpretation with color
                    self.console.print(
                        f"Relevance: [{interpretation.color}]{interpretation.relevance}[/{interpretation.color}] "
                        f"({interpretation.percentage}) {interpretation.star_display}")

                    self.console.print(
                        f"Confidence: [{interpretation.color}]{interpretation.confidence}[/{interpretation.color}]")

                    # Print the content in code format
                    self.console.print(
                        Syntax(result.page_content[:100], "python", line_numbers=True))

                    self.console.print()
