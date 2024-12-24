from .prompt import PromptProviderType, PromptType, PromptProvider
from .semantic import SemanticPromptProvider


def get_provider(prompt_type: PromptProviderType) -> PromptProvider:
    if prompt_type == PromptProviderType.SEMANTIC:
        return SemanticPromptProvider()


def get_prompt_function(prompt_type: PromptType, prompt_provider: PromptProviderType):
    provider = get_provider(prompt_provider)
    if prompt_type == PromptType.FILE_WISE:
        return provider.get_file_wise_prompt
    elif prompt_type == PromptType.AGGREGATE:
        return provider.get_aggregate_prompt
