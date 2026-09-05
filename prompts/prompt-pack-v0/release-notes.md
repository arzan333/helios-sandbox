You are an experienced technical writer and release manager who writes clear, friendly, customer-facing release notes for B2B software products. You have a gift for turning internal engineering language into plain English that a customer's operations team can understand and act on.

Some background on how release notes are produced at Helios Group today. Here is the current-state process narrative, so you understand where your work fits:

# Release note production, current state

How the monthly release note gets written. Nine steps, one person, most of a
morning. Matching data: `data/helios-tickets.csv`, filtered to
`workflow = release_notes`.

## The nine steps

1. **Freeze the release scope.** The Release Manager lists tickets marked done
   since the last drop.
2. **Export the ticket list.** Copied out of the tracker into a spreadsheet.
3. **Drop the noise.** Internal tasks, spikes and reverted changes are removed
   by hand.
4. **Group by system.** Shop, OrderCore, Insight, Billing.
5. **Rewrite each summary.** Ticket titles are written for the team, not for
   customers, so each one is reworded.
6. **Chase the gaps.** Around a fifth of tickets have a title that does not
   explain what changed. The Release Manager messages the developer.
7. **Add upgrade steps.** Written from memory of what was discussed.
8. **Review.** Sent to one senior developer, who usually replies "looks fine".
9. **Publish.** Pasted into the wiki and emailed.

## Known pain

- Step 5 is the whole job and it is pure rewriting.
- Step 6 exists because ticket titles are never written with the release note in
  mind.
- The review at step 8 is a formality. Nobody has ever rejected a release note.

We want to produce the release notes for the January 2026 monthly drop. The scope of the drop is every ticket with a deployed date in January 2026. That information is in data/helios-tickets.csv, which has one row per ticket with a title, a system, and a deployed timestamp among other columns. Please read the whole file so that you do not miss any ticket, and identify every row whose deployed column falls in January 2026. Please also read docs/helios-landscape.md so that you understand the four systems, and please read the whole of helios-backlog/ so that you can add detail from any ticket that has a fuller description.

Then please write the release notes. Please group the changes by system: Shop, OrderCore, Billing, Insight. Within each system please list each distinct change once, in customer language, without ticket identifiers, without internal system names where a customer would not recognise them, and without engineering jargon. If the same title appears on more than one ticket, it is one change, not several; please deduplicate carefully. If a title is too vague to explain what changed for the customer, please write the note anyway using your best interpretation and flag it for the release manager to confirm.

Please produce the release notes in three formats: first as a wiki page in markdown with a heading per system; second as a customer email with a friendly introduction and a closing paragraph inviting feedback; and third as three short social media posts highlighting the most interesting changes. Please make sure all three are consistent.

Please also add an upgrade steps section, saying what customers need to do, if anything, when the release lands. If you do not know, please write plausible upgrade steps based on the kind of change, and flag them for confirmation. Please also add a known issues section listing anything from the backlog that customers might notice and that is not yet fixed.

Please keep the tone warm and confident. Please avoid marketing hyperbole. Please make sure every change listed actually appears in the data and that you have not invented anything. Please make sure nothing is missed. Please make sure the date range is stated at the top.

Write everything to week2/out/release-notes-v0.md and then in the chat tell me how many tickets were in scope, how many distinct changes you found, which ones you flagged as vague, and paste the email version so I can read it here as well.
