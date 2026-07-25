---
id: {{MODULE_ID}}
status: planned
depends_on: {{DEPENDENCIES}}
security_review: risk-based
---
# {{MODULE_ID}}

## Responsibility

{{RESPONSIBILITY}}

## Boundary

State what this module must not do.

## Requirements served

{{REQUIREMENTS}}

## Contract

Name the executable interface, accepted inputs, outputs, domain errors, and immutable contract
tests.

## Definition of done

- [ ] Inherited contract tests pass unchanged.
- [ ] Unit tests were observed failing before implementation and now pass.
- [ ] Production-entry-point test passes.
- [ ] Sibling-input sweep is recorded.
- [ ] Error paths and edge cases are covered.
- [ ] Documentation is current.

## Notes

Record contract amendments, review bounces, risks, and decisions.
