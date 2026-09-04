"""Recommendation engine — scoring, guardrails, upsell, cross-sell."""
from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Product, RecommendationType


# ─────────────────────────── Scoring weights ──────────────────────────────────

WEIGHTS = {
    "intent_match": 0.30,
    "semantic_similarity": 0.25,
    "budget_fit": 0.20,
    "rating_score": 0.15,
    "popularity_score": 0.10,
}

# ─────────────────────────── Category affinities ─────────────────────────────

CROSS_SELL_AFFINITIES: dict[str, list[str]] = {
    "Laptops": ["Laptop Accessories", "Mice", "Keyboards", "Monitors", "Bags"],
    "Smartphones": ["Phone Cases", "Earphones", "Headphones", "Chargers", "Smartwatches"],
    "Headphones": ["Smartphones", "Gaming", "Laptop Accessories"],
    "Gaming": ["Headphones", "Keyboards", "Mice", "Monitors"],
    "Cameras": ["Camera Accessories", "Memory Cards", "Tripods", "Bags"],
    "Tablets": ["Keyboards", "Bags", "Stylus"],
    "Smartwatches": ["Smartphones", "Fitness Accessories"],
}


class RecommendationService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_recommendations(
        self,
        user_id: str,
        intent: str,
        entities: dict[str, Any],
        products: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Score and filter recommendations with guardrails."""
        if not products:
            return []

        # Only recommend active, in-stock products with verified prices
        valid_products = [
            p for p in products
            if p.get("id")
            and p.get("is_active", True)
            and p.get("stock", 0) > 0
            and p.get("price", 0) > 0
        ]

        scored = []
        for product in valid_products[:10]:
            score, breakdown = self._score(product, entities)
            reason = self._explain(product, entities, breakdown)
            scored.append({
                "product": product,
                "recommendation_type": RecommendationType.semantic.value,
                "reason": reason,
                "confidence": score,
                "score": score,
                "score_breakdown": breakdown,
                "prompt_version": "recommendation_v1",
            })

        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:5]

    def _score(
        self, product: dict[str, Any], entities: dict[str, Any]
    ) -> tuple[float, dict[str, float]]:
        breakdown: dict[str, float] = {}

        # Intent match — does the product category match what was searched?
        category = entities.get("category", "")
        prod_category = product.get("category", "")
        if category and prod_category:
            intent_match = 1.0 if category.lower() in prod_category.lower() else 0.3
        elif not category:
            intent_match = 0.7  # neutral if no category filter
        else:
            intent_match = 0.2
        breakdown["intent_match"] = round(intent_match, 3)

        # Budget fit
        budget_max = entities.get("budget_max")
        price = float(product.get("price", 0))
        if budget_max:
            if price <= budget_max:
                # Reward products near (but under) the budget
                budget_fit = min(1.0, price / budget_max * 1.2)
            else:
                budget_fit = 0.0  # Over budget — excluded
        else:
            budget_fit = 1.0
        breakdown["budget_fit"] = round(budget_fit, 3)

        # Rating score (normalized 0–5 → 0–1)
        rating = float(product.get("rating", 0))
        rating_score = rating / 5.0
        breakdown["rating_score"] = round(rating_score, 3)

        # Popularity score (normalized by review count — cap at 1000 reviews)
        review_count = int(product.get("review_count", 0))
        popularity_score = min(1.0, review_count / 1000)
        breakdown["popularity_score"] = round(popularity_score, 3)

        # Semantic similarity — placeholder (TF-IDF handled in tools.py)
        breakdown["semantic_similarity"] = 0.7  # default for pre-ranked products

        # Weighted sum
        total = sum(WEIGHTS[k] * breakdown[k] for k in WEIGHTS)
        return round(total, 4), breakdown

    def _explain(
        self,
        product: dict[str, Any],
        entities: dict[str, Any],
        breakdown: dict[str, float],
    ) -> str:
        reasons = []

        if breakdown.get("budget_fit", 0) == 1.0 and entities.get("budget_max"):
            reasons.append(f"Within your budget of ₹{entities['budget_max']:,.0f}")

        if breakdown.get("intent_match", 0) >= 0.8:
            category = entities.get("category", "")
            use_case = entities.get("use_case", "")
            if use_case:
                reasons.append(f"Matches your {use_case} use case")
            elif category:
                reasons.append(f"Matches your {category} requirement")

        if breakdown.get("rating_score", 0) >= 0.8:
            rating = product.get("rating", 0)
            count = product.get("review_count", 0)
            reasons.append(f"Highly rated: {rating}★ from {count:,} reviews")

        if breakdown.get("popularity_score", 0) >= 0.5:
            reasons.append("Popular choice in this category")

        return " • ".join(reasons) if reasons else "Good match for your requirements"

    async def get_upsell(
        self,
        product: dict[str, Any],
        budget_max: float | None,
    ) -> list[dict[str, Any]]:
        """Find a better version of the product within 125% of the original price."""
        price = float(product.get("price", 0))
        category = product.get("category", "")

        # Upsell ceiling: max 25% over current price, or within budget if specified
        upsell_max = budget_max if budget_max and budget_max > price else price * 1.25

        query = (
            select(Product)
            .where(
                Product.is_active == True,  # noqa: E712
                Product.stock > 0,
                Product.category == category,
                Product.price > price,
                Product.price <= upsell_max,
                Product.id != product.get("id"),
                Product.rating >= (float(product.get("rating", 0)) - 0.5),
            )
            .order_by(Product.rating.desc())
            .limit(2)
        )
        result = await self._db.execute(query)
        upsells = result.scalars().all()

        return [
            {
                "product": _product_to_dict(p),
                "recommendation_type": RecommendationType.upsell.value,
                "reason": (
                    f"Premium option with better specs — "
                    f"₹{float(p.price) - price:,.0f} more than your selection"
                ),
                "confidence": 0.75,
                "score": 0.75,
                "score_breakdown": {"upsell_value": 0.75},
            }
            for p in upsells
        ]

    async def get_cross_sell(self, cart_items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Find complementary products for cart items."""
        if not cart_items:
            return []

        cross_sells: list[dict[str, Any]] = []
        seen_ids: set[str] = {item.get("product_id", "") for item in cart_items}

        for item in cart_items[:2]:  # Look at top 2 cart items
            product_id = item.get("product_id", "")
            if not product_id:
                continue

            # Get the product's cross_sell_ids first
            result = await self._db.execute(
                select(Product).where(Product.id == product_id)
            )
            product = result.scalar_one_or_none()
            if not product:
                continue

            # Check explicit cross-sell relationships
            if product.cross_sell_ids:
                for cs_id in product.cross_sell_ids[:3]:
                    if cs_id in seen_ids:
                        continue
                    cs_result = await self._db.execute(
                        select(Product).where(
                            Product.id == cs_id,
                            Product.is_active == True,  # noqa: E712
                            Product.stock > 0,
                        )
                    )
                    cs_product = cs_result.scalar_one_or_none()
                    if cs_product:
                        seen_ids.add(cs_id)
                        cross_sells.append({
                            "product": _product_to_dict(cs_product),
                            "recommendation_type": RecommendationType.cross_sell.value,
                            "reason": f"Pairs well with your {product.name}",
                            "confidence": 0.80,
                            "score": 0.80,
                            "score_breakdown": {"cross_sell_affinity": 0.80},
                        })

            # Category affinity fallback
            if len(cross_sells) < 3:
                affinity_cats = CROSS_SELL_AFFINITIES.get(product.category, [])
                for aff_cat in affinity_cats[:2]:
                    aff_result = await self._db.execute(
                        select(Product)
                        .where(
                            Product.category.ilike(f"%{aff_cat}%"),
                            Product.is_active == True,  # noqa: E712
                            Product.stock > 0,
                            Product.id.notin_(seen_ids),
                        )
                        .order_by(Product.rating.desc())
                        .limit(1)
                    )
                    aff_product = aff_result.scalar_one_or_none()
                    if aff_product:
                        seen_ids.add(aff_product.id)
                        cross_sells.append({
                            "product": _product_to_dict(aff_product),
                            "recommendation_type": RecommendationType.cross_sell.value,
                            "reason": f"Complements your {product.name} — frequently bought together",
                            "confidence": 0.65,
                            "score": 0.65,
                            "score_breakdown": {"category_affinity": 0.65},
                        })

        return cross_sells[:4]


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
