from enum import Enum
from typing import Optional

import keyring


class APIProvider(Enum):
    """API providers supported by GEP"""
    OPENAI = "openai"
    GEMINI = "gemini"
    CLAUDE = "claude"
    HUGGINGFACE = "huggingface"


class APIKeyNotFoundError(Exception):
    """Raised when an API key is not found"""

    def __init__(self, provider: APIProvider) -> None:
        super().__init__(f"API key not found for {provider.value}")


class InvalidProviderError(Exception):
    """Raised when an invalid provider is provided"""

    def __init__(self, provider: str) -> None:
        super().__init__(f"Invalid provider: {provider}")


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
        api_key = keyring.get_password(cls.SERVICE_NAME, provider.value)
        if not api_key:
            raise APIKeyNotFoundError(provider)
        return api_key

    @classmethod
    def delete_api_key(cls, provider: APIProvider) -> None:
        """Delete API key from system keyring"""
        keyring.delete_password(cls.SERVICE_NAME, provider.value)


def verify_provider(name: str) -> APIProvider:
    """Verify the provider is valid"""
    try:
        return APIProvider(name.lower())
    except ValueError:
        raise InvalidProviderError(name)
