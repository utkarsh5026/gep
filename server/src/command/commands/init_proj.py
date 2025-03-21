from rich.console import Console
from rich.panel import Panel

from .base import BaseCommand
from config import verify_provider


class InitProjectCommand(BaseCommand):
    def __init__(self, console: Console, root_path: str, api_provider: str, api_key: str, overwrite: bool):
        super().__init__(console)
        self.root_path = root_path
        self.api_provider = verify_provider(api_provider)
        self.api_key = api_key
        self.overwrite = overwrite

    def run(self):
        self.console.print("\n[bold blue]🚀 Initializing Project[/bold blue]")
        with self.console.status("[bold green]Setting up your project..."):
            manager = init_project(
                root_path=self.root_path,
                api_provider=self.api_provider,
                api_key=self.api_key,
                overwrite=self.overwrite
            )
        self.console.print(
            "\n[bold green]✨ Project initialized successfully![/bold green]")
        self.console.print(Panel.fit(
            f"""
[yellow]Project Details:[/yellow]
• Root Path: [cyan]{manager.root_dir.resolve()}[/cyan]
• API Provider: [cyan]{self.api_provider.value}[/cyan]
• Configuration: [cyan]Ready[/cyan]
            """,
            title="[bold]Project Status",
            border_style="green"
        ))
