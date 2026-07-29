#!/usr/bin/env python3
"""Validate printable meshes and a painted 3MF with Bambu Studio."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import zipfile
from collections import Counter
from pathlib import Path


DEFAULT_BAMBU = Path("/Applications/BambuStudio.app/Contents/MacOS/BambuStudio")
KEY_VALUE = re.compile(r"^([A-Za-z0-9_]+)\s*=\s*(.+?)\s*$")
PAINT = re.compile(rb'paint_color="([^"]+)"')


def bambu_info(executable: Path, path: Path) -> dict:
    process = subprocess.run(
        [str(executable), "--info", str(path)],
        text=True,
        capture_output=True,
        check=False,
    )
    combined = "\n".join(value for value in [process.stdout, process.stderr] if value)
    values = {}
    for line in combined.splitlines():
        match = KEY_VALUE.match(line.strip())
        if match:
            values[match.group(1)] = match.group(2)
    return {
        "path": str(path.resolve()),
        "exit_code": process.returncode,
        "values": values,
        "raw": combined,
    }


def inspect_3mf(path: Path) -> dict:
    counts = Counter()
    with zipfile.ZipFile(path, "r") as archive:
        bad_member = archive.testzip()
        object_name = "3D/Objects/object_1.model"
        if object_name not in archive.namelist():
            raise ValueError(f"Missing {object_name}")
        with archive.open(object_name, "r") as stream:
            for line in stream:
                counts.update(
                    value.decode("utf-8") for value in PAINT.findall(line)
                )
    return {
        "zip_integrity": "passed" if bad_member is None else "failed",
        "bad_member": bad_member,
        "paint_counts": dict(sorted(counts.items())),
        "painted_triangles": sum(counts.values()),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bambu", type=Path, default=DEFAULT_BAMBU)
    parser.add_argument("--mesh", action="append", type=Path, default=[])
    parser.add_argument("--three-mf", type=Path)
    parser.add_argument("--expected-painted-triangles", type=int)
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()

    if not args.bambu.exists():
        print(f"Bambu Studio executable not found: {args.bambu}", file=sys.stderr)
        return 2

    failures = []
    mesh_reports = []
    for path in args.mesh:
        report = bambu_info(args.bambu, path)
        mesh_reports.append(report)
        if report["exit_code"] != 0:
            failures.append(f"Bambu import failed: {path}")
        if (
            "manifold" in report["values"]
            and report["values"].get("manifold") != "yes"
        ):
            failures.append(f"Non-manifold mesh: {path}")

    three_mf_report = None
    if args.three_mf:
        info = bambu_info(args.bambu, args.three_mf)
        try:
            package = inspect_3mf(args.three_mf)
        except Exception as exc:
            package = {"zip_integrity": "failed", "error": str(exc)}
            failures.append(f"3MF package inspection failed: {exc}")
        three_mf_report = {"bambu": info, "package": package}
        if info["exit_code"] != 0:
            failures.append(f"Bambu import failed: {args.three_mf}")
        if "manifold" in info["values"] and info["values"].get("manifold") != "yes":
            failures.append(f"Non-manifold 3MF: {args.three_mf}")
        if package.get("zip_integrity") != "passed":
            failures.append(f"Invalid 3MF ZIP: {args.three_mf}")
        if (
            args.expected_painted_triangles is not None
            and package.get("painted_triangles")
            != args.expected_painted_triangles
        ):
            failures.append(
                f"Painted triangles {package.get('painted_triangles')} != "
                f"expected {args.expected_painted_triangles}"
            )

    report = {
        "status": "failed" if failures else "passed",
        "bambu_executable": str(args.bambu),
        "meshes": mesh_reports,
        "three_mf": three_mf_report,
        "failures": failures,
    }
    payload = json.dumps(report, ensure_ascii=False, indent=2)
    print(payload)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(payload + "\n", encoding="utf-8")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
