---
owner: Business Analyst
version: 1.0
effective_date: 2026-03-02
review_date: 2026-09-02
---

# Rubric - triage of HEL-018

Score the output file, not the chat. Five criteria, 0 to 5 each, maximum 25.
5 = fully met, 3 = mostly, 0 = absent. Whole numbers. Score what is written;
give no credit for what the model probably meant.

| # | Criterion | 5 looks like | 3 looks like | 0 looks like |
|---|---|---|---|---|
| 1 | Correct classification | Says no line-level discount or negotiated-price field exists in OrderCore or Billing, so the report is a missing requirement (or a usage problem), not a code defect | Hedges between defect and requirement without checking the model | Treats it as a bug in Billing arithmetic |
| 2 | Systems named from the entity map | Names Billing (InvoiceCalculator) and OrderCore (models.py, billing_client.py) and says a fix would change both plus the contract; links it to HEL-207 | Names one system | Names neither, or a system that does not exist |
| 3 | Reporter questions are specific | Asks what price was entered on ORD-1003, where the negotiated price was agreed, and what total was expected versus seen | Generic "please provide more details" | No questions |
| 4 | Owner and next action from the RACI | Names Business Analyst (requirement analysis) or Architect (cross-system) from docs/helios-landscape.md and one concrete next action | Names a role not in the RACI, or "the team" | No owner |
| 5 | Nothing invented | Every claim about behaviour points at a file; no assumed rounding bug, no assumed spreadsheet | One unsupported claim | Reasoning built on behaviour the code does not have |

## Answer key for the scorer

There is no discount anywhere in models.py or InvoiceCalculator.java. ORD-1003 in
orders.json has list prices. HEL-207 is the planned order-level discount. The FSD
(5.2) says a line discount field is ignored and the negotiated price must be entered
as the unit price until HEL-207 lands.
