"""Agent tools — all tool calls that the agent can make.

IMPORTANT: All tools retrieve data from the database.
The LLM NEVER directly reads or writes database records.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import (
    Cart,
    CartItem,
    CartStatus,
    Order,
    OrderStatus,
    Product,
    Recommendation,
    RecommendationType,
)

if TYPE_CHECKING:
    from app.agents.state_machine import AgentContext


class AgentTools:
    """Registry of all agent tools. Each tool queries only the DB — never invents data."""

    def __init__(self, db: AsyncSession, user_id: str) -> None:
        self._db = db
        self._user_id = user_id

    async def execute(self, tool_name: str, ctx: "AgentContext") -> dict[str, Any]:
        """Dispatch a tool call by name."""
        dispatch: dict[str, Any] = {
            "search_products": self.search_products,
            "get_product_details": self.get_product_details,
            "compare_products": self.compare_products,
            "get_recommendations": self.get_recommendations,
            "get_upsell": self.get_upsell,
            "get_cross_sell": self.get_cross_sell,
            "get_cart": self.get_cart,
            "add_to_cart": self.add_to_cart,
            "remove_from_cart": self.remove_from_cart,
            "update_cart_quantity": self.update_cart_quantity,
            "calculate_cart_total": self.calculate_cart_total,
            "create_checkout": self.create_checkout,
            "get_order_status": self.get_order_status,
            "get_order_history": self.get_order_history,
        }
        fn = dispatch.get(tool_name)
        if fn is None:
            return {"error": f"Unknown tool: {tool_name}"}
        return await fn(ctx)

    # ── Search ─────────────────────────────────────────────────────────────────

    async def search_products(self, ctx: "AgentContext") -> dict[str, Any]:
        entities = ctx.entities
        query = select(Product).where(Product.is_active == True)  # noqa: E712

        if entities.get("category"):
            query = query.where(Product.category.ilike(f"%{entities['category']}%"))
        if entities.get("budget_max"):
            query = query.where(Product.price <= entities["budget_max"])
        if entities.get("budget_min"):
            query = query.where(Product.price >= entities["budget_min"])
        if entities.get("brand"):
            query = query.where(Product.brand.ilike(f"%{entities['brand']}%"))

        query = query.order_by(Product.rating.desc()).limit(20)
        result = await self._db.execute(query)
        products = result.scalars().all()

        # Semantic re-ranking if we have a query
        if ctx.user_message and products:
            from app.ai.embeddings.tfidf_embeddings import get_tfidf_provider
            provider = get_tfidf_provider()
            product_dicts = [p.to_dict() for p in products]
            ranked = provider.rank_products(ctx.user_message, product_dicts, top_k=10)
            product_ids_ranked = [r[0]["id"] for r in ranked]
            products_by_id = {p.id: p for p in products}
            products = [products_by_id[pid] for pid in product_ids_ranked if pid in products_by_id]

        return {"products": [_product_to_dict(p) for p in products[:10]]}

    async def get_product_details(self, ctx: "AgentContext") -> dict[str, Any]:
        product_name = ctx.entities.get("product_name", "")
        query = select(Product).where(
            and_(Product.is_active == True, Product.name.ilike(f"%{product_name}%"))  # noqa: E712
        ).limit(1)
        result = await self._db.execute(query)
        product = result.scalar_one_or_none()
        if not product:
            return {"error": "Product not found"}
        return {"product": _product_to_dict(product)}

    async def compare_products(self, ctx: "AgentContext") -> dict[str, Any]:
        # Get top 2 from search results
        search_result = await self.search_products(ctx)
        products = search_result.get("products", [])[:2]
        return {"products": products}

    async def get_recommendations(self, ctx: "AgentContext") -> dict[str, Any]:
        """Score and return product recommendations."""
        from app.services.recommendation_service import RecommendationService
        svc = RecommendationService(self._db)
        recs = await svc.get_recommendations(
            user_id=self._user_id,
            intent=ctx.intent,
            entities=ctx.entities,
            products=ctx.tool_results.get("search_products", {}).get("products", []),
        )
        return {"recommendations": recs}

    async def get_upsell(self, ctx: "AgentContext") -> dict[str, Any]:
        from app.services.recommendation_service import RecommendationService
        svc = RecommendationService(self._db)
        products = ctx.tool_results.get("search_products", {}).get("products", [])
        if not products:
            return {"upsells": []}
        upsells = await svc.get_upsell(products[0], ctx.entities.get("budget_max"))
        return {"upsells": upsells}

    async def get_cross_sell(self, ctx: "AgentContext") -> dict[str, Any]:
        from app.services.recommendation_service import RecommendationService
        svc = RecommendationService(self._db)
        cart = ctx.cart or await self.get_cart(ctx)
        cross_sells = await svc.get_cross_sell(cart.get("items", []))
        return {"cross_sells": cross_sells}

    # ── Cart ───────────────────────────────────────────────────────────────────

    async def get_cart(self, ctx: "AgentContext") -> dict[str, Any]:
        cart = await _get_active_cart(self._db, self._user_id)
        if not cart:
            return {"items": [], "total": 0, "subtotal": 0, "discount": 0, "item_count": 0}
        return _cart_to_dict(cart)

    async def add_to_cart(self, ctx: "AgentContext") -> dict[str, Any]:
        from app.services.cart_service import CartService
        svc = CartService(self._db)
        products = ctx.tool_results.get("search_products", {}).get("products", [])
        if not products:
            return {"error": "No product found to add"}
        product = products[0]
        cart = await svc.add_item(
            user_id=self._user_id,
            product_id=product["id"],
            quantity=ctx.entities.get("quantity") or 1,
        )
        ctx.cart_updated = True
        return _cart_to_dict(cart)

    async def remove_from_cart(self, ctx: "AgentContext") -> dict[str, Any]:
        from app.services.cart_service import CartService
        svc = CartService(self._db)
        product_name = ctx.entities.get("product_name", "")
        cart = await _get_active_cart(self._db, self._user_id)
        if not cart:
            return {"error": "Cart is empty"}
        # Find cart item by product name
        for item in cart.items:
            if product_name.lower() in item.product.name.lower():
                updated_cart = await svc.remove_item(cart.id, item.id)
                ctx.cart_updated = True
                return _cart_to_dict(updated_cart)
        return {"error": f"'{product_name}' not found in cart"}

    async def update_cart_quantity(self, ctx: "AgentContext") -> dict[str, Any]:
        from app.services.cart_service import CartService
        svc = CartService(self._db)
        product_name = ctx.entities.get("product_name", "")
        quantity = ctx.entities.get("quantity", 1)
        cart = await _get_active_cart(self._db, self._user_id)
        if not cart:
            return {"error": "Cart is empty"}
        for item in cart.items:
            if product_name.lower() in item.product.name.lower():
                updated_cart = await svc.update_quantity(cart.id, item.id, quantity)
                ctx.cart_updated = True
                return _cart_to_dict(updated_cart)
        return {"error": f"'{product_name}' not found in cart"}

    async def calculate_cart_total(self, ctx: "AgentContext") -> dict[str, Any]:
        cart_data = await self.get_cart(ctx)
        return {"total": cart_data.get("total", 0), "items": cart_data.get("item_count", 0)}

    async def create_checkout(self, ctx: "AgentContext") -> dict[str, Any]:
        # Only prepare checkout data — actual creation is confirmed by user
        cart_data = await self.get_cart(ctx)
        return {
            "ready_for_checkout": True,
            "total": cart_data.get("total", 0),
            "item_count": cart_data.get("item_count", 0),
        }

    # ── Orders ─────────────────────────────────────────────────────────────────

    async def get_order_status(self, ctx: "AgentContext") -> dict[str, Any]:
        query = select(Order).where(
            and_(Order.user_id == self._user_id, Order.status != OrderStatus.draft)
        ).order_by(Order.created_at.desc()).limit(1)
        result = await self._db.execute(query)
        order = result.scalar_one_or_none()
        if not order:
            return {"message": "No recent orders found"}
        return {
            "order_id": order.id,
            "status": order.status.value,
            "amount": float(order.amount),
            "created_at": order.created_at.isoformat(),
        }

    async def get_order_history(self, ctx: "AgentContext") -> dict[str, Any]:
        query = select(Order).where(
            and_(Order.user_id == self._user_id, Order.status != OrderStatus.draft)
        ).order_by(Order.created_at.desc()).limit(5)
        result = await self._db.execute(query)
        orders = result.scalars().all()
        return {
            "orders": [
                {
                    "id": o.id,
                    "status": o.status.value,
                    "amount": float(o.amount),
                    "created_at": o.created_at.isoformat(),
                }
                for o in orders
            ]
        }


# ─────────────────────────── Helpers ──────────────────────────────────────────

def _product_to_dict(p: Product) -> dict[str, Any]:
    price = float(p.price)
    orig = float(p.original_price) if p.original_price else None
    discount = round((1 - price / orig) * 100, 1) if orig and orig > price else None
    return {
        "id": p.id,
        "name": p.name,
        "description": p.description,
        "category": p.category,
        "price": price,
        "original_price": orig,
        "discount_percent": discount,
        "stock": p.stock,
        "rating": p.rating,
        "review_count": p.review_count,
        "brand": p.brand,
        "tags": p.tags or [],
        "features": p.features or [],
        "specifications": p.specifications or {},
        "image_url": p.image_url,
        "is_active": p.is_active,
    }


def _cart_to_dict(cart: Cart) -> dict[str, Any]:
    return {
        "id": cart.id,
        "status": cart.status.value,
        "items": [
            {
                "id": item.id,
                "product_id": item.product_id,
                "product_name": item.product.name if item.product else "",
                "quantity": item.quantity,
                "unit_price": float(item.unit_price),
                "total_price": float(item.total_price),
            }
            for item in (cart.items or [])
        ],
        "subtotal": float(cart.subtotal),
        "discount": float(cart.discount),
        "total": float(cart.total),
        "item_count": len(cart.items or []),
    }


async def _get_active_cart(db: AsyncSession, user_id: str) -> Cart | None:
    result = await db.execute(
        select(Cart)
        .options(selectinload(Cart.items).selectinload(CartItem.product))
        .where(and_(Cart.user_id == user_id, Cart.status == CartStatus.active))
        .order_by(Cart.created_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()
