"""Cross-sell prompt — version: cross_sell_v1."""
from __future__ import annotations

PROMPT_VERSION = "cross_sell_v1"

CROSS_SELL_PROMPT = """Generate a cross-sell recommendation message.

Customer's cart item: {cart_product} (₹{cart_price})
Complementary product: {cross_sell_product} (₹{cross_sell_price})
Relationship: {relationship}

Write ONE short sentence explaining why this product complements what the customer has.
Be specific about the benefit, not generic ("customers also buy").

Output JSON only:
{"suggestion": "..."}
"""
