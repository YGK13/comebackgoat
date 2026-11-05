# Scoring rubric (0 to 100)

Weights from `lanes.yaml` job_insurance.weights (defaults below). Score 0 to 1, multiply, round.

| Factor | Default weight | 1.0 means | 0.0 means |
|---|---|---|---|
| fit | 40 | every must-have requirement is met by a sourced claim | several must-haves missing |
| level | 20 | the role's scope matches the user's seniority | far above or below |
| domain | 15 | same industry or function the user is known for | unrelated domain |
| constraints | 15 | fully remote in their regions, no conflicts with days off | borderline (e.g. occasional travel) |
| comp | 10 | posted range starts at or above the floor | no range posted, or below the floor (below the floor fails the hard filter) |

Show the 3 strongest matching proof points and the 1 or 2 gaps an interviewer will probe.
