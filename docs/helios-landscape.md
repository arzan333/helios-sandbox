---
owner: Architect
version: 1.0
effective_date: 2026-01-05
review_date: 2026-07-05
source_system: Helios delivery
---

# Helios Group landscape

Helios Group is a mid-size consumer products company. The internal delivery team
is about 200 people. Everything in this repository is synthetic and exists only
for training.

## Systems

| System | Stack | Port | What it does |
|---|---|---|---|
| Shop | React + Vite | 5173 | Customer-facing order review screen |
| OrderCore | Python + FastAPI | 8080 | Order management API. The primary system |
| Billing | Java 17, JDK HTTP server | 8081 | Invoice calculation |
| Insight | Python scripts | n/a | Reporting over delivery data and orders |

## How they talk

```
Browser
   |
   v
Shop (5173)  --/api proxy-->  OrderCore (8080)  --POST /invoice-->  Billing (8081)
                                    |
                                    v
                              orders.json (seed)

Insight  --reads-->  data/helios-tickets.csv
         --calls-->  OrderCore (8080)
```

One cross-language call exists: OrderCore to Billing. Field naming differs across
that boundary and the translation lives in `apps/ordercore/app/billing_client.py`.

## Roles and RACI

| Activity | Business Analyst | Developer | Architect | Quality Engineer | Release Manager |
|---|---|---|---|---|---|
| Requirement analysis | **A** | C | C | C | I |
| Acceptance criteria | **A** | C | I | C | I |
| High-level design | C | C | **A** | I | I |
| Low-level design | I | **A** | C | I | I |
| Build | I | **A** | C | I | I |
| Test | C | C | I | **A** | I |
| Release approval | I | I | C | C | **A** |
| Cross-system change approval | I | C | **A** | C | C |

A = accountable, C = consulted, I = informed. Every gate in this programme must
name one of these five roles. "The team" is not an owner.

## Known constraints

These are real and they shape the numbers in `data/helios-tickets.csv`:

- There is one architect. Every design waits on the same person.
- There is one shared test environment. Every ticket queues for it.
- The entity map is maintained by hand and goes stale.
- Acceptance criteria are missing on roughly a third of tickets.
