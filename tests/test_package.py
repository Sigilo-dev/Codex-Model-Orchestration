"""Run via: python -m unittest discover -s tests -v"""
from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_script(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    # Dataclasses inspect sys.modules when resolving postponed annotations.
    import sys
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


installer = load_script("install")
validator = load_script("validate")


class PackageTests(unittest.TestCase):
    def test_static_validator(self):
        self.assertEqual(validator.validate(), [])

    def test_four_models_with_requested_effort(self):
        self.assertEqual(validator.MODELS, {
            "critical_planner": ("gpt-6-astra", "xhigh"),
            "visual_designer": ("gpt-6.1-terra", "high"),
            "code_executor": ("gpt-6.1-sol", "xhigh"),
            "technical_writer": ("gpt-6-luna", "xhigh"),
        })

    def test_project_install(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder)
            log = installer.install("project", target)
            self.assertTrue((target / ".codex/config.toml").exists())
            self.assertTrue((target / ".agents/skills/sol-router/SKILL.md").exists())
            self.assertEqual(len(list((target / ".codex/agents").glob("*.toml"))), 4)
            self.assertIn(installer.START, (target / "AGENTS.md").read_text())
            self.assertTrue(any("Installation" not in line for line in log))

    def test_user_install(self):
        with tempfile.TemporaryDirectory() as folder:
            home = Path(folder)
            installer.install("user", home=home)
            self.assertTrue((home / ".codex/AGENTS.md").exists())
            self.assertTrue((home / ".codex/config.toml").exists())
            self.assertTrue((home / ".agents/skills/sol-router/SKILL.md").exists())
            self.assertTrue((home / ".codex/agents/code_executor.toml").exists())

    def test_dry_run_writes_nothing(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder)
            installer.install("project", target, dry_run=True)
            self.assertEqual(list(target.iterdir()), [])

    def test_install_idempotent(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder)
            installer.install("project", target)
            original = (target / "AGENTS.md").read_text()
            logs = installer.install("project", target)
            self.assertEqual((target / "AGENTS.md").read_text(), original)
            self.assertTrue(any("already installed" in item for item in logs))

    def test_preserve_existing_agents_instructions(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder)
            (target / "AGENTS.md").write_text("# User instructions\nDo not touch files.\n")
            installer.install("project", target)
            content = (target / "AGENTS.md").read_text()
            self.assertTrue(content.startswith("# User instructions\nDo not touch files."))
            self.assertIn("Sol", content)
            self.assertEqual(content.count(installer.START), 1)

    def test_preserve_existing_config(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder)
            (target / ".codex").mkdir()
            existing = 'model = "gpt-6-luna"\n[agents]\nenabled = false\n'
            (target / ".codex/config.toml").write_text(existing)
            logs = installer.install("project", target)
            self.assertEqual((target / ".codex/config.toml").read_text(), existing)
            self.assertTrue(any("root model/effort differs" in line for line in logs))
            self.assertTrue(any("prevents delegation" in line for line in logs))

    def test_refuse_collisions_without_force(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder)
            changed = target / ".codex/agents/code_executor.toml"
            changed.parent.mkdir(parents=True)
            changed.write_text("user custom agent")
            with self.assertRaises(FileExistsError):
                installer.install("project", target)
            self.assertEqual(changed.read_text(), "user custom agent")
            self.assertFalse((target / "AGENTS.md").exists())

    def test_symlinked_agent_is_rejected_even_with_force(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder)
            outside = target / "elsewhere.toml"
            outside.write_text("never overwrite")
            link = target / ".codex/agents/code_executor.toml"
            link.parent.mkdir(parents=True)
            try:
                link.symlink_to(outside)
            except (OSError, NotImplementedError):
                self.skipTest("symlinks unavailable")
            with self.assertRaises(ValueError):
                installer.install("project", target, force=True)
            self.assertEqual(outside.read_text(), "never overwrite")

    def test_force_creates_backup(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder)
            changed = target / ".codex/agents/code_executor.toml"
            changed.parent.mkdir(parents=True)
            changed.write_text("user custom agent")
            installer.install("project", target, force=True)
            self.assertEqual((changed.parent / "code_executor.toml.bak1").read_text(), "user custom agent")
            self.assertIn('gpt-6.1-sol', changed.read_text())

    def test_policy_marker_preserves_surroundings(self):
        original = "BEGIN\n" + installer.START + "\nold managed text\n" + installer.END + "\nEND\n"
        updated = installer.insert_policy(original)
        self.assertTrue(updated.startswith("BEGIN\n"))
        self.assertTrue(updated.endswith("\nEND\n"))
        self.assertNotIn("old managed text", updated)

    def test_invalid_policy_markers_rejected(self):
        with self.assertRaises(ValueError):
            installer.insert_policy(installer.START + "missing ending marker")


if __name__ == "__main__":
    unittest.main()
