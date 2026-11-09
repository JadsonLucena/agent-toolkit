# Review Change

## Purpose

Perform a complete, read-only, risk-proportionate native code review of a Git change, **after OCR-first context preparation when permitted**. Produce a portable review result under `contracts/review-evidence.md`, suitable for human assessment and the Git pre-PR gate. An optional external engine may accelerate investigation but cannot define review completeness.

## Uses

* Rule: `contexts/review/rules/code-review.md`
* Skill: `contexts/review/skills/verify-findings/skill.md`
* Skill: `contexts/review/skills/coordinate-review-team/skill.md`
* Output contract: `contracts/review-evidence.md`
* Optional input contract: `contracts/test-basis.md`
* Optional input contract: `contracts/test-evidence.md`
* Optional input contract: `contracts/requirements.md`
* Optional input contract: `contracts/work-item.md`

## Working State

Track target and base/head identity; change boundary and stated claims; changed/selected/reviewed/excluded/unreviewed files; applicable requirements/contract evidence; risk profile and affected consumers; deterministic check results and provenance; raw and verified findings; selected collaborative team mode/roles, peer questions and resolutions when applicable; limitations and review verdict.

## Operational Graph

```mermaid
flowchart TD
    Start --> Preflight
    Preflight --> SkipOCR{no-ocr flag?}
    SkipOCR -->|yes| NeutralGit
    SkipOCR -->|no| OCRFirst[prepare_context: detect OCR >= 1.9]
    OCRFirst -->|available| OCRRules[OCR file/rule delegation]
    OCRFirst -->|absent/incompatible/failed| NeutralGit
    OCRRules --> Scope[Full original Git scope]
    NeutralGit --> Scope
    Scope --> Risk
    Risk --> Mode{Useful supported team?}
    Mode -->|yes| TeamCoordination
    Mode -->|no| NativeReview
    TeamCoordination --> PeerChallenges
    PeerChallenges --> NativeReview
    NativeReview --> VerifyFindings
    VerifyFindings --> CoverageAndEvidence
    CoverageAndEvidence -->|complete, no blockers| Pass
    CoverageAndEvidence -->|verified blockers| Fail
    CoverageAndEvidence -->|unknown, stale, incomplete| Incomplete
```

## Workflow

1. **Preflight — identify the change.** Resolve the explicitly supplied PR, commit, commit range, branch comparison, or working-tree changes. Identify the relevant base, head SHA, repository policy, current working-tree state, and whether files can be inspected. Do not silently assume `main` or fabricate a SHA. A missing review target is a blocker.
2. **Mandatory host-neutral preparation.** Before any investigation, freeze repository identity, complete Git inventory, target SHA/workspace fingerprint, risk and distinct concerns. Follow `contexts/review/rules/code-review.md` for helper handling and `contexts/review/skills/coordinate-review-team/skill.md` for runtime collaboration. `adapters/review/run_review.py` and `prepare_context.py` are reference implementations; any host can implement equivalent semantics without Python.
3. **Inventory and scope.** Independently verify the bootstrap's full changed-file list (including staged/unstaged/untracked content for workspace reviews). Compare the intended Change Boundary or slice to the diff. Record each exclusion and affected dependent file or consumer. For a large diff, divide the review into coherent groups and reconcile the groups to the original file set. A partial scan must be labeled partial.
4. **Understand behavior.** Read changed code, callers, callees, constraints, existing tests, project conventions, and applicable architecture/requirements material. Distinguish authoritative contract evidence from PR claims and author's explanations. If documentation is absent, inspect behavior and contracts in the repository; record requirements as unverified rather than inventing them.
5. **Select proportionate collaboration.** Apply the single normative selection and relay policy in `contexts/review/skills/coordinate-review-team/skill.md`; do not duplicate team sizing or bind the canonical workflow to any specific host's Task/resume API.
6. **Gather deterministic evidence.** Inspect relevant test assertions and available recorded build/lint/test/CI results. Run only non-destructive, permitted local checks when the platform permits them. Record exact command/source, result, timestamp or other freshness evidence, and code identity. Do not mark a check passed from a test filename, README claim, cached statement, or successful tool exit without inspecting its relevant results.
7. **Independent investigation and targeted collaboration.** Perform specification-compliance and correctness review before stylistic concerns. Evaluate reachable edge cases, behavioral changes, removed guarantees, data flow, impacted consumers, security, architecture, concurrency, resilience, test adequacy, performance/observability and rollout where applicable. Name concrete consequences. When team mode is selected, run separable lenses concurrently where safe and exchange evidence, questions and challenges between relevant peers; the lead retains the complete diff inventory. Native-solo review covers all relevant lenses without pretending that agents collaborated.
8. **Verify findings.** Apply `contexts/review/skills/verify-findings/skill.md` and verifier thresholds from `contexts/review/skills/coordinate-review-team/skill.md`. Require independent source inspection, not votes; document any native falsification fallback truthfully.
9. **Reconcile coverage and verdict.** Compare reviewed files with the initial inventory, record exclusions and failed work, verify whether required checks are current for the reviewed head, and generate `PASS`, `FAIL` or `INCOMPLETE` according to `contexts/review/rules/code-review.md`. A clean report with missing coverage is `INCOMPLETE`. If the head changes after review, the evidence becomes stale for pre-PR use.
10. **Report.** Supply the review target, coverage, risk, requirements inspected, checks observed/not executed, actual team mode and active roles (if any), material peer-to-peer/relayed challenges and resolutions, verified findings (with location, evidence, consequence, severity, confidence, priority and disposition), blockers, unresolved questions, and exact review verdict. State that code was not changed and remote Git actions were not performed.

## Output

A review result conforming semantically to `contracts/review-evidence.md`. Prioritize actionable verified findings and clear coverage/status over cosmetic commentary. A native result is equally valid whether OCR or another helper was present.

## Boundaries

* Read-only: do not edit implementation, tests, configuration or repository state; do not stage, commit, push, post PR reviews, create PRs, merge, release or deploy.
* Do not use potentially mutating check commands without explicit permission. Do not install helper software, request additional credentials or transmit repository content outside approved boundaries.
* Do not invoke another context's internal agents or skills merely to obtain evidence. Consume portable contract material or explicit user-provided sources.
* Do not claim live Agent Teams support, direct messaging or independently isolated verification unless the runtime actually provided and recorded them.
* Do not publish approval, claim all checks passed, or certify an incomplete review. Offer findings for separately authorized remediation.

## Stop Conditions

Report `INCOMPLETE` for the affected review if the target/diff is unavailable, required files are unreadable, mandatory verification is stale/missing, material business meaning is ambiguous, or review coverage cannot be established. Keep completed findings and exact reasons rather than hiding partial progress. An optional tool failure alone is not a stop condition when native review remains feasible.

