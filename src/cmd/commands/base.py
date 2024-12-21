from rich.console import Console
from abc import ABC, abstractmethod
from rich.panel import Panel


class BaseCommand(ABC):
    def __init__(self, console: Console) -> None:
        self.console = console

    @abstractmethod
    def run(self):
        """Run the command"""
        pass

    def error(self, message: str, e: Exception):
        """Print an error message"""
        self.console.print(Panel(
            f"[bold red]{message}:[/bold red]\n{str(e)}",
            title="[bold red]Error[/bold red]",
            border_style="red",
            padding=(1, 2)
        ))
