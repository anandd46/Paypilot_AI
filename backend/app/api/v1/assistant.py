"""AI Assistant route — entry point for the agent state machine."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.state_machine import AgentContext, CommerceAgentStateMachine
from app.api.v1.deps import get_current_user
from app.core.config import get_settings
from app.core.database import get_db
from app.main import limiter
from app.models import AgentAction, AuditLog, Conversation, ConversationMessage, User
from app.schemas.schemas import CartResponse, ChatRequest, ChatResponse, ProductResponse

router = APIRouter()
settings = get_settings()
_agent = CommerceAgentStateMachine()


def _product_dict_to_response(p: dict) -> ProductResponse:  # type: ignore[type-arg]
    return ProductResponse(
        id=p["id"],
        name=p["name"],
        description=p.get("description", ""),
        category=p.get("category", ""),
        sub_category=None,
        price=p["price"],
        original_price=p.get("original_price"),
        discount_percent=p.get("discount_percent"),
        stock=p.get("stock", 0),
        rating=p.get("rating", 0.0),
        review_count=p.get("review_count", 0),
        brand=p.get("brand"),
        tags=p.get("tags", []),
        features=p.get("features", []),
        specifications=p.get("specifications", {}),
        cross_sell_ids=p.get("cross_sell_ids", []),
        upsell_ids=p.get("upsell_ids", []),
        image_url=p.get("image_url"),
        is_active=p.get("is_active", True),
        created_at=p.get("created_at") or datetime.now(timezone.utc),
        updated_at=p.get("updated_at") or datetime.now(timezone.utc),
    )


@router.post("/chat", response_model=ChatResponse)
@limiter.limit("30/minute")
async def chat(
    request: Request,
    data: ChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ChatResponse:
    # Get or create conversation
    session_id = data.session_id or str(uuid.uuid4())
    conv_result = await db.execute(
        select(Conversation).where(Conversation.session_id == session_id)
    )
    conversation = conv_result.scalar_one_or_none()
    if not conversation:
        conversation = Conversation(
            user_id=current_user.id,
            session_id=session_id,
        )
        db.add(conversation)
        await db.flush()

    # Store user message
    user_msg = ConversationMessage(
        conversation_id=conversation.id,
        role="user",
        message=data.message,
    )
    db.add(user_msg)
    await db.flush()

    # Run agent state machine
    ctx = AgentContext(
        user_message=data.message,
        user_id=current_user.id,
        session_id=session_id,
        conversation_id=conversation.id,
        db=db,
    )
    ctx = await _agent.run(ctx)

    # Store assistant message
    assistant_msg = ConversationMessage(
        conversation_id=conversation.id,
        role="assistant",
        message=ctx.response_message,
        intent=ctx.intent,
        metadata={
            "confidence": ctx.confidence,
            "tool_calls": ctx.tool_calls,
            "provider": settings.effective_ai_provider,
        },
    )
    db.add(assistant_msg)

    # Store agent action telemetry (no chain-of-thought)
    agent_action = AgentAction(
        conversation_id=conversation.id,
        action_type=ctx.intent or "unknown",
        description=f"User: {data.message[:100]}",
        intent=ctx.intent,
        model=settings.openai_model if not settings.is_demo_ai else "mock-demo",
        provider=settings.effective_ai_provider,
        prompt_version=ctx.prompt_version,
        tool_calls=ctx.tool_calls,
        tool_durations=ctx.tool_durations,
        duration_ms=ctx.total_duration_ms,
        confidence=ctx.confidence,
        input_summary=data.message[:200],
        output_summary=ctx.response_message[:200],
        status="success" if ctx.success else "error",
        error=ctx.error,
    )
    db.add(agent_action)

    # Audit
    db.add(AuditLog(
        user_id=current_user.id,
        action="ai_chat",
        entity_type="conversation",
        entity_id=conversation.id,
        details={"intent": ctx.intent, "confidence": ctx.confidence},
    ))

    await db.commit()

    # Build response
    products = [_product_dict_to_response(p) for p in ctx.products[:8]]

    return ChatResponse(
        session_id=session_id,
        message=ctx.response_message,
        intent=ctx.intent,
        confidence=ctx.confidence,
        products=products,
        recommendations=[],  # Simplified for response size
        cart_updated=ctx.cart_updated,
        action_taken=ctx.action_taken,
        suggested_prompts=ctx.suggested_prompts[:4],
        is_demo=settings.is_demo_ai,
        provider=settings.effective_ai_provider,
    )
