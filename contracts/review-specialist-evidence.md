# Review Specialist Evidence Contract

## Purpose

A provider-neutral data handoff between independently isolated investigation
lenses, a source-inspecting finding verifier and the Code Review Lead.
JSON is the Python adapter representation; other hosts may use a lossless
structured mapping. No provider-specific transport is normative.

## First-pass Specialist

Require `review_id`, `repository`, `target`, `verified_head_sha`,
`role`, `task_id` (real isolated runtime identity), `reviewed_files`,
`candidate_findings`, `uncertainties` and `relay_requests`.
All specialists must confirm the same frozen target and head.

Each candidate finding requires `finding_id`, `location` (file:line),
`claim`, `trigger`, `evidence`, `consequence`, `severity`
(critical/high/medium/low) and `confidence` (high/medium/low).
Cross-lens requests contain `kind`, `recipient_role`, `subject`,
`evidence_refs` and `requested_action`.

First-pass agents must not issue `PASS`, `FAIL`, `review_status` or
`verdict`, must not receive the Lead's unverified hypotheses, and must not
refer to absent previous messages. Never include secrets or full transcripts.

## Independent Finding Verifier

Require the same target/review identity and actual isolated `task_id`,
`verified_head_sha`, `verification_method=source-inspection`,
`inspected_files` and `verified_findings`. For **every** candidate,
record `finding_id`, `verification_status`
(confirmed/supported/unverified/refuted), `location`, independent
`source_evidence`, counter-evidence when available, impact and disposition.
Votes are not evidence.

## Lead Result

The Lead reconciles all original Git paths, preserves each candidate
disposition and alone issues the verdict using
`contracts/review-evidence.md`. English evidence keys remain stable;
human prose follows user/project language.
