# Architecture and decision matrix

## Boundary

Codex root remains the orchestrator, holds approvals and repo permissions,
coordinates native subagents, and integrates all changes. Root should be
`gpt-6.1-sol` / `xhigh` through `.codex/config.toml`, or explicit launch
options. An already-running root cannot be hot-swapped by a skill.

## Dispatch

| Input | Native role | Work product | Writes? |
|---|---|---|---|
| Trivial/normal analysis | Root Sol | Decision / implementation | Code only when asked |
| High-impact architecture | `critical_planner` Astra | Bounded architecture plan + risks | No |
| Genuine visual/UX decisions | `visual_designer` Terra | UX/design handoff | No |
| All code implementation | Root Sol or `code_executor` Sol | Working code + tests | Assigned paths |
| Substantive docs | `technical_writer` Luna | Validated documentation | Assigned docs only |

When work is simultaneously visual and code-related, design precedes coding.
When code and docs depend on unresolved interfaces, documentation follows code.
Do not call four agents merely to get four different answers.

## Examples of critical Astra triggers

Changes to security boundaries, public API compatibility strategy, schema/data
migration design, domain boundaries, or architecture with material tradeoffs.
A one-file bug fix, lint task, or minor CSS adjustment is **not** critical.

## Verification and safeguards

- Native agent configuration is declarative, not evidence of live availability.
- A different model explicitly chosen by the user can override project root
  configuration; report the discrepancy rather than pretending Sol is root.
- No API keys, external bridges, or third-party model providers are required.
- Validate using `python scripts/validate.py`; run tests with
  `python -m unittest discover -s tests -v`.
