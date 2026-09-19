# Scoring: answering from the raw conversions vs from the repository

Scored 0, 1 or 2 per row against what is written in each file.

## week4/answer-raw.md

| # | Row | Score | Quoted from the file |
|---|---|---|---|
| 1 | Answers the question, or says plainly these files cannot | 2 | "Not in what I read." ... "OrderCore calculates the invoice itself using the same rules and returns it with `source = fallback` and a note saying why" |
| 2 | Names the document and the heading each fact came from | 2 | "The technical specification, under \"2. The invoice path\"" ... "functional specification, \"6.2 Fallback\"" ... "technical specification, \"5. Configuration\"" |
| 3 | Gives the owner and the review date of each document used | 1 | "\| Functional specification (`week4/raw/fsd.md`) \| Priya Raman (Product) \| Not in what I read \|" and "\| Technical specification (`week4/raw/techspec.md`) \| Architect \| Not in what I read \|" - owner for both, review date for neither |
| 4 | Invents nothing | 2 | "the retry behaviour \"is recorded in this diagram and nowhere else in the document\"" ... "`Billing unavailable (ConnectError); calculated locally`" ... "The timeout is 2000 ms" - each is a quotation or a restatement of text in the two raw files |
| 5 | Says where a missing fact would have to come from | 2 | "the number would have to come from Figure 2 of the original PDF" and "would have to come from the register governing these documents, not from either file" |

**Total: 9 / 10**

## week4/answer-repo.md

| # | Row | Score | Quoted from the file |
|---|---|---|---|
| 1 | Answers the question, or says plainly these files cannot | 2 | "Not in what I read." ... "A locally calculated invoice: OrderCore applies the same rules itself and returns it with `source = fallback` and a note describing why" |
| 2 | Names the document and the heading each fact came from | 2 | "The technical specification, \"2. The invoice path\"" ... "functional specification, \"6.2 Fallback\"" ... "\"6.3 Invoice examples\"" ... "technical specification, \"5. Configuration\"" |
| 3 | Gives the owner and the review date of each document used | 2 | "\| `specs/ordercore-fsd.md` \| Product Manager \| 2026-07-12 \|" and "\| `specs/ordercore-techspec.md` \| Architect \| 2026-09-03 \|" |
| 4 | Invents nothing | 2 | "Owners and dates are from each file's front matter; `specs/index.md` carries the same pair" - and "Both review dates have passed", which restates the line in `specs/index.md` rather than judging the dates unaided |
| 5 | Says where a missing fact would have to come from | 2 | "The number would have to come from Figure 2 of the original, `docs/specs/ordercore-techspec.pdf`" |

**Total: 10 / 10**

## What the repository bought

Only row 3 moved, 1 to 2: the review dates exist nowhere in the converted prose, and front matter is what supplied them.
Rows 1, 2 and 4 did not move - the raw conversions already carried the owner lines, the numbered headings and the sentence admitting the retry count is only in a diagram.
Row 5 did not move either, but the pointer sharpened from "the original PDF" to the exact path, because the `source` field names it.
The repository bought governance metadata and a named original, not better answers.
