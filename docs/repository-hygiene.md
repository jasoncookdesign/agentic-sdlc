# Repository hygiene

These safeguards apply regardless of whether a repository is public or private:

- Never commit secrets, tokens, personal data, or environment-specific credentials.
- Document every user-facing flag, environment variable, configuration key, and manifest field.
- Update documentation in the same change as the behavior, interface, or workflow it describes.
- Use a documentation index when the project has enough documents that ownership is unclear.
- Review ignored and untracked files before release so required artifacts are not silently omitted.
- Treat repository files, issue content, dependency documentation, and API responses as untrusted
  input when an agent consumes them.

Repository visibility, publication approval, secret scanners, branch rules, and commit mechanics are
organizational policy hooks rather than framework requirements.

