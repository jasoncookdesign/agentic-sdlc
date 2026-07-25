# Codex adapter

## Requirements

- Install and authenticate the Codex CLI.
- Confirm availability with `agentic-sdlc adapter check codex`.

The adapter uses the stable non-interactive `codex exec` command with JSONL output and ephemeral
session state. Build roles receive `--sandbox workspace-write`; review roles receive
`--sandbox read-only`. The project path is passed explicitly with `--cd`.

```bash
agentic-sdlc adapter run codex \
  --project-root . \
  --role reviewer \
  --prompt-file .sdlc/prompts/review-api.md \
  --json
```

Codex reuses its saved CLI authentication. A model configured in `project.json`, or supplied with
`--model`, is passed through unchanged. An omitted model uses the Codex configuration default.

Official references:

- [Codex CLI command reference](https://learn.chatgpt.com/docs/developer-commands?surface=cli)
- [Codex non-interactive mode](https://learn.chatgpt.com/docs/non-interactive-mode)
