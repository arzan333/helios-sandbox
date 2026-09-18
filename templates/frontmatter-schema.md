---
owner: Architect
version: 1.0
effective_date: 2026-03-02
review_date: 2026-09-02
---

# Front matter schema

Every document in a retrievable repository carries this block, first thing in the
file, between two lines of three dashes. A file without it is a file nobody owns.

| Field | Required | What it is | Example |
|---|---|---|---|
| `owner` | yes | One role, never a team. The person who answers when the document is wrong | `Architect` |
| `version` | yes | Increments when the meaning changes, not when a typo is fixed | `1.2` |
| `effective_date` | yes | When this version became the truth | `2026-03-02` |
| `review_date` | yes | When someone must look at it again. Past this date the document is suspect | `2026-09-02` |
| `source` | when converted | The file this was converted from, so the original can be found | `ordercore-fsd.docx` |
| `status` | no | `draft`, `current` or `superseded`. Absent means current | `draft` |

## The two that do the work

**`owner`** turns a stale document into somebody's problem. "The team" owns nothing.

**`review_date`** is what makes staleness visible. A document that is confidently
wrong is worse than one that is missing, because nobody checks a document they trust.

## Rules

- The block is the first thing in the file. Nothing above it, not even a heading.
- Dates are ISO: `YYYY-MM-DD`. No other format is accepted.
- A converted document keeps `source` for as long as the original exists.
- If you cannot name an owner, the document does not go in the repository.
