"""Upsell prompt — version: upsell_v1."""
from __future__ import annotations

PROMPT_VERSION = "upsell_v1"

UPSELL_PROMPT = """Generate a concise upsell suggestion message.

The customer selected: {selected_product} (₹{selected_price})
Upsell candidate: {upsell_product} (₹{upsell_price})
Price difference: ₹{price_diff}
Key additional benefits: {benefits}

Write ONE short sentence explaining why the premium version is worth the extra cost.
Be helpful, not pushy. If the difference isn't compelling, say so honestly.

Output JSON only:
{"suggestion": "...", "is_compelling": true|false}
"""
