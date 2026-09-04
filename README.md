# PayPilot AI — Autonomous Merchant Growth & Agentic Checkout Platform

> **"Commerce that thinks, recommends, and converts."**
>
> An AI-powered agentic commerce platform for intelligent product discovery, personalized recommendations, merchant growth, conversational shopping, secure checkout, and explainable payment workflows.

![Next.js](https://img.shields.io/badge/Next.js-16.3.3-black?style=for-the-badge&logo=next.js)
![React](https://img.shields.io/badge/React-19.2.8-61DAFB?style=for-the-badge&logo=react)
![TypeScript](https://img.shields.io/badge/TypeScript-5.x-3178C6?style=for-the-badge&logo=typescript)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?style=for-the-badge&logo=postgresql)
![SQLite](https://img.shields.io/badge/SQLite-Dev%20Mode-003B57?style=for-the-badge&logo=sqlite)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker)
![Razorpay](https://img.shields.io/badge/Razorpay-Test%20Mode-02042B?style=for-the-badge&logo=razorpay)
![JWT](https://img.shields.io/badge/JWT-Auth-000000?style=for-the-badge&logo=jsonwebtokens)

---

## Table of Contents

- [Overview](#overview)
- [Why PayPilot AI?](#why-paypilot-ai)
- [Problem Statement](#problem-statement)
- [Purpose](#purpose)
- [What is PayPilot AI?](#what-is-paypilot-ai)
- [Target Users](#target-users)
- [Features](#features)
- [System Architecture](#system-architecture)
- [How It Works](#how-it-works)
- [AI Agent Workflow](#ai-agent-workflow)
- [AI Architecture](#ai-architecture)
- [Recommendation Engine](#recommendation-engine)
- [Upselling and Cross-Selling](#upselling-and-cross-selling)
- [Explainability](#explainability)
- [Financial Safety & Policy Controls](#financial-safety--policy-controls)
- [Payment Workflow](#payment-workflow)
- [Database](#database)
- [Backend API](#backend-api)
- [Frontend](#frontend)
- [Merchant Dashboard](#merchant-dashboard)
- [Project Structure](#project-structure)
- [Technology Stack](#technology-stack)
- [Requirements](#requirements)
- [Environment Variables](#environment-variables)
- [Installation & Setup (Step-by-Step)](#installation--setup-step-by-step)
- [Running with Docker](#running-with-docker)
- [Demo Mode](#demo-mode)
- [Testing](#testing)
- [Manual Testing Checklist](#manual-testing-checklist)
- [Troubleshooting](#troubleshooting)
- [Security Considerations](#security-considerations)
- [Current Limitations](#current-limitations)
- [Future Enhancements](#future-enhancements)
- [Use Cases](#use-cases)
- [FAQ](#faq)
- [Recommended Demo Flow](#recommended-demo-flow)
- [Project Objectives](#project-objectives)
- [Project Highlights](#project-highlights)
- [Development Workflow](#development-workflow)
- [Author](#author)
- [License](#license)

---

## Overview

PayPilot AI is a production-grade, full-stack AI commerce platform that demonstrates how autonomous agents can intelligently assist customers through the entire shopping journey — from understanding what they want, to recommending the right products, to guiding them through a controlled and auditable checkout.

The platform is designed to solve real business problems: customers struggle to find products with keyword search, merchants miss upselling opportunities, and standard chatbots lack the safety boundaries required to handle financial operations. PayPilot AI addresses each of these with a layered architecture combining an AI agent state machine, a multi-component recommendation engine, policy validation, and a complete audit trail.

---

## Why PayPilot AI?

**Traditional E-Commerce Flow:**

```
Customer → Search → Browse → Product Page → Cart → Checkout → Payment
```

This flow is passive. The system waits for the customer to do all the work. Products are missed. Upsell opportunities are lost. Recommendations feel generic.

**The PayPilot AI Approach:**

```
Customer
  → Natural Language Request
  → AI Intent Understanding
  → Product Discovery (TF-IDF + Keyword Search)
  → Scored Recommendations
  → Upsell / Cross-sell Suggestions
  → Add to Cart
  → Policy Validation
  → User Confirmation
  → Checkout
  → Payment (Demo or Razorpay)
  → Audit Log
  → Merchant Analytics
```

By embedding an AI agent directly in the shopping funnel, PayPilot AI can understand nuanced customer needs ("I need gaming headphones under ₹5,000 for competitive play"), retrieve the most relevant products, explain recommendations clearly, and guide the customer toward purchase — all within a conversational interface.

This creates measurable business impact: higher average order value through intelligent upselling, better product discovery through semantic search, and merchant visibility into AI-driven conversions.

---

## Problem Statement

| Problem | How PayPilot AI Addresses It |
|---|---|
| Keyword search fails for complex needs | AI intent classification extracts category, budget, and use case |
| Generic recommendations feel irrelevant | Multi-factor scoring (intent + budget + rating + popularity) |
| Merchants miss upselling windows | Proactive upsell/cross-sell during product discovery |
| Checkout is disconnected from chat | Agent state machine guides user from chat to order creation |
| AI performing financial actions without safety | `FINANCIAL_ACTIONS` guard + `PolicyValidator` + user confirmation |
| No visibility into AI-driven behavior | `AgentAction` telemetry table + Merchant analytics dashboard |
| Payment failures corrupt order state | Atomic `_finalize_payment_failure()` with inventory release |
| AI decisions are unexplainable | `_explain()` method generates human-readable recommendation reasons |

---

## Purpose

PayPilot AI was built to:

1. **Improve product discovery** — let customers describe what they want in natural language.
2. **Understand customer intent** — extract category, budget, and use case automatically.
3. **Provide personalized recommendations** — multi-factor scoring with explainable output.
4. **Increase merchant revenue** — systematic upselling and cross-selling at discovery time.
5. **Enable intelligent upselling and cross-selling** — with category affinity maps and product relationships.
6. **Provide conversational commerce** — AI assistant integrated into the shopping journey.
7. **Provide controlled checkout** — policy-validated order creation with idempotency.
8. **Integrate payment workflows** — demo payment and Razorpay test-mode support.
9. **Maintain explainability** — every recommendation includes a human-readable reason.
10. **Maintain auditability** — immutable `AuditLog` for all agent actions and financial events.
11. **Provide merchant analytics** — real-time revenue, AI-assisted order tracking, and charts.
12. **Provide failure recovery** — graceful payment failure handling without corrupting order state.

---

## What is PayPilot AI?

> PayPilot AI is a full-stack AI-powered commerce platform where an AI shopping agent understands what a customer wants, searches an intelligent product catalog, recommends suitable products, identifies relevant upselling and cross-selling opportunities, manages the shopping cart, and guides the customer through a secure, policy-validated checkout workflow.

**Core Components:**

- **AI Agent** (`backend/app/agents/`) — An explicit state machine with 11 states, from `RECEIVE_REQUEST` to `AUDIT`. Handles intent classification, entity extraction, tool execution, confirmation gating, and response generation.
- **Recommendation Engine** (`backend/app/services/recommendation_service.py`) — Weighted scoring with intent match, budget fit, rating, popularity, and semantic similarity components.
- **TF-IDF Embeddings** (`backend/app/ai/embeddings/tfidf_embeddings.py`) — Local, dependency-free product similarity search using cosine similarity. Pre-fitted on startup.
- **Policy Guard** (`backend/app/agents/state_machine.py`) — `FINANCIAL_ACTIONS` set that gates checkout, payment, and discount actions behind user confirmation.
- **Payment Services** (`backend/app/payments/`) — Demo payment simulator and Razorpay integration with HMAC-SHA256 signature verification.
- **Frontend** (`frontend/`) — Next.js 16 / React 19 app with conversational chat UI, product catalog, cart, checkout, and merchant analytics dashboard.

---

## Target Users

### Customers
- Search for products by describing needs in natural language.
- Receive AI-scored, explainable product recommendations.
- Manage their shopping cart directly from the chat or the cart page.
- Experience a guided, policy-validated checkout.
- View their order history and individual order details.

### Merchants
- Manage the product catalog (create, update, soft-delete).
- View all customer orders and their payment statuses.
- Monitor real-time analytics: revenue, conversion rate, average order value.
- Track AI-assisted conversions and upsell/cross-sell performance.
- Review agent activity log for AI interaction telemetry.

### Administrators
- Access the full audit log (all system events, agent actions, payment events).
- Monitor system health (API, database, AI provider, payment gateway).
- Administer platform from the `/admin` dashboard.

---

## Features

### AI Commerce Assistant
- **Natural language queries** — customers type requests as they would speak them.
- **Intent detection** — classifies messages into `product_search`, `recommendation`, `add_to_cart`, `view_cart`, `checkout`, `order_status`, `product_comparison`, `upsell_request`, `cross_sell_request`.
- **Entity extraction** — extracts `category`, `budget_max`, `brand`, `use_case` from the message.
- **Suggested follow-up prompts** — AI suggests next questions after every response.
- **Cart integration** — `add_to_cart` intents update the cart via the backend API directly from chat.
- **Checkout gating** — checkout intents trigger a `REQUIRE_CONFIRMATION` state before any financial action.

### Product Discovery
- **Keyword search** — searches `name`, `description`, and `brand` fields (case-insensitive).
- **Category filtering** — filter by category name.
- **Price filtering** — `min_price` / `max_price` query parameters.
- **Rating filter** — `min_rating` filter.
- **Stock filtering** — `in_stock` parameter.
- **Sort options** — by `rating`, `price_asc`, `price_desc`, `newest`.
- **Pagination** — all list endpoints are paginated (`page`, `limit`).
- **Discount calculation** — automatically computed from `price` vs `original_price`.
- **Image fallback** — category-aware gradient + Lucide icon if product image fails to load.

### Recommendation Engine
- **Multi-factor weighted scoring** — see [Recommendation Engine](#recommendation-engine) section.
- **Upsell engine** — suggests better products within 125% of current price.
- **Cross-sell engine** — uses `CROSS_SELL_AFFINITIES` category map to suggest complementary items.
- **Score breakdown** — every recommendation includes a `score_breakdown` dict.
- **Explainable reasons** — `_explain()` generates a human-readable sentence per recommendation.
- **Guardrails** — only active, in-stock products with a valid price are eligible.

### Merchant Growth
- **Upselling** — surfaces premium alternatives when customer selects a product.
- **Cross-selling** — surfaces complementary categories (e.g., Laptop → Laptop Accessories).
- **Analytics** — AI-assisted order count, upsell/cross-sell revenue tracked in the dashboard.
- **Product relationships** — `cross_sell_ids` and `upsell_ids` fields stored per product.

### Cart & Checkout
- **Add to cart** — authenticated endpoint with stock validation.
- **Update quantity** — update any cart item by item ID.
- **Remove item** — remove any item from active cart.
- **Cart totals** — `subtotal`, `discount`, and `total` calculated server-side.
- **Order creation** — atomic: validates stock, reserves inventory, creates order with idempotency key.
- **Idempotency** — unique constraint on `idempotency_key` prevents duplicate orders.
- **Inventory reservation** — `InventoryReservation` rows hold stock for 15 minutes (configurable).

### Payment
- **Demo mode** — fully simulated payment with no external calls. Can simulate success or failure.
- **Razorpay test mode** — real Razorpay SDK integration with test credentials.
- **Signature verification** — HMAC-SHA256 timing-safe comparison for Razorpay payments.
- **Failure recovery** — `_finalize_payment_failure()` releases inventory, marks order `payment_failed`, and writes audit log.
- **Atomic state transitions** — `Order.can_transition_to()` validates every status change.
- **Rate limiting** — `/checkout` and `/payments` endpoints are rate-limited to 10/minute.

### Security
- **JWT authentication** — short-lived access tokens (15 min) + refresh tokens (7 days).
- **bcrypt password hashing** — via `passlib[bcrypt]`.
- **RBAC** — `require_merchant()` and `require_admin()` dependency guards.
- **CORS** — explicit origin allowlist via `ALLOWED_ORIGINS`.
- **Rate limiting** — `slowapi` on sensitive endpoints (login, register, chat, checkout, payment).
- **Input validation** — all requests validated via Pydantic schemas.
- **Financial action guard** — `FINANCIAL_ACTIONS` set requires user confirmation before execution.
- **Audit logging** — every sensitive action (login, register, product CRUD, checkout, payment) writes to `audit_logs`.

### Auditability
- `user_registered`, `user_login` — auth events.
- `product_created`, `product_updated`, `product_deactivated` — product management.
- `checkout_created` — order creation with amount and demo flag.
- `payment_success` — payment capture with order ID and amount.
- `payment_failed` — failure reason and order ID.
- All records include `user_id`, `entity_type`, `entity_id`, `details`, `ip_address`, and `timestamp`.

---

## System Architecture

```mermaid
graph TD
    Browser[Customer Browser] -->|HTTPS / REST| FE[Next.js 16 Frontend\nReact 19 + TypeScript]
    FE -->|Axios HTTP Client| API[FastAPI Backend\nPort 8000]

    subgraph Backend
        API --> Auth[JWT Auth + RBAC\npython-jose + passlib]
        Auth --> SM[AI Agent State Machine\n11-State Explicit FSM]

        SM --> IC[Intent Classifier\nRegex / OpenAI]
        SM --> EE[Entity Extractor\nCategory + Budget + Use Case]
        SM --> TS[Tool Selector\n9 Available Tools]

        TS --> PS[Product Search\nSQLAlchemy + TF-IDF]
        TS --> RE[Recommendation Engine\nWeighted Scoring]
        TS --> CS[Cross-sell Engine\nCategory Affinities]
        TS --> US[Upsell Engine\nPrice Range Query]

        SM --> PG[Policy Guard\nFINANCIAL_ACTIONS Gate]
        PG --> UC[User Confirmation Gate\nREQUIRE_CONFIRMATION State]
        UC --> CS2[Cart Service\nInventory Reservation]
        CS2 --> OS[Order Service\nAtomic State Machine]
        OS --> PS2[Payment Service\nDemo / Razorpay]
    end

    PS2 -->|Test API| RZ[Razorpay Test Mode]
    PS2 -->|Simulated| DM[Demo Payment Service]

    Backend --> AL[Audit Log\nImmutable Event Record]
    Backend --> DB[(SQLite Dev\nPostgreSQL Prod)]
    DB --> MA[Merchant Analytics\nRevenue + AI Conversions]
```

---

## How It Works

### Customer Workflow

1. Customer opens the application at `http://localhost:3000`.
2. Registers or logs in — receives a JWT access token stored in localStorage.
3. Browses the product catalog or opens the AI Chat page.
4. Types a natural language query: *"Find gaming headphones under ₹5,000."*
5. The `POST /api/v1/assistant/chat` endpoint is called with the message.
6. The AI Agent State Machine begins processing (see [AI Agent Workflow](#ai-agent-workflow)).
7. The agent classifies intent as `product_search` and extracts entities: `{category: "Headphones", budget_max: 5000, use_case: "gaming"}`.
8. Products are retrieved and scored by the Recommendation Engine.
9. The AI response includes products, recommendations with reasons, and suggested follow-up prompts.
10. Customer clicks "Add to Cart" — calls `POST /api/v1/cart/items` (authenticated).
11. Agent may surface upsell or cross-sell suggestions.
12. Customer opens the cart page and clicks "Proceed to Checkout".
13. `POST /api/v1/checkout/create` is called — validates stock, reserves inventory, creates `Order` in `pending_payment` status, creates a demo/Razorpay payment order, and audits the event.
14. Customer confirms payment — `POST /api/v1/payments/verify-demo` (in demo mode) is called.
15. Payment result is verified, inventory is confirmed or released.
16. Order status transitions atomically: `pending_payment → paid → processing`.
17. Audit record is written for `payment_success` or `payment_failed`.
18. Customer is redirected to the order confirmation page.

---

## AI Agent Workflow

The agent is implemented as an **explicit 11-state Python state machine** in `backend/app/agents/state_machine.py`. It does not use LangGraph or external agent frameworks — all transitions are deterministic and auditable.

```
User Message
    ↓
RECEIVE_REQUEST  — store message in AgentContext
    ↓
CLASSIFY_INTENT  — pattern match via regex OR OpenAI API call
    ↓
EXTRACT_ENTITIES — extract category, budget_max, brand, use_case
    ↓
PLAN             — decide which tools are needed
    ↓
SELECT_TOOL      — choose from: search_products, get_recommendations,
                   get_upsell, get_cross_sell, view_cart,
                   add_to_cart, create_order, get_order_status, etc.
    ↓
EXECUTE_TOOL     — run selected tool, store results in context
    ↓
VALIDATE_RESULT  — check for errors, missing products, etc.
    ↓
REQUIRE_CONFIRMATION  ← (only for FINANCIAL_ACTIONS: checkout, payment)
    |
    ↓
EXECUTE_ACTION   — perform the confirmed financial action
    ↓
GENERATE_RESPONSE — format AI message + products + recommendations
    ↓
AUDIT            — write AgentAction record with telemetry
    ↓
END              — return ChatResponse to frontend
```

**Financial Action Guard:**

The constant `FINANCIAL_ACTIONS = {"checkout", "create_payment", "apply_discount"}` in the state machine ensures that any action touching money enters the `REQUIRE_CONFIRMATION` state. The AI cannot execute a payment without explicit user acknowledgment.

---

## AI Architecture

PayPilot AI uses a **provider abstraction** (`BaseAIProvider`) so the AI backend can be swapped without changing agent logic.

### Mock Provider (Default — No API Key Required)
- **File:** `backend/app/ai/providers/mock_provider.py`
- Uses ordered regex patterns with word boundaries (`\b`) to classify intent.
- Uses priority-based keyword matching to extract category (e.g., "gaming headphones" → Headphones, not Gaming — because `headphone` has priority 10 vs `gaming` at priority 5).
- Generates deterministic, structured responses without any external calls.
- 100% offline — works immediately after installation.

### OpenAI Provider (Optional)
- **File:** `backend/app/ai/providers/openai_provider.py`
- Activated by setting `AI_PROVIDER=openai` and providing `OPENAI_API_KEY`.
- Configured model: `gpt-4o-mini` (set via `OPENAI_MODEL`).
- Falls back to Mock Provider if key is missing or API call fails.

### TF-IDF Embedding Provider
- **File:** `backend/app/ai/embeddings/tfidf_embeddings.py`
- Uses `scikit-learn`'s `TfidfVectorizer` + cosine similarity for product similarity scoring.
- Pre-fitted on startup from the product catalog (up to 500 products).
- Falls back to keyword-based scoring if `scikit-learn` is unavailable.
- No API key required.

### Provider Selection (via `.env`)
```env
AI_PROVIDER=mock          # Options: mock | openai
EMBEDDING_PROVIDER=tfidf  # Options: tfidf | openai
```

---

## Recommendation Engine

The Recommendation Engine (`backend/app/services/recommendation_service.py`) computes a weighted composite score for each candidate product.

### Scoring Formula

```
Recommendation Score =
  (intent_match     × 0.30)   # Does product category match the query?
+ (semantic_sim     × 0.25)   # TF-IDF cosine similarity to query
+ (budget_fit       × 0.20)   # Is price ≤ budget? Rewarded near the ceiling
+ (rating_score     × 0.15)   # Product rating normalized 0–5 → 0–1
+ (popularity_score × 0.10)   # Review count normalized (cap 1000 reviews)
```

### Component Details

| Component | Logic |
|---|---|
| `intent_match` | 1.0 if category matches, 0.3 if partial, 0.2 if miss, 0.7 if no filter |
| `budget_fit` | `min(1.0, price / budget_max × 1.2)` if under budget; 0.0 if over budget |
| `rating_score` | `rating / 5.0` |
| `popularity_score` | `min(1.0, review_count / 1000)` |
| `semantic_similarity` | Cosine similarity via TF-IDF (default 0.7 for pre-ranked results) |

### Guardrails
Only products that are `is_active=True`, `stock > 0`, and `price > 0` are eligible for recommendation. Top 5 scored results are returned.

### Upsell Logic
Finds products in the same category where `price > current` and `price ≤ max(current × 1.25, budget_max)` — i.e., better options within 25% price premium.

### Cross-sell Logic
Uses `CROSS_SELL_AFFINITIES` dictionary (e.g., `"Laptops" → ["Laptop Accessories", "Mice", "Keyboards"]`) to find complementary products in related categories.

---

## Upselling and Cross-Selling

### Upselling
Encourages customers to consider a higher-value product when it represents meaningful added value.

**Example:**
> Customer asks for "wireless headphones."
> AI recommends Sony WH-1000XM5 at ₹24,990.
> Upsell surfaces: Sony WH-1000XM5 Pro at ₹27,490 — *"Premium option with better specs — ₹2,500 more than your selection."*

The upsell ceiling is 25% above the currently viewed product's price, keeping suggestions realistic.

### Cross-Selling
Surfaces complementary products from related categories when a product is selected.

**Example:**
> Customer adds a Laptop to cart.
> Cross-sell surfaces: Wireless Mouse and USB-C Hub from Laptop Accessories.
> *"Customers who bought this laptop also considered these accessories."*

**Why it matters for merchants:** Every upsell or cross-sell accepted increases Average Order Value (AOV) without acquiring new customers. The Merchant Dashboard tracks these as separate revenue attribution metrics.

---

## Explainability

PayPilot AI avoids opaque recommendations. The `_explain()` method in the Recommendation Service generates a structured, human-readable reason for every recommendation.

**Example reasons generated:**
- *"Within your budget of ₹5,000"* — when `budget_fit == 1.0` and a budget was specified.
- *"Matches your gaming use case"* — when `intent_match ≥ 0.8` and a use case was extracted.
- *"Highly rated: 4.6★ from 2,847 reviews"* — when `rating_score ≥ 0.8`.
- *"Popular choice in this category"* — when `popularity_score ≥ 0.5`.

The `score_breakdown` dictionary is also returned in the API response so frontend UIs and developers can inspect the exact contribution of each factor.

---

## Financial Safety & Policy Controls

One of the most critical design decisions in PayPilot AI is that **the AI agent cannot perform financial operations unilaterally**. All money-touching actions require an explicit validation chain.

```
AI Agent identifies checkout intent
    ↓
State transitions to REQUIRE_CONFIRMATION
    ↓
User must explicitly confirm (separate API call)
    ↓
EXECUTE_ACTION proceeds
    ↓
POST /api/v1/checkout/create
    ↓
Stock validated + Inventory reserved
    ↓
Idempotency key checked (prevents duplicate orders)
    ↓
Payment order created (Demo / Razorpay)
    ↓
POST /api/v1/payments/verify OR /verify-demo
    ↓
Signature verified (Razorpay) or simulated (Demo)
    ↓
Atomic finalization: Order status + Inventory + AuditLog
    ↓
Audit record written
```

### Key Safeguards

| Safeguard | Implementation |
|---|---|
| Financial action gating | `FINANCIAL_ACTIONS = {"checkout", "create_payment", "apply_discount"}` |
| Idempotency | `UniqueConstraint` on `idempotency_key` in `orders` table |
| Signature verification | HMAC-SHA256 timing-safe comparison for Razorpay |
| Atomic state transitions | `Order.can_transition_to()` validates every status change |
| Inventory safety | `InventoryReservation` released on payment failure |
| Rate limiting | `/checkout` and `/payments` limited to 10/minute |
| Audit trail | Every financial event writes to `audit_logs` |

---

## Payment Workflow

### Success Path (Demo Mode)

```
1. Customer clicks "Place Order"
2. POST /api/v1/checkout/create
   - Validates active cart is non-empty
   - Calls OrderService.create_order_from_cart() (atomic, validates stock)
   - Calls DemoPaymentService.create_order() → returns demo_order_<hex>
   - Saves order in pending_payment status
   - Writes checkout_created audit log
3. Frontend receives order_id + razorpay_order_id + amount
4. POST /api/v1/payments/verify-demo (simulate_failure: false)
   - DemoPaymentService.simulate_payment() → returns demo_pay_<hex>
   - _finalize_payment_success() called atomically:
     → Payment.status = captured
     → Order transitions: pending_payment → paid
     → OrderService.confirm_inventory() called
     → payment_success audit log written
5. Order confirmation displayed to customer
```

### Failure Path

```
1. POST /api/v1/payments/verify-demo (simulate_failure: true)
   - DemoPaymentService returns failure_reason + failure_code
   - _finalize_payment_failure() called atomically:
     → Payment.status = failed
     → payment.failure_reason saved
     → Order transitions: pending_payment → payment_failed
     → OrderService.release_inventory() called
     → payment_failed audit log written
2. Frontend displays failure reason
3. User can retry (new checkout attempt, new idempotency_key)
4. Order is NEVER incorrectly marked as paid
```

### Razorpay Mode (Optional)
When `PAYMENT_PROVIDER=razorpay` and credentials are set:
- `RazorpayService.create_order()` creates a real Razorpay order.
- Frontend loads the Razorpay checkout widget.
- `POST /api/v1/payments/verify` verifies the signature and fulfills the order.

---

## Database

The database is managed by **SQLAlchemy (async)** with **Alembic** for schema migrations.

- **Development:** SQLite (`backend/paypilot.db`) — zero setup required.
- **Production:** PostgreSQL 16 (via Docker or managed service).

### Models

| Model | Table | Purpose |
|---|---|---|
| `User` | `users` | Authentication, roles (customer / merchant / admin) |
| `Product` | `products` | Catalog: price, stock, rating, category, images, embeddings |
| `InventoryReservation` | `inventory_reservations` | Temporarily holds stock during checkout (15-min TTL) |
| `Cart` | `carts` | User's active shopping session |
| `CartItem` | `cart_items` | Individual products in the cart with quantity |
| `Order` | `orders` | Finalized purchase record with idempotency key |
| `OrderItem` | `order_items` | Snapshot of product at time of purchase |
| `Payment` | `payments` | Payment transaction record (provider, status, failure reason) |
| `Recommendation` | `recommendations` | Tracks AI recommendations and attribution (shown → clicked → purchased) |
| `Conversation` | `conversations` | Chat session with session_id |
| `ConversationMessage` | `conversation_messages` | Individual chat messages with intent |
| `AgentAction` | `agent_actions` | AI agent telemetry (tool calls, duration, confidence, provider) |
| `SearchEvent` | `search_events` | Search funnel tracking (query → click → cart → purchase) |
| `WebhookEvent` | `webhook_events` | Idempotent Razorpay webhook processing |
| `AuditLog` | `audit_logs` | Immutable system event ledger |

### Enums

- `UserRole`: `customer`, `merchant`, `admin`
- `OrderStatus`: `draft`, `pending_payment`, `payment_authorized`, `paid`, `processing`, `completed`, `cancelled`, `payment_failed`
- `PaymentStatus`: `created`, `authorized`, `captured`, `failed`, `cancelled`, `refunded`
- `CartStatus`: `active`, `checked_out`, `abandoned`
- `RecommendationType`: `personalized`, `upsell`, `cross_sell`, `semantic`, `popular`

---

## Backend API

FastAPI provides automatic OpenAPI documentation available at **`http://localhost:8000/docs`** (Swagger UI) and **`http://localhost:8000/redoc`**.

### Endpoint Reference

| Method | Endpoint | Auth | Purpose |
|---|---|---|---|
| `GET` | `/health` | No | System health overview |
| `GET` | `/health/db` | No | Database connectivity check |
| `GET` | `/health/ai` | No | AI provider status |
| `GET` | `/health/payment` | No | Payment provider status |
| `POST` | `/api/v1/auth/register` | No | Create account (rate: 5/min) |
| `POST` | `/api/v1/auth/login` | No | Login, get JWT tokens (rate: 10/min) |
| `GET` | `/api/v1/auth/me` | JWT | Get current user profile |
| `GET` | `/api/v1/products` | No | List/search products (paginated, filterable) |
| `GET` | `/api/v1/products/{id}` | No | Get single product |
| `POST` | `/api/v1/products` | Merchant | Create product |
| `PUT` | `/api/v1/products/{id}` | Merchant | Update product |
| `DELETE` | `/api/v1/products/{id}` | Merchant | Soft-delete product |
| `POST` | `/api/v1/assistant/chat` | JWT | AI conversational endpoint (rate: 30/min) |
| `GET` | `/api/v1/cart` | JWT | Get active cart |
| `POST` | `/api/v1/cart/items` | JWT | Add item to cart |
| `PUT` | `/api/v1/cart/items/{id}` | JWT | Update cart item quantity |
| `DELETE` | `/api/v1/cart/items/{id}` | JWT | Remove cart item |
| `GET` | `/api/v1/recommendations` | JWT | Get product recommendations |
| `POST` | `/api/v1/checkout/create` | JWT | Create order + payment intent (rate: 10/min) |
| `POST` | `/api/v1/payments/verify` | JWT | Verify Razorpay signature + fulfill order |
| `POST` | `/api/v1/payments/verify-demo` | JWT | Simulate demo payment success/failure |
| `GET` | `/api/v1/orders` | JWT | List user's orders |
| `GET` | `/api/v1/orders/{id}` | JWT | Get single order detail |
| `GET` | `/api/v1/analytics/overview` | Merchant | Revenue, orders, AI metrics |
| `GET` | `/api/v1/analytics/revenue` | Merchant | Daily revenue time series |
| `GET` | `/api/v1/agent/activity` | Merchant | Agent action telemetry log |
| `GET` | `/api/v1/audit` | Admin | Full audit log (paginated) |
| `POST` | `/api/v1/payments/webhook` | No (signed) | Razorpay webhook receiver |

---

## Frontend

Built with the **Next.js 16 App Router** paradigm.

### Technology
- **Next.js 16.3.3** with App Router (`/app` directory).
- **React 19.2.8** and **TypeScript**.
- **Tailwind CSS 4.x** for utility-first styling.
- **Radix UI** primitives (via shadcn/ui pattern) for accessible components.
- **Lucide React** for icons.
- **Recharts 3.x** for analytics charts.
- **Axios** for typed HTTP client (`lib/api.ts`).

### Pages & Routes

| Route | Page | Description |
|---|---|---|
| `/` | Home | Landing page with feature overview |
| `/login` | Login | JWT authentication form |
| `/register` | Register | Account creation form |
| `/shop` | Shop | Product catalog with search and filter |
| `/chat` | AI Chat | Conversational AI shopping assistant |
| `/cart` | Cart & Checkout | Cart management + demo checkout flow |
| `/orders` | Orders | Customer order history |
| `/orders/[id]` | Order Detail | Individual order details + payment status |
| `/profile` | Profile | User account information |
| `/dashboard` | Dashboard | Customer quick links and recent activity |
| `/merchant` | Merchant Dashboard | Analytics: revenue, orders, AI metrics, charts |
| `/merchant/products` | Product Management | CRUD interface for product catalog |
| `/merchant/orders` | Merchant Orders | View all customer orders |
| `/admin` | Admin | System health monitoring |

### API Client (`lib/api.ts`)
A fully typed Axios wrapper that:
- Auto-attaches the JWT `Bearer` token from localStorage.
- Handles 401 errors by clearing auth state.
- Exposes typed methods: `login()`, `register()`, `getProducts()`, `chat()`, `addToCart()`, `createCheckout()`, `verifyDemoPayment()`, `getAnalyticsOverview()`, etc.

---

## Merchant Dashboard

The merchant dashboard (`/merchant`) provides a real-time view of business performance powered by the `/api/v1/analytics/overview` and `/api/v1/analytics/revenue` endpoints.

### Metrics Displayed

| Metric | Source |
|---|---|
| Total Revenue | Sum of `Order.amount` where status is `paid` or `completed` |
| Total Orders | Count of paid/completed orders |
| Total Customers | Distinct `user_id` on paid orders |
| Average Order Value | Total Revenue ÷ Total Orders |
| AI-Assisted Orders | Count of `AgentAction` rows with `action_type = "checkout"` |
| Payment Success Rate | (Paid orders ÷ Total payment attempts) × 100 |
| Failed Payments | Count of `Payment.status = failed` |
| AI-Assisted Revenue | Demo metric: ~42% of total revenue |
| Upsell Revenue | Demo metric: ~15% of total revenue |
| Cross-sell Revenue | Demo metric: ~12% of total revenue |

> **Note:** AI-assisted revenue, upsell revenue, and cross-sell revenue are computed as proportional demo metrics. Real attribution tracking infrastructure (the `Recommendation.added_to_cart_at` and `purchased_at` fields) is in place but requires user-event instrumentation to compute live values.

### Charts (via Recharts)
- **Area Chart** — Daily revenue over the last 30 days with AI revenue overlay.
- **Bar Chart** — Daily order counts.
- **Pie Chart** — Revenue distribution by category.

---

## Project Structure

```text
PayPilot-AI/
│
├── backend/                          # FastAPI application
│   ├── alembic/                      # Database migrations
│   │   └── versions/
│   │       └── 1c73a3cd532a_initial_migration.py
│   ├── app/
│   │   ├── agents/
│   │   │   ├── state_machine.py      # 11-state AI agent FSM
│   │   │   └── tools.py              # Agent tool implementations
│   │   ├── ai/
│   │   │   ├── embeddings/
│   │   │   │   └── tfidf_embeddings.py  # Local TF-IDF similarity
│   │   │   └── providers/
│   │   │       ├── base.py           # Abstract AIProvider
│   │   │       ├── mock_provider.py  # Default: regex-based, no API key
│   │   │       └── openai_provider.py  # Optional: GPT-4o-mini
│   │   ├── api/v1/
│   │   │   ├── auth.py               # Register, login, /me
│   │   │   ├── products.py           # CRUD + search
│   │   │   ├── cart.py               # Cart management
│   │   │   ├── assistant.py          # AI chat endpoint
│   │   │   ├── checkout.py           # Order creation + payment init
│   │   │   ├── payments.py           # Verify + demo payment
│   │   │   ├── health.py             # Health checks
│   │   │   └── _combined_routes.py   # Orders, recommendations, analytics, audit, agent, webhooks, admin
│   │   ├── core/
│   │   │   ├── config.py             # Pydantic Settings
│   │   │   ├── database.py           # SQLAlchemy async engine
│   │   │   └── security.py           # JWT + bcrypt + idempotency key
│   │   ├── models/
│   │   │   └── models.py             # All SQLAlchemy ORM models
│   │   ├── payments/
│   │   │   ├── demo_payment.py       # Demo payment simulator
│   │   │   └── razorpay_service.py   # Razorpay SDK wrapper
│   │   ├── schemas/
│   │   │   └── schemas.py            # Pydantic request/response schemas
│   │   ├── services/
│   │   │   ├── cart_service.py       # Cart business logic
│   │   │   ├── order_service.py      # Order + inventory logic
│   │   │   └── recommendation_service.py  # Scoring + upsell + cross-sell
│   │   └── main.py                   # FastAPI app, CORS, routers, startup
│   ├── tests/
│   │   ├── unit/                     # Unit test placeholder
│   │   └── integration/              # Integration test placeholder
│   ├── requirements.txt
│   ├── pyproject.toml                # Ruff, mypy, pytest config
│   ├── alembic.ini
│   └── Dockerfile
│
├── database/
│   └── seed/
│       └── seed.py                   # Seeds users, products (44+), and demo orders
│
├── frontend/                         # Next.js 16 application
│   ├── app/                          # App Router pages
│   │   ├── page.tsx                  # Landing page
│   │   ├── login/page.tsx
│   │   ├── register/page.tsx
│   │   ├── shop/page.tsx
│   │   ├── chat/page.tsx
│   │   ├── cart/page.tsx
│   │   ├── orders/page.tsx
│   │   ├── orders/[id]/page.tsx
│   │   ├── profile/page.tsx
│   │   ├── dashboard/page.tsx
│   │   ├── merchant/page.tsx
│   │   ├── merchant/products/page.tsx
│   │   ├── merchant/orders/page.tsx
│   │   └── admin/page.tsx
│   ├── components/ui/                # Radix UI + shadcn-pattern components
│   ├── lib/
│   │   ├── api.ts                    # Typed Axios API client
│   │   └── auth-context.tsx          # React auth context
│   ├── .env.local                    # Frontend env (NEXT_PUBLIC_API_URL)
│   ├── package.json
│   └── Dockerfile
│
├── docs/                             # Project documentation
├── screenshots/                      # UI screenshots
├── docker-compose.yml                # Full-stack Docker setup
├── .env.example                      # Environment variable template
└── README.md
```

---

## Technology Stack

| Layer | Technology | Version | Purpose |
|---|---|---|---|
| **Frontend Framework** | Next.js | 16.3.3 | React-based full-stack web framework |
| **UI Library** | React | 19.2.8 | Component-based UI |
| **Language (FE)** | TypeScript | 5.x | Static typing for frontend |
| **Styling** | Tailwind CSS | 4.x | Utility-first CSS framework |
| **UI Components** | Radix UI / shadcn | Latest | Accessible, composable primitives |
| **Icons** | Lucide React | 1.34.0 | Icon library |
| **Charts** | Recharts | 3.x | Analytics data visualization |
| **HTTP Client** | Axios | 1.x | Typed frontend API calls |
| **Backend Framework** | FastAPI | 0.100+ | Async Python REST API framework |
| **Language (BE)** | Python | 3.11+ | Backend + AI logic |
| **ORM** | SQLAlchemy (async) | 2.x | Database abstraction layer |
| **Migrations** | Alembic | Latest | Schema version control |
| **Database (Dev)** | SQLite + aiosqlite | Latest | Zero-config development database |
| **Database (Prod)** | PostgreSQL | 16 | Production-grade relational DB |
| **AI (Default)** | Mock Provider | N/A | Regex-based, fully offline |
| **AI (Optional)** | OpenAI | GPT-4o-mini | LLM-powered intent classification |
| **Embeddings** | scikit-learn TF-IDF | Latest | Local product similarity search |
| **Payments (Dev)** | Demo Service | N/A | Simulated payment gateway |
| **Payments (Opt)** | Razorpay | Test Mode | Real payment gateway integration |
| **Auth** | python-jose + passlib | Latest | JWT + bcrypt password hashing |
| **Rate Limiting** | slowapi | Latest | Per-endpoint rate limits |
| **Containers** | Docker Compose | Latest | Multi-service container orchestration |
| **Linting** | Ruff | Latest | Python linter and formatter |

---

## Requirements

### Software
| Requirement | Version | Notes |
|---|---|---|
| **Node.js** | 18+ (20+ recommended) | Needed for Next.js frontend |
| **npm** | 9+ | Comes with Node.js |
| **Python** | 3.11+ | Backend and seed scripts |
| **Git** | Any | Version control |
| **Docker & Docker Compose** | Latest | Optional, for PostgreSQL + full stack |

### API Keys (All Optional — Demo Mode Works Without Any)
| Service | Variable | Notes |
|---|---|---|
| OpenAI | `OPENAI_API_KEY` | Optional — Mock provider is default |
| Razorpay | `RAZORPAY_KEY_ID` + `RAZORPAY_KEY_SECRET` | Optional — Demo payment is default |

---

## Environment Variables

### Backend (`backend/.env`)

Copy `backend/.env.example` (or `.env.example` at root) to `backend/.env`.

```env
# ── Application ───────────────────────────────────────────────────────────────
APP_NAME=PayPilot AI
APP_ENV=development
DEBUG=true
SECRET_KEY=your-super-secret-key-change-this-min-32-chars

# ── Database ──────────────────────────────────────────────────────────────────
# Development (SQLite — zero setup):
DATABASE_URL=sqlite+aiosqlite:///./paypilot.db
DATABASE_URL_SYNC=sqlite:///./paypilot.db

# Production (PostgreSQL — use with Docker or managed service):
# DATABASE_URL=postgresql+asyncpg://paypilot:paypilot_pass@localhost:5432/paypilot_db
# DATABASE_URL_SYNC=postgresql://paypilot:paypilot_pass@localhost:5432/paypilot_db

# ── JWT ───────────────────────────────────────────────────────────────────────
JWT_SECRET_KEY=your-jwt-secret-key-min-32-characters-long
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# ── AI Provider ───────────────────────────────────────────────────────────────
# mock = default (no API key needed, fully offline)
# openai = real LLM (requires OPENAI_API_KEY)
AI_PROVIDER=mock
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

# ── Embedding Provider ────────────────────────────────────────────────────────
EMBEDDING_PROVIDER=tfidf

# ── Payments ──────────────────────────────────────────────────────────────────
# demo = default (simulated, no real money)
# razorpay = Razorpay test mode (requires credentials below)
PAYMENT_PROVIDER=demo
RAZORPAY_KEY_ID=rzp_test_your_key_id_here
RAZORPAY_KEY_SECRET=your_razorpay_key_secret_here
RAZORPAY_WEBHOOK_SECRET=your_razorpay_webhook_secret_here

# ── CORS ──────────────────────────────────────────────────────────────────────
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# ── Rate Limiting ─────────────────────────────────────────────────────────────
RATE_LIMIT_LOGIN=10/minute
RATE_LIMIT_REGISTER=5/minute
RATE_LIMIT_CHAT=30/minute
RATE_LIMIT_PAYMENT=10/minute

# ── Inventory ─────────────────────────────────────────────────────────────────
INVENTORY_RESERVATION_MINUTES=15
```

### Frontend (`frontend/.env.local`)

```env
# CRITICAL: Use 127.0.0.1 (not localhost) to avoid Node 18+ IPv6/IPv4 mismatch
# Node 18+ resolves "localhost" to ::1 (IPv6), but uvicorn binds to 127.0.0.1 (IPv4)
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000

# Optional: Set only if using Razorpay test mode in the frontend
NEXT_PUBLIC_RAZORPAY_KEY_ID=rzp_test_your_key_id_here
```

> ⚠️ **Warning:** Never commit `.env` or `.env.local` files containing real secrets, API keys, or payment credentials to version control.

---

## Installation & Setup (Step-by-Step)

This guide walks you from zero to a running application.

---

### Step 1 — Clone the Repository

```bash
git clone https://github.com/yourusername/paypilot-ai.git
cd paypilot-ai
```

---

### Step 2 — Set Up the Backend

#### 2a. Create a Python virtual environment

```bash
cd backend
python -m venv venv
```

#### 2b. Activate the virtual environment

**Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
venv\Scripts\activate.bat
```

**macOS / Linux:**
```bash
source venv/bin/activate
```

You should see `(venv)` prefix in your terminal.

#### 2c. Install Python dependencies

```bash
pip install -r requirements.txt
```

> If you're on Python 3.14+ and some packages fail to build, try:
> ```bash
> pip install -r requirements.txt --only-binary=:all: --prefer-binary
> ```

---

### Step 3 — Configure Backend Environment Variables

```bash
# From the backend/ directory
cp ../.env.example .env
```

For local development, edit `.env` and change the database to SQLite (no PostgreSQL needed):

```env
DATABASE_URL=sqlite+aiosqlite:///./paypilot.db
DATABASE_URL_SYNC=sqlite:///./paypilot.db
AI_PROVIDER=mock
PAYMENT_PROVIDER=demo
```

Leave all other values at their defaults for development.

---

### Step 4 — Start PostgreSQL (Optional — Skip for SQLite Dev Mode)

If you want to use PostgreSQL instead of SQLite:

```bash
# From the root directory
docker compose up -d db
```

This starts the `db` service defined in `docker-compose.yml` on port `5432`.

Wait until healthy:
```bash
docker compose ps
```

Then update `backend/.env` to use the PostgreSQL connection string from `.env.example`.

---

### Step 5 — Run Database Migrations

```bash
# From the backend/ directory (venv must be active)
alembic upgrade head
```

This applies the initial migration (`1c73a3cd532a_initial_migration.py`) and creates all tables.

---

### Step 6 — Seed the Database

```bash
# From the backend/ directory (venv must be active)
python -m database.seed.seed
```

This creates:
- **3 demo users:** Customer, Merchant, and Admin
- **44+ products** across 8 categories with images, ratings, and specs
- **30 demo orders** with realistic payment statuses for merchant analytics

> If the seed script fails with "already exists" errors, the database is already seeded — this is safe to ignore.

---

### Step 7 — Start the FastAPI Backend

```bash
# From the backend/ directory (venv must be active)
python -m uvicorn app.main:app --reload --port 8000
```

Expected output:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

Verify it's running:
```bash
curl http://127.0.0.1:8000/health
```

Expected response:
```json
{"status": "operational", "api": {"status": "operational"}, ...}
```

---

### Step 8 — Set Up and Start the Frontend

Open a **new terminal window** (keep the backend running in the first one).

```bash
cd frontend
npm install
```

Create the frontend environment file:

```bash
# Windows PowerShell:
echo "NEXT_PUBLIC_API_URL=http://127.0.0.1:8000" > .env.local

# macOS / Linux:
echo "NEXT_PUBLIC_API_URL=http://127.0.0.1:8000" > .env.local
```

> 🚨 **Important:** Use `127.0.0.1` not `localhost`. Node 18+ resolves `localhost` to `::1` (IPv6) but uvicorn binds to `127.0.0.1` (IPv4), causing `AxiosError: Network Error` on every API call.

Start the development server:

```bash
npm run dev
```

Expected output:
```
  ▲ Next.js 16.3.3
  - Local:        http://localhost:3000
  - Environments: .env.local

 ✓ Starting...
 ✓ Ready in 1234ms
```

---

### Step 9 — Open the Application

| URL | Purpose |
|---|---|
| `http://localhost:3000` | Frontend application |
| `http://127.0.0.1:8000/docs` | Swagger UI (interactive API docs) |
| `http://127.0.0.1:8000/redoc` | ReDoc API documentation |
| `http://127.0.0.1:8000/health` | Backend health check |

### Step 10 — Log In with Demo Accounts

All demo accounts use the password: **`Demo@123`**

| Role | Email | Access |
|---|---|---|
| Customer | `customer@paypilot.demo` | Shop, Chat, Cart, Orders |
| Merchant | `merchant@paypilot.demo` | + Analytics Dashboard, Product Management |
| Admin | `admin@paypilot.demo` | + Audit Logs, System Health |

---

## Running with Docker

Docker Compose runs the entire stack: PostgreSQL, FastAPI backend, and Next.js frontend.

### Start all services

```bash
# From the root directory
docker compose up --build
```

Services started:
- **`db`** — PostgreSQL 16 on port `5432`
- **`backend`** — FastAPI on port `8000` (auto-runs migrations + seed on startup)
- **`frontend`** — Next.js on port `3000`

### Stop all services

```bash
docker compose down
```

### Stop and remove all data (including database volume)

```bash
# WARNING: This permanently deletes all database data
docker compose down -v
```

### Access logs for a specific service

```bash
docker compose logs -f backend
docker compose logs -f frontend
```

---

## Demo Mode

Demo Mode is the default configuration for PayPilot AI. It allows the entire application to run without any external API keys or payment credentials.

### What Demo Mode Provides

| Component | Demo Behavior |
|---|---|
| **AI Provider** (`mock`) | Regex + keyword matching — no OpenAI API key needed |
| **Payment Provider** (`demo`) | Simulated payment IDs — no Razorpay account needed |
| **Embeddings** (`tfidf`) | Local TF-IDF via scikit-learn — no embedding API needed |
| **Database** (SQLite) | File-based DB in `backend/paypilot.db` — no PostgreSQL needed |

### How Demo Mode is Activated

Demo mode is the default. No configuration change is needed. Both conditions are checked:

```python
# From config.py
is_demo_ai: bool = ai_provider == "mock" or not openai_api_key
is_demo_payment: bool = payment_provider == "demo" or not razorpay_key_id
```

If `OPENAI_API_KEY` is missing even with `AI_PROVIDER=openai`, the system falls back to mock automatically.

### Demo Payment Simulation

- **Success:** `POST /api/v1/payments/verify-demo` with `simulate_failure: false` → returns a `demo_pay_<hex>` ID.
- **Failure:** `POST /api/v1/payments/verify-demo` with `simulate_failure: true` → returns failure with reason `"Payment declined by bank (Demo Mode)"`.

### Limitations of Demo Mode

- AI responses are rule-based (no language understanding beyond patterns).
- Payments are not real — no money moves.
- Recommendation scores are computed locally without learned user behavior.

---

## Testing

### Automated Tests

The project includes a `pytest` setup with `asyncio_mode = "auto"` configured in `pyproject.toml`. The `tests/unit/` and `tests/integration/` directories have `__init__.py` files ready for test implementation.

```bash
# From backend/ directory (venv active)
pytest tests/ -v
```

> **Note:** The automated test suite structure is in place (directories, `__init__.py`, pytest config), but individual test files are not yet populated. This is an identified area for contribution. Run the above command to verify the pytest setup works.

### Manual Testing

The recommended approach for verifying the application is the [Manual Testing Checklist](#manual-testing-checklist) and the [Recommended Demo Flow](#recommended-demo-flow).

---

## Manual Testing Checklist

### Authentication
- [ ] Register a new customer account at `/register`
- [ ] Login as customer (`customer@paypilot.demo` / `Demo@123`)
- [ ] Login as merchant (`merchant@paypilot.demo` / `Demo@123`)
- [ ] Login as admin (`admin@paypilot.demo` / `Demo@123`)
- [ ] Try invalid credentials — verify error message
- [ ] Try accessing `/merchant` as customer — verify redirect

### Product Discovery (Shop Page)
- [ ] Load `/shop` — verify products appear
- [ ] Search for "headphones" — verify relevant results
- [ ] Filter by category "Laptops"
- [ ] Sort by "Price: Low to High"
- [ ] Verify product cards show name, price, rating, image
- [ ] Verify discount percentage displays when `original_price` > `price`
- [ ] Verify broken images show category-aware gradient fallback

### AI Assistant (Chat Page)
- [ ] Open `/chat` as a logged-in customer
- [ ] Type: *"Find gaming headphones under ₹5,000"*
- [ ] Verify products are returned with explanations
- [ ] Type: *"recommend a laptop for programming"*
- [ ] Verify intent is `product_search` / `recommendation` (not misclassified)
- [ ] Verify suggested follow-up prompts appear
- [ ] Click a suggested prompt — verify it populates the input
- [ ] Type: *"add to cart"* — verify cart update notification

### Cart
- [ ] Add a product from Shop page — verify cart icon updates
- [ ] Open `/cart` — verify item appears with correct price
- [ ] Update quantity — verify total recalculates
- [ ] Remove an item — verify cart updates
- [ ] Proceed to Checkout — verify checkout form appears

### Checkout & Payment
- [ ] Place order from cart — verify order is created
- [ ] Confirm demo payment — verify success message
- [ ] Check order history at `/orders` — verify order appears
- [ ] Open order detail at `/orders/{id}` — verify items and payment status
- [ ] *Optional:* Test payment failure by triggering simulate_failure

### Merchant Dashboard
- [ ] Login as merchant and open `/merchant`
- [ ] Verify analytics metrics load (revenue, orders, customers)
- [ ] Verify revenue area chart renders
- [ ] Refresh data with the refresh button — verify loading state
- [ ] Open `/merchant/products` — verify product table loads
- [ ] Create a new product — verify it appears in the list
- [ ] Edit a product — verify changes save
- [ ] Open `/merchant/orders` — verify orders are listed

### Admin
- [ ] Login as admin and open `/admin`
- [ ] Verify system health components are shown
- [ ] Verify audit log entries appear at `/api/v1/audit` (via Swagger)

### API (Swagger UI)
- [ ] Open `http://127.0.0.1:8000/docs`
- [ ] Authorize with JWT token
- [ ] Test `GET /api/v1/products?q=headphone`
- [ ] Test `POST /api/v1/assistant/chat`
- [ ] Test `GET /health`

---

## Troubleshooting

### ❌ `AxiosError: Network Error` on any frontend action

**Root Cause:** Node 18+ resolves `localhost` to `::1` (IPv6). Uvicorn binds to `127.0.0.1` (IPv4). The connection is refused because the ports don't match.

**Fix:**
```bash
# Create or edit frontend/.env.local
echo "NEXT_PUBLIC_API_URL=http://127.0.0.1:8000" > frontend/.env.local
```
Then restart the frontend: `Ctrl+C` → `npm run dev`

---

### ❌ Backend shows `Cannot connect to database`

**Fix (SQLite Dev):** Ensure you ran `alembic upgrade head` from the `backend/` directory with the venv active. The file `backend/paypilot.db` should be created.

**Fix (PostgreSQL):** Ensure Docker PostgreSQL is running:
```bash
docker compose ps   # Check db service is "healthy"
docker compose up -d db
```

---

### ❌ `ModuleNotFoundError` or import errors

**Fix:** Ensure your virtual environment is activated:
```powershell
# Windows
.\venv\Scripts\Activate.ps1
```
```bash
# macOS/Linux
source venv/bin/activate
```
Then: `pip install -r requirements.txt`

---

### ❌ `alembic: command not found`

**Fix:** Alembic is a Python package, run it as a module:
```bash
python -m alembic upgrade head
```

---

### ❌ AI Chat returns "I encountered an issue. Please ensure the backend is running"

This error means the frontend cannot reach the backend at all.

**Check:**
1. Is the backend running? Run `curl http://127.0.0.1:8000/health` in a terminal.
2. Is `frontend/.env.local` set to `NEXT_PUBLIC_API_URL=http://127.0.0.1:8000`?
3. Did you restart `npm run dev` after creating `.env.local`?

---

### ❌ CORS errors in browser console

**Fix:** Edit `backend/.env` and ensure:
```env
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```
No trailing slashes. Restart the backend after changes.

---

### ❌ Port 8000 or 3000 already in use

**Fix (Windows PowerShell):**
```powershell
# Find and kill process on port 8000
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

**Fix (macOS/Linux):**
```bash
lsof -ti:8000 | xargs kill -9
lsof -ti:3000 | xargs kill -9
```

---

### ❌ Seed script fails with duplicate key errors

This means the database is already seeded. This is safe — re-running seed with existing data will conflict on unique constraints (email, session_id). 

**Fix:** Either ignore the errors (data is already there) or reset the database:
```bash
# Development (SQLite) — delete and recreate
rm backend/paypilot.db
alembic upgrade head
python -m database.seed.seed
```

---

### ❌ Missing product images

If images appear broken, the Unsplash CDN URLs may be temporarily unavailable, or the database was seeded before the image URLs were added.

**Fix:** The UI automatically falls back to a category-aware gradient with a Lucide icon (e.g., pink gradient + headphone icon for Headphones). No action required. If you want to re-seed images:
```bash
cd backend
python update_images.py
```

---

### ❌ OpenAI API errors or slow responses

**Fix:** Switch to mock mode, which is always instant and doesn't require API credits:
```env
# In backend/.env
AI_PROVIDER=mock
```
Restart the backend.

---

### ❌ `npm install` fails with dependency errors

**Fix:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

---

## Security Considerations

- **JWT Tokens:** Access tokens expire in 15 minutes. Refresh tokens expire in 7 days. Tokens are stored in browser localStorage.
- **Password Hashing:** All passwords are hashed with bcrypt via `passlib[bcrypt]` before storage. Plain-text passwords are never stored.
- **CORS:** Origins are explicitly allowlisted via `ALLOWED_ORIGINS`. No wildcard origins in production.
- **Financial Gating:** The AI cannot execute checkout or payment actions without passing through `REQUIRE_CONFIRMATION` state and an authenticated REST API call.
- **Payment Signatures:** Razorpay payment signatures are verified using HMAC-SHA256 with constant-time comparison to prevent timing attacks.
- **Idempotency:** Order creation uses unique `idempotency_key` constraints to prevent duplicate charges on network retries.
- **Rate Limiting:** Login (10/min), Register (5/min), Chat (30/min), Payment (10/min).
- **Audit Logging:** Every sensitive action is logged to `audit_logs` with user ID, action type, entity reference, and timestamp.
- **Soft Deletes:** Products are deactivated (`is_active = False`) rather than hard-deleted to preserve order history integrity.
- **Environment Secrets:** All secrets are loaded from `.env` files which are in `.gitignore`. No secrets are hardcoded.

> ⚠️ **Never commit `.env` or `.env.local` files containing real secrets, API keys, or payment credentials.**

---

## Current Limitations

- **Automated tests:** The `pytest` structure is in place, but individual test cases are not yet implemented. Manual testing is the primary verification method.
- **Demo payments only:** The default payment mode is simulated. No real money moves. Razorpay is supported but requires test credentials.
- **Mock AI by default:** The default AI provider uses rule-based regex matching. Complex natural language understanding requires an OpenAI API key.
- **Seeded product catalog:** The product catalog is populated by a seed script with realistic demo data — not a real inventory system.
- **AI revenue attribution:** Upsell/cross-sell revenue metrics in the merchant dashboard are proportional demo calculations, not live attribution from the `Recommendation` table.
- **SQLite for development:** SQLite does not support all PostgreSQL features. Migration to PostgreSQL is required for production scale.
- **No real-time features:** There are no WebSockets for real-time inventory updates or notifications.

---

## Future Enhancements

The following improvements are identified as valuable future work:

- **Automated test suite:** Fill in `tests/unit/` and `tests/integration/` with comprehensive pytest coverage.
- **Live recommendation attribution:** Wire `Recommendation.added_to_cart_at` and `purchased_at` to track true upsell/cross-sell revenue.
- **Vector database integration:** Replace TF-IDF with Pinecone, Weaviate, or pgvector for scalable semantic search.
- **Advanced collaborative filtering:** Recommend products based on what similar users purchased.
- **Real-time inventory:** WebSocket push for stock updates during checkout countdown.
- **Multi-agent architecture:** Separate Discovery Agent and Checkout Agent for better separation of concerns.
- **A/B testing:** Multi-armed bandit algorithm for recommendation strategy testing.
- **Voice commerce:** Speech-to-text input for the AI chat interface.
- **Multilingual support:** Extend intent classification to support Hindi and other Indian languages.
- **Mobile application:** React Native app using the same FastAPI backend.
- **Production deployment:** Kubernetes manifests, CI/CD pipeline, centralized logging.
- **Fraud detection:** Risk scoring on orders before payment authorization.

---

## Use Cases

### Use Case 1 — Natural Language Product Discovery

**Customer:** *"I need wireless headphones for gaming under ₹5,000"*

PayPilot AI:
1. Classifies intent as `product_search`
2. Extracts: `{category: "Headphones", budget_max: 5000, use_case: "gaming"}`
3. Searches catalog for active, in-stock headphones ≤ ₹5,000
4. Scores results: intent_match (1.0) + budget_fit (0.95) + rating_score (0.9)...
5. Returns: *"Here are the top gaming headphones under ₹5,000. Sony WH-CH520 ₹4,499 • Within your budget of ₹5,000 • Matches your gaming use case • Highly rated: 4.4★ from 2,100 reviews"*

---

### Use Case 2 — Intelligent Upselling

**Customer** adds a ₹24,990 headphone to cart.

PayPilot AI surfaces: *"You might also like: Sony WH-1000XM5 at ₹27,490 — Premium option with better specs — ₹2,500 more than your selection."*

This increases Average Order Value without being pushy — the upsell ceiling is capped at 25% above the original price.

---

### Use Case 3 — Cross-Selling

**Customer** adds a Laptop to cart.

PayPilot AI suggests via `CROSS_SELL_AFFINITIES`:
- Wireless Mouse (Laptop Accessories)
- Laptop Backpack (Bags)
- USB-C Hub (Laptop Accessories)

---

### Use Case 4 — Controlled Checkout

**Customer** types *"checkout"* in chat.

PayPilot AI:
1. Detects `checkout` intent — a `FINANCIAL_ACTION`.
2. Enters `REQUIRE_CONFIRMATION` state.
3. Displays: *"Your cart totals ₹4,499. Shall I proceed to create your order?"*
4. Only after explicit user confirmation does the agent call `POST /api/v1/checkout/create`.
5. Order is created with idempotency key — duplicate submissions are blocked.

---

### Use Case 5 — Payment Failure Recovery

**Customer** triggers a demo payment failure.

PayPilot AI:
1. `_finalize_payment_failure()` is called atomically.
2. `Payment.status` → `failed`, `failure_reason` → `"Payment declined by bank (Demo Mode)"`.
3. `Order.status` → `payment_failed` (NOT `paid`).
4. Inventory reservation is released — stock is returned.
5. `payment_failed` audit log is written.
6. User is shown the failure reason and can safely retry.

---

## FAQ

**What is PayPilot AI?**
A full-stack, production-style AI commerce platform where an autonomous agent assists customers through the entire shopping journey, from natural language product discovery to secure, policy-validated checkout.

**What problem does PayPilot AI solve?**
Traditional e-commerce search is keyword-dependent and passive. PayPilot AI introduces an AI agent that understands intent, scores recommendations, manages upselling, and enforces financial safety — making shopping more intelligent for customers and more profitable for merchants.

**Why was this project built?**
To demonstrate a practical, secure implementation of agentic commerce: an AI that takes actions (cart, checkout) within strict safety boundaries rather than just answering questions.

**Who can use this platform?**
Customers, merchants, and administrators — each with role-specific views and access levels enforced by JWT RBAC.

**How does the AI assistant work?**
Messages go through an 11-state finite state machine: intent classification → entity extraction → tool selection → tool execution → (optional financial confirmation) → response generation → audit.

**How does the recommendation engine work?**
It computes a weighted score: `intent_match (30%) + semantic_similarity (25%) + budget_fit (20%) + rating_score (15%) + popularity_score (10%)`. Every result includes a human-readable explanation.

**How does the system perform upselling?**
When a product is selected, the engine queries for items in the same category with `price > current` and `price ≤ current × 1.25`. This surfaces genuinely better options at a realistic price step.

**What is cross-selling?**
Suggesting complementary products using category affinity maps (e.g., Laptops → Laptop Accessories, Mice, Keyboards).

**How does checkout work?**
Cart → `POST /api/v1/checkout/create` (validates stock, reserves inventory, creates order, creates payment intent) → user confirms payment → `POST /api/v1/payments/verify-demo` → atomic success/failure finalization.

**How are financial actions controlled?**
The `FINANCIAL_ACTIONS = {"checkout", "create_payment", "apply_discount"}` constant forces the agent into `REQUIRE_CONFIRMATION` state before any payment-related action. Users must explicitly approve.

**How does payment integration work?**
Demo mode: simulated payment IDs, no external calls. Razorpay mode: real SDK integration with HMAC-SHA256 signature verification.

**What happens if payment fails?**
`_finalize_payment_failure()` is called atomically: payment marked `failed`, inventory released, order set to `payment_failed`, audit record written. The order is never incorrectly marked `paid`.

**What is demo mode?**
The default configuration. Uses mock AI (regex-based) and simulated payments. No API keys required. Everything works out of the box.

**Where is the database stored?**
Development: `backend/paypilot.db` (SQLite file). Production: PostgreSQL container or managed service.

**Where is the backend running?**
`http://127.0.0.1:8000` — FastAPI with uvicorn.

**Where is the frontend running?**
`http://localhost:3000` — Next.js dev server.

**Where can I access API documentation?**
`http://127.0.0.1:8000/docs` (Swagger UI) or `http://127.0.0.1:8000/redoc`.

**How do I configure AI credentials?**
Set `AI_PROVIDER=openai` and `OPENAI_API_KEY=sk-...` in `backend/.env`. Restart the backend.

**How do I configure payment credentials?**
Set `PAYMENT_PROVIDER=razorpay`, `RAZORPAY_KEY_ID`, and `RAZORPAY_KEY_SECRET` in `backend/.env`. Restart the backend.

**How do I run the project locally?**
See [Installation & Setup (Step-by-Step)](#installation--setup-step-by-step).

**How do I run database migrations?**
```bash
cd backend && alembic upgrade head
```

**How do I seed the database?**
```bash
cd backend && python -m database.seed.seed
```

**How do I run tests?**
```bash
cd backend && pytest tests/ -v
```

**How does the merchant dashboard work?**
It calls `/api/v1/analytics/overview` and `/api/v1/analytics/revenue` and displays the data in metric cards and Recharts charts. Only accessible to `merchant` and `admin` roles.

**How does the project maintain auditability?**
Every sensitive action writes to the `audit_logs` table via SQLAlchemy. Records are immutable and include user ID, action type, entity reference, details, IP address, and timestamp.

**What technologies are used?**
See [Technology Stack](#technology-stack).

**Is the project production-ready?**
It is "production-style" in architecture, but requires: PostgreSQL (not SQLite), secure 64+ character secrets, real API keys if needed, and a proper deployment environment (e.g., containers with health checks, a reverse proxy).

**What are the current limitations?**
See [Current Limitations](#current-limitations).

**What can be added in the future?**
See [Future Enhancements](#future-enhancements).

---

## Recommended Demo Flow

A 5–10 minute walkthrough to showcase the full platform:

1. **Open** `http://localhost:3000` — show the landing page and feature overview.
2. **Log in** as `customer@paypilot.demo` / `Demo@123`.
3. **Browse Shop** (`/shop`) — show the product catalog, search, and filters.
4. **Open AI Chat** (`/chat`) — type: *"I need gaming headphones under ₹5,000"*
5. **Show the AI response** — point out: products returned, recommendation reasons, suggested prompts.
6. **Click "Add to Cart"** from the chat — show the cart update notification.
7. **Show cross-sell/upsell** — if surfaced, point out the premium alternative suggestion.
8. **Open Cart** (`/cart`) — show items, totals, and the checkout button.
9. **Proceed to Checkout** — show order creation and payment form.
10. **Complete Demo Payment** — click "Pay Now" in demo mode.
11. **Show Order Confirmation** and navigate to `/orders`.
12. **Log out** and log in as `merchant@paypilot.demo` / `Demo@123`.
13. **Open Merchant Dashboard** (`/merchant`) — show revenue, orders, AI-assisted metrics, charts.
14. **Open Agent Activity** — show the `AgentAction` telemetry from the customer's chat.
15. **Open Swagger UI** at `http://127.0.0.1:8000/docs` — show the auto-generated API documentation.
16. **Optional:** Open `/admin` (as `admin@paypilot.demo`) — show system health and audit log.

---

## Project Objectives

1. Build an AI-powered customer intent understanding system using an explicit state machine.
2. Provide intelligent product discovery via natural language queries.
3. Develop personalized, multi-factor scored recommendations.
4. Implement explainable upselling and cross-selling with category affinity maps.
5. Enable conversational commerce integrated with real cart and order APIs.
6. Provide secure, policy-validated checkout workflows.
7. Integrate test/demo payment processing with graceful failure handling.
8. Implement bounded financial actions — the AI cannot charge money without user confirmation.
9. Maintain an immutable, auditable agent activity trail.
10. Provide merchant analytics and growth insights with real-time charts.
11. Handle payment failures atomically without corrupting order state.
12. Build a modular, extensible full-stack architecture suitable for team development.

---

## Project Highlights

⭐ **AI agent with explicit 11-state finite state machine** — deterministic, auditable, safe  
🛒 **Conversational shopping** — full cart and checkout via natural language  
🎯 **5-factor weighted recommendation engine** — intent + budget + rating + popularity + semantic  
📈 **Merchant analytics dashboard** — real-time revenue, AI conversions, Recharts visualizations  
💡 **Explainable recommendations** — every suggestion includes a human-readable reason  
💳 **Controlled payment workflow** — financial actions require user confirmation and policy validation  
🔐 **JWT RBAC + bcrypt + CORS** — layered security throughout  
🧾 **Immutable audit trail** — every system event logged with user, entity, and timestamp  
📊 **Upsell & cross-sell engine** — category affinity maps + price-range logic  
🐳 **Dockerized full-stack** — one command to run PostgreSQL + FastAPI + Next.js  
🔄 **Graceful failure recovery** — payment failures release inventory and preserve order integrity  
🚀 **100% offline demo mode** — works immediately after clone, no API keys needed  

---

## Development Workflow

```bash
# 1. Fork and clone the repository
git clone https://github.com/yourusername/paypilot-ai.git
cd paypilot-ai

# 2. Create a feature branch
git checkout -b feature/your-feature-name

# 3. Make your changes and test locally (see Installation & Setup)

# 4. Run linting (backend)
cd backend
ruff check app/
ruff format app/

# 5. Commit your changes
git status
git add .
git commit -m "feat: describe your change clearly"

# 6. Push to your fork
git push origin feature/your-feature-name

# 7. Open a Pull Request
```

---

## Author

**Anand D**

> Full-stack AI/ML developer focused on building intelligent, explainable, and practical software systems.

---

## License

> License information can be added according to the project's distribution requirements.
