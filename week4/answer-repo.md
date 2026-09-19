# Billing call failure - answered from week4/repo

**How many times is the call attempted?** Not in what I read. The technical
specification, "2. The invoice path", says the retry behaviour "is recorded in
this diagram and nowhere else in the document"; that diagram is not in the
markdown. The number would have to come from Figure 2 of the original,
`docs/specs/ordercore-techspec.pdf`.

**What does the caller get back?** A locally calculated invoice: OrderCore
applies the same rules itself and returns it with `source = fallback` and a note
describing why - functional specification, "6.2 Fallback", covering Billing
unreachable, timed out, or returning an unparsable response. "6.3 Invoice
examples" gives the note's form: `Billing unavailable (ConnectError); calculated
locally`. The timeout is 2000 ms - technical specification, "5. Configuration".

**Documents used**

| Document | Owner | Review date |
|---|---|---|
| `specs/ordercore-fsd.md` | Product Manager | 2026-07-12 |
| `specs/ordercore-techspec.md` | Architect | 2026-09-03 |

Both review dates have passed, so treat both documents as suspect. Owners and
dates are from each file's front matter; `specs/index.md` carries the same pair.
