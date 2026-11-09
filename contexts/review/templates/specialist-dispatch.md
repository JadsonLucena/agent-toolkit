# Specialist Dispatch — Portable Template

This is a neutral task description. Host adapters translate its contents to their
own task APIs; this template never requires a particular IDE, model or provider.

## Frozen identity

* `review_id`, `repository`, `target` (base/head SHA or workspace fingerprint)
* `risk_profile`, `role`, `changed_files`, `output_language`
* `read_only=true`, relevant acceptance criteria when available

## First-pass assignment

The Lead supplies verified scope and applicable requirements, **not the Lead's
candidate findings or hypotheses**. Inspect actual source and affected consumers
independently, and confirm the same head SHA and target identity. Return file
coverage and self-contained findings; no approval or final verdict.

For each issue include `finding_id`, `location` (file:line), `claim`,
`trigger`, `evidence`, `consequence`, `severity` and `confidence`.
Declare uncertainties and targeted cross-lens `relay_requests` separately.
Never write "see previous message" or refer to missing transcript content.

The separate verifier receives candidate IDs after the first pass and must
inspect source independently, not merely report agreement.
