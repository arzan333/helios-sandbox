---
name: stage-report
description: Summarise Helios delivery stage durations from data/helios-tickets.csv. Use when asked about cycle time, stage waits, bottlenecks, rework rates, or how long a Helios workflow takes.
---

# Stage report

Produces the median and 90th percentile duration for every stage transition in a
Helios workflow, and separates queues from effort.

This is the worked example participants copy in Week 4. It is deliberately small:
one job, a description that triggers on the words people actually use, and the
detail kept in a referenced file rather than inlined here.

## How to run it

```
python apps/insight/report.py stages --workflow <workflow>
```

Valid workflow values: `request_to_release`, `defect_triage`, `release_notes`,
`developer_onboarding`, `change_approval`. Omit `--workflow` for all tickets.

## How to read the result

- **Median** is the typical case. Use it for the headline.
- **P90** shows the tail. A p90 far above the median means the stage is unpredictable,
  which is a different problem from being slow.
- A transition is a **queue** when the ticket is waiting for a person or an
  environment, and **effort** when someone is working. Only queues can be removed
  by redesigning the workflow. Effort has to be made cheaper or eliminated.

Check the step in `docs/process/<workflow>.md` before calling anything a queue.

## Rules

- Never estimate a duration. Read it from the data.
- Always state the ticket count the numbers are based on.
- If asked about a workflow that is not in the list above, say so rather than guessing.
