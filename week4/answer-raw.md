# Billing call failure - from the raw conversions only

**How many times is the call attempted?** Not in what I read. The technical
specification, under "2. The invoice path", says the retry behaviour "is recorded
in this diagram and nowhere else in the document". That diagram did not survive
conversion; the number would have to come from Figure 2 of the original PDF.

**What does the caller get back?** OrderCore calculates the invoice itself using
the same rules and returns it with `source = fallback` and a note saying why -
functional specification, "6.2 Fallback", which covers Billing being unreachable,
timing out, or returning a response OrderCore cannot parse. "6.3 Invoice
examples" gives the note's form: `Billing unavailable (ConnectError); calculated
locally`. The timeout is 2000 ms - technical specification, "5. Configuration".

**Documents used**

| Document | Owner | Review date |
|---|---|---|
| Functional specification (`week4/raw/fsd.md`) | Priya Raman (Product) | Not in what I read |
| Technical specification (`week4/raw/techspec.md`) | Architect | Not in what I read |

Each names its owner in its opening lines. Neither states a review date; that
would have to come from the register governing these documents, not from either
file.
