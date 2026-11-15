#!/usr/bin/env python3
"""Static validation of fixed Codex role routing. No network or model calls."""
from __future__ import annotations

import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODELS = {
    "critical_planner": ("gpt-6-astra", "xhigh"),
    "visual_designer": ("gpt-6.1-terra", "high"),
    "code_executor": ("gpt-6.1-sol", "xhigh"),
    "technical_writer": ("gpt-6-luna", "xhigh"),
}


def validate(base: Path = ROOT) -> list[str]:
    errors: list[str] = []
    cfg_path = base / ".codex" / "config.toml"
    try:
        cfg = tomllib.loads(cfg_path.read_text(encoding="utf-8"))
        if cfg.get("model") != "gpt-6.1-sol":
            errors.append("Root model must be gpt-6.1-sol")
        if cfg.get("model_reasoning_effort") != "xhigh":
            errors.append("Root effort must be xhigh")
        if cfg.get("agents", {}).get("enabled") is not True:
            errors.append("[agents].enabled must be true")
    except (OSError, tomllib.TOMLDecodeError) as exc:
        errors.append(f"Invalid Codex project config: {exc}")

    for agent_name, (model, effort) in MODELS.items():
        path = base / ".codex" / "agents" / f"{agent_name}.toml"
        try:
            agent = tomllib.loads(path.read_text(encoding="utf-8"))
            if agent.get("name") != agent_name:
                errors.append(f"{agent_name}: name mismatch")
            if agent.get("model") != model:
                errors.append(f"{agent_name}: expected model {model}")
            if agent.get("model_reasoning_effort") != effort:
                errors.append(f"{agent_name}: expected effort {effort}")
            if not agent.get("description") or not agent.get("developer_instructions"):
                errors.append(f"{agent_name}: missing instructions")
            if agent.get("model_provider") or agent.get("mcp_servers"):
                errors.append(f"{agent_name}: external provider forbidden")
        except (OSError, tomllib.TOMLDecodeError) as exc:
            errors.append(f"{agent_name}: invalid TOML: {exc}")
    skill_path = base / ".agents" / "skills" / "sol-router" / "SKILL.md"
    try:
        text = skill_path.read_text(encoding="utf-8")
        if not text.startswith("---\nname: sol-router\n"):
            errors.append("Skill lacks expected YAML front matter")
        for name, (model, effort) in MODELS.items():
            if name not in text or model not in text or f"`{effort}`" not in text:
                errors.append(f"Skill does not document role/model/effort {name}")
    except OSError as exc:
        errors.append(f"Skill missing: {exc}")
    return errors


def main() -> int:
    errors = validate()
    if errors:
        print("INVALID CONFIGURATION:")
        for error in errors:
            print(" -", error)
        return 1
    print("PASS: four native roles, model IDs, efforts, skill and project configuration")
    print("NOTE: static validation only; runtime model access must be checked in Codex")
    return 0


if __name__ == "__main__":
    sys.exit(main())
