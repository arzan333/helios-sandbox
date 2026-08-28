---
owner: Business Analyst
version: 2.1
effective_date: 2025-11-03
review_date: 2026-05-03
source_system: Helios delivery
---

# Request to release, current state

How a request becomes deployed change at Helios Group today. Sixteen steps, five
roles, three queues. This is the process as it actually runs, not as anyone would
design it.

Matching data: `data/helios-tickets.csv`, filtered to `workflow = intake`.

## Roles

| Role | Who does it |
|---|---|
| Business Analyst | Two analysts, shared across all four systems |
| Architect | One architect. This matters. |
| Developer | Six developers across OrderCore, Shop and Insight |
| Quality Engineer | Two engineers sharing one test environment |
| Release Manager | One, part time |

## The sixteen steps, request to release

1. **Request raised.** A stakeholder opens a ticket. There is no template, so
   quality varies from a paragraph to a single sentence.
2. **Triage.** The Business Analyst reads the queue each morning and decides
   whether the request is a story, a defect or a question. Questions are closed
   with a comment.
3. **Component tagged.** The analyst guesses which system is affected. The guess
   is wrong often enough that "wrong system identified" is a standing rework
   reason in the ticket data.
4. **Analysis started.** The analyst picks the ticket up when capacity allows.
5. **Stakeholder clarification.** The analyst emails the requester with
   questions. Replies take between an hour and four days.
6. **Acceptance criteria drafted.** Written by the analyst, in the ticket
   description. There is no agreed format and no checklist.
7. **Analysis complete.** The analyst marks the ticket ready for design.
8. **Design queue.** The ticket waits for the architect. There is one architect.
9. **Impact assessed.** The architect works out what the change touches, mostly
   from memory and by opening files.
10. **High-level design written.** A markdown document, attached to the ticket.
    Length varies from four lines to four pages.
11. **Design review.** The architect reviews their own work, or asks a senior
    developer if one is free. There is no rubric, so two reviewers reach two
    different conclusions on the same document.
12. **Build.** A developer implements the change. Low-level design, where it
    exists at all, is written after the code.
13. **Test queue.** The ticket waits for the shared test environment.
14. **Test execution.** A Quality Engineer tests against the acceptance criteria
    if they were written, and against their own judgement if they were not.
15. **Release approval.** The Release Manager batches approved tickets into the
    monthly drop.
16. **Deployed and closed.** Release notes are compiled by hand afterwards.

## Known pain, as reported by the team

- "We wait for the architect." Raised in every retrospective for four quarters.
- "We test whatever we think it means." Acceptance criteria are missing on
  roughly a third of tickets that reach test.
- Rework is not tracked as a cost. The ticket simply moves backwards and the
  clock keeps running.
- Nobody owns the design review outcome. The architect signs their own work.

## What the data shows

Run the report yourself rather than taking this section on trust:

```
python apps/insight/report.py stages --workflow request_to_release
```

Two waits dominate. Neither is work being done; both are queues.
