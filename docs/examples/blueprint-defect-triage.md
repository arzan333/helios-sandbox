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

| Transition | Median h | P90 h | Queue or effort? |
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

Answer the three tests, then let them decide the category. All three yes is
AI-ready. Mixed is AI-assisted. A judgement call, or anything irreversible, is
human-only.

| # | Step | Bounded? | Checkable? | Reversible? | Category | Reason |
|---|---|---|---|---|---|---|
| 1 | Defect reported | no | no | yes | human-only | Comes from outside the team; nothing to automate yet |
| 2 | Duplicate check | yes | yes | yes | AI-ready | Search the backlog, a human sees the candidates, a wrong match is discarded |
| 3 | Reproduce | no | yes | yes | human-only | Needs a person driving a live environment and judging what they see |
| 4 | Severity assigned | yes | no | no | AI-assisted | AI can propose from impact and volume, but a mis-set severity changes who gets paged |
| 5 | Component identified | yes | yes | yes | AI-ready | The entity map says which system owns what, so the answer is checkable against it |
| 6 | Assigned to a developer | no | no | yes | human-only | Depends on who is free and who knows the system; AI can see neither |
| 7 | Root cause investigation | no | yes | yes | AI-assisted | AI narrows candidates from logs, the developer confirms the cause |
| 8 | Fix written | yes | yes | no | AI-assisted | AI drafts, the developer reviews and owns the diff |
| 9 | Test evidence attached | yes | yes | yes | AI-ready | Bounded and checkable, and it is a standing rework reason today |
| 10 | Peer review | no | no | no | human-only | Accountability for the merge sits with a named person |
| 11 | Merged and queued | yes | yes | no | human-only | Touches a release; not reversible |
| 12 | Closed | yes | yes | yes | AI-assisted | AI drafts the notification, the engineer sends it |

Step 4 is the one I went back and forth on. It is bounded and I could check it,
but being wrong is not cheap, so it is AI-assisted rather than AI-ready.

## 3. The new process

All twelve steps, rewritten.

| # | Step | Change | Who does it now |
|---|---|---|---|
| 1 | Defect reported | Unchanged | Person |
| 2 | Duplicate check | Removed | AI, folded into step 4 |
| 3 | Reproduce | Unchanged | Person |
| 4 | Triage call (severity and component) | Merged, was steps 4 and 5 | AI, person checks |
| 5 | Component identified | Merged into step 4 | — |
| 6 | Assigned to a developer | Unchanged | Person |
| 7 | Root cause investigation | Unchanged | AI, person checks |
| 8 | Fix written | Unchanged | AI, person checks |
| 9 | Test evidence attached | Unchanged | AI |
| 10 | Peer review | Unchanged | Person |
| 11 | Merged and queued | Unchanged | Person |
| 12 | Closed | Unchanged | AI, person checks |

Nine of twelve are unchanged, which is what I expected. The two I touched are the
two the rework data pointed at. Peer review and merge stay entirely human because
they are the last points where a wrong answer reaches a customer.

## 4. Gates

| Gate | Placed after step | Owner role | Pass criteria | Failure handling | Escalation trigger |
|---|---|---|---|---|---|
| Triage confirmation | Merged step 4+5 | Quality Engineer | Severity and component both stated with a reason; component matches the entity map | Returned to the AI step with the reason recorded; QE may override and set it manually | Same defect re-triaged twice |
| Fix acceptance | Step 9 | Developer (not the author) | Tests attached and passing; the diff does only what the ticket asked | Sent back to the author with named gaps | Rejected twice, or a severity-1 defect |

Both gates name one person. "The team reviews it" was what we had before, and it
is why nobody owned the outcome.

## 5. Metrics

| Metric | Today (from the data) | Target | How it will be measured |
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
