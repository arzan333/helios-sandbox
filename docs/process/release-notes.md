---
owner: Release Manager
version: 1.2
effective_date: 2025-09-20
review_date: 2026-03-20
source_system: Helios delivery
---

# Release note production, current state

How the monthly release note gets written. Nine steps, one person, most of a
morning. Matching data: `data/helios-tickets.csv`, filtered to
`workflow = release_notes`.

## The nine steps

1. **Freeze the release scope.** The Release Manager lists tickets marked done
   since the last drop.
2. **Export the ticket list.** Copied out of the tracker into a spreadsheet.
3. **Drop the noise.** Internal tasks, spikes and reverted changes are removed
   by hand.
4. **Group by system.** Shop, OrderCore, Insight, Billing.
5. **Rewrite each summary.** Ticket titles are written for the team, not for
   customers, so each one is reworded.
6. **Chase the gaps.** Around a fifth of tickets have a title that does not
   explain what changed. The Release Manager messages the developer.
7. **Add upgrade steps.** Written from memory of what was discussed.
8. **Review.** Sent to one senior developer, who usually replies "looks fine".
9. **Publish.** Pasted into the wiki and emailed.

## Known pain

- Step 5 is the whole job and it is pure rewriting.
- Step 6 exists because ticket titles are never written with the release note in
  mind.
- The review at step 8 is a formality. Nobody has ever rejected a release note.
