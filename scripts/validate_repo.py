"""Validate the Helios sandbox.

Checks structure, file syntax, front matter, and - most importantly - that every
path mentioned in the documentation actually exists. Cross-references rot fast in
a repository that grows a week at a time.

Run:  python scripts/validate_repo.py
"""

import csv
import html
import json
import re
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

failures = []
warnings = []
checks = 0


def check(condition, message):
    global checks
    checks += 1
    if not condition:
        failures.append(message)
    return condition


def warn(condition, message):
    global checks
    checks += 1
    if not condition:
        warnings.append(message)


# --------------------------------------------------------------- structure
REQUIRED = [
    "README.md",
    "CLAUDE.md",
    ".gitignore",
    "apps/ordercore/app/main.py",
    "apps/ordercore/app/models.py",
    "apps/ordercore/app/store.py",
    "apps/ordercore/app/billing_client.py",
    "apps/ordercore/tests/test_orders.py",
    "apps/ordercore/data/orders.json",
    "apps/ordercore/requirements.txt",
    "apps/billing/pom.xml",
    "apps/billing/src/main/java/com/helios/billing/BillingServer.java",
    "apps/billing/src/main/java/com/helios/billing/InvoiceCalculator.java",
    "apps/billing/src/main/java/com/helios/billing/Json.java",
    "apps/shop/package.json",
    "apps/shop/src/App.jsx",
    "apps/shop/src/api.js",
    "apps/insight/report.py",
    "data/helios-tickets.csv",
    "data/entity-map.md",
    "docs/helios-landscape.md",
    "docs/process/request-to-release.md",
    "docs/design/HEL-142-hld.md",
    "labs/week1.html",
    "rubrics/hld.md",
    "rubrics/lld.md",
    "templates/blueprint-canvas.md",
    "templates/self-check-8.md",
    "templates/baseline-capture.md",
    "skills/example-skill/SKILL.md",
    "scripts/generate_tickets.py",
]

for rel in REQUIRED:
    check((ROOT / rel).exists(), f"missing required file: {rel}")

# ------------------------------------------------------------------- JSON
for path in sorted(ROOT.glob("helios-backlog/*.json")) + [ROOT / "apps/ordercore/data/orders.json"]:
    try:
        json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        failures.append(f"invalid JSON in {path.relative_to(ROOT)}: {exc}")
    checks += 1

backlog = sorted(ROOT.glob("helios-backlog/*.json"))
check(len(backlog) == 12, f"expected 12 backlog tickets, found {len(backlog)}")

# --------------------------------------------------------------- CSV shape
csv_path = ROOT / "data" / "helios-tickets.csv"
with csv_path.open(encoding="utf-8") as handle:
    rows = list(csv.DictReader(handle))

STAGES = [
    "created", "triaged", "analysis_start", "analysis_done", "design_start",
    "design_done", "build_start", "build_done", "test_start", "test_done",
    "deployed", "closed",
]

check(len(rows) == 210, f"expected 210 ticket rows, found {len(rows)}")
check(all(s in rows[0] for s in STAGES), "CSV is missing one or more stage columns")

ids = {r["ticket_id"] for r in rows}
check("HEL-142" in ids, "HEL-142 is referenced by the Week 1 lab but missing from the CSV")
check("HEL-207" in ids, "HEL-207 is referenced by the Week 3 lab but missing from the CSV")
check(len(ids) == len(rows), "duplicate ticket_id values in the CSV")

out_of_order = 0
for row in rows:
    stamps = [datetime.strptime(row[s], "%Y-%m-%d %H:%M") for s in STAGES]
    if any(b < a for a, b in zip(stamps, stamps[1:], strict=False)):
        out_of_order += 1
check(out_of_order == 0, f"{out_of_order} rows have stage timestamps out of order")

workflows = {r["workflow"] for r in rows}
for required_workflow in ["request_to_release", "defect_triage", "release_notes", "change_approval"]:
    check(
        required_workflow in workflows,
        f"workflow '{required_workflow}' is offered in the lab but absent from the CSV",
    )

# ---------------------------------------------- backlog agrees with the CSV
by_id = {r["ticket_id"]: r for r in rows}
for path in backlog:
    ticket = json.loads(path.read_text(encoding="utf-8"))
    key = ticket["key"]
    check(key in by_id, f"{path.name} has key {key} which is not in the CSV")
    if key in by_id:
        check(
            ticket["summary"] == by_id[key]["title"],
            f"{key} summary does not match the CSV title "
            f"({ticket['summary']!r} vs {by_id[key]['title']!r})",
        )

# ------------------------------------------------------------- front matter
FRONT_MATTER_REQUIRED = [
    "data/entity-map.md",
    "docs/helios-landscape.md",
    "docs/process/request-to-release.md",
    "docs/process/defect-triage.md",
    "docs/process/release-notes.md",
    "docs/process/change-approval.md",
    "docs/design/HEL-142-hld.md",
    "rubrics/hld.md",
    "rubrics/lld.md",
]
for rel in FRONT_MATTER_REQUIRED:
    text = (ROOT / rel).read_text(encoding="utf-8")
    check(text.startswith("---\n"), f"{rel} has no front matter block")
    header = text.split("---", 2)[1] if text.startswith("---") else ""
    check("owner:" in header, f"{rel} front matter has no owner")

# ------------------------------------------------ cross-reference integrity
# Any repo-relative path mentioned in a markdown or html file must exist.
PATH_PATTERN = re.compile(
    r"`((?:apps|data|docs|labs|rubrics|templates|scripts|skills|helios-backlog)/[A-Za-z0-9_./<>-]+)`"
)
doc_files = (
    list(ROOT.glob("*.md"))
    + list(ROOT.glob("docs/**/*.md"))
    + list(ROOT.glob("rubrics/*.md"))
    + list(ROOT.glob("templates/*.md"))
    + list(ROOT.glob("skills/**/*.md"))
    + list(ROOT.glob("data/*.md"))
)
for doc in doc_files:
    for match in PATH_PATTERN.findall(doc.read_text(encoding="utf-8")):
        if "<" in match or match.endswith("/"):
            continue  # placeholder like docs/process/<workflow>.md
        checks += 1
        if not (ROOT / match).exists():
            failures.append(f"{doc.relative_to(ROOT)} references missing path: {match}")

# ----------------------------------------------------- lab book references
lab = (ROOT / "labs" / "week1.html").read_text(encoding="utf-8")
for referenced in [
    "docs/process/request-to-release.md",
    "templates/blueprint-canvas.md",
    "templates/self-check-8.md",
    "data/helios-tickets.csv",
    "docs/design/HEL-142-hld.md",
    "docs/helios-landscape.md",
]:
    # Windows snippets legitimately use backslashes, so accept either separator.
    variants = (referenced, referenced.replace("/", "\\"))
    check(any(v in lab for v in variants),
          f"week1.html does not reference {referenced}")

check(lab.count("snippet__copy") >= 6, "week1.html should have at least 6 copy buttons")

# Step 0 must give participants everything needed to reach step 1 unaided.
for needed, why in [
    ("git clone https://github.com/arzan333/helios-sandbox.git", "the clone command"),
    ("git checkout -b", "the branch command"),
    ("git config core.hooksPath .githooks", "the push guard"),
    ("Set up your working copy", "the step 0 heading"),
    ("What you will do", "the five-step summary"),
    ("week1/blueprint.md", "the named deliverable"),
    ("blueprint-defect-triage.md", "the link to the worked example"),
    ("The process you are analysing", "the process framing"),
    ("The three categories.", "the AI-ready definition at point of use"),
    ("What a gate is", "the gate definition at point of use"),
    ("Queue or effort.", "the queue vs effort definition at point of use"),
    ("gets a gate after it", "the rule that AI steps require a gate"),
    ("Challenge", "the swap and critique challenge"),
    ("Escalation trigger", "the full gate column set"),
    ("A target without a number is a wish", "the metrics discipline line"),
]:
    check(needed in lab, f"week1.html is missing {why}")

# The canvas must be created before it is first referenced.
canvas_created = lab.find("blueprint-canvas.md")
canvas_used = lab.find("section 1</b> of your blueprint")
check(canvas_created != -1 and canvas_used != -1 and canvas_created < canvas_used,
      "week1.html references the canvas before creating it")
check("&lt;" not in lab.split("<pre>")[0], "unescaped markup before the first snippet")

# Copy blocks must be plain ASCII, or paste breaks in a terminal.
for snippet in re.findall(r"<pre><code>(.*?)</code></pre>", lab, re.S):
    checks += 1
    non_ascii = [c for c in snippet if ord(c) > 127]
    if non_ascii:
        failures.append(f"non-ASCII character in a copy block: {non_ascii[:3]}")

# ------------------------------------------------- contract consistency
billing_java = (ROOT / "apps/billing/src/main/java/com/helios/billing/BillingServer.java").read_text()
client_py = (ROOT / "apps/ordercore/app/billing_client.py").read_text()
for field in ["orderId", "currency", "lines"]:
    check(field in billing_java and field in client_py,
          f"request field '{field}' is not present on both sides of the Billing contract")
calc_java = (ROOT / "apps/billing/src/main/java/com/helios/billing/InvoiceCalculator.java").read_text()
for field in ["subtotalPence", "taxPence", "totalPence"]:
    check(field in calc_java and field in client_py,
          f"response field '{field}' is not present on both sides of the Billing contract")

# Tax rate must agree between the Java service and the Python fallback.
java_rate = re.search(r"TAX_RATE_PERCENT\s*=\s*(\d+)", calc_java)
py_rate = re.search(r"TAX_RATE_PERCENT\s*=\s*(\d+)", client_py)
check(java_rate and py_rate and java_rate.group(1) == py_rate.group(1),
      "tax rate differs between Billing and the OrderCore fallback")

# The Shop must call OrderCore through the proxy path only.
api_js = (ROOT / "apps/shop/src/api.js").read_text()
check("localhost:8080" not in api_js, "Shop hardcodes the OrderCore port; use the /api proxy")
vite = (ROOT / "apps/shop/vite.config.js").read_text()
check("8080" in vite, "Vite proxy does not point at OrderCore on 8080")

# ------------------------------------------------------------------ report
# Every PowerShell block must be runnable from any directory. Claude Code takes
# over the terminal in step 0e, so participants paste later blocks into a new one.
_blocks = re.findall(
    r'<span class="snippet__lang">powershell</span>.*?<pre><code>(.*?)</code></pre>',
    lab, re.S)
_nocd = [b for b in _blocks if not html.unescape(b).strip().startswith(("cd ", "mkdir "))]
check(len(_nocd) == 0,
      f"{len(_nocd)} PowerShell block(s) in week1.html do not set their own directory")
check("takes over this PowerShell window" in lab,
      "week1.html does not warn that Claude Code occupies the terminal")

# Every prompt must be runnable on its own. A prompt that says "my table" without
# naming the file it lives in cannot be executed in one shot.
_prompts = re.findall(
    r'<span class="snippet__lang">prompt</span>.*?<pre><code>(.*?)</code></pre>',
    lab, re.S)
for _i, _b in enumerate(_prompts, 1):
    _txt = html.unescape(_b)
    _refs = re.findall(r'(?:docs|data|apps|templates|week1)/[A-Za-z0-9_./-]+', _txt)
    check(len(_refs) > 0, f"prompt {_i} in week1.html names no file for Claude to read")

# Section numbers the lab writes into must exist in the canvas, and the self-check
# must not cite a section that has been renamed or removed.
_canvas = (ROOT / "templates" / "blueprint-canvas.md").read_text(encoding="utf-8")
_chk = (ROOT / "templates" / "self-check-8.md").read_text(encoding="utf-8")
_canvas_secs = set(re.findall(r"^## (\d)\.", _canvas, re.M))
for _s in sorted(set(re.findall(r"section (\d)", lab))):
    check(_s in _canvas_secs, f"lab writes into section {_s} but the canvas has no such section")
for _s in sorted(set(re.findall(r"section (\d)", _chk))):
    check(_s in _canvas_secs, f"self-check cites section {_s} but the canvas has no such section")
check("target state" not in _chk.lower(),
      "self-check still references the removed 'target state' section")
check("The new process" in _canvas, "canvas section 3 is not the rewritten step list")

# The four phases quoted in step 3 must account for all sixteen steps.
_cov = set()
for _a, _b in re.findall(r"steps? (\d+)[\u2013-](\d+)", html.unescape(lab).lower()):
    _cov |= set(range(int(_a), int(_b) + 1))
check(set(range(1, 17)) <= _cov,
      f"step 3 phase ranges do not cover all sixteen steps, missing {sorted(set(range(1,17)) - _cov)}")

# One vocabulary across the lab, the template and the worked example. A column
# renamed in one place and not the others is how a participant gets lost.
_ex = (ROOT / "docs" / "examples" / "blueprint-defect-triage.md").read_text(encoding="utf-8")
_lab_plain = html.unescape(lab)
for _sec_body in re.findall(r"^## \d\. .+?$(.*?)(?=^## |\Z)", _canvas, re.M | re.S):
    _hdr = re.search(r"^\|(.+?)\|\s*$", _sec_body, re.M)
    if not _hdr:
        continue
    for _col in [c.strip() for c in _hdr.group(1).split("|") if c.strip()]:
        check(_col in _ex, f"worked example does not use canvas column '{_col}'")
for _term in ["queue", "effort", "AI-ready", "AI-assisted", "human-only",
              "Bounded", "Checkable", "Reversible", "Escalation trigger"]:
    check(_term.lower() in _lab_plain.lower(), f"lab never uses the term '{_term}'")
    check(_term.lower() in _ex.lower(), f"worked example never uses the term '{_term}'")

readme = (ROOT / "README.md").read_text(encoding="utf-8")
check("baseline-capture.md" in readme, "README does not mention the baseline capture step")

# ------------------------------------------------- worked example blueprint
example = ROOT / "docs" / "examples" / "blueprint-defect-triage.md"
check(example.exists(), "worked example blueprint is missing")
if example.exists():
    ex = example.read_text(encoding="utf-8")
    _canvas_titles = re.findall(r"^## (\d\. .+)$", _canvas, re.M)
    for section in _canvas_titles:
        check(section in ex,
              f"worked example is missing section '{section}' that the canvas defines")
    check("Bounded?" in ex and "Who does it now" in ex,
          "worked example does not use the current table columns")
    check("551.6" in ex, "worked example cycle time does not match the dataset")
    check("29.5%" in ex, "worked example rework rate does not match the dataset")
    check("defect_triage" in ex, "worked example does not name its scenario")

print(f"Ran {checks} checks.\n")
if warnings:
    print(f"{len(warnings)} warning(s):")
    for item in warnings:
        print(f"  ! {item}")
    print()
if failures:
    print(f"{len(failures)} FAILURE(S):")
    for item in failures:
        print(f"  x {item}")
    sys.exit(1)

print("All checks passed.")
