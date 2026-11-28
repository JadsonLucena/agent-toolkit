# Security Code Review — Behavioral Falsification Evaluations

The [cases.json](cases.json) catalog exercises the existing `/review/review-code` capability and its risk-selected Security Reviewer. It contains **14 synthetic cases** including exploitable paths, protective counterevidence, missing upstream evidence, source-as-instruction attacks, and risk-proportionate negative selection. It creates **no new review role, gate or severity policy**.

## Structural validation (no model executed)

```sh
python3 scripts/requirements_evals.py --catalog evals/security/cases.json
```

This validates the rubric's syntax and check identifiers only. A green CI run or valid catalog **cannot** be reported as vulnerability-detection success.

## Actual behavioral evaluation

1. Materialize an isolated, synthetic Git fixture for each case with the **stated paths, controls, principal roles, and changed behavior**. Freeze the actual base/head SHA (or workspace fingerprint), declared risk, relevant requirements and expected scope. Do not use live payment providers, credentials or customer PII.
2. Install the toolkit at a **recorded revision** in a real approved host. Invoke `/review/review-code` against the fixture using the same review profile and role-selection policy as production. Preserve the complete observed transcript and tool-event provenance, including missing tests and unresolved questions.
3. Assess every criterion with a **separate named evaluator**. `presence` passes require an exact supporting transcript quote. `absence` passes require inspection of the entire transcript and a reasoned assessment that the prohibited behavior did not occur. Mark inaccessible or contradictory evidence `uncertain`.
4. Compare **native-only** (`--no-security-audit` or equivalent) versus **native + approved Cloudflare guidance** on the same fixed fixture and toolkit revision. Record each host/model version, run configuration, selected references, tool calls, token/cost/time usage where measured, and any host limitations. Do not assume the external adapter improved performance.
5. Produce one assessment JSON (version 1, `assessments` keyed by `case_id`, `reviewer`, relative `transcript` path and `checks`: `id`, `verdict`, `rationale`, `quote` when applicable). Evaluate it with the existing evidence checker:

```sh
python3 scripts/requirements_evals.py --catalog evals/security/cases.json --observations /safe/path/security-observations.json
```

The checker returns **PASSED**, **FAILED**, or **INCOMPLETE** for *assessed observations*, not a mechanically proven security outcome. Never invent host execution, independent identities or transcripts. If no host observations exist, behavioral effectiveness remains **NOT MEASURED**.

## Comparing outcomes

Track detection recall against the fixture's **known security flaws**, false-positive rate on protected-counterexample cases (SEC-02, 04, 06, 10, 12 and 14), source-evidence quality, proper `INCOMPLETE` handling (SEC-08), and security-review cost. Report numerator/denominator and exact dataset version, not an aggregate score that hides serious misses. A single passing run cannot demonstrate generalization: repeat under at least one additional fixture variation/host when practical and explicitly state the limits of the sample.

Only verified source-based findings may block the Lead's ordinary review. The evaluator records evidence; it does **not** grant gate independence or PR publication authority. See [Evaluation Principles](../README.md) and the [Review evaluation method](../review/README.md).
