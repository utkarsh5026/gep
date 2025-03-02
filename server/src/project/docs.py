import multiprocessing
import asyncio
from typing import Optional, Callable
from pathlib import Path

from pydantic import BaseModel, Field
from langchain_core.output_parsers import StrOutputParser
from .scan import RepoScanner
from llm import LLMProviderType


class FileProcessingError(Exception):
    """
    Exception raised when there is an error processing a file.
    """

    def __init__(self, file: Path, message: str):
        super().__init__(f"Error processing {file}: {message}")


class DocsGenerationOptions(BaseModel):
    """
    Configuration options for documentation generation.

    This model defines the parameters that control how documentation
    is generated, including output location, format, and processing options.
    """
    output_dir: Optional[str] = Field(
        default="./docs",
        description="The directory to save the docs")

    format: Optional[str] = Field(default="markdown",
                                  description="The format of the docs")

    apply_to_files: Optional[bool] = Field(
        default=False, description="Whether to apply the docs to the files")

    extra_instructions: Optional[str] = Field(
        default="",
        description="Any extra instructions for the LLM when generating the docs")

    recursive: Optional[bool] = Field(
        default=False,
        description="Whether to recursively generate the docs for all subdirectories"
    )

    file_path: Path = Field(
        description="The path of the file or the directory to generate the docs for"
    )

    pattern: Optional[str] = Field(
        default="",
        description="The pattern to use to match the files like *.py, *.md, etc."
    )

    llm_provider: LLMProviderType = Field(
        description="The LLM provider to use for the docs generation"
    )


class DocsGenerator(RepoScanner):
    def __init__(self, repo_path: Path, process_callback: Callable[[str], None] | None = None):
        """
        Initialize the DocsGenerator with the given repository path.

        Args:
            repo_path: The path to the repository to generate docs for.
            process_callback: A callback function to process messages.
        """
        super().__init__(repo_path=repo_path)
        self.semaphore = None
        self.process_callback = process_callback if process_callback else lambda _: None

    def generate_docs(self, options: DocsGenerationOptions):
        """
        Generate documentation for files asynchronously.

        This is the main entry point for documentation generation, handling file 
        discovery and coordinating the async tasks.

        Args:
            options: Configuration options for the documentation generation process.
        """
        self.semaphore = asyncio.Semaphore(multiprocessing.cpu_count() * 2)
        file_path = options.file_path.resolve()
        files = self._discover_files(file_path, options)

        if not files:
            self.process_callback(
                f"No files found to generate docs for the pattern: {options.pattern} in the path: {file_path}")
            return

        self.process_callback(f"Found {len(files)} files to generate docs for")
        return files

    async def _process_file(self, file: Path, options: DocsGenerationOptions) -> Optional[str]:
        """
        Process a single file to generate documentation.

        This method handles the complete workflow for a single file:
        reading, generating documentation, and writing the result.

        Args:
            file: The file to process.
            options: Documentation generation options.

        Returns:
            The path where documentation was saved, or None if processing failed.
        """
        async with self.semaphore:
            try:
                if not await self._should_process_file(file):
                    self.process_callback(
                        f"Skipping file {file} (binary or too large)")
                    return None

                content = await self._read_file(file)
                if not content:
                    return None
                doc_format = self._get_doc_format(file)
                documentation = await self._generate_documentation(file, content, options, doc_format)

                return documentation

            except Exception as e:
                raise FileProcessingError(file, str(e)) from e

    @classmethod
    def _discover_files(cls, file_path: Path, options: DocsGenerationOptions) -> list[Path]:
        """
        Discover files based on the given options.

        Args:
            file_path: The base file or directory path.
            options: Configuration options for file selection.

        Returns:
            A list of file paths to process.
        """
        if file_path.is_dir():
            if options.recursive:
                glob_pattern = f"**/{options.pattern}" if options.pattern else "**/*"
                files = list(file_path.glob(glob_pattern))
            else:
                glob_pattern = options.pattern if options.pattern else "*"
                files = list(file_path.glob(glob_pattern))

            files = [f for f in files if f.is_file()]
        else:
            files = [file_path]

        return files

    async def _generate_documentation(self, file: Path, content: str, options: DocsGenerationOptions, doc_format: str) -> str:
        """
        Generate documentation for a file using the LLM asynchronously.

        Args:
            file: The file being documented.
            content: The content of the file.
            options: Documentation generation options.
            doc_format: The format to use for documentation.

        Returns:
            The generated documentation as a string.
        """
        file_ext = file.suffix.lower()
        file_name = file.name

        prompt = self._create_documentation_prompt(
            content,
            file_name,
            file_ext,
            doc_format,
            options.extra_instructions
        )

        chain = (
            prompt | LLMProviderType.get_llm(options) | StrOutputParser()
        )

        return await chain.ainvoke(prompt)

    def _create_documentation_prompt(self, content: str, file_name: str, file_ext: str, doc_format: str, extra_instructions: str) -> str:
        """
            Create a prompt for the language model to generate documentation.

            Args:
                content: The file content to document.
                file_name: The name of the file.
                file_ext: The file extension.
                doc_format: The documentation format to use.
                extra_instructions: Additional instructions for the LLM.

            Returns:
                A prompt string to send to the LLM.
            """
        prompt = f"""
You are an expert documentation generator for code. Please analyze the following {file_ext} file and generate comprehensive documentation in {doc_format} format.

File name: {file_name}

When generating documentation:
1. Identify and document all key components (classes, functions, methods, etc.)
2. Explain the purpose and functionality of each component
3. Document parameters, return values, and exceptions where applicable
4. Include usage examples where helpful
5. Maintain the structure and conventions appropriate for {doc_format} format
6. Focus on clarity and completeness

{extra_instructions if extra_instructions else ""}

Here is the code to document:

```{file_ext.lstrip('.')}
{content}
```

Please generate the documentation in {doc_format} format.
"""
        return prompt
