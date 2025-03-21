from .embed import EmbedCommand
from .api_key import APIKeyCommand
from .init_proj import InitProjectCommand
from .sample_config import SampleConfigCommand
from .update_ignore import UpdateIgnoreCommand
from .repo import RepoCommand
from .project import ProjectCommand

from rich.console import Console

console = Console()
RepoCommand(console=console).setup()
ProjectCommand(console=console).setup()


__all__ = ['EmbedCommand',
           'APIKeyCommand',
           'InitProjectCommand',
           'SampleConfigCommand',
           'UpdateIgnoreCommand',
           'RepoCommand',
           'ProjectCommand']
