# Determine Semantic Version

## Purpose

Use to determine a semantic-version increment from verified compatibility impact and repository release policy without inventing release intent.

## Uses

* Rule: `contexts/git/rules/git.md`
* Rule: `contexts/git/rules/semantic-version.md`

Optional requirements, work items, release notes, issues, or developer context may provide evidence of intended public behavior. They do not replace inspection of actual compatibility impact.

## Working State

Maintain:

* current verified version;
* repository versioning and release policy;
* relevant public API, consumer contract, or compatibility surface;
* actual changes and documented intent;
* pre-1.0 or repository-specific semantics when applicable;
* unresolved compatibility or release-intent ambiguity.

## Workflow

1. Inspect the current version, versioning policy, public API or consumer contract, relevant changes, and release context.
2. Determine whether the change is breaking, backward-compatible additive behavior, backward-compatible correction, or not release-relevant under repository policy.
3. Distinguish implementation size, effort, or file count from compatibility impact.
4. Apply pre-1.0 or repository-specific versioning policy when applicable.
5. Reconcile code evidence, documented intent, tests, release metadata, and optional planning evidence.
6. If compatibility impact or release intent is materially ambiguous, ask the developer rather than choosing the larger or smaller increment by default.
7. Propose the increment and resulting version only when the current version and applicable policy are verified.
8. Report the compatibility rationale, supporting evidence, and remaining uncertainty.

## Stop Conditions

Stop and surface the issue when:

* the current version cannot be verified;
* applicable versioning or release policy is missing or conflicting in a way that changes the result;
* compatibility impact cannot be established from available evidence;
* release intent is required to choose a version and remains materially ambiguous;
* continuing would require inventing a public contract or compatibility assumption.

## Output

Return the current version, proposed increment, resulting version when computable, compatibility rationale, supporting evidence, and unresolved issues.

## Boundary

Determining a version does not authorize editing version files, creating commits, tagging, pushing, publishing, deploying, or releasing.
