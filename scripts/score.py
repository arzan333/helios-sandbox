"""Score output files against their rubrics with a stronger model than wrote them.

    python scripts/score.py week2/ac-v2000.md week2/ac-v900.md week2/ac-v320.md --record week2/ledger.csv
    python scripts/score.py week2/out/code-review-v0.md --record week2/ledger.csv

For every output file this script:
  1. finds the rubric by convention (see RUBRIC_FOR),
  2. runs Claude Code once, non-interactively, on the OPUS model with read-only tools,
     using the scoring prompt in prompts/week2-lab/score.md,
  3. saves the five evidence lines and the total to week2/scores/<output name>.md,
  4. with --record, writes the total into the ledger row for that prompt and version.

Why a separate, stronger model: the file was written by Sonnet in your interactive
session. Scoring it with the same model in the same session is asking the author to
mark their own homework. `claude -p` starts a fresh process with no memory of the
run, and --model opus puts a stronger reader on the rubric. The script checks the
model that actually answered and refuses to record a score from anything else
unless you pass --allow-scorer-mismatch.

Standard library only. Requires Claude Code 2.1.211 or later on PATH.
"""

import argparse
import csv
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCORE_PROMPT = ROOT / "prompts" / "week2-lab" / "score.md"
SCORES_DIR = ROOT / "week2" / "scores"

# Output file name  ->  rubric.  Lab outputs are week2/ac-v<size>.md;
# pack outputs are week2/out/<name>-v<n>.md.
LAB_RUBRIC = "prompts/week2-lab/rubric-acceptance-criteria.md"
PACK_RUBRICS = "prompts/prompt-pack-v0/rubrics/{name}.md"
NAME_RE = re.compile(r"^(?P<prompt>[a-z][a-z0-9-]*?)-(?P<version>v\d+)\.md$")


def rubric_for(output: Path) -> tuple[Path, str, str]:
    """Return (rubric path, prompt name, version) for an output file."""
    m = NAME_RE.match(output.name)
    if not m:
        sys.exit(f"{output}: name must look like <prompt>-v<n>.md, e.g. code-review-v0.md or ac-v320.md")
    prompt, version = m.group("prompt"), m.group("version")
    if prompt == "ac":
        return ROOT / LAB_RUBRIC, prompt, version
    rubric = ROOT / PACK_RUBRICS.format(name=prompt)
    if not rubric.exists():
        sys.exit(f"{output}: no rubric at {rubric.relative_to(ROOT)}")
    return rubric, prompt, version


def build_prompt(rubric: Path, output: Path) -> str:
    template = SCORE_PROMPT.read_text(encoding="utf-8")
    return (template.replace("RUBRIC_FILE", rubric.relative_to(ROOT).as_posix())
                    .replace("OUTPUT_FILE", output.relative_to(ROOT).as_posix()))


def run_claude(prompt: str, model: str, effort: str) -> dict:
    exe = shutil.which("claude")
    if not exe:
        sys.exit("claude is not on PATH. Open a new terminal, or run claude --version to check the install.")
    cmd = [exe, "-p", "--model", model, "--effort", effort, "--output-format", "json",
           "--allowedTools", "Read,Grep,Glob", "--max-budget-usd", "0.75", "--no-session-persistence"]
    proc = subprocess.run(cmd, input=prompt, capture_output=True, text=True, cwd=ROOT, encoding="utf-8")
    if proc.returncode != 0:
        sys.exit(f"claude -p failed (exit {proc.returncode}):\n{proc.stderr.strip() or proc.stdout.strip()}")
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError:
        sys.exit(f"claude -p did not return JSON. First 300 characters:\n{proc.stdout[:300]}")


def scorer_model(payload: dict) -> str:
    usage = payload.get("modelUsage") or {}
    if isinstance(usage, dict) and usage:
        # The model that did the most output is the one that wrote the score.
        best = max(usage.items(), key=lambda kv: (kv[1] or {}).get("outputTokens", 0) if isinstance(kv[1], dict) else 0)
        return best[0]
    return payload.get("model", "unknown")


TOTAL_RE = re.compile(r"TOTAL:\s*(\d{1,2})\s*/\s*25", re.I)
ROW_RE = re.compile(r"^\s*(?:row\s*)?\(?(?P<n>[1-5])[.):|\s-]+.*?\b(?P<score>[0-5])\b", re.I | re.M)


def parse_total(text: str) -> int | None:
    m = TOTAL_RE.search(text)
    return int(m.group(1)) if m else None


def record(ledger: Path, prompt: str, version: str, score: int, note: str) -> None:
    if not ledger.exists():
        sys.exit(f"{ledger} does not exist. Record the run with scripts/ledger.py add first.")
    with ledger.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        fields = reader.fieldnames
    hits = [r for r in rows if r["prompt"] == prompt and r["version"] == version]
    if not hits:
        sys.exit(f"No ledger row for {prompt} {version}. Rows present: "
                 + ", ".join(f"{r['prompt']}/{r['version']}" for r in rows))
    hits[-1]["rubric_score"] = str(score)
    hits[-1]["notes"] = (hits[-1].get("notes") or "").strip()
    hits[-1]["notes"] = (hits[-1]["notes"] + "; " if hits[-1]["notes"] else "") + note
    with ledger.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def family(model: str) -> str:
    """opus / sonnet / haiku / fable, from names like claude-opus-5[1m]."""
    m = re.sub(r"^claude-", "", (model or "").lower())
    for name in ("opus", "fable", "sonnet", "haiku"):
        if name in m:
            return name
    return m.split("-")[0] if m else "unknown"


def generator_model(ledger: Path, prompt: str, version: str) -> str | None:
    """Which model wrote the answer, according to the ledger."""
    if not ledger.exists():
        return None
    with ledger.open(encoding="utf-8", newline="") as handle:
        hits = [r for r in csv.DictReader(handle)
                if r["prompt"] == prompt and r["version"] == version]
    return hits[-1]["model"] if hits else None


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("outputs", nargs="+", help="output files to score, e.g. week2/out/code-review-v0.md")
    parser.add_argument("--record", metavar="LEDGER", help="write each total into this ledger (scripts/ledger.py format)")
    parser.add_argument("--model", default="opus", help="scorer model alias (default opus; must be stronger than the generator)")
    parser.add_argument("--effort", default="high")
    parser.add_argument("--allow-scorer-mismatch", action="store_true",
                        help="record even if the model that answered is not an Opus (or Fable) model")
    args = parser.parse_args()

    SCORES_DIR.mkdir(parents=True, exist_ok=True)
    exit_code = 0
    for raw in args.outputs:
        output = (ROOT / raw).resolve() if not Path(raw).is_absolute() else Path(raw)
        if not output.exists():
            print(f"x {raw}: file not found (the run did not write it). Score it 0 with scripts/ledger.py score.")
            exit_code = 1
            continue
        rubric, prompt, version = rubric_for(output)
        print(f"Scoring {output.relative_to(ROOT)} against {rubric.relative_to(ROOT)} on {args.model} ...", flush=True)
        payload = run_claude(build_prompt(rubric, output), args.model, args.effort)
        text = payload.get("result") or ""
        model = scorer_model(payload)
        cost = payload.get("total_cost_usd")
        total = parse_total(text)

        evidence = SCORES_DIR / f"{output.stem}.md"
        evidence.write_text(
            f"# Score: {output.relative_to(ROOT).as_posix()}\n\n"
            f"Rubric: {rubric.relative_to(ROOT).as_posix()}  \n"
            f"Scorer model: {model}  \n"
            f"Scorer cost (list price): {cost if cost is not None else 'n/a'}\n\n"
            f"{text.strip()}\n",
            encoding="utf-8",
        )
        print(text.strip())
        print(f"-> scorer {model}, cost ${cost:.4f}" if isinstance(cost, (int, float)) else f"-> scorer {model}")
        print(f"-> evidence saved to {evidence.relative_to(ROOT).as_posix()}")

        stronger = any(k in model.lower() for k in ("opus", "fable"))
        if not stronger and not args.allow_scorer_mismatch:
            print(f"!! The scorer was {model}, not Opus. Not recording. Check that Opus is available to your seat, "
                  f"or re-run with --allow-scorer-mismatch to record anyway (the note will say so).")
            exit_code = 1
            continue

        wrote = generator_model(ROOT / args.record, prompt, version) if args.record else None
        if wrote and family(wrote) == family(model) and not args.allow_scorer_mismatch:
            print(f"!! {family(model)} is marking its own work: the answer was written by {wrote} and scored by {model}.")
            print(f"   Re-run the answer on a smaller model, then score again:")
            print(f"     python scripts/run.py <the prompt file> --name {prompt} --version {version} --model sonnet")
            print(f"   Or record it as it stands with --allow-scorer-mismatch (the ledger will say same-tier).")
            exit_code = 1
            continue
        if total is None:
            print("!! No 'TOTAL: n/25' line found. Read the evidence file and record the score by hand with scripts/ledger.py score.")
            exit_code = 1
            continue
        if args.record:
            same_tier = bool(wrote) and family(wrote) == family(model)
            note = f"scorer={model}" + (" (same tier as the writer)" if same_tier else "")
            record(ROOT / args.record if not Path(args.record).is_absolute() else Path(args.record),
                   prompt, version, total, note)
            print(f"-> recorded {prompt} {version} = {total}/25 in {args.record}")
        print()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
