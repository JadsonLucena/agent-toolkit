# HTTP API Engineering Behavioral Evaluations

These cases exercise **conditional selection and observable behavior** for the existing Requirements, Design, Implementation, Testing, Review and Delivery capabilities. No new commands, agents, review gates or acceptance authority are defined by this catalog. These are synthetic prompts and rubrics, **not actual agent output**.

## Run the Catalog

```sh
python3 scripts/requirements_evals.py --catalog evals/api/cases.json
python3 scripts/requirements_evals.py --catalog evals/api/cases.json --observations /path/to/observations.json
```

The first command validates catalog structure only. To assess real behavior, construct an isolated fixture matching each scenario; pin an actual source baseline and repository base/head or workspace fingerprint for Review cases. Invoke the **real** command in an approved host and capture the full transcript, observed calls, resulting artifacts and verification status. A separately identified evaluator must assess each criterion with direct quotes for positive evidence and full-transcript inspection for negative evidence. Preserve the exact tested revision. Do not invent transcripts, observed tool execution, synthetic identities or completed checks. Do not run payment flows against live providers.

Output-boundary scenarios additionally contrast justified field disclosure/redaction with forbidden property leakage and unnecessary Presenter ceremony. The synthetic fixtures contain no real PII; any actual evaluator must use synthetic data and independently inspect reachable response/log paths.

Optimistic concurrency scenarios focus on stale preconditions and atomic writes; catalog checks alone do not establish actual concurrency safety.

Observe both **positive selection** and **negative selection**: the agent should not impose keyset, hypermedia, JSON:API, idempotent PATCH or any particular framework absent governing needs. The rubric's absence checks distinguish appropriate restraint from a rote checklist. Tests of source files, links and metadata are structural—not behavioral proof.

A resulting INCOMPLETE means host behavior or other required evidence was not observed; it is not a failing API implementation by itself. A reviewer-attested PASSED records assessed evidence, not machine-proven correctness. See [Evaluation Principles](../README.md) and the [Review evaluation method](../review/README.md).
