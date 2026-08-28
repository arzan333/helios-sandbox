"""Client for the Billing service (Java).

This is the only cross-language call in Helios. It is deliberately visible:
Week 3 asks participants to change an API contract that crosses this boundary,
and the failure mode when only one side changes is the point of the exercise.

If Billing is not running, callers get a clearly marked local fallback rather
than an exception, so the Shop UI still renders during a lab.
"""

import os

import httpx

from .models import Invoice, Order

BILLING_URL = os.environ.get("HELIOS_BILLING_URL", "http://localhost:8081")
TIMEOUT_SECONDS = 3.0
TAX_RATE_PERCENT = 20


def _local_invoice(order: Order, note: str) -> Invoice:
    """Fallback used when Billing cannot be reached."""
    subtotal = order.subtotal_pence
    tax = round(subtotal * TAX_RATE_PERCENT / 100)
    return Invoice(
        order_id=order.order_id,
        currency=order.currency,
        subtotal_pence=subtotal,
        tax_pence=tax,
        total_pence=subtotal + tax,
        source="fallback",
        note=note,
    )


def request_invoice(order: Order, client: httpx.Client | None = None) -> Invoice:
    payload = {
        "orderId": order.order_id,
        "currency": order.currency,
        "lines": [
            {
                "sku": line.sku,
                "quantity": line.quantity,
                "unitPricePence": line.unit_price_pence,
            }
            for line in order.lines
        ],
    }

    owns_client = client is None
    if client is None:
        client = httpx.Client(timeout=TIMEOUT_SECONDS)

    try:
        response = client.post(f"{BILLING_URL}/invoice", json=payload)
        response.raise_for_status()
        body = response.json()
        return Invoice(
            order_id=body["orderId"],
            currency=body["currency"],
            subtotal_pence=body["subtotalPence"],
            tax_pence=body["taxPence"],
            total_pence=body["totalPence"],
            source="billing",
        )
    except (httpx.HTTPError, KeyError, ValueError) as exc:
        return _local_invoice(order, f"Billing unavailable ({type(exc).__name__}); calculated locally")
    finally:
        if owns_client:
            client.close()
