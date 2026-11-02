# Create Pull Request

## Intent

Create a remote pull request for an already published change using a verified head/base, truthful description, repository template/conventions, and explicit readiness state.

## Invocation

Use only when remote pull-request creation is explicitly requested.

Invocation authorizes creation of the remote PR object. The skill may perform the read-only preparation checks required to create it safely and truthfully.

## Uses

* Agent: `contexts/git/agents/git-engineer.md`
* Skill: `contexts/git/skills/manage-pull-request/skill.md` in `create` mode
* Rule: `contexts/git/rules/pull-request.md`
* Rule: `contexts/git/rules/git.md`
* Rule: `contexts/git/rules/gitflow.md` when applicable
* Optional contract: `contracts/work-item.md`
* Optional contract: `contracts/test-basis.md`
* Optional contract: `contracts/test-evidence.md`

## Inputs

* Published head branch or remote ref.
* Intended base branch.
* Prepared title/description when available, otherwise sufficient evidence to prepare them.
* Optional PR Boundary and traceability references.
* Optional explicit draft/ready intent when repository policy does not determine it.

## Output

A verified remote PR result containing:

* PR identifier and URL/reference;
* repository and verified head/base;
* title and description used;
* draft/ready state;
* preparation and verification summary;
* relevant limitations, dependencies, and follow-up work.

If an equivalent open PR already exists, report/reuse it instead of creating a duplicate.

## Boundary

This command authorizes only remote PR creation plus the read-only checks needed to support it.

It does not authorize pushing unpublished commits, creating commits, rewriting history, changing the implementation, assigning reviewers, applying labels or milestones, enabling auto-merge, merging, closing an existing PR, deleting branches, releasing, or deploying unless those operations are separately and explicitly authorized.

If the head branch is not published, required checks make the PR unsafe/misleading, the base is materially ambiguous, or preparation is `blocked`, do not create the PR.
