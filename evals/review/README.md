# SDD Code Review behavioral evaluation cases

The rubric catalog [cases.json](cases.json) exercises the existing Review specification lens, reliability failure-mode analysis, the single Lead verdict, source authority, and evidence integrity. These are **evaluation inputs, not actual agent outputs**.

A host must create or supply each synthetic Git fixture with explicit repository identity and fixed base/head (or workspace fingerprint) before invoking `/review/review-code`. Execute the real Agent with the stated source materials, capture its complete transcript and observed tool actions, then have a separate evaluator assess each check. Never fabricate a transcript, a tested revision, or reviewer identity.

Use the existing provider-neutral evidence checker:

```sh
python3 scripts/requirements_evals.py --catalog evals/review/cases.json
python3 scripts/requirements_evals.py --catalog evals/review/cases.json --observations /path/to/review-observations.json
```

The first command validates the rubric shape only. The second validates reviewer-attested evidence from actual transcripts; even an attested PASSED is not a machine-proven behavioral correctness claim. `presence` requires exact quoted transcript evidence for a pass; `absence` requires full independent transcript inspection. Missing evaluations remain INCOMPLETE.

The `RV-REL-*` cases deliberately include both reachable defects and correctly protected paths: a false-positive finding is a failed evaluation, not a safer review. Fixtures must provide the actual source/configuration and pinned contracts claimed by their inputs. Neither this catalog nor structural CI proves reviewer precision, recall, severity calibration or native host behavior without observed executions.

These cases are not a second Review gate, nor a requirement to materialize example repositories inside the toolkit. Git and Review continue to own their individual authorization and verdict semantics. Do not commit confidential project data or transcripts.
