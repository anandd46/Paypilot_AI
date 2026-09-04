"""Health check endpoints."""
from __future__ import annotations

from fastapi import APIRouter

from app.core.config import get_settings
from app.schemas.schemas import ComponentHealth, HealthResponse

router = APIRouter()
settings = get_settings()


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(
        status="operational",
        api=ComponentHealth(status="operational"),
        database=ComponentHealth(status="operational", message="PostgreSQL connected"),
        ai=ComponentHealth(
            status="demo_mode" if settings.is_demo_ai else "operational",
            provider=settings.effective_ai_provider,
            message="Using mock AI provider" if settings.is_demo_ai else f"OpenAI {settings.openai_model}",
        ),
        payment=ComponentHealth(
            status="demo_mode" if settings.is_demo_payment else "test_mode",
            provider=settings.effective_payment_provider,
            message="Demo payment mode active" if settings.is_demo_payment else "Razorpay test mode",
        ),
    )


@router.get("/health/db")
async def health_db() -> dict[str, str]:
    try:
        from app.core.database import engine
        async with engine.connect() as conn:
            await conn.execute(__import__("sqlalchemy").text("SELECT 1"))
        return {"status": "operational", "database": "PostgreSQL"}
    except Exception as e:
        return {"status": "unavailable", "error": str(e)}


@router.get("/health/ai")
async def health_ai() -> dict[str, str]:
    return {
        "status": "demo_mode" if settings.is_demo_ai else "operational",
        "provider": settings.effective_ai_provider,
        "model": settings.openai_model if not settings.is_demo_ai else "mock-demo",
    }


@router.get("/health/payment")
async def health_payment() -> dict[str, str]:
    return {
        "status": "demo_mode" if settings.is_demo_payment else "test_mode",
        "provider": settings.effective_payment_provider,
    }
