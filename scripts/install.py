#!/usr/bin/env python3
"""Install a minimal, first-party-only Codex routing skill and native agents."""
from __future__ import annotations

import argparse
import shutil
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path

PACKAGE = Path(__file__).resolve().parents[1]
AGENT_NAMES = (
    "critical_planner",
    "visual_designer",
    "code_executor",
    "technical_writer",
)
START = "<!-- sol-router:begin -->"
END = "<!-- sol-router:end -->"


@dataclass(frozen=True)
class Operation:
    source: Path
    target: Path
    action: str  # copy, same, conflict, config-preserved


def get_destination(scope: str, target: Path | None = None, home: Path | None = None) -> tuple[Path, Path, Path]:
    """Return skill directory, native agent directory, and config root."""
    if scope == "project":
        root = (target or Path.cwd()).expanduser().resolve()
        return root / ".agents" / "skills", root / ".codex" / "agents", root
    if scope == "user":
        root = (home or Path.home()).expanduser().resolve()
        return root / ".agents" / "skills", root / ".codex" / "agents", root / ".codex"
    raise ValueError(f"Unknown scope: {scope}")


def all_operations(skill_dir: Path, agent_dir: Path, root: Path) -> list[Operation]:
    pairs = [(PACKAGE / ".agents" / "skills" / "sol-router" / "SKILL.md",
              skill_dir / "sol-router" / "SKILL.md")]
    pairs += [
        (PACKAGE / ".codex" / "agents" / f"{name}.toml", agent_dir / f"{name}.toml")
        for name in AGENT_NAMES
    ]
    cfg_target = root / ".codex" / "config.toml" if root.name != ".codex" else root / "config.toml"
    pairs.append((PACKAGE / ".codex" / "config.toml", cfg_target))
    operations: list[Operation] = []
    for source, destination in pairs:
        if destination.is_symlink():
            action = "unsafe-link"
        elif destination.exists():
            if not destination.is_file():
                action = "conflict"
            elif destination.read_bytes() == source.read_bytes():
                action = "same"
            elif source.name == "config.toml":
                action = "config-preserved"
            else:
                action = "conflict"
        else:
            action = "copy"
        operations.append(Operation(source, destination, action))
    return operations


def policy_text() -> str:
    return START + "\n" + (PACKAGE / "AGENTS.md").read_text(encoding="utf-8").rstrip() + "\n" + END


def insert_policy(existing: str) -> str:
    """Append or refresh only our delimited AGENTS policy; preserve all other text."""
    block = policy_text()
    if START in existing or END in existing:
        if existing.count(START) != 1 or existing.count(END) != 1:
            raise ValueError("Malformed existing sol-router policy markers")
        left = existing.index(START)
        end_index = existing.index(END)
        right = end_index + len(END)
        if end_index <= left:
            raise ValueError("Malformed policy marker order")
        return existing[:left] + block + existing[right:]
    if not existing:
        return block + "\n"
    return existing.rstrip() + "\n\n" + block + "\n"


def backup(path: Path) -> Path:
    """Choose a never-overwritten simple numbered backup path."""
    number = 1
    while True:
        candidate = path.with_name(f"{path.name}.bak{number}")
        if not candidate.exists():
            shutil.copy2(path, candidate)
            return candidate
        number += 1


def install(scope: str, target: Path | None = None, *, dry_run: bool = False,
            force: bool = False, home: Path | None = None) -> list[str]:
    skill_dir, agent_dir, root = get_destination(scope, target, home)
    operations = all_operations(skill_dir, agent_dir, root)
    agents_path = root / "AGENTS.md"
    destinations = [op.target for op in operations] + [agents_path]
    for path in destinations:
        # Never follow symlinked directories or files, including broken symlinks.
        for parent in (path, *path.parents):
            if parent.is_symlink():
                raise ValueError(f"Refusing symlink in installation path: {parent}")
    if agents_path.exists() and not agents_path.is_file():
        raise ValueError(f"Refusing nonregular AGENTS.md: {agents_path}")
    old_policy = agents_path.read_text(encoding="utf-8") if agents_path.exists() else ""
    new_policy = insert_policy(old_policy)
    collisions = [op.target for op in operations if op.action in ("conflict", "unsafe-link")]
    if collisions and not force:
        raise FileExistsError("Existing managed files differ; use --force to back them up and replace:\n" +
                              "\n".join(str(p) for p in collisions))

    logs: list[str] = []
    for op in operations:
        if op.action == "same":
            logs.append(f"KEEP  {op.target} (already installed)")
        elif op.action == "config-preserved":
            logs.append(f"KEEP  {op.target} (existing config preserved; verify root model and agents.enabled)")
            if not dry_run:
                try:
                    with op.target.open("rb") as f:
                        existing_cfg = tomllib.load(f)
                    if existing_cfg.get("model") != "gpt-6.1-sol" or existing_cfg.get("model_reasoning_effort") != "xhigh":
                        logs.append("WARN  Existing root model/effort differs from Sol xhigh; no automatic overwrite")
                    if existing_cfg.get("agents", {}).get("enabled") is False:
                        logs.append("WARN  Existing [agents].enabled=false prevents delegation")
                except (OSError, tomllib.TOMLDecodeError) as exc:
                    logs.append(f"WARN  Could not parse existing Codex config: {exc}")
        else:
            logs.append(f"{'REPLACE' if op.action == 'conflict' else 'COPY'} {op.target}")
            if not dry_run:
                op.target.parent.mkdir(parents=True, exist_ok=True)
                if op.target.exists():
                    logs.append(f"BACKUP {backup(op.target)}")
                shutil.copy2(op.source, op.target)

    if old_policy != new_policy:
        logs.append(f"UPDATE {agents_path} (managed AGENTS.md block only)")
        if not dry_run:
            agents_path.parent.mkdir(parents=True, exist_ok=True)
            if agents_path.exists():
                logs.append(f"BACKUP {backup(agents_path)}")
            agents_path.write_text(new_policy, encoding="utf-8")
    else:
        logs.append(f"KEEP  {agents_path} (policy current)")
    return logs


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scope", choices=("project", "user"), default="project")
    parser.add_argument("--target", type=Path, help="Project root (only for project scope)")
    parser.add_argument("--dry-run", action="store_true", help="Show changes without writing files")
    parser.add_argument("--force", action="store_true", help="Back up and replace conflicting skill/agent files")
    args = parser.parse_args(argv)
    if args.scope == "user" and args.target is not None:
        parser.error("--target is only allowed with --scope project")
    try:
        for message in install(args.scope, args.target, dry_run=args.dry_run, force=args.force):
            print(message)
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    if args.dry_run:
        print("DRY RUN: no files written")
    else:
        print("Installation complete. Restart Codex and begin a new task.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
