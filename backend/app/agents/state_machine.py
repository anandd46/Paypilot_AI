"""PayPilot AI Commerce Agent — Explicit State Machine.

States:
    RECEIVE_REQUEST → CLASSIFY_INTENT → EXTRACT_ENTITIES → PLAN
    → SELECT_TOOL → EXECUTE_TOOL → VALIDATE_RESULT
    → [REQUIRE_CONFIRMATION if financial action]
    → EXECUTE_ACTION → GENERATE_RESPONSE → AUDIT → END
"""
from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.providers import get_ai_provider
from app.core.config import get_settings

settings = get_settings()


# ─────────────────────────── Agent States ─────────────────────────────────────

class AgentState(str, Enum):
    RECEIVE_REQUEST = "RECEIVE_REQUEST"
    CLASSIFY_INTENT = "CLASSIFY_INTENT"
    EXTRACT_ENTITIES = "EXTRACT_ENTITIES"
    PLAN = "PLAN"
    SELECT_TOOL = "SELECT_TOOL"
    EXECUTE_TOOL = "EXECUTE_TOOL"
    VALIDATE_RESULT = "VALIDATE_RESULT"
    REQUIRE_CONFIRMATION = "REQUIRE_CONFIRMATION"
    EXECUTE_ACTION = "EXECUTE_ACTION"
    GENERATE_RESPONSE = "GENERATE_RESPONSE"
    AUDIT = "AUDIT"
    END = "END"
    ERROR = "ERROR"


# ─────────────────────────── Financial Guard ──────────────────────────────────

FINANCIAL_ACTIONS = {"checkout", "create_payment", "apply_discount"}


# ─────────────────────────── Agent Context ────────────────────────────────────

@dataclass
class AgentContext:
    """Typed state object carrying data through the state machine."""

    # Input
    user_message: str
    user_id: str
    session_id: str
    conversation_id: str | None = None
    db: Any = field(default=None, repr=False)

    # Intent classification
    intent: str = ""
    confidence: str = "LOW"  # HIGH | MEDIUM | LOW
    entities: dict[str, Any] = field(default_factory=dict)
    prompt_version: str = ""

    # Planning
    plan: list[str] = field(default_factory=list)
    requires_confirmation: bool = False
    confirmation_message: str = ""

    # Tool execution
    current_tool: str = ""
    tool_calls: list[str] = field(default_factory=list)
    tool_results: dict[str, Any] = field(default_factory=dict)
    tool_durations: dict[str, int] = field(default_factory=dict)
    validation_errors: list[str] = field(default_factory=list)

    # Products / Recommendations
    products: list[dict[str, Any]] = field(default_factory=list)
    recommendations: list[dict[str, Any]] = field(default_factory=list)
    cart: dict[str, Any] | None = None
    cart_updated: bool = False

    # Response
    response_message: str = ""
    suggested_prompts: list[str] = field(default_factory=list)
    checkout_initiated: bool = False
    action_taken: str | None = None

    # Telemetry
    state: AgentState = AgentState.RECEIVE_REQUEST
    start_time: float = field(default_factory=time.time)
    total_duration_ms: int = 0
    error: str | None = None
    success: bool = True


# ─────────────────────────── State Machine ────────────────────────────────────

class CommerceAgentStateMachine:
    """Explicit state machine for the PayPilot AI Commerce Agent."""

    def __init__(self) -> None:
        self._ai = get_ai_provider()
        self._transitions: dict[AgentState, AgentState] = {
            AgentState.RECEIVE_REQUEST: AgentState.CLASSIFY_INTENT,
            AgentState.CLASSIFY_INTENT: AgentState.EXTRACT_ENTITIES,
            AgentState.EXTRACT_ENTITIES: AgentState.PLAN,
            AgentState.PLAN: AgentState.SELECT_TOOL,
            AgentState.SELECT_TOOL: AgentState.EXECUTE_TOOL,
            AgentState.EXECUTE_TOOL: AgentState.VALIDATE_RESULT,
            AgentState.VALIDATE_RESULT: AgentState.GENERATE_RESPONSE,
            AgentState.REQUIRE_CONFIRMATION: AgentState.GENERATE_RESPONSE,
            AgentState.EXECUTE_ACTION: AgentState.GENERATE_RESPONSE,
            AgentState.GENERATE_RESPONSE: AgentState.AUDIT,
            AgentState.AUDIT: AgentState.END,
        }

    async def run(self, ctx: AgentContext) -> AgentContext:
        """Run the full agent state machine."""
        try:
            ctx = await self._receive_request(ctx)
            ctx = await self._classify_intent(ctx)
            ctx = await self._extract_entities(ctx)
            ctx = await self._plan(ctx)
            ctx = await self._select_and_execute_tools(ctx)
            ctx = await self._validate_result(ctx)

            if ctx.requires_confirmation:
                ctx = await self._require_confirmation(ctx)
            else:
                ctx = await self._execute_action(ctx)

            ctx = await self._generate_response(ctx)
            ctx = await self._audit(ctx)

        except Exception as e:
            ctx.error = str(e)
            ctx.success = False
            ctx.state = AgentState.ERROR
            ctx.response_message = (
                "I encountered an issue processing your request. Please try again."
            )

        ctx.total_duration_ms = int((time.time() - ctx.start_time) * 1000)
        ctx.state = AgentState.END
        return ctx

    # ── State handlers ─────────────────────────────────────────────────────────

    async def _receive_request(self, ctx: AgentContext) -> AgentContext:
        ctx.state = AgentState.RECEIVE_REQUEST
        return ctx

    async def _classify_intent(self, ctx: AgentContext) -> AgentContext:
        ctx.state = AgentState.CLASSIFY_INTENT
        t0 = time.time()

        result = await self._ai.classify_intent(ctx.user_message)

        ctx.intent = result.get("intent", "product_search")
        ctx.confidence = result.get("confidence", "MEDIUM")
        ctx.entities = result.get("entities", {})
        ctx.prompt_version = result.get("prompt_version", "unknown")
        ctx.tool_durations["classify_intent"] = int((time.time() - t0) * 1000)

        return ctx

    async def _extract_entities(self, ctx: AgentContext) -> AgentContext:
        ctx.state = AgentState.EXTRACT_ENTITIES
        # Entities already extracted in classify_intent for efficiency
        # Validate / sanitize extracted values
        entities = ctx.entities

        # Validate budget values
        for key in ("budget_min", "budget_max"):
            val = entities.get(key)
            if val is not None:
                try:
                    entities[key] = max(0.0, float(val))
                except (TypeError, ValueError):
                    entities[key] = None

        # Validate quantity
        qty = entities.get("quantity")
        if qty is not None:
            try:
                entities["quantity"] = max(1, min(100, int(qty)))
            except (TypeError, ValueError):
                entities["quantity"] = 1

        ctx.entities = entities
        return ctx

    async def _plan(self, ctx: AgentContext) -> AgentContext:
        ctx.state = AgentState.PLAN

        intent_tool_map: dict[str, list[str]] = {
            "product_search": ["search_products", "get_recommendations"],
            "recommendation": ["search_products", "get_recommendations"],
            "product_details": ["get_product_details"],
            "product_comparison": ["search_products", "compare_products"],
            "category_search": ["search_products"],
            "price_filter": ["search_products"],
            "add_to_cart": ["search_products", "add_to_cart"],
            "remove_from_cart": ["get_cart", "remove_from_cart"],
            "update_cart": ["get_cart", "update_cart_quantity"],
            "view_cart": ["get_cart"],
            "checkout": ["get_cart", "create_checkout"],
            "order_status": ["get_order_status"],
            "order_history": ["get_order_history"],
            "upsell_request": ["search_products", "get_upsell"],
            "cross_sell_request": ["get_cart", "get_cross_sell"],
            "general_question": [],
            "unclear": [],
        }

        ctx.plan = intent_tool_map.get(ctx.intent, ["search_products"])

        # Financial actions need confirmation
        if ctx.intent in ("checkout",):
            ctx.requires_confirmation = True

        return ctx

    async def _select_and_execute_tools(self, ctx: AgentContext) -> AgentContext:
        ctx.state = AgentState.SELECT_TOOL

        from app.agents.tools import AgentTools

        tools = AgentTools(db=ctx.db, user_id=ctx.user_id)

        for tool_name in ctx.plan:
            if tool_name in FINANCIAL_ACTIONS and ctx.requires_confirmation:
                # Don't execute financial tools without confirmation
                continue

            ctx.state = AgentState.EXECUTE_TOOL
            ctx.current_tool = tool_name
            ctx.tool_calls.append(tool_name)
            t0 = time.time()

            try:
                result = await tools.execute(tool_name, ctx)
                ctx.tool_results[tool_name] = result
            except Exception as e:
                ctx.tool_results[tool_name] = {"error": str(e)}

            ctx.tool_durations[tool_name] = int((time.time() - t0) * 1000)

        return ctx

    async def _validate_result(self, ctx: AgentContext) -> AgentContext:
        ctx.state = AgentState.VALIDATE_RESULT

        # Validate products returned are real (not hallucinated)
        products = ctx.tool_results.get("search_products", {}).get("products", [])
        ctx.products = [p for p in products if p.get("id") and p.get("price", 0) > 0]

        # Validate cart
        cart_result = ctx.tool_results.get("get_cart", {})
        if cart_result and not cart_result.get("error"):
            ctx.cart = cart_result

        # Validate recommendations
        recs = ctx.tool_results.get("get_recommendations", {}).get("recommendations", [])
        ctx.recommendations = [r for r in recs if r.get("product", {}).get("id")]

        return ctx

    async def _require_confirmation(self, ctx: AgentContext) -> AgentContext:
        ctx.state = AgentState.REQUIRE_CONFIRMATION

        if ctx.intent == "checkout":
            cart = ctx.cart or {}
            total = cart.get("total", 0)
            count = len(cart.get("items", []))
            ctx.confirmation_message = (
                f"Your cart has {count} item(s) totaling ₹{total:,.0f}. "
                f"Confirm to proceed to payment."
            )
        return ctx

    async def _execute_action(self, ctx: AgentContext) -> AgentContext:
        ctx.state = AgentState.EXECUTE_ACTION
        # Non-financial actions already executed in tool execution phase
        ctx.action_taken = ctx.intent if ctx.tool_calls else None
        return ctx

    async def _generate_response(self, ctx: AgentContext) -> AgentContext:
        ctx.state = AgentState.GENERATE_RESPONSE

        if ctx.confidence == "LOW" and ctx.entities.get("clarification_needed"):
            ctx.response_message = ctx.entities["clarification_needed"]
            ctx.suggested_prompts = _get_suggested_prompts(ctx.intent)
            return ctx

        if ctx.requires_confirmation:
            ctx.response_message = ctx.confirmation_message
            ctx.suggested_prompts = ["Yes, proceed to payment", "Show my cart", "Cancel"]
            return ctx

        # Generate natural language response
        ctx.response_message = await self._ai.generate_response(
            context={
                "user_message": ctx.user_message,
                "intent": ctx.intent,
                "entities": ctx.entities,
                "cart": ctx.cart,
            },
            intent=ctx.intent,
            products=ctx.products[:5],
        )

        ctx.suggested_prompts = _get_suggested_prompts(ctx.intent)
        return ctx

    async def _audit(self, ctx: AgentContext) -> AgentContext:
        ctx.state = AgentState.AUDIT
        # Audit logging is handled by the API layer (has DB access via dependency injection)
        return ctx


# ─────────────────────────── Helpers ──────────────────────────────────────────

def _get_suggested_prompts(intent: str) -> list[str]:
    prompts: dict[str, list[str]] = {
        "product_search": [
            "Add to cart",
            "Compare these products",
            "Show accessories",
        ],
        "recommendation": [
            "Add recommended item to cart",
            "Show more options",
            "Compare products",
        ],
        "view_cart": ["Proceed to checkout", "Remove an item", "Continue shopping"],
        "checkout": ["Confirm checkout", "Back to cart", "Apply coupon"],
        "add_to_cart": ["Go to checkout", "Show cart", "Find accessories"],
        "order_status": ["Show all orders", "Return to shop"],
        "general_question": [
            "Find gaming headphones under ₹5,000",
            "Recommend a laptop for programming",
            "What's in my cart?",
        ],
        "unclear": [
            "Find gaming headphones under ₹5,000",
            "Recommend a laptop for programming",
            "Show popular products",
        ],
    }
    return prompts.get(intent, [
        "Search products",
        "View my cart",
        "Help me checkout",
    ])
