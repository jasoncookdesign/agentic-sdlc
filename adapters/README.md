# Runtime adapters

Adapters connect the lifecycle to a particular agent runtime. Version 1 adapters are documentation
only; the generic CLI is the sole executable integration.

An adapter should describe:

- How capability profiles map to available models or humans.
- How to create an independent review context.
- How roles receive artifact paths and return structured results.
- How optional security and release hooks are invoked.
- Whether tool hooks can enforce test-first work.
- Which operating systems the runtime supports.

Adapters preserve the lifecycle contract while translating generic capability profiles and roles
into runtime-specific configuration. Provider-specific model names belong in that local mapping.
