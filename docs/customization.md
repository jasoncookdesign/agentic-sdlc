# Customization

`project.json` is the runtime-neutral configuration surface.

## Layout

`project.project_root` identifies the software project. `project.artifact_root` identifies lifecycle
artifacts. The default is `<project>/.sdlc/`; explicit paths support monorepos, shared process
directories, or separate lifecycle repositories.

## Coordination

```json
{"coordination": {"mode": "standalone", "delivery_lead": null}}
```

In standalone mode the `engineering_agent` coordinates the lifecycle. In delegated mode it accepts
scope and decisions from a configured `delivery_lead`. The engineering process is otherwise
identical.

## Capability profiles

Profiles describe capabilities rather than providers:

- `advanced-reasoning`: ambiguity resolution, architecture, and contract design.
- `implementation`: specified work under executable tests.
- `advanced-review`: adversarial evaluation in an independent context.

An adapter may map these to any hosted model, local inference server, human role, or combination.
The reviewer capability must not be weaker than the builder capability.

## Policy hooks

Security review defaults to risk-based. Release approval defaults off. Organizations may enable,
disable, or replace either without changing lifecycle stages.

```json
{
  "policy_hooks": {
    "security_review": {"mode": "risk-based", "role": "security_reviewer"},
    "release_approval": {"enabled": false, "role": "accountable_approver"}
  }
}
```

Risk-based security triggers normally include credentials, authorization, sensitive data, untrusted
input, financial transactions, and changes to security posture.

## Mechanical commands

Configure commands for the local stack:

```json
{
  "commands": {
    "test": "python -m unittest discover",
    "contract_test": "python -m unittest discover -s tests/contract",
    "release_verify": "./scripts/smoke-test"
  }
}
```

Commands are data, allowing each project to use its own language, package manager, CI provider,
shell, and operating system.

## Runtime adapters

Provider model names are optional project-local bindings:

```json
{
  "adapters": {
    "default": "codex",
    "providers": {
      "claude-code": {"model": null},
      "codex": {"model": null},
      "gemini": {"model": null},
      "local": {
        "model": null,
        "command": [
          "my-agent",
          "--root", "{project_root}",
          "--role", "{role}",
          "--model", "{model}",
          "--prompt", "{prompt}"
        ]
      }
    }
  }
}
```

Supported local-command placeholders are `{project_root}`, `{artifact_root}`, `{role}`, `{model}`,
and `{prompt}`. The command must be a JSON array. Each item becomes one process argument; shell
strings, pipelines, redirections, substitutions, and implicit shell expansion are not accepted.

Use `--model` for a one-run override. An omitted model lets the runtime apply its own configured
default.

The project root is always the runtime working directory. When the artifact root is outside the
project root, hosted adapters receive it as an additional readable directory. Local commands
receive both paths through placeholders when those placeholders are included.

Roles that may change project files require `--allow-write`. The `reviewer` and
`security_reviewer` roles are always invoked read-only. `adapter render` shows the exact argument
vector without starting a model; `adapter check` verifies that the selected runtime is available.
Adapter responses can be normalized as JSON, but they do not mutate lifecycle status or record
review verdicts automatically.

## Upgrading a version 1 project

Existing lifecycle artifacts remain compatible with version 2 or later. The new adapter configuration is
optional for Claude Code, Codex, and Gemini unless a project-level model binding is desired. To use
the local adapter, add its command array under `adapters.providers.local` as shown above.

Newly initialized projects use configuration schema version 2. Do not re-run `init` merely to
upgrade an existing project.
