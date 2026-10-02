# Architecture

## Canonical Organization

The toolkit is context-first: each engineering context owns its rules, skills, commands, and agents. Cross-context contracts live separately and contain data shapes only.

```text
agent-toolkit/
├── contexts/
│   ├── requirements/
│   │   ├── rules/
│   │   ├── skills/
│   │   ├── commands/
│   │   └── agents/
│   ├── testing/
│   │   ├── rules/
│   │   ├── skills/
│   │   ├── commands/
│   │   └── agents/
│   └── git/
│       ├── rules/
│       ├── skills/
│       ├── commands/
│       └── agents/
├── contracts/
├── ARCHITECTURE.md
├── MIGRATION.md
└── README.md
```

## Artifact Responsibilities

| Artifact | Owns | Must not own |
|---|---|---|
| Rule | Durable principles, constraints, invariants, quality and safety semantics | Step-by-step workflow |
| Skill | Reusable procedure, decision loop, state machine, verification and stop conditions | Persistent policy duplicated from rules |
| Command | Explicit engineering-intent entry point, authorization boundary, selected agent/skill, expected output | Full workflow or policy |
| Agent | Specialist role, scope, evidence discipline, routing, boundaries, handoffs | Detailed reusable procedures already owned by skills |
| Contract | Neutral handoff/data shape between contexts or workflow stages | Behavior, policy, orchestration, or vendor metadata |

## Dependency Direction

1. Commands select agents and skills.
2. Agents apply rules and route to skills.
3. Skills apply rules and may consume contracts.
4. Rules do not depend on commands, agents, or skills.
5. Contracts do not depend on behavioral artifacts.
6. Contexts may consume another context's contract, but should not require another context's agent or skill unless the workflow explicitly composes them.
7. Testing and Git remain independently usable when Requirements artifacts are absent.
8. Vendor adapters may depend on canonical artifacts; canonical artifacts never depend on a vendor adapter.

## Responsibility Matrix

| Context | Rules | Skills | Commands | Agents |
|---|---|---|---|---|
| Requirements | requirement semantics and quality; backlog quality | elicit; specify; validate; build/refine backlog | elicit; specify; validate; build backlog; refine backlog | requirements analyst; requirements specifier; backlog planner |
| Testing | testing quality and safety | generate tests | generate tests | test engineer |
| Git | Git safety; Gitflow when applicable; commit semantics; semantic versioning | commit changes; determine version; manage branch work | commit changes; determine semantic version | git engineer |

## Cross-Context Principle

Evidence precedes inference. Context from requirements, backlog, issues, code, tests, or Git history can support a decision, but no context source may be silently promoted into intent it does not establish. Material semantic ambiguity routes to stakeholder or developer clarification.
