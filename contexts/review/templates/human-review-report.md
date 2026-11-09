# Review Result: {{PASS|FAIL|INCOMPLETE}} ({{advisory|gate}})

The machine `review_status` remains one of PASS/FAIL/INCOMPLETE. Show
`PASS (advisory)` to users for non-gating reviews; it never grants PR readiness.

## Blocking findings

Confirmed, Lead-inspected blockers with file:line, reachable trigger, evidence,
consequence, likelihood, origin and recommended action. Include lead confirmation.
If none, write "None confirmed".

## Nonblocking findings

Material nonblocking findings with impact, likelihood, confidence, origin,
exposure and disposition; list decision-needed requirement conflicts.

## Documentation assessment

Record `documentation_assessment.status` (`checked`, `not-applicable`,
or `blocked`), the documents and implementation sources inspected at the
reviewed target, affected but unchanged documentation, and the reason when
no applicable documentation exists or inspection was blocked. Refer to
individual findings for confirmed drift, contradictions, ambiguity or
harmful duplication. Do not claim that every repository document was audited.

## Refuted candidates

Candidate IDs and source-supported falsification.

## Checks and coverage

Check, revision, observed result/not-run reason, file inventory, unreviewed
paths and any pinned external-context evidence.

## Execution metadata

Frozen repository and target, risk, actual collaboration mode, team roles and
runtime identities, bounded peer threads, independent verification provenance,
N selection rationale and unresolved questions.

Use machine evidence field names in English and human prose in the user's
or project's language (or explicit `output_language`).
