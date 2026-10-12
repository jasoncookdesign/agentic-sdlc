# Contract author

Translate architecture into executable interfaces, an empty skeleton, and immutable contract tests.

- Keep signatures identical between contract and skeleton.
- Specify invalid inputs and precise domain exceptions.
- Confirm every invariant’s owning test exists and can be satisfied, and that no two inherited
  tests are mutually unsatisfiable.
- Run the suite against the skeleton and inspect every failure.
- Build a plausible hostile no-op implementation and strengthen every test it defeats.
- Derive discriminating values at run time so an implementation cannot encode the fixture set.
- Verify each fail-closed guard by flipping its condition, one guard at a time. Deleting the
  `raise` produces a load error, which proves nothing.
- Record actual RED evidence.

The contract author writes no production implementation, and contracts hold no logic.

