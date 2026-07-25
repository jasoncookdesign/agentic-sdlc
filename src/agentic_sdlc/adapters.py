from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

ADAPTERS = {
    "claude-code": {"executable": "claude", "version_args": ["--version"]},
    "codex": {"executable": "codex", "version_args": ["--version"]},
    "gemini": {"executable": "gemini", "version_args": ["--version"]},
    "local": {"executable": None, "version_args": ["--version"]},
}
READ_ONLY_ROLES = {"reviewer", "security_reviewer"}
ROLE_INSTRUCTIONS = {
    "engineering_agent": (
        "Coordinate the lifecycle, maintain durable artifacts, and surface unresolved decisions. "
        "Do not let narrative claims substitute for gate evidence."
    ),
    "delivery_lead": (
        "Coordinate scope and configured policy hooks without replacing architecture, build, "
        "review, or accountable approval."
    ),
    "requirements_interviewer": (
        "Elicit testable requirements with stable identifiers. Record ambiguity and assumptions; "
        "do not choose the architecture."
    ),
    "architect": (
        "Define module boundaries, two-way requirements coverage, integration seams, and "
        "test-owned cross-module invariants. Write no production implementation."
    ),
    "contract_author": (
        "Write executable interfaces, an empty skeleton, failing contract tests, and an "
        "adversarial no-op gate. Write no production implementation."
    ),
    "builder": (
        "Implement one specified module test-first. Inherited contract tests are immutable: "
        "never edit, skip, weaken, or replace them."
    ),
    "reviewer": (
        "Review independently from the builder context. Do not modify the work. Return evidence "
        "and exactly one verdict: clear, clear-with-conditions, or block."
    ),
    "security_reviewer": (
        "Review trust boundaries, authority, secrets, untrusted input, data lifecycle, dependency "
        "risk, auditability, and bypass paths. Do not modify the work."
    ),
}


class AdapterError(Exception):
    """An adapter request is invalid or cannot be completed."""


@dataclass(frozen=True)
class AdapterRequest:
    adapter: str
    prompt: str
    project_root: Path
    role: str
    artifact_root: Path | None = None
    model: str | None = None
    allow_write: bool = False
    local_command: Sequence[str] | None = None


def available_adapters() -> list[str]:
    return sorted(ADAPTERS)


def _validate_request(request: AdapterRequest) -> None:
    if request.adapter not in ADAPTERS:
        raise AdapterError(
            f"unknown adapter {request.adapter!r}; choose from "
            f"{', '.join(available_adapters())}"
        )
    if not request.prompt.strip():
        raise AdapterError("prompt must not be empty")
    if not request.project_root.is_dir():
        raise AdapterError(f"project root is not a directory: {request.project_root}")
    if request.artifact_root is not None and not request.artifact_root.is_dir():
        raise AdapterError(f"artifact root is not a directory: {request.artifact_root}")
    if request.role not in ROLE_INSTRUCTIONS:
        raise AdapterError(f"unknown Agentic SDLC role: {request.role!r}")
    if request.role not in READ_ONLY_ROLES and not request.allow_write:
        raise AdapterError(
            f"role {request.role!r} may modify project files; pass explicit write authorization"
        )


def compose_prompt(request: AdapterRequest) -> str:
    artifact_root = request.artifact_root or (request.project_root / ".sdlc")
    return "\n\n".join([
        f"You are performing the Agentic SDLC `{request.role}` role.",
        ROLE_INSTRUCTIONS[request.role],
        f"Project root: {request.project_root}\nLifecycle artifact root: {artifact_root}",
        "Use the lifecycle artifacts as the durable source of requirements and phase state. "
        "Do not claim a gate passed without observable evidence.",
        f"Task:\n{request.prompt.strip()}",
    ])


def _separate_artifact_root(request: AdapterRequest) -> Path | None:
    if request.artifact_root is None:
        return None
    try:
        request.artifact_root.relative_to(request.project_root)
    except ValueError:
        return request.artifact_root
    return None


def build_command(request: AdapterRequest) -> list[str]:
    _validate_request(request)
    root = str(request.project_root)
    prompt = compose_prompt(request)
    extra_root = _separate_artifact_root(request)

    if request.adapter == "codex":
        command = [
            "codex",
            "exec",
            "--json",
            "--ephemeral",
            "--sandbox",
            "read-only" if request.role in READ_ONLY_ROLES else "workspace-write",
            "--cd",
            root,
        ]
        if extra_root:
            command.extend(["--add-dir", str(extra_root)])
        if request.model:
            command.extend(["--model", request.model])
        command.append(prompt)
        return command

    if request.adapter == "claude-code":
        command = [
            "claude",
            "--print",
            "--output-format",
            "json",
            "--no-session-persistence",
            "--permission-mode",
            "plan" if request.role in READ_ONLY_ROLES else "acceptEdits",
        ]
        if extra_root:
            command.extend(["--add-dir", str(extra_root)])
        if request.model:
            command.extend(["--model", request.model])
        command.append(prompt)
        return command

    if request.adapter == "gemini":
        command = [
            "gemini",
            "--output-format",
            "json",
            "--approval-mode",
            "plan" if request.role in READ_ONLY_ROLES else "auto_edit",
        ]
        if extra_root:
            command.extend(["--include-directories", str(extra_root)])
        if request.model:
            command.extend(["--model", request.model])
        command.extend(["--prompt", prompt])
        return command

    if isinstance(request.local_command, (str, bytes)) or not request.local_command:
        raise AdapterError(
            "local adapter requires local_command as a non-empty JSON array of arguments"
        )
    replacements = {
        "{prompt}": prompt,
        "{project_root}": root,
        "{artifact_root}": str(request.artifact_root or request.project_root / ".sdlc"),
        "{role}": request.role,
        "{model}": request.model or "",
    }
    command = []
    for argument in request.local_command:
        if not isinstance(argument, str):
            raise AdapterError("every local_command argument must be a string")
        for marker, value in replacements.items():
            argument = argument.replace(marker, value)
        command.append(argument)
    return command


def _local_executable(local_command: Sequence[str] | None) -> str | None:
    if isinstance(local_command, (str, bytes)) or not local_command:
        return None
    first = local_command[0]
    return first if isinstance(first, str) and first else None


def probe_adapter(
    adapter: str,
    *,
    local_command: Sequence[str] | None = None,
    timeout_seconds: int = 10,
) -> dict:
    if adapter not in ADAPTERS:
        raise AdapterError(f"unknown adapter {adapter!r}")
    executable = (
        _local_executable(local_command)
        if adapter == "local"
        else str(ADAPTERS[adapter]["executable"])
    )
    if not executable:
        return {
            "adapter": adapter,
            "available": False,
            "executable": None,
            "version": None,
            "error": "local command is not configured",
        }
    resolved = shutil.which(executable)
    if not resolved:
        return {
            "adapter": adapter,
            "available": False,
            "executable": executable,
            "version": None,
            "error": "executable not found on PATH",
        }
    try:
        completed = subprocess.run(
            [resolved, *ADAPTERS[adapter]["version_args"]],
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {
            "adapter": adapter,
            "available": False,
            "executable": resolved,
            "version": None,
            "error": str(exc),
        }
    version = (completed.stdout or completed.stderr).strip().splitlines()
    return {
        "adapter": adapter,
        "available": completed.returncode == 0,
        "executable": resolved,
        "version": version[0] if version else None,
        "error": None if completed.returncode == 0 else f"version command exited {completed.returncode}",
    }


def normalize_output(adapter: str, stdout: str) -> str:
    if adapter == "local":
        return stdout.strip()

    if adapter == "codex":
        messages = []
        for line in stdout.splitlines():
            if not line.strip():
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            item = event.get("item") if isinstance(event, dict) else None
            if (
                event.get("type") == "item.completed"
                and isinstance(item, dict)
                and item.get("type") == "agent_message"
                and isinstance(item.get("text"), str)
            ):
                messages.append(item["text"])
        if messages:
            return messages[-1].strip()
        raise AdapterError("Codex JSONL contained no completed agent message")

    try:
        payload = json.loads(stdout)
    except json.JSONDecodeError as exc:
        raise AdapterError(f"{adapter} returned invalid JSON: {exc}") from exc
    field = "result" if adapter == "claude-code" else "response"
    response = payload.get(field) if isinstance(payload, dict) else None
    if not isinstance(response, str):
        raise AdapterError(f"{adapter} JSON output lacks string field {field!r}")
    return response.strip()


def run_adapter(
    request: AdapterRequest,
    *,
    timeout_seconds: int = 1800,
) -> dict:
    command = build_command(request)
    try:
        completed = subprocess.run(
            command,
            cwd=request.project_root,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )
    except FileNotFoundError as exc:
        raise AdapterError(f"adapter executable not found: {command[0]}") from exc
    except subprocess.TimeoutExpired as exc:
        raise AdapterError(
            f"{request.adapter} exceeded timeout of {timeout_seconds} seconds"
        ) from exc
    response = None
    parse_error = None
    if completed.stdout:
        try:
            response = normalize_output(request.adapter, completed.stdout)
        except AdapterError as exc:
            parse_error = str(exc)
    return {
        "adapter": request.adapter,
        "role": request.role,
        "exit_code": completed.returncode,
        "response": response,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "parse_error": parse_error,
        "command": command,
    }
