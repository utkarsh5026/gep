import asyncio
from typing import AsyncGenerator, Any
from rich.console import Console, Group
from rich.markdown import Markdown
from rich.live import Live
from rich.padding import Padding
from rich.panel import Panel
from rich.style import Style
from rich.theme import Theme
from rich.syntax import Syntax
from rich.table import Table

# Define custom theme for consistent styling
custom_theme = Theme({
    "markdown.heading": Style(color="bright_blue", bold=True),
    "markdown.code": Style(color="bright_green"),
    "markdown.link": Style(color="cyan", underline=True),
    "markdown.blockquote": Style(color="yellow", italic=True),
    "markdown.item": Style(color="bright_white"),
})

class MarkdownDisplayManager:
    def __init__(self, console: Console):
        self.console = console
        self.console.theme = custom_theme
        self.buffer = ""
        self.display_text = ""
        
    def create_markdown_content(self, text: str) -> Group:
        """
        Creates a richly formatted markdown content group with enhanced styling.
        Includes special handling for code blocks and tables.
        """
        components = []
        
        # Add top margin for better spacing
        components.append(Padding("", (1, 0)))
        
        # Process and add the main markdown content
        md = Markdown(
            text,
            justify="left",
            code_theme="monokai",
            hyperlinks=True
        )
        
        # Wrap markdown in a panel for better visual separation
        panel = Panel(
            md,
            border_style="bright_blue",
            padding=(1, 2),
            title="Content",
            subtitle="Live Preview"
        )
        components.append(panel)
        
        # Add bottom margin
        components.append(Padding("", (1, 0)))
        
        return Group(*components)

    async def format_code_blocks(self, text: str) -> str:
        """
        Enhanced code block formatting with syntax highlighting and line numbers.
        """
        import re
        
        code_block_pattern = r"```(\w+)?\n(.*?)```"
        
        def replace_code_block(match):
            language = match.group(1) or "text"
            code = match.group(2)
            
            # Create syntax highlighted code
            syntax = Syntax(
                code.strip(),
                language,
                theme="monokai",
                line_numbers=True,
                word_wrap=True
            )
            return str(syntax)
            
        return re.sub(code_block_pattern, replace_code_block, text, flags=re.DOTALL)

    async def display_markdown_stream(self, text_generator: AsyncGenerator[str, Any]) -> None:
        """
        Displays streaming markdown text with enhanced visual formatting and smooth updates.
        Features include:
        - Syntax highlighting for code blocks
        - Clean typography with proper spacing
        - Visual hierarchy with panels and borders
        - Smooth content updates with buffering
        """
        # Initialize the display with a welcome message
        initial_content = self.create_markdown_content("Initializing content stream...")

        with Live(
            initial_content,
            console=self.console,
            refresh_per_second=15,  # Increased for smoother updates
            vertical_overflow="visible",
            auto_refresh=True
        ) as live:
            try:
                async for chunk in text_generator:
                    # Accumulate text in buffer
                    self.buffer += chunk
                    
                    # Check for natural break points in text
                    if (any(delimiter in chunk for delimiter in ['.', '!', '?', '\n', ':']) or
                            len(self.buffer) > 80):  # Increased buffer size for smoother flow
                        
                        self.display_text += self.buffer
                        self.buffer = ""
                        
                        # Format code blocks if present
                        formatted_text = await self.format_code_blocks(self.display_text)
                        
                        # Create and update content with enhanced formatting
                        content = self.create_markdown_content(formatted_text)
                        live.update(content)
                        
                        # Add small delay for smooth visual updates
                        await asyncio.sleep(0.05)
                
                # Handle any remaining text in buffer
                if self.buffer:
                    self.display_text += self.buffer
                    final_content = self.create_markdown_content(self.display_text)
                    live.update(final_content)
                    
            except Exception as e:
                error_panel = Panel(
                    f"[red]Error displaying markdown:[/red]\n{str(e)}",
                    border_style="red",
                    title="Error"
                )
                self.console.print(error_panel)

# Usage example in your CLI
async def display_markdown_stream(console: Console, text_generator: AsyncGenerator[str, Any]) -> None:
    """
    Enhanced wrapper function for markdown display
    """
    display_manager = MarkdownDisplayManager(console)
    await display_manager.display_markdown_stream(text_generator)