You are a highly experienced engineering manager and defect triage lead with a strong background in both software development and support operations. You are excellent at reading between the lines of a vague bug report, working out what is actually going on, and deciding who should do what next. You are calm, structured and decisive.

We have a defect to triage in the Helios Group delivery backlog. Here is the full ticket exactly as exported:

{
  "key": "HEL-018",
  "summary": "Invoice total ignores line level discount",
  "type": "Bug",
  "status": "Triage",
  "priority": "high",
  "reporter": "Helios delivery team",
  "assignee": "unassigned",
  "components": [
    "Billing",
    "OrderCore"
  ],
  "labels": [
    "defect"
  ],
  "created": "2025-12-30",
  "description": "Finance report that when a line has a negotiated price the invoice still shows the list total. Reproduced on ORD-1003. Unclear whether Billing or OrderCore is at fault.",
  "acceptance_criteria": [],
  "linked_documents": [],
  "notes": "No acceptance criteria written."
}

Helios sells cleaning and household products to wholesale customers. Orders live in OrderCore (Python), invoices are calculated by Billing (Java), and the Shop (React) displays both. Money is always in whole pence. Here is the entity map for the estate, which tells you which files each business concept touches, so that you can work out which system is at fault:

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

To triage this properly, please read every ticket in helios-backlog/ so that you know whether this defect is related to anything else that is open or planned, and please read data/helios-tickets.csv to see how often this defect title has been raised before and what happened to those tickets, and please read docs/process/defect-triage.md so that your triage follows the current process, and please read docs/helios-landscape.md for the roles, and please read apps/ordercore/app/models.py and apps/billing/src/main/java/com/helios/billing/InvoiceCalculator.java so that you can check whether a discount field exists anywhere in the code, and please read docs/specs/ordercore-fsd.txt for what the specification says about discounts and line prices.

Then please write a triage report with the following sections. One: a restatement of the problem in your own words. Two: your analysis of what is actually happening, including which system is responsible, with evidence from the files you read. Three: a classification of the ticket as a defect, a missing requirement, a data problem or a usage problem, with a justification. Four: a severity and priority recommendation, with reasoning, considering the business impact on Finance. Five: the questions that need to go back to the reporter before anyone starts work, phrased as you would send them. Six: a recommended owner role from the landscape RACI and a recommended next action. Seven: a note of any related tickets. Eight: a summary suitable for pasting into the ticket as a comment.

Please be careful not to jump to conclusions. Please consider all possibilities. Please explain your reasoning at each step so that the team can follow it. If you are uncertain, please say so, and give your best estimate anyway with a confidence level. Please make sure the severity is justified and not just a guess.

Write the report to week2/out/defect-triage-v0.md and then in the chat give me the classification, the owner and the next action, and also repeat the questions for the reporter, and also give a brief overview of what you found in the related tickets.
