# Scheduled runs (Sunday to Thursday only)

Two scheduled tasks run the cohort without the coach typing anything. Each run starts fresh, so every prompt names the skill, the ops folder and the output. Create them in Claude's scheduled tasks (the coach approves each one). Cron times below are for Asia/Jerusalem; sprint emails should land around 07:00 ET (14:00 Israel), so the morning run leaves drafts ready well before that.

| Task | When | Cron |
|---|---|---|
| Cohort intake and payments | 09:13 Sunday to Thursday | `CRON_TZ=Asia/Jerusalem 13 9 * * 0-4` |
| Cohort morning run | 11:47 Sunday to Thursday, during the sprint | `CRON_TZ=Asia/Jerusalem 47 11 * * 0-4` |

Turn the morning run on 2 days before Day 1 and off after the last D15. Turn intake off when seats are full.

## Prompt: Cohort intake and payments
```
Use the cohort-operator skill. Ops folder: the private Google Drive folder "Comeback GOAT Ops" (or ~/Documents/ComebackGOAT-ops if reachable). Run "cohort intake" and "cohort payments" from Gmail, as the skill describes. Create Gmail drafts only; never send anything. Do not decide accept or decline yourself: draft S1 only for applicants scored "accept", leave S2 unwritten and list those applicants for the coach. Save the ops files back. Finish with the COHORT report block. If any setting in cohort.yaml is SET_ME, report it and draft nothing that needs it.
```

## Prompt: Cohort morning run
```
Use the cohort-operator skill. Ops folder: the private Google Drive folder "Comeback GOAT Ops" (or ~/Documents/ComebackGOAT-ops if reachable). Run "cohort today" exactly as the skill's morning run describes: read Gmail since the last run, update the ops files, create every due draft in Gmail (never send), prepare the WhatsApp group texts, save the ops files back and finish with the COHORT report block. If today is Thursday, also draft Friday's sprint emails with the [SCHEDULE SEND] line on top.
```
