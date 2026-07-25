from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import UTC, datetime
from importlib.resources import files
from pathlib import Path

DEFAULT_ARTIFACT_ROOT = ".sdlc"
TEMPLATES = {
    "RECORD.md": "build-record.md",
    "REQUIREMENTS.md": "requirements.md",
    "ARCHITECTURE.md": "architecture.md",
    "INVARIANTS.md": "invariants.md",
}
VALID_STATUSES = {"planned", "ready", "building", "review", "blocked", "complete"}
VALID_VERDICTS = {"clear", "clear-with-conditions", "block"}
STATUS_TRANSITIONS = {
    "planned": {"ready", "blocked"},
    "ready": {"building", "blocked"},
    "building": {"review", "blocked"},
    "review": {"complete", "building", "blocked"},
    "blocked": {"planned", "ready"},
    "complete": set(),
}


class ContextError(Exception):
    """The requested project or artifact context cannot be resolved."""


def _now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def _resolve(project_root: str, artifact_root: str | None) -> tuple[Path, Path]:
    project = Path(project_root).expanduser().resolve()
    artifact = (
        Path(artifact_root).expanduser().resolve()
        if artifact_root
        else project / DEFAULT_ARTIFACT_ROOT
    )
    return project, artifact


def _load_project(artifact: Path) -> dict:
    config = artifact / "project.json"
    if not config.is_file():
        raise ContextError(
            f"{config} does not exist; run 'agentic-sdlc init' or pass --artifact-root"
        )
    try:
        data = json.loads(config.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContextError(f"cannot read {config}: {exc}") from exc
    if not isinstance(data, dict):
        raise ContextError(f"{config} must contain a JSON object")
    return data


def _template(name: str, replacements: dict[str, str]) -> str:
    text = (
        files("agentic_sdlc")
        .joinpath("resources", "templates", name)
        .read_text(encoding="utf-8")
    )
    for key, value in replacements.items():
        text = text.replace(f"{{{{{key}}}}}", value)
    return text


def cmd_init(args: argparse.Namespace) -> int:
    project, artifact = _resolve(args.project_root, args.artifact_root)
    if artifact.exists() and any(artifact.iterdir()) and not args.force:
        print(
            f"artifact root already exists and is not empty: {artifact}; use --force",
            file=sys.stderr,
        )
        return 2
    project.mkdir(parents=True, exist_ok=True)
    artifact.mkdir(parents=True, exist_ok=True)
    (artifact / "modules").mkdir(exist_ok=True)

    created = _now()
    config = {
        "schema_version": 1,
        "project": {
            "name": args.name,
            "slug": args.slug or _slugify(args.name),
            "project_root": str(project),
            "artifact_root": str(artifact),
            "created": created,
        },
        "coordination": {
            "mode": args.coordination,
            "delivery_lead": None,
            "accountable_approver": None,
        },
        "execution": {"concurrency": 1, "isolation_provider": None},
        "capability_profiles": {
            "architecture": "advanced-reasoning",
            "build": "implementation",
            "review": "advanced-review",
        },
        "invariants": {
            "independent_review_context": True,
            "contract_tests_immutable_to_builder": True,
            "reviewer_capability_not_weaker_than_builder": True,
        },
        "policy_hooks": {
            "security_review": {"mode": "risk-based", "role": "security_reviewer"},
            "release_approval": {"enabled": False, "role": "accountable_approver"},
        },
        "commands": {"test": None, "contract_test": None, "release_verify": None},
    }
    (artifact / "project.json").write_text(
        json.dumps(config, indent=2) + "\n", encoding="utf-8"
    )
    replacements = {
        "PROJECT_NAME": args.name,
        "PROJECT_SLUG": config["project"]["slug"],
        "CREATED": created[:10],
    }
    for destination, source in TEMPLATES.items():
        path = artifact / destination
        if not path.exists() or args.force:
            path.write_text(_template(source, replacements), encoding="utf-8")
    reviews = artifact / "reviews.json"
    if not reviews.exists() or args.force:
        reviews.write_text('{"schema_version": 1, "modules": {}}\n', encoding="utf-8")
    print(f"Initialized Agentic SDLC artifacts at {artifact}")
    return 0


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "project"


def _frontmatter(path: Path) -> dict[str, object]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return {}
    try:
        raw = text.split("---\n", 2)[1]
    except IndexError:
        return {}
    result: dict[str, object] = {}
    for line in raw.splitlines():
        if ":" not in line or line.lstrip().startswith("#"):
            continue
        key, value = line.split(":", 1)
        value = value.strip()
        if key.strip() == "depends_on":
            result[key.strip()] = (
                [] if value.lower() in {"", "none", "[]"} else
                [part.strip() for part in value.strip("[]").split(",") if part.strip()]
            )
        else:
            result[key.strip()] = value
    return result


def _modules(artifact: Path) -> dict[str, dict]:
    result = {}
    for path in sorted((artifact / "modules").glob("*.md")):
        data = _frontmatter(path)
        module_id = str(data.get("id") or path.stem)
        data["_path"] = str(path)
        result[module_id] = data
    return result


def _validate(artifact: Path, config: dict) -> dict:
    findings: list[dict[str, str]] = []
    checks = 0

    def check(ok: bool, guard: str, detail: str) -> None:
        nonlocal checks
        checks += 1
        if not ok:
            findings.append({"guard": guard, "detail": detail})

    for name in TEMPLATES:
        check((artifact / name).is_file(), "artifact_present", f"{name} is missing")
    for section in ("project", "coordination", "execution", "invariants", "policy_hooks"):
        check(section in config, "config_section", f"project.json lacks {section}")

    requirements = _safe_read(artifact / "REQUIREMENTS.md")
    req_rows = re.findall(r"^\|\s*(REQ-\d+)\s*\|(.+?)\|(.+?)\|", requirements, re.M)
    concrete = [row for row in req_rows if "<" not in "".join(row)]
    check(bool(concrete), "requirements_present", "no completed REQ-NN row found")
    for req_id, requirement, acceptance in concrete:
        check(
            bool(requirement.strip()) and bool(acceptance.strip()),
            "requirement_testable",
            f"{req_id} lacks a requirement or acceptance statement",
        )
    check(
        not re.search(r"\b(TBD|TODO|as appropriate|etc\.?|and so on)\b", requirements, re.I),
        "no_unresolved_placeholders",
        "requirements contain unresolved placeholder language",
    )

    architecture = _safe_read(artifact / "ARCHITECTURE.md")
    module_ids = set(_modules(artifact))
    check(bool(module_ids), "module_specs_present", "no module specifications found")
    for module_id, data in _modules(artifact).items():
        status = str(data.get("status", ""))
        check(status in VALID_STATUSES, "module_status", f"{module_id}: invalid status {status!r}")
        check(bool(data.get("id")), "module_id", f"{module_id}: frontmatter id is missing")
        for dep in data.get("depends_on", []):
            check(dep in module_ids, "dependency_exists", f"{module_id}: unknown dependency {dep}")
        body = _safe_read(Path(str(data["_path"])))
        for heading in ("Responsibility", "Boundary", "Contract", "Definition of done"):
            check(
                bool(re.search(rf"^##\s+{re.escape(heading)}\s*$", body, re.M | re.I)),
                "module_section",
                f"{module_id}: missing section {heading}",
            )
        check(
            module_id in architecture,
            "architecture_module_coverage",
            f"{module_id}: absent from ARCHITECTURE.md",
        )

    invariants = _safe_read(artifact / "INVARIANTS.md")
    inv_rows = re.findall(r"^\|\s*(INV-\d+)\s*\|(.+?)\|(.+?)\|(.+?)\|", invariants, re.M)
    concrete_inv = [row for row in inv_rows if "<" not in "".join(row)]
    for inv_id, statement, spanned, test in concrete_inv:
        check(bool(statement.strip()), "invariant_statement", f"{inv_id}: statement missing")
        check("," in spanned or "+" in spanned, "invariant_spans_boundary",
              f"{inv_id}: must name at least two modules")
        check("test" in test.lower(), "invariant_test_owned", f"{inv_id}: owning test missing")

    checks += 1
    if not concrete_inv and "No cross-module invariants" not in invariants:
        findings.append({
            "guard": "invariants_dispositioned",
            "detail": "record at least one invariant or state 'No cross-module invariants'",
        })

    return {
        "ok": not findings,
        "project": config.get("project", {}).get("name", "unknown"),
        "counts": {
            "requirements": len(concrete),
            "modules": len(module_ids),
            "invariants": len(concrete_inv),
            "checks": checks,
            "findings": len(findings),
        },
        "findings": findings,
    }


def _safe_read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def cmd_validate(args: argparse.Namespace) -> int:
    _, artifact = _resolve(args.project_root, args.artifact_root)
    try:
        config = _load_project(artifact)
    except ContextError as exc:
        return _context_error(exc, args.json)
    report = _validate(artifact, config)
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        counts = report["counts"]
        print(
            f"Validation: requirements={counts['requirements']} "
            f"modules={counts['modules']} invariants={counts['invariants']} "
            f"checks={counts['checks']}"
        )
        if report["ok"]:
            print("PASS")
        else:
            print(f"FAIL — {counts['findings']} finding(s)")
            for finding in report["findings"]:
                print(f"  x {finding['guard']}: {finding['detail']}")
    return 0 if report["ok"] else 1


def _status(artifact: Path, config: dict) -> dict:
    modules = _modules(artifact)
    by_status: dict[str, int] = {}
    for data in modules.values():
        status = str(data.get("status", "invalid"))
        by_status[status] = by_status.get(status, 0) + 1
    return {
        "project": config.get("project", {}).get("name", "unknown"),
        "artifact_root": str(artifact),
        "modules": {"total": len(modules), "by_status": by_status},
        "policy_hooks": config.get("policy_hooks", {}),
    }


def cmd_status(args: argparse.Namespace) -> int:
    _, artifact = _resolve(args.project_root, args.artifact_root)
    try:
        config = _load_project(artifact)
    except ContextError as exc:
        return _context_error(exc, args.json)
    status = _status(artifact, config)
    if args.json:
        print(json.dumps(status, indent=2))
    else:
        print(f"{status['project']} — {status['modules']['total']} module(s)")
        for name, count in sorted(status["modules"]["by_status"].items()):
            print(f"  {name}: {count}")
    return 0


def cmd_next(args: argparse.Namespace) -> int:
    _, artifact = _resolve(args.project_root, args.artifact_root)
    try:
        _load_project(artifact)
    except ContextError as exc:
        return _context_error(exc, args.json)
    modules = _modules(artifact)
    complete = {name for name, data in modules.items() if data.get("status") == "complete"}
    ready = []
    blocked: dict[str, list[str]] = {}
    for name, data in modules.items():
        if data.get("status") not in {"planned", "ready"}:
            continue
        missing = [dep for dep in data.get("depends_on", []) if dep not in complete]
        if missing:
            blocked[name] = missing
        else:
            ready.append(name)
    payload: dict[str, object]
    if ready:
        payload = {"module": sorted(ready)[0], "ready": sorted(ready), "blocked": blocked}
        code = 0
    else:
        payload = {"module": None, "ready": [], "blocked": blocked}
        code = 1
    if args.json:
        print(json.dumps(payload, indent=2))
    elif ready:
        print(sorted(ready)[0])
    else:
        print("No module is ready.")
        for name, missing in blocked.items():
            print(f"  {name}: waiting on {', '.join(missing)}")
    return code


def cmd_record_review(args: argparse.Namespace) -> int:
    _, artifact = _resolve(args.project_root, args.artifact_root)
    try:
        _load_project(artifact)
    except ContextError as exc:
        return _context_error(exc, False)
    if args.module not in _modules(artifact):
        print(f"unknown module: {args.module}", file=sys.stderr)
        return 2
    path = artifact / "reviews.json"
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        state = {"schema_version": 1, "modules": {}}
    review = {
        "recorded_at": _now(),
        "reviewer": args.reviewer,
        "verdict": args.verdict,
        "conditions": args.condition,
        "evidence": args.evidence,
        "independent_context": not args.non_independent,
    }
    state.setdefault("modules", {}).setdefault(args.module, []).append(review)
    path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    print(f"Recorded {args.verdict} review for {args.module}")
    return 0


def cmd_add_module(args: argparse.Namespace) -> int:
    _, artifact = _resolve(args.project_root, args.artifact_root)
    try:
        _load_project(artifact)
    except ContextError as exc:
        return _context_error(exc, False)
    module_id = _slugify(args.id)
    path = artifact / "modules" / f"{module_id}.md"
    if path.exists():
        print(f"module already exists: {path}", file=sys.stderr)
        return 2
    dependencies = ", ".join(args.depends_on) if args.depends_on else "none"
    requirements = "\n".join(f"- {req}" for req in args.requirement) or "- <REQ-NN>"
    text = _template(
        "module-spec.md",
        {
            "MODULE_ID": module_id,
            "RESPONSIBILITY": args.responsibility,
            "DEPENDENCIES": dependencies,
            "REQUIREMENTS": requirements,
        },
    )
    path.write_text(text, encoding="utf-8")
    print(f"Created module specification {path}")
    return 0


def _replace_frontmatter_value(text: str, key: str, value: str) -> str:
    if not text.startswith("---\n") or text.count("---\n") < 2:
        raise ContextError("module specification has no valid frontmatter")
    head, frontmatter, body = text.split("---\n", 2)
    del head
    pattern = re.compile(rf"^{re.escape(key)}\s*:.*$", re.M)
    if not pattern.search(frontmatter):
        raise ContextError(f"module frontmatter lacks {key}")
    frontmatter = pattern.sub(f"{key}: {value}", frontmatter, count=1)
    return f"---\n{frontmatter}---\n{body}"


def cmd_set_status(args: argparse.Namespace) -> int:
    _, artifact = _resolve(args.project_root, args.artifact_root)
    try:
        _load_project(artifact)
    except ContextError as exc:
        return _context_error(exc, False)
    modules = _modules(artifact)
    if args.module not in modules:
        print(f"unknown module: {args.module}", file=sys.stderr)
        return 2
    current = str(modules[args.module].get("status", ""))
    if args.status not in STATUS_TRANSITIONS.get(current, set()):
        print(f"invalid transition: {current} -> {args.status}", file=sys.stderr)
        return 2
    path = Path(str(modules[args.module]["_path"]))
    try:
        updated = _replace_frontmatter_value(
            path.read_text(encoding="utf-8"), "status", args.status
        )
    except (OSError, ContextError) as exc:
        return _context_error(exc, False)
    path.write_text(updated, encoding="utf-8")
    print(f"Updated {args.module}: {current} -> {args.status}")
    return 0


def _context_error(exc: Exception, json_output: bool) -> int:
    if json_output:
        print(json.dumps({"ok": False, "error": str(exc), "exit": 2}))
    else:
        print(f"CONTEXT ERROR: {exc}", file=sys.stderr)
    return 2


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(prog="agentic-sdlc")
    sub = root.add_subparsers(dest="command", required=True)

    def paths(command: argparse.ArgumentParser) -> None:
        command.add_argument("--project-root", default=".")
        command.add_argument("--artifact-root")

    init = sub.add_parser("init", help="initialize a portable SDLC artifact set")
    paths(init)
    init.add_argument("--name", required=True)
    init.add_argument("--slug")
    init.add_argument("--coordination", choices=("standalone", "delegated"), default="standalone")
    init.add_argument("--force", action="store_true")
    init.set_defaults(func=cmd_init)

    validate = sub.add_parser("validate", help="validate lifecycle artifacts")
    paths(validate)
    validate.add_argument("--json", action="store_true")
    validate.set_defaults(func=cmd_validate)

    status = sub.add_parser("status", help="summarize project lifecycle state")
    paths(status)
    status.add_argument("--json", action="store_true")
    status.set_defaults(func=cmd_status)

    next_command = sub.add_parser("next", help="select the next dependency-ready module")
    paths(next_command)
    next_command.add_argument("--json", action="store_true")
    next_command.set_defaults(func=cmd_next)

    review = sub.add_parser("record-review", help="append an independent review verdict")
    paths(review)
    review.add_argument("--module", required=True)
    review.add_argument("--verdict", required=True, choices=sorted(VALID_VERDICTS))
    review.add_argument("--reviewer", required=True)
    review.add_argument("--condition", action="append", default=[])
    review.add_argument("--evidence")
    review.add_argument("--non-independent", action="store_true")
    review.set_defaults(func=cmd_record_review)

    add_module = sub.add_parser("add-module", help="create a portable module specification")
    paths(add_module)
    add_module.add_argument("--id", required=True)
    add_module.add_argument("--responsibility", required=True)
    add_module.add_argument("--depends-on", action="append", default=[])
    add_module.add_argument("--requirement", action="append", default=[])
    add_module.set_defaults(func=cmd_add_module)

    set_status = sub.add_parser("set-status", help="advance a module through valid states")
    paths(set_status)
    set_status.add_argument("--module", required=True)
    set_status.add_argument("--status", required=True, choices=sorted(VALID_STATUSES))
    set_status.set_defaults(func=cmd_set_status)
    return root


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
