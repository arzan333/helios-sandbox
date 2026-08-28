---
template: AI-Native Workflow Blueprint
week: 1
---

# Workflow blueprint — request to release

Author: <your name>  ·  Date: <date>  ·  Workflow: request to release

## 1. Stage durations

From `data/helios-tickets.csv`, filtered to request_to_release.

| Transition | Median h | P90 h | Queue or effort? |
|---|---|---|---|
|  |  |  |  |

Three worst by median: 1. ___  2. ___  3. ___

A queue is the ticket sitting still. Effort is someone working. They are fixed
differently, so say which each one is.

## 2. Step classification

Answer the three tests, then let them decide the category. All three yes is
AI-ready. Mixed is AI-assisted. A judgement call, or anything irreversible, is
human-only.

| # | Step | Bounded? | Checkable? | Reversible? | Category | Reason |
|---|---|---|---|---|---|---|
|  |  |  |  |  |  |  |

"It is faster" is not a justification. Say what makes the task bounded and
verifiable, or what makes it a judgement call.

## 3. The new process

All sixteen steps, rewritten. Change is Removed, Merged into step N, or Unchanged.
Who does it now is Person, AI, or AI with a person checking.

| # | Step | Change | Who does it now |
|---|---|---|---|
|  |  |  |  |

Most steps should say Unchanged. Leaving a step alone is a decision; record it.

## 4. Gates

Minimum two. Every gate names one role from the RACI in `docs/helios-landscape.md`.

| Gate | Placed after step | Owner role | Pass criteria | Failure handling | Escalation trigger |
|---|---|---|---|---|---|
|  |  |  |  |  |  |

## 5. Metrics

| Metric | Today (from the data) | Target | How it will be measured |
|---|---|---|---|
| Cycle time, created to closed |  |  |  |
| Rework rate |  |  |  |
| Reviewer hours per ticket |  |  |  |
