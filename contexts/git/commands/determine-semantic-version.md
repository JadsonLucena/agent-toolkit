# Determine Semantic Version

## Intent

Determine the semantic version increment supported by verified compatibility impact and repository release policy.

## Invocation

This command performs version analysis only. It does not authorize editing version files, tagging, publishing, or releasing.

## Uses

* Agent: `contexts/git/agents/git-engineer.md`
* Skill: `contexts/git/skills/determine-semantic-version.md`

## Inputs

* Current version and release policy.
* Relevant changes and public compatibility evidence.
* Optional requirements, backlog, issue, or release context as supporting evidence.

## Output

Current version, proposed increment, resulting version, rationale, evidence, and unresolved ambiguity.

## Boundary

If compatibility impact or release intent is materially ambiguous, ask the developer rather than guessing.
