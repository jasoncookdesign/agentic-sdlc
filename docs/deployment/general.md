# Deployment

Deployment is a project-defined integration point. Every project should document:

- Build artifact and provenance.
- Target environment and runtime version.
- Configuration and secret injection.
- Installation or rollout command.
- Health and behavioral verification.
- Rollback procedure.
- Data migration and rollback constraints.
- Observability and failure notification.

Deployment success is established by inspecting the deployed behavior, not by trusting a command’s
zero exit code or a platform’s success message.

Treat a runtime or interpreter upgrade as a redeploy of every service that runs on it. Confirm each
has a current dependency manifest, reinstall its dependencies, then run each one and confirm a clean
result before relying on its next scheduled run.
