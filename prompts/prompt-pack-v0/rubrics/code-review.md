---
owner: Developer
version: 1.0
effective_date: 2026-03-02
review_date: 2026-09-02
---

# Rubric - code review of billing_client.py

Score the output file, not the chat. Five criteria, 0 to 5 each, maximum 25.
5 = fully met, 3 = mostly, 0 = absent. Whole numbers. Score what is written;
give no credit for what the model probably meant.

| # | Criterion | 5 looks like | 3 looks like | 0 looks like |
|---|---|---|---|---|
| 1 | Severity on every finding | Each finding is Critical, Warning or Suggestion, and the severity fits the consequence | Severities present but one or two are clearly wrong for the consequence | No severities, or one severity for everything |
| 2 | Findings are located | Every finding names the function or line it is about | Most do | Findings float free of the code |
| 3 | Catches the duplicated tax rate | Says TAX_RATE_PERCENT lives in both billing_client.py and InvoiceCalculator.java and that changing one silently leaves the fallback wrong | Mentions the constant without the cross-system consequence | Not mentioned |
| 4 | Catches the masked contract failure | Says the except clause (HTTPError, KeyError, ValueError) turns a broken Billing contract into a fallback invoice that looks like success, and that callers must check source | Mentions broad exception handling generically | Not mentioned |
| 5 | No false positives | Nothing invented; does not call round() a float bug (it returns an int here), does not flag things the file does not do | One dubious finding | Two or more findings that are not real |

## Answer key for the scorer

Real findings in this file: the tax rate is defined twice across two languages
(entity map calls this out); the fallback masks contract breaks; there is no retry
and no distinction between a timeout and a bad response; the `note` text leaks an
exception class name to the caller; `client` type hint uses `httpx.Client | None`
which is fine. Anything beyond that list needs evidence from the code.
