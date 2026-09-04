"""Payment routes — verify signature, demo payment, failure handling."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_user
from app.core.config import get_settings
from app.core.database import get_db
from app.main import limiter
from app.models import AuditLog, Order, OrderStatus, Payment, PaymentStatus, User
from app.payments.demo_payment import DemoPaymentService
from app.payments.razorpay_service import RazorpayService
from app.schemas.schemas import PaymentResponse, PaymentVerifyDemoRequest, PaymentVerifyRequest
from app.services.order_service import OrderService

router = APIRouter()
settings = get_settings()


async def _finalize_payment_success(
    db: "AsyncSession",
    order: Order,
    payment: Payment,
    user_id: str,
) -> None:
    """Atomic: update payment + order + confirm inventory + audit."""
    order_svc = OrderService(db)
    payment.status = PaymentStatus.captured
    order = await order_svc.transition_status(order.id, OrderStatus.paid)
    await order_svc.confirm_inventory(order.id)
    db.add(AuditLog(
        user_id=user_id,
        action="payment_success",
        entity_type="payment",
        entity_id=payment.id,
        details={"order_id": order.id, "amount": float(payment.amount)},
    ))
    await db.commit()


async def _finalize_payment_failure(
    db: "AsyncSession",
    order: Order,
    payment: Payment,
    user_id: str,
    reason: str,
) -> None:
    """Atomic: update payment failed + order + release inventory + audit."""
    order_svc = OrderService(db)
    payment.status = PaymentStatus.failed
    payment.failure_reason = reason
    await order_svc.transition_status(order.id, OrderStatus.payment_failed)
    await order_svc.release_inventory(order.id)
    db.add(AuditLog(
        user_id=user_id,
        action="payment_failed",
        entity_type="payment",
        entity_id=payment.id,
        details={"reason": reason, "order_id": order.id},
    ))
    await db.commit()


@router.post("/verify", response_model=PaymentResponse)
@limiter.limit("10/minute")
async def verify_payment(
    request: Request,
    data: PaymentVerifyRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PaymentResponse:
    """Verify Razorpay payment signature and fulfill order."""
    if settings.is_demo_payment:
        raise HTTPException(status_code=400, detail="Use /verify-demo in demo mode")

    order_result = await db.execute(
        select(Order).where(
            Order.id == data.order_id,
            Order.user_id == current_user.id,
        )
    )
    order = order_result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Verify the Razorpay order ID matches our DB record
    if order.razorpay_order_id != data.razorpay_order_id:
        raise HTTPException(status_code=400, detail="Order ID mismatch")

    # Verify signature — HMAC-SHA256 timing-safe comparison
    razorpay_svc = RazorpayService()
    if not razorpay_svc.verify_payment_signature(
        data.razorpay_order_id,
        data.razorpay_payment_id,
        data.razorpay_signature,
    ):
        # Record failure
        payment = Payment(
            order_id=order.id,
            razorpay_payment_id=data.razorpay_payment_id,
            razorpay_order_id=data.razorpay_order_id,
            amount=float(order.amount),
            status=PaymentStatus.failed,
            failure_reason="Invalid payment signature",
            provider="razorpay",
        )
        db.add(payment)
        await _finalize_payment_failure(db, order, payment, current_user.id, "Invalid signature")
        raise HTTPException(status_code=400, detail="Payment signature verification failed")

    # Create payment record
    payment = Payment(
        order_id=order.id,
        razorpay_payment_id=data.razorpay_payment_id,
        razorpay_order_id=data.razorpay_order_id,
        amount=float(order.amount),
        status=PaymentStatus.captured,
        provider="razorpay",
    )
    db.add(payment)
    await db.flush()
    await _finalize_payment_success(db, order, payment, current_user.id)

    return PaymentResponse(
        id=payment.id,
        order_id=order.id,
        razorpay_payment_id=payment.razorpay_payment_id,
        amount=float(payment.amount),
        currency="INR",
        status=payment.status.value,
        failure_reason=None,
        provider="razorpay",
        created_at=payment.created_at,
    )


@router.post("/verify-demo", response_model=PaymentResponse)
@limiter.limit("10/minute")
async def verify_demo_payment(
    request: Request,
    data: PaymentVerifyDemoRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PaymentResponse:
    """Simulate payment success or failure in demo mode."""
    order_result = await db.execute(
        select(Order).where(
            Order.id == data.order_id,
            Order.user_id == current_user.id,
        )
    )
    order = order_result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    demo_svc = DemoPaymentService()
    payment_result = demo_svc.simulate_payment(
        order.razorpay_order_id or f"demo_{order.id}",
        simulate_failure=data.simulate_failure,
    )

    payment = Payment(
        order_id=order.id,
        razorpay_payment_id=payment_result["payment_id"],
        razorpay_order_id=order.razorpay_order_id,
        amount=float(order.amount),
        status=PaymentStatus.created,
        provider="demo",
    )
    db.add(payment)
    await db.flush()

    if data.simulate_failure:
        await _finalize_payment_failure(db, order, payment, current_user.id, payment_result["failure_reason"])
    else:
        await _finalize_payment_success(db, order, payment, current_user.id)

    return PaymentResponse(
        id=payment.id,
        order_id=order.id,
        razorpay_payment_id=payment.razorpay_payment_id,
        amount=float(payment.amount),
        currency="INR",
        status=payment.status.value,
        failure_reason=payment.failure_reason,
        provider="demo",
        created_at=payment.created_at,
    )
