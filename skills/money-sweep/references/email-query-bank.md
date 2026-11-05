# Email query bank (Gmail syntax; adapt for Outlook)

Open each candidate thread before trusting it; previews show only the first message. Add `-category:promotions` when noise is high.

## Receivables
- R1 `in:sent (invoice OR "statement of work" OR SOW OR "payment terms") newer_than:1y` then check each thread for a paid confirmation or a later remittance email.
- R2 `("past due" OR overdue OR "payment pending" OR "awaiting payment" OR remittance OR "payment schedule") -category:promotions newer_than:1y`
- R3 `("signed" OR DocuSign OR "fully executed" OR "countersigned") (agreement OR contract OR SOW OR engagement) newer_than:6m` (signed work that may never have been invoiced)

## Platform payouts
- P1 `(payout OR "payment sent" OR withdrawal OR "funds available" OR "balance available" OR "minimum threshold") (stripe OR paypal OR wise OR payoneer OR deel OR tipalti OR upwork OR fiverr OR "expert network") newer_than:1y`
- P2 `(royalties OR "royalty statement" OR "earnings report" OR "affiliate commission" OR "creator payout") newer_than:2y`
- P3 `("action required" OR "verify your" OR "tax information" OR W-8 OR W-9) (payout OR payment OR earnings) newer_than:1y` (payouts held until a form is filed)

## Refunds, credits, deposits
- F1 `(refund OR reimbursement OR "credit balance" OR overpayment OR "store credit" OR "account credit") -category:promotions newer_than:2y`
- F2 `("security deposit" OR "deposit return" OR escrow) newer_than:3y`
- F3 `("travel credit" OR "future flight credit" OR voucher OR "e-credit") newer_than:2y`

## Dormant and lost accounts
- D1 `(dormant OR inactive OR "unclaimed property" OR escheat OR "abandoned property" OR "transferred to the state") newer_than:5y`
- D2 `(401k OR 401(k) OR 403b OR pension OR "retirement plan" OR "plan administrator" OR rollover) newer_than:10y`
- D3 `(HSA OR FSA OR "health savings" OR "flexible spending" OR "run-out period") newer_than:3y`

## Tax and settlements
- T1 `(1099 OR W-2 OR "tax document" OR "tax form") newer_than:3y` (list payers only, never numbers)
- S1 `("class action" OR "settlement administrator" OR "claim form" OR "you may be eligible" OR "settlement notice") -category:promotions newer_than:2y`

## Corporate exit (left a job in the last 24 months)
- X1 `(severance OR "separation agreement" OR "release agreement" OR "final paycheck" OR "PTO payout") newer_than:2y`
- X2 `(vesting OR "stock options" OR RSU OR "exercise window" OR "equity" OR Carta OR "Shareworks" OR "E*TRADE") newer_than:2y`
- X3 `(COBRA OR "benefits end" OR "coverage ends" OR "expense report" OR reimbursement OR "tuition") newer_than:2y`
