from rich.console import Console
from rich.panel import Panel

from .base import BaseCommand
from config import ProjectManager


class UpdateIgnoreCommand(BaseCommand):
    """
    Update the ignore patterns for the project.
    """

    def __init__(self, console: Console, update_vector_store: bool):
        """
        Initialize the UpdateIgnoreCommand.

        Args:
            console (Console): The console instance.
            update_vector_store (bool): Whether to update the vector store.
        """
        super().__init__(console)
        self.update_vector_store = update_vector_store

    def run(self):

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

            self.console.print(Panel(
                panel_content,
                title="[bold]Ignore Patterns Diff[/bold]",
                border_style="cyan",
                padding=(1, 2)
            ))

        except Exception as e:
            self.error(e)
