"""Cart service — all cart mutations go through here (never through LLM)."""
from __future__ import annotations

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Cart, CartItem, CartStatus, Product


class CartService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_or_create_cart(self, user_id: str) -> Cart:
        result = await self._db.execute(
            select(Cart)
            .options(selectinload(Cart.items).selectinload(CartItem.product))
            .where(and_(Cart.user_id == user_id, Cart.status == CartStatus.active))
            .order_by(Cart.created_at.desc())
            .limit(1)
        )
        cart = result.scalar_one_or_none()
        if not cart:
            cart = Cart(user_id=user_id)
            self._db.add(cart)
            await self._db.flush()
            await self._db.refresh(cart, ["items"])
        return cart

    async def add_item(self, user_id: str, product_id: str, quantity: int = 1) -> Cart:
        # Verify product exists and is in stock (DB is source of truth)
        prod_result = await self._db.execute(
            select(Product).where(
                and_(Product.id == product_id, Product.is_active == True)  # noqa: E712
            )
        )
        product = prod_result.scalar_one_or_none()
        if not product:
            raise ValueError("Product not found or unavailable")
        if product.stock < quantity:
            raise ValueError(f"Only {product.stock} units available")

        cart = await self.get_or_create_cart(user_id)

        # Check if already in cart
        existing_result = await self._db.execute(
            select(CartItem).where(
                and_(CartItem.cart_id == cart.id, CartItem.product_id == product_id)
            )
        )
        existing = existing_result.scalar_one_or_none()

        if existing:
            new_qty = existing.quantity + quantity
            if product.stock < new_qty:
                raise ValueError(f"Only {product.stock} units available")
            existing.quantity = new_qty
            existing.total_price = float(product.price) * new_qty
        else:
            item = CartItem(
                cart_id=cart.id,
                product_id=product_id,
                quantity=quantity,
                unit_price=float(product.price),
                total_price=float(product.price) * quantity,
            )
            self._db.add(item)

        await self._db.flush()
        return await self._recalculate_and_refresh(cart.id)

    async def remove_item(self, cart_id: str, item_id: str) -> Cart:
        result = await self._db.execute(
            select(CartItem).where(
                and_(CartItem.id == item_id, CartItem.cart_id == cart_id)
            )
        )
        item = result.scalar_one_or_none()
        if item:
            await self._db.delete(item)
            await self._db.flush()
        return await self._recalculate_and_refresh(cart_id)

    async def update_quantity(self, cart_id: str, item_id: str, quantity: int) -> Cart:
        result = await self._db.execute(
            select(CartItem)
            .options(selectinload(CartItem.product))
            .where(and_(CartItem.id == item_id, CartItem.cart_id == cart_id))
        )
        item = result.scalar_one_or_none()
        if not item:
            raise ValueError("Cart item not found")
        if item.product and item.product.stock < quantity:
            raise ValueError(f"Only {item.product.stock} units available")

        item.quantity = quantity
        item.total_price = float(item.unit_price) * quantity
        await self._db.flush()
        return await self._recalculate_and_refresh(cart_id)

    async def _recalculate_and_refresh(self, cart_id: str) -> Cart:
        result = await self._db.execute(
            select(Cart)
            .options(selectinload(Cart.items).selectinload(CartItem.product))
            .where(Cart.id == cart_id)
        )
        cart = result.scalar_one()

        subtotal = sum(float(item.total_price) for item in cart.items)
        cart.subtotal = subtotal
        cart.discount = 0.0
        cart.total = subtotal - float(cart.discount)

        await self._db.commit()

        # Re-query after commit to get fresh data with relationships eagerly loaded.
        # Do NOT use db.refresh() here — it does not reload selectinload relationships
        # and causes MissingGreenlet when cart.items is accessed lazily in async context.
        result = await self._db.execute(
            select(Cart)
            .options(selectinload(Cart.items).selectinload(CartItem.product))
            .where(Cart.id == cart_id)
        )
        return result.scalar_one()


    async def clear_cart(self, cart_id: str) -> None:
        result = await self._db.execute(
            select(CartItem).where(CartItem.cart_id == cart_id)
        )
        for item in result.scalars().all():
            await self._db.delete(item)
        await self._db.flush()

    async def mark_checked_out(self, cart_id: str) -> None:
        result = await self._db.execute(select(Cart).where(Cart.id == cart_id))
        cart = result.scalar_one()
        cart.status = CartStatus.checked_out
        await self._db.flush()
