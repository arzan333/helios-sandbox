---
template: AI-Native Workflow Blueprint
week: 1
---

# Workflow blueprint — request to release

Author: <your name>  ·  Date: <date>  ·  Workflow: request to release

## 1. Stage durations

From `data/helios-tickets.csv`, filtered to request_to_release.

| Transition | Median hours | P90 hours | Wait or work? |
|---|---|---|---|
|  |  |  |  |

Three worst by median: 1. ___  2. ___  3. ___

State for each whether it is a queue (waiting) or effort (working). They are
treated differently.

## 2. Step classification

Answer the three tests, then let them decide the category. All three yes is
AI-ready. Mixed is AI-assisted. A judgement call, or anything irreversible, is
human-only.

| # | Step | Bounded? | Checkable? | Reversible? | Category | Reason |
|---|---|---|---|---|---|---|
|  |  |  |  |  |  |  |

"It is faster" is not a justification. Say what makes the task bounded and
verifiable, or what makes it a judgement call.

## 3. Target state

Pattern chosen: <Draft-Review-Approve | Analyze-Validate-Escalate | Generate-Verify-Publish>

| Change | Steps affected |
|---|---|
| Disappears |  |
| Merges |  |
| Untouched |  |

## 4. Gates

Minimum two. Every gate names one role from the RACI in `docs/helios-landscape.md`.

| Gate | Placed after step | Owner role | Pass criteria | Failure handling | Escalation trigger |
|---|---|---|---|---|---|
|  |  |  |  |  |  |

## 5. Metrics

| Metric | Today (from data) | Target | How it will be measured |
|---|---|---|---|
| Cycle time, created to closed |  |  |  |
| Rework rate |  |  |  |
| Reviewer hours per ticket |  |  |  |
