from typing import Optional, List
from dotenv import load_dotenv
from enum import Enum, auto
from langchain_openai import ChatOpenAI

load_dotenv()

class LLMProviderType(Enum):
    GPT_4O_MINI = auto()
    GPT_4O = auto()
    GPT_O3_MINI = auto()


    @classmethod
    def list_names(cls) -> List[str]:
        return [
            "gpt-4o-mini",
            "gpt-4o",
            "gpt-3.5-o-mini",
            "gpt-o3-mini",
        ]


    @classmethod
    def get_llm(cls, provider: Optional["LLMProviderType"]) -> ChatOpenAI:
        print("🔄 Getting LLM provider... ", provider)
        if provider is None:
            provider = LLMProviderType.GPT_4O_MINI

        if provider == LLMProviderType.GPT_4O_MINI:
            print("🔄 Using gpt-4o-mini")
            return ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0.7,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
            )

        elif provider == LLMProviderType.GPT_4O:
            return ChatOpenAI(
                model="gpt-4o",
                temperature=0.7,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
            )

        elif provider == LLMProviderType.GPT_O3_MINI:
            return ChatOpenAI(
                model="gpt-3.5-o-mini",
                temperature=0.7,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
            )

    @classmethod
    def from_string(cls, model_name: Optional[str]):
        if model_name is None:
            return cls.get_llm(LLMProviderType.GPT_4O_MINI)

        model_name = model_name.strip().lower()
        if model_name == "gpt-4o-mini":
            return cls.get_llm(LLMProviderType.GPT_4O_MINI)
        elif model_name == "gpt-4o":    
            return cls.get_llm(LLMProviderType.GPT_4O)
        elif model_name == "gpt-3.5-o-mini":
            return cls.get_llm(LLMProviderType.GPT_O3_MINI)


        raise ValueError(f"Unknown model name: {model_name}")


    @classmethod
    def parse_type_from_string(cls, model_name: Optional[str]) -> "LLMProviderType":
        if model_name is None:
            return LLMProviderType.GPT_4O_MINI

        model_name = model_name.strip().lower()
        if model_name == "gpt-4o-mini":
            return LLMProviderType.GPT_4O_MINI
        elif model_name == "gpt-4o":    
            return LLMProviderType.GPT_4O
        elif model_name == "gpt-3.5-o-mini":
            return LLMProviderType.GPT_O3_MINI

        raise ValueError(f"Unknown model name: {model_name}")
llm_names = LLMProviderType.list_names()
