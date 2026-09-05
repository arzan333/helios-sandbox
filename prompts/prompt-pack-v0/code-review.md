You are an extremely experienced principal software engineer and code reviewer with decades of experience reviewing Python in production financial systems. You are thorough, rigorous, fair and detail-oriented, and you never let a bug through. You always explain your reasoning so that junior developers can learn from your reviews.

I would like you to perform a complete and comprehensive code review of one file in the Helios OrderCore service. Helios Group is a mid-size consumer products company and OrderCore is its order management API, written in Python with FastAPI. The file in question is the Billing client, which is the only cross-language call in the whole Helios estate (Python calling a Java service), and therefore it is very important that it is correct.

To make sure you review against the right standards, here is the full contents of the repository's CLAUDE.md, which contains the coding standards you must apply:

--- CLAUDE.md begins ---
# CLAUDE.md

Helios Group sandbox. A synthetic training environment for the Claude Code
Capability Program. Everything here is fictional.

## What is in here

- `apps/` - four small services. Shop (React), OrderCore (Python), Billing (Java), Insight (Python scripts).
- `data/` - the delivery dataset and the entity map.
- `docs/` - process narratives and design documents.
- `helios-backlog/` - tickets in Jira export shape.
- `labs/` - self-paced lab books, one per week. Open them in a browser.
- `rubrics/` - design review rubrics.
- `templates/` - canvases and checklists participants fill in.

## Where authority lives

- The landscape and role RACI: `docs/helios-landscape.md`
- What a change touches: `data/entity-map.md`
- How the current process runs: `docs/process/`
- Ticket detail: `helios-backlog/<KEY>.json`

If those disagree with something in a lab book, the lab book is the one being
followed today, but say so rather than quietly picking one.

## Standards

- Money is always a whole number of pence. Never a float. Format only at the UI edge.
- Python: 4-space indent, type hints on function signatures, `ruff` clean.
- Java: 4-space indent, no new runtime dependencies in Billing.
- React: function components, hooks, no class components.
- Tests live beside the code they cover and must pass before a commit.
- Commit locally only. Nothing in this programme is ever pushed. A `pre-push` hook in
 `.githooks/` blocks it; never suggest bypassing it with `--no-verify`.

## What not to modify

- `data/helios-tickets.csv` - regenerate it with `scripts/generate_tickets.py` if
 it must change. Editing rows by hand breaks the worked answers.
- `scripts/generate_tickets.py` seed value. Every participant must see identical numbers.
- Other participants' `week1/`-`week4/` folders.

## Running things

```
# OrderCore
cd apps/ordercore && pip install -r requirements.txt && uvicorn app.main:app --port 8080

# Billing (Maven, needs network the first time)
cd apps/billing && mvn -q package && java -jar target/billing-1.0.0.jar

# Billing (no Maven, fully offline - Billing has no runtime dependencies)
cd apps/billing && javac -d out $(find src/main/java -name "*.java") && java -cp out com.helios.billing.BillingServer

# Shop
cd apps/shop && npm install && npm run dev

# Reports
python apps/insight/report.py stages --workflow request_to_release
```

Billing is optional. If it is not running, OrderCore calculates invoices locally
and marks them `source: "fallback"`.

## Working style in this repository

Plan before you generate. Say what you are about to change and which files it
touches before changing them. Keep diffs small and one concern at a time. Run the
tests before saying something is done.
--- CLAUDE.md ends ---

And here is the full source code of the file to review, apps/ordercore/app/billing_client.py, so that you have it in front of you:

--- billing_client.py begins ---
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
--- billing_client.py ends ---

In addition to the pasted file, please also open and read apps/ordercore/app/billing_client.py directly from disk in case the pasted version above is out of date, and please also read every other file under apps/ordercore/app/ and apps/ordercore/tests/ so that you understand the full context in which this file is used, and please also read data/entity-map.md and docs/helios-landscape.md so that you understand the architecture, and the Java side in apps/billing/src/main/java/com/helios/billing/ so that you can check the contract from both ends.

Please review the file for: correctness bugs; security; performance; error handling; code quality; type hints; adherence to the CLAUDE.md standards above; test coverage gaps; anything that could cause a pricing discrepancy between OrderCore and Billing; anything else a world-class reviewer would notice.

For each finding, please give: a severity (Critical, Warning or Suggestion); the line number or function name; a detailed explanation of the problem and why it matters, in a paragraph; the potential impact on the business if it is not fixed; a concrete code example showing the fix; and a note on how to test that the fix works.

After the findings, please write a general assessment of the code in prose, covering its overall design, its strengths and weaknesses, and how it compares to best practice. Then please write a prioritised action plan. Then a summary.

Please be thorough. Please do not miss anything. It is very important that this review is complete, because this file is on the money path. If you are not sure whether something is an issue, include it anyway, because it is better to over-report than to under-report.

Write the full review to week2/out/code-review-v0.md with clear headings, and then in the chat repeat the list of findings with their severities, and explain your overall conclusion.
