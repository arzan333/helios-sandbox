"""In-memory order store seeded from data/orders.json.

No database. The training scenarios never need one, and a database would add
setup failure modes that teach nothing.
"""

import json
import threading
from pathlib import Path

from .models import NewOrder, Order

SEED_FILE = Path(__file__).resolve().parents[1] / "data" / "orders.json"


class OrderStore:
    def __init__(self, seed_file: Path = SEED_FILE) -> None:
        self._lock = threading.Lock()
        self._orders: dict[str, Order] = {}
        self._seed_file = seed_file
        self.reload()

    def reload(self) -> None:
        """Load the seed file, discarding anything created at runtime."""
        with self._lock:
            self._orders.clear()
            raw = json.loads(self._seed_file.read_text(encoding="utf-8"))
            for item in raw:
                order = Order(**item)
                self._orders[order.order_id] = order

    def list_orders(self, status: str | None = None) -> list[Order]:
        with self._lock:
            orders = list(self._orders.values())
        if status:
            orders = [o for o in orders if o.status == status]
        return sorted(orders, key=lambda o: o.order_id)

    def get(self, order_id: str) -> Order | None:
        with self._lock:
            return self._orders.get(order_id)

    def add(self, payload: NewOrder) -> Order:
        with self._lock:
            next_number = 1001 + len(self._orders)
            while f"ORD-{next_number}" in self._orders:
                next_number += 1
            order = Order(
                order_id=f"ORD-{next_number}",
                customer=payload.customer,
                currency=payload.currency,
                status="pending",
                lines=payload.lines,
            )
            self._orders[order.order_id] = order
            return order
