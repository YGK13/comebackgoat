---
name: network-engine
description: Map and score the user's professional network from their own LinkedIn export, saved contacts and email, then find warm paths for every other Comeback GOAT lane (a referral for a job, a former colleague at a company with a trigger, someone who knows a program officer) and surface connector income (recruiting referrals, paid introductions, venture scouting) within legal lines. Drafts intro requests for the user's yes; never messages anyone. Use when the user says "who do I know at", "warm intro", "map my network", "referral path", "who should I reconnect with", "connector income", or when another engine needs a warm path.
---

# Network Engine

A mid-career expert's network is their largest undeclared asset. This engine turns the member's own exports into a warmth-scored graph and puts it to work for every other engine. Warm paths convert far better than cold outreach; say so when choosing between them.

## Non-negotiables

1. **The member's own data only:** their LinkedIn data export, their contacts export, their own email. Never scrape LinkedIn or any site, never automate LinkedIn.
2. **Other people's data stays private.** The index lives in `ComebackGOAT/private/` (create it; it is never published, committed or uploaded). Drafts mention a contact only when the user is asking that contact for something.
3. **Drafts only.** Intro requests and reconnection notes are Gmail drafts or text in the tracker. Nothing is sent, connected, liked or messaged.
4. **No mass outreach.** At most 5 network drafts a day across all lanes, each written to one person about one specific ask.
5. **Connector income stays legal** (`references/connector-income.md`): no success fees for introducing investors to securities offerings, no fees charged to job seekers, and state licensing checks for recruiting and real estate.

## Build (once, then monthly)

1. Ask the user to request their LinkedIn data export (LinkedIn: Settings, Data privacy, Get a copy of your data; choose Connections and Messages; it arrives by email, usually within a day) and their Google or Outlook contacts export. Explain why in one line: "This is how I find who can open each door."
2. Build the index (this skill's script, standard library only):
   `python3 scripts/network_index.py build --owner "<name as on LinkedIn>" --out ComebackGOAT/private/network.json --connections Connections.csv --contacts contacts.csv --messages messages.csv`
3. Show `stats`: people indexed, warmth bands, top 15 companies. Ask the user to mark 10 to 20 people they trust most (former bosses, clients, close peers); record them in `context/claims.yaml` under `never_say` only if they must not be mentioned, otherwise in `trackers/learnings.md` as "trusted connectors".
4. No LinkedIn export yet: start from sent mail (people the user wrote to in the last 3 years, counted by thread) and refine later.

## Serving the other engines

- **job-insurance:** for each queued role, `lookup --company`; warmth 40+ gets a referral-ask draft before the application; under 40, find adjacent paths (same function at the company's investors, partners or recent alumni).
- **project-hunter:** weekly, list warmth 40+ people at companies with a trigger (funding, new leader, layoffs, expansion) and anyone who once paid or praised the user and has not heard from them in 6+ months; draft up to 5 reconnection notes.
- **grant-hunter:** for a high-scoring program, look for past winners, program staff or board members in the index; a short "what did reviewers value" ask beats a cold application.
- **setup and alignment:** suggest 3 people for testimonials and 3 for a "how would you describe what I do" check.

## Connector income (opt-in lane)

When the user turns it on in `lanes.yaml` (network: connector_income: true), watch for matches between people the user knows and needs the other engines see: a company hiring for a role a trusted contact fits, a founder raising who fits a fund the user scouts for, a client needing a service a partner sells. Propose the match with the fee basis (written referral agreement first) and draft the double-opt-in intro: ask each side separately before connecting them. Follow `references/connector-income.md`.

## Output

`trackers/network.csv` (shared columns; engine `network`, id prefix N-) for drafted intros and reconnections, and a short line in the Revenue Brief: "N warm paths found, N drafts waiting."
