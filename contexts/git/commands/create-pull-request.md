# Create Pull Request

## Intent

Create a remote pull request for an already published change using a verified head/base, truthful description, repository template/conventions, and explicit readiness state.

## Invocation

Use only when remote pull-request creation is explicitly requested.

Invocation authorizes creation of the remote PR object only **after** current independent code review (PASS), applicable project tests, and lint have satisfied the pre-creation gate, including for draft PRs. The skill may perform the read-only preparation checks required to create it safely and truthfully; when review evidence is missing, an explicitly authorized multi-context orchestrator may obtain a separate read-only Review result before retrying. The Git workflow consumes the neutral contract and does not invoke Review internals.

## Uses

* Agent: `contexts/git/agents/git-engineer.md`
* Skill: `contexts/git/skills/manage-pull-request/skill.md` in `create` mode
* Rule: `contexts/git/rules/pull-request.md`
* Rule: `contexts/git/rules/git.md`
* Rule: `contexts/git/rules/gitflow.md` when applicable
* Optional contract: `contracts/work-item.md`
* Optional contract: `contracts/test-basis.md`
* Required review handoff contract: `contracts/review-evidence.md`
* Optional contract: `contracts/test-evidence.md`

## Inputs

* Published head branch or remote ref.
* Intended base branch.
* Prepared title/description when available, otherwise sufficient evidence to prepare them.
* Optional PR Boundary and traceability references.
* Independent review evidence for the intended revision, and actual test/lint results or documented genuine non-applicability; these may be collected during authorized read-only preflight.
* Optional explicit draft/ready intent when repository policy does not determine it.

## Output

A verified remote PR result containing:

* PR identifier and URL/reference;
* repository and verified head/base;
* title and description used;
* draft/ready state;
* independent review verdict, identity/coverage, and applicable test/lint evidence;
* preparation and verification summary;
* relevant limitations, dependencies, and follow-up work.

If an equivalent open PR already exists, report/reuse it instead of creating a duplicate.

## Boundary

This command authorizes only remote PR creation plus the read-only checks needed to support it.

It does not authorize pushing unpublished commits, creating commits, rewriting history, changing the implementation, assigning reviewers, applying labels or milestones, enabling auto-merge, merging, closing an existing PR, deleting branches, releasing, or deploying unless those operations are separately and explicitly authorized.

Do not create the PR when independent review is missing, not PASS, stale or incomplete; applicable tests/lint are missing, failed or stale; the head branch is unpublished; the base is materially ambiguous; preparation is `blocked`; or any required verification makes creation unsafe or misleading.
