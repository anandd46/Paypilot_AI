"""Checkout route — atomic order creation."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.v1.deps import get_current_user
from app.core.config import get_settings
from app.core.database import get_db
from app.core.security import generate_idempotency_key
from app.main import limiter
from app.models import AuditLog, Cart, CartItem, CartStatus, Order, OrderStatus, User
from app.payments.demo_payment import DemoPaymentService
from app.payments.razorpay_service import RazorpayService
from app.schemas.schemas import CheckoutCreateRequest, CheckoutResponse
from app.services.order_service import OrderService

router = APIRouter()
settings = get_settings()


@router.post("/create", response_model=CheckoutResponse)
@limiter.limit("10/minute")
async def create_checkout(
    request: Request,
    data: CheckoutCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CheckoutResponse:
    # Find active cart
    cart_result = await db.execute(
        select(Cart)
        .options(selectinload(Cart.items).selectinload(CartItem.product))
        .where(and_(Cart.user_id == current_user.id, Cart.status == CartStatus.active))
        .order_by(Cart.created_at.desc())
        .limit(1)
    )
    cart = cart_result.scalar_one_or_none()
    if not cart or not cart.items:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cart is empty")

    idempotency_key = data.idempotency_key or generate_idempotency_key()

    # Create order atomically (validates stock + reserves inventory)
    order_svc = OrderService(db)
    try:
        order = await order_svc.create_order_from_cart(
            user_id=current_user.id,
            cart_id=cart.id,
            idempotency_key=idempotency_key,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e

    # Create payment order
    razorpay_order_id = None
    is_demo = settings.is_demo_payment

    if is_demo:
        payment_svc = DemoPaymentService()
        payment_order = payment_svc.create_order(float(order.amount))
        razorpay_order_id = payment_order["id"]
    else:
        payment_svc_real = RazorpayService()
        payment_order = payment_svc_real.create_order(
            float(order.amount),
            notes={"order_id": order.id, "user_id": current_user.id},
        )
        razorpay_order_id = payment_order["id"]

    # Update order with Razorpay order ID
    order.razorpay_order_id = razorpay_order_id
    order.status = OrderStatus.pending_payment
    await db.flush()

    db.add(AuditLog(
        user_id=current_user.id,
        action="checkout_created",
        entity_type="order",
        entity_id=order.id,
        details={"amount": float(order.amount), "is_demo": is_demo},
    ))
    await db.commit()

    return CheckoutResponse(
        order_id=order.id,
        razorpay_order_id=razorpay_order_id,
        amount=float(order.amount),
        currency="INR",
        payment_provider=settings.effective_payment_provider,
        is_demo=is_demo,
        idempotency_key=idempotency_key,
    )
