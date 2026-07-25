# Simplicity

## Iron law

> Nothing is built until the complexity ladder has been climbed.

Stop at the first rung that solves the understood problem:

1. Does this need to exist?
2. Does it already exist in the codebase?
3. Does the language runtime or standard library provide it?
4. Does the platform or framework provide it?
5. Does an existing dependency provide it?
6. Is it a small composition of existing pieces?
7. Only then, write the minimum new code.

The ladder never authorizes reduced validation, error handling, security, accessibility, or
data-loss protection.

For solved problem domains—cryptography, timezones, encodings, archive and document parsing, HTML
sanitization—the burden reverses. Building requires justification because incomplete implementations
carry an open-ended correctness tail. Decide per responsibility, evaluate candidates on real inputs,
and isolate the choice behind a replaceable interface.

