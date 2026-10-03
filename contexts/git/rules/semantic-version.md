# Semantic Version Rules

## Applicability

* Apply Semantic Versioning only when the project declares or follows SemVer for a defined public API.
* The project must make the public API explicit through documentation, code, contracts, or another clear declaration.
* Determine version impact from the compatibility of the public API and the declared release contract, not from change size, implementation effort, number of commits, branch names, or perceived importance.
* Follow stricter project-specific release policies when they remain compatible with the declared versioning scheme.

## Version Format

* Stable versions use `MAJOR.MINOR.PATCH`, where each component is a non-negative integer without leading zeroes.
* Once a version is released, its contents must not be changed; publish any modification as a new version.
* Version `1.0.0` defines the stable public API.
* Version `0.y.z` represents initial development; the public API should not be considered stable unless the project defines a stricter contract.

## Version Increments

* Increment `PATCH` for backward-compatible bug fixes.
* Increment `MINOR` for backward-compatible public functionality or deprecation of public functionality.
* Increment `MAJOR` for backward-incompatible changes to the stable public API.
* Reset lower-order components to zero when incrementing a higher-order component.
* When a release contains changes requiring different increments, use the highest required increment.
* For `0.y.z`, follow the project's explicit release policy rather than inventing stable-API bump semantics.

## Commit and Release Semantics

* Conventional Commit metadata represents declared change intent and may be used as release-automation input; it does not override contradictory evidence about actual compatibility.
* For stable APIs, a breaking change maps to `MAJOR`, `feat` maps to `MINOR`, and `fix` maps to `PATCH`.
* Types other than `feat` and `fix` have no default Semantic Versioning effect unless the project's release policy explicitly maps them.

## Automated Version Inference

* Treat Conventional Commit based version inference as authoritative automation only when the repository explicitly adopts the commit convention as part of its release contract.
* Require automated commit-message validation when releases depend on commit semantics.
* Ensure the repository's merge or squash strategy preserves the semantic information used by release automation.
* Require compatibility review before merge when a change may affect the public API in a way that is not reliably represented by its commit type or breaking-change marker.
* Require explicit developer or release-owner review when compatibility is ambiguous, when repository history is not reliably conventional, when `0.y.z` has no explicit bump policy, or when observed public-API impact conflicts with commit metadata.
* Developer review may approve an automatically calculated version; it does not require manual version entry.

## Pre-release and Build Metadata

* A pre-release version appends `-` followed by one or more dot-separated identifiers to `MAJOR.MINOR.PATCH`.
* Pre-release identifiers must contain only ASCII alphanumeric characters and hyphens, must not be empty, and numeric identifiers must not contain leading zeroes.
* A pre-release version has lower precedence than the associated normal version and indicates that the release may not satisfy the intended compatibility guarantees of that normal version.
* Build metadata appends `+` followed by one or more dot-separated identifiers containing only ASCII alphanumeric characters and hyphens.
* Build metadata must not affect version precedence.
* Follow project conventions for semantic pre-release identifiers such as `alpha`, `beta`, or `rc`.

## Precedence

* Compare `MAJOR`, then `MINOR`, then `PATCH` numerically.
* A normal version has higher precedence than a pre-release version with the same `MAJOR.MINOR.PATCH`.
* Compare pre-release identifiers from left to right until a difference is found.
* Numeric pre-release identifiers compare numerically and have lower precedence than non-numeric identifiers.
* Non-numeric pre-release identifiers compare lexically in ASCII sort order.
* A larger set of equal preceding pre-release identifiers has higher precedence than a smaller set.
* Ignore build metadata when determining precedence.

## Quality Guardrails

* Identify the current version, public API, release policy, release intent, and relevant changes before proposing the next version.
* Do not invent a version bump when the project does not require a release.
* If the public-API impact, release intent, or required version increment cannot be determined with sufficient confidence, ask the developer or release owner rather than guessing a version.
