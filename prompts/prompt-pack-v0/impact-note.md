You are a senior software architect with deep expertise in impact analysis for changes to distributed systems, especially ones with cross-language service boundaries. You are careful, systematic, and you always check the code rather than trusting documentation.

We need an impact note for a change to the Helios estate. An impact note is a short document that says, before anyone writes code, which files and services a change will touch, what could break, and who has to approve it. Here are three examples of impact notes from previous changes so that you can see the format we use.

Example one. Change: add a description to order lines. Files touched: apps/ordercore/app/models.py (new optional field), apps/shop/src/OrderDetail.jsx (display). Not touched: Billing, because the description is not sent on the invoice request. Risk: low; the field is optional and defaults to empty. Tests: test_orders.py gains one case. Approval: Developer.

Example two. Change: rename the customer field to account_name. Files touched: models.py, store.py, orders.json (seed), main.py (response model), OrderList.jsx, OrderDetail.jsx, test_orders.py, report.py (orders report reads customer). Not touched: Billing, which never sees the customer. Risk: medium; every consumer changes at once and the seed file format changes. Approval: Architect, because it crosses into Insight.

Example three. Change: charge tax at 0 percent for a flagged customer. Files touched: InvoiceCalculator.java, BillingServer.java (new request field), Json.java, billing_client.py (send the flag, and mirror in the fallback), models.py (flag on the order), OrderDetail.jsx (show zero tax). Risk: high; the contract between OrderCore and Billing changes, and the fallback must mirror it or a Billing outage silently charges tax. Approval: Architect, cross-system change approval per the RACI.

Now the change we need to assess. Here is the full ticket:

{
  "key": "HEL-207",
  "summary": "Add discount code field to the order API",
  "type": "Story",
  "status": "Ready for Build",
  "priority": "high",
  "reporter": "Daniel Okoro (Sales Operations)",
  "assignee": "unassigned",
  "components": [
    "OrderCore",
    "Billing",
    "Shop"
  ],
  "labels": [
    "pricing",
    "cross-system"
  ],
  "created": "2025-10-31",
  "description": "Sales agree ad hoc discounts with wholesale customers over email. Finance then adjusts the invoice by hand, which is slow and occasionally wrong.\n\nAdd an optional discount to an order. OrderCore should accept a whole-percentage discount on the order, pass it to Billing, and Billing should apply it to the subtotal before tax. The Shop should show the discount as its own line in the totals.\n\nDiscount must be between 0 and 50 percent. Anything above 50 needs a finance approval we are not building yet, so reject it.",
  "acceptance_criteria": [
    "An order can carry an optional discount_percent between 0 and 50",
    "Billing applies the discount to the subtotal before tax is calculated",
    "Tax is charged on the discounted subtotal, not the original subtotal",
    "A discount above 50 or below 0 is rejected with a 422",
    "Orders without a discount behave exactly as they do today",
    "The Shop totals panel shows the discount as its own row when present"
  ],
  "linked_documents": [
    "data/entity-map.md"
  ],
  "notes": "Touches Python and Java. The contract between OrderCore and Billing changes.",
  "expected_outputs": [
    "docs/design/HEL-207-lld.md (written by you during the build)"
  ]
}

Please read data/entity-map.md, which lists which files each concept touches and explains the cross-system boundary between OrderCore and Billing, and docs/helios-landscape.md for the RACI. Then please read all of the following files in full so that your impact note is based on the code and not on the documentation: apps/ordercore/app/models.py, apps/ordercore/app/main.py, apps/ordercore/app/store.py, apps/ordercore/app/billing_client.py, apps/ordercore/tests/test_orders.py, apps/billing/src/main/java/com/helios/billing/InvoiceCalculator.java, apps/billing/src/main/java/com/helios/billing/BillingServer.java, apps/billing/src/main/java/com/helios/billing/Json.java, apps/billing/src/test/java/com/helios/billing/BillingServerTest.java, apps/billing/src/test/java/com/helios/billing/InvoiceCalculatorTest.java, apps/shop/src/OrderDetail.jsx, apps/shop/src/OrderList.jsx and apps/shop/src/api.js. Please also read docs/specs/ordercore-fsd.txt to see what the specification says about discounts, tax and rounding.

Please then write the impact note following the format of the three examples above, but in more detail, with these sections: the change in one sentence; every file touched, grouped by system, with one line each on what changes in it; every file you considered and decided is not touched, with the reason; the contract change between OrderCore and Billing, described field by field in both naming conventions; the fallback path and what must change there; the tests that must be added or changed, by file; the risks, each with a likelihood and an impact rating and a mitigation; the approval needed and why, citing the RACI; an effort estimate in developer days with your reasoning; and a list of open questions for the reporter.

Please be exhaustive. Please do not miss a file. If you are unsure whether a file is affected, include it and say why you are unsure. Please cross-check every file you list against the entity map and note any place where the entity map is stale or wrong, because it is maintained by hand.

Write the note to week2/out/impact-note-v0.md, and then in the chat list the files touched, the approval needed, and the effort estimate, and briefly restate the risks.
