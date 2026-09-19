---
owner: Architect
version: 1.0
effective_date: 2026-09-19
review_date: 2027-03-19
---

# OrderCore specification repository

## What is here

The OrderCore functional and technical specifications, converted out of Word and
PDF into markdown so they can be read, searched and diffed as text, plus an index
at each level. Nothing here is an original; every converted file names the one it
came from.

## Standards

- Front matter is mandatory and is the first thing in the file, above every
  heading. A file without it is a file nobody owns.
- Dates are ISO `YYYY-MM-DD`, in front matter and in prose.
- A converted document keeps a `source` field naming its original, for as long as
  that original exists.
- Money is a whole number of pence, never a float. Format only at the UI edge.
- Heading level follows the section number already in the text: `#` for the title,
  `##` for `4.`, `###` for `4.1`, `####` for `4.1.1`. Never renumber to fit.
- A `review_date` in the past makes the document suspect. Say so when you quote it.

## Where to look

- `index.md` answers: what is in each folder here, and which index to read next.
- `specs/index.md` answers: which specification covers which subject, who owns it,
  and when it falls due for review.

Start at `index.md`. Neither index repeats what a specification says.

## Do not

- Do not treat `week4/raw` as part of this repository. It holds the raw converter
  output and is kept only so the conversion can be measured.
- Do not edit the originals under `docs/specs`. They are the source of record.
- Do not fill in, from memory or from elsewhere, a fact that existed only in a
  diagram. Figures did not survive conversion and one error table is an image
  only; where the text says a fact is not here, leave the gap and raise it.

## Ownership

The Architect owns this repository and the technical specification; the Product
Manager owns the functional specification.
