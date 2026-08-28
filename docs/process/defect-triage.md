---
owner: Quality Engineer
version: 1.4
effective_date: 2025-10-12
review_date: 2026-04-12
source_system: Helios delivery
---

# Defect triage, current state

How a reported defect reaches a fix. Twelve steps. Matching data:
`data/helios-tickets.csv`, filtered to `workflow = defect_triage`.

## The twelve steps

1. **Defect reported.** From the contact centre, a monitoring alert, or a
   developer noticing something.
2. **Duplicate check.** The Quality Engineer searches the backlog by hand.
   Duplicates are found about half the time.
3. **Reproduce.** The engineer tries to reproduce on the shared environment.
   Roughly one in five cannot be reproduced and is parked.
4. **Severity assigned.** Judgement call. There is no severity matrix.
5. **Component identified.** Which of Shop, OrderCore, Insight or Billing owns
   this. Cross-system defects like currency rounding stall here because neither
   side accepts them.
6. **Assigned to a developer.** By whoever has capacity, not by system knowledge.
7. **Root cause investigation.** The developer reads logs and code. There is no
   agreed order of investigation, so two developers check things in two orders
   and one of them takes twice as long.
8. **Fix written.**
9. **Test evidence attached.** Sometimes. "No test evidence" is a standing
   rework reason.
10. **Peer review.** Another developer looks at the diff. No checklist.
11. **Merged and queued for release.**
12. **Closed.** The original reporter is notified only if they asked to be.

## Known pain

- Cross-system defects have no owner and sit longest.
- Reproduction happens before severity, so low-value defects consume the same
  effort as high-value ones.
- Investigation order is personal habit rather than a defined sequence.
