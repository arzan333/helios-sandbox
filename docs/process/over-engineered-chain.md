---
owner: Release Manager
version: 1.0
effective_date: 2026-03-02
review_date: 2026-09-02
---

# Release notes, as currently automated

This is a real shape, written down honestly. It works. It is also four times the
size it needs to be, and nobody has ever priced it.

## The chain

| Step | Agent | What it is given | What it does | What it returns |
|---|---|---|---|---|
| 1 | **Collector** | The whole ticket dataset | Reads every row, keeps the ones deployed this month | The month's tickets, in full |
| 2 | **Summariser** | Step 1's output, in full | Writes a paragraph about each ticket | One paragraph per ticket |
| 3 | **Grouper** | Step 2's output, in full, plus the ticket dataset again | Groups the paragraphs by system and removes duplicates | Grouped paragraphs |
| 4 | **Writer** | Step 3's output, in full, plus the house style guide | Rewrites everything in customer language | The release note |

Each step is a separate session. Each one is handed the previous step's entire
output as text.

## What it costs, per monthly run

These are measured, not estimated.

| Step | Model | Input tokens | Output tokens | Notes |
|---|---|---|---|---|
| 1 Collector | deep | 41,000 | 12,000 | The dataset is 210 rows; it reads all of them |
| 2 Summariser | deep | 14,000 | 9,500 | One paragraph per ticket, 41 tickets |
| 3 Grouper | deep | 24,000 | 6,200 | Re-reads the dataset to check the grouping |
| 4 Writer | deep | 8,900 | 3,100 | The only step whose output anyone reads |

Every step runs on the deep tier because the chain was built in an afternoon and
nobody revisited the choice.

## Questions worth asking before you price it

- Step 1 filters rows by date. What in that needs a model at all?
- Step 2 writes a paragraph per ticket. Step 4 then rewrites all of them. Who reads
  step 2's output?
- Step 3 re-reads the dataset that step 1 already read. Why is it not carried
  forward?
- Four sessions means four context bills. What would one session cost?

## The rule this illustrates

Every hand-off pays the context bill again. A chain is worth its cost when the
steps genuinely need different tools, different permissions, or a human in
between. Four steps because the work felt like four steps is not a reason.
