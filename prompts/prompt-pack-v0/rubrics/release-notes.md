---
owner: Release Manager
version: 1.0
effective_date: 2026-03-02
review_date: 2026-09-02
---

# Rubric - release notes for the January 2026 drop

Score the output file, not the chat. Five criteria, 0 to 5 each, maximum 25.
5 = fully met, 3 = mostly, 0 = absent. Whole numbers. Score what is written;
give no credit for what the model probably meant.

| # | Criterion | 5 looks like | 3 looks like | 0 looks like |
|---|---|---|---|---|
| 1 | Scope is right and stated | Says the drop covers tickets deployed 1 to 31 January 2026 and gives the row count (41) | Right range, no count, or count off by a few | Wrong month, or the whole file |
| 2 | Deduplicated and denoised | Each distinct title appears once (17 distinct in January), and internal tasks (release notes, onboarding, setup guide, approvals, retention change) are dropped or separated from customer changes | Duplicates removed but internal tasks kept as customer changes | One line per row |
| 3 | Grouped by system | Shop, OrderCore, Billing, Insight, using the system column; titles that appear under several systems are flagged rather than listed four times | Grouped, not flagged | Not grouped |
| 4 | Customer wording | No ticket ids, no "API", "schema", "extract" left unexplained; each change says what the customer can now do or will no longer see | Mostly rewritten; a few titles copied verbatim | Ticket titles copied |
| 5 | Nothing invented | Upgrade steps and known issues are either from the data or clearly flagged as unconfirmed; no features that are not in the CSV | One unflagged guess | Invented features or confident invented upgrade steps |

## Answer key for the scorer

January 2026 deployed rows: 41. Distinct titles: 17. Titles appear under several
systems because the dataset is synthetic; a good note flags that rather than
pretending each is four changes. A command that gets the scope without reading the
whole file, for the scorer's reference:

    python -c "import csv;r=[x for x in csv.DictReader(open('data/helios-tickets.csv')) if x['deployed'].startswith('2026-01')];print(len(r),len({x['title'] for x in r}))"
