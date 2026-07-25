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

`agentic-sdlc next` performs step 3 and returns the next dependency-ready module. Agent dispatch,
source-control isolation, and execution environments can be supplied by an adapter or external
orchestrator.

Sequential execution is the safe default. Parallel execution requires an isolation provider that
prevents builders from sharing mutable working state.
