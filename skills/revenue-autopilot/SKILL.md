---
name: revenue-autopilot
description: Put the Revenue Engine on a schedule - creates the user's scheduled tasks for money-sweep, grant-hunter, project-hunter and job-insurance from their Founder Context Pack, plus one short daily Revenue Brief that merges every engine's "needs you" items, deadlines and wins. Draft-only by design. Also handles "send 2, submit 5"-style replies, pausing an engine, changing caps and the weekly scorecard. Use when the user says "run this every day", "put it on autopilot", "schedule my engines", "daily revenue brief", "what needs me today", or "pause the job search".
---

# Revenue Autopilot

The engines are only valuable if they run when the user is busy. Autopilot schedules them, keeps one place to look (the Revenue Brief) and makes approving work a one-line reply.

## Non-negotiables

1. **Draft-only.** Scheduled runs may create Gmail drafts, edit the user's tracker files and fill forms up to Submit. They never send, submit, post, pay, sign or create accounts. `lanes.yaml` autopilot.approval must stay `draft_only`.
2. **Respect the user's days off and hours** from `constraints.yaml`: no runs, nudges or deadlines suggested on those days.
3. **One brief, short.** The Revenue Brief fits on a phone screen: needs-you items, deadlines inside 7 days, wins. Details live in the trackers.
4. **Scheduled tasks start in a fresh session.** Every task prompt must be standalone: where the workspace is, which skill to run, the caps, the allowed writes.

## Set up (first time)

1. Confirm the pack exists and validates (`revenue-engine-setup`). List enabled engines from `lanes.yaml`.
2. Check the scheduler this session offers (scheduled tasks in the Claude app, or cron-style routines in Claude Code). If none, say so and give the user the prompts to schedule from the app.
3. Propose a schedule in the user's time zone, staggered so engines finish before the brief (defaults in `references/schedule.md`), skipping their days off. Use an off-the-hour minute.
4. Build each task prompt from `references/task-prompt-template.md`, filled with the workspace path and caps. Show the list in one message; create on the user's yes. Report each task's approval setting from the scheduler's response.
5. Run the brief once now so the user sees the format.

## The Revenue Brief (daily)

The daily-plan run executes first, so the brief reports what Claude already did and lists only what needs the user, ordered by distance to revenue (R1 cash first). Read every tracker and `runs/<date>-today.json`; output (`references/brief-format.md`):
1. **Needs you today**: items with status `needs_you` or `prepared`, highest value and nearest deadline first, each with its one action.
2. **Deadlines inside 7 days.**
3. **Since yesterday**: replies, interviews, money confirmed, wins.
4. **Pipeline line**: counts by engine (found, waiting, sent or submitted, won), and confirmed money found to date.

## Handling replies

"send P-2" or "submit G-5": open the item, confirm what will happen in one line, and only then act if the session permits sending (a user-approved, specific send is the user's yes). If this session cannot send, tell the user exactly where the draft or tab is. "skip J-4 too junior": mark skipped with the reason so the engine learns. "pause jobs": set `job_insurance.enabled: false` and pause its scheduled task.

## Weekly scorecard (Sundays or the user's first workday)

Per engine: found, prepared, acted on, replies, wins, money confirmed; best source; one recommended change. Apply weight changes only with the user's yes, at most 5 points per factor per week.
