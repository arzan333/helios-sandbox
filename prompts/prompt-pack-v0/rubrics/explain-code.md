---
owner: Developer
version: 1.0
effective_date: 2026-03-02
review_date: 2026-09-02
---

# Rubric - explanation of apps/insight/report.py

Score the output file, not the chat. Five criteria, 0 to 5 each, maximum 25.
5 = fully met, 3 = mostly, 0 = absent. Whole numbers. Score what is written;
give no credit for what the model probably meant.

| # | Criterion | 5 looks like | 3 looks like | 0 looks like |
|---|---|---|---|---|
| 1 | Commands are exact | python apps/insight/report.py stages and ... orders; the only option is --workflow; no invented flags | One flag or path slightly wrong | Commands that do not run |
| 2 | Data sources named | Stages report reads data/helios-tickets.csv; orders report calls OrderCore on localhost:8080 and needs httpx | One of the two | Not explained |
| 3 | Median, p90, queue and effort | Explains what median and p90 tell you, and the queue versus effort distinction from docs/process/request-to-release.md | Two of the three | None |
| 4 | Workflow filter | Explains --workflow and lists the five valid values | Explains the flag without the values | Not mentioned |
| 5 | Pitched for a new joiner | No unexplained jargon; a developer who knows Python could run both reports after reading it | Some jargon; mostly followable | Assumes knowledge of the codebase |

## Answer key for the scorer

Valid workflow values: request_to_release, defect_triage, release_notes,
developer_onboarding, change_approval. The orders report exits with a message if
httpx is missing or OrderCore is not running. Length is not scored, but an
explanation of every import line is padding, not teaching.
