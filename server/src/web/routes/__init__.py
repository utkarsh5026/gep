from .github import router as github_router
from .llm import router as llm_router
from .settings import router as settings_router

__all__ = ["github_router", "llm_router", "settings_router"]
