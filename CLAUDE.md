# CLAUDE.md

Helios Group sandbox. A synthetic training environment for the Claude Code
Capability Program. Everything here is fictional.

## What is in here

- `apps/` — four small services. Shop (React), OrderCore (Python), Billing (Java), Insight (Python scripts).
- `data/` — the delivery dataset and the entity map.
- `docs/` — process narratives and design documents.
- `helios-backlog/` — tickets in Jira export shape.
- `labs/` — self-paced lab books, one per week. Open them in a browser.
- `rubrics/` — design review rubrics.
- `templates/` — canvases and checklists participants fill in.

## Where authority lives

- The landscape and role RACI: `docs/helios-landscape.md`
- What a change touches: `data/entity-map.md`
- How the current process runs: `docs/process/`
- Ticket detail: `helios-backlog/<KEY>.json`

If those disagree with something in a lab book, the lab book is the one being
followed today, but say so rather than quietly picking one.

## Standards

- Money is always a whole number of pence. Never a float. Format only at the UI edge.
- Python: 4-space indent, type hints on function signatures, `ruff` clean.
- Java: 4-space indent, no new runtime dependencies in Billing.
- React: function components, hooks, no class components.
- Tests live beside the code they cover and must pass before a commit.
- Commit locally only. Nothing in this programme is ever pushed. A `pre-push` hook in
  `.githooks/` blocks it; never suggest bypassing it with `--no-verify`.

## What not to modify

- `data/helios-tickets.csv` — regenerate it with `scripts/generate_tickets.py` if
  it must change. Editing rows by hand breaks the worked answers.
- `scripts/generate_tickets.py` seed value. Every participant must see identical numbers.
- Other participants' `week1/`–`week4/` folders.

## Running things

```
# OrderCore
cd apps/ordercore && pip install -r requirements.txt && uvicorn app.main:app --port 8080

# Billing  (Maven, needs network the first time)
cd apps/billing && mvn -q package && java -jar target/billing-1.0.0.jar

# Billing  (no Maven, fully offline - Billing has no runtime dependencies)
cd apps/billing && javac -d out $(find src/main/java -name "*.java") && java -cp out com.helios.billing.BillingServer

# Shop
cd apps/shop && npm install && npm run dev

# Reports
python apps/insight/report.py stages --workflow intake
```

Billing is optional. If it is not running, OrderCore calculates invoices locally
and marks them `source: "fallback"`.

## Working style in this repository

Plan before you generate. Say what you are about to change and which files it
touches before changing them. Keep diffs small and one concern at a time. Run the
tests before saying something is done.
