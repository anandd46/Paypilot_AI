"""Razorpay payment service — Test Mode only."""
from __future__ import annotations

import hashlib
import hmac
from typing import Any

import razorpay  # type: ignore[import-untyped]

from app.core.config import get_settings

settings = get_settings()


class RazorpayService:
    """Razorpay Standard Checkout integration — Test Mode."""

    def __init__(self) -> None:
        self._client = razorpay.Client(
            auth=(settings.razorpay_key_id, settings.razorpay_key_secret)
        )

    def create_order(self, amount_inr: float, currency: str = "INR", notes: dict[str, Any] | None = None) -> dict[str, Any]:
        """Create a Razorpay order. Amount is in paise (INR × 100)."""
        amount_paise = int(amount_inr * 100)
        order_data: dict[str, Any] = {
            "amount": amount_paise,
            "currency": currency,
            "payment_capture": 1,
            "notes": notes or {},
        }
        order: dict[str, Any] = self._client.order.create(data=order_data)
        return order

    def verify_payment_signature(
        self,
        razorpay_order_id: str,
        razorpay_payment_id: str,
        razorpay_signature: str,
    ) -> bool:
        """Verify payment signature using HMAC-SHA256 (timing-safe)."""
        expected_signature = hmac.new(
            settings.razorpay_key_secret.encode("utf-8"),
            f"{razorpay_order_id}|{razorpay_payment_id}".encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(expected_signature, razorpay_signature)

    def verify_webhook_signature(self, body: bytes, signature: str) -> bool:
        """Verify Razorpay webhook signature."""
        expected = hmac.new(
            settings.razorpay_webhook_secret.encode("utf-8"),
            body,
            hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(expected, signature)

    def fetch_payment(self, payment_id: str) -> dict[str, Any]:
        payment: dict[str, Any] = self._client.payment.fetch(payment_id)
        return payment
