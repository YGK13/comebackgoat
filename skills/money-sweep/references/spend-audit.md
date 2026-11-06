# Leak mode: the five-stage spend audit

The personal-CFO method: export, clean, look, ask, audit, re-shop, draft. Adapted from Ruben Hassid's "Be my CFO" workflow (ruben.substack.com/p/cfo, Nov 2026) and tested on a real two-country household (US business account plus Israeli household) the same week.

## Inputs, best first

1. Bank and card CSV exports, 12+ months, one folder per account (`<BANK>-PERSO`, `<BANK>-PRO`).
2. Read-only connectors (Mercury, QuickBooks, Stripe, PayPal): pull every page before totaling anything.
3. Email receipts and billing notices: `spend-query-bank.md`. These catch charges on cards with no export and show plan names, seats and promo end dates that statements hide.
4. Browser history (if a browser or history export is connected): billing, "manage subscription" and "plans" pages visited in the last year point to accounts the user pays for but forgot.
5. Files on the computer or drive: statements and invoices (`file-search-patterns.md`).

## Stage 1: Clean

- Summarize each source: institution, currency, date range, transaction count.
- Build one table: date, account (last 4), merchant (cleaned: `SQ *`, `TST*`, `PAYPAL *`, `GOOGLE *`, `APPLE.COM/BILL` prefixes stripped), amount, currency, category.
- Remove internal transfers, card bill payments, currency conversions and refunds paired with their charge, so nothing is counted twice.
- Group charges through middlemen (Apple, Google, PayPal, Amazon, Stripe-billed SaaS) by amount and day of month: each cluster is usually one hidden subscription.
- Pair every fee line with the charge that caused it (for example, a card's "Intl. Transaction Fee" posted minutes after a foreign purchase) and compute the effective rate.

## Stage 2: First look

- Money in, money out and net per month.
- Cost centers: housing, utilities, telecom, food, transport, software and AI tools, subscriptions and media, insurance, fees and interest, travel, debt service, business.
- Recurring charges list: merchant, price, cadence, card, next renewal, yearly cost.

## Stage 3: Ask (one message, then wait)

5 to 10 questions, only where the answer changes a score: unidentified merchants; which account is business and which personal; which tools are still used weekly; seats and who uses them; savings goal or debt plan; country of residence for re-shopping.

## Stage 4: Audit per cost center

For each cost center: monthly and yearly spend, trend, what is normal for this household (cite the benchmark), then every merchant scored:
- **KEEP**: used, fairly priced.
- **WATCH**: used but overpriced, overlapping or due for a price check.
- **CUT**: unused, duplicated or replaceable by something already paid for.

### Leak patterns to hunt

| Pattern | How to spot it |
|---|---|
| Ghost subscription | recurring charge with no matching use (no login emails, no files, no browser visits) |
| Duplicate charge or seat | same merchant, same amount, same day; two plans for one person; seats for people who left |
| Price increase | "price change", "new price", promo or intro price ending; compare first and latest charge |
| Trial turned paid | "trial ends" email followed by a first charge |
| Charge after cancellation | "cancellation confirmed" email followed by a later charge (owed mode: request a refund) |
| Tiny test charges | under $2 from unknown merchants (possible card testing: tell the user to call the card issuer) |
| Pay-as-you-go top-ups | repeated credit packs from one tool; compare with its plan price |
| Retired-brand tools | domains, email, Workspace tenants and software kept for a brand the user retired |
| Tool overlap | two or more tools doing the same job (schedulers, outreach, LinkedIn automation, slides, transcription) |
| Already included | a paid tool replaced by a feature in something already paid for (calendar booking pages in Workspace, slides in Claude) |
| Failed-payment cascade | many "payment failed" emails from one card at once: an empty or locked funding account, risking lost service and late fees |
| Fees | bank account fees, card FX fees, ATM fees, wire FX spread, late fees, interest, reinstatement fees |
| Wrong card for the currency | foreign-currency spend on a card with an FX fee when a local or no-FX card exists |
| Personal on business account | groceries, taxes or household bills paid from a business account (one-line CPA referral; never advise on tax treatment) |
| Debt on the expensive plan | loan on a standard plan when an income-driven or lower-rate option exists (one-line referral) |
| Annual versus monthly | monthly price on a tool used all year where annual is 15 to 33% cheaper; only suggest it when cash flow allows |

## Stage 5: Re-shop and act

Follow `reshop-and-scripts.md`. For every renewing bill (phone, internet, energy, insurance, software, virtual mailbox, domains) give 2 to 3 current offers with links and the date checked, then the action: cancel, downgrade, switch or negotiate. Draft every email in Gmail (never send) and write call scripts for providers that only negotiate by phone.

## Rules carried from the source method

- Every number comes from the files or a linked source; estimates are labeled.
- Tax, legal, pension and insurance questions get a one-line referral to a professional.
- Never ask for passwords or account numbers.
- The deliverable is a savings-sorted action list with checkboxes, plus the drafts.

## Push back where the source method does not fit

- A processing-fee renegotiation (the source's biggest win was a payment processor's fee) only pays at real volume. Below roughly $50K a year of card volume, say the saving is small and move on.
- Cutting a tool that earns money is not a saving. Score revenue tools on cost per result, not price.
