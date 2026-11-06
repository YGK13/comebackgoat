# Monthly tracker and cut tracker

After the first audit, keep a phone-first page the user opens once a month.

## The page

- Opens on the latest full month (marked "so far" when incomplete), with arrows to switch months.
- Headline: money left this month, with money in and money out and an up or down pill against last month.
- Bar chart of money out over the last 12 months.
- Cost centers as bank-style rows with monthly totals.
- Recurring charges: new, increased, stopped, next date, yearly cost.
- Cut tracker: every CUT from the audit and whether its charge stopped (yes, no, too early).
- Design: one sans-serif font, tabular numbers, grey and white cards, green only for savings, red only for losses, dark mode.

Use the artifact or dashboard type the session offers; otherwise one self-contained HTML page. Personal finance data stays private to the user.

## The routine

1. The user drops new exports (or the connectors refresh) and says "Add <month>".
2. Append only rows newer than the last stored date; dedupe on date, merchant and amount so old rows never double-count.
3. Update the page and reply in three lines: what changed, the biggest new or increased charge and cuts that did not stop.
4. Any CUT still charging after one full cycle gets a fresh refund or cancel draft.
