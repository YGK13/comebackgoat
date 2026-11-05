# Comeback GOAT: Participant Email Sequence and WhatsApp Group Posts

Every word a participant gets from the coach, in order. The cohort-operator skill drafts these in the coach's Gmail with the blanks filled; the coach presses Send. Nothing here is ever sent automatically.

**Blanks.** `{{FIRST_NAME}}`, `{{DAY1_DATE}}` and `{{DATE_DAY_n}}` are filled per person. `{{BOOKING_URL}}`, `{{WHATSAPP_GROUP_LINK}}`, `{{WHATSAPP_DM_LINK}}`, `{{PAY_FULL_LINK}}`, `{{PAY_PLAN_LINK}}` and `{{KIT_LINK}}` come from `program/cohort.yaml`.

**How the program talks to people (say it the same way everywhere):**
- **Email from Yuri every sprint morning:** today's mission in three steps. This is the instruction channel.
- **Claude in their own Project:** does the work and shows their Progress Board every day.
- **The WhatsApp group:** questions, wins and tips with the cohort. Yuri answers there within 1 working day.
- **WhatsApp DM to Yuri:** private questions only (money, a former employer, anything personal). Messages, not calls.
- **Two 30-minute calls with Yuri:** kickoff (before Day 1) and review (Day 14). Booked from one link.

**The daily email template** (every Day email follows it, so people learn the shape once):
```
Subject: Day [n] of 14: [mission in 5 words]

Hi [First name],

TODAY ([minutes] minutes): [one sentence]
1. ...
2. ...
3. Send your daily report (Claude drafts it; one press).

DONE LOOKS LIKE: [one concrete line]

COACH'S NOTE: [two or three sentences]

YOUR PROGRESS: Day [n] of 14  [bar]  Target so far: [cumulative target]

Questions: the group ({{WHATSAPP_GROUP_LINK}}). Private: WhatsApp me ({{WHATSAPP_DM_LINK}}).
Yuri
```

---

## Part 1: Before the sprint

### S1. Accepted (send within 2 working days of the application)
**Subject:** You're in: Comeback GOAT founding cohort

Hi {{FIRST_NAME}},

You have a seat in the Comeback GOAT founding cohort. We start on {{DAY1_DATE}}.

To confirm your seat, pay here: {{PAY_FULL_LINK}} ($997). Or use the payment plan, 2 × $549 (today and Day 7): {{PAY_PLAN_LINK}}.

As soon as you pay I'll send your setup kit. It takes about 30 minutes, and Claude walks you through most of it.

One thing to start today, because it takes up to a day: request your LinkedIn data export (LinkedIn, Settings, Data privacy, Get a copy of your data, choose the larger archive).

Looking forward to this.
Yuri

### S2. Not this time (send within 2 working days)
**Subject:** Your Comeback GOAT application

Hi {{FIRST_NAME}},

Thank you for applying. This cohort is not the right fit for where you are right now: [one honest sentence, e.g. "it is built for people ready to reach out to their network in the next two weeks"].

[Optional: one useful pointer.] I'd be glad to hear from you for a future cohort.

All the best,
Yuri

### S3. Welcome and setup kit (send the day payment lands)
**Subject:** Welcome to Comeback GOAT: your 3 setup steps

Hi {{FIRST_NAME}},

Payment received. Welcome in. Here is everything you need before {{DAY1_DATE}}, in order:

**1. Book your kickoff call (30 min)** for any time before {{DAY1_DATE}}: {{BOOKING_URL}}

**2. Set up Claude (about 30 minutes).** Download your kit ({{KIT_LINK}}), unzip it, open the Claude desktop app, start a new chat and upload `CLAUDE-SETUP.md` with the words "Set me up for Comeback GOAT." Claude walks you through every step and checks it worked. If anything breaks, screenshot it and post it in the group.

**3. Join the cohort's WhatsApp group:** {{WHATSAPP_GROUP_LINK}}
Introduce yourself in two lines: your last role and what a win in 90 days looks like.

Then reply to this email with the word **ready**.

How the 14 days run: every sprint morning you get an email from me with today's mission in three steps. Claude does the legwork; you press Send. Questions go to the group, where I answer within 1 working day. Private questions go to my WhatsApp: {{WHATSAPP_DM_LINK}}. We talk live twice: at kickoff and at your Day 14 review.

Yuri


### S4. Setup nudge (Day -1, only if "ready" has not arrived)
**Subject:** Tomorrow we start: are you set up?

Hi {{FIRST_NAME}},

Day 1 is tomorrow. I haven't seen your "ready" yet. Where are you stuck? Reply with one line or post a screenshot in the group and we'll fix it today. If the kickoff call isn't booked yet, grab a time here: {{BOOKING_URL}}

Yuri

---

## Part 2: The sprint (one email each sprint morning)

### Day 1. Calibrate: Claude reads your career
**Subject:** Day 1 of 14: Claude reads your career

TODAY (20 minutes of you, about an hour of Claude): Claude reads your email, files and public profile and drafts your Context Pack.
1. Open your Comeback GOAT project in Claude and type **"Day 1."**
2. Let it harvest. It asks up to 10 questions at the end. Answer honestly, especially runway and what you will never say.
3. Send your daily report.

DONE LOOKS LIKE: a draft profile with your five strongest claims, and your questions answered.

COACH'S NOTE: Most people underrate their own record. Today you'll see a decade of wins in one place. Read it slowly. That's the material we sell from.

YOUR PROGRESS: Day 1 of 14  ▓░░░░░░░░░░░░░  Target so far: calibration started

### Day 2. Lock your facts and your voice
**Subject:** Day 2 of 14: lock your facts and voice

TODAY (15 minutes): pick the true version of every fact and approve how you sound.
1. Type **"Day 2."** Claude shows any contradictions (titles, dates, numbers). Pick one version of each.
2. Read the three voice samples and say which sounds like you. Fix anything that sounds like a robot.
3. Send your daily report. It includes your profile summary so I can review it.

DONE LOOKS LIKE: a final Context Pack. Every draft from here on is true and sounds like you.

COACH'S NOTE: Accuracy is your safety net. Nobody gets caught out by a claim Claude invented, because it can't: everything comes from the facts you just locked.

YOUR PROGRESS: Day 2 of 14  ▓▓░░░░░░░░░░░░  Target so far: profile locked

### Day 3. Choose ONE offer
**Subject:** Day 3 of 14: choose ONE offer

TODAY (30 minutes): the most important decision of the sprint.
1. Type **"Day 3."** Claude shows your warm-path map (your Top 25 people), former employers you could return to as a consultant, any money you are owed and 2 or 3 offer options.
2. Say **"Run my offer call."** Claude asks you the five questions I'd ask live and pushes you to ONE offer and a price range.
3. Post your offer line in the group for a thumbs-up, then send your daily report.

DONE LOOKS LIKE: one sentence a buyer would understand: who you help, with what outcome, in what time, for what price range.

COACH'S NOTE: Pick the offer with the clearest buyer and the most recent proof, not the one that sounds grandest. "Strategic advisory" sells nothing. "A 60-day AI rollout plan for a 200-person HR team" sells. Price floor: a project worth at least two to three weeks of your old salary.

YOUR PROGRESS: Day 3 of 14  ▓▓▓░░░░░░░░░░░  Target so far: offer chosen

### Day 4. First 5 reconnects
**Subject:** Day 4 of 14: send your first 5

TODAY (20 minutes): your first money moves.
1. Type **"Day 4."** Claude shows 5 reconnect drafts to the warmest people on your Top 25.
2. Edit at most one sentence each. Then send all 5.
3. Tell Claude "sent" and send your daily report.

DONE LOOKS LIKE: 5 messages sent. Not drafted. Sent.

COACH'S NOTE: You are asking for a conversation, not a job. Most people like being asked what they see in their market. The first send is the hardest one of the whole sprint; after today it gets easier.

YOUR PROGRESS: Day 4 of 14  ▓▓▓▓░░░░░░░░░░  Target so far: 5 sent

### Day 5. Five more, plus your boomerang notes
**Subject:** Day 5 of 14: 5 more plus 2 boomerangs

TODAY (20 minutes):
1. Type **"Day 5."** Send the next 5 reconnects.
2. Send the 2 notes to insiders at former employers (only the ones Claude marked eligible).
3. Answer any replies with Claude's drafts, then send your daily report.

DONE LOOKS LIKE: 12 messages sent in total.

COACH'S NOTE: Silence after one day means nothing. Senior people reply in 3 to 5 days. Claude tracks every follow-up, so you never have to remember who owes you an answer.

YOUR PROGRESS: Day 5 of 14  ▓▓▓▓▓░░░░░░░░░  Target so far: 12 sent

### Day 6. Follow up and go public
**Subject:** Day 6 of 14: follow up and go public

TODAY (25 minutes):
1. Type **"Day 6."** Send every follow-up Claude has due.
2. Read the LinkedIn post announcing your offer. Change what you like and post it.
3. Send your daily report.

DONE LOOKS LIKE: follow-ups sent and your offer visible to your network.

COACH'S NOTE: The post is not for strangers; it's so the 25 people you're writing to see you're serious when they look you up. Short and specific beats clever.

YOUR PROGRESS: Day 6 of 14  ▓▓▓▓▓▓░░░░░░░░  Target so far: 12 sent + post live

### Day 7. Halfway: your scorecard
**Subject:** Day 7 of 14: halfway scorecard

TODAY (20 minutes):
1. Type **"Day 7."** Claude shows your midpoint scorecard: sent, replies, calls booked, money found.
2. Catch up anything you missed this week. Pick ONE change for week 2 (sharper message, different people, more follow-ups).
3. Post your scorecard line in the group and send your daily report.

DONE LOOKS LIKE: you are caught up and you know the one change for week 2.

COACH'S NOTE: Halfway is where most people slow down. The ones who get paid don't do more; they keep the streak. Count what you did this week: it's more than most people do in a month of job boards.

YOUR PROGRESS: Day 7 of 14  ▓▓▓▓▓▓▓░░░░░░░  Target so far: 12 sent, all follow-ups current

*(Payment-plan participants also get T3 today.)*

### Day 8. New names and calls
**Subject:** Day 8 of 14: 5 new names

TODAY (25 minutes):
1. Type **"Day 8."** Send 5 more reconnects (Top 25, numbers 16 to 25) or referral asks.
2. Read the one-page brief for any call you have booked.
3. Send your daily report.

DONE LOOKS LIKE: 17 sent in total and every booked call prepped.

COACH'S NOTE: If nothing has come back yet, the fix is the message or the list, not more volume. Post your best draft in the group today; a fresh pair of eyes usually spots it in a minute.

YOUR PROGRESS: Day 8 of 14  ▓▓▓▓▓▓▓▓░░░░░░  Target so far: 17 sent

### Day 9. Ask for introductions
**Subject:** Day 9 of 14: ask for 2 introductions

TODAY (20 minutes):
1. Type **"Day 9."** Send due follow-ups.
2. Send 2 referral asks to connectors: people who know everyone. Claude names them and drafts the ask.
3. Send your daily report.

DONE LOOKS LIKE: 19 sent in total, 2 of them asking for introductions.

COACH'S NOTE: An introduction from someone they trust is worth ten cold notes. Make the ask easy: one sentence on who you help and a short paragraph they can forward as is.

YOUR PROGRESS: Day 9 of 14  ▓▓▓▓▓▓▓▓▓░░░░░  Target so far: 19 sent

### Day 10. Conversations first, and book your review
**Subject:** Day 10 of 14: conversations first

TODAY (30 minutes):
1. Type **"Day 10."** Answer every reply and lead. Conversations beat new outreach from here.
2. If you are open to a bridge role, review the applications Claude filled (max 5) and press Submit on the ones you want.
3. **Book your Day 14 review call (30 min):** {{BOOKING_URL}}. Then send your daily report.

DONE LOOKS LIKE: every reply answered and your review call on the calendar.

COACH'S NOTE: Replies are where the money is. A "not now, but talk to Dana" reply is a win: chase Dana today.

YOUR PROGRESS: Day 10 of 14  ▓▓▓▓▓▓▓▓▓▓░░░░  Target so far: 20+ sent, review booked

### Day 11. Follow the warm threads
**Subject:** Day 11 of 14: follow the warm threads

TODAY (25 minutes):
1. Type **"Day 11."** Send follow-ups and the second-degree intros people offered you.
2. Read the offer draft Claude tailored to your warmest conversation.
3. Send your daily report.

DONE LOOKS LIKE: every warm thread has a next step, and your offer draft is ready.

COACH'S NOTE: People who replied once are your best list now. Make it easy for them to say yes to the next small step: a 20-minute call, an intro, a short scope.

YOUR PROGRESS: Day 11 of 14  ▓▓▓▓▓▓▓▓▓▓▓░░░  Target so far: 22+ sent

### Day 12. Calls and recaps
**Subject:** Day 12 of 14: calls and recaps

TODAY (30 minutes plus calls):
1. Type **"Day 12."** Take your calls with Claude's brief open.
2. After each call, tell Claude what happened in two lines; it drafts the thank-you and recap within the hour. Send them.
3. Send your daily report.

DONE LOOKS LIKE: every call has a recap sent the same day.

COACH'S NOTE: On a call, ask about their problem before you describe your offer. When they ask "what would that look like?", that's your cue for the price range you picked on Day 3. Say it calmly and stop talking.

YOUR PROGRESS: Day 12 of 14  ▓▓▓▓▓▓▓▓▓▓▓▓░░  Target so far: 24+ sent, calls recapped

### Day 13. Send an offer
**Subject:** Day 13 of 14: send one offer today

TODAY (20 minutes): the finish line of the sprint.
1. Type **"Day 13."** Claude shows a one-page offer (scope, timeline, price range) for your warmest conversation.
2. Read it, adjust the price only upward or not at all, and send it.
3. Post "Offer sent" in the group and send your daily report.

DONE LOOKS LIKE: at least one offer in a real buyer's inbox.

COACH'S NOTE: An offer is not pushy; it's a courtesy. It tells them exactly what you'd do and what it costs, so they can decide. A "not yet" still teaches you more than no offer at all.

YOUR PROGRESS: Day 13 of 14  ▓▓▓▓▓▓▓▓▓▓▓▓▓░  Target so far: 25 sent + 1 offer

### Day 14. Review and your next 30 days
**Subject:** Day 14 of 14: your scorecard and next 30 days

TODAY (45 minutes including our call):
1. Type **"Day 14."** Claude builds your full scorecard, what worked and a 30-day plan.
2. Bring it to our review call. If you haven't booked it yet: {{BOOKING_URL}}
3. Send your Day 14 report.

DONE LOOKS LIKE: a scorecard, a plan for the next 30 days and a call with me.

COACH'S NOTE: Fourteen days ago you had a fear and a blank page. Now you have a clear offer, a live pipeline and proof that people answer you. Whatever the scorecard says, you've built the habit that gets people paid.

YOUR PROGRESS: Day 14 of 14  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓  Sprint complete

---

## Part 3: After the sprint

### D15. Thank you, and two asks (the day after the review call)
**Subject:** What's next after Comeback GOAT

Hi {{FIRST_NAME}},

Thank you for doing the work. Two small asks:
1. Would you share two or three sentences on what changed for you in these 14 days? Reply here; I'll only publish it with your OK.
2. Who are two people in the spot you were in two weeks ago? I'll reach out to them personally.

Keep running your daily plan: type **"Today"** in your Comeback GOAT project each morning and it keeps ranking your moves by distance to money. The group stays open for the next 30 days.

Yuri

### D30. 30-day check-in
**Subject:** 30 days in: what moved?

Hi {{FIRST_NAME}},

It's been 30 days since your sprint ended. What moved? One line is plenty: a client, a call, a role, or nothing yet. If you're stuck, tell me where and I'll point you to the next step.

Yuri

---

## Part 4: Triggered emails (only when the cohort-operator flags them)

### T1. No report yesterday (yellow)
**Subject:** Quick check: Day [n]

Hi {{FIRST_NAME}}, no report came through yesterday. What's in the way of the first two items on today's list? If it's time, send just one. If it's something else, reply with one line and we'll fix it. Missed days don't reset anything: type "catch up" and Claude puts the two most important items first.

Yuri

### T2. Two quiet days (red)
**Subject:** Let's get you moving again

Hi {{FIRST_NAME}}, two quiet days happen to everyone, no judgment. Send me a WhatsApp voice note with what's going on ({{WHATSAPP_DM_LINK}}) and I'll reply with one concrete next step. Today, just open Claude, type "smallest move" and send that one thing.

Yuri

### T3. Second installment (Day 7, payment-plan participants only)
**Subject:** Comeback GOAT: second installment

Hi {{FIRST_NAME}}, quick admin note: the second payment of $549 is due today. Here's the link: {{PAY_PLAN_LINK}}. Thanks, and keep the streak going.

Yuri

### T4. Setup stuck (any time before Day 2)
**Subject:** Let's fix your setup

Hi {{FIRST_NAME}}, setup is the one place tech can eat a day, so let's not let it. Post a screenshot of where you're stuck in the group or send it to my WhatsApp ({{WHATSAPP_DM_LINK}}). If a connector won't work, the fallback is simple: upload your resume and LinkedIn export straight into the Claude Project and keep going.

Yuri

---

## Part 5: WhatsApp group posts (the coach pastes these; never automated)

**Group name:** Comeback GOAT · Founders [month year]
**Settings:** only admins can edit group info; members can send messages; turn on "Approve new members".

### G0. Pinned welcome and rules (post when the group is created, then pin it)
> Welcome to Comeback GOAT. This group is for three things:
> 1. **Questions.** Ask here, not in DMs, so everyone learns. I answer within 1 working day (Sunday to Thursday; I'm offline Friday sundown to Saturday night).
> 2. **Wins.** Every reply, call and offer counts. Post it.
> 3. **Help each other.** Intros, feedback on a draft, a tip that worked.
>
> House rules: keep what people share in confidence; no selling to each other unless asked; private matters go to my WhatsApp DM; messages, not calls.
> Start here: introduce yourself in two lines: your last role and your 90-day win.

### G1. Monday: wins thread
> Monday wins. Post one thing that moved last week: a reply, a call, an intro, an offer, money found. Small counts.

### G2. Thursday: stuck thread
> Thursday unstick. One line: where are you stuck? Paste your draft if it's a message problem. Everyone: if you can help, reply in the thread.

### G3. Day 7: halfway
> Halfway. Post your scorecard line: sent / replies / calls. The people who keep the streak in week 2 are the ones who get paid.

### G4. Day 13: offers day
> Offers day. When yours is sent, post "Offer sent" here. Let's see how many we get.

### G5. Day 14: graduation
> Fourteen days. Thank you all for showing up for yourselves and for each other. The group stays open for 30 days: keep posting wins, and keep making intros for each other.
