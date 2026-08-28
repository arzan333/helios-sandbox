---
owner: Architect
version: 0.1
effective_date: 2026-01-20
review_date: unset
source_system: Helios delivery
ticket: HEL-142
---

# HEL-142 high-level design

Show an estimated delivery window in the cart.

## Approach

The Shop will call OrderCore for the delivery window and render it on the cart
page above the checkout button. OrderCore will work out the window from the stock
location and the carrier cut-off time.

We will add a new endpoint, `GET /orders/{id}/delivery-window`, returning a start
date and an end date. The Shop will display them as a range.

## Data

Stock location is held in the warehouse spreadsheet. We will import it. The
carrier cut-off is 16:00 on weekdays.

## Effort

About three days.

## Risks

Some risk around the spreadsheet import.
EOF
