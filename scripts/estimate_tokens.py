"""Estimate the token size of prompt files before you run them.

    python scripts/estimate_tokens.py prompts/prompt-pack-v0/code-review.md
    python scripts/estimate_tokens.py prompts/prompt-pack-v0/*.md
    python scripts/estimate_tokens.py --compare prompts/prompt-pack-v0/code-review.md week2/prompts/v1/code-review.md

This is an estimate, not a measurement. English prose averages about four
characters per token on Claude's tokenizer, so the figure here is characters
divided by four, and is usually within 15 percent of the true count. The true
count for a run comes from /usage in Claude Code; this script exists so you can
see the size of a prompt before you pay for it, and compare two versions of the
same prompt on equal terms. Standard library only.
"""

import argparse
import glob
import sys
from pathlib import Path

CHARS_PER_TOKEN = 4.0


def estimate(path: Path) -> tuple[int, int, int]:
    text = path.read_text(encoding="utf-8")
    chars = len(text)
    words = len(text.split())
    return chars, words, int(round(chars / CHARS_PER_TOKEN))


def expand(patterns: list[str]) -> list[Path]:
    paths: list[Path] = []
    for pattern in patterns:
        matches = sorted(glob.glob(pattern))
        if not matches:
            sys.exit(f"No file matches {pattern}")
        paths += [Path(m) for m in matches]
    return paths


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("files", nargs="+", help="prompt files (globs allowed)")
    parser.add_argument("--compare", action="store_true",
                        help="treat files as pairs: before after [before after ...] and show the reduction")
    args = parser.parse_args()
    paths = expand(args.files)

    if args.compare:
        if len(paths) % 2:
            sys.exit("--compare needs pairs of files: before after")
        print(f"{'before':<44}{'after':<44}{'tokens':>16}{'change':>9}")
        print("-" * 113)
        total_a = total_b = 0
        for a, b in zip(paths[::2], paths[1::2]):
            _, _, ta = estimate(a)
            _, _, tb = estimate(b)
            total_a += ta
            total_b += tb
            print(f"{str(a):<44}{str(b):<44}{ta:>7,} -> {tb:<5,}{(tb - ta) / ta * 100:>+8.1f}%")
        if len(paths) > 2:
            print("-" * 113)
            print(f"{'ALL':<88}{total_a:>7,} -> {total_b:<5,}{(total_b - total_a) / total_a * 100:>+8.1f}%")
        return

    print(f"{'file':<52}{'chars':>8}{'words':>8}{'est. tokens':>13}")
    print("-" * 81)
    for path in paths:
        chars, words, tokens = estimate(path)
        print(f"{str(path):<52}{chars:>8,}{words:>8,}{tokens:>13,}")
    print("\nEstimate only (chars / 4). The real count for a run is in /usage.")


if __name__ == "__main__":
    main()
