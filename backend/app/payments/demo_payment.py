"""Demo payment provider — same interface as Razorpay, no external calls.

Executes the FULL business logic (order creation, inventory, audit)
just like the real provider, but uses simulated payment IDs.
"""
from __future__ import annotations

import secrets
import uuid
from datetime import UTC, datetime
from typing import Any


class DemoPaymentService:
    """Simulated payment service for demo/development mode."""

    provider_name = "demo"

    def create_order(
        self,
        amount_inr: float,
        currency: str = "INR",
        notes: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Simulate creating a payment order."""
        return {
            "id": f"demo_order_{secrets.token_hex(8)}",
            "amount": int(amount_inr * 100),
            "currency": currency,
            "status": "created",
            "provider": "demo",
            "notes": notes or {},
        }

    def simulate_payment(self, order_id: str, simulate_failure: bool = False) -> dict[str, Any]:
        """Simulate payment success or failure."""
        if simulate_failure:
            return {
                "payment_id": f"demo_pay_{secrets.token_hex(8)}",
                "order_id": order_id,
                "status": "failed",
                "failure_reason": "Payment declined by bank (Demo Mode)",
                "failure_code": "BAD_REQUEST_ERROR",
            }
        return {
            "payment_id": f"demo_pay_{secrets.token_hex(8)}",
            "order_id": order_id,
            "status": "captured",
            "method": "demo_card",
            "captured_at": datetime.now(UTC).isoformat(),
        }

    def verify_payment_signature(
        self,
        razorpay_order_id: str,
        razorpay_payment_id: str,
        razorpay_signature: str,
    ) -> bool:
        """Demo mode: always valid (signature check skipped)."""
        return True

    def verify_webhook_signature(self, body: bytes, signature: str) -> bool:
        """Demo mode: always valid."""
        return True
