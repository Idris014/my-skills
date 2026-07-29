#!/usr/bin/env python3
"""Classify display color and printable face-color data in GLB and 3MF files."""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
import zipfile
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree as ET


CLASSIFICATIONS = {
    "texture_only_glb",
    "vertex_color_glb",
    "material_regions_glb",
    "uniform_or_uncolored_glb",
    "face_painted_3mf",
    "unpainted_3mf",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def inspect_glb(path: Path) -> dict:
    data = path.read_bytes()
    if len(data) < 20 or data[:4] != b"glTF":
        raise ValueError("not a valid binary glTF file")

    version = struct.unpack_from("<I", data, 4)[0]
    declared_length = struct.unpack_from("<I", data, 8)[0]
    json_length = struct.unpack_from("<I", data, 12)[0]
    json_type = struct.unpack_from("<I", data, 16)[0]
    if json_type != 0x4E4F534A:
        raise ValueError("first GLB chunk is not JSON")
    document = json.loads(
        data[20 : 20 + json_length].decode("utf-8").rstrip("\x00 ")
    )

    primitives = [
        primitive
        for mesh in document.get("meshes", [])
        for primitive in mesh.get("primitives", [])
    ]
    material_indices = [
        primitive.get("material")
        for primitive in primitives
        if primitive.get("material") is not None
    ]
    used_materials = sorted(set(material_indices))
    has_vertex_color = any(
        "COLOR_0" in primitive.get("attributes", {}) for primitive in primitives
    )
    base_color_texture_materials = 0
    for material in document.get("materials", []):
        pbr = material.get("pbrMetallicRoughness", {})
        if "baseColorTexture" in pbr:
            base_color_texture_materials += 1

    if len(used_materials) > 1:
        classification = "material_regions_glb"
    elif has_vertex_color:
        classification = "vertex_color_glb"
    elif base_color_texture_materials:
        classification = "texture_only_glb"
    else:
        classification = "uniform_or_uncolored_glb"

    images = document.get("images", [])
    return {
        "format": "glb",
        "classification": classification,
        "display_color_present": bool(
            base_color_texture_materials
            or has_vertex_color
            or document.get("materials")
        ),
        "bambu_face_paint_present": False,
        "requires_texture_to_color_for_face_paint": (
            classification == "texture_only_glb"
        ),
        "glb_version": version,
        "declared_length": declared_length,
        "actual_length": len(data),
        "nodes": len(document.get("nodes", [])),
        "meshes": len(document.get("meshes", [])),
        "primitives": len(primitives),
        "primitive_attributes": [
            sorted(primitive.get("attributes", {}).keys())
            for primitive in primitives
        ],
        "materials": len(document.get("materials", [])),
        "material_names": [
            material.get("name") for material in document.get("materials", [])
        ],
        "used_material_indices": used_materials,
        "base_color_texture_materials": base_color_texture_materials,
        "textures": len(document.get("textures", [])),
        "images": len(images),
        "embedded_images": sum(
            1 for image in images if "bufferView" in image or "uri" not in image
        ),
        "has_COLOR_0": has_vertex_color,
        "extensions_used": document.get("extensionsUsed", []),
    }


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def inspect_3mf(path: Path) -> dict:
    vertices = 0
    triangles = 0
    paint_counts: Counter[str] = Counter()
    p1_counts: Counter[str] = Counter()
    pid_counts: Counter[str] = Counter()
    model_members: list[str] = []

    with zipfile.ZipFile(path) as archive:
        bad_member = archive.testzip()
        for member in sorted(archive.namelist()):
            if not member.lower().endswith(".model"):
                continue
            model_members.append(member)
            with archive.open(member) as handle:
                for _, element in ET.iterparse(handle, events=("end",)):
                    tag = local_name(element.tag)
                    if tag == "vertex":
                        vertices += 1
                    elif tag == "triangle":
                        triangles += 1
                        paint_counts[element.attrib.get("paint_color", "none")] += 1
                        p1_counts[element.attrib.get("p1", "none")] += 1
                        pid_counts[element.attrib.get("pid", "none")] += 1
                    element.clear()

    painted_triangles = triangles - paint_counts.get("none", 0)
    classification = (
        "face_painted_3mf" if painted_triangles else "unpainted_3mf"
    )
    return {
        "format": "3mf",
        "classification": classification,
        "display_color_present": bool(painted_triangles),
        "bambu_face_paint_present": bool(painted_triangles),
        "zip_integrity": "passed" if bad_member is None else "failed",
        "bad_member": bad_member,
        "model_members": model_members,
        "vertices": vertices,
        "triangles": triangles,
        "painted_triangles": painted_triangles,
        "unpainted_triangles": paint_counts.get("none", 0),
        "full_face_paint_coverage": bool(triangles)
        and painted_triangles == triangles,
        "paint_color_counts": dict(sorted(paint_counts.items())),
        "p1_counts": dict(sorted(p1_counts.items())),
        "pid_counts": dict(sorted(pid_counts.items())),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("asset")
    parser.add_argument(
        "--expect-classification", choices=sorted(CLASSIFICATIONS)
    )
    parser.add_argument("--expected-painted-triangles", type=int)
    parser.add_argument("--require-full-paint", action="store_true")
    parser.add_argument("--json-out")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    path = Path(args.asset).resolve()
    failures: list[str] = []

    if path.suffix.lower() == ".glb":
        details = inspect_glb(path)
    elif path.suffix.lower() == ".3mf":
        details = inspect_3mf(path)
    else:
        raise SystemExit("supported formats: .glb and .3mf")

    if (
        args.expect_classification
        and details["classification"] != args.expect_classification
    ):
        failures.append(
            "classification mismatch: "
            f"expected {args.expect_classification}, "
            f"got {details['classification']}"
        )

    if args.expected_painted_triangles is not None:
        actual = details.get("painted_triangles", 0)
        if actual != args.expected_painted_triangles:
            failures.append(
                "painted triangle mismatch: "
                f"expected {args.expected_painted_triangles}, got {actual}"
            )

    if args.require_full_paint and not details.get(
        "full_face_paint_coverage", False
    ):
        failures.append("full face-paint coverage is required")

    report = {
        "path": str(path),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
        **details,
        "status": "passed" if not failures else "failed",
        "failures": failures,
    }
    output = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    print(output, end="")
    if args.json_out:
        json_path = Path(args.json_out).resolve()
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(output, encoding="utf-8")
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
