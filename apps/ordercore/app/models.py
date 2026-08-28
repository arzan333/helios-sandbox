"""Data shapes for OrderCore.

Deliberately small. One order, one or more lines, no inheritance, no ORM.
"""

from typing import Literal

from pydantic import BaseModel, Field

OrderStatus = Literal["pending", "confirmed", "shipped", "cancelled"]


class OrderLine(BaseModel):
    sku: str = Field(..., min_length=1)
    description: str = ""
    quantity: int = Field(..., gt=0)
    unit_price_pence: int = Field(..., ge=0)

    @property
    def line_total_pence(self) -> int:
        return self.quantity * self.unit_price_pence


class Order(BaseModel):
    order_id: str
    customer: str
    status: OrderStatus = "pending"
    currency: str = "GBP"
    lines: list[OrderLine]

    @property
    def subtotal_pence(self) -> int:
        return sum(line.line_total_pence for line in self.lines)


class NewOrder(BaseModel):
    """Payload for POST /orders. The service allocates the order_id."""

    customer: str = Field(..., min_length=1)
    currency: str = "GBP"
    lines: list[OrderLine] = Field(..., min_length=1)


class Invoice(BaseModel):
    """Returned by the Billing service. Money is always in pence."""

    order_id: str
    currency: str
    subtotal_pence: int
    tax_pence: int
    total_pence: int
    source: str = "billing"
    note: str | None = None
