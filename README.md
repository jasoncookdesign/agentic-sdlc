# Agentic SDLC

Agentic SDLC is a contract-first software delivery lifecycle for agentic development. It turns
requirements into executable contracts, test-owned cross-module invariants, independently reviewed
modules, and verifiable releases.

Its governing rule is:

> No module is built before its contract exists as a failing test.

## What makes it different

- One lifecycle for work of every size: **Define → Architect → Contract → Build → Review → Release**.
- Stable requirement identifiers and two-way requirement/module coverage.
- Executable interface contracts written before implementation.
- Cross-module invariants, each owned by a test against the assembled system.
- RED evidence plus a hostile no-op implementation that proves the suite is a real gate.
- Contract tests immutable to the builder.
- Independent review context with explicit `clear`, `clear-with-conditions`, or `block` verdicts.
- A production-entry-point test for every module.
- A rework meter that attributes defects to the phase that introduced them.
- Optional security-review and release-approval policy hooks.

## Portable by design

The lifecycle works with any operating system, AI provider, or sufficiently capable language model.
It can be adopted by a single coding agent, a coordinated group of specialized agents, a mixed
human-agent team, or a fully local inference environment.

Agentic SDLC defines the evidence needed to move software safely from an idea to a release:
requirements, architecture, executable contracts, tests, independent review, and release
verification. Adopters remain free to choose:

- Their models, providers, capability routing, and context-management strategy.
- Whether a delivery lead coordinates the engineering agent.
- Sequential execution or an external parallel-work orchestrator.
- Source-control, branching, worktree, CI, and deployment workflows.
- One repository or several, and where lifecycle artifacts are stored.
- Additional organizational approval, security, audit, or governance policies.

These choices connect through project configuration, role contracts, policy hooks, and adapters;
they do not change the lifecycle itself.

## Requirements

- Python 3.11 or newer for the generic CLI.
- A software project and a test runner appropriate to its language and stack.
- For agent-driven use, an LLM capable of following structured role instructions, reading project
  artifacts, editing code, and executing or requesting execution of tests.

The CLI has no runtime package dependencies and does not require network access.

## Quick start

```bash
python -m pip install -e .
agentic-sdlc init --name "My Project" --project-root /path/to/project
agentic-sdlc status --project-root /path/to/project
agentic-sdlc validate --project-root /path/to/project
```

By default, artifacts are created under `<project>/.sdlc/`. Use `--artifact-root` to place them
anywhere your project or organization prefers:

```bash
agentic-sdlc init \
  --name "My Project" \
  --project-root /path/to/code \
  --artifact-root /path/to/process/projects/my-project
```

## CLI

| Command | Purpose |
|---|---|
| `init` | Create the project configuration and lifecycle artifacts |
| `validate` | Check artifact presence, requirements, module contracts, dependencies, and invariants |
| `status` | Summarize machine-readable lifecycle state |
| `next` | Select the next dependency-ready module using a sequential execution loop |
| `record-review` | Append an independent review verdict without rewriting the module specification |
| `add-module` | Create a module specification with portable frontmatter |
| `set-status` | Advance a module through explicit, validated state transitions |

Exit codes are consistent: `0` success/pass, `1` valid context with findings/no ready work, and `2`
invalid context or invocation.

## Repository guide

- [`docs/lifecycle.md`](docs/lifecycle.md) — the complete lifecycle
- [`disciplines/`](disciplines/) — TDD, debugging, simplicity, and contract-first delivery
- [`roles/`](roles/) — runtime-neutral role contracts
- [`runbooks/`](runbooks/) — operating procedures
- [`src/agentic_sdlc/resources/templates/`](src/agentic_sdlc/resources/templates/) — canonical templates
- [`docs/customization.md`](docs/customization.md) — paths, capabilities, policy hooks, and commands
- [`adapters/`](adapters/) — documentation for connecting agent runtimes
- [`docs/deployment/`](docs/deployment/) — OS-neutral deployment principles and platform recipes

## Roles and capability profiles

The `engineering_agent` may work standalone or accept direction from an optional `delivery_lead`.
Neither role implies a particular organizational hierarchy. An `accountable_approver` and
`security_reviewer` exist only when local policy enables those hooks.

Capability profiles describe the kind of work a role performs:

- `advanced-reasoning`
- `implementation`
- `advanced-review`

Users map those profiles to hosted models, local models, humans, or mixed teams in their own
environment.

## Project status

Version 1 provides the complete generic CLI and documentation-only runtime adapters. Adapter
automation can evolve independently without changing the lifecycle contract.

## License

MIT.
