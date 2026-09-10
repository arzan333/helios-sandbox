---
owner: Developer
version: 1.0
effective_date: 2026-03-02
review_date: 2026-09-02
---

# Tool chain design - <your workflow>

Fill this in as you go. Every figure must be traceable to a file or a run; where
one is not, write "assumed" beside it and say why.

## 1. Task type at each AI step

| # | Step | Task type | Why that type |
|---|---|---|---|
| | | | |

Task types: classify, extract, synthesize, generate, reason.

## 2. Tier selection

| # | Step | Tier | Quality need | Latency need | Monthly volume | Why this tier |
|---|---|---|---|---|---|---|
| | | | | | | |

No rationale, no assignment. A tier chosen because it is the one you always use is
not a rationale.

## 3. Does this step need AI at all?

| # | Step | Verdict | Deterministic alternative | Kept or removed |
|---|---|---|---|---|
| | | | | |

At least one step must fail this test and be replaced by something named - a
script, a regex, a linter, a static check.

## 4. Fallback per step

| # | Step | If the preferred model is unavailable | If the step fails outright |
|---|---|---|---|
| | | | |

## 5. Anti-pattern audit

| # | Anti-pattern | Present? | What you will do instead |
|---|---|---|---|
| 1 | Context dumping | | |
| 2 | Over-prompting | | |
| 3 | Retry without change | | |
| 4 | Duplicate derivation | | |
| 5 | Redundant verification | | |
| 6 | Premature chaining | | |

## 6. The numbers

| Figure | Value | Where it came from |
|---|---|---|
| Monthly cost, with retries | | Cost model, Model sheet, total |
| Cost per unit of work | | Monthly cost divided by monthly volume |
| Chain as designed | | Cost model, Chain compare |
| Chain redesigned | | Cost model, Chain compare |
| Steps removed | | Section 3 |

## 7. One sentence

The change I would defend to a finance reviewer, and the number behind it:
