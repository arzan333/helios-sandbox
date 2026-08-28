---
owner: Architect
version: 1.0
effective_date: 2026-02-01
review_date: 2026-08-01
---

# High-level design gate rubric

Used at the design gate, before build starts. Score each criterion 0, 1 or 2.
Evidence must be pointed at, not asserted.

**Pass threshold: 8 of 10, and no criterion at 0.**

| # | Criterion | 0 | 1 | 2 | Evidence required |
|---|---|---|---|---|---|
| 1 | Scope is bounded | No statement of what is out of scope | Implied | Explicit in and out of scope | The out-of-scope list |
| 2 | Integration impact | Downstream systems not mentioned | Named but not assessed | Named, with the effect on each | Entity map reference |
| 3 | Non-functionals | Absent | Mentioned without numbers | Stated with a number or a limit | The stated figure |
| 4 | Alternatives | None | One named, not compared | At least one compared and rejected with a reason | The rejection reason |
| 5 | Risk and ownership | No risks, or no owner | Risks listed without owners | Each risk has an owner and a response | Named role per risk |

## How to use it

Score against the document as written. Do not fill gaps from what you know or
from a conversation you had. If the document does not say it, it scores 0.

A rubric where everything passes first time is too soft. If a real design scores
10 on its first pass, tighten the criteria before you trust it.
