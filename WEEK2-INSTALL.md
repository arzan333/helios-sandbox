# Installing the Week 2 assets

1. Unzip over the repository root. It adds files and replaces README.md and CLAUDE.md.
2. From the root, run both validators:
       python scripts/validate_repo.py
       python scripts/validate_week2.py
3. Facilitator only: git add -A && git commit -m "Week 2" && git push --no-verify
4. Recommended: in setup/Setup-HeliosWorkstation.ps1 raise the Claude Code Min from 2.0.0 to 2.1.211.

## The 20-minute dry run before class (the only thing not testable in the build environment)

On the facilitator VM, on your own branch:

    git fetch origin && git merge origin/main
    python scripts/run.py prompts/week2-lab/ac-320.md --name ac --version v320
    python scripts/score.py week2/ac-v320.md --record week2/ledger.csv
    python scripts/ledger.py show week2/ledger.csv

Three things to confirm:
- the run records a row with real token figures (this proves /usage-free recording works on your seats)
- the scorer line says an Opus model. If it says Sonnet, your seats cannot reach Opus:
  tell the room to add --allow-scorer-mismatch and check two rows by hand instead of one
- lab step 5a publishes an artifact. If it does not, tell the room up front to use the
  local-file path; every other step is unchanged

Keep your ledger rows - they are the reference numbers for the room.

Participants pick everything up in lab step 0b.
