# Test-driven development

## Iron law

> No production behavior without a failing test first.

Use the cycle RED → GREEN → REFACTOR:

1. Write one minimal behavioral test.
2. Run it and confirm it fails for the expected missing behavior.
3. Write the minimum implementation that passes.
4. Run the full suite with clean output.
5. Refactor without adding behavior, rerunning tests after each change.

A test that passes immediately is not RED evidence. Import, syntax, and collection errors are not
behavioral failures. Tests-after do not demonstrate that a test can detect the missing behavior.

Avoid testing mocks, adding production methods solely for tests, broad exception assertions, and
mocking dependencies whose real contract is not understood.

Exceptions for generated code, prototypes, or configuration require a recorded rationale and the
authority configured by the adopting organization. Silence is not an exception.

