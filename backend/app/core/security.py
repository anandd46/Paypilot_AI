"""Security utilities — JWT, password hashing, and token verification."""
from __future__ import annotations

import hmac
import secrets
from datetime import UTC, datetime, timedelta
from typing import Any
import bcrypt

from jose import JWTError, jwt

from app.core.config import get_settings

settings = get_settings()


# ── Password ───────────────────────────────────────────────────────────────────

def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hash."""
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False


# ── JWT ────────────────────────────────────────────────────────────────────────

def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(UTC) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    to_encode["exp"] = expire
    to_encode["type"] = "access"
    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_refresh_token(data: dict[str, Any]) -> str:
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(days=settings.refresh_token_expire_days)
    to_encode["exp"] = expire
    to_encode["type"] = "refresh"
    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict[str, Any]:
    try:
        payload: dict[str, Any] = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        return payload
    except JWTError as e:
        raise ValueError(f"Invalid token: {e}") from e


# ── Idempotency ────────────────────────────────────────────────────────────────

def generate_idempotency_key() -> str:
    return secrets.token_urlsafe(32)


# ── HMAC ──────────────────────────────────────────────────────────────────────

def verify_hmac_signature(payload: bytes, signature: str, secret: str) -> bool:
    """Timing-safe HMAC-SHA256 signature verification."""
    expected = hmac.new(secret.encode(), payload, "sha256").hexdigest()
    return hmac.compare_digest(expected, signature)
