# Contract-first delivery

## Iron law

> No module is built before its contract exists as a failing test.

A prose interface is a design note. An executable interface plus a test observed failing for
missing behavior is a contract.

Contracts define typed signatures, units, ranges, return shapes, domain errors, invalid-input
behavior, and the integration seam. Builders inherit contract tests unchanged. A disputed contract
returns to architecture; it is never weakened by the implementation role.

RED against an empty skeleton proves only that the suite loads. A hostile implementation that
returns plausible constants, performs no guarded work, and still fails the suite is stronger
evidence that the suite is a gate.

Every invariant spanning modules names an owning test run against the assembled system. Tests must
pair negative assertions with positive evidence only real work can satisfy, use specific exception
types, and avoid fixtures whose expected answer is plainly recoverable from raw bytes.

A production-entry-point test that stubs the entry point proves only that argument parsing is wired.
At least one test constructs the real composition root (real configuration and collaborators) and
drives the capability end to end through its entry point over temporary paths, stubbing only
genuinely external effects such as network, paid services, and the clock. Hostile and adversarial
implementations replace a component, so they cannot detect defects in the wiring around it.

A change to a shared interface or data format first enumerates every consumer, then updates them in
the same change and lists them in its description. For stored data, deploy readers that accept both
shapes first, then migrate, then regenerate derived artifacts. A consumer that cannot be updated is
named, with its breakage risk, before the change lands.

