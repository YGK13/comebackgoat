# Who does what

The test for every item: **can Claude finish it up to a single press by the user, inside the guardrails?** If yes, Claude does it now.

## Claude does (no input needed)

| Item | What "done" means |
|---|---|
| Reply to an inbound email | Gmail draft in the thread, in the user's voice, with the booking link from `logistics.yaml` when a call is the next step |
| Follow-up on a sent proposal, application or note | Draft in the same thread, shorter than the first message, one new reason to reply |
| Invoice or receivable reminder | Draft with the amount and invoice date from the source and the payment link from `logistics.yaml` |
| Unclaimed property, refund or payout claim | Claim page opened, the user's public details filled, steps listed; identity checks left for the user |
| Job, grant or program application | Form filled to the last click from `claims.yaml` and `logistics.yaml` standard answers; the tab left open on Submit |
| Proposal or SOW | Draft in the user's tool of record (`logistics.yaml` systems.proposals), fee as a range from the rate card |
| Research (company, person, funder, RFP) | 5-line brief attached to the item |
| Social and job-board monitoring | Done by the engines; only scored items reach the plan |
| Tracker hygiene | Statuses, dates, dedupes, expired items marked |
| Calendar | Proposes times inside `logistics.yaml` availability; never creates or accepts an event |

## Only the user does

- Press Send, Submit, Post, Pay, Sign or Accept.
- Anything behind a password, a one-time code, a CAPTCHA or an identity check.
- Live calls, meetings and interviews (Claude preps a one-page brief).
- Decisions on price, scope, saying yes or no to an engagement and anything in `constraints.yaml` marked as theirs.

## When Claude is blocked

Say what blocked it in one line and move the item to the user's list with the exact first step (for example "Desktop app closed: the form will be refilled on the next run" or "Site needs your sign-in: open the tab and sign in, I continue after").

## Caps (never exceeded in one day)

Per-engine caps in `lanes.yaml` apply: job forms at most `job_insurance.daily_cap`, network drafts at most 5, autopilot drafts per run at most `max_drafts_per_run`.
