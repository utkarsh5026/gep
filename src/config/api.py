from enum import Enum
from typing import Optional

import keyring


class APIProvider(Enum):
    """API providers supported by GEP"""
    OPENAI = "openai"
    GEMINI = "gemini"
    CLAUDE = "claude"
    HUGGINGFACE = "huggingface"


class APIKeyManager:
    """Manages API keys securely using system keyring"""

    SERVICE_NAME = "gep"

    @classmethod
    def set_api_key(cls, provider: APIProvider, api_key: str) -> None:
        """Store API key in system keyring"""
        keyring.set_password(cls.SERVICE_NAME, provider.value, api_key)

    @classmethod
    def get_api_key(cls, provider: APIProvider) -> Optional[str]:
        """Retrieve API key from system keyring"""
        return keyring.get_password(cls.SERVICE_NAME, provider.value)

    @classmethod
    def delete_api_key(cls, provider: APIProvider) -> None:
        """Delete API key from system keyring"""
        keyring.delete_password(cls.SERVICE_NAME, provider.value)


def verify_provider(name: str) -> APIProvider:
    """Verify the provider is valid"""
    if name.lower() in APIProvider.__members__.values():
        return APIProvider(name.lower())
    raise ValueError(f"Invalid provider: {name}")
