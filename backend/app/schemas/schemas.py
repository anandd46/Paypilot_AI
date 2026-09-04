"""Pydantic schemas for PayPilot AI API."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, EmailStr, Field, field_validator


# ─────────────────────────── Common ───────────────────────────────────────────

class PaginatedResponse(BaseModel):
    items: list[Any]
    total: int
    page: int
    limit: int
    pages: int


class MessageResponse(BaseModel):
    message: str
    success: bool = True


# ─────────────────────────── Auth ─────────────────────────────────────────────

class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    role: str = Field(default="customer")

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        if v not in ("customer", "merchant"):
            return "customer"
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    role: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ─────────────────────────── Products ─────────────────────────────────────────

class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=500)
    description: str = Field(..., min_length=10)
    category: str = Field(..., min_length=1, max_length=100)
    sub_category: str | None = None
    price: float = Field(..., gt=0)
    original_price: float | None = Field(None, gt=0)
    stock: int = Field(..., ge=0)
    rating: float = Field(default=0.0, ge=0, le=5)
    review_count: int = Field(default=0, ge=0)
    brand: str | None = None
    tags: list[str] = []
    features: list[str] = []
    specifications: dict[str, Any] = {}
    cross_sell_ids: list[str] = []
    upsell_ids: list[str] = []
    image_url: str | None = None


class ProductUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    category: str | None = None
    price: float | None = Field(None, gt=0)
    original_price: float | None = Field(None, gt=0)
    stock: int | None = Field(None, ge=0)
    rating: float | None = Field(None, ge=0, le=5)
    brand: str | None = None
    tags: list[str] | None = None
    features: list[str] | None = None
    specifications: dict[str, Any] | None = None
    cross_sell_ids: list[str] | None = None
    upsell_ids: list[str] | None = None
    image_url: str | None = None
    is_active: bool | None = None


class ProductResponse(BaseModel):
    id: str
    name: str
    description: str
    category: str
    sub_category: str | None
    price: float
    original_price: float | None
    discount_percent: float | None = None
    stock: int
    rating: float
    review_count: int
    brand: str | None
    tags: list[str]
    features: list[str]
    specifications: dict[str, Any]
    cross_sell_ids: list[str]
    upsell_ids: list[str]
    image_url: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

    @property
    def computed_discount(self) -> float | None:
        if self.original_price and self.original_price > self.price:
            return round((1 - self.price / self.original_price) * 100, 1)
        return None


class ProductSearchRequest(BaseModel):
    query: str | None = None
    category: str | None = None
    brand: str | None = None
    min_price: float | None = Field(None, ge=0)
    max_price: float | None = Field(None, ge=0)
    min_rating: float | None = Field(None, ge=0, le=5)
    in_stock: bool | None = None
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=20, ge=1, le=100)
    sort_by: str = "relevance"  # relevance | price_asc | price_desc | rating | newest


# ─────────────────────────── Cart ─────────────────────────────────────────────

class AddToCartRequest(BaseModel):
    product_id: str
    quantity: int = Field(default=1, ge=1, le=100)


class UpdateCartItemRequest(BaseModel):
    quantity: int = Field(..., ge=1, le=100)


class CartItemResponse(BaseModel):
    id: str
    product_id: str
    product: ProductResponse
    quantity: int
    unit_price: float
    total_price: float

    model_config = {"from_attributes": True}


class CartResponse(BaseModel):
    id: str
    status: str
    items: list[CartItemResponse]
    subtotal: float
    discount: float
    total: float
    item_count: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ─────────────────────────── Checkout & Orders ────────────────────────────────

class CheckoutCreateRequest(BaseModel):
    idempotency_key: str | None = None


class CheckoutResponse(BaseModel):
    order_id: str
    razorpay_order_id: str | None
    amount: float
    currency: str
    payment_provider: str
    is_demo: bool
    idempotency_key: str | None = None


class PaymentCreateRequest(BaseModel):
    order_id: str


class PaymentVerifyRequest(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str
    order_id: str


class PaymentVerifyDemoRequest(BaseModel):
    order_id: str
    simulate_failure: bool = False


class PaymentResponse(BaseModel):
    id: str
    order_id: str
    razorpay_payment_id: str | None
    amount: float
    currency: str
    status: str
    failure_reason: str | None
    provider: str
    created_at: datetime

    model_config = {"from_attributes": True}


class OrderItemResponse(BaseModel):
    id: str
    product_id: str
    product_name: str
    quantity: int
    price: float

    model_config = {"from_attributes": True}


class OrderResponse(BaseModel):
    id: str
    status: str
    amount: float
    currency: str
    razorpay_order_id: str | None
    items: list[OrderItemResponse]
    payments: list[PaymentResponse]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ─────────────────────────── Recommendations ──────────────────────────────────

class RecommendationResponse(BaseModel):
    id: str
    product: ProductResponse
    recommendation_type: str
    reason: str
    confidence: float
    score: float
    score_breakdown: dict[str, float]
    prompt_version: str | None = None

    model_config = {"from_attributes": True}


# ─────────────────────────── Assistant / Chat ─────────────────────────────────

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    session_id: str | None = None
    context: dict[str, Any] = {}


class ChatResponse(BaseModel):
    session_id: str
    message: str
    intent: str | None
    confidence: str  # HIGH | MEDIUM | LOW
    products: list[ProductResponse] = []
    recommendations: list[RecommendationResponse] = []
    cart_updated: bool = False
    cart: CartResponse | None = None
    checkout_url: str | None = None
    action_taken: str | None = None
    suggested_prompts: list[str] = []
    is_demo: bool = False
    provider: str = "mock"


# ─────────────────────────── Analytics ───────────────────────────────────────

class AnalyticsOverview(BaseModel):
    total_revenue: float
    total_orders: int
    total_customers: int
    avg_order_value: float
    conversion_rate: float
    ai_assisted_orders: int
    ai_assisted_revenue: float
    upsell_revenue: float
    cross_sell_revenue: float
    payment_success_rate: float
    failed_payments: int
    is_demo: bool = True


class RevenuePoint(BaseModel):
    date: str
    revenue: float
    orders: int
    ai_revenue: float


class AgentActionResponse(BaseModel):
    id: str
    conversation_id: str
    action_type: str
    description: str | None
    intent: str | None
    provider: str | None
    prompt_version: str | None
    tool_calls: list[str]
    duration_ms: int | None
    confidence: str | None
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class AuditLogResponse(BaseModel):
    id: str
    user_id: str | None
    action: str
    entity_type: str | None
    entity_id: str | None
    details: dict[str, Any]
    timestamp: datetime

    model_config = {"from_attributes": True}


# ─────────────────────────── Health ───────────────────────────────────────────

class ComponentHealth(BaseModel):
    status: str  # operational | demo_mode | test_mode | unavailable
    provider: str | None = None
    message: str | None = None


class HealthResponse(BaseModel):
    status: str
    api: ComponentHealth
    database: ComponentHealth
    ai: ComponentHealth
    payment: ComponentHealth
    version: str = "1.0.0"
