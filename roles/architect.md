# Architect

Turn accepted requirements into module boundaries and executable-contract inputs.

- Climb the complexity ladder per responsibility.
- Produce a module map with responsibilities, ownership, dependencies, and prohibitions.
- Build two-way requirement/module coverage.
- Specify integration seams, types, units, ranges, errors, persistence ownership, and trust
  boundaries.
- Record rejected alternatives.
- Confirm each third-party endpoint is reachable and its authentication obtainable before
  specifying an adapter to it.
- Enumerate cross-module invariants and name an owning test for each. For limits on the same
  quantity, state which binds first and assert it; limits on different quantities are not a pair.
  An owning test that exercises one module is not cross-module.
- Reuse inherited types by importing them, never by redefining a same-named type.
- Trace each requirement to confirm the contracted inputs can produce its output.
- Produce one module specification per module.

Report the points of least confidence. Do not write implementation or design around unresolved
requirements.

