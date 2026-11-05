# Workspace layout

One folder per business, owned by the user. Every Comeback GOAT skill reads `context/` and writes only to `trackers/`, `packages/` and `runs/`.

```
ComebackGOAT/
  context/
    capabilities.md      what this session can reach (connectors, folder, browser, scheduler)
    evidence.md          every harvested fact: fact | source | date seen
    profile.md           who they are and what they sell (human-readable)
    claims.yaml          THE CANON: the only facts any draft may use
    voice.md             how they write: rules plus 2 real samples
    messaging-kit.md     one-liner, bios, proof stories, rate language
    constraints.yaml     hard filters every engine applies
    lanes.yaml           which engines run, targets, caps, scoring weights, today block
    logistics.yaml       links, systems of record, files, credentials, standard answers (no secrets)
  trackers/
    money-ledger.csv     money-sweep findings
    grants.csv           grant-hunter queue
    projects.csv         project-hunter queue
    jobs.csv             job-insurance queue
    network.csv          network-engine intros and reconnections
    boomerang.csv        former-employer reconnections and offers (B- prefix)
    tasks.csv            items from pasted briefs and to-do lists (daily-plan, T- prefix)
    calibration.json     learned win rates by stage and engine (daily-plan learn)
    learnings.md         what got replies, wins, skips and why (all engines)
  packages/
    <YYYY-MM-DD>-<slug>/ one folder per prepared application or proposal
  private/
    network.json         warmth-scored network index (other people's data: never published or committed)
  runs/
    <YYYY-MM-DD>-<engine>.md   one run log per engine per day
    <YYYY-MM-DD>-today.json    the day's plan (used to spot carried-over items)
```

## Tracker columns (CSV, header row required)

All trackers share the first seven columns so comeback-autopilot can merge them into one digest:

`id,date_found,engine,title,link,value_usd,status,deadline,score,prepared,next_action,notes`

- `id`: `<engine-prefix>-<n>` (M-, G-, P-, J-, N-, B-, T-), never reused.
- `value_usd`: a number only when the source states it; otherwise empty. Never an estimate.
- `status`: one of `found`, `prepared`, `needs_you`, `sent`, `submitted`, `won`, `lost`, `skipped`, `expired`.
- `prepared`: under 80 characters ("Gmail draft ready", "Form filled, Submit waits", "Claim link + steps").
- `next_action`: one verb-led line for the user.
- Optional columns any tracker may add: `updated` (date of the last status change, used for follow-ups), `minutes` (user time the next action takes), `stage` (revenue ladder stage: cash, close, conversation, warm, apply, cold, asset, admin).

## When there is no folder

In a chat-only session keep the same files in the working directory and, at the end of setup, publish `profile.md` and `claims.yaml` into one Docs artifact titled "<Name> Founder Context Pack" so the user keeps them. Trackers can live in one Sheets artifact with one tab per tracker.
