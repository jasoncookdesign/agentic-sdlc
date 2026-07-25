# {{PROJECT_NAME}} — Cross-Module Invariants

Every invariant spans a real module boundary and names an owning executable test.

| id | Invariant | Modules spanned | Owning test | Verified |
|---|---|---|---|---|
| INV-01 | <relationship that must hold> | <module-a>, <module-b> | `tests/contract/test_invariants.py::test_<property>` | RED pending |

## Categories swept

- Mutually satisfiable bounds
- Ordering
- Lifecycle and state transitions
- Units and representations
- Authority
- Conservation
- Inherited controls on new paths

## Accepted untestable invariants

| id | Invariant | Why untestable | Risk accepted by |
|---|---|---|---|

If the design has none, replace the placeholder row with the exact statement:
`No cross-module invariants`.

