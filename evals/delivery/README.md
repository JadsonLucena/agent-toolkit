# SDD Delivery end-to-end behavioral evaluations

The [catalog](cases.json) lists forty-two high-value pilot behaviors for the future native SDD workflow: simple feature, financial risk, unresolved source meaning, TDD RED integrity, changed baseline, unproductive retries, unsafe parallelism, side-effect replay, stale review, missing operational observations, and explicit Git handoffs for commits and PR planning. The direct Implementation case verifies Git policy outside Delivery. Additional Integration cases cover Review failure and revision freshness, the distinction between preparation and publication, authorized Drafts with gaps, post-PR CI failures, and separately authorized merge with target-state verification.

Additional DL-22–DL-28 cases distinguish PR integration from complete Product Slice behavior, check cross-PR interaction guarantees, verify selective context loading without dropping critical obligations, detect inaccessible or superseded sources, and permit evidence-backed learning slices without invented feature delivery.

DL-29 explicitly checks the blocked remote-publication path when a branch exists only locally and the caller did not authorize a push.

**DL-30–DL-34 add explicit negative-path checks for Design, Testing and Delivery authority, feedback-driven changes and independent Review. They require observed tool traces and scoped source evidence; a coordinator or specialist must not acquire ownership from a convenient available tool.**

**DL-35–DL-38 cover derived local-commit authority, Delivery handoff, multiple TDD cycles per atomic intention, and explicit no-commit restrictions. Each requires real Git history and tool-trace evidence rather than structural text matches.**

**DL-19 now blocks remote Draft publication with missing checks or Code Review. DL-39–DL-42 exercise direct PR creation, required Review routing, Draft non-bypass, freshness after code changes, and the optional guarded GitHub adapter's signed-Draft restriction. These scenarios still require observed agent/host traces to establish behavior.**

These are specifications of tests, not tests that have been run. A passing structural CI is not evidence of an agent executing a software change.

## Run in a genuine host

1. For each case, prepare a disposable fixture repository and authoritative approved source artifacts. Pin the repository and exact base/head or workspace fingerprint. Set only the explicitly described operation permissions; use fake/sandbox external services for high-risk cases.
2. Invoke the actual canonical `/delivery/deliver-change` workflow through the host; preserve full conversation, tool observations, commands, source revisions, denial/approval events, and resulting Git state.
3. Independently assess each specified check against the real transcript. Positive passes need exact quotations; absence passes require inspection of the complete trace.
4. Supply all findings to the existing, provider-neutral rubric checker; do not substitute an imagined transcript or a source-code string match:

```sh
python3 scripts/requirements_evals.py --catalog evals/delivery/cases.json
python3 scripts/requirements_evals.py --catalog evals/delivery/cases.json --observations /path/to/delivery-observations.json
```

The first invocation validates the fixture catalog only and explicitly evaluates **no agent behavior**. Missing observations remain INCOMPLETE, including cases for which no supported runtime exists. Never store secrets, personal information, external production data, or private transcripts in this repository.

## Exit conditions

The SDD MVP requires at least one actually executed, complete vertical change through implementation and applicable review with source/revision evidence, and truthful state/authorization boundaries. A v1.0 quality claim additionally requires representative negative-path runs and independent assessment. The outcomes may be pending where production observation is unavailable.

This catalog does not authorize changing a real repository, remote PR creation, external effects, agent execution or installation of a provider. It is intentionally runtime-neutral.
