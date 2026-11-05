# Comeback GOAT Founding Cohort: Coach Playbook (A to Z)

The program runs itself; you supply judgment and presence. Claude does each participant's legwork inside their own Claude account from `PARTICIPANT-PROTOCOL.md`. Your Claude runs the cohort from `skills/cohort-operator`: it reads applications, payments and daily reports, drafts every email in your Gmail and tells you the few things only you can do. You press Send, take two calls per person and answer the WhatsApp group.

**The whole system on one page:**

| Channel | What it carries | Who does the work |
|---|---|---|
| Daily email from you (sprint mornings) | That day's mission in 3 steps (`EMAIL-SEQUENCE.md`) | Your Claude drafts; you press Send |
| The participant's Claude Project | The actual work: research, drafts, Progress Board | Their Claude; they press Send |
| Daily report email from them | Day, counts, streak, stuck, tracker link | Their Claude drafts; they press Send |
| Google Sheet tracker (theirs) | One row per day; shared with you only if they choose | Their Claude fills it |
| Cohort WhatsApp group | Questions, wins, tips, intros between members | You answer within 1 working day |
| WhatsApp DM to you | Private questions only. Messages, not calls | You |
| Two 30-minute calls | Kickoff (before Day 1) and review (Day 14) | You, booked from your Calendly link |

Settings for all of it live in `program/cohort.yaml` (booking link, WhatsApp number and group link, payment links, Day 1 date).

---

## 1. The offer and the price

**Founding cohort: $997 per person, 5 seats.** Apply first; pay only if accepted.
- Payment plan: 2 × $549 (at acceptance and on Day 7).
- Next cohort: $1,497.
- Participants pay Anthropic directly for their own Claude Pro or Max plan.

**Why $997:** about 1.3 working days of former pay for someone who earned $200K, and about a quarter of what one more week out of work costs them ($3,846). It sits well below coaching and outplacement packages, mirrors your $997 entry offer and filters out people who won't press Send.

**Stripe payment links (live):**
- Full payment, $997: https://buy.stripe.com/3cI4gAd6R9FX3mCfbwgQE0U
- Installment, $549 (at acceptance, then again on Day 7): https://buy.stripe.com/9B614oaYJ6tLf5kfbwgQE0V

**Effort guarantee (instead of a refund):** if a participant completes calibration by Day 2, sends at least 25 messages, sends the daily report on at least 10 of the 14 days and attends both calls, and still has no paid conversation booked by Day 14, you run another 14 days with them at no charge.

**Refunds:** full refund if they withdraw before the kickoff call. After kickoff, the effort guarantee applies instead.

---

## 2. Your time budget (5 participants)

| Touchpoint | Time |
|---|---|
| Screening applications (Claude pre-scores; you decide) | about 5 min each |
| Kickoff calls, 30 min each | 2h 30m |
| Daily: press Send on the morning drafts, read the cohort board | about 10 min a day |
| WhatsApp group and DMs | about 15 min a day |
| Day 14 review calls, 30 min each | 2h 30m |
| **Total over 2 weeks** | **about 12 hours** |

At $4,985 for the cohort that is about $415 an hour.

**Schedule:** Sunday to Thursday for you. Never anything from Friday sundown to Saturday night or on Jewish holidays; the group pin says so. Participants' sprint days run Monday to Friday by default. Friday's morning email is drafted on Thursday: use Gmail's **Schedule send** on it. Pick a Monday as Day 1.

---

## 3. Stage A: Fill the cohort

1. **Post** on LinkedIn (comment "GOAT" or DM), comebackgoat.com in the first comment.
2. **Applications** arrive through the site form. Your Claude reads them ("cohort intake"), scores them and drafts S1 (accept) or S2 (decline) for each. Reply within 2 working days.
3. **Screen** with these criteria (the operator applies them; you make the call):
   - **Accept:** 10+ years at director level or above; out of work, leaving within 90 days or newly solo; 30 minutes a day for 14 days; willing to contact former colleagues; has or will get Claude Pro or Max.
   - **Red flags:** wants it done for them; refuses outreach; active legal dispute with a former employer; hostile to AI; in acute crisis (refer to support instead); expects a guaranteed job.
   - **Unsure?** Send one clarifying question by email instead of booking a fit call. The calls are reserved for kickoff and review.
4. **Seat confirmed on payment.** The operator checks Stripe receipts in Gmail and drafts S3 (welcome and setup kit) the day payment lands.

---

## 4. Stage B: Setup (before Day 1)

S3 gives each participant three steps: book the kickoff call, run `CLAUDE-SETUP.md` in Claude (about 30 minutes, Claude guides them and checks each step), join the WhatsApp group and reply "ready" with their setup report.

**Before the cohort starts, you do this once:**
1. Fill `program/cohort.yaml` (booking link, WhatsApp DM number, group invite link, Day 1 date).
2. Build the kit: `python3 scripts/build_kit.py` → `dist/comeback-goat-kit.zip`. Attach it to each S3 email.
3. Create the WhatsApp group (name: "Comeback GOAT · Founders [month year]"), turn on member approval, copy the invite link into `cohort.yaml`, post and pin G0 from `EMAIL-SEQUENCE.md`.

**Your check (Day 0):** every participant has replied "ready" with a setup report and booked a kickoff. The operator lists anyone missing and drafts S4.

---

## 5. Stage C: Kickoff call (30 minutes, before Day 1)

| Minute | What happens |
|---|---|
| 0 to 5 | Welcome. The rule: "Claude prepares, you press, I coach." The Day 14 target: a paid conversation booked and an offer sent. |
| 5 to 10 | Their setup report: anything red gets fixed now or gets the upload fallback. |
| 10 to 20 | Their story: best three wins in 10 years, who loved their work, which former employers they'd go back to as a consultant. Name the likely offer direction. |
| 20 to 25 | Their 90-day win in one sentence; runway in broad terms; days and time slot they will work. Focus mode yes or no. |
| 25 to 30 | How help works: the daily email, the group for questions, your DM for private things, Day 14 review. Ask them to post their intro in the group today. |

Your note after the call (2 minutes; tell your Claude "kickoff notes for [name]: ..."): energy, likely offer, risk.

---

## 6. Stage D: The sprint (Days 1 to 14)

### 6.1 Every sprint morning (10 minutes)
Your Claude (scheduled, or when you type "cohort today") has already:
- read yesterday's daily reports (Gmail subject "Comeback GOAT Day"),
- scored each person green, yellow or red,
- drafted today's mission email for each person (one draft each, name and links filled),
- drafted T1 or T2 for anyone yellow or red, and T3 on Day 7 for payment-plan participants,
- written the cohort board: who is where, wins to celebrate, who asked for feedback.

You: read the board, press Send on the drafts, open any tracker someone shared with "Feedback please".

| Status | Rule | What gets drafted |
|---|---|---|
| Green | Report in, minimum met, streak intact | Nothing extra. Celebrate wins in the group. |
| Yellow | No report yesterday, or below the day's minimum | T1 |
| Red | 2 working days with no report or money move, "stuck" twice, or 0 replies after 15 sends | T2, and a note to you to DM them a voice message |

### 6.2 The WhatsApp group (15 minutes a day)
- Answer questions within 1 working day. If two people ask the same thing, answer once in the group and pin it.
- Post G1 on Monday, G2 on Thursday, G3 on Day 7, G4 on Day 13, G5 on Day 14 (your Claude reminds you and has the text ready).
- Push members to help each other: intros, draft feedback, tips. That is the network effect they're paying for.
- Never automate WhatsApp. You type or paste every message yourself.

### 6.3 Feedback on request
A participant may share their tracker with you and ask "Feedback please". Give one strength and one change, in two lines: in the group if it helps others, by DM if private. Do not open a tracker nobody shared.

### 6.4 Proposals and pricing
When a buyer asks for a proposal or price, the participant may DM you Claude's draft. Turn it around within 4 working hours: tighten scope, defend the price, add one proof point.

---

## 7. Stage E: Day 14 review (30 minutes)

Bring their Day 14 report (scorecard, what worked, 30-day plan).
1. **Scorecard (5 min):** what moved and which channel produced replies.
2. **Next 30 days (10 min):** the refined offer, the next 25 people, weekly targets, engines to keep running.
3. **Case study (5 min, recorded only with permission):** before, what they did, the result so far.
4. **Next step (10 min):** continue on their own (the daily plan keeps running), the Authority Stack for those ready to scale, or the effort guarantee if they qualify. Ask for a testimonial and two referrals (D15).

---

## 8. Intervention playbook

| Pattern | Sign | Your move |
|---|---|---|
| Not pressing Send | Drafts pile up; streak breaks | DM: "Send the two smallest ones now and tell me when." Suggest focus mode. |
| Perfectionism | Rewrites every draft | Rule: edit one sentence max, then send. |
| Fear of looking foolish | Avoids former colleagues | Reframe: they're asking for advice, not a job. Start with the warmest 3. |
| Vague offer | Can't say who buys or what it costs | Tell them to type "Run my offer call" and post the result in the group for you to sharpen. |
| Price fear | Wants to quote low | Anchor to former weekly pay and the buyer's cost of the problem. Quote a range. |
| All job, no business | Only wants applications | Fine if that's the goal; keep warm outreach as the main channel because referrals beat applications. |
| Zero replies | 15+ sends, nothing back | Ask them to post two drafts in the group; check targets (too senior, too cold) and message (too long, unclear ask). |
| Overwhelm or distress | Shuts down, emotional reports | Slow down; human first. Suggest professional support when warranted. The sprint can pause. |
| Tech blocker | Connector or export fails | Upload fallback; never let tech eat more than one day. |

---

## 9. Guardrails for you as coach

- You never log into a participant's accounts. Their Claude works inside their own account.
- Nothing goes out in a participant's name without their press. Nothing goes out in your name without yours.
- You see a participant's tracker only if they share it.
- You are not their lawyer, accountant or therapist. Flag; refer; do not advise on separation agreements.
- Keep what participants share confidential, including in the group. Case studies only with written permission.
- Record calls only with consent.

---

## 10. After the cohort

- D15 the day after each review; D30 thirty days later (the operator drafts both).
- The group stays open 30 days after Day 14, then archive it.
- Cohort retro (1 hour, solo): reply rates by channel, where people got stuck, protocol changes. Change the protocol and email files first, then run the next cohort.
- Track across cohorts: calibration by Day 2, average sends, reply rate, % with a paid conversation by Day 14, % with an offer sent, revenue at 30 and 90 days, referrals.

---

## 11. Running it from your Claude thread

Install `skills/cohort-operator` in your own Claude (Claude Code, or upload its ZIP from `dist/coach/` in Settings, Capabilities, Skills). Then:

| You type | Claude does |
|---|---|
| "cohort intake" | Reads new applications, scores them, drafts S1 or S2 for each |
| "cohort payments" | Matches Stripe receipts to accepted applicants, drafts S3 |
| "cohort today" | The morning run in 6.1 |
| "cohort board" | Pipeline and sprint status for everyone, no drafts |
| "kickoff notes for [name]: ..." | Saves your call notes to the roster |
| "cohort wrap" | D15 and D30 drafts, retro numbers |

Scheduled versions of intake and the morning run are in `skills/cohort-operator/references/schedule.md` (Sunday to Thursday only). Every message is a draft until you press Send.

Not legal, tax, financial or employment advice. Results depend on each participant's market, network and follow-through.
