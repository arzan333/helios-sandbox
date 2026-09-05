---
owner: Architect
version: 1.0
effective_date: 2026-03-02
review_date: 2026-09-02
---

# Rubric - impact note for HEL-207

Score the output file, not the chat. Five criteria, 0 to 5 each, maximum 25.
5 = fully met, 3 = mostly, 0 = absent. Whole numbers. Score what is written;
give no credit for what the model probably meant.

| # | Criterion | 5 looks like | 3 looks like | 0 looks like |
|---|---|---|---|---|
| 1 | All three places named | Java (InvoiceCalculator, BillingServer, Json), Python (models.py, billing_client.py, main.py response), React (OrderDetail.jsx) | Two of the three languages | One |
| 2 | Contract change field by field | Request gains discount_percent / discountPercent; response gains a discount amount in pence in both conventions | Named in one convention only | Contract not described |
| 3 | Fallback path | Says _local_invoice must apply the same discount or a Billing outage silently ignores it, and the tax rate duplication is a second instance of the same risk | Mentions the fallback without the consequence | Fallback not mentioned |
| 4 | Rules from the ticket | Tax on the discounted subtotal; 0 to 50 inclusive; outside the range is 422; no discount means unchanged behaviour | One rule missing or wrong | Rules not stated |
| 5 | Approval and tests | Architect, cross-system change approval per the RACI; tests named by file on both sides (test_orders.py, InvoiceCalculatorTest.java, BillingServerTest.java) | Approval right, tests vague | No approval, or a role not in the RACI |

## Answer key for the scorer

data/entity-map.md gives the three-place rule and the fallback and tax-rate
warnings. The ticket gives the six acceptance criteria. An effort estimate is not
scored; a note that invents a Sprints board or a database scores 0 on criterion 5.
