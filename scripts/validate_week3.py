"""Check the Week 3 material before anyone teaches from it.

    python scripts/validate_week3.py

Every rule here exists because something went wrong once. The build session must
run this until it prints "All Week 3 checks passed", then run
scripts/simulate_participant.py until that reports no complaints. Neither is
optional and neither replaces the other: this checks what the documents say, the
simulator checks what happens when you do it.
"""

import csv
import html
import re
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
failures: list[str] = []
checks = 0

LAB = "labs/week3.html"
ACT = "labs/week3-activity.html"


def check(condition, message):
    global checks
    checks += 1
    if not condition:
        failures.append(message)
    return condition


# --------------------------------------------------------------- files exist
REQUIRED = [
    LAB, ACT,
    "rubrics/hld.md", "rubrics/lld.md",
    "data/model-pricing.csv", "data/cost-model.xlsx", "data/helios-volumes.csv",
    "data/entity-map.md",
    "docs/process/over-engineered-chain.md",
    "templates/anti-pattern-checklist.md", "templates/toolchain-canvas.md",
    "helios-backlog/HEL-207.json",
    "apps/ordercore/app/models.py",
    "apps/billing/src/main/java/com/helios/billing/InvoiceCalculator.java",
    "scripts/simulate_participant.py",
]
for rel in REQUIRED:
    check((ROOT / rel).exists(), f"missing required file: {rel}")
if failures:
    print("\n".join(failures))
    sys.exit(1)

lab = (ROOT / LAB).read_text(encoding="utf-8")
act = (ROOT / ACT).read_text(encoding="utf-8")
BOOKS = [(LAB, lab), (ACT, act)]

# ------------------------------------------------------------ house format
class Tags(HTMLParser):
    VOID = {"meta", "br", "hr", "img", "input", "link"}

    def __init__(self):
        super().__init__()
        self.stack, self.errors = [], []

    def handle_starttag(self, tag, attrs):
        if tag not in self.VOID:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if tag in self.VOID:
            return
        if not self.stack or self.stack[-1] != tag:
            self.errors.append(f"unexpected </{tag}>")
        else:
            self.stack.pop()


for rel, text in BOOKS:
    p = Tags()
    p.feed(text)
    check(not p.errors and not p.stack, f"{rel}: broken HTML - {p.errors[:2]} unclosed {p.stack[:3]}")
    for needed in ('class="masthead"', "snippet__copy", "Passing bar", "If something breaks",
                   'class="meta"', 'class="step"'):
        check(needed in text, f"{rel}: house format is missing {needed}")
    check(text.count("snippet__copy") >= 10, f"{rel}: fewer than 10 copy buttons")
    check("</style>" in text and "</script>" in text,
          f"{rel}: must be self-contained - styles and script inline")
    check("http://" not in text.replace("http://www.w3.org", ""),
          f"{rel}: insecure or external reference")

# --------------------------------------------------------- steps and pacing
for rel, text in BOOKS:
    parts = re.split(r'<div class="step">\s*<span class="step__n">(\d+)</span>'
                     r'<span class="step__t">([^<]+)</span>', text)
    nums = [parts[i] for i in range(1, len(parts), 3)]
    check(nums == [str(n) for n in range(len(nums))],
          f"{rel}: steps must run 0,1,2,... in order; found {nums}")
    for i in range(1, len(parts), 3):
        num, title, body = parts[i], parts[i + 1], parts[i + 2]
        head = body[:1400]
        check("<b>Why." in head or "Why this" in head,
              f"{rel} step {num} '{title}': does not say why it exists")
        no_optional = re.sub(r"(?s)<details>.*?</details>", "", body.split("<h2>")[0])
        runs = re.findall(r'"snippet__lang">(?:powershell|prompt|claude code)', no_optional)
        shown = re.findall(r'"snippet__lang">(?:output|[^"<]*\.(?:md|csv|xlsx))', no_optional)
        if runs:
            check(shown, f"{rel} step {num} '{title}': runs commands but shows no expected output")
        letters = re.findall(r"<p><b>([a-h])\.</b>", body)
        check(letters == sorted(letters), f"{rel} step {num}: lettered parts out of order: {letters}")
    times = re.findall(r'step__time">([^<]+)', text)
    check(len(times) == len(nums), f"{rel}: every step needs a time budget")

# --------------------------------------------------------- copy-block safety
for rel, text in BOOKS:
    for lang, body in re.findall(r'<span class="snippet__lang">([^<]+)</span>.*?<pre><code>(.*?)</code></pre>',
                                 text, re.S):
        code = html.unescape(body)
        bad = sorted({c for c in code if ord(c) > 127})
        check(not bad, f"{rel}: non-ASCII in a '{lang}' block ({bad[:3]}) - PowerShell will mangle it")
        lines = [l.strip() for l in code.splitlines()]
        if lang.lower().startswith("powershell"):
            first = next((l for l in lines if l), "")
            check(first.startswith(("cd ", "mkdir ")),
                  f"{rel}: a PowerShell block must set its own folder first, not '{first[:50]}'")
            for l in lines:
                check(not re.search(r'"[^"]*\$\d', l),
                      f"{rel}: a dollar sign in double quotes will be eaten: {l[:50]}")
            for idx, l in enumerate(lines):
                if re.match(r"(?:copy|Set-Content) .*week3\\", l):
                    guarded = "Test-Path" in l or any("Test-Path" in x for x in lines[max(0, idx - 2):idx])
                    check(guarded, f"{rel}: unguarded write into the participant's folder "
                                   f"would destroy their work: {l[:60]}")
                if l.startswith("code ") and "week3" in l and "--diff" not in l:
                    ok = any(x.startswith("dir ") or "copy " in x or x.startswith("Set-Content")
                             for x in lines[:idx])
                    check(ok, f"{rel}: `{l[:50]}` with no prior listing - a missing file opens blank")
        if lang.lower().startswith("prompt"):
            check(re.search(r"week3/[A-Za-z0-9_./-]+", code) or "do not edit" in code.lower(),
                  f"{rel}: a prompt that names no output file - the answer lands in the chat: {code[:60]}")

# --------------------------------------------- three rules, each from a defect
# Every rule below was written after something got through the checks above and
# only failed when the commands were run on a real Windows workstation. They are
# applied to Week 3 as failures and to Week 2 as advice, because Week 2 is
# already in participants' hands.

# What the Week 1 setup script actually puts on a workstation. Anything a book
# invokes that is not here, and is not a PowerShell builtin, is a command that
# works for the author and not for the room.
SETUP = ROOT / "setup/Setup-HeliosWorkstation.ps1"
_probes = set(re.findall(r"Probe='(\w+)'", SETUP.read_text(encoding="utf-8"))) if SETUP.exists() else set()
_pips = set(re.findall(r"'([\w-]+)'", re.search(r"PipPackages\s*=\s*@\(([^)]*)\)",
            SETUP.read_text(encoding="utf-8")).group(1))) if SETUP.exists() else set()
# Tools that arrive with one of the probed installs rather than on their own.
RIDES_ALONG = {"java": {"javac", "jar", "jshell"}, "node": {"npm", "npx"},
               "python": {"py", "pip"}}
INSTALLED = set(_probes) | set(_pips)
for base, extra in RIDES_ALONG.items():
    if base in _probes:
        INSTALLED |= extra
# PowerShell's own verbs and aliases. Not applications, so not the setup script's job.
SHELL_BUILTINS = {
    "cd", "dir", "ls", "type", "cat", "copy", "cp", "move", "mkdir", "md", "rmdir",
    "del", "rm", "echo", "exit", "if", "else", "elseif", "foreach", "for", "while",
    "try", "catch", "finally", "function", "return", "param", "Get-ChildItem",
    "Get-Content", "Get-Item", "Get-Location", "Get-Command", "Get-Process",
    "Stop-Process", "Set-Content", "Set-Location", "Set-Clipboard", "Add-Content",
    "New-Item", "Remove-Item", "Copy-Item", "Move-Item", "Rename-Item", "Test-Path",
    "Out-Null", "Out-File", "Out-String", "Write-Host", "Write-Output",
    "Select-Object", "Where-Object", "ForEach-Object", "Sort-Object",
    "Measure-Object", "Select-String", "Start-Sleep", "Start-Process",
    "Invoke-Item", "Invoke-WebRequest", "Invoke-Expression", "Join-Path",
    "Split-Path", "Compare-Object", "Import-Csv", "Export-Csv", "ConvertTo-Json",
}
# Documents only Office opens. The setup script installs no Office.
OFFICE_SUFFIXES = (".xlsx", ".xls", ".xlsm", ".docx", ".doc", ".pptx", ".ppt")


def ps_lines(text):
    """Every PowerShell line in a book, with the lang of the block it sits in."""
    for lang, body in re.findall(
            r'<span class="snippet__lang">([^<]+)</span>.*?<pre><code>(.*?)</code></pre>',
            text, re.S):
        if not lang.lower().startswith("powershell"):
            continue
        for line in html.unescape(body).splitlines():
            yield lang, line.strip()


def prompt_blocks(text):
    for lang, body in re.findall(
            r'<span class="snippet__lang">([^<]+)</span>.*?<pre><code>(.*?)</code></pre>',
            text, re.S):
        if lang.lower().startswith("prompt"):
            yield lang, html.unescape(body)


def house_rules(rel, text):
    """Return a list of complaints. Empty means the book is clean."""
    found = []

    # 1. `dir a b` is not a listing of two files. PowerShell binds the first
    #    argument to -Path and the second to -Filter, so the second file is
    #    silently ignored; a third argument fails outright. One path per line.
    for lang, line in ps_lines(text):
        m = re.match(r"(?:dir|ls|Get-ChildItem)\s+(.+)$", line)
        if not m:
            continue
        args = [a for a in re.findall(r'"[^"]*"|\S+', m.group(1)) if not a.startswith("-")]
        if len(args) > 1:
            found.append(f"{rel}: `{line[:60]}` lists more than one path. PowerShell binds "
                         f"only the first; the second becomes a filter. One dir per line.")

    # 2. openpyxl ignores a None passed as the `value=` argument, so a cell the
    #    book says is cleared is not cleared and a stale row stays in the total.
    #    A prompt may name the broken form only to warn against it.
    for lang, code in prompt_blocks(text):
        for ln in code.splitlines():
            if re.search(r"cell\([^)]*value\s*=\s*None", ln):
                if not re.search(r"\b(do not|don't|never|instead of|rather than)\b", ln, re.I):
                    found.append(f"{rel}: a prompt clears a cell with value=None, which openpyxl "
                                 f"ignores. Use .value = None: {ln.strip()[:60]}")

    # 3. A command the Week 1 setup script does not install. Either the book
    #    must not need it, or the block must be marked optional and the book
    #    must work without it.
    for lang, line in ps_lines(text):
        if not line or line.startswith("#"):
            continue
        head = line.split()[0].strip("(")
        if head and re.fullmatch(r"[A-Za-z][\w.-]*", head):
            base = head[:-4] if head.lower().endswith(".exe") else head
            if base not in SHELL_BUILTINS and base not in INSTALLED:
                found.append(f"{rel}: `{base}` is not installed by "
                             f"setup/Setup-HeliosWorkstation.ps1 and is not a PowerShell "
                             f"builtin, so this line works only on the author's machine")
        if re.match(r"(?:Invoke-Item|Start-Process)\b", line) and line.lower().rstrip('"').endswith(OFFICE_SUFFIXES):
            if "only if" not in lang.lower():
                found.append(f"{rel}: `{line[:50]}` opens an Office document, and the setup "
                             f"script installs no Office. Mark the block 'only if' and give "
                             f"the step a path that does not need it")
    return found


for rel, text in BOOKS:
    for complaint in house_rules(rel, text):
        check(False, complaint)
    checks += 3  # the three rules ran clean on this book

# Week 2 is already with participants. Report, do not fail the Week 3 build.
WEEK2_FINDINGS = []
for rel in ("labs/week2.html", "labs/week2-activity.html"):
    p = ROOT / rel
    if p.exists():
        WEEK2_FINDINGS += house_rules(rel, p.read_text(encoding="utf-8"))

# ------------------------------------------------------- paths really exist
for rel, text in BOOKS:
    plain = html.unescape(text)
    refs = set(re.findall(r"(?<![\w\\/])(?:apps|data|docs|labs|prompts|rubrics|templates|scripts|"
                          r"helios-backlog|setup)[/\\][A-Za-z0-9_./\\-]+", plain))
    for ref in refs:
        clean = re.sub(r"</code>.*$", "", ref.replace("\\", "/")).rstrip(".,;:)")
        if "<" in clean or "*" in clean or clean.endswith("..."):
            continue
        check((ROOT / clean).exists(), f"{rel}: refers to a path that does not exist: {clean}")

# ------------------------------------------------------------ Week 3 scope
SCOPE = {
    "model tiers": ["tier"],
    "when not to use AI": ["deterministic"],
    "anti-patterns": ["anti-pattern"],
    "cost management": ["cost"],
    "gate keeping with a rubric": ["rubric"],
}
for topic, words in SCOPE.items():
    joined = html.unescape(lab + act).lower()
    check(any(w in joined for w in words), f"Week 3 scope not covered: {topic}")
check("HEL-207" in html.unescape(lab), "the lab does not work from the Week 3 ticket")
check("cost-model.xlsx" in html.unescape(act), "the activity never uses the cost model")
check("over-engineered-chain" in html.unescape(act), "the activity never prices the chain")
check("lld.md" in html.unescape(lab), "the lab never gates the change against the design rubric")

# ------------------------------------------- the pricing the activity quotes
with (ROOT / "data/model-pricing.csv").open(encoding="utf-8") as fh:
    tiers = {r["tier"]: r for r in csv.DictReader(fh)}
for t in ("fast", "balanced", "deep"):
    check(t in tiers, f"data/model-pricing.csv has no '{t}' tier")
    check(float(tiers[t]["input_usd_per_million"]) > 0, f"'{t}' tier has no input price")
check("captured_on" in next(iter(tiers.values())),
      "the pricing sheet does not record when it was captured; prices go stale silently")

# ------------------------------------------------ the workbook actually works
try:
    from openpyxl import load_workbook
    wb = load_workbook(ROOT / "data/cost-model.xlsx", data_only=True)
    check({"Rates", "Model", "Chain compare"} <= set(wb.sheetnames),
          f"cost-model.xlsx sheets are {wb.sheetnames}")
    ws = wb["Model"]
    row = [ws.cell(row=7, column=c).value for c in (4, 5, 6, 7, 8, 9)]
    check(all(v is not None for v in row),
          "cost-model.xlsx: the worked example row does not calculate - run the recalc script")
    if all(isinstance(v, (int, float)) for v in row):
        runs, tin, tout, per_run, monthly, retried = row
        rate_in = float(tiers["fast"]["input_usd_per_million"])
        rate_out = float(tiers["fast"]["output_usd_per_million"])
        expect = (tin * rate_in + tout * rate_out) / 1e6
        check(abs(per_run - expect) < 1e-6,
              f"cost-model.xlsx: cost per run is {per_run}, arithmetic says {expect:.6f}")
        check(abs(monthly - per_run * runs) < 1e-6, "cost-model.xlsx: monthly cost does not follow")
        check(retried > monthly, "cost-model.xlsx: the retry allowance is not applied")
except ImportError:
    check(True, "")

# ------------------------------------------------------ the code still runs
r = subprocess.run([sys.executable, "-m", "pytest", "-q"], cwd=ROOT / "apps/ordercore",
                   capture_output=True, text=True)
if "No module named" in (r.stdout + r.stderr):
    check(False, "the OrderCore dependencies are not installed on this machine, so the lab's "
                 "change cannot be verified. From apps/ordercore: "
                 "pip install -r requirements.txt --break-system-packages")
else:
    check(r.returncode == 0, f"the OrderCore tests do not pass, so the lab's change cannot be "
                             f"verified:\n{(r.stdout or r.stderr)[-400:]}")

# ------------------------------------------- the rest of the repo is intact
r = subprocess.run([sys.executable, "scripts/validate_repo.py"], cwd=ROOT, capture_output=True, text=True)
check(r.returncode == 0, f"scripts/validate_repo.py fails:\n{r.stdout[-400:]}")
if (ROOT / "scripts/validate_week2.py").exists():
    r = subprocess.run([sys.executable, "scripts/validate_week2.py"], cwd=ROOT,
                       capture_output=True, text=True)
    check(r.returncode == 0, f"the Week 3 work broke Week 2:\n{r.stdout[-400:]}")

print(f"Ran {checks} checks.")
if WEEK2_FINDINGS:
    print(f"\nADVISORY - the same three rules fired {len(WEEK2_FINDINGS)} time(s) on Week 2, "
          f"which is already with participants:")
    for f in WEEK2_FINDINGS:
        print(f"  ! {f}")
    print("  These do not fail this build. Decide separately whether to reissue Week 2.")
else:
    print("The three workstation rules were also run against both Week 2 books: no findings.")
if failures:
    print(f"{len(failures)} FAILURE(S):")
    for f in failures:
        print(f"  x {f}")
    sys.exit(1)
print("All Week 3 checks passed.")
