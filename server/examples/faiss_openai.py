
from langchain_openai import ChatOpenAI
import asyncio

import os
from dotenv import load_dotenv
import sys
sys.path.append('..')


load_dotenv()


async def main():
    from src.vector import EmbeddingManager, OpenAIEmbeddingProvider, FAISSVectorStore, EmbeddingProviderConfig, create_file_content_map
    from src.query import QueryProcessor
    from src.prompt import PromptType, PromptProviderType
    from src.cmd import create_output_manager

    file_content_map = create_file_content_map(
        root_dir=os.path.join("..", "src", "watcher"),
        accept_patterns=["*.py"])

    config = EmbeddingProviderConfig(model_name="text-embedding-3-small")
    embedding_provider = OpenAIEmbeddingProvider(config=config)
    vector_store = FAISSVectorStore(
        dimension=1536,
        index_path="faiss_index.bin")

    embedding_manager = EmbeddingManager(
        embedding_provider=embedding_provider,
        vector_store=vector_store,
    )

    texts = list(file_content_map.values())
    metadatas = [{"source": file_path}
                 for file_path in file_content_map.keys()]

    await embedding_manager.add_texts(texts=texts, metadatas=metadatas)

    query_processor = QueryProcessor(embedding_manager=embedding_manager,
                                     llm=ChatOpenAI())

    output_manager = create_output_manager()

    async for result in query_processor.process_query(query="how file watching is implemented", prompt_type=PromptType.AGGREGATE, prompt_provider=PromptProviderType.SEMANTIC):
        await output_manager.print_stream(result.content)


if __name__ == "__main__":
    asyncio.run(main())
