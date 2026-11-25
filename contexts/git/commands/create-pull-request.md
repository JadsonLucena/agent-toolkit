---
name: create-pull-request
description: "Create a remote pull request after verified checks and review; when authorized, publish only its missing source branch. Never infer merge or force-push permission."
---

# Create Pull Request

## Intent

Create a remote pull request using a verified head/base, truthful description, repository template/conventions and explicit readiness state. Publish the intended source branch first only when needed and permitted by the Git-owned remote authorization invariant.

## Invocation

**Before any remote action:** An explicit PR-creation request may include **only the necessary initial non-force publication of its unpublished source branch** to the verified hosting remote. Confirm the user did not prohibit push, branch and remote are unambiguous, the destination ref is absent, and Git/host policy permits it. Stop on missing permission or any existing divergent remote ref. Do not infer force-push, merge, release or deployment authority. Apply the Git-owned remote authorization invariant before acting.

Use only when remote pull-request creation is explicitly requested. **Before creating either a ready PR or a Draft**, require passing applicable project tests/lint and a complete Code Review `PASS` for the exact final head/base. If review evidence is absent or stale, this request authorizes initiating the separate read-only `/review/review-code` capability with `review_profile=advisory` without a second authorization. A recorded `FAIL` or unresolved material `INCOMPLETE` routes findings to the responsible owner and blocks creation until corrected and re-reviewed. Git consumes `contracts/review-evidence.md` without performing Review internals. Missing or failed evidence blocks remote creation, not merely ready status.

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

* Intended source branch (local unpublished or already published) and verified hosting remote.
* Intended base branch.
* Prepared title/description when available, otherwise sufficient evidence to prepare them.
* Optional PR Boundary and traceability references.
* Existing Code Review `PASS` evidence for the intended revision with complete scope, if valid; otherwise obtain it under Invocation. Actual test/lint and established coverage results (or documented genuine non-applicability) must identify execution source and revision/scope; missing checks must be executed when authorized during preflight.
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

This command authorizes remote PR creation, the necessary read-only checks, and conditional initial publication of the exact source branch under Git's remote authorization invariant.

It does not authorize creating commits, updating existing remote refs, force-pushing, rewriting history, changing the implementation, changing the remote or source repository, assigning reviewers, applying labels or milestones, enabling auto-merge, merging, closing an existing PR, deleting branches, releasing or deploying unless separately authorized. A push explicitly prohibited by the user is never inferred from a PR request.

Do not create **any** pull request, including Draft, when `contexts/git/rules/pull-request.md` does not allow that publication. Do not claim gate in the description unless that rule says the gate is satisfied.
