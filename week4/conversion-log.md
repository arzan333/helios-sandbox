# Conversion log

Two source specifications were converted to Markdown. Both commands were run
from the repository root.

## Commands

    pandoc docs/specs/ordercore-fsd.docx -t gfm -o week4/raw/fsd.md
    python -m markitdown docs/specs/ordercore-techspec.pdf -o week4/raw/techspec.md

## Which converter read which format

| Source | Format | Converter | Output |
| --- | --- | --- | --- |
| `docs/specs/ordercore-fsd.docx` | Word (.docx) | pandoc 3.10.2, GitHub-flavoured Markdown (`-t gfm`) | `week4/raw/fsd.md` |
| `docs/specs/ordercore-techspec.pdf` | PDF | markitdown, run as `python -m markitdown` | `week4/raw/techspec.md` |

## Exit codes

| Command | Exit code |
| --- | --- |
| `pandoc docs/specs/ordercore-fsd.docx -t gfm -o week4/raw/fsd.md` | 0 |
| `python -m markitdown docs/specs/ordercore-techspec.pdf -o week4/raw/techspec.md` | 0 |

Both converters exited 0. Neither output file was edited after conversion; they
are the raw converter output.
