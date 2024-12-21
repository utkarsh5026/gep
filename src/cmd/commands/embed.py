import asyncio

from rich.console import Console
from rich.panel import Panel


from .base import BaseCommand
from config import ProjectManager, EmbeddingConfig, VectorConfig, ProjectConfig, APIKeyManager, verify_provider
from vector import create_file_content_map, create_embedding_provider, EmbeddingProviderConfig, EmbeddingProvider, EmbeddingManager, VectorStore, VectorStoreType, FAISSVectorStore


class UnsupportedVectorStoreError(Exception):
    """Raised when vector store type is not supported"""
    pass


class EmbedCommand(BaseCommand):
    """Embed command used to embed documents and store them in a vector store"""

    def __init__(self, console: Console):
        super().__init__(console)

    def __load_project(self):
        try:
            proj_config = ProjectManager.self_load()
            embedding_config = proj_config.emb_config
            vector_config = proj_config.vector_config
            self.__print_project_info(embedding_config, vector_config)

            return proj_config, embedding_config, vector_config
        except Exception as e:
            self.error("Error loading project", e)
            raise e

    def __print_project_info(self, embedding_config: EmbeddingConfig, vector_config: VectorConfig):
        """Print the project information in a panel"""
        emb_panel_content = "\n".join([
            f"[yellow]Embedding Type:[/yellow] [cyan]{
                embedding_config.embedding_type}[/cyan]",
            f"[yellow]Model Name:[/yellow] [cyan]{
                embedding_config.model_name}[/cyan]",
            f"[yellow]Batch Size:[/yellow] [cyan]{
                embedding_config.batch_size}[/cyan]",
            f"[yellow]Dimension:[/yellow] [cyan]{
                embedding_config.dimension}[/cyan]",
            f"[yellow]Additional Params:[/yellow] [cyan]{
                embedding_config.additional_params or 'None'}[/cyan]"
        ])
        self.console.print(Panel(
            emb_panel_content,
            title="[bold]Embedding Configuration[/bold]",
            border_style="blue",
            padding=(1, 2)
        ))

        # Vector Store Configuration Panel
        vector_panel_content = "\n".join([
            f"[yellow]Store Type:[/yellow] [cyan]{
                vector_config.store_type}[/cyan]",
            f"[yellow]Persist Directory:[/yellow] [cyan]{
                vector_config.persist_dir}[/cyan]",
            f"[yellow]Dimension:[/yellow] [cyan]{
                vector_config.dimension}[/cyan]",
            f"[yellow]Additional Params:[/yellow] [cyan]{
                vector_config.additional_params or 'None'}[/cyan]"
        ])
        self.console.print(Panel(
            vector_panel_content,
            title="[bold]Vector Store Configuration[/bold]",
            border_style="green",
            padding=(1, 2)
        ))

    def __create_file_content_map(self, proj_config: ProjectConfig) -> dict[str, str] | None:
        """Create a file content map for the project"""
        try:
            with self.console.status("[bold green]Creating file content map...", spinner="dots") as status:
                file_map = create_file_content_map(root_dir=str(proj_config.root_dir),
                                                   ignore_patterns=proj_config.ignore_patterns,
                                                   accept_patterns=proj_config.accepted_patterns)
            status.update("[bold green]File mapping complete!")
            self.console.print(Panel(
                f"[green]Successfully mapped {len(file_map)} files[/green]",
                title="[bold]File Mapping Results[/bold]",
                border_style="cyan",
                padding=(1, 2)
            ))

            return file_map
        except Exception as e:
            self.error("Error creating file content map", e)

    def __create_embedding_provider(self, embedding_config: EmbeddingConfig) -> EmbeddingProvider:
        """Create an embedding provider"""
        provider = verify_provider(embedding_config.embedding_type.value)
        provider_config = EmbeddingProviderConfig(
            model_name=embedding_config.model_name,
            api_key=APIKeyManager.get_api_key(provider)
        )
        emb_provider = create_embedding_provider(
            embedding_config.embedding_type,
            provider_config)

        self.console.print(Panel(
            "[green]Successfully created embedding provider[/green]",
            title="[bold]Embedding Provider[/bold]",
            border_style="cyan",
            padding=(1, 2)
        ))
        return emb_provider

    def __create_vector_store(self, vector_config: VectorConfig) -> VectorStore:
        """Create a vector store"""
        store_type = vector_config.store_type

        if store_type == VectorStoreType.FAISS:
            return FAISSVectorStore(dimension=vector_config.dimension,
                                    index_path=vector_config.persist_dir)

        raise UnsupportedVectorStoreError(
            f"Unsupported vector store type: {store_type}")

    async def __embed_docs(self, embedding_manager: EmbeddingManager, file_content_map: dict[str, str]):
        """Embed the documents"""
        texts = list(file_content_map.values())
        metadatas = [{"source": file_path}
                     for file_path in file_content_map.keys()]

        try:
            with self.console.status("[bold green]Embedding and storing documents...", spinner="dots") as status:
                await embedding_manager.add_texts(texts=texts, metadatas=metadatas)
                status.update("[bold green]Embedding complete!")

            self.console.print(Panel(
                f"[green]Successfully embedded and stored {
                    len(texts)} documents[/green]",
                title="[bold]Embedding Results[/bold]",
                border_style="cyan",
                padding=(1, 2)
            ))

        except Exception as e:
            self.error("Error embedding documents", e)

    def run(self):
        """Run the embed command"""
        asyncio.run(self.__async_run())

    async def __async_run(self):
        """Async run the embed command"""
        proj_config, embedding_config, vector_config = self.__load_project()
        file_content_map = self.__create_file_content_map(proj_config)
        if file_content_map is None:
            return

        emb_provider = self.__create_embedding_provider(embedding_config)
        vector_store = self.__create_vector_store(vector_config)

        emb_manager = EmbeddingManager(emb_provider, vector_store)
        await self.__embed_docs(emb_manager, file_content_map)
