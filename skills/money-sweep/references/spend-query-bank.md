# Spend query bank (Gmail syntax; adapt for Outlook)

Previews show only the oldest messages in a thread: open every candidate with the full thread before trusting an amount. Exclude the user's own digests with `-subject:(brief OR digest OR summary)`.

## Receipts and recurring charges
- L1 `(subject:receipt OR subject:invoice OR subject:"payment confirmation" OR subject:"order confirmation") newer_than:1y -from:me`
- L2 `from:stripe.com (receipt OR invoice) newer_than:1y` (most SaaS bills through Stripe; the display name is the vendor)
- L3 `("your subscription" OR renews OR renewal OR "has been renewed" OR "auto-renew") (plan OR membership OR subscription) newer_than:1y`
- L4 `from:(apple.com OR google.com OR paypal.com OR amazon.com) (receipt OR subscription OR "payment") newer_than:1y` (middlemen)

## Price changes, trials, cancellations
- L5 `("price increase" OR "price change" OR "new price" OR "special price" OR "pricing update" OR "rate increase") newer_than:1y -category:promotions`
- L6 `("trial ends" OR "trial ending" OR "trial has ended" OR "you will be charged" OR "upcoming charge") newer_than:6m -category:promotions`
- L7 `("cancellation confirmed" OR "has been cancelled" OR "subscription canceled" OR "renewal cancellation") newer_than:1y` then search the same sender for later charges.

## Failed payments and fees
- L8 `("payment failed" OR "card was declined" OR "unable to charge" OR "payment was declined" OR "billing suspension" OR "past due") newer_than:3m` (a burst means the funding account needs attention first)
- L9 `("foreign transaction fee" OR "international transaction fee" OR "currency conversion" OR "late fee" OR "overdraft" OR "interest charge") newer_than:1y`

## Seats, plans and duplicates
- L10 `(seat OR seats OR "per user" OR license OR licenses) (invoice OR billing OR plan) newer_than:1y`
- L11 `("Business Starter" OR "Business Standard" OR "Workspace") (invoice OR "price change" OR suspended) newer_than:1y` (one tenant per domain: retired domains often keep a paid tenant)

## Debt and big-ticket bills
- L12 `(loan OR servicer OR "income-driven" OR IBR OR "repayment plan" OR rehabilitation) newer_than:1y`
- L13 `(insurance OR policy OR premium) (renewal OR invoice OR "price") newer_than:1y`

## Hebrew (Israel)
- H1 `(subject:חשבונית OR subject:קבלה OR "חשבונית מס") newer_than:1y`
- H2 `(חיוב OR "הוראת קבע" OR מנוי) newer_than:1y`
- H3 `("דמי ניהול" OR עמלה OR "עמלת" OR "ריבית") newer_than:1y`
- H4 `(ארנונה OR "חברת חשמל" OR גז OR מים OR סלולר OR אינטרנט) newer_than:1y`
- H5 `(ביטוח OR פוליסה OR פרמיה) newer_than:2y`
