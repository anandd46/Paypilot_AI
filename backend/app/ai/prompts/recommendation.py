"""Recommendation prompt — version: recommendation_v1."""
from __future__ import annotations

PROMPT_VERSION = "recommendation_v1"

RECOMMENDATION_EXPLANATION_PROMPT = """Generate a concise, user-facing explanation for why this product is recommended.

## INPUT
- User intent/query: {user_query}
- Product: {product_name} — ₹{price}
- Score breakdown: {score_breakdown}
- Recommendation type: {recommendation_type}

## RULES
- Keep explanation to 2-3 bullet points maximum
- Only mention verified scores (do NOT invent reasons)
- Be specific and factual
- Do NOT say "I think" or "probably"
- Format as a JSON list of reason strings

## SCORE BREAKDOWN MEANINGS
- intent_match > 0.7: "Matches your {use_case} requirements"
- semantic_similarity > 0.7: "Closely matches what you described"
- budget_fit = 1.0: "Within your budget"
- rating_score > 0.8: "Highly rated by customers ({rating}★)"
- popularity_score > 0.7: "Popular choice in this category"

Output JSON only:
{"reasons": ["reason 1", "reason 2", "reason 3"]}
"""
