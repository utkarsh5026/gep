import rich_click as click

from rich.console import Console
from rich.panel import Panel
from rich.progress import track
from rich.syntax import Syntax

from pyperclip import copy as copy_to_clipboard


from vector import VectorStoreType, EmbeddingProviderType
from query import QueryProcessor, LLMType
from prompt import PromptProviderType, PromptType
from config import create_sample_config_file, init_project as init_project, sample_config, ProjectManager


# Configure rich-click
click.rich_click.USE_RICH_MARKUP = True
click.rich_click.USE_MARKDOWN = True
click.rich_click.SHOW_ARGUMENTS = True
click.rich_click.SHOW_METAVARS_COLUMN = True
click.rich_click.SHOW_LINKS = True

# Additional styling configurations
# Groups arguments and options separately
click.rich_click.GROUP_ARGUMENTS_OPTIONS = True
# Style for error suggestions
click.rich_click.STYLE_ERRORS_SUGGESTION = "yellow italic"
click.rich_click.STYLE_OPTIONS = "bold cyan"  # Style for option names
click.rich_click.STYLE_ARGUMENTS = "bold green"  # Style for argument names
click.rich_click.STYLE_COMMANDS = "bold blue"  # Style for command names
click.rich_click.MAX_WIDTH = 100  # Maximum width of the help output
# Show arguments in a separate panel
click.rich_click.SHOW_ARGUMENTS_PANEL = True
click.rich_click.ALIGN_OPTIONS_SWITCHES = True  # Align option switches
# Custom title for options panel
click.rich_click.OPTIONS_PANEL_TITLE = "💫 Options"
# Custom title for arguments panel
click.rich_click.ARGUMENTS_PANEL_TITLE = "📝 Arguments"
# Custom title for commands panel
click.rich_click.COMMANDS_PANEL_TITLE = "🚀 Commands"

console = Console()


vector_stores = [store.name.lower() for store in VectorStoreType]
embedding_providers = [provider.name.lower()
                       for provider in EmbeddingProviderType]
prompt_providers = [provider.name.lower()
                    for provider in PromptProviderType]
prompt_types = [prompt_type.name.lower()
                for prompt_type in PromptType]
api_providers = [llm_type.name.lower()
                 for llm_type in LLMType]


@click.group()
def cli():
    console.print(
        "[bold blue]Welcome to Your Application[/bold blue]\n\n"
        "A CLI tool for processing queries and managing embeddings.\n\n"
        "[bold green]Project Manager[/bold green]\n"
    )


@cli.command()
@click.argument('query', required=True)
@click.argument('relevance_score', default=0.5, type=float)
@click.argument('max_results', default=10, type=int)
@click.option('--prompt_type', '-t', type=click.Choice(prompt_types), default='file_wise', help='The type of prompt to use for processing the query')
@click.option('--prompt_provider', '-p', type=click.Choice(prompt_providers), default='semantic', help='The type of prompt provider to use for processing the query')
def process_query(query: str, relevance_score: float, max_results: int, prompt_type: str, prompt_provider: str):
    """
    Process a query and return results.

    Arguments:\n
        query: The query string to process\n
        relevance_score: The relevance score to use for filtering results (default: 0.5)\n
        max_results: The maximum number of results to process (default: 10)
    """
    with console.status("[bold green]Processing query..."):
        processor = QueryProcessor()
        result = processor.process(query)
        console.print(Panel(f"Result: {result}", title="Query Result"))


@cli.command()
@click.option('--provider', '-p',
              type=click.Choice(['openai', 'local']),
              default='openai',
              help='Select the embedding provider')
@click.option('--create/--no-create',
              default=False,
              help='Create new embeddings')
def manage_embeddings(provider: str, create: bool):
    """
    Manage embedding operations.

    Options:
        --provider: The embedding provider to use
        --create: Whether to create new embeddings
    """
    console.print(f"\n[bold]Embedding Management - Using {provider}[/bold]")

    if create:
        for step in track(range(100), description="Creating embeddings..."):
            # Your embedding creation logic here
            pass
        console.print("[green]Embeddings updated successfully![/green]")


@cli.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
def status(verbose: bool):
    """Check the status of the application."""
    with console.status("[bold blue]Checking status..."):
        # Add your status check logic here
        status_msg = "All systems operational"
        console.print(Panel(status_msg, title="Status Check"))

        if verbose:
            # Add detailed status information
            console.print("[dim]Detailed status information...[/dim]")


@cli.command()
@click.option('--root-path', '-r', type=click.Path(exists=True), default='.', help='The root path to watch')
@click.option('--config-path', '-c', type=click.Path(exists=True), default='config.yaml', help='The path to the project configuration file')
@click.option('--api-provider', '-a', type=click.Choice(api_providers), default='openai', help='The API provider to use')
@click.option('--use-gitignore', '-g', is_flag=True, help='Use gitignore to ignore files')
def init(root_path: str, config_path: str, api_provider: str, api_key: str, use_gitignore: bool):
    """
    Initialize the application.
    """
    ProjectManager.load_from_yaml(root_path, config_path)


@cli.command(name='csc')
@click.option('--config-path', '-c', type=click.Path(exists=True), default='config.yaml', help='The path to the project configuration file')
@click.option('--on-screen/--no-on-screen', '-o', is_flag=True, help='Display the configuration file on the screen')
def create_sample_config(config_path: str, on_screen: bool):
    """
    Create a sample configuration file for the project.
    """
    if on_screen:
        yaml_content = sample_config()
        syntax = Syntax(yaml_content, "yaml",
                        theme="monokai",
                        line_numbers=True,
                        padding=(1, 1, 1, 1))
        console.print(Panel(syntax, title="Sample Configuration"))

        copy_to_clipboard(yaml_content)
        console.print(
            "[bold green]Sample configuration file copied to clipboard 😃[/bold green]")

    else:
        create_sample_config_file(config_path)
        console.print(f"Sample configuration file created at {config_path}")


@cli.command(name='init')
@click.option('--root-path', '-r', type=click.Path(exists=True), default='.', help='The root path to watch')
@click.option('--overwrite/--no-overwrite', '-o', is_flag=True, help='Overwrite existing project')
@click.option('--api-provider', '-a', type=click.Choice(api_providers), default='openai', help='The API provider to use')
@click.option('--api-key', '-k', type=str, help='The API key to use')
def init(root_path: str, api_provider: str, api_key: str, overwrite: bool):
    """
    Initialize the project.
    """
    console.print("\n[bold blue]🚀 Initializing Project[/bold blue]")
    with console.status("[bold green]Setting up your project..."):
        manager = init_project(root_path, api_provider, api_key, overwrite)
        console.print(
            "\n[bold green]✨ Project initialized successfully![/bold green]")
        console.print(Panel.fit(
            f"""
[yellow]Project Details:[/yellow]
• Root Path: [cyan]{manager.root_dir.resolve()}[/cyan]
• API Provider: [cyan]{api_provider}[/cyan]
• Configuration: [cyan]Ready[/cyan]
            """,
            title="[bold]Project Status",
            border_style="green"
        ))


@cli.command(name='upnore')
@click.option('--update-vector-store', '-v', is_flag=True, help='Update the vector store (remove the files we need to ignore)')
def update_ignore(update_vector_store: bool):
    """
    Update the files which we need to ignore.
    """

    try:
        old_patterns, new_patterns = ProjectManager.update_ignore()
        old_set, new_set = set(old_patterns), set(new_patterns)

        removed_patterns = old_set - new_set
        added_patterns = new_set - old_set
        unchanged_patterns = old_set & new_set

        panel_content = "[yellow]Changes in Ignore Patterns:[/yellow]\n"

        if removed_patterns:
            panel_content += "\n[red]Removed Patterns:[/red]\n"
            panel_content += '\n'.join(
                f'- [red]{pattern}[/red]' for pattern in sorted(removed_patterns))

        if added_patterns:
            panel_content += "\n[green]Added Patterns:[/green]\n"
            panel_content += '\n'.join(
                f'+ [green]{pattern}[/green]' for pattern in sorted(added_patterns))

        if unchanged_patterns:
            panel_content += "\n[blue]Unchanged Patterns:[/blue]\n"
            panel_content += '\n'.join(
                f'  [dim]{pattern}[/dim]' for pattern in sorted(unchanged_patterns))

        if not (removed_patterns or added_patterns):
            panel_content += "\n[dim]No changes in ignore patterns[/dim]"

        console.print(Panel(
            panel_content,
            title="[bold]Ignore Patterns Diff[/bold]",
            border_style="cyan",
            padding=(1, 2)
        ))

    except Exception as e:
        console.print(Panel(
            f"[bold red]Error updating ignore patterns:[/bold red]\n{str(e)}",
            title="[bold red]Error[/bold red]",
            border_style="red",
            padding=(1, 2)
        ))
        return
