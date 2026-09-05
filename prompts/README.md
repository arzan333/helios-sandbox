# Prompts

Prompt assets for the Claude Code Capability Program.

- `week2-lab/` - the Week 2 lab: one task (acceptance criteria for HEL-142) at
  three prompt sizes, the rubric they are all scored on, and `score.md`, the
  scoring prompt (Claude scores with evidence per row; you check one row).
- `prompt-pack-v0/` - eight deliberately bloated prompts, 600 to 2,000 tokens
  each, used in the Week 2 hands-on activity and again in Week 4. Each has a
  25-point rubric in `prompt-pack-v0/rubrics/`.

Every prompt writes its output to a file under `week2/out/` so that it can be
scored and diffed. Never edit the v0 prompts in place; optimised versions go in
`week2/prompts/v1/` on your own branch.

Size a prompt before you run it:

```
python scripts/estimate_tokens.py prompts/prompt-pack-v0/*.md
```

Record what a run actually cost, from `/usage` in Claude Code:

```
python scripts/ledger.py add week2/ledger.csv --prompt code-review --version v0 --score 18 --usage "<the Usage by model line>"
python scripts/ledger.py show week2/ledger.csv
```

Score outputs with a stronger model than wrote them (fresh `claude -p` process,
Opus, rubric + output only), and record the totals:

```
python scripts/score.py week2/out/code-review-v0.md --record week2/ledger.csv
```
