---
name: sol-router
description: Route Codex software tasks between GPT-6.1 Sol xhigh (routine reasoning and all code), GPT-6.1 Terra high (visual design), GPT-6 Luna xhigh (writing), and GPT-6 Astra xhigh (only critical high-impact reasoning). Use for planning, architecture, UI/UX, implementation, documentation, or multi-step app development; avoid unnecessary delegation.
---

# Sol Router — focused Codex model orchestration

## Fixed model mapping

| Responsibility | Native Codex role | Exact model | Effort |
|---|---|---|---|
| Root, everyday thinking, coding, tests, integration | Current root / `code_executor` | `gpt-6.1-sol` | `xhigh` |
| Critical planning or high-impact decisions only | `critical_planner` | `gpt-6-astra` | `xhigh` |
| Visual design, UI/UX, responsive visual review | `visual_designer` | `gpt-6.1-terra` | `high` |
| Technical writing and documentation | `technical_writer` | `gpt-6-luna` | `xhigh` |

These are strict routes. Never silently substitute an unavailable model or effort.
If the current root is not Sol xhigh, say so; a skill **cannot** change the root
model in an already running session. To enforce Sol as root, use project `.codex/config.toml`
or launch `codex -m gpt-6.1-sol -c model_reasoning_effort=xhigh`.

## Primary rule: Sol thinks normally; Astra thinks only when consequential

Sol xhigh owns routine planning, small decisions, bug diagnosis, library selection,
implementation, refactoring, testing, and integration. Do **not** delegate simply
because a request uses words like "plan", "think", or "analyze".

Escalate to Astra xhigh if at least one *substantive* trigger exists:
- New or materially changed system architecture, bounded context, persistent domain model,
  public API contract, authentication/authorization boundary, or multi-service protocol.
- A complex migration, backward-compatibility strategy, data-loss/security risk, or an
  expensive-to-reverse technical decision.
- Multiple competing architectural options with important operations, maintainability,
  scaling, or safety tradeoffs that cannot be resolved by an ordinary local change.
- A user explicitly requests a critical/high-stakes architectural review.

Do **not** escalate for routine single-module features, minor UI tweaks, isolated bugs,
text changes, existing-pattern implementations, or ordinary tests. Large line count
alone is not a reason to use Astra. A critical plan must be bounded, with useful
acceptance criteria, and its recommendations must be checked by the root.

## Route visual work without confusing design and code

All appearance, layout, component behavior, interaction design, accessibility,
responsive breakpoints, style/token decisions, and screenshot review go first to
`visual_designer` when they require genuine visual judgment. Existing Figma designs
and supplied tokens take precedence over invention.

**Terra creates or reviews visual specifications; Sol implements visual code.**
Do not assign application code, HTML/CSS/JS, React/Vue/Astro components, or their tests
to Terra merely because the resulting code is visual. Sol follows Terra's handoff.
For a tiny visual adjustment with already unambiguous tokens or exact values, Sol
may implement directly, but don't invent a new design decision on Terra's behalf.

## Route writing

Use `technical_writer` for README/API docs/ADRs/technical descriptions/user guides/
release notes when the task is substantive. It may write only explicitly delegated
documentation files. Sol supplies verified code or API facts and validates the result.
Short inline comments and error messages that accompany code are Sol's work.

## Execution algorithm

1. **Triage locally (Sol xhigh).** Read task, project instructions, existing code and
   tests. Determine whether a genuine Astra trigger exists; whether visual judgment
   or substantive writing is required; and whether a subagent adds real value.
2. **Critical reasoning only if triggered.** Invoke `critical_planner` with a bounded
   packet: requirements, constraints, current architecture, disputed decisions,
   and a specific question. The root reviews and adopts or rejects its recommendations.
3. **Visual handoff only when applicable.** Invoke `visual_designer` with screenshots,
   paths, tokens, breakpoints, and expected interaction. Obtain implementable criteria.
4. **Code in Sol xhigh.** The root implements directly for small/medium sequential work.
   Invoke `code_executor` only for bounded, independently owned implementation work
   or when multi-agent separation measurably helps. Avoid two writers on same files.
5. **Documentation when needed.** Invoke `technical_writer` after interfaces have
   stabilized. Give it verified behavior and a strict list of docs paths.
6. **Integrate and verify (root Sol).** Run relevant tests/lint/build, review visual
   output where relevant, compare with acceptance criteria, report results and gaps.
   Escalate new critical decisions to Astra, but not ordinary failures.

Sequential dependencies stay sequential; parallelize only independent work. No agent
may spawn descendants by default. Root owns scheduling, file permissions, final
integration, and all user-visible claims. Astra advises the root; it is not the root.

## Delegation packet contract

Every spawn request includes: (a) goal and expected deliverable, (b) necessary
file paths/constraints, (c) permitted write paths or explicit read-only status,
(d) prior approved decisions where relevant, and (e) verifiable success criteria.

Require each agent to return its role, model/effort *as configured* (not proof of
runtime execution), result, changed paths, and unverified assumptions. Do not claim
that a model ran just because the role was mentioned in text: actual native spawn
and configured agent settings are required. If the host cannot spawn the role,
report the blocker. Never change another model's slot to hide unavailability.

## Examples

- "Fix a failing unit test" → root Sol xhigh. No other agents.
- "Change the color using existing tokens" → root Sol xhigh. Terra not necessary.
- "Redesign the responsive dashboard" → Terra high spec, then Sol xhigh code.
- "Choose microservices vs modular monolith for a major migration" → Astra xhigh
  architecture decision, Sol xhigh implementation, Luna xhigh ADR if requested.
- "Write an accurate API guide from final source" → Luna xhigh; Sol verifies.
- "Create a new auth architecture + UI + docs" → Astra → Terra → Sol → Luna,
  with root Sol checking each handoff and tests before release.

## Constraints

- Use exact installed agent names: `critical_planner`, `visual_designer`,
  `code_executor`, `technical_writer`.
- Honor a user's explicit "no subagents" preference; Sol root works alone and
  discloses when a requested specialized model cannot run under that restriction.
- Do not modify authentication, `model_provider`, API keys, or Codex sign-in.
- Do not require Claude, OpenRouter, external MCP servers, custom adapters, or an API key.
- Never claim a skill changes the active root model or guarantees future activation.
