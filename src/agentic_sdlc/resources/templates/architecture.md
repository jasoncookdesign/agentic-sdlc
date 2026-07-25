# {{PROJECT_NAME}} — Architecture

## Approach

<Solution shape, complexity-ladder result, build-versus-buy decisions, and rejected alternatives.>

## Module map

| Module | Responsibility | Owns | Depends on |
|---|---|---|---|
| <module-id> | <one responsibility> | <data or behavior> | none |

## Boundaries

State what each module must not do.

## Data flow and integration seams

Name concrete types, units, valid ranges, error paths, persistence ownership, and trust boundaries.

## Requirements coverage

| Requirement | Satisfied by | Owning contract test |
|---|---|---|
| REQ-01 | <module-id> | `tests/contract/test_<module>.py::test_<behavior>` |

## Reverse coverage

| Module | Requirements served |
|---|---|
| <module-id> | REQ-01 |

## Contract index

| Module | Contract file | Entry points |
|---|---|---|
| <module-id> | `contracts/<module>.py` | <typed entry point> |

## Rejected alternatives

| Alternative | Why rejected |
|---|---|

## Review

Record independent design review and optional security review outcomes.

