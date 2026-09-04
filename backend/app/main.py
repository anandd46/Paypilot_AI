"""PayPilot AI — FastAPI Application Entry Point."""
from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.core.config import get_settings
from app.core.database import engine

settings = get_settings()

# ── Rate limiter ───────────────────────────────────────────────────────────────
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application startup / shutdown."""
    # Pre-fit TF-IDF on startup for faster first search
    try:
        from app.ai.embeddings.tfidf_embeddings import get_tfidf_provider
        from app.core.database import AsyncSessionLocal
        from app.models import Product
        from sqlalchemy import select

        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(Product).where(Product.is_active == True).limit(500)  # noqa: E712
            )
            products = result.scalars().all()
            if products:
                provider = get_tfidf_provider()
                provider.fit([p.to_dict() for p in products])
    except Exception:
        pass  # Non-fatal — will fit on first search

    yield

    await engine.dispose()


# ── Application ────────────────────────────────────────────────────────────────
app = FastAPI(
    title="PayPilot AI",
    description="Autonomous Merchant Growth & Agentic Checkout Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ── Middleware ─────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore[arg-type]

# ── Routers ────────────────────────────────────────────────────────────────────
from app.api.v1 import (  # noqa: E402
    auth,
    products,
    cart,
    assistant,
    recommendations,
    checkout,
    payments,
    orders,
    analytics,
    agent,
    audit,
    webhooks,
    health,
    admin,
)

API_PREFIX = "/api/v1"

app.include_router(health.router, tags=["Health"])
app.include_router(auth.router, prefix=f"{API_PREFIX}/auth", tags=["Authentication"])
app.include_router(products.router, prefix=f"{API_PREFIX}/products", tags=["Products"])
app.include_router(cart.router, prefix=f"{API_PREFIX}/cart", tags=["Cart"])
app.include_router(assistant.router, prefix=f"{API_PREFIX}/assistant", tags=["AI Assistant"])
app.include_router(recommendations.router, prefix=f"{API_PREFIX}/recommendations", tags=["Recommendations"])
app.include_router(checkout.router, prefix=f"{API_PREFIX}/checkout", tags=["Checkout"])
app.include_router(payments.router, prefix=f"{API_PREFIX}/payments", tags=["Payments"])
app.include_router(orders.router, prefix=f"{API_PREFIX}/orders", tags=["Orders"])
app.include_router(analytics.router, prefix=f"{API_PREFIX}/analytics", tags=["Analytics"])
app.include_router(agent.router, prefix=f"{API_PREFIX}/agent", tags=["Agent"])
app.include_router(audit.router, prefix=f"{API_PREFIX}/audit", tags=["Audit"])
app.include_router(webhooks.router, prefix=f"{API_PREFIX}/webhooks", tags=["Webhooks"])
app.include_router(admin.router, prefix=f"{API_PREFIX}/admin", tags=["Admin"])


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "name": "PayPilot AI",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "operational",
    }
