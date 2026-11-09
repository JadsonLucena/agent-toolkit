# Migration

## Structural Change

The repository moved from artifact-type-first top-level folders to context-first ownership:

* Git rules and the Git Engineer moved under `contexts/git/`.
* Testing rules, skills, and the Test Engineer moved under `contexts/testing/`.
* Requirements engineering and backlog planning are owned by `contexts/requirements/`.
* `contracts/` contains neutral semantic handoffs and is not a fifth canonical artifact type.

## Moved Responsibility

* Detailed atomic commit execution moved from `git-engineer.md` to `contexts/git/skills/create-semantic-commits/skill.md`.
* Semantic-version decision procedure lives in `contexts/git/skills/determine-semantic-version/skill.md`.
* Branch, synchronization, integration, and worktree procedure lives in `contexts/git/skills/manage-branch-work/skill.md`.
* `git-engineer.md` owns Git specialization, evidence discipline, routing, authorization boundaries, and handoffs.
* Testing consumes `contracts/test-basis.md` only as optional evidence and remains independent from Requirements agents and skills.

## Naming Migration

The following names were made more explicit so commands express engineering intent and backlog artifacts own a narrower concern:

* `contexts/requirements/rules/planning.md` → `contexts/requirements/rules/backlog.md`
* `contexts/requirements/skills/planning/skill.md` → `contexts/requirements/skills/backlog-planning/skill.md`
* `contexts/requirements/commands/elicit.md` → `elicit-requirements.md`
* `contexts/requirements/commands/specify.md` → `specify-requirements.md`
* `contexts/requirements/commands/audit.md` → `validate-requirements.md`
* `contexts/requirements/commands/items.md` → `build-backlog.md`
* `contexts/requirements/commands/refinement.md` → `refine-backlog.md`
* `contexts/testing/commands/test.md` → `generate-tests.md`
* `contracts/testing.md` → `contracts/test-basis.md`

## Preserved Semantics

* Existing Git, Gitflow, semantic-commit, semantic-version, and testing rules remain authoritative.
* Requirements remains usable without a repository.
* Testing remains usable without Requirements artifacts.
* Git remains usable without Requirements or Testing.
* Cross-context evidence may support decisions but does not silently become authoritative intent.
* Material semantic ambiguity must be surfaced rather than guessed.

## Intentional Consolidation

* Backlog creation and refinement use one backlog-planning skill with explicit `build` and `refine` modes.
* Requirement and work-item semantics remain separate contracts.
* Elicitation and specification use the same Requirements contract to preserve semantic continuity without introducing a workflow-specific mega-contract.
* Cross-context data shapes remain contracts rather than generic shared rules.

## Methodology Hardening

The context-first migration was also hardened against later requirements-review findings:

* `requirements/rules/tailoring.md` makes rigor proportional to risk and uncertainty instead of document count.
* Elicitation now separates Need, Business Goal, success evidence, Current/Future State, Work Scope, Product Boundary, and candidate solutions when those concerns are material.
* Requirements semantics now cover conditional data, quality, security, transition, scenario, rationale, and rule-governance concerns without making every concern mandatory.
* `example-discovery/skill.md` owns stable behavioral Scenario Sets plus domain examples, counterexamples, boundaries, and questions before test automation.
* `contracts/test-basis.md` preserves portable scenario identity into Testing, while `contracts/test-evidence.md` records scenario-to-test coverage and verification without mutating upstream semantics.
* Backlog planning now supports coherent vertical/use-case/journey slicing, explicit learning work, trim-the-tail candidates, critical guarantees, optional Story Mapping semantics, User Story diagnostics, and fuller Use-Case 2.0 progression from simplest useful to sufficient behavior.
* Requirement Patterns now preserve applicability, investigation guidance, related concerns, downstream considerations, and organizational learning without becoming automatic requirements.
* Validation is read-only and evaluates missing knowledge, cross-artifact consistency, Use-Case set quality when applicable, severity, and risk-proportional readiness.
* `/requirements/shape-change` provides one neutral composite entry point over the existing Requirements capabilities without duplicating their procedures or expanding into design/implementation scope.
* Test generation may diagnose production defects but may not modify production artifacts without separate authorization.
* Commit verification may diagnose failures but may not edit the authorized implementation merely to make a commit pass.

## Intentional Deletions

Former top-level `rules/`, `skills/`, and `agents/` copies were removed after migration to avoid duplicate canonical sources.

Detailed procedures removed from agents are not semantic losses when their durable constraints remain in rules or their reusable workflow moved into a skill.

No vendor-specific adapter files are introduced by this migration.

## 2026-11 — Portable Review evidence and host-native execution

* Added two-phase review: `run_review.py --prepare-only --out /tmp/context.json`
  and `run_review.py --validate-evidence /tmp/evidence.json --context /tmp/context.json`.
  Subprocess `-- <reviewer-command>` remains supported. Both paths use one
  validator with target freshness and complete coverage checks.
* Added `--base-branch` to resolve a local or cached remote-tracking base,
  without fetching. Local divergence from cached `origin/<branch>` warns.
* Added `--output-language` for human prose. Machine field names stay English.
* `--concern` canonical names are `contract`, `correctness`,
  `security`, `reliability`, `testing`, `architecture`; aliases
  `spec`, `specification` and `arch` normalize to canonical values.
* Small R3 changes with one or two real concerns are valid but must record
  below-ideal N. Isolated verifier remains required when isolated tasks exist.
* Confirmed blockers yield FAIL even when unresolved questions remain. Every
  question is retained. R2 may use two independent lenses for cost efficiency.
* Specialist outputs now require self-contained source evidence and verified
  head identity under `contracts/review-specialist-evidence.md`.
  **Compatibility:** host serializers returning only free-form narratives or
  "previous message" pointers must adapt to this contract. CLI changes are
  additive; adapters may implement equivalent semantics without Python.
* OCR-excluded paths remain required natively and system OCR rules are generic,
  nonbinding hints. Project-specific OCR rule injection was **not** added
  without an independently verified adapter capability.

## 2026-11 — Advisory / Gate Profiles and Review Calibration (P13–P22)

* **Profile semantics:** `review_profile=advisory|gate` is frozen with the
  review context. Without attested independent execution, default to advisory.
  The `review_status` enum remains PASS/FAIL/INCOMPLETE; advisory PASS is
  labeled `PASS (advisory)` for humans and **never** satisfies a pre-PR gate.
* **Pre-PR breaking change (intentional fail-closed):** older signed review
  JSON missing `review_profile` is rejected. Independent signers must
  explicitly include `"review_profile": "gate"` in the exact SSHSIG-signed
  bytes; no reviewer flag or signature can promote advisory evidence.
  No change to the SSHSIG namespace, trust policy or key custody.
* **Finding fields (additive/backward-compatible):** optional
  `likelihood=high|medium|low`, `origin=introduced|pre-existing|amplified-pre-existing`,
  `lead_confirmed` on confirmed blockers, and `external_evidence[]`
  (repository, pinned SHA, files, claim_supported). An amplified existing
  risk needs evidence of increased exposure and a fix/decision-needed choice.
  Lower-impact unresolved questions may declare `material:false`.
* **Review depth:** calibrated impact/likelihood/confidence, R3 triggers
  and eight falsification heuristics live in the canonical
  `contexts/review/rules/code-review.md` and
  `contexts/review/rules/high-risk-patterns.md`. They are not automatic
  blockers. Requirement conflicts without valid supersession are
  `decision-needed`; other-repository claims require pinned context.
* **Host neutrality:** profile propagation and evidence checks are available
  in the optional Python adapter; runtime-specific tasks, models and
  project conventions are not new canonical format requirements.
  Choosing whether project conventions (SOLID, DDD, Clean Architecture)
  should be mandatory remains a **team policy proposal**, not enabled by
  this toolkit migration.
