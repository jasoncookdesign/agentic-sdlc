# Linux with systemd

Use a versioned artifact, an unprivileged service account, an `EnvironmentFile` or platform secret
store, explicit working directory, restart policy, and health verification. Run `systemd-analyze
verify` on unit files, reload the daemon after changes, restart or reload the service, and inspect
both service status and application behavior. Document rollback to the previous artifact.

