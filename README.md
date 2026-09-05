# Helios Sandbox

The practice environment for the **Claude Code Capability Program**.

Helios Group is a fictional consumer products company with an internal delivery
team of about 200 people. Every system, document, ticket and number in this
repository is synthetic. Nothing here comes from a real client.

## What you do first

1. Run `Setup-HeliosWorkstation.ps1` from an elevated PowerShell prompt.
2. Clone this repository, create your own branch, and turn on the push guard:
   ```
   git checkout -b <yourname>/foundation
   git config core.hooksPath .githooks
   ```
   The second line installs a `pre-push` hook that refuses every push. Your work
   stays on your machine.
3. Fill in `templates/baseline-capture.md`.
4. Open `labs/week1.html` in a browser and work through it. Week 2 is `labs/week2.html`
   followed by `labs/week2-activity.html`.

**Commits stay local.** Nothing in this programme is ever pushed.

## Layout

```
apps/          four small services - see below
data/          delivery dataset and entity map
docs/          process narratives and design documents
helios-backlog/  tickets in Jira export shape
labs/          self-paced lab books, one per week (week2.html is the lab, week2-activity.html the hands-on)
prompts/       week 2 lab prompts and the prompt pack (see prompts/README.md)
rubrics/       design review rubrics
scripts/       dataset generator and repo validator
setup/         workstation setup script
skills/        worked example Skill
templates/     canvases and checklists you fill in
```

## The systems

| System | Stack | Port | Purpose |
|---|---|---|---|
| `apps/shop` | React + Vite | 5173 | Order review screen |
| `apps/ordercore` | Python + FastAPI | 8080 | Order management API |
| `apps/billing` | Java 17 | 8081 | Invoice calculation |
| `apps/insight` | Python | n/a | Reports over delivery data |

Full picture: `docs/helios-landscape.md`.

## Running it

You do not need any of this for Week 1. It is here for later weeks.

```bash
# OrderCore
cd apps/ordercore
pip install -r requirements.txt
uvicorn app.main:app --port 8080

# Billing (optional - OrderCore falls back if it is down)
cd apps/billing
mvn -q package && java -jar target/billing-1.0.0.jar

# Billing without Maven - it has no runtime dependencies
cd apps/billing
javac -d out $(find src/main/java -name "*.java")
java -cp out com.helios.billing.BillingServer

# Shop
cd apps/shop
npm install
npm run dev
```

## Tests

```bash
cd apps/ordercore && python -m pytest      # 11 tests
cd apps/billing   && mvn -q test           # 19 tests
cd apps/shop      && npm run lint
python scripts/validate_repo.py            # 161 repo consistency checks
python scripts/validate_week2.py           # week 2 assets and lab books
# Week 2 tooling: scripts/ledger.py (token ledger), scripts/estimate_tokens.py,
# scripts/score.py (rubric scoring on a stronger model via claude -p)
```

## Regenerating the dataset

`data/helios-tickets.csv` is generated, not hand-written. The seed is fixed so
every participant sees identical numbers.

```bash
python scripts/generate_tickets.py
```

Do not edit the CSV by hand. It breaks the worked answers.
