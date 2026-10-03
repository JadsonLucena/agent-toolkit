# Gitflow Rules

## Applicability

* Treat Gitflow as a legacy, release-oriented branching workflow, not as a universal default.
* Apply Gitflow only when the repository explicitly uses it or when a release-oriented model with equivalent branch roles is required.
* Do not impose Gitflow on repositories using trunk-based development, GitHub Flow, or another established workflow.
* Preserve repository-defined branch names, prefixes, merge policies, protections, and release practices when they differ from the conventional names below.
* Apply `contexts/git/rules/git.md` to repository state, synchronization, history rewriting, remote operations, tags, signing, worktrees, and Git safety.
* Apply `contexts/git/rules/semantic-version.md` to release, hotfix, and tag version identifiers when the project declares a versioning scheme.

## Branch Roles

* The production branch, commonly `main` or historically `master`, represents released or production-ready history.
* The integration branch, commonly `develop`, contains changes intended for the next release.
* Supporting branches such as `feature/*`, `release/*`, and `hotfix/*` are temporary and have distinct lifecycles and integration targets.
* Derive a new branch's role, base, and semantic name from the intended work and repository conventions.
* If the work intent or correct branch role cannot be determined with sufficient confidence, ask the developer before creating the branch.

## Feature Branches

* Refresh the integration branch before creating a feature branch.
* Create the feature branch from the latest relevant integration state, commonly `develop`.
* Merge completed feature work back into the integration branch, never directly into the production branch in Gitflow.
* Before integration, refresh the integration target and handle divergence according to the repository's merge or rebase policy; do not require merging or rebasing the integration branch into the feature branch unless repository policy requires it.
* Keep feature branches focused and integrate them promptly to reduce divergence and merge risk.

## Release Branches

* Refresh the integration branch and create a release branch from the intended integration state when the selected release scope is ready for stabilization.
* Cutting the release branch establishes an independent stabilization line for that release while the integration branch may continue receiving work for future releases.
* Determine the intended release version when cutting the release branch, so stabilization, version metadata, and release documentation refer to one agreed version.
* When the repository encodes the version in the release branch name, the encoded identifier must be valid under the project's declared versioning scheme.
* Treat a version encoded in a branch name as declared intent rather than evidence of the required increment; reconcile it with the release scope's actual public-API compatibility before finalizing the release and correct the version when they disagree.
* After the release branch is cut, restrict it to release preparation, documentation, version metadata, and fixes required for that release.
* When the project publishes stabilization builds from the release branch, use its declared pre-release identifiers rather than reusing the final release identifier.
* Do not merge later integration-branch changes into an active release branch merely to keep it synchronized with `develop`.
* Before finalizing the release, refresh the relevant production and integration references to detect concurrent changes, but preserve the release branch's defined scope.
* If changes made during stabilization alter the release's compatibility impact, recompute the required version before tagging instead of keeping the version chosen at cut time.
* When ready, merge the release into the production branch and tag the released production commit with the agreed release version.
* Merge the release back into the integration branch so release-specific fixes and metadata changes needed by future development are preserved.
* Remove the temporary release branch after completion when consistent with repository practice.

## Hotfix Branches

* Refresh the production branch before creating a hotfix.
* Create the hotfix from the latest applicable production branch or released production tag, never from the integration branch.
* Treat the hotfix as an independent production-correction line; do not merge `develop` into it merely to make it current.
* Keep the hotfix limited to the urgent production issue and necessary release adjustments.
* Derive the hotfix version from the released version being corrected, incremented according to the project's declared versioning scheme.
* Determine the hotfix increment from the compatibility impact of the correction, not from its urgency; a correction that changes public-API compatibility requires the increment that compatibility demands and is a release-policy decision.
* Before production integration, refresh the production target and handle any relevant production divergence according to repository policy.
* When ready, merge the hotfix into the production branch and tag the resulting production release with its own new version.
* If no release branch is active, merge the hotfix into the integration branch so the correction is preserved in future releases.
* If a release branch is active, merge the hotfix into that release branch instead of the integration branch by default; the release will later merge back into the integration branch.
* If ongoing integration work requires the hotfix before the active release is completed, the hotfix may also be integrated into the integration branch according to repository policy.
* Remove the temporary hotfix branch after completion when consistent with repository practice.

## Integration and History

* Gitflow branch roles do not themselves determine the merge strategy.
* Preserve production-branch stability.
* Keep supporting branches as short-lived as practical; the workflow should support the release process rather than become unnecessary process overhead.

## Quality Guardrails

* Do not introduce future-release feature work into an active release or hotfix branch.
* Do not guess a branch role, base, or semantic name when multiple plausible interpretations remain; ask the developer when the ambiguity can materially change the Gitflow operation.
* Do not treat Gitflow as a universal best practice; use it only when it fits the repository's release model.
