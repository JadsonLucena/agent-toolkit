# Review Code

## Intent

Perform an independent, risk-proportionate and evidence-based review of a change, producing a portable verdict and actionable findings for development or PR preparation.

## Invocation

Use to review a specified PR, branch diff, commit/range, file set, or current workspace changes. Invocation authorizes read-only inspection and non-destructive verification only where allowed by the runtime, including risk-selected collaboration between read-only review agents if the platform supports isolation and peer messaging. It does not authorize remediation or PR publication.

**Mandatory semantics; optional adapter:** Freeze repository, target SHA/workspace fingerprint, full Git inventory, risk and separable concerns before any review. The Python `adapters/review/run_review.py` is one reference adapter, not a mandatory runtime. A host-native reviewer may use two phases: `run_review.py --prepare-only --out <context.json>`, perform the independent review using approved native capabilities, then `run_review.py --validate-evidence <evidence.json> --context <context.json>`. Equivalent host implementations must preserve the same validation and report adapter provenance.

## Uses

* Agent: `contexts/review/agents/code-reviewer.md`
* Skill: `contexts/review/skills/review-change/skill.md`
* Rule: `contexts/review/rules/code-review.md`
* Output contract: `contracts/review-evidence.md`
* Optional input contract: `contracts/test-evidence.md`

## Inputs

* Explicit target or identified current workspace change, and intended comparison base when known.
* Optional change objective, Change Boundary, requirements, scenarios, work item, ADRs, PR claims, test evidence, risk constraints or project review instructions.
* Determine actual runtime capabilities according to `contexts/review/skills/coordinate-review-team/skill.md`. Reference CLI accepts `--risk-profile`, repeated `--concern` (`contract|correctness|security|reliability|testing|architecture`), `--task-capable`, `--isolated-subagents`, `--direct-peer-supported`, `--lead-implemented-change`, `--base-branch` and `--output-language`. Aliases: `spec|specification` → `contract`, `arch` → `architecture`.
* Optional helper opt-out `--no-ocr` (or equivalent host-native setting) follows the mandatory behavior in `contexts/review/rules/code-review.md`.

**Helper policy:** Optional OCR and native fallback are defined once in `contexts/review/rules/code-review.md`. No helper result proves review completion; inspect all original Git paths.

## Output

A `PASS`, `FAIL`, or `INCOMPLETE` report with frozen repo/base/head or workspace fingerprint, full file coverage, risk, actual `execution_mode`, `team_members` role/reason/Task IDs, `coordination` transport, bounded `peer_threads`, `independent_verification`, `n_justification`, verified findings, checks and unresolved questions.

## Boundary

Read-only. Does not authorize changing code or tests, staging, committing, pushing, creating/publishing PRs or review comments, approving a hosted PR, merging, releasing, deploying, installing OCR, or transmitting code to an unapproved provider. If the target or evidence cannot be inspected, record `INCOMPLETE` rather than inventing a clean review.

