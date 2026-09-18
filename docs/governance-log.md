---
owner: Architect
version: 1.0
effective_date: 2026-03-02
review_date: 2026-09-02
---

# Documentation governance log

One row per document in the repository. Registering a document is the act that gives
it an owner and a review date; an unregistered document is not part of the repository
no matter where the file sits.

| Document | Owner | Version | Effective | Review by | Status |
|---|---|---|---|---|---|
| `docs/helios-landscape.md` | Architect | 1.0 | 2026-01-12 | 2026-07-12 | current |
| `data/entity-map.md` | Architect | 1.3 | 2026-02-20 | 2026-08-20 | current |
| `docs/process/request-to-release.md` | Release Manager | 1.0 | 2025-11-04 | 2026-05-04 | **overdue** |
| `docs/process/defect-triage.md` | Quality Engineer | 1.1 | 2026-01-30 | 2026-07-30 | current |
| `docs/process/release-notes.md` | Release Manager | 1.0 | 2025-12-01 | 2026-06-01 | **overdue** |
| `rubrics/hld.md` | Architect | 1.0 | 2026-03-02 | 2026-09-02 | current |
| `rubrics/lld.md` | Architect | 1.0 | 2026-03-02 | 2026-09-02 | current |
| `docs/specs/ordercore-fsd.docx` | Product Manager | 0.9 | 2026-01-12 | 2026-07-12 | draft |
| `docs/specs/ordercore-techspec.pdf` | Architect | 0.7 | 2026-03-03 | 2026-09-03 | draft |

## Two rows are already overdue

Both are process narratives, both are read every week, and neither has been looked at
since last year. That is the ordinary way a repository rots: not by documents going
missing, but by documents nobody re-reads staying confidently out of date.

## Adding a row

A document joins the repository when its row is added here and its front matter
matches. The two must agree. Where they differ, the file's front matter is what a
tool reads, so fix the file and then fix the row.
