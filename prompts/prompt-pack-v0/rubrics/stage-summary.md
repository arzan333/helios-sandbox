---
owner: Business Analyst
version: 1.0
effective_date: 2026-03-02
review_date: 2026-09-02
---

# Rubric - request-to-release stage summary for the engineering manager

Score the output file, not the chat. Five criteria, 0 to 5 each, maximum 25.
5 = fully met, 3 = mostly, 0 = absent. Whole numbers. Score what is written;
give no credit for what the model probably meant.

| # | Criterion | 5 looks like | 3 looks like | 0 looks like |
|---|---|---|---|---|
| 1 | Numbers match the report | The three worst medians match apps/insight/report.py stages --workflow request_to_release within 0.1 h: 147.1, 136.2, 69.2 | Two of three match | Numbers differ from the report, or are described as estimates |
| 2 | Ticket count stated | Says the numbers are based on 91 tickets | Count present but wrong | No count |
| 3 | Worst three with queue or effort | analysis_done -> design_start (queue, waiting for the architect), build_done -> test_start (queue, waiting for the test environment), build_start -> build_done (effort), each tied to a step in the narrative | Names them without the judgement | Wrong transitions |
| 4 | Rework matches | Rate 34.1% (31 of 91); top reasons: acceptance criteria missing 9, no test evidence 9, wrong system identified 7 | Rate right, reasons partial | Missing or wrong |
| 5 | Fit for a manager | Readable in two minutes; each recommendation points at a number above it | Readable, recommendations generic | A ten-minute memo with an ASCII chart and no decision in it |

## Answer key for the scorer

Run the report yourself and compare:

    python apps/insight/report.py stages --workflow request_to_release

Median created -> closed is 546.5 h. Anything the memo says that the report does
not say needs its own evidence.
