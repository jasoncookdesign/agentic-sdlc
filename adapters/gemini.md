# Gemini CLI adapter

## Requirements

- Install and authenticate Gemini CLI.
- Confirm availability with `agentic-sdlc adapter check gemini`.

The adapter invokes Gemini headless mode with `--output-format json`. Build roles use
`--approval-mode auto_edit`; review roles use the read-only `--approval-mode plan`.

```bash
agentic-sdlc adapter run gemini \
  --project-root . \
  --role security_reviewer \
  --prompt-file .sdlc/prompts/security-review.md \
  --json
```

Gemini CLI returns a JSON object whose `response` field becomes the normalized adapter response.
Exit codes from the runtime are preserved by the adapter result.

Official references:

- [Gemini CLI headless mode](https://geminicli.com/docs/cli/headless/)
- [Gemini CLI Plan Mode](https://geminicli.com/docs/cli/plan-mode/)
- [Gemini CLI configuration](https://geminicli.com/docs/reference/configuration/)
