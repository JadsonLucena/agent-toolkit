# Review Code

## Intent

Perform an independent, risk-proportionate and evidence-based review of a change, producing a portable verdict and actionable findings for development or PR preparation.

## Invocation

Use to review a specified PR, branch diff, commit/range, file set, or current workspace changes. Invocation authorizes read-only inspection and non-destructive verification only where allowed by the runtime, including risk-selected collaboration between read-only review agents if the platform supports isolation and peer messaging. It does not authorize remediation or PR publication.

## Uses

* Agent: `contexts/review/agents/code-reviewer.md`
* Skill: `contexts/review/skills/review-change/skill.md`
* Rule: `contexts/review/rules/code-review.md`
* Output contract: `contracts/review-evidence.md`
* Optional input contract: `contracts/test-evidence.md`

## Inputs

* Explicit target or identified current workspace change, and intended comparison base when known.
* Optional change objective, Change Boundary, requirements, scenarios, work item, ADRs, PR claims, test evidence, risk constraints or project review instructions.
* Available repository inspection/verification capabilities, optional existing OCR or other helpers, and optional agent-team messaging capabilities or explicit preference for collaborative review.

## Output

A `PASS`, `FAIL`, or `INCOMPLETE` review report with reviewed base/head identity, file coverage, risk profile, verified and outstanding findings, check evidence, stale/unavailable checks, actual team mode and collaboration evidence when used, and remediation or investigation needs. A report from native review is valid without OCR.

## Boundary

Read-only. Does not authorize changing code or tests, staging, committing, pushing, creating/publishing PRs or review comments, approving a hosted PR, merging, releasing, deploying, installing OCR, or transmitting code to an unapproved provider. If the target or evidence cannot be inspected, record `INCOMPLETE` rather than inventing a clean review.

