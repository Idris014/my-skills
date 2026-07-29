#!/usr/bin/env python3
"""Audit 3MF mesh bounds, degenerates, and edge manifoldness without a slicer."""

from __future__ import annotations

import argparse
import hashlib
import json
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

import numpy as np


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("three_mf", type=Path)
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()
    path = args.three_mf.expanduser().resolve()

    vertices: list[tuple[float, float, float]] = []
    faces: list[tuple[int, int, int]] = []
    paint_colors: list[str | None] = []
    with zipfile.ZipFile(path) as archive:
        members = [
            name
            for name in archive.namelist()
            if name.startswith("3D/Objects/") and name.endswith(".model")
        ]
        if len(members) != 1:
            raise RuntimeError(f"Expected one object model, found {members}")
        with archive.open(members[0]) as stream:
            for _, element in ET.iterparse(stream, events=("end",)):
                name = local_name(element.tag)
                if name == "vertex":
                    vertices.append(
                        (
                            float(element.attrib["x"]),
                            float(element.attrib["y"]),
                            float(element.attrib["z"]),
                        )
                    )
                elif name == "triangle":
                    faces.append(
                        (
                            int(element.attrib["v1"]),
                            int(element.attrib["v2"]),
                            int(element.attrib["v3"]),
                        )
                    )
                    paint_colors.append(element.attrib.get("paint_color"))
                element.clear()

    vertex_array = np.asarray(vertices, dtype=np.float64)
    face_array = np.asarray(faces, dtype=np.int64)
    if vertex_array.ndim != 2 or vertex_array.shape[1] != 3:
        raise RuntimeError("Invalid vertex array")
    if face_array.ndim != 2 or face_array.shape[1] != 3:
        raise RuntimeError("Invalid face array")
    if face_array.min() < 0 or face_array.max() >= len(vertex_array):
        raise RuntimeError("Triangle index outside vertex range")

    repeated_index = (
        (face_array[:, 0] == face_array[:, 1])
        | (face_array[:, 1] == face_array[:, 2])
        | (face_array[:, 2] == face_array[:, 0])
    )
    p0 = vertex_array[face_array[:, 0]]
    p1 = vertex_array[face_array[:, 1]]
    p2 = vertex_array[face_array[:, 2]]
    doubled_area = np.linalg.norm(np.cross(p1 - p0, p2 - p0), axis=1)
    zero_area = doubled_area <= 1e-12

    edges = np.concatenate(
        (
            face_array[:, [0, 1]],
            face_array[:, [1, 2]],
            face_array[:, [2, 0]],
        ),
        axis=0,
    )
    edges.sort(axis=1)
    order = np.lexsort((edges[:, 1], edges[:, 0]))
    face_ids = np.tile(np.arange(len(face_array), dtype=np.int64), 3)
    edges = edges[order]
    face_ids = face_ids[order]
    new_edge = np.ones(len(edges), dtype=bool)
    new_edge[1:] = np.any(edges[1:] != edges[:-1], axis=1)
    starts = np.flatnonzero(new_edge)
    counts = np.diff(np.append(starts, len(edges)))
    boundary_edges = int(np.count_nonzero(counts == 1))
    nonmanifold_edges = int(np.count_nonzero(counts > 2))
    unique_edges = int(len(counts))
    problematic = []
    for start, count in zip(starts, counts):
        if count == 2:
            continue
        edge = edges[start]
        incident = face_ids[start:start + count]
        problematic.append(
            {
                "vertices": edge.tolist(),
                "coordinates": vertex_array[edge].tolist(),
                "incident_face_count": int(count),
                "incident_faces": incident.tolist(),
                "paint_colors": [paint_colors[index] for index in incident],
            }
        )

    minimum = vertex_array.min(axis=0)
    maximum = vertex_array.max(axis=0)
    report = {
        "path": str(path),
        "sha256": sha256(path),
        "vertices": int(len(vertex_array)),
        "triangles": int(len(face_array)),
        "bounds_mm": {
            "min": minimum.tolist(),
            "max": maximum.tolist(),
            "size": (maximum - minimum).tolist(),
        },
        "repeated_index_triangles": int(np.count_nonzero(repeated_index)),
        "zero_area_triangles": int(np.count_nonzero(zero_area)),
        "unique_edges": unique_edges,
        "boundary_edges": boundary_edges,
        "nonmanifold_edges": nonmanifold_edges,
        "problematic_edges": problematic,
        "edge_manifold_closed": boundary_edges == 0 and nonmanifold_edges == 0,
        "status": (
            "passed"
            if not np.any(repeated_index)
            and not np.any(zero_area)
            and boundary_edges == 0
            and nonmanifold_edges == 0
            else "failed"
        ),
    }
    payload = json.dumps(report, ensure_ascii=False, indent=2)
    print(payload)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(payload + "\n", encoding="utf-8")
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
