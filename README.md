# Revenue Engine

Five Claude engines that find money for a solo consultant, coach, advisor or fractional executive in their first year out of corporate, plus one onboarding that makes them accurate.

| Skill | What it does | First-run time |
|---|---|---|
| **revenue-engine-setup** | Reads your email, files and public web presence, asks only what it can't find, and builds your Founder Context Pack: the facts you can prove, your voice, your constraints, your bios. Flags every place your resume, LinkedIn and site disagree. | about 20 min |
| **money-sweep** | Finds money you're already owed or about to lose: unpaid invoices, payouts, refunds, dormant accounts, unclaimed property, and severance, equity and benefits deadlines if you left a job in the last 2 years. | 15 to 30 min |
| **grant-hunter** | No-equity money you actually qualify for (grants, fellowships, prizes, pitch competitions, credits), verified open, scam-filtered, prepared to the last click. | 15 min per run |
| **project-hunter** | Paid work: inbound requests, warm-network reactivation, public "looking for" posts, fractional roles, RFPs, expert calls, workshops, speaking. Drafts every reply in your voice. | 15 min per run |
| **job-insurance** | A quiet, capped, verified job search in the background. Tailored resume and filled form for each role; you press Submit. | 20 min per run |
| **revenue-autopilot** | Schedules the engines and sends one short Revenue Brief a day. Reply "send P-2, submit G-5". | 5 min |

**The rule that never changes:** the engines prepare; you press Send or Submit. Nothing is sent, submitted, signed, paid or posted without your yes.

## Install

**Claude Code:** add this repo as a plugin marketplace or copy `skills/*` into `~/.claude/skills/`, restart, then say **"set up my revenue engine"**.

**Claude app (desktop or web):** upload each folder in `skills/` as a skill (Settings, Capabilities, Skills), connect Gmail or Outlook and Google Drive, then say **"set up my revenue engine"**.

Best results: connect email, a cloud drive or local folder with your resume and old decks, and web search. A browser lets the engines fill forms for you.

## Your data

Everything lives in a `RevenueEngine/` folder you own, inside your own Claude account. Nothing is uploaded to Portfolio Leverage Co. The pack never stores ID numbers, full account numbers, passwords or codes, and the validator refuses a pack that contains them.

## For developers

- `skills/revenue-engine-setup/scripts/validate_pack.py <workspace> [--export pack.json]` validates a pack and exports the portable JSON (`schemas/context-pack.schema.json`) that SMBeastMode imports.
- `python3 scripts/validate_skills.py` checks every SKILL.md; `python3 -m unittest discover tests` runs the validator tests.
- `examples/sample-workspace/` is a complete fictional pack.

Not legal, tax, financial or employment advice. Results vary; amounts shown come only from your own documents and the funders' own pages.

Proprietary. Copyright 2026 Grand Kru Ventures LLC (Portfolio Leverage Co.).
