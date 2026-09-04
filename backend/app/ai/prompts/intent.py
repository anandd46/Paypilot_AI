"""Intent classification prompt — version: intent_v1."""
from __future__ import annotations

PROMPT_VERSION = "intent_v1"

INTENT_CLASSIFICATION_PROMPT = """Classify the customer's message into one of these intents and extract entities.

## VALID INTENTS
- product_search: Looking for products (with category, budget, use case)
- product_details: Asking about a specific product
- product_comparison: Comparing two or more products
- recommendation: Asking for recommendations
- price_filter: Filtering by price only
- category_search: Browsing a category
- add_to_cart: Want to add something to cart
- remove_from_cart: Want to remove from cart
- update_cart: Change quantity in cart
- view_cart: Show cart contents
- checkout: Ready to buy / checkout
- payment_status: Asking about payment
- order_status: Asking about an existing order
- order_history: Viewing past orders
- upsell_request: Want a premium/better version
- cross_sell_request: Want accessories/related products
- general_question: General help question
- unclear: Cannot determine intent (LOW confidence)

## OUTPUT FORMAT (JSON only, no explanation)
{
  "intent": "<intent>",
  "confidence": "HIGH" | "MEDIUM" | "LOW",
  "entities": {
    "category": "<string or null>",
    "budget_max": <number or null>,
    "budget_min": <number or null>,
    "brand": "<string or null>",
    "use_case": "<string or null>",
    "product_name": "<string or null>",
    "quantity": <number or null>,
    "clarification_needed": "<what to ask if LOW/MEDIUM confidence, or null>"
  }
}

## EXAMPLES

Input: "I need wireless headphones under ₹5000 for gaming"
Output: {"intent": "product_search", "confidence": "HIGH", "entities": {"category": "headphones", "budget_max": 5000, "budget_min": null, "brand": null, "use_case": "gaming", "product_name": null, "quantity": null, "clarification_needed": null}}

Input: "give me something good"
Output: {"intent": "unclear", "confidence": "LOW", "entities": {"category": null, "budget_max": null, "budget_min": null, "brand": null, "use_case": null, "product_name": null, "quantity": null, "clarification_needed": "What type of product are you looking for, and what's your approximate budget?"}}

Input: "add the Sony headphones to my cart"
Output: {"intent": "add_to_cart", "confidence": "HIGH", "entities": {"category": null, "budget_max": null, "budget_min": null, "brand": "Sony", "use_case": null, "product_name": "Sony headphones", "quantity": 1, "clarification_needed": null}}

Now classify this message:
"""
