import rich_click as click

from rich.console import Console
from rich.panel import Panel


from vector import VectorStoreType, EmbeddingProviderType
from query import QueryProcessor, LLMType
from prompt import PromptProviderType, PromptType
from config import ProjectManager
from cmd.commands import EmbedCommand, APIKeyCommand, InitProjectCommand, SampleConfigCommand, UpdateIgnoreCommand


# Configure rich-click
click.rich_click.USE_RICH_MARKUP = True
click.rich_click.USE_MARKDOWN = True
click.rich_click.SHOW_ARGUMENTS = True
click.rich_click.SHOW_METAVARS_COLUMN = True
click.rich_click.SHOW_LINKS = True

click.rich_click.GROUP_ARGUMENTS_OPTIONS = True
click.rich_click.STYLE_ERRORS_SUGGESTION = "yellow italic"
click.rich_click.STYLE_OPTIONS = "bold cyan"
click.rich_click.STYLE_ARGUMENTS = "bold green"
click.rich_click.STYLE_COMMANDS = "bold blue"
click.rich_click.MAX_WIDTH = 100
click.rich_click.SHOW_ARGUMENTS_PANEL = True
click.rich_click.ALIGN_OPTIONS_SWITCHES = True
click.rich_click.OPTIONS_PANEL_TITLE = "💫 Options"
click.rich_click.ARGUMENTS_PANEL_TITLE = "📝 Arguments"
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
    """
    with console.status("[bold green]Processing query..."):
        processor = QueryProcessor()
        result = processor.process(query)
        console.print(Panel(f"Result: {result}", title="Query Result"))


@cli.command(name='load')
@click.option('--root-path', '-r', type=click.Path(exists=True), default='.', help='The root path to watch')
@click.option('--config-path', '-c', type=click.Path(exists=True), default='config.yaml', help='The path to the project configuration file')
@click.option('--api-provider', '-a', type=click.Choice(api_providers), default='openai', help='The API provider to use')
@click.option('--use-gitignore', '-g', is_flag=True, help='Use gitignore to ignore files')
def load_project(root_path: str, config_path: str, api_provider: str, api_key: str, use_gitignore: bool):
    """
    Load the project.
    """
    ProjectManager.load_from_yaml(root_path)


@cli.command(name='csc')
@click.option('--config-path', '-c', type=click.Path(exists=True), default='config.yaml', help='The path to the project configuration file')
@click.option('--on-screen/--no-on-screen', '-o', is_flag=True, help='Display the configuration file on the screen')
def create_sample_config(config_path: str, on_screen: bool):
    """
    Create a sample configuration file for the project.
    """
    SampleConfigCommand(console=console,
                        config_path=config_path,
                        on_screen=on_screen).run()


@cli.command(name='init')
@click.option('--root-path', '-r', type=click.Path(exists=True), default='.', help='The root path to watch')
@click.option('--overwrite/--no-overwrite', '-o', is_flag=True, help='Overwrite existing project')
@click.option('--api-provider', '-a', type=click.Choice(api_providers), default='openai', help='The API provider to use')
@click.option('--api-key', '-k', type=str, help='The API key to use')
def init(root_path: str, api_provider: str, api_key: str, overwrite: bool):
    """
    Initialize the project.
    """
    InitProjectCommand(console=console,
                       root_path=root_path,
                       api_provider=api_provider,
                       api_key=api_key,
                       overwrite=overwrite).run()


@cli.command(name='upnore')
@click.option('--update-vector-store', '-v', is_flag=True, help='Update the vector store (remove the files we need to ignore)')
def update_ignore(update_vector_store: bool):
    """
    Update the files which we need to ignore.
    """
    UpdateIgnoreCommand(console=console,
                        update_vector_store=update_vector_store).run()


@cli.command()
def embed():
    """
    Embed the project and store the embeddings in the vector store.
    """
    EmbedCommand(console).run()


@cli.command(name='api-key')
@click.option('--op-type', '-o', type=click.Choice(['add', 'delete', 'get']), help='The type of operation to perform')
@click.option('--api-provider', '-a', type=click.Choice(api_providers), help='The API provider to use')
@click.option('--api-key', '-k', type=str, help='The API key to use')
def api_key(op_type: str, api_provider: str, api_key: str):
    """
    Manage API keys.
    """

    APIKeyCommand(console, op_type, api_provider, api_key).run()
