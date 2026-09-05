---
owner: Developer
version: 1.0
effective_date: 2026-03-02
review_date: 2026-09-02
---

# Rubric - first-week onboarding plan for OrderCore

Score the output file, not the chat. Five criteria, 0 to 5 each, maximum 25.
5 = fully met, 3 = mostly, 0 = absent. Whole numbers. Score what is written;
give no credit for what the model probably meant.

| # | Criterion | 5 looks like | 3 looks like | 0 looks like |
|---|---|---|---|---|
| 1 | Setup path is right | Setup-HeliosWorkstation.ps1, clone, git checkout -b <name>/foundation, git config core.hooksPath .githooks, nothing is pushed | One step missing | Setup invented or wrong |
| 2 | Run and test commands are right | From apps/ordercore: pip install -r requirements.txt, uvicorn app.main:app --port 8080, python -m pytest (11 tests); report.py from the root | A path or count wrong | Commands that do not run |
| 3 | The two gotchas are taught | Money is whole pence, never a float; a fallback invoice (source = fallback) proves nothing about Billing | One of the two | Neither |
| 4 | Only real things referenced | Every file, tool and service named exists in the repository; Billing is optional and can run without Maven | One invented reference | A database, a Sprints board, a wiki, or a service that does not exist |
| 5 | Realistic and checkable | Each block ends in something the developer can show; the week fits a developer who knows Python but not FastAPI | Some blocks have no outcome | An hour-by-hour timetable nobody would follow |

## Answer key for the scorer

README.md and CLAUDE.md are the sources. The ticket (HEL-166) explicitly warns that
old notes referenced a service that no longer exists, so criterion 4 is the one
that matters most.
