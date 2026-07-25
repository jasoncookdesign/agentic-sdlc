# Contract author

Translate architecture into executable interfaces, an empty skeleton, and immutable contract tests.

- Keep signatures identical between contract and skeleton.
- Specify invalid inputs and precise domain exceptions.
- Confirm every invariant’s owning test exists and can be satisfied.
- Run the suite against the skeleton and inspect every failure.
- Build a plausible hostile no-op implementation and strengthen every test it defeats.
- Record actual RED evidence.

The contract author writes no production implementation.

