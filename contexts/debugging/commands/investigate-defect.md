---
name: investigate-defect
description: "Investigate a specified software defect read-only, recording causal evidence and uncertainty for handoff. Use for standalone diagnosis, not patching or PR review approval."
---

# Investigate Defect

## Intent

Investigate an observed or reported technical failure, yielding a source-grounded diagnosis without applying a correction.

## Invocation

Select the Debugging Investigator and systematic-debugging procedure for the supplied symptom and bounded evidence. The invocation authorizes read-only inspection of available, permitted material; it does not authorize state-changing reproductions, test authoring, code modification or external effects.

## Uses

* Agent: `contexts/debugging/agents/debugging-investigator.md`
* Skill: `contexts/debugging/skills/systematic-debugging/SKILL.md`
* Rule: `contexts/debugging/rules/debugging.md`
* Output contract: `contracts/debugging-evidence.md`

## Inputs

Observed or reported symptom, expected behavior and its source when known, code/environment identity, applicable logs and traces, reproduction conditions, time window, scope and tool/experiment permissions. Unknowns remain explicit.

## Output

A `contracts/debugging-evidence.md`-compatible diagnosis with actual observations and checks, status and competing explanations, revision identity and next responsible owner; never a second Review verdict.

## Boundary

Read-only by default. Does not authorize editing files, tests or requirements; Git commits or PRs; publishing review comments; telemetry installation; destructive, billable or production experiments; deployment; rollback; or granting other context permissions. Where no safe experiment exists, report the limitation.
