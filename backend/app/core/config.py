"""PayPilot AI — Application Configuration."""
from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ───────────────────────────
    app_name: str = "PayPilot AI"
    app_env: Literal["development", "staging", "production"] = "development"
    debug: bool = True
    secret_key: str = "change-this-in-production-min-32-chars"

    # ── Database ──────────────────────────────
    database_url: str = "postgresql+asyncpg://paypilot:paypilot_pass@localhost:5432/paypilot_db"
    database_url_sync: str = "postgresql://paypilot:paypilot_pass@localhost:5432/paypilot_db"

    # ── JWT ───────────────────────────────────
    jwt_secret_key: str = "change-this-jwt-secret-min-32-characters"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    # ── AI Provider ───────────────────────────
    ai_provider: Literal["openai", "mock"] = "mock"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    openai_embedding_model: str = "text-embedding-3-small"

    # ── Embedding Provider ────────────────────
    embedding_provider: Literal["openai", "sentence_transformer", "tfidf"] = "tfidf"

    # ── Payments ──────────────────────────────
    payment_provider: Literal["razorpay", "demo"] = "demo"
    razorpay_key_id: str = ""
    razorpay_key_secret: str = ""
    razorpay_webhook_secret: str = ""

    # ── CORS ──────────────────────────────────
    allowed_origins: str = "http://localhost:3000,http://127.0.0.1:3000"

    # ── Inventory ─────────────────────────────
    inventory_reservation_minutes: int = 15

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]

    @property
    def is_demo_ai(self) -> bool:
        return self.ai_provider == "mock" or not self.openai_api_key

    @property
    def is_demo_payment(self) -> bool:
        return self.payment_provider == "demo" or not self.razorpay_key_id

    @property
    def effective_ai_provider(self) -> str:
        if self.is_demo_ai:
            return "mock"
        return self.ai_provider

    @property
    def effective_payment_provider(self) -> str:
        if self.is_demo_payment:
            return "demo"
        return self.payment_provider


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings()
