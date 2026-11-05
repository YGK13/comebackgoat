# Alignment check

New solo operators usually present four slightly different people: the resume (corporate), LinkedIn (half-updated), the new website (aspirational) and the email signature (whatever was quickest). Funders, clients and recruiters cross-check. One contradiction costs credibility; consistent claims compound.

## 1. Build the comparison

For each field below, list the value found in each source with its citation:

| Field | Resume | LinkedIn | Website | Email signature | User said |
|---|---|---|---|---|---|
| Name as published | | | | | |
| Current title and company | | | | | |
| One-line positioning | | | | | |
| Location shown publicly | | | | | |
| Years of experience | | | | | |
| Headline numbers (people coached, revenue led, team size) | | | | | |
| Past employers and dates | | | | | |
| Credentials and degrees | | | | | |
| Awards and rankings | | | | | |
| Offers and prices | | | | | |

## 2. Flag

- **Contradiction:** two sources disagree (titles, dates, numbers, location).
- **Stale:** a source shows a past role as current.
- **Unsupported:** a number or award with no source anywhere. It stays out of `claims.yaml` until the user gives a source or confirms it in writing ("stated by user <date>").
- **Personal vs professional mismatch:** the user's stated goals, values or constraints conflict with how they present (for example "I only want remote work" vs a site advertising on-site workshops in one city). Ask which one is true now.
- **Risky:** anything that could read as an earnings or results promise ("I'll double your revenue") or a credential they do not hold (a license, an admission to practice). Recommend a safe phrasing.

## 3. Resolve in one pass

Show only the flagged rows, each with a recommended canonical value, and ask the user to accept or edit. Use AskUserQuestion with "Use recommended" as the first option when available.

## 4. Write the canon

`claims.yaml` gets one entry per accepted fact (template in `templates/claims.yaml`) with:
- `id` (short slug), `claim` (exact wording to reuse), `source`, `ok_for` (`public`, `applications`, `private`), optional `phrasing_notes` (for example "cite as Top 10, never a rank number").
- `never_say`: the user's list plus anything they rejected in this step.

Finish with a short "fix list" the user can do outside Claude (update LinkedIn headline, change the site's location line), each item one line, so their public footprint matches the canon. This list is a deliverable: it is often the first concrete win.
