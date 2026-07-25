from __future__ import annotations

import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from agentic_sdlc.cli import main


class CliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def run_cli(self, *args: str) -> tuple[int, str, str]:
        stdout, stderr = StringIO(), StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            code = main(list(args))
        return code, stdout.getvalue(), stderr.getvalue()

    def init_project(self) -> Path:
        code, output, _ = self.run_cli(
            "init", "--project-root", str(self.root), "--name", "Example"
        )
        self.assertEqual(code, 0, output)
        return self.root / ".sdlc"

    def test_init_creates_portable_artifact_set(self) -> None:
        artifact_root = self.init_project()
        self.assertTrue((artifact_root / "project.json").is_file())
        self.assertTrue((artifact_root / "RECORD.md").is_file())
        self.assertTrue((artifact_root / "REQUIREMENTS.md").is_file())
        self.assertTrue((artifact_root / "ARCHITECTURE.md").is_file())
        self.assertTrue((artifact_root / "INVARIANTS.md").is_file())
        self.assertTrue((artifact_root / "modules").is_dir())
        config = json.loads((artifact_root / "project.json").read_text())
        self.assertEqual(config["project"]["name"], "Example")
        self.assertEqual(config["coordination"]["mode"], "standalone")
        self.assertFalse(config["policy_hooks"]["release_approval"]["enabled"])

    def test_init_refuses_to_overwrite_without_force(self) -> None:
        self.init_project()
        code, _, error = self.run_cli(
            "init", "--project-root", str(self.root), "--name", "Other"
        )
        self.assertEqual(code, 2)
        self.assertIn("already exists", error)

    def test_validate_distinguishes_context_error_from_findings(self) -> None:
        code, _, _ = self.run_cli("validate", "--project-root", str(self.root))
        self.assertEqual(code, 2)
        self.init_project()
        code, output, _ = self.run_cli(
            "validate", "--project-root", str(self.root), "--json"
        )
        self.assertEqual(code, 1)
        report = json.loads(output)
        self.assertGreater(report["counts"]["findings"], 0)
        self.assertGreater(report["counts"]["checks"], 0)

    def test_validate_passes_complete_minimal_project(self) -> None:
        artifact_root = self.init_project()
        (artifact_root / "REQUIREMENTS.md").write_text(
            """# Requirements
## Requirements
| id | Requirement | Acceptance statement | Priority |
|---|---|---|---|
| REQ-01 | Return health state | A health call returns `ok` | Must |
## Explicit non-goals
- No remote monitoring.
""",
            encoding="utf-8",
        )
        (artifact_root / "ARCHITECTURE.md").write_text(
            """# Architecture
## Module map
| Module | Responsibility | Owns | Depends on |
|---|---|---|---|
| health | Return health state | health result | none |
""",
            encoding="utf-8",
        )
        (artifact_root / "INVARIANTS.md").write_text(
            "# Invariants\n\nNo cross-module invariants\n", encoding="utf-8"
        )
        (artifact_root / "modules" / "health.md").write_text(
            module_spec("health"), encoding="utf-8"
        )
        code, output, _ = self.run_cli(
            "validate", "--project-root", str(self.root), "--json"
        )
        self.assertEqual(code, 0, output)
        self.assertTrue(json.loads(output)["ok"])

    def test_next_selects_ready_module_and_respects_dependencies(self) -> None:
        artifact_root = self.init_project()
        (artifact_root / "modules" / "storage.md").write_text(
            module_spec("storage", status="complete"), encoding="utf-8"
        )
        (artifact_root / "modules" / "api.md").write_text(
            module_spec("api", depends_on=["storage"]), encoding="utf-8"
        )
        (artifact_root / "modules" / "ui.md").write_text(
            module_spec("ui", depends_on=["api"]), encoding="utf-8"
        )
        code, output, _ = self.run_cli(
            "next", "--project-root", str(self.root), "--json"
        )
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(output)["module"], "api")

    def test_next_reports_blocked_dependency_without_guessing(self) -> None:
        artifact_root = self.init_project()
        (artifact_root / "modules" / "ui.md").write_text(
            module_spec("ui", depends_on=["missing"]), encoding="utf-8"
        )
        code, output, _ = self.run_cli(
            "next", "--project-root", str(self.root), "--json"
        )
        self.assertEqual(code, 1)
        self.assertEqual(json.loads(output)["blocked"]["ui"], ["missing"])

    def test_record_review_updates_machine_state_without_rewriting_spec(self) -> None:
        artifact_root = self.init_project()
        spec = artifact_root / "modules" / "api.md"
        original = module_spec("api", status="review")
        spec.write_text(original, encoding="utf-8")
        code, output, _ = self.run_cli(
            "record-review",
            "--project-root", str(self.root),
            "--module", "api",
            "--verdict", "clear-with-conditions",
            "--reviewer", "independent-reviewer",
            "--condition", "Add deployment rollback evidence.",
        )
        self.assertEqual(code, 0, output)
        self.assertEqual(spec.read_text(encoding="utf-8"), original)
        state = json.loads((artifact_root / "reviews.json").read_text())
        review = state["modules"]["api"][-1]
        self.assertEqual(review["verdict"], "clear-with-conditions")
        self.assertEqual(review["conditions"], ["Add deployment rollback evidence."])

    def test_explicit_artifact_root_supports_split_layout(self) -> None:
        artifacts = self.root / "process" / "example"
        code, _, _ = self.run_cli(
            "init",
            "--project-root", str(self.root),
            "--artifact-root", str(artifacts),
            "--name", "Example",
        )
        self.assertEqual(code, 0)
        code, output, _ = self.run_cli(
            "status",
            "--project-root", str(self.root),
            "--artifact-root", str(artifacts),
            "--json",
        )
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(output)["project"], "Example")

    def test_add_module_creates_valid_spec_without_overwriting(self) -> None:
        artifact_root = self.init_project()
        code, output, _ = self.run_cli(
            "add-module",
            "--project-root", str(self.root),
            "--id", "api",
            "--responsibility", "Expose the application contract.",
            "--requirement", "REQ-01",
        )
        self.assertEqual(code, 0, output)
        spec = artifact_root / "modules" / "api.md"
        self.assertTrue(spec.is_file())
        self.assertIn("id: api", spec.read_text())
        code, _, error = self.run_cli(
            "add-module",
            "--project-root", str(self.root),
            "--id", "api",
            "--responsibility", "Overwrite it.",
        )
        self.assertEqual(code, 2)
        self.assertIn("already exists", error)

    def test_set_status_enforces_transition_and_preserves_body(self) -> None:
        artifact_root = self.init_project()
        spec = artifact_root / "modules" / "api.md"
        spec.write_text(module_spec("api"), encoding="utf-8")
        body_before = spec.read_text().split("---\n", 2)[2]
        code, output, _ = self.run_cli(
            "set-status",
            "--project-root", str(self.root),
            "--module", "api",
            "--status", "building",
        )
        self.assertEqual(code, 0, output)
        self.assertEqual(_frontmatter_for_test(spec)["status"], "building")
        self.assertEqual(spec.read_text().split("---\n", 2)[2], body_before)
        code, _, error = self.run_cli(
            "set-status",
            "--project-root", str(self.root),
            "--module", "api",
            "--status", "complete",
        )
        self.assertEqual(code, 2)
        self.assertIn("invalid transition", error)

    def test_adapter_list_reports_v2_integrations(self) -> None:
        code, output, _ = self.run_cli("adapter", "list", "--json")
        self.assertEqual(code, 0)
        self.assertEqual(
            set(json.loads(output)["adapters"]),
            {"claude-code", "codex", "gemini", "local"},
        )

    def test_adapter_render_uses_project_configuration(self) -> None:
        artifact_root = self.init_project()
        config_path = artifact_root / "project.json"
        config = json.loads(config_path.read_text())
        config["adapters"]["providers"]["local"]["command"] = [
            "my-agent", "--root", "{project_root}", "--prompt", "{prompt}"
        ]
        config_path.write_text(json.dumps(config), encoding="utf-8")
        code, output, _ = self.run_cli(
            "adapter", "render", "local",
            "--project-root", str(self.root),
            "--role", "reviewer",
            "--prompt", "Review the module.",
            "--json",
        )
        self.assertEqual(code, 0, output)
        command = json.loads(output)["command"]
        self.assertEqual(command[0], "my-agent")
        self.assertIn(str(self.root.resolve()), command)

    def test_adapter_render_requires_explicit_write_authorization(self) -> None:
        self.init_project()
        code, _, error = self.run_cli(
            "adapter", "render", "codex",
            "--project-root", str(self.root),
            "--role", "builder",
            "--prompt", "Build it.",
        )
        self.assertEqual(code, 2)
        self.assertIn("write authorization", error)

    @patch("agentic_sdlc.cli.run_adapter")
    def test_adapter_run_returns_normalized_result(self, run) -> None:
        self.init_project()
        run.return_value = {
            "adapter": "codex",
            "role": "reviewer",
            "exit_code": 0,
            "response": "clear",
            "stdout": "",
            "stderr": "",
            "parse_error": None,
            "command": ["codex"],
        }
        code, output, _ = self.run_cli(
            "adapter", "run", "codex",
            "--project-root", str(self.root),
            "--role", "reviewer",
            "--prompt", "Review it.",
            "--json",
        )
        self.assertEqual(code, 0, output)
        self.assertEqual(json.loads(output)["response"], "clear")


def module_spec(
    name: str,
    *,
    status: str = "ready",
    depends_on: list[str] | None = None,
) -> str:
    dependencies = ", ".join(depends_on or []) or "none"
    return f"""---
id: {name}
status: {status}
depends_on: {dependencies}
security_review: risk-based
---
# {name}

## Responsibility
Own one explicit responsibility.

## Boundary
Must not absorb unrelated responsibilities.

## Requirements served
- REQ-01

## Contract
`contracts/{name}.py`

## Definition of done
- [ ] Contract tests pass.
- [ ] Production entry-point test passes.
"""


def _frontmatter_for_test(path: Path) -> dict[str, str]:
    raw = path.read_text().split("---\n", 2)[1]
    return {
        key.strip(): value.strip()
        for line in raw.splitlines()
        if ":" in line
        for key, value in [line.split(":", 1)]
    }


if __name__ == "__main__":
    unittest.main()
