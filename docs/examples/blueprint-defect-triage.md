---
template: AI-Native Workflow Blueprint
week: 1
status: worked example
---

# Workflow blueprint — defect triage

Author: Priya Raman (Quality Engineer)  ·  Date: 2026-08-14  ·  Scenario: defect_triage

> **This is a finished example, so you can see what you are aiming at.**
> It covers *defect triage*. In the lab you build one for *requirement intake*,
> so you cannot copy this — but the shape, the level of detail and the kind of
> reasoning are exactly what is expected of yours.

## 1. Stage durations

From `data/helios-tickets.csv`, filtered to `defect_triage`.

| Transition | Median hours | P90 hours | Wait or work? |
|---|---|---|---|
| analysis_done -> design_start | 170.9 | 251.4 | **Wait** — sitting in the architect's queue |
| build_done -> test_start | 140.1 | 198.6 | **Wait** — sitting in the shared test environment queue |
| build_start -> build_done | 54.3 | 117.2 | **Work** — the developer is actually fixing it |
| analysis_start -> analysis_done | 23.9 | 68.0 | Work — reproducing and investigating |
| created -> triaged | 4.3 | 20.1 | Wait, but short enough to ignore for now |

Three worst by median: 1. analysis_done → design_start  2. build_done → test_start  3. build_start → build_done

The first two are queues. Nothing is happening to the ticket; it is waiting for a
person or an environment. The third is real effort and will not be fixed by
changing the process, so I have left it alone.

## 2. Step classification

| # | Step | AI-ready / AI-assisted / human-only | One-line justification |
|---|---|---|---|
| 1 | Defect reported | human-only | The report comes from outside the team; nothing to automate yet |
| 2 | Duplicate check | **AI-ready** | Bounded (search the backlog), checkable (a human sees the candidates), reversible (a wrong match is just discarded) |
| 3 | Reproduce | human-only | Needs a person driving a live environment and judging what they see |
| 4 | Severity assigned | AI-assisted | AI can propose from impact and volume, but there is no severity matrix, so a person owns the call |
| 5 | Component identified | **AI-ready** | The entity map says which system owns what; the answer is checkable against it |
| 6 | Assigned to a developer | human-only | Depends on who is free and who knows the system — AI cannot see either |
| 7 | Root cause investigation | AI-assisted | AI reads logs and narrows candidates; the developer confirms the cause |
| 8 | Fix written | AI-assisted | AI drafts, developer reviews and owns the diff |
| 9 | Test evidence attached | **AI-ready** | Bounded, checkable, reversible — and it is a standing rework reason today |
| 10 | Peer review | human-only | Accountability for the merge sits with a named person |
| 11 | Merged and queued | human-only | Touches a release; irreversible |
| 12 | Closed | AI-assisted | AI drafts the notification, the engineer sends it |

I marked step 4 AI-assisted rather than AI-ready because being wrong is not
cheap: a mis-set severity changes who gets paged.

## 3. Target state

Pattern chosen: **Analyze-Validate-Escalate**

| Change | Steps affected |
|---|---|
| Disappears | Step 2 — the manual backlog search stops being a human task |
| Merges | Steps 4 and 5 merge into one triage call, proposed by AI, confirmed by the Quality Engineer |
| Untouched | Steps 3, 6, 10, 11 — reproduction, assignment, review and merge stay entirely human |

Being explicit about what stays: peer review and merge are the two places where a
wrong answer reaches a customer, so neither gets AI anywhere near the decision.

## 4. Gates

| Gate | Placed after step | Owner role | Pass criteria | Failure handling | Escalation trigger |
|---|---|---|---|---|---|
| Triage confirmation | Merged step 4+5 | Quality Engineer | Severity and component both stated with a reason; component matches the entity map | Returned to the AI step with the reason recorded; QE may override and set it manually | Same defect re-triaged twice |
| Fix acceptance | Step 9 | Developer (not the author) | Tests attached and passing; the diff does only what the ticket asked | Sent back to the author with named gaps | Rejected twice, or a severity-1 defect |

Both gates name one person. "The team reviews it" was what we had before, and it
is why nobody owned the outcome.

## 5. Metrics

| Metric | Today (from data) | Target | How it will be measured |
|---|---|---|---|
| Cycle time, created to closed | 551.6 h median | 400 h | Same report, same filter, re-run monthly |
| Rework rate | 29.5% (18 of 61) | 20% | `rework_count > 0` on defect_triage tickets |
| Reviewer hours per ticket | not measured today | establish a baseline first | Add a field before claiming an improvement |

The top rework reason is "design not reviewed" (6 of 18). The triage confirmation
gate is aimed straight at it. "No test evidence" (3 of 18) is aimed at by the fix
acceptance gate. I would expect those two to move first, and cycle time to move
last, because cycle time is dominated by the two queues rather than by rework.

## Design gate verdict

I read `docs/design/HEL-142-hld.md` and would **not** pass it. It never says what
is out of scope, and it does not mention Insight even though Insight reads the
order data the change touches. The estimate has no basis. None of that makes it
obviously wrong — it makes it unreviewable, which is the problem.
