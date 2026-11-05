---
name: comeback-doctor
description: Checks and repairs a Comeback GOAT participant's Claude setup - Desktop Commander scoped to safe folders, Gmail, Drive and Calendar connectors, the Comeback GOAT skills, the Project and protocol file, the Sprint Ledger and the Google Sheet progress tracker - then prints a setup report and fixes or routes around anything broken. Use at the end of setup, before Day 1, or whenever something feels off ("check my setup", "Claude forgot where I am", "drafts are generic", "a connector stopped working", "comeback doctor").
---

# Comeback Doctor

Run every check, fix what you can with the participant's OK, give a fallback for the rest. Short sentences, plain words, one fix at a time. Never ask for or handle passwords, codes or ID, card or account numbers. Never send anything.

## Checks (in order)

| # | Check | How to verify | If it fails |
|---|---|---|---|
| 1 | Desktop Commander connected | Call get_config | "+", Connectors, Browse connectors, "Desktop Commander"; then fully quit and reopen the app |
| 2 | Desktop Commander scoped | `allowedDirectories` lists only approved folders (Documents, Desktop, Downloads, cloud-sync folders) | Propose the list, get a yes, set it with set_config_value, read it back |
| 3 | Working folder | `Documents/ComebackGOAT/` with context, trackers, packages, runs, private | Create the missing parts (the only place you write) |
| 4 | Gmail, Drive, Calendar | One harmless read each | Reconnect from "+", Connectors; if it fails twice, use uploads instead |
| 5 | Skills | You can see comeback-sprint, comeback-setup, daily-plan, network-engine, boomerang, money-sweep, comeback-doctor | Settings, Capabilities, Skills, Upload skill (the ZIP, not the folder); turn on Code execution and file creation |
| 6 | In the Project | The protocol file PARTICIPANT-PROTOCOL.md is readable in this chat | Open the Comeback GOAT Project and start a new chat there |
| 7 | Sprint Ledger | `ComebackGOAT/sprint.json` (or the latest SPRINT LEDGER in the Project) reads cleanly, `day` matches the calendar | Rebuild it from trackers and sent mail; ask only what you can't find |
| 8 | Progress tracker | `tracker_url` in the ledger opens; today's rows exist | Recreate it (CLAUDE-SETUP.md step 10); sharing with the coach stays their choice |
| 9 | Context Pack | `ComebackGOAT/context/claims.yaml` and `voice.md` exist after Day 2 | Generic drafts come from here: run Day 1 and 2 calibration |

## Report

```
COMEBACK GOAT SETUP REPORT
Desktop Commander ............... ✓/✗  folders: [list]
ComebackGOAT folder ............. ✓/✗
Gmail / Drive / Calendar ........ ✓/✗ ✓/✗ ✓/✗
Skills installed ................ [n] of 7 required
Project + protocol file ......... ✓/✗
Sprint Ledger ................... ✓/✗  Day [n]
Progress tracker ................ ✓/✗  [link]  shared with coach: yes/no
Context Pack .................... ✓/✗/not yet (Day 1 to 2)
Fixed now: [list]   Still open: [one fix + fallback]
```

If something is still broken after two tries, draft a short message for the cohort WhatsApp group with a description of the problem and tell them to post it with a screenshot. Tech never gets more than one day of the sprint.
