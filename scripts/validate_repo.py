"""Validate the Helios sandbox.

Checks structure, file syntax, front matter, and - most importantly - that every
path mentioned in the documentation actually exists. Cross-references rot fast in
a repository that grows a week at a time.

Run:  python scripts/validate_repo.py
"""

import csv
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
    "docs/process/requirement-intake.md",
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
for required_workflow in ["intake", "defect_triage", "release_notes", "change_approval"]:
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
    "docs/process/requirement-intake.md",
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
    "docs/process/requirement-intake.md",
    "docs/process/defect-triage.md",
    "docs/process/release-notes.md",
    "docs/process/change-approval.md",
    "templates/blueprint-canvas.md",
    "templates/self-check-8.md",
    "data/helios-tickets.csv",
    "docs/design/HEL-142-hld.md",
    "docs/helios-landscape.md",
]:
    check(referenced in lab, f"week1.html does not reference {referenced}")

check(lab.count("snippet__copy") >= 6, "week1.html should have at least 6 copy buttons")
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
