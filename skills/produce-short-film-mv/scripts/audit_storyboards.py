#!/usr/bin/env python3
"""Audit storyboard PNG naming, dimensions, versions, and START/END coverage."""

from __future__ import annotations

import argparse
import csv
import json
import re
import struct
import sys
from collections import defaultdict
from pathlib import Path


NAME_RE = re.compile(
    r"^(?P<episode>EP\d{2})-(?P<scene>SC\d{2})-(?P<shot>SH\d{3})"
    r"_KF-(?P<frame>START|END|MID\d+)(?:_(?P<tag>[A-Za-z0-9-]+))?"
    r"_v(?P<version>\d+)\.png$",
    re.IGNORECASE,
)
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def png_dimensions(path: Path) -> tuple[int, int]:
    with path.open("rb") as handle:
        header = handle.read(24)
    if len(header) < 24 or header[:8] != PNG_SIGNATURE or header[12:16] != b"IHDR":
        raise ValueError("not a valid PNG with an IHDR header")
    return struct.unpack(">II", header[16:24])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path, help="Folder to scan recursively")
    parser.add_argument("--expected-width", type=int, help="Expected width from the project manifest")
    parser.add_argument("--expected-height", type=int, help="Expected height from the project manifest")
    parser.add_argument(
        "--expected-csv",
        type=Path,
        help="Optional frame-slot/lock manifest CSV to reconcile against physical files",
    )
    parser.add_argument("--prefix", default="", help="Only inspect filenames beginning with this value")
    parser.add_argument("--strict-names", action="store_true", help="Treat nonconforming PNG names as errors")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of Markdown")
    return parser.parse_args()


def first_value(row: dict[str, str], names: tuple[str, ...]) -> str:
    for name in names:
        value = row.get(name, "").strip()
        if value:
            return value
    return ""


def load_expected_manifest(path: Path, prefix: str) -> tuple[dict[str, dict[str, str]], list[str]]:
    manifest = path.expanduser().resolve()
    if not manifest.is_file():
        raise FileNotFoundError(f"expected CSV does not exist: {manifest}")

    rows: dict[str, dict[str, str]] = {}
    duplicates: list[str] = []
    with manifest.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError(f"expected CSV has no header: {manifest}")
        for row in reader:
            slot = first_value(row, ("帧位编号", "frame_slot", "FRAME_SLOT", "frame_id", "FRAME_ID"))
            if not slot:
                filename = first_value(
                    row,
                    ("预期文件名", "expected_filename", "EXPECTED_FILENAME", "锁定文件名", "adopted_file"),
                )
                match = NAME_RE.match(Path(filename).name) if filename else None
                if match:
                    data = match.groupdict()
                    slot = (
                        f"{data['episode'].upper()}-{data['scene'].upper()}-{data['shot'].upper()}"
                        f"_KF-{data['frame'].upper()}"
                    )
            slot = slot.upper()
            if not slot or (prefix and not slot.startswith(prefix.upper())):
                continue
            if slot in rows:
                duplicates.append(slot)
            rows[slot] = row
    return rows, sorted(set(duplicates))


def audit(args: argparse.Namespace) -> dict[str, object]:
    root = args.root.expanduser().resolve()
    if not root.is_dir():
        raise FileNotFoundError(f"root folder does not exist: {root}")
    if (args.expected_width is None) != (args.expected_height is None):
        raise ValueError("provide both --expected-width and --expected-height, or neither")

    files = sorted(
        path for path in root.rglob("*.png") if not args.prefix or path.name.startswith(args.prefix)
    )
    invalid_names: list[str] = []
    unreadable: list[dict[str, str]] = []
    dimension_mismatches: list[dict[str, object]] = []
    records: list[dict[str, object]] = []
    groups: dict[str, dict[str, list[dict[str, object]]]] = defaultdict(
        lambda: defaultdict(list)
    )

    for path in files:
        relative = str(path.relative_to(root))
        match = NAME_RE.match(path.name)
        if not match:
            invalid_names.append(relative)
            continue
        try:
            width, height = png_dimensions(path)
        except (OSError, ValueError) as exc:
            unreadable.append({"file": relative, "error": str(exc)})
            continue

        data = match.groupdict()
        shot_id = f"{data['episode'].upper()}-{data['scene'].upper()}-{data['shot'].upper()}"
        frame = data["frame"].upper()
        record = {
            "file": relative,
            "shot_id": shot_id,
            "frame": frame,
            "tag": data.get("tag") or "",
            "version": int(data["version"]),
            "width": width,
            "height": height,
        }
        records.append(record)
        groups[shot_id][frame].append(record)
        if args.expected_width is not None and (width, height) != (
            args.expected_width,
            args.expected_height,
        ):
            dimension_mismatches.append(
                {
                    "file": relative,
                    "actual": f"{width}x{height}",
                    "expected": f"{args.expected_width}x{args.expected_height}",
                }
            )

    end_without_start: list[str] = []
    start_without_end: list[str] = []
    latest: list[dict[str, object]] = []
    for shot_id in sorted(groups):
        frames = groups[shot_id]
        if "END" in frames and "START" not in frames:
            end_without_start.append(shot_id)
        if "START" in frames and "END" not in frames:
            start_without_end.append(shot_id)
        for frame in sorted(frames):
            newest = max(frames[frame], key=lambda item: int(item["version"]))
            latest.append(newest)

    expected_rows: dict[str, dict[str, str]] = {}
    duplicate_expected_slots: list[str] = []
    missing_expected_slots: list[str] = []
    unexpected_physical_slots: list[str] = []
    manifest_pending_but_file_present: list[str] = []
    manifest_adopted_but_missing: list[str] = []
    locked_filename_missing: list[dict[str, str]] = []
    actual_slots = {
        f"{record['shot_id']}_KF-{record['frame']}" for record in records
    }

    if args.expected_csv:
        expected_rows, duplicate_expected_slots = load_expected_manifest(
            args.expected_csv, args.prefix
        )
        expected_slots = set(expected_rows)
        missing_expected_slots = sorted(expected_slots - actual_slots)
        unexpected_physical_slots = sorted(actual_slots - expected_slots)

        for slot, row in expected_rows.items():
            status = first_value(
                row,
                ("第四阶段结论", "status", "STATUS", "lock_status", "adopted_status"),
            ).upper()
            locked_name = first_value(
                row,
                ("锁定文件名", "adopted_file", "ADOPTED_FILE", "locked_file", "LOCKED_FILE"),
            )
            if slot in actual_slots and status in {"", "PENDING", "SELF-QA", "REVISE"}:
                manifest_pending_but_file_present.append(slot)
            if slot not in actual_slots and status in {"PASS", "REVIEWED", "LOCKED", "ADOPTED"}:
                manifest_adopted_but_missing.append(slot)
            if locked_name and not (root / Path(locked_name).name).is_file():
                locked_filename_missing.append(
                    {"slot": slot, "locked_file": locked_name}
                )

    errors = (
        len(unreadable)
        + len(dimension_mismatches)
        + len(end_without_start)
        + len(missing_expected_slots)
        + len(duplicate_expected_slots)
        + len(manifest_adopted_but_missing)
        + len(locked_filename_missing)
    )
    if args.strict_names:
        errors += len(invalid_names)

    return {
        "root": str(root),
        "png_files_seen": len(files),
        "valid_storyboard_files": len(records),
        "unique_shots": len(groups),
        "expected_csv": str(args.expected_csv.expanduser().resolve()) if args.expected_csv else "",
        "expected_frame_slots": len(expected_rows),
        "highest_version_frames_not_adoption": latest,
        "invalid_names": invalid_names,
        "unreadable_pngs": unreadable,
        "dimension_mismatches": dimension_mismatches,
        "end_without_start": end_without_start,
        "start_without_end_info": start_without_end,
        "missing_expected_slots": missing_expected_slots,
        "unexpected_physical_slots_info": unexpected_physical_slots,
        "duplicate_expected_slots": duplicate_expected_slots,
        "manifest_pending_but_file_present_info": manifest_pending_but_file_present,
        "manifest_adopted_but_missing": manifest_adopted_but_missing,
        "locked_filename_missing": locked_filename_missing,
        "error_count": errors,
    }


def print_markdown(result: dict[str, object], strict_names: bool) -> None:
    print("# Storyboard audit")
    print(f"- Root: `{result['root']}`")
    print(f"- PNG files seen: {result['png_files_seen']}")
    print(f"- Valid storyboard files: {result['valid_storyboard_files']}")
    print(f"- Unique shots: {result['unique_shots']}")
    if result["expected_csv"]:
        print(f"- Expected CSV: `{result['expected_csv']}`")
        print(f"- Expected frame slots: {result['expected_frame_slots']}")
    print(f"- Errors: {result['error_count']}")
    print("- Note: highest version is not proof of adoption; reconcile the lock/adopted manifest.")

    sections = [
        ("Dimension mismatches", result["dimension_mismatches"]),
        ("Unreadable PNGs", result["unreadable_pngs"]),
        ("END without START", result["end_without_start"]),
        ("Missing expected frame slots", result["missing_expected_slots"]),
        ("Duplicate expected frame slots", result["duplicate_expected_slots"]),
        ("Adopted/locked manifest rows missing physical frames", result["manifest_adopted_but_missing"]),
        ("Locked filenames missing from root", result["locked_filename_missing"]),
        ("Unexpected physical slots (informational)", result["unexpected_physical_slots_info"]),
        ("Physical frames with pending manifest status (informational)", result["manifest_pending_but_file_present_info"]),
        ("Nonconforming names" + (" (errors)" if strict_names else " (warnings)"), result["invalid_names"]),
        ("START without END (informational)", result["start_without_end_info"]),
    ]
    for title, items in sections:
        print(f"\n## {title}")
        if not items:
            print("- None")
            continue
        for item in items[:20]:
            if isinstance(item, dict):
                print("- " + ", ".join(f"{key}: `{value}`" for key, value in item.items()))
            else:
                print(f"- `{item}`")
        if len(items) > 20:
            print(f"- … {len(items) - 20} more; use `--json` for the full list")


def main() -> int:
    args = parse_args()
    try:
        result = audit(args)
    except (OSError, ValueError) as exc:
        print(f"audit failed: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print_markdown(result, args.strict_names)
    return 1 if int(result["error_count"]) else 0


if __name__ == "__main__":
    raise SystemExit(main())
