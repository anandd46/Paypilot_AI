"""SQLAlchemy ORM models for PayPilot AI."""
from __future__ import annotations

import enum
import uuid
from datetime import UTC, datetime

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


# ─────────────────────────────── Enums ────────────────────────────────────────

class UserRole(str, enum.Enum):
    customer = "customer"
    merchant = "merchant"
    admin = "admin"


class OrderStatus(str, enum.Enum):
    draft = "draft"
    pending_payment = "pending_payment"
    payment_authorized = "payment_authorized"
    paid = "paid"
    processing = "processing"
    completed = "completed"
    cancelled = "cancelled"
    payment_failed = "payment_failed"


class PaymentStatus(str, enum.Enum):
    created = "created"
    authorized = "authorized"
    captured = "captured"
    failed = "failed"
    cancelled = "cancelled"
    refunded = "refunded"


class CartStatus(str, enum.Enum):
    active = "active"
    checked_out = "checked_out"
    abandoned = "abandoned"


class ReservationStatus(str, enum.Enum):
    reserved = "reserved"
    confirmed = "confirmed"
    released = "released"
    expired = "expired"


class RecommendationType(str, enum.Enum):
    personalized = "personalized"
    upsell = "upsell"
    cross_sell = "cross_sell"
    semantic = "semantic"
    popular = "popular"


class WebhookStatus(str, enum.Enum):
    received = "received"
    processed = "processed"
    failed = "failed"
    duplicate = "duplicate"


class AgentConfidence(str, enum.Enum):
    high = "HIGH"
    medium = "MEDIUM"
    low = "LOW"


# ─────────────────────────────── Helpers ──────────────────────────────────────

def _uuid() -> str:
    return str(uuid.uuid4())


def _now() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


# ─────────────────────────────── Models ───────────────────────────────────────

class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        Index("ix_users_email", "email", unique=True),
        Index("ix_users_role", "role"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.customer)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=_now, onupdate=_now)

    carts: Mapped[list[Cart]] = relationship("Cart", back_populates="user")
    orders: Mapped[list[Order]] = relationship("Order", back_populates="user")
    conversations: Mapped[list[Conversation]] = relationship("Conversation", back_populates="user")
    recommendations: Mapped[list[Recommendation]] = relationship("Recommendation", back_populates="user")
    audit_logs: Mapped[list[AuditLog]] = relationship("AuditLog", back_populates="user")


class Product(Base):
    __tablename__ = "products"
    __table_args__ = (
        Index("ix_products_category", "category"),
        Index("ix_products_price", "price"),
        Index("ix_products_is_active", "is_active"),
        Index("ix_products_brand", "brand"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    sub_category: Mapped[str] = mapped_column(String(100), nullable=True)
    price: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    original_price: Mapped[float] = mapped_column(Numeric(12, 2), nullable=True)
    stock: Mapped[int] = mapped_column(Integer, default=0)
    rating: Mapped[float] = mapped_column(Float, default=0.0)
    review_count: Mapped[int] = mapped_column(Integer, default=0)
    brand: Mapped[str] = mapped_column(String(100), nullable=True)
    # JSON fields: tags, features, specifications, cross_sell_ids, upsell_ids
    tags: Mapped[list] = mapped_column(JSON, default=list)
    features: Mapped[list] = mapped_column(JSON, default=list)
    specifications: Mapped[dict] = mapped_column(JSON, default=dict)
    cross_sell_ids: Mapped[list] = mapped_column(JSON, default=list)
    upsell_ids: Mapped[list] = mapped_column(JSON, default=list)
    image_url: Mapped[str] = mapped_column(String(1000), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    # Cached embedding vector (JSON list of floats)
    embedding: Mapped[list] = mapped_column(JSON, nullable=True)
    embedding_provider: Mapped[str] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=_now, onupdate=_now)

    cart_items: Mapped[list[CartItem]] = relationship("CartItem", back_populates="product")
    order_items: Mapped[list[OrderItem]] = relationship("OrderItem", back_populates="product")
    recommendations: Mapped[list[Recommendation]] = relationship("Recommendation", back_populates="product")
    reservations: Mapped[list[InventoryReservation]] = relationship("InventoryReservation", back_populates="product")


class InventoryReservation(Base):
    __tablename__ = "inventory_reservations"
    __table_args__ = (
        Index("ix_inv_res_product_id", "product_id"),
        Index("ix_inv_res_status", "status"),
        Index("ix_inv_res_expires_at", "expires_at"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    product_id: Mapped[str] = mapped_column(String(36), ForeignKey("products.id"), nullable=False)
    order_id: Mapped[str] = mapped_column(String(36), ForeignKey("orders.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    status: Mapped[ReservationStatus] = mapped_column(
        Enum(ReservationStatus), default=ReservationStatus.reserved
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=_now, onupdate=_now)

    product: Mapped[Product] = relationship("Product", back_populates="reservations")
    order: Mapped[Order] = relationship("Order", back_populates="reservations")


class Cart(Base):
    __tablename__ = "carts"
    __table_args__ = (
        Index("ix_carts_user_id", "user_id"),
        Index("ix_carts_status", "status"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    status: Mapped[CartStatus] = mapped_column(Enum(CartStatus), default=CartStatus.active)
    subtotal: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    discount: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    total: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=_now, onupdate=_now)

    user: Mapped[User] = relationship("User", back_populates="carts")
    items: Mapped[list[CartItem]] = relationship(
        "CartItem", back_populates="cart", cascade="all, delete-orphan"
    )


class CartItem(Base):
    __tablename__ = "cart_items"
    __table_args__ = (
        Index("ix_cart_items_cart_id", "cart_id"),
        UniqueConstraint("cart_id", "product_id", name="uq_cart_items_cart_product"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    cart_id: Mapped[str] = mapped_column(String(36), ForeignKey("carts.id"), nullable=False)
    product_id: Mapped[str] = mapped_column(String(36), ForeignKey("products.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    unit_price: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    total_price: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=_now, onupdate=_now)

    cart: Mapped[Cart] = relationship("Cart", back_populates="items")
    product: Mapped[Product] = relationship("Product", back_populates="cart_items")


class Order(Base):
    __tablename__ = "orders"
    __table_args__ = (
        Index("ix_orders_user_id", "user_id"),
        Index("ix_orders_status", "status"),
        UniqueConstraint("razorpay_order_id", name="uq_orders_razorpay_order_id"),
        UniqueConstraint("idempotency_key", name="uq_orders_idempotency_key"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    status: Mapped[OrderStatus] = mapped_column(Enum(OrderStatus), default=OrderStatus.draft)
    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="INR")
    razorpay_order_id: Mapped[str] = mapped_column(String(100), nullable=True, unique=True)
    idempotency_key: Mapped[str] = mapped_column(String(100), nullable=True, unique=True)
    notes: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=_now, onupdate=_now)

    user: Mapped[User] = relationship("User", back_populates="orders")
    items: Mapped[list[OrderItem]] = relationship(
        "OrderItem", back_populates="order", cascade="all, delete-orphan"
    )
    payments: Mapped[list[Payment]] = relationship("Payment", back_populates="order")
    reservations: Mapped[list[InventoryReservation]] = relationship(
        "InventoryReservation", back_populates="order"
    )

    # ── Valid state transitions ──────────────
    _VALID_TRANSITIONS: dict[OrderStatus, set[OrderStatus]] = {
        OrderStatus.draft: {OrderStatus.pending_payment, OrderStatus.cancelled},
        OrderStatus.pending_payment: {
            OrderStatus.payment_authorized,
            OrderStatus.paid,
            OrderStatus.payment_failed,
            OrderStatus.cancelled,
        },
        OrderStatus.payment_authorized: {OrderStatus.paid, OrderStatus.cancelled},
        OrderStatus.paid: {OrderStatus.processing, OrderStatus.cancelled},
        OrderStatus.processing: {OrderStatus.completed, OrderStatus.cancelled},
        OrderStatus.completed: set(),
        OrderStatus.cancelled: set(),
        OrderStatus.payment_failed: {OrderStatus.pending_payment, OrderStatus.cancelled},
    }

    def can_transition_to(self, new_status: OrderStatus) -> bool:
        return new_status in self._VALID_TRANSITIONS.get(self.status, set())


class OrderItem(Base):
    __tablename__ = "order_items"
    __table_args__ = (Index("ix_order_items_order_id", "order_id"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    order_id: Mapped[str] = mapped_column(String(36), ForeignKey("orders.id"), nullable=False)
    product_id: Mapped[str] = mapped_column(String(36), ForeignKey("products.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    price: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    product_name: Mapped[str] = mapped_column(String(500), nullable=False)
    product_snapshot: Mapped[dict] = mapped_column(JSON, default=dict)

    order: Mapped[Order] = relationship("Order", back_populates="items")
    product: Mapped[Product] = relationship("Product", back_populates="order_items")


class Payment(Base):
    __tablename__ = "payments"
    __table_args__ = (
        Index("ix_payments_order_id", "order_id"),
        UniqueConstraint("razorpay_payment_id", name="uq_payments_razorpay_payment_id"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    order_id: Mapped[str] = mapped_column(String(36), ForeignKey("orders.id"), nullable=False)
    razorpay_payment_id: Mapped[str] = mapped_column(String(100), nullable=True, unique=True)
    razorpay_order_id: Mapped[str] = mapped_column(String(100), nullable=True)
    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="INR")
    status: Mapped[PaymentStatus] = mapped_column(
        Enum(PaymentStatus), default=PaymentStatus.created
    )
    failure_reason: Mapped[str] = mapped_column(String(500), nullable=True)
    failure_code: Mapped[str] = mapped_column(String(50), nullable=True)
    method: Mapped[str] = mapped_column(String(50), nullable=True)
    provider: Mapped[str] = mapped_column(String(20), default="demo")
    payment_metadata: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=_now, onupdate=_now)

    order: Mapped[Order] = relationship("Order", back_populates="payments")


class WebhookEvent(Base):
    __tablename__ = "webhook_events"
    __table_args__ = (
        UniqueConstraint("event_id", name="uq_webhook_events_event_id"),
        Index("ix_webhook_events_status", "status"),
        Index("ix_webhook_events_created_at", "created_at"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    event_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    status: Mapped[WebhookStatus] = mapped_column(
        Enum(WebhookStatus), default=WebhookStatus.received
    )
    error_message: Mapped[str] = mapped_column(Text, nullable=True)
    processed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)


class Recommendation(Base):
    __tablename__ = "recommendations"
    __table_args__ = (
        Index("ix_recommendations_user_id", "user_id"),
        Index("ix_recommendations_product_id", "product_id"),
        Index("ix_recommendations_type", "recommendation_type"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    product_id: Mapped[str] = mapped_column(String(36), ForeignKey("products.id"), nullable=False)
    recommendation_type: Mapped[RecommendationType] = mapped_column(Enum(RecommendationType))
    reason: Mapped[str] = mapped_column(Text, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    score: Mapped[float] = mapped_column(Float, default=0.0)
    score_breakdown: Mapped[dict] = mapped_column(JSON, default=dict)
    source: Mapped[str] = mapped_column(String(50), nullable=True)
    prompt_version: Mapped[str] = mapped_column(String(50), nullable=True)
    # Attribution tracking
    shown_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    clicked_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    added_to_cart_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    purchased_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)

    user: Mapped[User] = relationship("User", back_populates="recommendations")
    product: Mapped[Product] = relationship("Product", back_populates="recommendations")


class Conversation(Base):
    __tablename__ = "conversations"
    __table_args__ = (
        Index("ix_conversations_user_id", "user_id"),
        UniqueConstraint("session_id", name="uq_conversations_session_id"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    session_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=_now, onupdate=_now)

    user: Mapped[User] = relationship("User", back_populates="conversations")
    messages: Mapped[list[ConversationMessage]] = relationship(
        "ConversationMessage", back_populates="conversation", cascade="all, delete-orphan"
    )
    agent_actions: Mapped[list[AgentAction]] = relationship(
        "AgentAction", back_populates="conversation"
    )


class ConversationMessage(Base):
    __tablename__ = "conversation_messages"
    __table_args__ = (Index("ix_conv_messages_conversation_id", "conversation_id"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    conversation_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("conversations.id"), nullable=False
    )
    role: Mapped[str] = mapped_column(String(20), nullable=False)  # user | assistant | system
    message: Mapped[str] = mapped_column(Text, nullable=False)
    intent: Mapped[str] = mapped_column(String(100), nullable=True)
    msg_metadata: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)

    conversation: Mapped[Conversation] = relationship("Conversation", back_populates="messages")


class AgentAction(Base):
    __tablename__ = "agent_actions"
    __table_args__ = (
        Index("ix_agent_actions_conversation_id", "conversation_id"),
        Index("ix_agent_actions_created_at", "created_at"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    conversation_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("conversations.id"), nullable=False
    )
    action_type: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    # Structured telemetry (no chain-of-thought)
    intent: Mapped[str] = mapped_column(String(100), nullable=True)
    model: Mapped[str] = mapped_column(String(50), nullable=True)
    provider: Mapped[str] = mapped_column(String(50), nullable=True)
    prompt_version: Mapped[str] = mapped_column(String(50), nullable=True)
    tool_calls: Mapped[list] = mapped_column(JSON, default=list)
    tool_durations: Mapped[dict] = mapped_column(JSON, default=dict)
    duration_ms: Mapped[int] = mapped_column(Integer, nullable=True)
    confidence: Mapped[str] = mapped_column(String(10), nullable=True)
    recommendation_type: Mapped[str] = mapped_column(String(50), nullable=True)
    input_summary: Mapped[str] = mapped_column(Text, nullable=True)
    output_summary: Mapped[str] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="success")
    error: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)

    conversation: Mapped[Conversation] = relationship("Conversation", back_populates="agent_actions")


class SearchEvent(Base):
    """Tracks search funnel: query → click → cart → purchase."""

    __tablename__ = "search_events"
    __table_args__ = (
        Index("ix_search_events_user_id", "user_id"),
        Index("ix_search_events_created_at", "created_at"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
    query: Mapped[str] = mapped_column(Text, nullable=False)
    intent: Mapped[str] = mapped_column(String(100), nullable=True)
    products_returned: Mapped[int] = mapped_column(Integer, default=0)
    product_clicked_id: Mapped[str] = mapped_column(String(36), nullable=True)
    added_to_cart: Mapped[bool] = mapped_column(Boolean, default=False)
    purchased: Mapped[bool] = mapped_column(Boolean, default=False)
    session_id: Mapped[str] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)


class AuditLog(Base):
    __tablename__ = "audit_logs"
    __table_args__ = (
        Index("ix_audit_logs_user_id", "user_id"),
        Index("ix_audit_logs_timestamp", "timestamp"),
        Index("ix_audit_logs_entity_type", "entity_type"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=True)
    entity_id: Mapped[str] = mapped_column(String(36), nullable=True)
    details: Mapped[dict] = mapped_column(JSON, default=dict)
    ip_address: Mapped[str] = mapped_column(String(45), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=_now)

    user: Mapped[User] = relationship("User", back_populates="audit_logs")
