# Codex role routing policy

This repository uses `.agents/skills/sol-router/SKILL.md` for model routing.
Read and apply that skill for engineering work involving architecture, UI/UX,
implementation, testing, documentation, or orchestration.

- Day-to-day reasoning, all implementation code, integration and validation:
  GPT-6.1 Sol `gpt-6.1-sol`, `xhigh` (usually the Codex root).
- High-impact architecture and consequential planning **only**:
  `critical_planner` (GPT-6 Astra `gpt-6-astra`, `xhigh`).
- Genuine visual/UX decisions and visual review:
  `visual_designer` (GPT-6.1 Terra `gpt-6.1-terra`, `high`).
- Substantive documentation and technical writing:
  `technical_writer` (GPT-6 Luna `gpt-6-luna`, `xhigh`).

Sol owns implementation even for UI code; Terra supplies visual guidance.
Do not spawn Astra for trivial planning or small decisions. Use subagents only
when justified. Do not silently substitute models. Root validates results.
