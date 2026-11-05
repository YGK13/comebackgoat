# The revenue ladder

Every action gets an R-level: how many steps it sits from money in the bank. Lower is closer. The planner ranks by expected dollars (amount x chance of cash), discounted for how long cash takes, boosted by deadlines, inside these buckets:

1. Anything due within 48 hours at R1 to R5.
2. R1 to R3 (cash, close, conversation).
3. Everything else.

| R | Stage | Typical actions | Default chance of cash | Typical days to cash |
|---|---|---|---|---|
| R1 | cash | send or chase an invoice, release a payout, file an unclaimed-property or refund claim, deposit a check | 80% | 14 |
| R2 | close | send a requested proposal or SOW, follow up on a sent proposal, answer pricing questions, return a contract for signature, negotiate an offer | 35% | 21 |
| R3 | conversation | reply to an inbound request, book or prep a discovery call or interview, follow up after a call | 15% | 45 |
| R4 | warm path | reconnect with a former client, boss or colleague; ask for an intro or referral | 5% | 60 |
| R5 | application | submit a job, grant, fellowship, RFP or program application (grants 8%, jobs 3%) | 4% | 75 |
| R6 | cold | comment on a public post, cold pitch, speaker or podcast pitch | 1% | 75 |
| R7 | asset | website, LinkedIn rewrite, bios, case study, content | 0.5% | 120 |
| R8 | admin | setup, exports, learning, organizing | 0.1% | 180 |

The default chances are starting assumptions for a new solo practice, not facts. They are deliberately conservative, and `plan_today.py learn` replaces them with the user's own results (each stage's prior counts as 10 observations, so about 20 real outcomes outweigh it).

## Stage inference

When a row has no `stage`, the planner reads the title, next action and notes: money words (invoice, payout, refund, unclaimed) mean R1; proposal, SOW, contract, sign, pricing mean R2; reply, call, meeting, interview mean R3 (for jobs and grants only "interview" counts); warm, reconnect, referral mean R4; then the engine default (money-sweep R1, grants and jobs R5, network R4, projects R6). Set `stage` explicitly whenever the inference would be wrong.

## Amounts

Only amounts stated by the source count as sourced. Without one, the planner uses `today.default_deal_usd`, else the project minimum, else 3 day rates, else $1,000, and the plan says "no amount stated". Never write an estimate into `value_usd`.

## Why R7 and R8 sink

Assets and setup feel productive and are the most common way a first year stalls. They are not banned: they get Claude's time first (Claude drafts the LinkedIn rewrite) and the user's time only once R1 to R3 is clear.
