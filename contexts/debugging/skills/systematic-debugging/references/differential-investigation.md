# Differential Investigation and Regression Isolation

Use this reference only when one comparable execution works and another fails, or a known-good revision differs from a failing revision. A contrast suggests hypotheses; it is not itself causal proof.

## Comparative Procedure

1. Anchor each side to its **actual** commit/build, configuration, environment, inputs, dependency versions, feature flags, time window and observed outcome. Mark absent information unknown.
2. Compare the smallest useful variables first: request data, event ordering, runtime state, deployment version or dependency behavior. Avoid reading an entire repository before establishing what can change the decision.
3. Record each difference as a candidate explanation and predict what would happen if that one factor were controlled. Confounders (different traffic, clocks, data sets, experiments or permission scopes) must remain explicit.
4. Prefer passive comparison or an authorized isolated reproduction. Use `git bisect` only when a reliable good/bad predicate and safe test harness exist; don't treat intermittent outcomes as deterministic. If the test mutates a shared resource, do not run it under a read-only invocation.
5. Report what the evidence differentiates and which candidates remain untested.

## Stop Signals

If neither execution has a trustworthy baseline, if conditions cannot be made sufficiently comparable, or if every proposed trial is unsafe, report `inconclusive` or `blocked` and the exact evidence needed. Do not edit unrelated code to manufacture a good example.
