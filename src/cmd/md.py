import asyncio

from enum import Enum
from rich.console import Console
from rich.markdown import Markdown
from typing import AsyncGenerator, Union


class OutputFormat(Enum):
    TEXT = "text"
    MARKDOWN = "markdown"


class MarkdownOutput:
    """Manages formatted console output for LLM analysis results."""

    def __init__(self, format: OutputFormat = OutputFormat.MARKDOWN):
        self.format = format
        self.console = Console()

    def _print_result(self, content: str):
        """Print a single result with appropriate formatting."""
        if self.format == OutputFormat.MARKDOWN:
            self.console.print(Markdown(content))
        else:
            self.console.print(content)

    async def print_stream(self, stream: AsyncGenerator[Union[str, dict], None]):
        """Print a stream of LLM analysis results."""
        try:
            # If stream is a string, print it directly
            if isinstance(stream, str):
                self._print_result(stream)
                return

            # Otherwise handle as async generator
            async for result in stream:
                if isinstance(result, str):
                    self._print_result(result)
                elif isinstance(result, dict) and 'content' in result:
                    self._print_result(result['content'])
                await asyncio.sleep(0)  # Allow other tasks to run

        except Exception as e:
            self.console.print(f"Error printing stream: {e}", style="bold red")


def create_output_manager(format: str = "markdown") -> MarkdownOutput:
    """Factory function to create an output manager with the specified format."""
    format_map = {
        "text": OutputFormat.TEXT,
        "markdown": OutputFormat.MARKDOWN,
    }
    return MarkdownOutput(format_map.get(format, OutputFormat.MARKDOWN))
