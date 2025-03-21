import rich_click as click
from rich.console import Console
from rich.syntax import Syntax

from .base import BaseCommand
from command.internal.cli import cli, async_command
from command.internal.options import (
    with_llm_options,
    LLMConfigOptions,
    with_file_options,
    FileOptions
)

from vectorstores import VectorStoreType, CreateVectorStoreConfig
from vectorstores.search_analyzer import SearchAnalyzer

from project.proj import Project
from project.docs import DocsGenerator, DocsGenerationOptions


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
        @click.option("--from-scratch",
                      "-f",
                      is_flag=True,
                      help="Vectorize from scratch instead of incremental update", default=False)
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

            with self.console.status("[bold green]Searching..."):
                results = await proj.search(query, limit)
                analyzer = SearchAnalyzer(results)
                analysis = analyzer.analyze()
                self.console.print(f"Found {len(results)} results:")

                for i, (result, interpretation) in enumerate(analysis, 1):
                    self.console.print(f"\n[bold cyan]Result {i}[/bold cyan]")
                    self.console.print(
                        f"[bold white on blue] {result.metadata.get('source', 'Unknown source')} [/bold white on blue]")

                    self.console.print(f"[dim]{'─' * 50}[/dim]")
                    self.console.print(
                        f"[bold]Relevance:[/bold] [{interpretation.color}]{interpretation.relevance}[/{interpretation.color}] "
                        f"({interpretation.percentage}) {interpretation.star_display}")

                    self.console.print(
                        f"[bold]Confidence:[/bold] [{interpretation.color}]{interpretation.confidence}[/{interpretation.color}]")
                    self.console.print(f"[dim]{'─' * 50}[/dim]")

                    self.console.print("[bold]Code Preview:[/bold]")
                    self.console.print(
                        Syntax(
                            result.page_content,
                            "python",
                            theme="monokai",
                            word_wrap=True,
                            padding=(1, 2, 1, 2)
                        )
                    )

                    self.console.print(f"[dim]{'═' * 80}[/dim]\n")

        @project.command(name="docs")
        @click.option("--query", "-q", type=str, help="Any extra instructions for the LLM when generating the docs")
        @click.option("--output-dir", "-o", type=str, help="The path to the directory where the docs will be saved", default="./docs")
        @click.option("--apply-to-files", "-a", is_flag=True, help="Apply the docs to the files in the project", default=False)
        @click.option("--format", "-f", type=click.Choice(["markdown", "html", "pdf"]), help="The format of the docs", default="markdown")
        @with_llm_options
        @with_file_options
        @async_command
        async def docs(query: str, output_dir: str, apply_to_files: bool, format: str,
                       llm_options: LLMConfigOptions, file_options: FileOptions):
            """
            Generate documentation for your project using AI.

            This command analyzes your codebase and generates comprehensive documentation
            based on the code structure, comments, and functionality. You can specify
            which files to document, the output format, and provide additional instructions
            to guide the documentation generation process.

            Options:
              --query, -q             Additional instructions for the AI when generating docs
              --output-dir, -o        Directory where documentation will be saved (default: ./docs)
              --apply-to-files, -a    Add documentation directly to source files (default: False)
              --format, -f            Output format: markdown, html, or pdf (default: markdown)
              --file-path, -f         Specific file or directory to document
              --recursive, -r         Process all files in directories recursively
              --llm-type              AI model to use for documentation generation

            Examples:
              ## Generate markdown docs for the entire project
              git-repo project docs

              ## Document a specific module with custom instructions
              git-repo project docs --file-path src/auth --query "Focus on security aspects"

              ## Create HTML documentation for a single file
              git-repo project docs --file-path src/main.py --format html

              ## Generate docs and add them directly to source files
              git-repo project docs --apply-to-files --llm-type gpt-4o
            """
            self.console.print(
                f"Generating documentation with format: {format}")
            self.console.print(f"Output directory: {output_dir}")
