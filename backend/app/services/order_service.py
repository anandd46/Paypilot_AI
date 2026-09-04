"""Order service — atomic checkout, state machine transitions, inventory."""
from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import get_settings
from app.core.security import generate_idempotency_key
from app.models import (
    Cart,
    CartItem,
    CartStatus,
    InventoryReservation,
    Order,
    OrderItem,
    OrderStatus,
    Payment,
    PaymentStatus,
    Product,
    ReservationStatus,
)

settings = get_settings()


class OrderService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def create_order_from_cart(
        self,
        user_id: str,
        cart_id: str,
        idempotency_key: str | None = None,
    ) -> Order:
        """Atomic: validate cart + stock + reserve + create order — all in one transaction."""

        # Idempotency check — return existing order if key matches
        if idempotency_key:
            existing = await self._db.execute(
                select(Order).where(Order.idempotency_key == idempotency_key)
            )
            existing_order = existing.scalar_one_or_none()
            if existing_order:
                return existing_order

        # Load cart with items and products
        cart_result = await self._db.execute(
            select(Cart)
            .options(selectinload(Cart.items).selectinload(CartItem.product))
            .where(and_(Cart.id == cart_id, Cart.user_id == user_id))
        )
        cart = cart_result.scalar_one_or_none()
        if not cart:
            raise ValueError("Cart not found")
        if not cart.items:
            raise ValueError("Cart is empty")
        if cart.status != CartStatus.active:
            raise ValueError("Cart is not active")

        # Validate stock and prices (DB is source of truth)
        total = 0.0
        order_items_data: list[dict[str, Any]] = []
        for item in cart.items:
            product: Product = item.product
            if not product or not product.is_active:
                raise ValueError(f"Product '{item.product_id}' is no longer available")
            if product.stock < item.quantity:
                raise ValueError(
                    f"Only {product.stock} units of '{product.name}' available"
                )
            # Use DB price — never trust frontend price
            unit_price = float(product.price)
            line_total = unit_price * item.quantity
            total += line_total
            order_items_data.append({
                "product_id": product.id,
                "product_name": product.name,
                "quantity": item.quantity,
                "price": unit_price,
                "product_snapshot": {
                    "name": product.name,
                    "brand": product.brand,
                    "category": product.category,
                    "image_url": product.image_url,
                },
            })

        # Create order
        order = Order(
            user_id=user_id,
            status=OrderStatus.draft,
            amount=total,
            currency="INR",
            idempotency_key=idempotency_key or generate_idempotency_key(),
        )
        self._db.add(order)
        await self._db.flush()

        # Create order items
        for item_data in order_items_data:
            order_item = OrderItem(order_id=order.id, **item_data)
            self._db.add(order_item)

        # Reserve inventory
        expires_at = datetime.now(UTC).replace(tzinfo=None) + timedelta(
            minutes=settings.inventory_reservation_minutes
        )
        for item in cart.items:
            reservation = InventoryReservation(
                product_id=item.product_id,
                order_id=order.id,
                quantity=item.quantity,
                expires_at=expires_at,
                status=ReservationStatus.reserved,
            )
            self._db.add(reservation)
            # Deduct from stock
            item.product.stock -= item.quantity

        # Mark cart as checked out
        cart.status = CartStatus.checked_out

        await self._db.commit()
        await self._db.refresh(order)
        return order

    async def transition_status(self, order_id: str, new_status: OrderStatus) -> Order:
        """Enforce valid state transitions."""
        result = await self._db.execute(select(Order).where(Order.id == order_id))
        order = result.scalar_one_or_none()
        if not order:
            raise ValueError("Order not found")
        if not order.can_transition_to(new_status):
            raise ValueError(
                f"Cannot transition order from {order.status.value} to {new_status.value}"
            )
        order.status = new_status
        await self._db.flush()
        return order

    async def confirm_inventory(self, order_id: str) -> None:
        """Convert inventory reservations to confirmed sales."""
        result = await self._db.execute(
            select(InventoryReservation).where(
                and_(
                    InventoryReservation.order_id == order_id,
                    InventoryReservation.status == ReservationStatus.reserved,
                )
            )
        )
        for res in result.scalars().all():
            res.status = ReservationStatus.confirmed
        await self._db.flush()

    async def release_inventory(self, order_id: str) -> None:
        """Release inventory reservations (payment failed/cancelled)."""
        result = await self._db.execute(
            select(InventoryReservation).where(
                and_(
                    InventoryReservation.order_id == order_id,
                    InventoryReservation.status == ReservationStatus.reserved,
                )
            )
        )
        for res in result.scalars().all():
            res.status = ReservationStatus.released
            # Return stock
            prod_result = await self._db.execute(
                select(Product).where(Product.id == res.product_id)
            )
            product = prod_result.scalar_one_or_none()
            if product:
                product.stock += res.quantity
        await self._db.flush()
