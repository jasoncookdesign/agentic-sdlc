# Changelog

All notable changes to Agentic SDLC are documented here.

## 2.0.0

- Added executable adapters for Claude Code, Codex, Gemini CLI, and configurable local agents.
- Added role-aware prompt composition for all lifecycle roles.
- Added runtime discovery, command rendering, execution, and normalized JSON output.
- Added explicit write authorization for implementation roles and enforced read-only review roles.
- Added support for lifecycle artifacts stored inside or outside the software project.
- Added project-local model bindings and shell-free local command templates.
- Expanded provider setup, authentication, safety, and troubleshooting guidance.

Version 1 project artifacts remain compatible. Adapter configuration is optional except when using
the configurable local-command adapter.

## 1.0.0

- Introduced the portable contract-first lifecycle and generic Python CLI.
- Added lifecycle artifacts, role contracts, disciplines, runbooks, templates, validation, module
  state transitions, dependency-ready selection, and independent review records.
