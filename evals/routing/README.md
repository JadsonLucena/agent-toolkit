# Capability Routing Evaluations

This catalog tests **discovery and invocation decisions**, not the quality of the final engineering artifact. It is owned by the evaluation layer, not by any Skill, Agent, Command, Rule, or provider adapter.

## What CI proves

From repository root:

```sh
python3 scripts/routing_evals.py --catalog evals/routing/cases.json
python3 -m unittest tests.test_routing_evals -v
```

CI validates unique scenario identities, real canonical capability names, meaningful prompts, explicit Command dispatch scenarios, required/forbidden/permitted-companion expectations, and evaluator behavior. The output **STRUCTURAL_PASS; NOT_MEASURED** is intentional: no model was invoked, no host event occurred, and no successful route was inferred.

## Host runtime study

1. Install the exact toolkit revision in a **disposable consumer workspace**, using the host's supported discovery path. Confirm installed SHA and host version, not just the source checkout.
2. Start a fresh session per scenario, with only the intended capabilities available. Supply the literal prompt (and explicit Slash/Agent invocation where indicated). For any scenario permitting edits, use only a throwaway fixture; never run destructive or remote operations against a real project.
3. Record actual discovery, dispatch, Rule injection, and/or isolated subagent activation from observable **host/tool events**. Reading a Markdown file manually or an LLM saying "I used the skill" is not activation evidence.
4. Export observations using the contract below. Mark a host that genuinely lacks a compatible primitive as **unsupported**; do not invent an equivalent. Mark missing evidence as **not-run**.
5. Score only the component type that can be verified, and retain logs. Negative cases are as important as positive ones.

The four hosts require **separately verified installation and telemetry**; one Cursor plugin manifest does not install the same capabilities on Codex, Gemini CLI, or Claude Code.

| Host | Integration to verify before running cases |
| --- | --- |
| Cursor | Plugin catalog, Slash Commands, delegated subagent identity, and requestable Rule body activation |
| Codex | Skill discovery via SKILL.md; independently configured subagents and instruction surfaces (not Cursor Markdown aliases) |
| Gemini CLI | SKILL.md discovery and activate_skill; separately configured agents, TOML commands, and applicable instructions |
| Claude Code | Skills/Slash invocation and subagent delegation; CLAUDE.md instructions do not equal Cursor Rule selection |

No host was executed automatically by this repository's CI. Differences in runtimes are **measurement limitations**, not a reason to fabricate equivalence.

## Capture template and scoring

```sh
python3 scripts/routing_evals.py --kind skill \
  --template-host cursor --plugin-revision ACTUAL_INSTALLED_SHA \
  --host-version ACTUAL_CURSOR_VERSION \
  > /tmp/cursor-skills-observations.json

# Fill each scenario from fresh host event evidence before scoring:
python3 scripts/routing_evals.py --kind skill \
  --observations /tmp/cursor-skills-observations.json
```

A collected file has this shape:

```json
{
  "schema_version": 1,
  "host": "cursor",
  "host_version": "3.29.15",
  "plugin_revision": "ACTUAL_INSTALLED_SHA",
  "results": [
    {
      "id": "skill-validation-positive",
      "status": "observed",
      "events": [
        {
          "kind": "skill",
          "name": "requirements-validation",
          "action": "activated",
          "origin": "host",
          "evidence_ref": "host-run-id/tool-event-id"
        }
      ]
    }
  ]
}
```

Each case lists `expected` (required activations), `forbidden` (explicitly disallowed activations), and optionally `allowed_companions` (contextually legitimate but **not required** supporting activations of the same kind). The three sets must be disjoint; companions must be named per scenario, not globally whitelisted. For example, the high-risk Review case requires `high-risk-patterns` and permits `code-review` for finding classification. This does **not** permit `high-risk-patterns` in the low-risk Review negative case. A companion alone cannot satisfy a missing required activation.

Record *all* observed activations of the evaluated kind, including unexpected ones and permitted companions. A true negative uses status **observed** and an empty events array; this requires an actual session trace, not absence of a test. Results marked **not-run** or **unsupported** are never counted as passing runtime cases. The scorer validates event attribution and references structurally; it **cannot authenticate** a claimed host trace or prove isolation by itself. Retain raw host logs and independently verify provenance before making deployment or quality-gate claims.

Metrics: **precision** = required activations observed / (required activations observed + unexpected activations); **recall** = required activations observed / all required activations; **false positives** = observed activations neither required nor permitted; **false negatives** = missed required activations; **permitted_companion_activations** counts optional, legitimate supporting activations without inflating true positives or penalizing precision; **forbidden activations** = explicit disallowed matches; **coverage** = measured scenarios / total scenarios. Undefined precision/recall are reported as null, not 100%.

## Semantic boundaries tested

- **Requirements:** elicitation versus definition versus read-only validation; backlog planning versus requirement creation.
- **Debugging:** evidence-first standalone diagnosis versus Requirements ambiguity, Implementation fixes, Review candidate verification and test-only work; no implied runtime tool permission.
- **Implementation and Testing:** production-slice editing versus test-only work; TDD only when selected.
- **Review:** an explicitly scoped review versus routine implementation checks; reviewer-team delegation only when risk justifies it; candidate verification after findings exist.
- **Git:** atomic commit, PR planning, remote PR creation and SemVer are distinct and independently authorized; Gitflow is conditional.
- **Rules:** applicability, nonactivation outside a context, and high-risk heuristics versus automatic blockers.

Keep scenario prompts versioned and provider-neutral. A metadata change may improve structural clarity but is not a measured improvement until a comparable host run proves it.

Official references: https://cursor.com/docs/reference/plugins ; https://developers.openai.com/blog/eval-skills ; https://geminicli.com/docs/cli/skills-best-practices/ ; https://code.claude.com/docs/en/skills .
