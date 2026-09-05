"""Run a prompt and record what it cost. No copying numbers by hand.

    python scripts/run.py prompts/prompt-pack-v0/code-review.md --version v0

What it does, in one step:
  1. reads the prompt file (any <!-- comment --> at the top is stripped, so your
     notes to yourself cost nothing),
  2. runs it in a fresh Claude Code session on Sonnet - no memory of anything
     before it, so the numbers belong to this prompt and nothing else, and the
     Opus scorer is always a stronger model than the one that wrote the answer,
  3. reads the real token counts and cost back from that session,
  4. writes a row to week2/ledger.csv.

The prompt writes its own output file, exactly as it would if you pasted it into
the chat. Use --version to say which attempt this is (v0 for the original, v1
for your edit). The name in the ledger comes from the file name.

Standard library only. Needs Claude Code 2.1.211 or later on PATH.
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LEDGER = "week2/ledger.csv"
COMMENT = re.compile(r"(?s)<!--.*?-->")


def read_prompt(path: Path) -> str:
    text = COMMENT.sub("", path.read_text(encoding="utf-8")).strip()
    if not text:
        sys.exit(f"{path} is empty once comments are removed.")
    return text + "\n"


def run(prompt: str, model: str | None, budget: float) -> dict:
    exe = shutil.which("claude")
    if not exe:
        sys.exit("claude is not on PATH. Open a new terminal, or run  claude --version  to check the install.")
    cmd = [exe, "-p", "--output-format", "json", "--permission-mode", "acceptEdits",
           "--max-budget-usd", str(budget), "--no-session-persistence"]
    if model:
        cmd += ["--model", model]
    proc = subprocess.run(cmd, input=prompt, capture_output=True, text=True, cwd=ROOT, encoding="utf-8")
    if proc.returncode != 0:
        sys.exit("The run did not finish:\n" + (proc.stderr.strip() or proc.stdout.strip())[-500:])
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError:
        sys.exit("Claude did not return the expected data. First 300 characters:\n" + proc.stdout[:300])


def usage(payload: dict) -> tuple[str, int, int, int, int]:
    models = payload.get("modelUsage") or {}
    if not isinstance(models, dict) or not models:
        sys.exit("The run reported no token usage. Check  claude --version  is 2.1.211 or later.")
    name, u = max(models.items(), key=lambda kv: (kv[1] or {}).get("outputTokens", 0))
    g = lambda k: int((u or {}).get(k, 0) or 0)
    return name, g("inputTokens"), g("outputTokens"), g("cacheReadInputTokens"), g("cacheCreationInputTokens")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("prompt_file")
    ap.add_argument("--version", required=True, help="which attempt this is, e.g. v0 or v1")
    ap.add_argument("--name", help="ledger name; defaults to the prompt file name")
    ap.add_argument("--ledger", default=DEFAULT_LEDGER)
    ap.add_argument("--model", default="sonnet",
                    help="model that writes the answer. Defaults to sonnet so that the Opus scorer "
                         "is always a stronger model than the writer. Pass another alias to override.")
    ap.add_argument("--budget", type=float, default=2.0, help="stop the run if it would cost more than this")
    args = ap.parse_args()

    path = Path(args.prompt_file)
    if not path.is_absolute():
        path = ROOT / path
    if not path.exists():
        sys.exit(f"{args.prompt_file} does not exist. Check the name.")
    name = args.name or re.sub(r"-v\d+$", "", path.stem)

    print(f"Running {path.name} ... this takes a moment and writes its own output file.", flush=True)
    payload = run(read_prompt(path), args.model, args.budget)
    model, inp, out, cread, cwrite = usage(payload)
    cost = payload.get("total_cost_usd")
    if cost is None:
        sys.exit("The run reported no cost. Record it by hand with scripts/ledger.py add.")

    reply = (payload.get("result") or "").strip()
    if reply:
        print("Claude replied: " + reply.splitlines()[0][:160])

    ledger = Path(args.ledger)
    if not ledger.is_absolute():
        ledger = ROOT / ledger
    cmd = [sys.executable, str(ROOT / "scripts" / "ledger.py"), "add", str(ledger),
           "--prompt", name, "--version", args.version, "--model", model,
           "--input", str(inp), "--output", str(out),
           "--cache-read", str(cread), "--cache-write", str(cwrite), "--cost", str(cost)]
    add = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    if add.returncode != 0:
        sys.exit("Recording failed:\n" + (add.stderr or add.stdout).strip())
    print(add.stdout.strip())


if __name__ == "__main__":
    main()
