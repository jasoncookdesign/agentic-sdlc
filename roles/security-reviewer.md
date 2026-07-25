# Security reviewer

Provide independent risk review when the configured policy hook triggers.

Typical triggers include credentials, authorization, untrusted input, sensitive data, financial
transactions, security posture, and release mechanisms.

Review trust boundaries, least privilege, failure mode, secret handling, dependency risk, data
lifecycle, auditability, and bypass paths. Return `clear`, `clear-with-conditions`, or `block`.
Conditions never auto-clear.

The role is runtime-neutral: it may be performed by a specialized agent, a human reviewer, or an
external security process.

