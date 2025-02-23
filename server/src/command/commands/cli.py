import functools
import asyncio
import rich_click as click

from typing import Callable, AsyncGenerator, Any
from rich.console import Console


# Configurerich-click
click.rich_click.USE_RICH_MARKUP = True
click.rich_click.USE_MARKDOWN = True
click.rich_click.SHOW_ARGUMENTS = True
click.rich_click.SHOW_METAVARS_COLUMN = True

click.rich_click.GROUP_ARGUMENTS_OPTIONS = True
click.rich_click.STYLE_ERRORS_SUGGESTION = "yellow italic"
click.rich_click.MAX_WIDTH = 100
click.rich_click.OPTIONS_PANEL_TITLE = "💫 Options"
click.rich_click.ARGUMENTS_PANEL_TITLE = "📝 Arguments"
click.rich_click.COMMANDS_PANEL_TITLE = "🚀 Commands"

console = Console()


@click.group()
def cli():
    """
    A CLI tool for processing queries and managing embeddings.
    """
    console.print(
        "[bold blue]Welcome to Your Application[/bold blue]\n\n"
        "A CLI tool for processing queries and managing embeddings.\n\n"
        "[bold green]Project Manager[/bold green]\n"
    )


def async_command(f: Callable) -> Callable:
    """
    Decorator to handle async commands in Rich Click.
    This wrapper ensures async functions can be used with Click's synchronous interface.
    """
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))
    return wrapper


async def display_markdown_stream(console: Console, text_generator: AsyncGenerator[str, Any]) -> None:
    """
    Displays streaming markdown text with enhanced visual formatting and smooth updates.
    Uses Rich's supported markdown styling capabilities for reliable rendering.
    """
    from rich.markdown import Markdown
    from rich.live import Live
    from rich.padding import Padding
    from rich.console import Group
    import asyncio

    # Initialize text accumulators
    buffer = ""
    display_text = ""
    
    # Create the initial display with padding for better visual spacing
    initial_content = Group(
        Padding("", (1, 0)),  # Top padding
        Markdown("Processing..."),
        Padding("", (1, 0))   # Bottom padding
    )

    with Live(
        initial_content,
        console=console,
        refresh_per_second=10,
        vertical_overflow="visible",
        auto_refresh=True
    ) as live:
        try:
            async for chunk in text_generator:
                buffer += chunk
                if (any(delimiter in chunk for delimiter in ['.', '!', '?', '\n', ':']) or 
                    len(buffer) > 50):
                    display_text += buffer
                    buffer = ""
                    
                    content = Group(
                        Padding("", (1, 0)),
                        Markdown(display_text,
                         justify="left",
                          hyperlinks=True),
                        Padding("", (1, 0))
                    )
                    
                    live.update(content)
                    await asyncio.sleep(0.1)
            
            if buffer:
                display_text += buffer
                final_content = Group(
                    Padding("", (1, 0)),
                    Markdown(display_text, justify="left"),
                    Padding("", (1, 0))
                )
                live.update(final_content)
                
        except Exception as e:
            # Simple error handling with clear formatting
            console.print("\n[red]Error displaying markdown:[/red] " + str(e) + "\n")
    