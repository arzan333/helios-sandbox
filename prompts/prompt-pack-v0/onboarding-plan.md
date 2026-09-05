You are an experienced engineering lead who has onboarded dozens of developers onto unfamiliar codebases. You know that the first week sets the tone, that people learn by doing, and that the fastest way to lose a new developer is to give them a setup document that is out of date.

Three developers join the Helios Group delivery team next month and will work on OrderCore (see helios-backlog/HEL-166.json - the ticket says the current setup notes are eight months old and reference a service that no longer exists). I would like you to write a first-week onboarding plan for them.

Here is the repository README so you have the layout and the run commands:

--- README.md begins ---
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
4. Open `labs/week1.html` in a browser and work through it.

**Commits stay local.** Nothing in this programme is ever pushed.

## Layout

```
apps/          four small services - see below
data/          delivery dataset and entity map
docs/          process narratives and design documents
helios-backlog/  tickets in Jira export shape
labs/          self-paced lab books, one per week
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
```

## Regenerating the dataset

`data/helios-tickets.csv` is generated, not hand-written. The seed is fixed so
every participant sees identical numbers.

```bash
python scripts/generate_tickets.py
```

Do not edit the CSV by hand. It breaks the worked answers.
--- README.md ends ---

Please also read CLAUDE.md for the standards and working style, docs/helios-landscape.md for the systems and roles, data/entity-map.md for which files each concept touches, docs/specs/ordercore-fsd.txt for the functional behaviour of OrderCore, and please read every file under apps/ordercore/ so that you know what a new developer will actually see, and please read setup/Setup-HeliosWorkstation.ps1 so that you can describe what the setup script does, and please look at apps/billing/ and apps/shop/ briefly so you can describe how OrderCore relates to them.

Then please write a five-day onboarding plan. For each day please give an hour-by-hour schedule from 09:00 to 17:00, with a learning objective for each block, the exact files to read or commands to run, what the developer should be able to do or explain at the end of the block, and a suggested buddy check-in question. Day one should get the environment working and prove it with the tests. Day two should be the order lifecycle and data model. Day three should be the Billing boundary and the fallback, which is the thing people most often get wrong. Day four should be a small supervised change. Day five should be a review and a retrospective.

Please also include: a checklist of accounts and access the developer needs before day one; a list of the ten things every OrderCore developer must know, drawn from CLAUDE.md and the entity map; a list of the most common mistakes new developers make on this codebase and how to avoid them; a glossary; a set of ten questions the developer should be able to answer by Friday; and a section for the buddy on how to run the week.

Please make sure every command in the plan works from the repository root on Windows. Please do not reference any service, file or tool that does not exist in the repository. Please make the plan realistic for a developer who knows Python but has never seen FastAPI or this codebase. Please keep the tone welcoming.

Write the plan to week2/out/onboarding-plan-v0.md, and then in the chat give me the day-one schedule and the ten things every developer must know, so I can review the level.
