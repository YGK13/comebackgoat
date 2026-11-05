# Boomerang signals

Search the last 90 days for each eligible employer. Open the source page before saving a signal; record it in the row's `notes` as `signal | source URL | date`.

| Signal | Why it opens a door | Search |
|---|---|---|
| Rehiring former staff or an alumni program | They already value returners | `"<employer>" (rehire OR "boomerang" OR "alumni network" OR "welcome back")` |
| AI rollout trouble or reversal | The work the user did may need doing again, now with AI | `"<employer>" AI (rollout OR pilot OR layoffs OR "rehire" OR reversal)` |
| New leader in the user's old function | New leaders buy outside help in their first 100 days | `"<employer>" ("appointed" OR "joins as" OR "named") (<function>)` |
| Open roles in the user's function | Unfilled seats are budget; a contract can fill the gap | Greenhouse, Lever, Ashby or Workable board for the employer (job-insurance `ats-endpoints.md`), filtered by the user's titles |
| Reorganization, layoffs or a merger | Integration and change work, often urgent | `"<employer>" (reorganization OR restructuring OR acquisition OR merger)` |
| Funding, expansion, new market | Growth outpaces the team | `"<employer>" (raises OR funding OR expansion OR "new office")` |

Rank signals by how directly they map to the user's offers in `claims.yaml`. One strong signal beats three weak ones. Never use non-public information the user had as an employee.
