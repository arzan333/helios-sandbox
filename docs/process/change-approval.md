---
owner: Architect
version: 1.0
effective_date: 2025-12-01
review_date: 2026-06-01
source_system: Helios delivery
---

# Change approval, current state

How a change that crosses a system boundary gets approved. Ten steps. Matching
data: `data/helios-tickets.csv`, filtered to `workflow = change_approval`.

## The ten steps

1. **Change proposed.** Usually inside a story ticket, occasionally by email.
2. **Change type classified.** Schema, interface, configuration or retention.
   The classification is informal.
3. **Downstream consumers identified.** From `data/entity-map.md`, which is
   maintained by hand and is sometimes out of date.
4. **Consumers notified.** An email. Replies are not tracked.
5. **Risk described.** A paragraph in the ticket. No scoring, no categories.
6. **Architect review.** One architect, and no second opinion.
7. **Approval recorded.** A comment saying "approved". No conditions, no expiry.
8. **Change implemented.**
9. **Downstream verification.** Whoever remembers checks that Insight still
   works after an OrderCore schema change.
10. **Closed.**

## Known pain

- Step 3 depends on a document nobody owns updating.
- Step 7 records a decision but not the reasoning, so the same question is
  re-argued three months later.
- Step 9 is optional in practice. Insight has broken twice this way.
