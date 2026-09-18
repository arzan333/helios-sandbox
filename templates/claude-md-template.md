---
owner: Architect
version: 1.0
effective_date: 2026-03-02
review_date: 2026-09-02
---

# CLAUDE.md template

A repository's instruction file. It is read on every request in that repository, so
every word in it is paid for on every request. Keep it under one page.

Use the five headings below and nothing else. Replace the guidance in each with your
own, delete the guidance, and stop.

```
# <Repository name>

## What is here
Two or three lines. What this repository contains and what it is for. Not a history.

## Standards
The rules that would otherwise be repeated in every prompt. Ones that are specific
to this codebase, not general good practice. Five or six lines at most.

## Where to look
A short list: for X, read Y. Point at directories and index files, never paste their
contents. This is the section that saves the most tokens.

## Do not
The exclusions. Files that are generated, data that must not be edited by hand,
directories that are not source. Being explicit here prevents a whole class of
expensive mistake.

## Ownership
Who to ask, by role. One line.
```

## What does not belong in it

- Anything a reader can find by opening the directory
- A file-by-file inventory that goes stale the day it is written
- Explanation of how to use git, Python, or any general tool
- Anything you would not want re-read on every single request

## The test

If a section would be just as useful sitting in its own document with a pointer from
here, put it in its own document and point at it. `CLAUDE.md` is an index, not a
library.
