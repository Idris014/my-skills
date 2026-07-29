#!/usr/bin/env python3
"""Copy accepted renders into a versioned archive and create a manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import struct
from datetime import datetime, timezone
from pathlib import Path


IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def png_size(path: Path):
    with path.open("rb") as stream:
        header = stream.read(24)
    if header[:8] == b"\x89PNG\r\n\x1a\n" and len(header) >= 24:
        return struct.unpack(">II", header[16:24])
    return None


def jpeg_size(path: Path):
    with path.open("rb") as stream:
        if stream.read(2) != b"\xff\xd8":
            return None
        while True:
            marker_start = stream.read(1)
            if not marker_start:
                return None
            if marker_start != b"\xff":
                continue
            marker = stream.read(1)
            while marker == b"\xff":
                marker = stream.read(1)
            if marker in {b"\xd8", b"\xd9"}:
                continue
            length_bytes = stream.read(2)
            if len(length_bytes) != 2:
                return None
            length = struct.unpack(">H", length_bytes)[0]
            if marker and marker[0] in {
                0xC0,
                0xC1,
                0xC2,
                0xC3,
                0xC5,
                0xC6,
                0xC7,
                0xC9,
                0xCA,
                0xCB,
                0xCD,
                0xCE,
                0xCF,
            }:
                data = stream.read(5)
                if len(data) == 5:
                    height, width = struct.unpack(">HH", data[1:5])
                    return width, height
                return None
            stream.seek(length - 2, 1)


def image_size(path: Path):
    if path.suffix.lower() == ".png":
        return png_size(path)
    if path.suffix.lower() in {".jpg", ".jpeg"}:
        return jpeg_size(path)
    return None


def classify(name: str) -> str:
    value = name.lower()
    if "standing" in value or "pose" in value:
        return "ai-generated character pose reference"
    if "front" in value or "3q" in value:
        return "front three-quarter assembly"
    if "side" in value or "clearance" in value:
        return "side support or clearance validation"
    if "underside" in value or "exploded" in value or "magnetic" in value:
        return "connection or magnetic interface"
    if "plan" in value or "top" in value:
        return "base outline or plan"
    if "audit" in value or "source" in value:
        return "source audit"
    return "render"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-dir", required=True, type=Path)
    parser.add_argument("--archive-root", required=True, type=Path)
    parser.add_argument("--version", required=True)
    parser.add_argument("--replace", action="store_true")
    args = parser.parse_args()

    source = args.source_dir.resolve()
    destination = args.archive_root.resolve() / args.version
    images_dir = destination / "images"
    if destination.exists():
        if not args.replace:
            raise SystemExit(
                f"Archive already exists: {destination}; use --replace explicitly"
            )
        shutil.rmtree(destination)

    files = sorted(
        path
        for path in source.rglob("*")
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
    )
    if not files:
        raise SystemExit(f"No supported images found in {source}")

    images_dir.mkdir(parents=True)
    created_at = datetime.now(timezone.utc).isoformat()
    records = []
    for path in files:
        relative = path.relative_to(source)
        target = images_dir / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
        size = image_size(target)
        records.append(
            {
                "filename": str(relative),
                "role": classify(path.name),
                "width": size[0] if size else None,
                "height": size[1] if size else None,
                "bytes": target.stat().st_size,
                "sha256": sha256(target),
                "source": str(path.resolve()),
            }
        )

    manifest = {
        "version": args.version,
        "created_at": created_at,
        "source_directory": str(source),
        "copy_mode": "copy",
        "images": records,
    }
    (destination / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    lines = [
        f"# Render archive: {args.version}",
        "",
        f"Archived {len(records)} accepted render(s) from `{source}`.",
        "",
        "| File | Role | Pixels | SHA-256 |",
        "| --- | --- | ---: | --- |",
    ]
    for record in records:
        pixels = (
            f"{record['width']} × {record['height']}"
            if record["width"] and record["height"]
            else "unknown"
        )
        lines.append(
            f"| `images/{record['filename']}` | {record['role']} | "
            f"{pixels} | `{record['sha256']}` |"
        )
    (destination / "README.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )
    print(destination)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
