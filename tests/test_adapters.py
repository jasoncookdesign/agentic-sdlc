from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from agentic_sdlc.adapters import (
    AdapterError,
    AdapterRequest,
    available_adapters,
    build_command,
    compose_prompt,
    normalize_output,
    probe_adapter,
    run_adapter,
)


class AdapterContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.prompt = "Implement the health module."

    def tearDown(self) -> None:
        self.temp.cleanup()

    def request(self, adapter: str, **overrides) -> AdapterRequest:
        values = {
            "adapter": adapter,
            "prompt": self.prompt,
            "project_root": self.root,
            "role": "builder",
            "artifact_root": None,
            "model": None,
            "allow_write": True,
            "local_command": None,
        }
        values.update(overrides)
        return AdapterRequest(**values)

    def test_registry_contains_every_v2_adapter(self) -> None:
        self.assertEqual(
            set(available_adapters()),
            {"claude-code", "codex", "gemini", "local"},
        )

    def test_codex_command_uses_exec_workspace_and_explicit_sandbox(self) -> None:
        command = build_command(self.request("codex", model="configured-codex"))
        self.assertEqual(command[:2], ["codex", "exec"])
        self.assertIn("--json", command)
        self.assertEqual(command[command.index("--sandbox") + 1], "workspace-write")
        self.assertEqual(command[command.index("--cd") + 1], str(self.root))
        self.assertEqual(command[command.index("--model") + 1], "configured-codex")
        self.assertIn(self.prompt, command[-1])
        self.assertIn("immutable", command[-1].lower())

    def test_codex_review_is_read_only(self) -> None:
        command = build_command(
            self.request("codex", role="reviewer", allow_write=False)
        )
        self.assertEqual(command[command.index("--sandbox") + 1], "read-only")

    def test_claude_command_uses_print_json_and_permission_mode(self) -> None:
        command = build_command(self.request("claude-code", model="configured-claude"))
        self.assertEqual(command[0], "claude")
        self.assertIn("--print", command)
        self.assertEqual(command[command.index("--output-format") + 1], "json")
        self.assertEqual(command[command.index("--permission-mode") + 1], "acceptEdits")
        self.assertEqual(command[command.index("--model") + 1], "configured-claude")
        self.assertIn(self.prompt, command[-1])

    def test_gemini_command_uses_headless_json(self) -> None:
        command = build_command(self.request("gemini", model="configured-gemini"))
        self.assertEqual(command[0], "gemini")
        self.assertEqual(command[command.index("--output-format") + 1], "json")
        self.assertEqual(command[command.index("--approval-mode") + 1], "auto_edit")
        self.assertEqual(command[command.index("--model") + 1], "configured-gemini")
        self.assertIn(self.prompt, command[command.index("--prompt") + 1])

    def test_gemini_review_uses_read_only_plan_mode(self) -> None:
        command = build_command(
            self.request("gemini", role="reviewer", allow_write=False)
        )
        self.assertEqual(command[command.index("--approval-mode") + 1], "plan")

    def test_local_command_is_argv_template_without_shell(self) -> None:
        command = build_command(
            self.request(
                "local",
                local_command=[
                    "my-agent",
                    "--root",
                    "{project_root}",
                    "--role",
                    "{role}",
                    "--prompt",
                    "{prompt}",
                ],
            )
        )
        self.assertEqual(
            command,
            [
                "my-agent",
                "--root",
                str(self.root),
                "--role",
                "builder",
                "--prompt",
                command[-1],
            ],
        )
        self.assertIn(self.prompt, command[-1])

    def test_local_command_rejects_string_shell_template(self) -> None:
        with self.assertRaises(AdapterError):
            build_command(self.request("local", local_command="agent {prompt}"))

    def test_normalizes_provider_outputs(self) -> None:
        codex = "\n".join([
            json.dumps({"type": "thread.started", "thread_id": "t1"}),
            json.dumps({
                "type": "item.completed",
                "item": {"type": "agent_message", "text": "Codex result"},
            }),
        ])
        self.assertEqual(normalize_output("codex", codex), "Codex result")
        self.assertEqual(
            normalize_output("claude-code", json.dumps({"result": "Claude result"})),
            "Claude result",
        )
        self.assertEqual(
            normalize_output("gemini", json.dumps({"response": "Gemini result"})),
            "Gemini result",
        )
        self.assertEqual(normalize_output("local", "Local result\n"), "Local result")

    @patch("agentic_sdlc.adapters.shutil.which", return_value="/usr/bin/codex")
    @patch("agentic_sdlc.adapters.subprocess.run")
    def test_probe_reports_version(self, run, _which) -> None:
        run.return_value.returncode = 0
        run.return_value.stdout = "codex-cli 1.2.3\n"
        run.return_value.stderr = ""
        result = probe_adapter("codex")
        self.assertTrue(result["available"])
        self.assertEqual(result["version"], "codex-cli 1.2.3")

    @patch("agentic_sdlc.adapters.subprocess.run")
    def test_run_uses_argv_cwd_timeout_and_no_shell(self, run) -> None:
        run.return_value.returncode = 0
        run.return_value.stdout = json.dumps({"response": "done"})
        run.return_value.stderr = ""
        result = run_adapter(
            self.request("gemini"),
            timeout_seconds=90,
        )
        self.assertEqual(result["response"], "done")
        _, kwargs = run.call_args
        self.assertEqual(kwargs["cwd"], self.root)
        self.assertEqual(kwargs["timeout"], 90)
        self.assertNotIn("shell", kwargs)

    def test_write_capable_role_requires_allow_write(self) -> None:
        with self.assertRaises(AdapterError):
            build_command(self.request("codex", allow_write=False, role="builder"))

    def test_role_contract_is_composed_with_task(self) -> None:
        prompt = compose_prompt(
            self.request("codex", role="reviewer", allow_write=False)
        )
        self.assertIn("independent", prompt.lower())
        self.assertIn("do not modify", prompt.lower())
        self.assertIn(self.prompt, prompt)

    def test_split_artifact_root_is_granted_to_each_provider(self) -> None:
        artifacts = self.root.parent / "process-artifacts"
        artifacts.mkdir(exist_ok=True)
        codex = build_command(self.request("codex", artifact_root=artifacts))
        claude = build_command(self.request("claude-code", artifact_root=artifacts))
        gemini = build_command(self.request("gemini", artifact_root=artifacts))
        self.assertEqual(codex[codex.index("--add-dir") + 1], str(artifacts))
        self.assertEqual(claude[claude.index("--add-dir") + 1], str(artifacts))
        self.assertEqual(
            gemini[gemini.index("--include-directories") + 1], str(artifacts)
        )


if __name__ == "__main__":
    unittest.main()
