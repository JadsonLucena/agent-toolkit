# Refactoring and Legacy Displacement — Conditional Design Reference

Use for material decisions on structural improvement; not a mandatory stage or a design-pattern checklist. The canonical `contexts/design/rules/design.md` owns design constraints and `design-solution` owns the decision workflow.

## Problem and evidence

- Name the observed maintenance or operational problem, code and consumers affected, and evidence of change amplification, cognitive load, hidden dependencies, leakage of volatile decisions or testing difficulty.
- Separate accidental implementation complexity from genuine domain constraints. A code smell is a lead to investigate, not proof of architectural failure.
- Establish existing observable contract obligations and differences between accepted requirements, observed behavior, known defects and newly desired behavior. Requirements owns unsupported business semantics.
- Consider no refactoring when the current structure is stable and expected benefit cannot justify cost and risk.

## Candidate strategies

| Boundary | Candidate | Safety focus |
| --- | --- | --- |
| Local function/class/module | Fowler's small transformations (Extract/Move/Encapsulate) | Characterization, tests, local contracts |
| In-process implementation substitution | Branch by Abstraction | Consumer compatibility and separate verified intentions |
| Public API or persistent schema | Parallel Change (expand, migrate, contract) | Mixed-version compatibility, data migration and retirement criteria |
| Legacy business capability | Strangler Fig / incremental displacement | Seam or routing boundary, coexistence, state ownership and recovery |
| Parallel implementation comparison | Differential or shadow testing | Observational equivalence and suppression of irreversible effects |

Do not call all replacements "refactoring": modernization may include authorized behavior changes, migrations and operational transitions. A Strangler Fig is an architectural migration pattern, not a default remedy for a long method.

## Tradeoffs

Consider at least two credible options ("leave as is" may be one) when the decision is materially risky. Evaluate the expected reduction in propagation cost and information leakage against extra interfaces, pass-through layers, operational complexity, testing burden, rollout risks and reversibility. Prefer a deep interface that hides volatile details to speculative pattern compliance. Do not demand this analysis for a simple safe rename.

## Handoff to Implementation

When relevant, record: chosen/alternative strategies and rationale; affected behavior and versioned consumers; preconditions/postconditions, invariants, side effects; characterization/contract test targets; migration steps and intermediate safe states; rollback, forward-fix and reconciliation obligations; assumptions and decisions requiring approval. Use the existing design-evidence contract and source references.

Foundations: Parnas (1972), Fowler (*Refactoring*), Feathers (*Working Effectively with Legacy Code*), Ousterhout (*A Philosophy of Software Design*), Kerievsky (*Refactoring to Patterns*), and Fowler's legacy displacement patterns.