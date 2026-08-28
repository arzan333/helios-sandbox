---
owner: Developer
version: 1.0
effective_date: 2026-02-01
review_date: 2026-08-01
---

# Low-level design gate rubric

Used before a change is accepted. Score each criterion 0, 1 or 2.

**Pass threshold: 8 of 10, and no criterion at 0.**

| # | Criterion | 0 | 1 | 2 | Evidence required |
|---|---|---|---|---|---|
| 1 | Contracts | Field names or types changed on one side only | Both sides changed, no test | Both sides changed and a contract test covers it | The contract test |
| 2 | Error handling | Failure path undefined | Handled, message unclear | Handled with a specific status and message | The rejecting test |
| 3 | Tests | None added | Happy path only | Happy path plus at least one boundary and one rejection | Test names |
| 4 | Security and validation | Input unvalidated | Validated loosely | Range or format enforced and tested | The validation test |
| 5 | Standards conformance | Linter fails | Linter passes, house rules broken | Linter passes and house rules met | Lint output, `CLAUDE.md` rule |

## House rules this rubric checks

- Money is a whole number of pence, never a float.
- No new runtime dependency in Billing.
- Tests sit beside the code they cover.
- One concern per commit.

## How to use it

Score your own change before asking anyone else to look at it. Reworking your own
work against a rubric is the point of the exercise, not an overhead on it.
