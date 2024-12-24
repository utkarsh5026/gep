from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

from pyperclip import copy as copy_to_clipboard

from .base import BaseCommand
from config import sample_config, create_sample_config_file


class SampleConfigCommand(BaseCommand):
    """
    Create a sample configuration file for the project.
    """

    def __init__(self, console: Console, config_path: str, on_screen: bool):
        """
        Create a sample configuration file for the project.

        Args:
            console (Console): The console to use for output.
            config_path (str): The path to the configuration file.
            on_screen (bool): Whether to display the configuration file on the screen.
        """
        super().__init__(console)
        self.config_path = config_path
        self.on_screen = on_screen

    def run(self):
        if self.on_screen:
            yaml_content = sample_config()
            syntax = Syntax(yaml_content, "yaml",
                            theme="monokai",
                            line_numbers=True,
                            padding=(1, 1, 1, 1))
            self.console.print(Panel(syntax, title="Sample Configuration"))

            copy_to_clipboard(yaml_content)
            self.console.print(
                "[bold green]Sample configuration file copied to clipboard 😃[/bold green]")

        else:
            create_sample_config_file(self.config_path)
            self.console.print(
                f"Sample configuration file created at {self.config_path}")
