"""AI provider factory."""
from __future__ import annotations

from app.ai.providers.base import BaseAIProvider
from app.core.config import get_settings

_provider_instance: BaseAIProvider | None = None


def get_ai_provider() -> BaseAIProvider:
    """Return the configured AI provider (singleton)."""
    global _provider_instance
    if _provider_instance is not None:
        return _provider_instance

    settings = get_settings()
    provider_name = settings.effective_ai_provider

    if provider_name == "openai":
        from app.ai.providers.openai_provider import OpenAIProvider
        _provider_instance = OpenAIProvider()
    else:
        from app.ai.providers.mock_provider import MockAIProvider
        _provider_instance = MockAIProvider()

    return _provider_instance
