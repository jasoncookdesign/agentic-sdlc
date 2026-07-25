# Lifecycle

Agentic SDLC uses one lifecycle for every change. Small work uses small artifacts; it does not use a
different process.

## 1. Define

Produce `REQUIREMENTS.md`.

- Give each requirement a stable, append-only `REQ-NN` identifier.
- Pair it with an acceptance statement a test could assert.
- Record explicit non-goals.
- State failure behavior, scale, data handling, security, observability, and accessibility.
- Treat unresolved ambiguity as a finding. Do not convert it into a plausible assumption.

Exit when requirements are testable and blocking questions are resolved or explicitly carried.

## 2. Architect

Produce `ARCHITECTURE.md`, `INVARIANTS.md`, and one file in `modules/` per module.

- Map every requirement to at least one module.
- Map every module back to at least one requirement.
- State what each module owns and what it must not do.
- Define concrete integration seams, units, ranges, error types, and trust boundaries.
- Answer build-versus-buy per responsibility.
- Give every cross-module invariant an executable owning test.

Exit after independent design review. Security review is an optional risk-based policy hook.

## 3. Contract

Write executable contracts, an empty implementation skeleton, and failing contract tests.

1. Run the suite against the skeleton.
2. Confirm failures are missing-behavior failures, not import, syntax, or collection errors.
3. Record actual RED output.
4. Run the real suite against a plausible hostile no-op implementation.
5. Strengthen every test that the no-op passes; do not expand an allowlist to manufacture green.
6. Have an independent reviewer write or assess a separate adversarial implementation.

Exit only when the suite is demonstrated to constrain cheap implementations.

## 4. Build

Build one dependency-ready module at a time.

- The builder inherits contract tests and may not edit, skip, weaken, or replace them.
- A runtime adapter may edit the project only when the invocation explicitly grants write access.
- Each new unit test is observed failing before implementation.
- Implementation is the minimum needed to pass.
- Every module includes a production-entry-point test.
- Every fix includes a sibling-input sweep.
- Contract defects return to Contract or Architect; the builder does not repair its own judge.

## 5. Review

Review occurs in a context independent of the builder’s reasoning trace.

- Run reviewer and security-reviewer roles without project write access.
- Review contracts, behavior, tests, integration seams, error paths, and scope.
- Run invariants against the assembled system.
- Use `clear`, `clear-with-conditions`, or `block`.
- Never silently reinterpret a conditional clear as a clean clear.
- Record every defect’s phase of introduction in the rework meter.
- Two bounces warrant stronger review; three require architecture reassessment.

## 6. Release

Release approval is optional organizational policy. The lifecycle always requires:

- Mechanical checks pass.
- No open blocking verdict.
- Review conditions are discharged or explicitly accepted.
- Deployment and rollback methods are identified.
- The deployed artifact is verified directly.
- Documentation and user-facing configuration are current.

The runtime, process manager, hosting platform, and source-control workflow are local choices.

## Executing roles

The lifecycle is usable as a human process, through another orchestration system, or directly
through the version 2 or later runtime adapters. Adapter execution combines the selected role contract with
the task prompt and the configured project and artifact roots.

```bash
agentic-sdlc adapter check codex
agentic-sdlc adapter run codex \
  --project-root /path/to/project \
  --role reviewer \
  --prompt "Review the next module and return a recorded verdict." \
  --json
```

Use `adapter render` to inspect the exact argument vector before execution. Builder and other
write-capable roles require `--allow-write`; reviewer roles remain read-only.
