---
owner: Developer
version: 1.0
effective_date: 2026-03-02
review_date: 2026-09-02
---

# Anti-pattern audit

Six questions. Run them against your own design before you cost it. Answer yes or
no, and where the answer is yes, say what you will do instead.

| # | Anti-pattern | The question to ask | What it looks like when it is wrong |
|---|---|---|---|
| 1 | Context dumping | Does any step receive more than it needs to do its job? | A whole repository pasted when three files mattered |
| 2 | Over-prompting | Does any instruction bury its real constraint under other instructions? | Six paragraphs of stacked rules, the important one third from the end |
| 3 | Retry without change | What happens when a step fails - is the same input sent again? | The same wrong instruction run three times, charged three times |
| 4 | Duplicate derivation | Do two steps work out the same thing? | Two steps that both read and interpret the same dataset |
| 5 | Redundant verification | Is a model checking something a deterministic check already covers? | A model asked whether the tests passed, when the test runner already said |
| 6 | Premature chaining | Would one call do what this chain does? | Four steps because the work felt like four steps |

## How to record it

One line per row: the number, yes or no, and if yes, the replacement. A "no" with
no evidence behind it is a guess - point at the step you checked.

## The one that catches everyone

Number 6. A chain feels like better engineering than a single call. It is better
engineering only when the steps need different tools, different permissions, or a
human decision in between. Otherwise it is the same work, billed once per step.
