---
owner: Developer
version: 1.0
effective_date: 2026-03-02
review_date: 2026-09-02
---

# Prompt efficiency techniques

Six named techniques. When you optimise a prompt in Week 2, tag every edit with
the technique that justifies it, so that the change is a decision and not a hunch.
A prompt with no tags has been shortened; a prompt with tags has been engineered.

| Tag | Technique | What it cuts | Before | After |
|---|---|---|---|---|
| T1 | Reference, do not paste | Pasted file contents, pasted tickets, pasted standards. Claude can read the file itself, and a file it reads is one tool call, not 800 tokens of your prompt on every retry | "Here is the full CLAUDE.md: ...600 words..." | "Apply the standards in CLAUDE.md." |
| T2 | Targeted read | Whole-file and whole-folder reads when a section, a function or a filtered set of rows is what matters | "Read data/helios-tickets.csv in full and find January." | "Filter data/helios-tickets.csv to rows with deployed in 2026-01 using a command; do not read the whole file." |
| T3 | Structure over prose | Paragraphs of instruction that a heading, a numbered list or a schema says in a quarter of the space, and that the model follows more reliably | "First I would like you to..., then it would be helpful if..., after that..." | "Output: 1. ... 2. ... 3. ..." |
| T4 | Output shaping | Unbounded output: executive summaries, reasoning shown, three formats of the same thing, a chat recap of the file just written. Output tokens are the expensive half | "Write the report, then summarise it in the chat and explain your decisions." | "Write the file. Reply with one line: the number of findings." |
| T5 | Few-shot pruning | Examples that do not change the output. Keep an example only when the format cannot be described in fewer tokens than the example costs | Three worked examples of an impact note | One example, or a column list |
| T6 | Instruction compression | Role inflation, hedging ("where appropriate", "if possible"), restated constraints ("please make sure... again, it is really important..."), courtesy | "You are a world-class... with twenty years... Please make sure... Again, please..." | "You are the BA on this ticket. Rules: ..." |

## How to tag an edit

Put a block at the top of the optimised prompt file, above the prompt itself, in
an HTML comment. The activity's copy command strips the comment before pasting, so
it documents the decision without costing tokens at run time:

```
<!-- v1 edits
T1  replaced the pasted CLAUDE.md and source file with a reference to each
T2  review billing_client.py only; dropped the read of every file in apps/
T4  file only, one-line chat reply; dropped the prose assessment and action plan
T6  cut the role paragraph to one sentence; removed restated constraints
-->
```

Three named techniques is the minimum for the hands-on activity. Six is not the
target; the target is the smallest prompt that still scores 90 percent or more of
its baseline on the rubric.

## What you are not allowed to cut

- The output file path. A prompt that does not name the file writes to the chat.
- The rubric's content requirements. Cutting "cover the cut-off rule" saves eight
  tokens and loses five points.
- Anything that makes the output checkable: exact strings, status codes, counts.

## Reading the trade

Tokens down 40 percent at 95 percent of the score is a result. Tokens down 40
percent at 60 percent of the score is a regression, and the v1 goes back for a
v2. If a v2 still fails, the cut that broke it is the finding; write that down.
