# Create Pull Request

## Intent

Create a remote pull request for an already published change using a verified head/base, truthful description, repository template/conventions, and explicit readiness state.

## Invocation

Use only when remote pull-request creation is explicitly requested.

Invocation authorizes a draft when publication is explicitly requested and signed `review_profile=gate` evidence is missing, stale, failed, or only advisory. The description must name that gap and must not claim `PASS`. Invocation authorizes a ready-for-review PR only after explicitly signed `review_profile=gate` independent code review (PASS), applicable project tests, and lint have satisfied the pre-creation gate. Advisory evidence never satisfies ready. The skill must discover repository-defined lint/tests and established coverage checks, inspect effective pre-commit/pre-push hooks and completed CI evidence, reuse only results valid for the intended revision and full scope, and execute missing non-destructive checks when authorized before creation. A workflow triggered only after PR creation does not satisfy this gate. The skill may perform the read-only preparation checks required to create it safely and truthfully; when review evidence is missing, an explicitly authorized multi-context orchestrator may obtain a separate read-only Review result before retrying. The Git workflow consumes the neutral contract and does not invoke Review internals. When a protected pre-creation runtime is configured, creation goes through that runtime.

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
* Independent review evidence for the intended revision, plus actual test/lint and established coverage results (or documented genuine non-applicability) with execution source and revision/scope; missing checks must be executed when authorized during preflight.
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

Do not create a ready-for-review PR when independent review is missing, not a signed gate `PASS`, stale or incomplete, or when applicable tests/lint are missing, failed or stale. An explicitly requested draft may be created in that case only when its description states the gap and does not claim `PASS`. Do not create any PR when the head branch is unpublished, the base is materially ambiguous, preparation is `blocked`, or creation would be unsafe or misleading.
