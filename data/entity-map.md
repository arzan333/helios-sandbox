---
owner: Architect
version: 1.0
effective_date: 2026-01-05
review_date: 2026-07-05
source_system: Helios delivery
---

# Entity map

Which files and services each business concept touches. Use this to write an impact
note before changing anything. It is maintained by hand and is occasionally stale,
which is itself worth checking.

## Order

| Concern | Location |
|---|---|
| Shape and validation | `apps/ordercore/app/models.py` |
| Storage and seeding | `apps/ordercore/app/store.py`, `apps/ordercore/data/orders.json` |
| HTTP surface | `apps/ordercore/app/main.py` |
| Tests | `apps/ordercore/tests/test_orders.py` |
| Front end display | `apps/shop/src/OrderList.jsx`, `apps/shop/src/OrderDetail.jsx` |

## Invoice and pricing

| Concern | Location |
|---|---|
| Calculation | `apps/billing/src/main/java/com/helios/billing/InvoiceCalculator.java` |
| HTTP surface | `apps/billing/src/main/java/com/helios/billing/BillingServer.java` |
| Request and response parsing | `apps/billing/src/main/java/com/helios/billing/Json.java` |
| Caller | `apps/ordercore/app/billing_client.py` |
| Contract tests | `apps/billing/src/test/java/com/helios/billing/BillingServerTest.java` |
| Front end totals | `apps/shop/src/OrderDetail.jsx` |

## Reporting

| Concern | Location |
|---|---|
| Stage and order reports | `apps/insight/report.py` |
| Delivery dataset | `data/helios-tickets.csv` |

## Cross-system boundaries

There is exactly one cross-language call in Helios:

```
Shop (React)  ->  OrderCore (Python)  ->  Billing (Java)
                  /orders/{id}/invoice     POST /invoice
```

The field names differ either side of that call. OrderCore uses `snake_case`,
Billing uses `camelCase`, and the translation lives in `billing_client.py`.
Any change to invoice fields must be made in three places or it will half-work:

1. `InvoiceCalculator` and `BillingServer` in Java
2. `billing_client.py` and `models.py` in Python
3. `OrderDetail.jsx` in React

If Billing is unreachable, OrderCore calculates locally and marks the invoice
`source: "fallback"`. That is deliberate. It keeps a lab running when a service is
down, and it also means a broken contract can look like it is working. Check the
`source` field before trusting a total.

The tax rate is written down twice: `TAX_RATE_PERCENT` in `InvoiceCalculator.java`
and again in the fallback inside `billing_client.py`. Change one and the other
keeps quietly returning the old answer whenever Billing is down. Any pricing
change has to touch both.
