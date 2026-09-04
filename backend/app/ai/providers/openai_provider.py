"""OpenAI AI provider."""
from __future__ import annotations

import json
import re
from typing import Any

from openai import AsyncOpenAI

from app.ai.prompts.intent import INTENT_CLASSIFICATION_PROMPT, PROMPT_VERSION as INTENT_VERSION
from app.ai.prompts.system import SYSTEM_PROMPT
from app.ai.providers.base import AIMessage, AIResponse, BaseAIProvider
from app.core.config import get_settings

settings = get_settings()


class OpenAIProvider(BaseAIProvider):
    """OpenAI GPT provider."""

    def __init__(self) -> None:
        self._client = AsyncOpenAI(api_key=settings.openai_api_key)

    @property
    def provider_name(self) -> str:
        return "openai"

    @property
    def model_name(self) -> str:
        return settings.openai_model

    async def complete(
        self,
        messages: list[AIMessage],
        temperature: float = 0.3,
        max_tokens: int = 1000,
        response_format: str | None = None,
    ) -> AIResponse:
        oai_messages = [{"role": m.role, "content": m.content} for m in messages]
        kwargs: dict[str, Any] = {
            "model": self.model_name,
            "messages": oai_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if response_format == "json":
            kwargs["response_format"] = {"type": "json_object"}

        resp = await self._client.chat.completions.create(**kwargs)
        content = resp.choices[0].message.content or ""
        return AIResponse(
            content=content,
            model=self.model_name,
            provider=self.provider_name,
            usage={
                "prompt_tokens": resp.usage.prompt_tokens if resp.usage else 0,
                "completion_tokens": resp.usage.completion_tokens if resp.usage else 0,
            },
        )

    async def classify_intent(self, user_message: str) -> dict[str, Any]:
        prompt = INTENT_CLASSIFICATION_PROMPT + f'"{user_message}"'
        resp = await self.complete(
            messages=[
                AIMessage(role="system", content="You are a JSON-only intent classifier."),
                AIMessage(role="user", content=prompt),
            ],
            temperature=0.0,
            response_format="json",
        )
        try:
            result: dict[str, Any] = json.loads(resp.content)
            result["prompt_version"] = INTENT_VERSION
            return result
        except json.JSONDecodeError:
            return self._fallback_intent(user_message)

    async def generate_response(
        self,
        context: dict[str, Any],
        intent: str,
        products: list[dict[str, Any]],
    ) -> str:
        context_str = json.dumps({"intent": intent, "products_count": len(products)})
        resp = await self.complete(
            messages=[
                AIMessage(role="system", content=SYSTEM_PROMPT),
                AIMessage(role="user", content=f"Context: {context_str}\nUser: {context.get('user_message', '')}"),
            ],
            temperature=0.4,
            max_tokens=500,
        )
        return resp.content

    @staticmethod
    def _fallback_intent(message: str) -> dict[str, Any]:
        """Deterministic fallback if JSON parsing fails."""
        msg = message.lower()
        if any(w in msg for w in ["cart", "add", "buy"]):
            return {"intent": "add_to_cart", "confidence": "MEDIUM", "entities": {}}
        if any(w in msg for w in ["checkout", "pay", "purchase"]):
            return {"intent": "checkout", "confidence": "MEDIUM", "entities": {}}
        return {"intent": "product_search", "confidence": "LOW", "entities": {}}
