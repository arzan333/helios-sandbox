"""Tests for OrderCore.

These are the tests Week 3 asks participants to keep green while they change
the API. Keep them fast and free of network calls.
"""

import pytest
from fastapi.testclient import TestClient

from app import billing_client
from app.main import app, store
from app.models import Order

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_store():
    """Every test starts from the seed file."""
    store.reload()
    yield
    store.reload()


def test_health_reports_seeded_orders():
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["orders"] == 5


def test_list_orders_returns_all_seeded_orders():
    response = client.get("/orders")
    assert response.status_code == 200
    assert len(response.json()) == 5


def test_list_orders_filters_by_status():
    response = client.get("/orders", params={"status": "confirmed"})
    assert response.status_code == 200
    statuses = {order["status"] for order in response.json()}
    assert statuses == {"confirmed"}


def test_get_single_order():
    response = client.get("/orders/ORD-1001")
    assert response.status_code == 200
    body = response.json()
    assert body["customer"] == "Northwind Retail"
    assert len(body["lines"]) == 2


def test_missing_order_returns_404():
    response = client.get("/orders/ORD-9999")
    assert response.status_code == 404


def test_subtotal_is_quantity_times_unit_price():
    order = Order(**client.get("/orders/ORD-1002").json())
    # 100 units at 189 pence
    assert order.subtotal_pence == 18900


def test_create_order_allocates_an_id():
    payload = {
        "customer": "Testing Ltd",
        "lines": [{"sku": "HG-SOAP-250", "quantity": 2, "unit_price_pence": 189}],
    }
    response = client.post("/orders", json=payload)
    assert response.status_code == 201
    body = response.json()
    assert body["order_id"].startswith("ORD-")
    assert body["status"] == "pending"


def test_create_order_rejects_empty_lines():
    response = client.post("/orders", json={"customer": "Testing Ltd", "lines": []})
    assert response.status_code == 422


def test_create_order_rejects_zero_quantity():
    payload = {
        "customer": "Testing Ltd",
        "lines": [{"sku": "HG-SOAP-250", "quantity": 0, "unit_price_pence": 189}],
    }
    assert client.post("/orders", json=payload).status_code == 422


def test_invoice_falls_back_when_billing_is_down(monkeypatch):
    """The fallback must engage when Billing is unreachable.

    The URL is forced to a closed port rather than relying on Billing being
    absent. Week 3 has participants running Billing while they change it, and a
    test that only passes when a service is stopped is worse than no test.
    """
    monkeypatch.setattr(billing_client, "BILLING_URL", "http://127.0.0.1:9")
    response = client.get("/orders/ORD-1002/invoice")
    assert response.status_code == 200
    body = response.json()
    assert body["source"] == "fallback"
    assert body["subtotal_pence"] == 18900
    assert body["tax_pence"] == 3780          # 20 percent
    assert body["total_pence"] == 22680


def test_invoice_for_missing_order_returns_404():
    assert client.get("/orders/ORD-9999/invoice").status_code == 404
