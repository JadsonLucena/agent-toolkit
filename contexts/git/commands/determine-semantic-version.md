# Determine Semantic Version

## Intent

Determine the semantic-version increment supported by verified compatibility impact and repository release policy.

## Invocation

This command performs version analysis only. It does not authorize editing version files, creating commits, tagging, pushing, publishing, deploying, or releasing.

## Uses

* Agent: `contexts/git/agents/git-engineer.md`
* Skill: `contexts/git/skills/determine-semantic-version/skill.md`
* Rule: `contexts/git/rules/semantic-version.md`

## Inputs

* Current version and repository release policy.
* Relevant changes and public compatibility evidence.
* Optional requirement, work-item, issue, or release context as supporting evidence.

## Output

Current version, proposed increment, resulting version when computable, compatibility rationale, supporting evidence, and unresolved ambiguity.

## Boundary

If compatibility impact, public API boundaries, or release intent is materially ambiguous, ask the developer or release owner rather than guessing.
