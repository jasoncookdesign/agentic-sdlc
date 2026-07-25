# Runtime adapters

Adapters connect lifecycle roles to installed agent runtimes. Version 2 provides executable
adapters for Claude Code, Codex, Gemini CLI, and configurable local commands.

Every adapter:

- Runs non-interactively in the selected project root.
- Uses machine-readable provider output and returns a normalized final response.
- Accepts an optional project-local model binding or one-run `--model` override.
- Renders read-only permissions for `reviewer` and `security_reviewer`.
- Requires `--allow-write` for every other role.
- Executes an argument vector directly, never a shell command string.

Adapters preserve the lifecycle contract while translating generic capability profiles and roles
into runtime-specific configuration. Provider-specific model names belong in that local mapping.

## Commands

```bash
agentic-sdlc adapter list
agentic-sdlc adapter check <adapter> [--json]
agentic-sdlc adapter render <adapter> \
  --project-root . --role reviewer --prompt-file prompt.md --json
agentic-sdlc adapter run <adapter> \
  --project-root . --role builder --prompt-file prompt.md --allow-write --json
```

`render` is the preflight: inspect it before first use or after changing runtime configuration.
`run` returns exit code `0` only when the provider exits successfully and its final response can be
normalized.

## Credential handling

Adapters reuse authentication already configured by each runtime. Credentials are never accepted
as CLI arguments, written to `project.json`, or copied into prompts. Configure authentication using
the runtime’s official mechanism or inject secrets through the execution environment.

## Independence

Each invocation starts a new non-interactive run. For independent review, pass only the
specification, artifacts, tests, and review rubric needed by the reviewer. Do not include the
builder’s reasoning transcript.
