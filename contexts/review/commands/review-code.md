# Review Code

## Intent

Perform an independent, risk-proportionate and evidence-based review of a change, producing a portable verdict and actionable findings for development or PR preparation.

## Invocation

Use to review a specified PR, branch diff, commit/range, file set, or current workspace changes. Invocation authorizes read-only inspection and non-destructive verification only where allowed by the runtime, including risk-selected collaboration between read-only review agents if the platform supports isolation and peer messaging. It does not authorize remediation or PR publication.

**Mandatory preparation before reviewer analysis:** The approved host runtime must invoke `adapters/review/run_review.py` (which calls `adapters/review/prepare_context.py`) and supply an authorized host-reviewer command. For a range: `python3 /path/to/agent-toolkit/adapters/review/run_review.py --repo . --from <base> --to <head> -- <approved-reviewer-command>`. For a commit use `--commit <sha>`; for workspace omit comparison flags. The host-reviewer command receives the complete context on stdin and must independently inspect the full Git change inventory before producing Review evidence. This command Markdown alone cannot start a model: host configuration must bind `/review/review-code` to the executable runner or faithfully implement the same required ordering.

## Uses

* Agent: `contexts/review/agents/code-reviewer.md`
* Skill: `contexts/review/skills/review-change/skill.md`
* Rule: `contexts/review/rules/code-review.md`
* Output contract: `contracts/review-evidence.md`
* Optional input contract: `contracts/test-evidence.md`

## Inputs

* Explicit target or identified current workspace change, and intended comparison base when known.
* Optional change objective, Change Boundary, requirements, scenarios, work item, ADRs, PR claims, test evidence, risk constraints or project review instructions.
* Available repository inspection, OCR and actual Task/subagent capabilities. The lead must classify R0–R3 risk and separable concerns before any spawn. The executable planner accepts `--risk-profile`, repeated `--concern`, `--task-capable`, `--isolated-subagents`, `--direct-peer-supported` and `--lead-implemented-change`. In Cursor Task without observed direct messaging the default is `team-relayed`, not native-solo.
* Optional flag `--no-ocr` propagated **unchanged** to the runtime runner. When present, use only neutral Git inventory and native review: never import the OCR adapter, check `ocr --version`, call `ocr delegate`, or require OCR. Record `optional_helpers.ocr.status=disabled`.

**Default ordering (without `--no-ocr`):** run the preparation bootstrap **before reviewing code**; check OCR availability and version (>= 1.9.0), resolve OCR file selection/rules when available, and then perform the complete native review using the original Git inventory and supplemental OCR context. OCR errors or absence trigger native-only fallback. OCR delegation is a deterministic helper, not a separately executed LLM review or source of a verdict. The invocation must never report successful review based only on `prepare_context.py` output.

## Output

A `PASS`, `FAIL`, or `INCOMPLETE` report with frozen repo/base/head or workspace fingerprint, full file coverage, risk, actual `execution_mode`, `team_members` role/reason/Task IDs, `coordination` transport, bounded `peer_threads`, `independent_verification`, `n_justification`, verified findings, checks and unresolved questions.

## Boundary

Read-only. Does not authorize changing code or tests, staging, committing, pushing, creating/publishing PRs or review comments, approving a hosted PR, merging, releasing, deploying, installing OCR, or transmitting code to an unapproved provider. If the target or evidence cannot be inspected, record `INCOMPLETE` rather than inventing a clean review.

