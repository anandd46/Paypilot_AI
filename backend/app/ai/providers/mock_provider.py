"""Mock/Demo AI provider — deterministic, no external calls."""
from __future__ import annotations

import re
from typing import Any

from app.ai.providers.base import AIMessage, AIResponse, BaseAIProvider


# ── Intent keyword maps ────────────────────────────────────────────────────────

_INTENT_KEYWORDS: list[tuple[str, str]] = [
    # (pattern, intent) — ordered from most-specific to most-general
    (r"\b(checkout|pay now|buy now|place order|complete order)\b", "checkout"),
    (r"\b(add|put)\b.*(cart|bag)", "add_to_cart"),
    (r"\b(remove|delete|take out)\b.*(cart|bag)", "remove_from_cart"),
    (r"\b(update|change|modify)\b.*(cart|quantity)\b", "update_cart"),
    (r"\b(what.s in my cart|show.*(my )?cart|view.*cart|my cart|cart|basket|bag)\b", "view_cart"),
    (r"\b(order status|track|where is my order)\b", "order_status"),
    (r"\b(history|past orders|my orders)\b", "order_history"),
    (r"\b(compare|vs|versus|difference between)\b", "product_comparison"),
    (r"\b(upsell|better version|premium upgrade|higher end)\b", "upsell_request"),
    (r"\b(accessory|accessories|compatible|goes with|pair with)\b", "cross_sell_request"),
    (r"\b(recommend|suggest|what should|best for me|top pick)\b", "recommendation"),
    (r"\b(find|search|show|looking for|need|want|give me|list)\b", "product_search"),
    (r"\b(laptop|computer|pc|headphone|earphone|earbuds|speaker|phone|smartphone|mobile|camera|tablet|watch|gaming|smartwatch)\b", "product_search"),
]

# ── Category priority-based extraction ────────────────────────────────────────
# Each entry: (keyword, category, priority)
# Higher priority = wins when multiple keywords match in the same message.
# Product-type words (headphone, laptop) have priority 10.
# Use-case/modifier words (gaming) have priority 5.
# This ensures "gaming headphones" → Headphones, NOT Gaming.
_CATEGORY_KEYWORDS: list[tuple[str, str, int]] = [
    # Product types — high priority (what the product IS)
    ("headphone", "Headphones", 10),
    ("earphone", "Headphones", 10),
    ("earbuds", "Headphones", 10),
    ("laptop", "Laptops", 10),
    ("notebook", "Laptops", 10),
    ("computer", "Laptops", 9),
    ("smartphone", "Smartphones", 10),
    ("iphone", "Smartphones", 10),
    ("phone", "Smartphones", 9),
    ("mobile", "Smartphones", 8),
    ("camera", "Cameras", 10),
    ("dslr", "Cameras", 10),
    ("mirrorless", "Cameras", 10),
    ("photography", "Cameras", 8),
    ("tablet", "Tablets", 10),
    ("ipad", "Tablets", 10),
    ("smartwatch", "Smartwatches", 10),
    ("watch", "Smartwatches", 9),
    ("wearable", "Smartwatches", 8),
    ("speaker", "Speakers", 10),
    ("soundbar", "Speakers", 10),
    ("mouse", "Laptop Accessories", 10),
    ("keyboard", "Laptop Accessories", 10),
    ("charger", "Laptop Accessories", 9),
    # Use-case / modifiers — lower priority (HOW the product is used)
    ("gaming", "Gaming", 5),
    ("gamer", "Gaming", 5),
]

_USE_CASE_KEYWORDS: dict[str, str] = {
    "gaming": "gaming",
    "programming": "programming",
    "coding": "programming",
    "music": "music",
    "photography": "photography",
    "travel": "travel",
    "office": "office",
    "work": "office",
    "study": "education",
    "student": "education",
    "video": "video",
    "beginner": "beginner",
    "professional": "professional",
}


def _kw_match(keyword: str, text: str) -> bool:
    """Word-boundary-aware keyword match.

    Uses \\b before the keyword so 'phone' won't match inside 'headphone'
    or 'smartphone', while still correctly matching standalone 'phone'.
    """
    return bool(re.search(rf"\b{re.escape(keyword)}", text, re.I))


def _extract_budget(text: str) -> tuple[float | None, float | None]:
    """Extract budget constraints from natural language text."""
    text = text.replace(",", "")
    # "under ₹5000" / "below ₹5000" / "less than 5000" / "upto 70000"
    under_match = re.search(
        r"(?:under|below|less than|max|maximum|upto|up to)\s*[₹rs\.]?\s*(\d+(?:\.\d+)?)\s*k?",
        text, re.I
    )
    if under_match:
        val = float(under_match.group(1))
        suffix = text[under_match.start(): under_match.end() + 2].lower()
        if "k" in suffix:
            val *= 1000
        return None, val

    # "above ₹5000" / "more than ₹5000"
    above_match = re.search(
        r"(?:above|over|more than|minimum|atleast|at least)\s*[₹rs\.]?\s*(\d+(?:\.\d+)?)\s*k?",
        text, re.I
    )
    if above_match:
        val = float(above_match.group(1))
        return val, None

    # "₹5000 to ₹10000"
    range_match = re.search(
        r"[₹rs\.]?\s*(\d+(?:\.\d+)?)\s*k?\s*(?:to|-)\s*[₹rs\.]?\s*(\d+(?:\.\d+)?)\s*k?",
        text, re.I
    )
    if range_match:
        lo, hi = float(range_match.group(1)), float(range_match.group(2))
        return lo, hi

    return None, None


class MockAIProvider(BaseAIProvider):
    """Deterministic mock AI provider for demo mode — no external API calls."""

    @property
    def provider_name(self) -> str:
        return "mock"

    @property
    def model_name(self) -> str:
        return "mock-demo"

    async def complete(
        self,
        messages: list[AIMessage],
        temperature: float = 0.3,
        max_tokens: int = 1000,
        response_format: str | None = None,
    ) -> AIResponse:
        last_user = next(
            (m.content for m in reversed(messages) if m.role == "user"), ""
        )
        return AIResponse(
            content=f"Demo response for: {last_user[:100]}",
            model=self.model_name,
            provider=self.provider_name,
        )

    async def classify_intent(self, user_message: str) -> dict[str, Any]:
        """Classify user intent and extract entities from the message."""
        msg = user_message.lower()

        # Match intent — first match wins (ordered most-specific → most-general)
        intent = "product_search"  # default
        for pattern, matched_intent in _INTENT_KEYWORDS:
            if re.search(pattern, msg, re.I):
                intent = matched_intent
                break

        # Priority-based category extraction.
        # Scans ALL keywords and picks the highest-priority match.
        # "gaming headphones" → headphone (priority 10) beats gaming (priority 5)
        # → category = "Headphones", use_case = "gaming"
        # Uses _kw_match() for word-boundary safety: 'phone' won't match 'headphone'.
        best_category: str | None = None
        best_priority: int = -1
        for kw, cat, priority in _CATEGORY_KEYWORDS:
            if _kw_match(kw, msg) and priority > best_priority:
                best_category = cat
                best_priority = priority

        category = best_category

        # Use-case extraction (independent from category)
        use_case = None
        for kw, uc in _USE_CASE_KEYWORDS.items():
            if _kw_match(kw, msg):
                use_case = uc
                break

        budget_min, budget_max = _extract_budget(msg)

        # Brand extraction
        brand = None
        known_brands = [
            "sony", "apple", "lg", "bose", "jbl", "boat", "realme",
            "oneplus", "xiaomi", "asus", "dell", "hp", "lenovo", "acer",
            "canon", "nikon", "fujifilm", "logitech", "razer", "corsair",
            "samsung",  # keep last so it doesn't override product types
        ]
        for b in known_brands:
            if _kw_match(b, msg):
                brand = b.title()
                break

        # Confidence scoring
        confidence = "HIGH"
        if not category and intent in ("product_search", "recommendation"):
            confidence = "MEDIUM"
        if intent == "unclear":
            confidence = "LOW"

        clarification = None
        if confidence == "LOW":
            clarification = "What type of product are you looking for, and what's your approximate budget?"
        elif confidence == "MEDIUM" and not category:
            clarification = "Could you tell me what type of product you're looking for?"

        return {
            "intent": intent,
            "confidence": confidence,
            "entities": {
                "category": category,
                "budget_max": budget_max,
                "budget_min": budget_min,
                "brand": brand,
                "use_case": use_case,
                "product_name": None,
                "quantity": None,
                "clarification_needed": clarification,
            },
            "prompt_version": "intent_v2_mock",
        }

    async def generate_response(
        self,
        context: dict[str, Any],
        intent: str,
        products: list[dict[str, Any]],
    ) -> str:
        """Generate a deterministic, data-grounded response."""
        entities = context.get("entities", {})
        budget_max = entities.get("budget_max")
        category = entities.get("category", "products")
        use_case = entities.get("use_case", "")

        if intent == "view_cart":
            cart = context.get("cart")
            if not cart or not cart.get("items"):
                return "Your cart is currently empty. What would you like to shop for today?"
            total = cart.get("total", 0)
            count = len(cart.get("items", []))
            return (
                f"Your cart has {count} item(s) totaling ₹{total:,.0f}. "
                "Would you like to proceed to checkout?"
            )

        if intent == "checkout":
            cart = context.get("cart")
            if not cart or not cart.get("items"):
                return "Your cart is empty. Please add some products before checking out."
            total = cart.get("total", 0)
            return (
                f"I've prepared your checkout. Your cart total is ₹{total:,.0f}. "
                "Please confirm to proceed with payment."
            )

        if intent == "add_to_cart":
            if products:
                return (
                    f"I've added **{products[0]['name']}** to your cart! "
                    "Would you like to continue shopping or proceed to checkout?"
                )
            return "I've added that to your cart! Would you like to continue shopping or proceed to checkout?"

        if intent == "product_comparison":
            if len(products) >= 2:
                p1, p2 = products[0], products[1]
                return (
                    f"Here's a comparison:\n\n"
                    f"**{p1['name']}** — ₹{p1['price']:,.0f} | {p1['rating']}★ "
                    f"| {p1.get('brand', '')}\n"
                    f"**{p2['name']}** — ₹{p2['price']:,.0f} | {p2['rating']}★ "
                    f"| {p2.get('brand', '')}\n\n"
                    "Both are excellent options. Would you like me to help you choose based on your specific needs?"
                )
            return "I found a product for comparison. Would you like to see more options?"

        if not products:
            budget_str = f" under ₹{budget_max:,.0f}" if budget_max else ""
            cat_str = category or "products"
            return (
                f"I searched for {cat_str}{budget_str} but couldn't find exact matches. "
                "Try adjusting your filters or let me know more details about what you need."
            )

        count = len(products)
        budget_str = f" under ₹{budget_max:,.0f}" if budget_max else ""
        use_str = f" for {use_case}" if use_case else ""
        top = products[0]

        return (
            f"I found {count} {category or 'product'}(s){budget_str}{use_str}. "
            f"My top recommendation is the **{top['name']}** at ₹{top['price']:,.0f} "
            f"({top['rating']}★ from {top.get('review_count', 0):,} reviews). "
            "Here are the best options for you:"
        )
