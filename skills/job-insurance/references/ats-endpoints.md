# Verifying a posting on the employer's own system

Identify the ATS from the Apply link or careers page, then read its public job-board endpoint (read-only endpoints the vendors publish for career sites). A role is live only if it appears there with the same title and a consistent location.

| ATS | Public endpoint | Form (no account) |
|---|---|---|
| Greenhouse | `https://boards-api.greenhouse.io/v1/boards/<board>/jobs/<id>?questions=true` | `https://job-boards.greenhouse.io/embed/job_app?for=<board>&token=<id>` (EU boards use job-boards.eu.greenhouse.io) |
| Lever | `https://api.lever.co/v0/postings/<company>?mode=json` | `https://jobs.lever.co/<company>/<id>/apply` |
| Ashby | `https://api.ashbyhq.com/posting-api/job-board/<board>?includeCompensation=true` | `https://jobs.ashbyhq.com/<board>/<id>/application` |
| Workable | `https://apply.workable.com/api/v1/widget/accounts/<account>` | apply.workable.com form |
| SmartRecruiters | `https://api.smartrecruiters.com/v1/companies/<company>/postings/<id>` | guest apply where offered |
| Workday, iCIMS, Taleo, SuccessFactors | read the careers page; no stable public API | account required: hand to the user |

Record the endpoint URL and the check time in the tracker Notes. Re-verify any role older than 72 hours before the user submits.

Ashby postings expose `workplaceType` (Remote, Hybrid, OnSite); drop Hybrid and OnSite unless the user's regions allow them. Greenhouse `questions=true` returns the custom questions so answers can be drafted before opening the form.
