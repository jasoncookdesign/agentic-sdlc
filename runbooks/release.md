# Release

1. Run the complete configured mechanical gate.
2. Confirm no open `block` verdict.
3. Discharge or explicitly accept every review condition.
4. Run assembled-system invariant tests.
5. Reconcile documentation and user-facing configuration.
6. Identify deployment, rollback, and health-verification procedures.
7. Invoke the optional release-approval hook when enabled.
8. Deploy through the project’s chosen mechanism.
9. Verify the deployed artifact directly, not merely the deployment report.
10. Record release evidence and deferred risks in the Build Record.

See `docs/deployment/` for platform recipes. Connect source-control promotion through the project’s
chosen release workflow.
