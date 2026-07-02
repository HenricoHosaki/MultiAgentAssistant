"""Order service client + helpers.

Orders are a cross-cutting entity: a customer can ask about an order from a delivery,
payment, or product angle. Instead of giving every specialist an order-lookup tool, the
Flow calls this service once (when the question mentions an order number) and injects the
result as shared context — the same cross-cutting pattern used for the guardrail.
"""

import os
import re

import requests

BASE_URL = os.environ.get("MOCK_STORE_URL", "http://localhost:8000/mock")
TIMEOUT = 10

_ORDER_ID_PATTERN = re.compile(r"\b\d{4,6}\b")


def extract_order_id(text: str) -> str | None:
    """Return the first 4-6 digit number in the text, treated as a candidate order id."""
    match = _ORDER_ID_PATTERN.search(text)
    return match.group(0) if match else None


def fetch_order(order_id: str) -> dict | None:
    try:
        resp = requests.get(f"{BASE_URL}/orders/{order_id}", timeout=TIMEOUT)
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException:
        return None


def format_order(order: dict) -> str:
    items = "\n".join(
        f"  - {item['quantity']}x {item['title']} "
        f"(${item['unit_price']:.2f} each = ${item['line_total']:.2f})"
        for item in order["items"]
    )
    tracking = order["tracking_code"] or "not available yet"
    estimated = order["estimated_delivery"] or "not available"
    return (
        f"Order {order['id']}:\n"
        f"- Status: {order['status']}\n"
        f"- Items:\n{items}\n"
        f"- Amount paid: ${order['amount_paid']:.2f}\n"
        f"- Payment method: {order['payment_method']}\n"
        f"- Shipping address: {order['shipping_address']}\n"
        f"- Purchase date: {order['purchase_date']}\n"
        f"- Tracking code: {tracking}\n"
        f"- Estimated delivery: {estimated}"
    )
