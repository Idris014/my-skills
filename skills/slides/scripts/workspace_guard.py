#!/usr/bin/env python3
"""Create and audit a single-root workspace for Slides production."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sys


DIRECTORIES = (
    "00_inventory",
    "10_script",
    "20_research",
    "30_assets/searched",
    "30_assets/generated",
    "30_assets/selected",
    "40_layout",
    "50_pptx",
    "55_demos",
    "60_renders",
    "70_qa",
    "80_keynote",
    "90_final-staging",
    "logs",
    "tmp",
)


def safe_slug(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", value.strip()).strip("-.")
    return slug or "slides"


def is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def project_snapshot(project: Path, excluded: tuple[Path, ...]) -> dict[str, dict[str, int]]:
    snapshot: dict[str, dict[str, int]] = {}
    for path in project.rglob("*"):
        resolved = path.resolve()
        if any(is_relative_to(resolved, item) for item in excluded):
            continue
        if ".git" in path.parts or not path.is_file():
            continue
        stat = path.stat()
        snapshot[str(path.relative_to(project))] = {
            "size": stat.st_size,
            "mtime_ns": stat.st_mtime_ns,
        }
    return snapshot


def init_workspace(args: argparse.Namespace) -> int:
    project = args.project_dir.expanduser().resolve()
    if not project.is_dir():
        raise SystemExit(f"Project directory does not exist: {project}")

    build_parent = (
        args.build_parent.expanduser().resolve()
        if args.build_parent
        else project / ".slides-work"
    )
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    root = build_parent / f"{safe_slug(args.deck_slug)}-{timestamp}"
    root.mkdir(parents=True, exist_ok=False)
    for relative in DIRECTORIES:
        (root / relative).mkdir(parents=True, exist_ok=False)

    excluded = (project / ".git", root)
    manifest = {
        "schema_version": 1,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "project_dir": str(project),
        "build_parent": str(build_parent),
        "job_root": str(root),
        "directories": {item: str(root / item) for item in DIRECTORIES},
        "project_baseline": project_snapshot(project, excluded),
    }
    manifest_path = root / "00_inventory" / "workspace-manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "job_root": str(root),
                "manifest": str(manifest_path),
                "tmp_dir": str(root / "tmp"),
                "final_staging": str(root / "90_final-staging"),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


def audit_workspace(args: argparse.Namespace) -> int:
    root = args.build_root.expanduser().resolve()
    manifest_path = root / "00_inventory" / "workspace-manifest.json"
    if not manifest_path.is_file():
        raise SystemExit(f"Workspace manifest does not exist: {manifest_path}")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    project = Path(manifest["project_dir"]).resolve()
    baseline = manifest["project_baseline"]
    allowed = {path.expanduser().resolve() for path in args.allow_final}
    excluded = (project / ".git", root)
    current = project_snapshot(project, excluded)

    unexpected: list[dict[str, str]] = []
    for relative, metadata in current.items():
        path = (project / relative).resolve()
        if path in allowed:
            continue
        previous = baseline.get(relative)
        if previous is None:
            unexpected.append({"path": str(path), "change": "created"})
        elif previous != metadata:
            unexpected.append({"path": str(path), "change": "modified"})

    missing_allowed = sorted(str(path) for path in allowed if not path.exists())
    result = {
        "job_root": str(root),
        "unexpected_outside_archive": unexpected,
        "missing_allowed_finals": missing_allowed,
        "passed": not unexpected and not missing_allowed,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["passed"] else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init")
    init_parser.add_argument("--project-dir", type=Path, required=True)
    init_parser.add_argument("--deck-slug", required=True)
    init_parser.add_argument("--build-parent", type=Path)
    init_parser.set_defaults(handler=init_workspace)

    audit_parser = subparsers.add_parser("audit")
    audit_parser.add_argument("--build-root", type=Path, required=True)
    audit_parser.add_argument("--allow-final", type=Path, action="append", default=[])
    audit_parser.set_defaults(handler=audit_workspace)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    return args.handler(args)


if __name__ == "__main__":
    sys.exit(main())
