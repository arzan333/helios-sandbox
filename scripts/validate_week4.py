"""Check the Week 4 material before anyone teaches from it.

    python scripts/validate_week4.py

Same contract as Week 3: this checks what the documents say, and
scripts/simulate_participant.py checks what happens when you do it. Both must be
clean. Every rule here exists because something went wrong once.
"""

import html
import re
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LAB, ACT = "labs/week4.html", "labs/week4-activity.html"
failures: list[str] = []
checks = 0


def check(condition, message):
    global checks
    checks += 1
    if not condition:
        failures.append(message)
    return condition


REQUIRED = [
    LAB, ACT,
    "docs/specs/ordercore-fsd.docx", "docs/specs/ordercore-techspec.pdf",
    "templates/frontmatter-schema.md", "templates/claude-md-template.md",
    "docs/governance-log.md", "skills/example-skill/SKILL.md",
    "CLAUDE.md", "rubrics/lld.md", "data/entity-map.md",
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

SETUP = (ROOT / "setup/Setup-HeliosWorkstation.ps1").read_text(encoding="utf-8", errors="replace") \
    if (ROOT / "setup/Setup-HeliosWorkstation.ps1").exists() else ""


# ------------------------------------------------------------- house format
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
    check("</style>" in text and "</script>" in text, f"{rel}: must be self-contained")

# --------------------------------------------------------- steps and pacing
for rel, text in BOOKS:
    parts = re.split(r'<div class="step">\s*<span class="step__n">(\d+)</span>'
                     r'<span class="step__t">([^<]+)</span>', text)
    nums = [parts[i] for i in range(1, len(parts), 3)]
    check(nums == [str(n) for n in range(len(nums))],
          f"{rel}: steps must run 0,1,2,... in order; found {nums}")
    for i in range(1, len(parts), 3):
        num, title, body = parts[i], parts[i + 1], parts[i + 2]
        check("<b>Why." in body[:1400] or "Why this" in body[:1400],
              f"{rel} step {num} '{title}': does not say why it exists")
        no_opt = re.sub(r"(?s)<details>.*?</details>", "", body.split("<h2>")[0])
        runs = re.findall(r'"snippet__lang">(?:powershell|prompt|claude code)', no_opt)
        shown = re.findall(r'"snippet__lang">(?:output|[^"<]*\.(?:md|csv|json|txt))', no_opt)
        if runs:
            check(shown, f"{rel} step {num} '{title}': runs commands but shows no expected output")
        letters = re.findall(r"<p><b>([a-h])\.</b>", body)
        check(letters == sorted(letters), f"{rel} step {num}: lettered parts out of order: {letters}")
    check(len(re.findall(r'step__time">([^<]+)', text)) == len(nums),
          f"{rel}: every step needs a time budget")

# --------------------------------------------------------- copy-block safety
BUILTIN = {"cd", "dir", "type", "copy", "mkdir", "del", "ren", "echo", "cls", "where.exe",
           "Get-Content", "Set-Content", "Add-Content", "Test-Path", "New-Item", "Remove-Item",
           "Copy-Item", "Move-Item", "Rename-Item", "Select-String", "Measure-Object",
           "Out-Null", "Out-File", "Start-Process", "Invoke-Item", "Invoke-WebRequest",
           "Set-Clipboard", "Get-ChildItem", "Write-Host", "foreach", "if"}
INSTALLED = {"git", "python", "py", "pip", "node", "npm", "code", "claude", "javac", "java",
             "pandoc", "markitdown", "ruff", "pytest"}

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
            for idx, l in enumerate(lines):
                check(not re.search(r'"[^"]*\$\d', l),
                      f"{rel}: a dollar sign in double quotes will be eaten: {l[:50]}")
                if l.startswith("dir "):
                    args = [a for a in l[4:].split() if not a.startswith("-")]
                    check(len(args) <= 1,
                          f"{rel}: `dir` takes one path; PowerShell binds the second to -Filter: {l[:60]}")
                if re.match(r"(?:copy|Set-Content|Add-Content) .*week4\\", l):
                    guarded = "Test-Path" in l or any("Test-Path" in x for x in lines[max(0, idx - 2):idx])
                    check(guarded, f"{rel}: unguarded write into the participant's folder: {l[:60]}")
                if l.startswith("code ") and "week4" in l and "--diff" not in l:
                    ok = any(x.startswith("dir ") or "copy " in x or x.startswith("Set-Content")
                             for x in lines[:idx])
                    check(ok, f"{rel}: `{l[:50]}` with no prior listing - a missing file opens blank")
                if l.startswith("Invoke-Item") and "optional" not in lang.lower():
                    check(False, f"{rel}: Invoke-Item on an Office document, outside an optional block - "
                                 f"the workstation has no Office")
                verb = l.split()[0] if l.split() else ""
                if verb and verb not in BUILTIN and verb not in INSTALLED and not verb.startswith(("$", "(", "#", "}")):
                    check(False, f"{rel}: '{verb}' is not installed by the Week 1 setup script: {l[:60]}")
        if lang.lower().startswith("prompt"):
            check(re.search(r"week4/[A-Za-z0-9_./-]+", code) or "do not edit" in code.lower()
                  or "reply" in code.lower(),
                  f"{rel}: a prompt that names no output - the answer lands in the chat: {code[:60]}")

# --------------------------------------- no branches, no blanks to fill in by hand
# Week 4 is run in front of a room. A book that offers a path to pick, or a blank the
# participant has to type a value into, stalls everybody at the same moment: the
# facilitator then answers the same question thirty times instead of teaching. Both
# are build failures, not style.

CHOICE_PHRASES = [
    r"pick one", r"you pick", r"pick the (?:one|shape|option)",
    r"your choice", r"whichever you (?:prefer|like|want)",
    r"if you (?:prefer|would rather)", r"would rather", r"rather run",
    r"instead of the prompt", r"choose", r"a choice between",
    r"shape [ab]", r"option [ab]", r"either shape", r"two shapes",
    r"up to you", r"decide which (?:one|shape|route)",
]
CHOICE_LANGS = ["only if", "alternative", "instead of", "rather than the prompt",
                "optional", "shape a", "shape b"]
PLACEHOLDERS = ["TO-DECIDE", "TO DECIDE", "PASTE", "FILL IN", "FILL-IN", "TODO",
                "TBD", "XXX", "YOUR-", "REPLACE-ME", "<your", "<YOUR"]
PATTERNS = ("prompt - analysis", "prompt - coding", "prompt - validation")

for rel, text in BOOKS:
    prose = html.unescape(re.sub(r"<[^>]+>", " ", text))

    for pat in CHOICE_PHRASES:
        m = re.search(pat, prose, re.I)
        check(m is None,
              f"{rel}: offers a path to pick ({m.group(0)!r} at {m.start()})" if m else "")

    for d in re.findall(r"(?s)<details>.*?</details>", text):
        check(not re.search(r'snippet__lang">(?:powershell|prompt|claude code)', d),
              f"{rel}: a <details> block hides commands, which is a second route "
              f"through the book: {re.sub(chr(60)+'[^'+chr(62)+']*'+chr(62), '', d)[:60]!r}")

    for lang in re.findall(r'<span class="snippet__lang">([^<]+)</span>', text):
        low = lang.lower()
        hit = next((k for k in CHOICE_LANGS if k in low), None)
        check(hit is None, f"{rel}: copy block labelled '{lang}' marks an optional or "
                           f"alternative route ({hit!r})")
        if low.startswith("prompt"):
            check(low in PATTERNS,
                  f"{rel}: every prompt is labelled with its pattern - '{lang}' is not "
                  f"one of {PATTERNS}")

    check("<!-- hand-edit" not in text,
          f"{rel}: a hand-edit directive - the participant is being asked to edit a file "
          f"by hand")
    for token in PLACEHOLDERS:
        check(token not in text, f"{rel}: contains the placeholder {token!r}, which a "
                                 f"participant would have to replace by hand")
    for lang, body in re.findall(r'<span class="snippet__lang">([^<]+)</span>.*?'
                                 r'<pre><code>(.*?)</code></pre>', text, re.S):
        if not lang.lower().startswith(("powershell", "prompt", "claude code")):
            continue
        code = html.unescape(body)
        blank = re.search(r"[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+", code)
        check(blank is None, f"{rel}: a blank to fill in inside a '{lang}' block: "
                             f"{blank.group(0)!r}" if blank else "")
        angle = re.search(r"<[A-Za-z][A-Za-z0-9_-]*>", code)
        check(angle is None, f"{rel}: a placeholder inside a '{lang}' block: "
                             f"{angle.group(0)!r}" if angle else "")


# ------------------------------------------------------- paths really exist
for rel, text in BOOKS:
    plain = html.unescape(text)
    for ref in set(re.findall(r"(?<![\w\\/])(?:apps|data|docs|labs|prompts|rubrics|templates|scripts|"
                              r"skills|helios-backlog|setup)[/\\][A-Za-z0-9_./\\-]+", plain)):
        clean = re.sub(r"</code>.*$", "", ref.replace("\\", "/")).rstrip(".,;:)")
        if "<" in clean or "*" in clean or clean.endswith("...") or "/week4" in clean:
            continue
        check((ROOT / clean).exists(), f"{rel}: refers to a path that does not exist: {clean}")

# ------------------------------------------------------------ Week 4 scope
joined = html.unescape(lab + act).lower()
for topic, words in {
    "prompt patterns": ["analysis", "coding", "validation"],
    "skills": ["skill"],
    "AI-ready documents": ["front matter", "front-matter", "frontmatter"],
    "repository architecture": ["folder", "index"],
    "governance and freshness": ["review date", "owner", "stale"],
}.items():
    check(any(w in joined for w in words), f"Week 4 scope not covered: {topic}")
check("ordercore-techspec.pdf" in html.unescape(lab), "the lab never converts the technical spec")
check("ordercore-fsd.docx" in html.unescape(lab), "the lab never converts the functional spec")
check("CLAUDE.md" in html.unescape(lab), "the lab never writes a CLAUDE.md")
check("skills/example-skill" in html.unescape(act), "the activity never uses the example Skill as a pattern")
check("governance-log" in html.unescape(act), "the activity never registers the repository")

# ------------------------------------ the source documents are still awkward
try:
    out = subprocess.run(["pdftotext", "-layout", str(ROOT / "docs/specs/ordercore-techspec.pdf"), "-"],
                         capture_output=True, text=True)
    if out.returncode == 0:
        txt = out.stdout
        check("unitPricePence" in txt, "the technical spec's field table no longer survives extraction")
        check("no retry" not in txt.lower(),
              "the technical spec now states the retry rule in text; it must live only in the diagram, "
              "or the lab's point about image-only content disappears")
except FileNotFoundError:
    pass

for rel in ("templates/frontmatter-schema.md", "templates/claude-md-template.md", "docs/governance-log.md"):
    body = (ROOT / rel).read_text(encoding="utf-8")
    check(body.startswith("---"), f"{rel} has no front matter of its own")
    for field in ("owner:", "version:", "effective_date:", "review_date:"):
        check(field in body.split("---")[1], f"{rel} front matter is missing {field}")
check("overdue" in (ROOT / "docs/governance-log.md").read_text(encoding="utf-8").lower(),
      "the governance log has no overdue rows, so staleness cannot be taught from it")

# ------------------------------------------- the rest of the repo is intact
for script, label in (("scripts/validate_repo.py", "the repository"),
                      ("scripts/validate_week2.py", "Week 2"),
                      ("scripts/validate_week3.py", "Week 3")):
    if (ROOT / script).exists():
        r = subprocess.run([sys.executable, script], cwd=ROOT, capture_output=True, text=True)
        check(r.returncode == 0, f"the Week 4 work broke {label}:\n{r.stdout[-400:]}")

print(f"Ran {checks} checks.")
if failures:
    print(f"{len(failures)} FAILURE(S):")
    for f in failures:
        print(f"  x {f}")
    sys.exit(1)
print("All Week 4 checks passed.")
