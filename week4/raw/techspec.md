OrderCore - Technical Specification
Helios Group. Version 0.7, draft. Owner: Architect. Last edited 3 March 2026.
Companion to the functional specification. This document describes how OrderCore is built and run. Where
the two disagree, the functional specification describes intent and this document describes what is deployed;
raise the difference rather than resolving it silently.
1. Runtime shape
Three processes, started by hand in the training environment and by the pipeline elsewhere. There is no
orchestration layer, no service discovery and no shared database. Each process holds its own state in
memory and reads its seed data from disk at start.
Figure 1. Ports, the Billing timeout and the fallback rule are recorded here and nowhere else.
Helios Group - OrderCore technical specification - draft 0.7 Page 1

2. The invoice path
The only cross-language call in the estate. OrderCore translates its snake_case fields to Billing's camelCase
on the way out and back again on the way in. That translation is the contract, and it is enforced by nothing but
code review.
Figure 2. The retry behaviour is recorded in this diagram and nowhere else in the document.
2.1 Field mapping
| OrderCore | Billing | Type   | Notes                 |
| --------- | ------- | ------ | --------------------- |
| order_id  | orderId | string | Echoed back unchanged |
unit_price_pence unitPricePence integer Whole pence, never a decimal
discount_percent discountPercent integer 0 to 50 inclusive, added HEL-207
| subtotal_pence | subtotalPence | integer | Derived, not stored |
| -------------- | ------------- | ------- | ------------------- |
tax_pence taxPence integer 20 percent, calculated once on the order
total_pence totalPence integer subtotal minus discount, plus tax
Helios Group - OrderCore technical specification - draft 0.7 Page 2

3. Error handling
Three responses leave the service, and one condition that looks like an error to an operator is not an error to
the caller.
Figure 3. The error table exists only as an image in this document.
Helios Group - OrderCore technical specification - draft 0.7 Page 3

4. Performance
Measured in staging against the seeded dataset. The figures below are the only measurements anyone has
taken since the service went live.
Figure 4. One of these bars breaches a stated non-functional requirement.
Helios Group - OrderCore technical specification - draft 0.7 Page 4

5. Configuration
| Setting | Where it lives | Default | Changing it |
| ------- | -------------- | ------- | ----------- |
Billing base URL billing_client.py http://localhost:8081 Code change and review
Billing timeout billing_client.py 2000 ms Code change and review
Tax rate Both sides 20 percent Architect approval, both copies
Max discount Both sides 50 percent Architect approval, both copies
Seed file orders.json five orders Never edited to pass a test
Two of these values are written down in two languages. There is no mechanism that checks the copies
agree; the only protection is that both changes appear in the same review.
6. Testing
| Suite | Command | Covers | Does not cover |
| ----- | ------- | ------ | -------------- |
OrderCore python -m pytest Validation, lifecycle, the fallback Anything that reaches Billing
|     | apps/ordercore/tests | path | over the wire |
| --- | -------------------- | ---- | ------------- |
Billing JUnit, no runner installed Calculation, request parsing What OrderCore actually sends
| Lint | python -m ruff check | Style, unused imports | Correctness |
| ---- | -------------------- | --------------------- | ----------- |
apps/ordercore
7. Known gaps
| Ref | Gap | Consequence | Owner |
| --- | --- | ----------- | ----- |
TG-1 No contract test across the wire A field can be dropped in transit Architect
unnoticed
| TG-2 | Tax rate duplicated in two | Silent divergence | Architect |
| ---- | -------------------------- | ----------------- | --------- |
languages
TG-3 Invoice p95 over the NFR since Undetected breach Developer
February
TG-4 Runtime orders lost on restart Acceptable in training only Product
TG-5 No caller identity on any request NFR-7 cannot be met Architect
This table is the most useful page in the document and the least read, because it is the last one and nothing
links to it.
Helios Group - OrderCore technical specification - draft 0.7 Page 5