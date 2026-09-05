"""Token ledger for the Claude Code Capability Program (Week 2).

Records one row per prompt run, taken from the Session block that Claude Code's
/usage command prints. Nothing is estimated here: every number is copied from a
real run. Standard library only.

Add a row by pasting the "Usage by model" line from /usage:

    python scripts/ledger.py add week2/ledger.csv --prompt ac --version v2000 --score 17 \
        --usage "claude-sonnet-5: 1.2k input, 5.3k output, 940.0k cache read, 50.0k cache write ($0.55)"

Or type the four counts and the cost yourself:

    python scripts/ledger.py add week2/ledger.csv --prompt ac --version v900 --score 19 \
        --input 1.1k --output 2.4k --cache-read 300k --cache-write 48k --cost 0.31

Attach a rubric score to a row you recorded earlier:

    python scripts/ledger.py score week2/ledger.csv --prompt ac --version v2000 --score 17 --judge opus

Show the ledger with fresh-token and cost deltas per prompt:

    python scripts/ledger.py show week2/ledger.csv

Facilitators: merge several participants' ledgers into one (a participant column
is added from each file name) and show room-level totals:

    python scripts/ledger.py merge room.csv bundles/*.csv
    python scripts/ledger.py show room.csv
"""

import argparse
import csv
import re
import sys
from datetime import datetime
from pathlib import Path

COLUMNS = [
    "recorded_at", "prompt", "version", "model", "input_tokens", "output_tokens",
    "cache_read_tokens", "cache_write_tokens", "fresh_tokens", "cost_usd",
    "rubric_score", "notes",
]

USAGE_LINE = re.compile(
    r"(?P<model>[A-Za-z0-9._-]+)\s*:\s*"
    r"(?P<input>[\d.,]+[kKmM]?)\s+input,\s*"
    r"(?P<output>[\d.,]+[kKmM]?)\s+output,\s*"
    r"(?P<cread>[\d.,]+[kKmM]?)\s+cache read,\s*"
    r"(?P<cwrite>[\d.,]+[kKmM]?)\s+cache write"
    r"(?:\s*\(\$?(?P<cost>[\d.]+)\))?"  # $ optional: PowerShell eats $0 inside double quotes
)


def to_int(value: str) -> int:
    """'1.2k' -> 1200, '940.0k' -> 940000, '2.1m' -> 2100000, '412' -> 412."""
    text = value.strip().replace(",", "")
    mult = 1
    if text[-1] in "kK":
        mult, text = 1_000, text[:-1]
    elif text[-1] in "mM":
        mult, text = 1_000_000, text[:-1]
    return int(round(float(text) * mult))


def fmt(n: int) -> str:
    return f"{n:,}"


def cmd_add(args: argparse.Namespace) -> None:
    path = Path(args.ledger)
    if args.usage:
        match = USAGE_LINE.search(args.usage)
        if not match:
            sys.exit(
                "Could not parse the usage line. It should look like:\n"
                "  claude-sonnet-5: 1.2k input, 5.3k output, 940.0k cache read, 50.0k cache write ($0.55)"
            )
        model = match.group("model")
        inp, out = to_int(match.group("input")), to_int(match.group("output"))
        cread, cwrite = to_int(match.group("cread")), to_int(match.group("cwrite"))
        cost = float(match.group("cost")) if match.group("cost") else args.cost
    else:
        missing = [n for n in ("input", "output", "cache_read", "cache_write")
                   if getattr(args, n) is None]
        if missing:
            sys.exit(f"Either give --usage, or all of --input --output --cache-read --cache-write. Missing: {', '.join(missing)}")
        if not args.model:
            sys.exit("Add --model with the model the run used (e.g. --model sonnet). The ledger needs it to keep comparisons like for like.")
        model = args.model
        inp, out = to_int(args.input), to_int(args.output)
        cread, cwrite = to_int(args.cache_read), to_int(args.cache_write)
        cost = args.cost
    if cost is None:
        sys.exit("No cost found. Add --cost with the Total cost figure from /usage, e.g. --cost 0.55")

    new_file = not path.exists() or path.stat().st_size == 0
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS)
        if new_file:
            writer.writeheader()
        writer.writerow({
            "recorded_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "prompt": args.prompt,
            "version": args.version,
            "model": model,
            "input_tokens": inp,
            "output_tokens": out,
            "cache_read_tokens": cread,
            "cache_write_tokens": cwrite,
            "fresh_tokens": inp + out,
            "cost_usd": f"{cost:.4f}",
            "rubric_score": args.score if args.score is not None else "",
            "notes": args.notes or "",
        })
    print(f"Added: {args.prompt} {args.version}  fresh {fmt(inp + out)} tokens "
          f"({fmt(inp)} in + {fmt(out)} out), cache read {fmt(cread)}, cost ${cost:.4f}"
          + (f", score {args.score}" if args.score is not None else ""))


def load(path: Path) -> list[dict]:
    if not path.exists():
        sys.exit(f"{path} does not exist yet. Add a row first.")
    with path.open(encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def cmd_score(args: argparse.Namespace) -> None:
    path = Path(args.ledger)
    rows = load(path)
    hits = [r for r in rows if r["prompt"] == args.prompt and r["version"] == args.version]
    if not hits:
        sys.exit(f"No row for prompt={args.prompt} version={args.version}. Rows present: "
                 + ", ".join(f"{r['prompt']}/{r['version']}" for r in rows))
    hits[-1]["rubric_score"] = str(args.score)
    if args.judge:
        existing = hits[-1].get("notes", "") or ""
        tag = f"scorer={args.judge}"
        hits[-1]["notes"] = (existing + "; " if existing and tag not in existing else "") + (tag if tag not in existing else existing)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Scored: {args.prompt} {args.version} = {args.score}/25" + (f"  (judge: {args.judge})" if args.judge else ""))


def cmd_merge(args: argparse.Namespace) -> None:
    out = Path(args.output)
    merged: list[dict] = []
    for src in args.inputs:
        for r in load(Path(src)):
            r = dict(r)
            r["notes"] = (f"[{Path(src).stem}] " + (r.get("notes") or "")).strip()
            merged.append(r)
    with out.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(merged)
    print(f"Merged {len(merged)} rows from {len(args.inputs)} ledger(s) into {out}. "
          f"Run: python scripts/ledger.py show {out}")


def cmd_show(args: argparse.Namespace) -> None:
    rows = load(Path(args.ledger))
    if not rows:
        sys.exit("Ledger is empty.")
    print(f"{'prompt':<14}{'version':<15}{'model':<12}{'fresh':>9}{'in':>8}{'out':>8}{'cache rd':>10}{'cost $':>9}{'score':>7}  {'scorer':<12}")
    print("-" * 106)
    for r in rows:
        model = r["model"].replace("claude-", "")[:11]
        scorer = ""
        for part in (r.get("notes") or "").split(";"):
            part = part.strip()
            if part.startswith(("scorer=", "judge=")):
                scorer = part.split("=", 1)[1].replace("claude-", "")[:11]
        print(f"{r['prompt']:<14}{r['version']:<15}{model:<12}{int(r['fresh_tokens']):>9,}"
              f"{int(r['input_tokens']):>8,}{int(r['output_tokens']):>8,}"
              f"{int(r['cache_read_tokens']):>10,}{float(r['cost_usd']):>9.4f}{r['rubric_score']:>7}  {scorer:<12}")

    # Deltas: compare the first version of each prompt against its latest.
    # If a version was run more than once, its most recent attempt is the one that counts.
    latest: dict[tuple[str, str], dict] = {}
    order: list[tuple[str, str]] = []
    for r in rows:
        key = (r["prompt"], r["version"])
        if key not in latest:
            order.append(key)
        latest[key] = r
    by_prompt: dict[str, list[dict]] = {}
    for key in order:
        by_prompt.setdefault(key[0], []).append(latest[key])
    multi = {p: v for p, v in by_prompt.items() if len(v) > 1}
    if not multi:
        return
    print("\nChange from first recorded version to latest, per prompt:")
    print(f"{'prompt':<16}{'versions':<24}{'fresh tokens':>14}{'cost':>9}{'score':>16}")
    print("-" * 79)
    t_first = t_last = c_first = c_last = 0.0
    for p, versions in multi.items():
        a, b = versions[0], versions[-1]
        fa, fb = int(a["fresh_tokens"]), int(b["fresh_tokens"])
        ca, cb = float(a["cost_usd"]), float(b["cost_usd"])
        if a["version"] == "v0":  # the ALL row is the hands-on activity's bar: v0 baselines only
            t_first += fa; t_last += fb; c_first += ca; c_last += cb
        tok_pct = (fb - fa) / fa * 100 if fa else 0.0
        cost_pct = (cb - ca) / ca * 100 if ca else 0.0
        sa, sb = a["rubric_score"], b["rubric_score"]
        score_txt = f"{sa} -> {sb}" if sa and sb else "-"
        if sa and sb and float(sa) > 0:
            score_txt += f" ({float(sb) / float(sa) * 100:.0f}%)"
        print(f"{p:<16}{a['version'] + ' -> ' + b['version']:<24}{tok_pct:>+13.1f}%{cost_pct:>+8.1f}%{score_txt:>16}")
    mixed = [p for p, v in multi.items() if len({r["model"] for r in v}) > 1]
    if mixed:
        print("\n!! Model changed between versions of: " + ", ".join(mixed)
              + ". Those comparisons are not like for like; start the RUN window with the same --model every time.")
    if t_first:
        print("-" * 79)
        print(f"{'ALL (v0 prompts)':<40}{(t_last - t_first) / t_first * 100:>+13.1f}%"
              f"{(c_last - c_first) / c_first * 100 if c_first else 0.0:>+8.1f}%")
        print("\nPassing bar for the hands-on activity: ALL fresh tokens down 35% or more,"
              "\nand no prompt's latest score below 90% of its first score.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    add = sub.add_parser("add", help="append one run to the ledger")
    add.add_argument("ledger")
    add.add_argument("--prompt", required=True, help="short name, e.g. ac, code-review")
    add.add_argument("--version", required=True, help="e.g. v2000, v0, v1")
    add.add_argument("--usage", help='the "Usage by model" line from /usage, in quotes')
    add.add_argument("--model")
    add.add_argument("--input")
    add.add_argument("--output")
    add.add_argument("--cache-read", dest="cache_read")
    add.add_argument("--cache-write", dest="cache_write")
    add.add_argument("--cost", type=float, help="Total cost from /usage, e.g. 0.55")
    add.add_argument("--score", type=int, help="rubric score out of 25")
    add.add_argument("--notes")
    add.set_defaults(func=cmd_add)

    score = sub.add_parser("score", help="attach a rubric score to a recorded run")
    score.add_argument("ledger")
    score.add_argument("--prompt", required=True)
    score.add_argument("--version", required=True)
    score.add_argument("--score", required=True, type=int, help="rubric score out of 25")
    score.add_argument("--judge", help="which model scored it, e.g. opus. scripts/score.py fills this in automatically")
    score.set_defaults(func=cmd_score)

    merge = sub.add_parser("merge", help="facilitator: combine several ledgers into one")
    merge.add_argument("output")
    merge.add_argument("inputs", nargs="+")
    merge.set_defaults(func=cmd_merge)

    show = sub.add_parser("show", help="print the ledger with deltas")
    show.add_argument("ledger")
    show.set_defaults(func=cmd_show)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
