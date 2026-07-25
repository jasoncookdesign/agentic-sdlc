# Module execution loop

The module execution loop advances independently specified modules through build and review.

1. Read `RECORD.md`, `project.json`, and every module specification.
2. Confirm artifact state against the filesystem.
3. Select one module whose dependencies are complete and whose status is `planned` or `ready`.
4. Give the builder its module specification and immutable contract tests.
5. Run configured contract, unit, and project checks.
6. Send the artifact to an independent reviewer without the builder’s reasoning trace.
7. Record the verdict and conditions.
8. Mark the module complete only after blocking findings are resolved.
9. Repeat.

`agentic-sdlc next` performs step 3 and returns the next dependency-ready module.

Version 2 can dispatch the build and review roles directly:

```bash
agentic-sdlc adapter check codex
agentic-sdlc adapter render codex \
  --project-root /path/to/project \
  --role builder \
  --prompt-file build-task.md
agentic-sdlc adapter run codex \
  --project-root /path/to/project \
  --role builder \
  --prompt-file build-task.md \
  --allow-write \
  --json
agentic-sdlc adapter run codex \
  --project-root /path/to/project \
  --role reviewer \
  --prompt-file review-task.md \
  --json
```

The builder invocation requires explicit write authorization. The reviewer invocation is read-only
and should receive the resulting artifacts and diff, not the builder’s reasoning trace. Record the
review outcome with `agentic-sdlc record-review`; adapter output does not advance module state
automatically.

The adapters do not create branches, worktrees, containers, or queues. Source-control isolation,
parallel scheduling, and long-running orchestration remain integration choices.

Sequential execution is the safe default. Parallel execution requires an isolation provider that
prevents builders from sharing mutable working state.
