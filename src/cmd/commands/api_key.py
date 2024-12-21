from rich.console import Console
from rich.panel import Panel
from typing import Literal, Optional

from .base import BaseCommand
from config import APIKeyManager, APIProvider, verify_provider
from config.api import InvalidProviderError


class APIKeyCommand(BaseCommand):
    """Command to manage API keys"""

    def __init__(self, console: Console,
                 op_type: Literal["add", "delete", "get"],
                 api_provider: str,
                 api_key: Optional[str] = None) -> None:
        """Initialize the API key command

        Args:
            console (Console): The console to use
            op_type (Literal["add", "delete", "get"]): The type of operation to perform
            api_provider (str): The API provider to use (e.g. "openai")
            api_key (Optional[str]): The API key to use
        """
        super().__init__(console)

        try:
            self.op_type = op_type
            self.api_provider = verify_provider(api_provider)
            self.api_key = api_key
        except InvalidProviderError as e:
            self.error("Invalid API provider", e)

    def run(self):
        """Run the API key command"""
        try:
            if self.op_type == "add":
                self.__add_api_key()
            elif self.op_type == "delete":
                self.__delete_api_key()
            elif self.op_type == "get":
                self.__get_api_key()
        except Exception as e:
            self.error(f"Error doing operation {self.op_type}", e)

    def __add_api_key(self):
        """Add an API key"""
        APIKeyManager.set_api_key(self.api_provider, self.api_key)
        self.console.print(Panel(
            "[green]Successfully added API key[/green]",
            border_style="green",
            padding=(1, 2)
        ))

    def __get_api_key(self):
        """Get an API key"""
        try:
            api_key = APIKeyManager.get_api_key(self.api_provider)
            self.console.print(Panel(
                f"[green]API key for {
                    self.api_provider.value}: {api_key}[/green]",
                border_style="green",
                padding=(1, 2)
            ))
        except InvalidProviderError as e:
            self.error("Invalid provider", e)

    def __delete_api_key(self):
        """Delete an API key"""
        APIKeyManager.delete_api_key(self.api_provider)
        self.console.print(Panel(
            "[green]Successfully deleted API key[/green]",
            border_style="green",
            padding=(1, 2)
        ))
