# Harvest map

Read-only. Work top to bottom; stop a source when two consecutive searches add no new facts. Record each fact in `context/evidence.md` as `fact | source (email subject + date, file path, or URL) | date seen`.

## 1. Email

Search syntax below is Gmail; translate for Outlook (`from:`, `subject:`, `received>=`). Open threads before trusting a preview: previews often show only the first message.

| Goal | Query (start here, then adapt) | Extract |
|---|---|---|
| Voice | `in:sent newer_than:180d -in:chats` (read 15 to 25 of their longest sent messages to clients or partners) | sentence length, greeting and sign-off, words they use often, words they never use, 2 short samples |
| Signature and titles | `in:sent newer_than:30d` (last 5) | current title, company, phone, site, booking link |
| Clients and revenue | `in:sent (invoice OR "statement of work" OR SOW OR proposal OR retainer) newer_than:2y` | client names, offers, prices, dates; never bank details |
| Testimonials | `("thank you" OR grateful OR "changed" OR recommend) (coaching OR session OR workshop OR project) -in:sent newer_than:3y` | quotes under 25 words, first name and title only; mark "needs permission to publish" |
| Visibility | `(podcast OR panel OR keynote OR "speak at" OR webinar OR interview) newer_than:2y` | appearances, audiences, hosts |
| Prior applications | `(application OR "thank you for applying" OR fellowship OR grant OR accelerator OR RFP) newer_than:2y` | what they applied to, outcomes; prevents re-queuing |
| Opportunity newsletters | `(grant OR RFP OR "call for" OR fellowship OR opportunities) category:updates newer_than:60d` | sender names to add as sources |
| Exit facts (left corporate in the last 2 years) | `(severance OR "separation agreement" OR COBRA OR "final paycheck" OR vesting OR "stock options" OR 401k OR "benefits end") newer_than:2y` | dates and deadlines only, for money-sweep's exit audit |

## 2. Files (local folder, Drive, OneDrive, Notion)

Search names and contents for: `resume`, `CV`, `bio`, `LinkedIn`, `Profile.pdf`, `Connections.csv`, `proposal`, `SOW`, `case study`, `testimonial`, `deck`, `pitch`, `headshot`, `certificate`, `operating agreement`, `articles of organization`, `EIN` (existence and date only), `1099`, `W-2` (payer names only), `separation`.
- Newest resume wins for dates; older versions reveal dropped roles worth asking about.
- `Connections.csv` (LinkedIn export): the header row starts at "First Name" after a few note lines; count connections by company and title for warm-path scoring. Never copy contact emails into claims.
- Skip anything under folders named tax, medical, bank, legal-private unless the user points you there.

## 3. Web

- Their own site: services, prices, case studies, about page.
- Public LinkedIn (headline and About as rendered publicly), author pages, podcast pages, press.
- State business registry for their entity: legal name, state, formation date, status (active or not). Grants check these.
- Search their name plus company in quotes to find what a funder or client will find. Note anything outdated or contradictory for the alignment check.

## 4. Connected business tools (if present, read-only)

QuickBooks, Stripe, Mercury, PayPal: customer names, invoice totals and dates, open receivables. These feed proof ("12 paying clients since March") only when the user approves the number for public use.

## Done when

`evidence.md` has at least: current title and offer, 3 proof points with sources, 1 voice sample, contact facts, location facts, and either a resume or a LinkedIn profile. If any is missing, it becomes a question in Step 4.
