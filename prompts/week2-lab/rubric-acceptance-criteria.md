---
owner: Business Analyst
version: 1.0
effective_date: 2026-03-02
review_date: 2026-09-02
---

# Rubric - acceptance criteria for HEL-142

Used in the Week 2 lab to score the three runs of the same task. Five criteria,
each scored 0 to 5. Maximum 25. Score against the file as written; do not give
credit for what you know the model meant.

**How to score quickly:** read the file once, then score each row below in under
a minute. 5 means the standard is fully met, 3 means mostly, 0 means not at all.
Whole numbers only.

| # | Criterion | 5 looks like | 3 looks like | 0 looks like |
|---|---|---|---|---|
| 1 | Testable | Every Then names something a tester can observe on a screen or in a response: an exact string, a date, a presence or absence | Most are observable; one or two say "clearly", "appropriate" or "correctly" without saying what that is | Prose statements of intent, no observable outcome |
| 2 | Covers FSD section 7 | All six rule areas present: shown before confirm; display format (all three cases); cut-off rule; region transit; unavailable case with the fallback text; banned hedging words | Four or five of the six | Two or fewer |
| 3 | Traceable | Every criterion cites the FSD sub-section (7.2, 7.3, 7.4) or the ticket it came from | Most cite a source | No sources |
| 4 | Nothing invented | Every rule stated appears in the ticket or in section 7. The exact strings from 7.3 and 7.4 are used verbatim | One invented rule or one paraphrased string that changes the meaning | Rules about accessibility, performance, timezones, or a data source, none of which section 7 decides |
| 5 | Open questions surfaced | Lists the undecided items as questions and does not answer them: where stock data lives (7.5), bank holidays as an image (7.5), contractual or advisory (OI-6), HLD and FSD disagreements | Lists some, or answers one | None listed, or the answer decides the data source |

## Reading the result

- A run that scores well on 2 and badly on 4 has covered the ground by inventing
  some of it. That is the most expensive kind of output, because a developer will
  build the invented rule.
- A run that scores well on 1 and 4 but drops to 3 on criterion 2 has missed a
  rule. Say which one. That is the trade the Week 2 lab is about: what did the
  short prompt lose, and was it worth it.
- Two people scoring the same file should land within 2 points. If they do not,
  the rubric row is too vague; say so on the findings line.
