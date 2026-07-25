# Local inference adapter

The local adapter connects Agentic SDLC to any non-interactive agent executable. Configure an argv
template in `.sdlc/project.json`:

```json
{
  "adapters": {
    "providers": {
      "local": {
        "model": "local-coder",
        "command": [
          "my-agent",
          "--root", "{project_root}",
          "--artifacts", "{artifact_root}",
          "--role", "{role}",
          "--model", "{model}",
          "--prompt", "{prompt}"
        ]
      }
    }
  }
}
```

The executable may use Ollama, LM Studio, llama.cpp, vLLM, or another inference backend; it is
responsible for tools and agent behavior. Its final response must be plain text on stdout and
failures must use a nonzero exit code.

The adapter replaces placeholders argument-by-argument and executes without a shell. A string such
as `"my-agent --prompt {prompt}"` is rejected. Use a JSON array so prompts cannot become shell
syntax.

When one local model performs both build and review, start separate invocations and give the review
run only the specification, artifact, tests, and rubric.
