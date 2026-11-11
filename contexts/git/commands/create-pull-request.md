# Create Pull Request

## Intent

Create a remote pull request for an already published change using a verified head/base, truthful description, repository template/conventions, and explicit readiness state.

## Invocation

Use only when remote pull-request creation is explicitly requested.

Readiness, draft, and gate claims are the Pre-Creation Quality Gate in `contexts/git/rules/pull-request.md`. Execute that decision through `contexts/git/skills/manage-pull-request/SKILL.md` in `create` mode. Check discovery stays in `contexts/git/rules/git.md`. This invocation does not authorize a description that claims gate when that rule does not.

## Uses

* Agent: `contexts/git/agents/git-engineer.md`
* Skill: `contexts/git/skills/manage-pull-request/SKILL.md` in `create` mode
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

Do not create a pull request when `contexts/git/rules/pull-request.md` does not allow that publication. Do not claim gate in the description unless that rule says the gate is satisfied.
