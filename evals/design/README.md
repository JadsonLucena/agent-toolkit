# Optional Independent Design Critique — Evaluation Pilot

This catalog tests a **hypothesis**, not a new toolkit capability: an independent
critique of an already proposed technical design may identify material decision
risks *before* Implementation, especially when choices are hard to reverse.
The existing Design Engineer still owns design; Requirements owns accepted
behavior and authority; Review owns code-change verdicts.

## Scope and trigger

Run this pilot **only when there is a material design decision** (for example
cross-context ownership, irreversible migration, public contract or significant
quality-attribute trade-off), with a versioned design baseline and source
constraints. For local, reversible choices, the correct result is **no additional
review**. This experiment does not insert a mandatory step into the SDLC,
introduce a Design Reviewer agent, create an approval gate, or grant mutation
authority.

## How to evaluate

1. In an isolated disposable fixture, have the normal `/design/design-solution`
   capability produce or receive a pinned `contracts/design-evidence.md`-compatible
   proposal. Preserve the accepted requirements, relevant existing architecture,
   exact source identity, alternatives and stated assumptions.
2. In a **separate, observed reviewer context**, provide that frozen design and
   sources, but **not** the author's private reasoning or desired verdict.
   Ask for a read-only critique of adequacy, trade-offs, feasibility and
   disconfirming scenarios. Do not invoke a new toolkit command or pretend
   a role rename provides independence. Source authority and prior accepted
   requirements cannot be changed by the reviewer.
3. Record findings with source references, consequence, confidence, counterevidence,
   and `decision-needed` for material unresolved authority. Capture actual host
   events and output; retain the original proposal and review as separate artifacts.
4. Have a separately identified evaluator compare the original design with the
   critique and assess **material additional findings, false positives, duplication
   and effort**. Do not claim value from the existence of a document or a catalog.
5. Test negative cases in which no independent critique should be triggered.
   Stop the pilot if it adds ceremony, speculation or decisions without authority.

## Catalog validation

```sh
python3 scripts/requirements_evals.py --catalog evals/design/review-cases.json
python3 scripts/requirements_evals.py --catalog evals/design/review-cases.json --observations /path/to/design-review-observations.json
```

The first command validates JSON **structure only**; no actual Design Reviewer
or independent runtime execution occurs in CI. The second checks the supplied
evaluator-attested transcript evidence, not correctness automatically.
Follow [evaluation principles](../README.md) and the source-bound
`contracts/design-evidence.md` semantics.

## Promotion criterion

Only consider a permanent review capability if observed host runs show
repeatable **material decisions found earlier** at an acceptable false-positive,
effort and duplication cost, compared with the existing Design Engineer.
A successful pilot does not itself authorize a new command, agent or gate.
