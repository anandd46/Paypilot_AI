"""Abstract AI provider base class."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class AIMessage:
    role: str  # system | user | assistant
    content: str


@dataclass
class AIResponse:
    content: str
    model: str
    provider: str
    usage: dict[str, int] = field(default_factory=dict)
    raw: dict[str, Any] = field(default_factory=dict)


class BaseAIProvider(ABC):
    """Abstract base for AI completion providers."""

    @property
    @abstractmethod
    def provider_name(self) -> str: ...

    @property
    @abstractmethod
    def model_name(self) -> str: ...

    @abstractmethod
    async def complete(
        self,
        messages: list[AIMessage],
        temperature: float = 0.3,
        max_tokens: int = 1000,
        response_format: str | None = None,
    ) -> AIResponse: ...

    @abstractmethod
    async def classify_intent(self, user_message: str) -> dict[str, Any]: ...

    @abstractmethod
    async def generate_response(
        self,
        context: dict[str, Any],
        intent: str,
        products: list[dict[str, Any]],
    ) -> str: ...
