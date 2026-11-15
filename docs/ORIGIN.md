# Attribution and scope

- Inspiration: Cjbuilds/Codex-Orchestration, https://github.com/Cjbuilds/Codex-Orchestration
- Referenced upstream README and `plugins/codex-orchestration/skills/codex-orchestration/SKILL.md` on 2026-11-12.
- Upstream license: MIT (copyright 2026 Codex-Orchestration contributors).
- This distribution is a **standalone minimal adaptation**, not a byte-for-byte
  fork or full snapshot of the upstream Git tree. The source archive could not
  be fetched in this environment. Its native-agent / skill workflow was
  reviewed and reduced to four fixed, first-party OpenAI model routes.
- No upstream bridge, provider registry, external-auth code, lifecycle hooks,
  install/update commands, plugin marketplace integration, or original tests
  are embedded. The files under `scripts/`, `.codex/`, `.agents/`, and `tests/`
  in this ZIP were authored as a small independent implementation.
- Verify compatibility against your installed Codex version before relying on
  native model availability. Model settings do not grant subscription access.
