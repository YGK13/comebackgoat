# Submission package

One folder per application: `RevenueEngine/packages/<YYYY-MM-DD>-<slug>/package.md`.

```
# <Funder> - <Program>
Link: <program page>  |  Deadline: <date, time zone>  |  Amount: <as stated>  |  Equity: none / <terms>
Verified open on <date> from <URL>.

## Eligibility
<each gate row: pass / unknown, one line each>

## Questions and answers
### <Question copied exactly> (<limit: words or characters>)
<Answer within the limit, from claims.yaml and messaging-kit.md only. State the count at the end: (143/150 words).>

## Budget (if asked)
| Line | Amount | Basis (source or user-confirmed) |

## Attachments
| Item | Exists? | Where |
<resume, deck, demo video, financials, letters: mark which the user must supply>

## Last step for you
<exactly what to click, sign, attest or pay, in order. Example: "Open the tab titled X, review answers 3 and 7, tick the attestation box, press Submit.">
```

Answer-writing rules:
- Mirror the funder's own words for its priorities in the first sentence; then the user's proof.
- One idea per answer; concrete numbers only from claims; no superlatives without a source.
- Keep 5 to 10% under hard limits so the user can edit.
- Voice from `context/voice.md`; banned phrases removed.
- Location and residency exactly as `claims.yaml` person.public_location and `constraints.yaml` allow.
