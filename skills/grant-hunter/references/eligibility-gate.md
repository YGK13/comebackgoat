# Eligibility gate

Read the program's own rules page and FAQ. Every row is pass, fail or unknown. One fail drops the item. Two or more unknowns on must-haves: drop, unless the item scores 85+ (then queue it with the unknowns as questions for the funder).

| Check | Compare against |
|---|---|
| Applicant type (individual, sole prop, LLC, corporation, nonprofit, fiscal sponsorship) | `claims.yaml` entity.type |
| Location and residency of the business and of the founder | `constraints.yaml` location; never claim a residency the user does not have |
| In-person attendance or relocation, and for how long | `constraints.location.in_person_max_days`, relocation |
| Business age, revenue, employee count, funding raised | `claims.yaml` and the setup answers |
| Owner demographics (if targeted) | only `constraints.grants.demographic_screens` the user volunteered |
| Sector and use of funds | profile offers and focus |
| Citizenship or work authorization | `constraints.work_authorization` |
| Application fee | `constraints.grants.max_application_fee_usd` |
| Equity, revenue share or IP terms hidden in the rules | `lanes.grant_hunter.equity_ok`; read the terms page |
| Schedule conflicts (events on the user's days off) | `constraints.schedule.days_off` |
| Program exclusions the user set | `constraints.exclusions` |
| Deadline at least 3 days out, or rolling | today's date |
