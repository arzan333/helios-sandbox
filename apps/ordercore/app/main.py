"""OrderCore - the Helios order management API.

Run locally:
    uvicorn app.main:app --reload --port 8080
"""


from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from .billing_client import request_invoice
from .models import Invoice, NewOrder, Order
from .store import OrderStore

app = FastAPI(
    title="Helios OrderCore",
    description="Order management for Helios Group. Training environment.",
    version="1.0.0",
)

# The Shop front end runs on a different port during labs.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

store = OrderStore()


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "ordercore", "orders": len(store.list_orders())}


@app.get("/orders", response_model=list[Order])
def list_orders(status: str | None = Query(default=None)) -> list[Order]:
    return store.list_orders(status=status)


@app.get("/orders/{order_id}", response_model=Order)
def get_order(order_id: str) -> Order:
    order = store.get(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail=f"Order {order_id} not found")
    return order


@app.post("/orders", response_model=Order, status_code=201)
def create_order(payload: NewOrder) -> Order:
    return store.add(payload)


@app.get("/orders/{order_id}/invoice", response_model=Invoice)
def get_invoice(order_id: str) -> Invoice:
    order = store.get(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail=f"Order {order_id} not found")
    return request_invoice(order)
