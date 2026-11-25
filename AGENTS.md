# Agent Toolkit — Instructions for Coding Agents

These instructions apply when **maintaining this repository**. They do not redefine the behavior of specialist agents supplied by the toolkit or automatically apply to repositories that install toolkit skills.

## Orient Before Editing

- Identify the smallest affected context and read only the relevant source files first. Do not load every rule, skill, or agent merely because it exists.
- Read [ARCHITECTURE.md](ARCHITECTURE.md) for canonical ownership, dependency direction, naming, Skill format, and command structure. Its artifact matrix is consumed by the structural linter.
- Read the applicable `contexts/<context>/rules/` and the exact Skill, Command, Agent, or Contract being modified. Treat their declared boundaries as authoritative for their responsibility.
- Inspect the actual repository state and intended change scope before edits. Distinguish observed facts from assumptions and unresolved questions.

## Preserve Ownership and Boundaries

- Keep `contexts/` organized by engineering responsibility and preserve the canonical Rule / Skill / Command / Agent distinctions described in [ARCHITECTURE.md](ARCHITECTURE.md).
- Put durable behavioral constraints in the owning Rule, reusable procedures in Skills, invocation and authorization in Commands, specialist responsibilities in Agents, and portable handoff semantics in `contracts/`. Link to owners rather than copying their normative content.
- When adding, renaming, or removing canonical artifacts, update the artifact matrix in `ARCHITECTURE.md`, affected references, relevant contracts, and regression tests.
- Keep `adapters/` optional and provider-specific. Canonical workflows must remain usable without a vendor adapter; do not claim runtime enforcement from Markdown alone.
- Preserve unrelated edits and avoid scope expansion. Do not silently change upstream requirements, contract semantics, or authorization while adjusting downstream artifacts.

## Documentation Ownership

- `README.md`: project purpose, capabilities, first steps, and links for readers; **not** a rulebook, operation log, or detailed workflow specification.
- `ARCHITECTURE.md`: current structural architecture, canonical matrix, and cross-context invariants.
- `AGENTS.md`: concise repository-maintenance instructions and verification entry points; reference, do not reproduce, canonical rules.
- Context files, `contracts/`, and adapter READMEs: detailed domain semantics, evidence shapes, and integration instructions respectively.
- Update all affected links when moving or removing documentation. Do not preserve obsolete paths or historical compatibility notes as active guidance.

## Validate the Change

From the repository root, run:

```sh
python3 scripts/toolkit_lint.py
python3 -m unittest discover -s tests -v
```

When evaluating toolkit claims or writing assessment criteria, use the [evaluation principles](evals/README.md) as the single assessment methodology. They guide evidence judgments, not specialist authorization or runtime enforcement.

For evaluation-catalog changes, also run the relevant catalog command documented in [toolkit-validation.yml](.github/workflows/toolkit-validation.yml). Routing scenarios additionally use `python3 scripts/routing_evals.py`; without host observations this validates catalog structure only, not selection behavior. The workflow defines the current CI check set. These checks validate structure and selected evidence, **not** correctness of actual agent behavior or runtime authorization.

Inspect the final diff for broken links, duplication, stale references, and unintentional changes. Report exactly which checks ran, their results, and any checks that could not be executed.

## Git and External Effects

Use [Git rules](contexts/git/rules/git.md), [Pull Request rules](contexts/git/rules/pull-request.md), and the relevant Git Skill for staging, atomic commits, branch work, reviews, and PRs. Treat external mutations (pushes, remote PR creation, merge, release, deployment) as separate authorization decisions; do not infer them from permission to edit files.
