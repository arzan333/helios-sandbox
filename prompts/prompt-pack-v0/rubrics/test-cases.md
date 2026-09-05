---
owner: Quality Engineer
version: 1.0
effective_date: 2026-03-02
review_date: 2026-09-02
---

# Rubric - test cases for order creation

Score the output file, not the chat. Five criteria, 0 to 5 each, maximum 25.
5 = fully met, 3 = mostly, 0 = absent. Whole numbers. Score what is written;
give no credit for what the model probably meant.

| # | Criterion | 5 looks like | 3 looks like | 0 looks like |
|---|---|---|---|---|
| 1 | Boundaries covered | quantity 0 and 1; unit price -1, 0 and 1; empty lines and one line; empty customer and one character; missing and empty SKU | Two boundary pairs missing | Happy path only |
| 2 | Expected results are checkable | Every case states the HTTP status and what the body contains (or that nothing is stored) | Most do; some say "error" without a status | Expected results are vague or missing |
| 3 | Identifier allocation | Covers ORD-1001 as the first free id, and that a seeded id already in use is skipped (store.py) | Covers the format only | Not covered |
| 4 | Agrees with the code | No case expects behaviour models.py does not have: currency is not validated, description is optional, quantity is an int | One case contradicts the code | Several cases test rules that do not exist |
| 5 | One check per case, no duplicates | Each case tests one rule; the set has no repeats, however many formats it is presented in | A couple of overlaps | The same cases repeated under different headings and counted as coverage |

## Answer key for the scorer

models.py: customer min_length 1; lines min_length 1; sku min_length 1;
quantity gt 0; unit_price_pence ge 0; currency defaults to GBP with no validation;
description defaults to empty. store.py allocates 1001 + len(orders) and loops
past any id already present. main.py returns 201 on success; validation errors are
422 from the framework.
