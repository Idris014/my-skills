#!/usr/bin/env python3
"""Inspect a binary glTF (.glb) without external dependencies."""

from __future__ import annotations

import argparse
import json
import struct
import sys
from pathlib import Path


JSON_CHUNK = 0x4E4F534A


def read_glb(path: Path) -> dict:
    with path.open("rb") as stream:
        header = stream.read(12)
        if len(header) != 12:
            raise ValueError("File is too short to be a GLB")
        magic, version, declared_length = struct.unpack("<4sII", header)
        if magic != b"glTF":
            raise ValueError(f"Unexpected magic: {magic!r}")

        document = None
        chunks = []
        while stream.tell() < declared_length:
            chunk_header = stream.read(8)
            if not chunk_header:
                break
            if len(chunk_header) != 8:
                raise ValueError("Truncated GLB chunk header")
            chunk_length, chunk_type = struct.unpack("<II", chunk_header)
            payload = stream.read(chunk_length)
            if len(payload) != chunk_length:
                raise ValueError("Truncated GLB chunk")
            chunks.append({"type": chunk_type, "length": chunk_length})
            if chunk_type == JSON_CHUNK:
                document = json.loads(payload.decode("utf-8").rstrip("\x00 \t\r\n"))

    if document is None:
        raise ValueError("GLB has no JSON chunk")

    position_accessors = []
    accessors = document.get("accessors", [])
    for mesh_index, mesh in enumerate(document.get("meshes", [])):
        for primitive_index, primitive in enumerate(mesh.get("primitives", [])):
            accessor_index = primitive.get("attributes", {}).get("POSITION")
            if accessor_index is None or accessor_index >= len(accessors):
                continue
            accessor = accessors[accessor_index]
            position_accessors.append(
                {
                    "mesh": mesh_index,
                    "primitive": primitive_index,
                    "accessor": accessor_index,
                    "count": accessor.get("count"),
                    "min": accessor.get("min"),
                    "max": accessor.get("max"),
                }
            )

    images = document.get("images", [])
    return {
        "path": str(path.resolve()),
        "bytes": path.stat().st_size,
        "magic": magic.decode("ascii"),
        "version": version,
        "declared_length": declared_length,
        "nodes": len(document.get("nodes", [])),
        "meshes": len(document.get("meshes", [])),
        "mesh_primitives": sum(
            len(mesh.get("primitives", [])) for mesh in document.get("meshes", [])
        ),
        "materials": len(document.get("materials", [])),
        "material_names": [
            material.get("name") for material in document.get("materials", [])
        ],
        "textures": len(document.get("textures", [])),
        "images": len(images),
        "embedded_images": sum(1 for image in images if "bufferView" in image),
        "external_images": [
            image.get("uri") for image in images if image.get("uri")
        ],
        "image_mime_types": [image.get("mimeType") for image in images],
        "skins": len(document.get("skins", [])),
        "animations": len(document.get("animations", [])),
        "extensions_used": document.get("extensionsUsed", []),
        "position_accessors": position_accessors,
        "chunks": chunks,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("glb", type=Path)
    parser.add_argument("--expect-version", type=int, default=2)
    parser.add_argument("--expect-meshes", type=int)
    parser.add_argument("--min-embedded-images", type=int)
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()

    try:
        report = read_glb(args.glb)
    except Exception as exc:
        print(f"GLB inspection failed: {exc}", file=sys.stderr)
        return 2

    failures = []
    if report["version"] != args.expect_version:
        failures.append(
            f"version {report['version']} != expected {args.expect_version}"
        )
    if args.expect_meshes is not None and report["meshes"] != args.expect_meshes:
        failures.append(
            f"meshes {report['meshes']} != expected {args.expect_meshes}"
        )
    if (
        args.min_embedded_images is not None
        and report["embedded_images"] < args.min_embedded_images
    ):
        failures.append(
            f"embedded images {report['embedded_images']} "
            f"< expected {args.min_embedded_images}"
        )

    report["status"] = "failed" if failures else "passed"
    report["failures"] = failures
    payload = json.dumps(report, ensure_ascii=False, indent=2)
    print(payload)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(payload + "\n", encoding="utf-8")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
