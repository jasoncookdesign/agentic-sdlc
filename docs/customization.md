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
