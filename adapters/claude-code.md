# Claude Code adapter

## Requirements

- Install and authenticate Claude Code.
- Confirm availability with `agentic-sdlc adapter check claude-code`.

The adapter uses `claude --print --output-format json` with session persistence disabled. Build
roles use `--permission-mode acceptEdits`; review roles use `--permission-mode plan`.

```bash
agentic-sdlc adapter run claude-code \
  --project-root . \
  --role builder \
  --prompt-file .sdlc/prompts/build-api.md \
  --allow-write \
  --json
```

Claude Code reuses its configured authentication and settings. A model configured in
`project.json`, or supplied with `--model`, is passed through unchanged. Review should be a fresh
invocation containing the review inputs rather than the builder transcript.

Official reference:

- [Claude Code CLI reference](https://docs.anthropic.com/en/docs/claude-code/cli-usage)
