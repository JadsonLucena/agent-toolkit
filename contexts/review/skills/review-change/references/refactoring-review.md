# Structural Refactoring Review — Conditional Investigation Lens

For a material refactoring diff, apply the owning Code Review Rule's Structural Refactoring Assessment and normal verification procedure. This is a read-only heuristic, not a second verdict, new specialist, or independent gate.

## Verify behavioral preservation

- Confirm intended refactor scope, frozen source revision, applicable requirements, old and new consumers and relevant baseline tests.
- Check output, exception semantics, state transitions, persistence, transaction boundaries, API/schema/event contracts, retries, concurrency and externally visible side effects when reachable.
- Inspect meaningful differences and test gaps, not just green checks. Characterization evidence describes observed behavior, not automatically desired business policy.
- For branch-by-abstraction, parallel change or strangler migration, inspect mixed-version consumers, state ownership, duplicate effects, cutover and recovery.

## Evaluate structural improvement

- Is the motivating maintainability or architectural problem supported by actual code and change history where available?
- Does the new boundary reduce change propagation, opaque dependencies, information leakage or cognitive load, or merely relocate complexity?
- Does it introduce pass-through wrappers, speculative interfaces, unnecessary patterns or new coupling that outweigh benefits?
- Is a smaller local refactoring or no-op a credible alternative? Do not prescribe a redesign simply because SOLID, Clean Code, GRASP, GoF or Object Calisthenics could be applied.

## Findings

Use existing `introduced`, `pre-existing` and `amplified-pre-existing` origin classifications and ordinary severity/likelihood/confidence criteria. A pre-existing smell without material new exposure is not a blocking regression. For material contract deviations, cite concrete reachable behavior; for preferences or unevidenced future risks, report a non-blocking recommendation or uncertainty. The Lead owns verification and the single review verdict.

Foundations: Fowler, Feathers, Meyer, Ousterhout, Parnas, Kerievsky and architectural evolution patterns.