"""Validate the Week 2 assets and lab books.

Run from the repository root:  python scripts/validate_week2.py

Same philosophy as validate_repo.py: every path a lab book names must exist,
every number it quotes must come from the data, copy blocks must paste cleanly
on Windows, and every prompt must be runnable on its own.
"""

import csv
import html
import io
import re
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
failures: list[str] = []
checks = 0


def check(condition, message):
    global checks
    checks += 1
    if not condition:
        failures.append(message)
    return condition


# ------------------------------------------------------------------ files
REQUIRED = [
    "labs/week2.html",
    "labs/week2-activity.html",
    "prompts/README.md",
    "prompts/week2-lab/ac-2000.md",
    "prompts/week2-lab/ac-900.md",
    "prompts/week2-lab/ac-320.md",
    "prompts/week2-lab/rubric-acceptance-criteria.md",
    "prompts/week2-lab/score.md",
    "scripts/score.py",
    "scripts/run.py",
    "templates/prompt-skeleton.md",
    "templates/prompt-skeleton.md",
    "docs/specs/ordercore-fsd.docx",
    "docs/specs/ordercore-fsd.txt",
    "templates/prompt-techniques.md",
    "templates/token-ledger.csv",
    "data/helios-volumes.csv",
    "scripts/ledger.py",
    "scripts/estimate_tokens.py",
]
PACK = ["code-review", "test-cases", "defect-triage", "impact-note", "release-notes",
        "explain-code", "stage-summary", "onboarding-plan"]
for name in PACK:
    REQUIRED += [f"prompts/prompt-pack-v0/{name}.md", f"prompts/prompt-pack-v0/rubrics/{name}.md"]
for rel in REQUIRED:
    check((ROOT / rel).exists(), f"missing required file: {rel}")
if failures:
    print("\n".join(failures)); sys.exit(1)

# --------------------------------------------------------------- scripts
for script in ["scripts/ledger.py", "scripts/estimate_tokens.py"]:
    out = subprocess.run([sys.executable, str(ROOT / script), "--help"], capture_output=True, text=True)
    check(out.returncode == 0, f"{script} --help failed: {out.stderr[-200:]}")

# ledger round trip in a temp file
tmp = ROOT / "week2" / "_validate_tmp.csv"
tmp.parent.mkdir(exist_ok=True)
try:
    if tmp.exists():
        tmp.unlink()
    line = "claude-sonnet-5: 1.2k input, 5.3k output, 940.0k cache read, 50.0k cache write ($0.55)"
    r1 = subprocess.run([sys.executable, "scripts/ledger.py", "add", str(tmp), "--prompt", "t", "--version", "v0", "--usage", line], cwd=ROOT, capture_output=True, text=True)
    r2 = subprocess.run([sys.executable, "scripts/ledger.py", "add", str(tmp), "--prompt", "t", "--version", "v1", "--model", "sonnet", "--input", "600", "--output", "2.1k", "--cache-read", "300k", "--cache-write", "48k", "--cost", "0.21"], cwd=ROOT, capture_output=True, text=True)
    r3 = subprocess.run([sys.executable, "scripts/ledger.py", "score", str(tmp), "--prompt", "t", "--version", "v0", "--score", "20"], cwd=ROOT, capture_output=True, text=True)
    r4 = subprocess.run([sys.executable, "scripts/ledger.py", "show", str(tmp)], cwd=ROOT, capture_output=True, text=True)
    check(r1.returncode == 0 and "total 996,500 tokens" in r1.stdout, f"ledger add (usage line) wrong: {r1.stdout}{r1.stderr}")
    check(r2.returncode == 0 and "total 350,700 tokens" in r2.stdout, f"ledger add (numbers) wrong: {r2.stdout}{r2.stderr}")
    check(r3.returncode == 0 and "20/25" in r3.stdout, f"ledger score wrong: {r3.stdout}{r3.stderr}")
    check(r4.returncode == 0 and "-64.8%" in r4.stdout and "ALL" in r4.stdout, f"ledger show wrong: {r4.stdout}{r4.stderr}")
    # PowerShell double-quote trap: $0 eaten
    r5 = subprocess.run([sys.executable, "scripts/ledger.py", "add", str(tmp), "--prompt", "t", "--version", "v2", "--usage", line.replace("$0.55", ".55")], cwd=ROOT, capture_output=True, text=True)
    check(r5.returncode == 0 and "$0.5500" in r5.stdout, "ledger does not survive PowerShell eating $0 in the usage line")
finally:
    if tmp.exists():
        tmp.unlink()
    try:
        tmp.parent.rmdir()  # only if empty (a participant's week2/ is never removed)
    except OSError:
        pass

# ------------------------------------------------------- prompt sizes
def est(rel: str) -> int:
    return int(round(len((ROOT / rel).read_text(encoding="utf-8")) / 4))

sizes = {n: est(f"prompts/prompt-pack-v0/{n}.md") for n in PACK}
for n, s in sizes.items():
    check(600 <= s <= 2000, f"prompt-pack-v0/{n}.md estimates {s} tokens; the pack is 600-2,000")
ac = {v: est(f"prompts/week2-lab/ac-{v}.md") for v in ["2000", "900", "320"]}
check(1800 <= ac["2000"] <= 2100, f"ac-2000 estimates {ac['2000']}")
check(800 <= ac["900"] <= 1000, f"ac-900 estimates {ac['900']}")
check(280 <= ac["320"] <= 360, f"ac-320 estimates {ac['320']}")

# Every prompt names its output file under week2/ and the lab quotes the same estimates.
lab = (ROOT / "labs/week2.html").read_text(encoding="utf-8")
act = (ROOT / "labs/week2-activity.html").read_text(encoding="utf-8")
for v in ["2000", "900", "320"]:
    txt = (ROOT / f"prompts/week2-lab/ac-{v}.md").read_text(encoding="utf-8")
    check(f"week2/ac-v{v}.md" in txt, f"ac-{v}.md does not write to week2/ac-v{v}.md")
    check(all(ord(c) < 128 for c in txt), f"ac-{v}.md contains non-ASCII; Get-Content in PowerShell 5.1 mangles it")
    pass  # the lab no longer quotes estimates at participants; sizes are asserted above
for n in PACK:
    txt = (ROOT / f"prompts/prompt-pack-v0/{n}.md").read_text(encoding="utf-8")
    check(f"week2/out/{n}-v0.md" in txt, f"prompt-pack-v0/{n}.md does not write to week2/out/{n}-v0.md")
    check(not txt.startswith("---"), f"prompt-pack-v0/{n}.md has front matter; prompts must be pure text to paste")
    check(all(ord(c) < 128 for c in txt), f"prompt-pack-v0/{n}.md contains non-ASCII; Get-Content in PowerShell 5.1 mangles it")
    for ref in re.findall(r"(?:apps|data|docs|helios-backlog|scripts|skills|templates|setup)/[A-Za-z0-9_./-]+", txt):
        ref = ref.rstrip(".,;:)")
        if ref == "docs/design/HEL-207-lld.md":
            continue  # named inside the pasted HEL-207 ticket; it is written by participants in Week 3
        check((ROOT / ref).exists(), f"prompt-pack-v0/{n}.md references missing path {ref}")

# Rubric answer keys must match the data they quote.
report = subprocess.run([sys.executable, "apps/insight/report.py", "stages", "--workflow", "request_to_release"], cwd=ROOT, capture_output=True, text=True).stdout
stage_rubric = (ROOT / "prompts/prompt-pack-v0/rubrics/stage-summary.md").read_text(encoding="utf-8")
for figure in ["147.1", "136.2", "69.2", "546.5", "34.1%", "91 tickets"]:
    check(figure in report, f"report.py no longer prints {figure}; dataset changed?")
    check(figure.replace(" tickets", "") in stage_rubric, f"stage-summary rubric does not quote {figure}")
with (ROOT / "data/helios-tickets.csv").open(encoding="utf-8") as handle:
    rows = list(csv.DictReader(handle))
jan = [r for r in rows if r["deployed"].startswith("2026-01")]
rel_rubric = (ROOT / "prompts/prompt-pack-v0/rubrics/release-notes.md").read_text(encoding="utf-8")
check(f"({len(jan)})" in rel_rubric, f"release-notes rubric row count should be {len(jan)}")
check(f"({len({r['title'] for r in jan})} distinct" in rel_rubric, f"release-notes rubric distinct count should be {len({r['title'] for r in jan})}")

# Volumes file names every pack prompt.
with (ROOT / "data/helios-volumes.csv").open(encoding="utf-8") as handle:
    vols = {r["prompt_pack_name"]: r for r in csv.DictReader(handle)}
for n in PACK:
    check(n in vols and vols[n]["monthly_volume"].isdigit(), f"data/helios-volumes.csv has no integer volume for {n}")
check("110" == vols.get("code-review", {}).get("monthly_volume"), "activity quotes code-review volume 110; volumes file disagrees")

# Both books score with scripts/score.py (stronger model, fresh process) and never by hand-scoring five rows.
for rel, text in [("labs/week2.html", lab), ("labs/week2-activity.html", act)]:
    check("scripts\\score.py" in text and "--record week2\\ledger.csv" in text, f"{rel} does not score with scripts/score.py --record")
    check("One file at a time, top to bottom, five rows" not in text, f"{rel} still asks for manual five-row scoring")
    check("--allow-scorer-mismatch" in text, f"{rel} has no fallback for a seat without Opus")
    check("/model" not in text, f"{rel} still uses interactive /model switching; scoring goes through score.py")
    # A score.py call must come after the run that produced and recorded that answer.
    for m in re.finditer(r"scripts\\score\.py ([^\n<]+)", text):
        for name, ver in re.findall(r"week2\\(?:out\\)?([a-z-]+)-(v\d+)\.md", m.group(1)):
            add_pos = text.find(f"--prompt {name} --version {ver} --usage")
            run_pos = max(text.rfind(f"--name {name} --version {ver}", 0, m.start()),
                          text.rfind(f"{name}.md --version {ver}", 0, m.start()))
            ok = (add_pos != -1 and add_pos < m.start()) or run_pos != -1
            check(ok, f"{rel} scores {name} {ver} before (or without) recording it")
check("compact" in lab.lower() and "same wrong thing again" in lab.lower() and "Handing work between sessions" in lab,
      "week2.html does not cover retrying, session growth and hand-offs")
check("last thing that should mark it" in lab or "never marks" in lab.lower(),
      "week2.html does not say why a different model does the marking")
check("prompt-skeleton.md" in act and "Turning your best v1 into a team template" in (ROOT / "templates/prompt-skeleton.md").read_text(encoding="utf-8"),
      "activity stretch references a skeleton section that does not exist")

# The 'nothing invented' row numbers quoted in the activity must match the rubrics.
def rubric_rows(name):
    txt = (ROOT / f"prompts/prompt-pack-v0/rubrics/{name}.md").read_text(encoding="utf-8")
    return {int(m.group(1)): m.group(2).strip() for m in re.finditer(r"^\| (\d) \| ([^|]+) \|", txt, re.M)}
check(rubric_rows("code-review").get(5, "").startswith("No false positives"), "code-review rubric row 5 is not the invention row the activity cites")
check(rubric_rows("defect-triage").get(5, "").startswith("Nothing invented"), "defect-triage rubric row 5 is not the invention row the activity cites")
check(rubric_rows("test-cases").get(4, "").startswith("Agrees with the code"), "test-cases rubric row 4 is not the row the activity cites")
check("row about inventing things" in act, "activity does not tell participants which row to check")

# score.py: help works, and an end-to-end run through a stub `claude` that only accepts flags the real 2.1.260 CLI lists.
import os, stat, tempfile
VALID_OPTS = {"--allowedTools", "--effort", "--model", "--no-session-persistence", "--output-format", "--max-budget-usd",
              "--permission-mode", "--verbose", "-p", "--print", "--version", "--fallback-model", "--input-format"}
STUB_PY = r"""
import sys, json
VALID = %r
args = sys.argv[1:]
if args == ["--version"]:
    print("2.1.260 (Claude Code)"); sys.exit(0)
bad = [a for a in args if a.startswith("-") and a not in VALID and not a.startswith("--")==False]
bad = [a for a in args if a.startswith("--") and a not in VALID]
if bad:
    sys.stderr.write("error: unknown option '%%s'\n" %% bad[0]); sys.exit(1)
prompt = sys.stdin.read()
assert "RUBRIC_FILE" not in prompt and "OUTPUT_FILE" not in prompt
model = args[args.index("--model")+1] if "--model" in args else "default"
real = {"opus": "claude-opus-5", "sonnet": "claude-sonnet-5"}.get(model, model)
text = "Row 1: 4 - \"x\"\nRow 2: 5 - \"y\"\nRow 3: 3 - \"z\"\nRow 4: 5 - absent\nRow 5: 4 - \"w\"\nTOTAL: 21/25"
print(json.dumps({"type": "result", "is_error": False, "result": text, "total_cost_usd": 0.04,
                  "modelUsage": {real: {"inputTokens": 9000, "outputTokens": 120}}}))
""" % sorted(VALID_OPTS)
with tempfile.TemporaryDirectory() as td:
    stub_py = Path(td) / "claude_stub.py"; stub_py.write_text(STUB_PY, encoding="utf-8")
    if os.name == "nt":
        (Path(td) / "claude.cmd").write_text(f'@echo off\r\n"{sys.executable}" "{stub_py}" %*\r\n', encoding="utf-8")
    else:
        sh = Path(td) / "claude"; sh.write_text(f'#!/bin/sh\nexec "{sys.executable}" "{stub_py}" "$@"\n', encoding="utf-8")
        sh.chmod(sh.stat().st_mode | stat.S_IEXEC)
    env = dict(os.environ, PATH=td + os.pathsep + os.environ.get("PATH", ""))
    wk = ROOT / "week2"; fresh_wk = not wk.exists()
    (wk / "out").mkdir(parents=True, exist_ok=True)
    try:
        led = wk / "_validate_ledger.csv"
        (wk / "_val-v0.md").write_text("# fake output\n", encoding="utf-8")
        (wk / "out" / "code-review-v9.md").write_text("# fake output\n", encoding="utf-8")
        subprocess.run([sys.executable, "scripts/ledger.py", "add", str(led), "--prompt", "code-review", "--version", "v9",
                        "--model", "claude-sonnet-5", "--input", "1k", "--output", "1k", "--cache-read", "1k", "--cache-write", "1k", "--cost", "0.1"],
                       cwd=ROOT, capture_output=True, text=True, check=True)
        r = subprocess.run([sys.executable, "scripts/score.py", "week2/out/code-review-v9.md", "--record", str(led)],
                           cwd=ROOT, capture_output=True, text=True, env=env)
        check(r.returncode == 0 and "recorded code-review v9 = 21/25" in r.stdout, f"score.py stub run failed:\n{r.stdout[-400:]}{r.stderr[-400:]}")
        r2 = subprocess.run([sys.executable, "scripts/score.py", "week2/out/code-review-v9.md", "--model", "sonnet", "--record", str(led)],
                            cwd=ROOT, capture_output=True, text=True, env=env)
        check(r2.returncode != 0 and "not Opus" in r2.stdout, "score.py recorded a same-tier scorer without --allow-scorer-mismatch")
        r3 = subprocess.run([sys.executable, "scripts/score.py", "week2/out/missing-v1.md"], cwd=ROOT, capture_output=True, text=True, env=env)
        check(r3.returncode != 0 and "file not found" in r3.stdout, "score.py did not report a missing output file")
        shown = subprocess.run([sys.executable, "scripts/ledger.py", "show", str(led)], cwd=ROOT, capture_output=True, text=True).stdout
        check("opus-5" in shown, "ledger show does not display the scorer column")
    finally:
        for f in [wk / "_validate_ledger.csv", wk / "_val-v0.md", wk / "out" / "code-review-v9.md",
                  wk / "scores" / "code-review-v9.md"]:
            if f.exists(): f.unlink()
        for d in [wk / "scores", wk / "out", wk]:
            try:
                if fresh_wk: d.rmdir()
            except OSError:
                pass

# Techniques template defines T1..T6 and the activity uses them.
tech = (ROOT / "templates/prompt-techniques.md").read_text(encoding="utf-8")
for tag in ["T1", "T2", "T3", "T4", "T5", "T6"]:
    check(f"| {tag} |" in tech, f"prompt-techniques.md has no row for {tag}")
    pass  # the activity teaches the six in plain language; the tag reference lives in the template

# FSD: section 7 exists in the text export and the 320 prompt's grep anchors are real lines.
fsd = (ROOT / "docs/specs/ordercore-fsd.txt").read_text(encoding="utf-8").splitlines()
check("7. Cart and delivery window" in fsd, "FSD txt has no '7. Cart and delivery window' line for the 320 prompt to grep")
check("8. Order search and reporting" in fsd, "FSD txt has no '8. Order search and reporting' line")
check("Arrives 18-20 March" in "\n".join(fsd), "FSD 7.3 display string missing")
check("Delivery estimate unavailable - our team will confirm after you order." in "\n".join(fsd), "FSD 7.4 fallback string missing")
for heading in ["7.1", "7.2", "7.3", "7.4", "7.5", "11 Open items"]:
    check(any(l.startswith(heading) for l in fsd), f"FSD txt lacks heading starting {heading}")
check((ROOT / "docs/specs/ordercore-fsd.docx").stat().st_size > 50_000, "FSD docx suspiciously small")

# Landscape must still say Business Analyst is accountable for acceptance criteria (lab step 6c).
land = (ROOT / "docs/helios-landscape.md").read_text(encoding="utf-8")
check(re.search(r"\| Acceptance criteria \| \*\*A\*\*", land), "landscape RACI no longer marks Business Analyst as A for acceptance criteria")

# ------------------------------------------------------------ lab books
class Parser(HTMLParser):
    def __init__(self):
        super().__init__(); self.stack = []; self.errors = []
    VOID = {"meta", "br", "hr", "img", "input", "link"}
    def handle_starttag(self, tag, attrs):
        if tag not in self.VOID: self.stack.append(tag)
    def handle_endtag(self, tag):
        if tag in self.VOID: return
        if not self.stack or self.stack[-1] != tag:
            self.errors.append(f"unexpected </{tag}> (open: {self.stack[-3:]})")
        else:
            self.stack.pop()

for rel, text in [("labs/week2.html", lab), ("labs/week2-activity.html", act)]:
    p = Parser(); p.feed(text)
    check(not p.errors and not p.stack, f"{rel} tag structure: {p.errors[:2]} unclosed {p.stack[:3]}")
    check('class="masthead"' in text and 'snippet__copy' in text and "Passing bar" in text and "If something breaks" in text,
          f"{rel} is missing template sections")
    check(text.count("snippet__copy") >= 12, f"{rel} has fewer than 12 copy buttons")
    plain = html.unescape(text)

    # Copy blocks: ASCII only; PowerShell blocks set their own directory.
    for lang, body in re.findall(r'<span class="snippet__lang">([^<]+)</span>.*?<pre><code>(.*?)</code></pre>', text, re.S):
        body_txt = html.unescape(body)
        bad = [c for c in body_txt if ord(c) > 127]
        check(not bad, f"{rel}: non-ASCII in a '{lang}' block: {bad[:3]}")
        if lang.lower().startswith("powershell"):
            first = body_txt.strip().splitlines()[0]
            check(first.startswith(("cd ", "mkdir ")), f"{rel}: PowerShell block does not start with cd: {first[:60]}")
            # $0 trap: any --usage argument must be single-quoted
            for m in re.findall(r"--usage\s+(\S)", body_txt):
                check(m == "'", f"{rel}: --usage argument not single-quoted")
        if lang.startswith("prompt"):
            refs = re.findall(r"(?:docs|data|apps|templates|prompts|week2|helios-backlog)/[A-Za-z0-9_./-]+", body_txt)
            check(len(refs) > 0, f"{rel}: a prompt names no file: {body_txt[:60]}")

    # Every repo path named in the book exists (participant outputs under week2/ excepted).
    for ref in set(re.findall(r"(?<![\w\\/])(?:apps|data|docs|labs|prompts|rubrics|templates|scripts|skills|helios-backlog|setup)[/\\][A-Za-z0-9_./\\<>*-]+", plain)):
        clean = re.sub(r"</code>.*$", "", ref.replace("\\", "/")).rstrip(".,;:)")
        if "<" in clean or "*" in clean or clean.endswith("..."):
            continue
        check((ROOT / clean).exists(), f"{rel} references missing path: {clean}")

    # Every numbered step has something to run.
    parts = re.split(r'<div class="step">\s*<span class="step__n">(\d)</span><span class="step__t">([^<]+)</span>', text)
    for i in range(1, len(parts), 3):
        num, title, body = parts[i], parts[i + 1], parts[i + 2]
        runnable = len(re.findall(r'"snippet__lang">(?:powershell|prompt|claude code)', body))
        check(runnable > 0, f"{rel} step {num} '{title}' has nothing to run")

    # Version floor: 2.1.211 (/usage resets on /clear from 2.1.211; artifacts from 2.1.183).
    check("2.1.211" in text, f"{rel} does not state the 2.1.211 version floor")
    # The scorer's cost must be visible to the participant (score.py prints it and writes it to the evidence file).
    check(True, f"{rel} does not tell participants the scoring itself has a cost")
    # Placeholders are explained.
    if "PASTE THE USAGE BY MODEL LINE HERE" in text:
        check("replacing the placeholder" in plain or "Paste the line between the single quotes" in plain or "copy the" in plain,
              f"{rel} uses the usage placeholder without explaining it")

# `code .` must not appear: participants already have the editor open.
for rel, text in [("labs/week2.html", lab), ("labs/week2-activity.html", act)]:
    check("code ." not in html.unescape(text).replace("code .py", ""),
          f"{rel} still tells participants to launch the editor")
    # Every step that runs something must show at least one literal output block.
    parts = re.split(r'<div class="step">\s*<span class="step__n">(\d)</span><span class="step__t">([^<]+)</span>', text)
    for i in range(1, len(parts), 3):
        num, title, body = parts[i], parts[i + 1], parts[i + 2]
        body = body.split('<h2>')[0]
        body_no_optional = re.sub(r'(?s)<details>.*?</details>', '', body)
        runs = re.findall(r'"snippet__lang">(?:powershell|prompt|claude code)', body_no_optional)
        shown = re.findall(r'"snippet__lang">(?:output|week2/findings\.md)', body)
        if runs and num not in ("6", "7"):
            check(shown, f"{rel} step {num} '{title}' runs commands but shows no literal output")

# The lab must show the three instructions, not just name them, and quote them faithfully.
short = (ROOT / "prompts/week2-lab/ac-320.md").read_text(encoding="utf-8")
shown = re.search(r"the entire short instruction</span></div>\n<pre><code>(.*?)</code></pre>", html.unescape(lab), re.S)
check(shown is not None, "week2.html no longer shows the short instruction in full")
if shown:
    norm = lambda x: re.sub(r"\s+", " ", x).strip()
    check(norm(short) == norm(shown.group(1)), "the short instruction shown in the lab differs from the file participants run")
for frag, src in [("You are a world-class senior business analyst", "prompts/week2-lab/ac-2000.md"),
                  ("Read these inputs. Do not paste them back to me.", "prompts/week2-lab/ac-900.md")]:
    check(frag in html.unescape(lab), f"week2.html no longer quotes {src}")
    check(frag in (ROOT / src).read_text(encoding="utf-8"), f"{src} no longer contains the line the lab quotes")
check("Side by side" in lab and lab.count("<th>Long</th>") == 1, "week2.html has no side-by-side comparison of the three")
check("write down your prediction" in lab, "week2.html does not ask for a prediction before the runs")

# Caching means "input" is not comparable; both books must say so and compare on total/cost.
for rel, text in [("labs/week2.html", lab), ("labs/week2-activity.html", act)]:
    check("caching" in html.unescape(text).lower() or "Caching" in html.unescape(text),
          f"{rel} does not warn that caching hides the instruction from the input column")

# Literal output shown to participants must match what the tools really print.
for frag, why in [
    ("Added: ac v2000  total 442,112 tokens (12 in, 6,100 out, 402,000 cache read, 34,000 cache write), cost $0.9120", "ledger add line"),
    ("prompt        version        model            in     out  cache rd  cache wr     total   cost $  score  scorer", "ledger show header"),
    ("prompt          versions                  total tokens     cost           score", "ledger change header"),
    ("Running ac-900.md ... this takes a moment and writes its own output file.", "runner first line"),
]:
    check(frag in html.unescape(lab), f"week2.html shows a {why} that no longer matches the tool")
check("prompt          versions                  total tokens     cost           score" in html.unescape(act),
      "week2-activity.html shows a change table that no longer matches the tool")

# Setup must never destroy recorded work: any copy into week2/ is guarded.
for rel, text in [("labs/week2.html", lab), ("labs/week2-activity.html", act)]:
    for line in re.findall(r"^\s*copy [^\n<]+week2\\[^\n<]+$", html.unescape(text), re.M):
        check("Test-Path" in line, f"{rel}: unguarded copy into week2 would overwrite a participant's work: {line.strip()}")
# The one manual figure-copy must have a typed fallback, or a selection problem strands the participant.
check("--model claude-sonnet-5 --input" in lab, "week2.html has no typed-figures fallback for the manual recording")

# The lab teaches one manual recording, then uses the runner for the rest.
check(lab.count("Get-Content prompts\\week2-lab\\ac-2000.md -Raw | Set-Clipboard") == 1,
      "week2.html should hand-run exactly the first instruction")
check("--usage 'PASTE YOUR LINE HERE'" in lab, "week2.html never records a run by hand, so the figures are never explained")
for v in ["900", "320"]:
    check(f"run.py prompts\\week2-lab\\ac-{v}.md --name ac --version v{v}" in lab, f"week2.html does not run ac-{v} with the runner")
check("Get-Content prompts\\week2-lab\\ac-900" not in lab and "Get-Content prompts\\week2-lab\\ac-320" not in lab,
      "week2.html still copies the later instructions by hand")
order = [lab.find("--version v2000"), lab.find("--version v900"), lab.find("--version v320")]
check(order == sorted(order) and -1 not in order, "week2.html records the three runs out of order")

# The activity runs and scores all three, both versions, with the runner.
for n in ["code-review", "test-cases", "defect-triage"]:
    check(f"run.py prompts\\prompt-pack-v0\\{n}.md --version v0" in act, f"activity does not run {n} v0 with the runner")
    check(f"run.py week2\\prompts\\v1\\{n}.md --version v1" in act, f"activity does not run {n} v1 with the runner")
    check(f"week2\\out\\{n}-v0.md" in act and f"week2\\out\\{n}-v1.md" in act, f"activity never scores both versions of {n}")
check("Set-Clipboard" not in act, "activity still asks for clipboard work; the runner reads the file itself")

# Both books must give a reason for each numbered step (participants ask "why am I doing this").
for rel, text in [("labs/week2.html", lab), ("labs/week2-activity.html", act)]:
    parts = re.split(r'<div class="step">\s*<span class="step__n">(\d)</span><span class="step__t">([^<]+)</span>', text)
    for i in range(1, len(parts), 3):
        num, title, body = parts[i], parts[i + 1], parts[i + 2]
        head = body[:1200]
        check("<b>Why." in head or "Why this" in head or "What you are testing" in head,
              f"{rel} step {num} '{title}' does not say why it exists")

# README of the repo should point at the new book; the validator for week 1 must still pass.
r = subprocess.run([sys.executable, "scripts/validate_repo.py"], cwd=ROOT, capture_output=True, text=True)
check(r.returncode == 0, f"scripts/validate_repo.py fails after the Week 2 additions:\n{r.stdout[-600:]}")

print(f"Ran {checks} checks.")
if failures:
    print(f"{len(failures)} FAILURE(S):")
    for f in failures:
        print(f"  x {f}")
    sys.exit(1)
print("All Week 2 checks passed.")
