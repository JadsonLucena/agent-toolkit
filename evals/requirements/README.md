# Requirements behavioral evaluation baseline

This is a **provider-neutral evaluation corpus and reviewer-evidence checker**, not
a model runner or an automated judge of requirement semantics. The evaluator
validates provenance and the completeness of recorded human/independent review
findings. It does not infer whether an agent was correct from keywords.

## Scope

The cases in [cases.json](cases.json) sample the existing commands:

- Elicitation: solution-first framing, dependent decisions, known evidence,
  unauthorized Change Boundary expansion, and contextual investigation selection
  (causal uncertainty, assumption scrutiny, option comparison, prospective risks,
  hypothesis-driven learning, overlap, and avoiding needless technique ceremony),
  plus outcome-to-actor impacts, event/policy reconstruction, evidence-backed
  opportunities, stakeholder worldviews, goal-linked measurement, safety-critical
  hazard questions, and non-mandatory investigation routing.
- Definition: unsupported non-functional thresholds and ambiguous temporal
  boundaries.
- Example Discovery: stable scenario identity, negative cases, and concurrency.
- Validation: contradictory authority and read-only behavior.
- Backlog: critical financial guarantees during slicing.
- Composite `shape-change`: two complementary cases: `SC-01A` supplies the
  full authorized refund-count policy for validated planning; `SC-01B`
  deliberately leaves business semantics unresolved and checks that the
  agent asks for clarification instead of manufacturing requirements.
  Neither case authorizes implementation, code tasks, or test generation.

Cases are a deliberately small initial baseline, not comprehensive coverage.
Each case defines an invocation and observable review criteria, including
negative criteria that cannot be proven by a single keyword match.

## Run the evaluation

1. Run the given `command` in an agent host with the case's `input`. Supply
   only the stated sources/context. Record the **complete actual conversation
   or output**, including questions and tool observations, as a UTF-8 text
   transcript. Do not fabricate an agent response or silently fill the gaps.
   Treat each case's input as the complete supplied business evidence; do not
   infer unstated policy from neighboring cases, external project memory, or
   subsequent evaluations.
2. Independently review that complete transcript against each case's checks.
   Mark every check `pass`, `fail`, or `uncertain`, with a rationale.
   Positive (`presence`) passes also require a verbatim `quote` from the
   transcript. Negative (`absence`) passes require a reviewer to inspect the
   full trace; the script cannot prove absence by itself.
   For every pass/fail, `rationale` must be a nonempty text string;
   `null`, booleans, arrays, objects and whitespace-only values are invalid.
3. Write an observations file beside the transcripts. Do not commit real
   stakeholder/customer transcripts or confidential requirements to Git.
   An example envelope for one case is below; the **quote and assessment are
   illustrative only**, not an actual run or a baseline measurement.

```json
{
  "version": 1,
  "assessments": [
    {
      "case_id": "EL-01",
      "reviewer": "reviewer-identity",
      "transcript": "traces/EL-01.txt",
      "checks": [
        {
          "id": "c1",
          "verdict": "pass",
          "quote": "What business problem should the dashboard solve?",
          "rationale": "The agent challenged the solution-first framing."
        },
        {
          "id": "c2",
          "verdict": "pass",
          "rationale": "Reviewed the entire transcript; no unapproved solution was promoted to a requirement."
        }
      ]
    }
  ]
}
```

Run:

```sh
python3 scripts/requirements_evals.py
python3 scripts/requirements_evals.py --observations /path/to/observations.json
```

The first command only validates the **catalog** and prints a notice that no
agent behavior was evaluated. The second validates the reviewer observations
and transcript evidence. Exit status is `0` for all cases reviewed and
recorded as `PASSED`, `1` for any `FAILED`, and `2` for an
`INCOMPLETE` or invalid result. A missing case or check never silently
passes. A recorded `PASSED` is **reviewer-attested**, not an independently
machine-proven result.

## CI and decision boundaries

CI checks the corpus's structure and the evaluation tool's regression tests.
It does **not** invoke an AI provider or assert agent quality. A future host
adapter may collect transcripts and supply this evidence envelope without
making its representation canonical.

Continue treating `contracts/requirements.md`, `contracts/test-basis.md`,
and the owning Requirements rules as the semantic sources of truth. These
evaluation envelopes are test fixtures and verification records, not a new
Requirements contract or a mandatory output format for agents.

**Granular tasks:** `/requirements/shape-change` already orchestrates
elicitation through backlog planning. It may produce vertical slices and
planning tasks supported by validated source semantics. Detailed
architecture-specific engineering tasks belong to later Design/Implementation
work and should not be invented by Requirements. An eventual cross-context
SDD delivery command can orchestrate those later stages without duplicating
`shape-change`.
