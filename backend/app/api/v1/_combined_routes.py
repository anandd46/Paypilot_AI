"""Remaining API routes — orders, recommendations, analytics, agent, audit, webhooks, admin."""
from __future__ import annotations

# ── orders.py ─────────────────────────────────────────────────────────────────
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.v1.deps import get_current_user, require_admin, require_merchant
from app.core.config import get_settings
from app.core.database import get_db
from app.models import (
    AgentAction,
    AuditLog,
    Conversation,
    Order,
    OrderItem,
    OrderStatus,
    Payment,
    PaymentStatus,
    Product,
    Recommendation,
    User,
    WebhookEvent,
    WebhookStatus,
)
from app.schemas.schemas import (
    AgentActionResponse,
    AnalyticsOverview,
    AuditLogResponse,
    OrderItemResponse,
    OrderResponse,
    PaginatedResponse,
    PaymentResponse,
    RecommendationResponse,
)

settings = get_settings()

# ────────────────────────────── ORDERS ────────────────────────────────────────
orders_router = APIRouter()


def _build_order_response(order: Order) -> OrderResponse:
    items = [
        OrderItemResponse(
            id=i.id, product_id=i.product_id, product_name=i.product_name,
            quantity=i.quantity, price=float(i.price),
        )
        for i in (order.items or [])
    ]
    payments = [
        PaymentResponse(
            id=p.id, order_id=p.order_id, razorpay_payment_id=p.razorpay_payment_id,
            amount=float(p.amount), currency=p.currency, status=p.status.value,
            failure_reason=p.failure_reason, provider=p.provider,
            created_at=p.created_at,
        )
        for p in (order.payments or [])
    ]
    return OrderResponse(
        id=order.id, status=order.status.value, amount=float(order.amount),
        currency=order.currency, razorpay_order_id=order.razorpay_order_id,
        items=items, payments=payments,
        created_at=order.created_at, updated_at=order.updated_at,
    )


@orders_router.get("", response_model=PaginatedResponse)
async def list_orders(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PaginatedResponse:
    query = (
        select(Order)
        .options(selectinload(Order.items), selectinload(Order.payments))
        .where(and_(Order.user_id == current_user.id, Order.status != OrderStatus.draft))
        .order_by(Order.created_at.desc())
    )
    count_result = await db.execute(select(func.count()).select_from(
        select(Order).where(and_(Order.user_id == current_user.id, Order.status != OrderStatus.draft)).subquery()
    ))
    total = count_result.scalar_one()
    result = await db.execute(query.offset((page - 1) * limit).limit(limit))
    orders = result.scalars().all()
    return PaginatedResponse(
        items=[_build_order_response(o) for o in orders],
        total=total, page=page, limit=limit, pages=-(-total // limit),
    )


@orders_router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> OrderResponse:
    result = await db.execute(
        select(Order)
        .options(selectinload(Order.items), selectinload(Order.payments))
        .where(and_(Order.id == order_id, Order.user_id == current_user.id))
    )
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return _build_order_response(order)


# ──────────────────────────── RECOMMENDATIONS ─────────────────────────────────
recommendations_router = APIRouter()


@recommendations_router.get("", response_model=list[dict])
async def get_recommendations(
    category: str | None = None,
    budget_max: float | None = None,
    limit: int = Query(default=5, ge=1, le=20),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[dict]:  # type: ignore[type-arg]
    from app.services.recommendation_service import RecommendationService
    svc = RecommendationService(db)

    # Fetch top-rated products in category
    query = select(Product).where(Product.is_active == True, Product.stock > 0)  # noqa: E712
    if category:
        query = query.where(Product.category.ilike(f"%{category}%"))
    if budget_max:
        query = query.where(Product.price <= budget_max)
    query = query.order_by(Product.rating.desc()).limit(20)
    result = await db.execute(query)
    products = result.scalars().all()

    from app.agents.tools import _product_to_dict
    product_dicts = [_product_to_dict(p) for p in products]
    recs = await svc.get_recommendations(
        user_id=current_user.id,
        intent="recommendation",
        entities={"category": category, "budget_max": budget_max},
        products=product_dicts,
    )
    return recs[:limit]


# ──────────────────────────── ANALYTICS ──────────────────────────────────────
analytics_router = APIRouter()


@analytics_router.get("/overview", response_model=AnalyticsOverview)
async def analytics_overview(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_merchant),
) -> AnalyticsOverview:
    # Total orders (paid/completed)
    completed_orders_result = await db.execute(
        select(func.count(), func.coalesce(func.sum(Order.amount), 0))
        .where(Order.status.in_([OrderStatus.paid, OrderStatus.completed]))
    )
    row = completed_orders_result.one()
    total_orders, total_revenue = int(row[0]), float(row[1])

    # Unique customers
    customers_result = await db.execute(
        select(func.count(Order.user_id.distinct()))
        .where(Order.status.in_([OrderStatus.paid, OrderStatus.completed]))
    )
    total_customers = customers_result.scalar_one()

    avg_order_value = total_revenue / max(total_orders, 1)

    # Failed payments
    failed_result = await db.execute(
        select(func.count()).where(Payment.status == PaymentStatus.failed)
    )
    failed_payments = failed_result.scalar_one()

    # AI-assisted orders (via agent conversations)
    ai_orders_result = await db.execute(
        select(func.count(AgentAction.id.distinct()))
        .where(AgentAction.action_type == "checkout")
    )
    ai_assisted = ai_orders_result.scalar_one()

    total_payments = total_orders + failed_payments
    success_rate = (total_orders / total_payments * 100) if total_payments > 0 else 100.0

    return AnalyticsOverview(
        total_revenue=total_revenue,
        total_orders=total_orders,
        total_customers=total_customers,
        avg_order_value=avg_order_value,
        conversion_rate=min(100.0, success_rate),
        ai_assisted_orders=ai_assisted,
        ai_assisted_revenue=total_revenue * 0.42,  # Demo metric
        upsell_revenue=total_revenue * 0.15,
        cross_sell_revenue=total_revenue * 0.12,
        payment_success_rate=success_rate,
        failed_payments=failed_payments,
        is_demo=True,
    )


@analytics_router.get("/revenue")
async def analytics_revenue(
    days: int = Query(default=30, ge=7, le=365),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_merchant),
) -> list[dict]:  # type: ignore[type-arg]
    from datetime import UTC, datetime, timedelta
    # Return seeded-style daily revenue data
    start = datetime.now(UTC).replace(tzinfo=None) - timedelta(days=days)
    result = await db.execute(
        select(
            func.date(Order.created_at).label("date"),
            func.count(Order.id).label("orders"),
            func.coalesce(func.sum(Order.amount), 0).label("revenue"),
        )
        .where(
            Order.status.in_([OrderStatus.paid, OrderStatus.completed]),
            Order.created_at >= start,
        )
        .group_by(func.date(Order.created_at))
        .order_by(func.date(Order.created_at))
    )
    return [
        {"date": str(row.date), "revenue": float(row.revenue), "orders": row.orders, "ai_revenue": float(row.revenue) * 0.4}
        for row in result.all()
    ]


# ──────────────────────────── AGENT ──────────────────────────────────────────
agent_router = APIRouter()


@agent_router.get("/activity", response_model=PaginatedResponse)
async def agent_activity(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_merchant),
) -> PaginatedResponse:
    count_result = await db.execute(select(func.count(AgentAction.id)))
    total = count_result.scalar_one()
    result = await db.execute(
        select(AgentAction).order_by(AgentAction.created_at.desc())
        .offset((page - 1) * limit).limit(limit)
    )
    actions = result.scalars().all()
    return PaginatedResponse(
        items=[
            AgentActionResponse(
                id=a.id, conversation_id=a.conversation_id, action_type=a.action_type,
                description=a.description, intent=a.intent, provider=a.provider,
                prompt_version=a.prompt_version, tool_calls=a.tool_calls or [],
                duration_ms=a.duration_ms, confidence=a.confidence, status=a.status,
                created_at=a.created_at,
            ).model_dump()
            for a in actions
        ],
        total=total, page=page, limit=limit, pages=-(-total // limit),
    )


# ──────────────────────────── AUDIT ──────────────────────────────────────────
audit_router = APIRouter()


@audit_router.get("", response_model=PaginatedResponse)
async def audit_logs(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> PaginatedResponse:
    count_result = await db.execute(select(func.count(AuditLog.id)))
    total = count_result.scalar_one()
    result = await db.execute(
        select(AuditLog).order_by(AuditLog.timestamp.desc())
        .offset((page - 1) * limit).limit(limit)
    )
    logs = result.scalars().all()
    return PaginatedResponse(
        items=[
            AuditLogResponse(
                id=l.id, user_id=l.user_id, action=l.action, entity_type=l.entity_type,
                entity_id=l.entity_id, details=l.details or {}, timestamp=l.timestamp,
            ).model_dump()
            for l in logs
        ],
        total=total, page=page, limit=limit, pages=-(-total // limit),
    )


# ──────────────────────────── WEBHOOKS ───────────────────────────────────────
webhooks_router = APIRouter()


@webhooks_router.post("/razorpay", status_code=200)
async def razorpay_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    body = await request.body()
    signature = request.headers.get("x-razorpay-signature", "")

    # Verify signature
    if not settings.is_demo_payment:
        from app.payments.razorpay_service import RazorpayService
        svc = RazorpayService()
        if not svc.verify_webhook_signature(body, signature):
            return {"status": "invalid_signature"}

    import json
    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        return {"status": "invalid_payload"}

    event_id = payload.get("event", "") + "_" + payload.get("payload", {}).get("payment", {}).get("entity", {}).get("id", "")
    event_type = payload.get("event", "unknown")

    # Idempotency check
    existing = await db.execute(select(WebhookEvent).where(WebhookEvent.event_id == event_id))
    if existing.scalar_one_or_none():
        return {"status": "duplicate"}

    webhook_event = WebhookEvent(
        event_id=event_id,
        event_type=event_type,
        payload=payload,
        status=WebhookStatus.received,
    )
    db.add(webhook_event)
    await db.flush()

    # Process
    try:
        payment_entity = payload.get("payload", {}).get("payment", {}).get("entity", {})
        razorpay_order_id = payment_entity.get("order_id")

        if razorpay_order_id:
            order_result = await db.execute(
                select(Order).where(Order.razorpay_order_id == razorpay_order_id)
            )
            order = order_result.scalar_one_or_none()

            if order:
                from app.services.order_service import OrderService
                order_svc = OrderService(db)
                if event_type == "payment.captured":
                    await order_svc.transition_status(order.id, OrderStatus.paid)
                    await order_svc.confirm_inventory(order.id)
                elif event_type == "payment.failed":
                    await order_svc.transition_status(order.id, OrderStatus.payment_failed)
                    await order_svc.release_inventory(order.id)

        webhook_event.status = WebhookStatus.processed
        from datetime import UTC, datetime
        webhook_event.processed_at = datetime.now(UTC).replace(tzinfo=None)

    except Exception as e:
        webhook_event.status = WebhookStatus.failed
        webhook_event.error_message = str(e)

    await db.commit()
    return {"status": "ok"}


# ──────────────────────────── ADMIN ──────────────────────────────────────────
admin_router = APIRouter()


@admin_router.get("/users", response_model=PaginatedResponse)
async def list_users(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> PaginatedResponse:
    from app.schemas.schemas import UserResponse
    count_result = await db.execute(select(func.count(User.id)))
    total = count_result.scalar_one()
    result = await db.execute(
        select(User).order_by(User.created_at.desc())
        .offset((page - 1) * limit).limit(limit)
    )
    users = result.scalars().all()
    return PaginatedResponse(
        items=[UserResponse.model_validate(u).model_dump() for u in users],
        total=total, page=page, limit=limit, pages=-(-total // limit),
    )


@admin_router.get("/system")
async def system_info(
    current_user: User = Depends(require_admin),
) -> dict:  # type: ignore[type-arg]
    return {
        "ai_provider": settings.effective_ai_provider,
        "payment_provider": settings.effective_payment_provider,
        "is_demo_ai": settings.is_demo_ai,
        "is_demo_payment": settings.is_demo_payment,
        "app_env": settings.app_env,
        "version": "1.0.0",
    }
