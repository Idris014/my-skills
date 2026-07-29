"""Audit one mesh object. Run inside Blender or import and call audit_object()."""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector


def connected_components(bm) -> int:
    count = 0
    seen = set()
    for vertex in bm.verts:
        if vertex.index in seen:
            continue
        count += 1
        stack = [vertex]
        seen.add(vertex.index)
        while stack:
            current = stack.pop()
            for edge in current.link_edges:
                other = edge.other_vert(current)
                if other.index not in seen:
                    seen.add(other.index)
                    stack.append(other)
    return count


def audit_object(object_name: str) -> dict:
    obj = bpy.data.objects[object_name]
    if obj.type != "MESH":
        raise TypeError(f"{object_name} is not a mesh")
    mesh = obj.data

    geometry = hashlib.sha256()
    for vertex in mesh.vertices:
        geometry.update(struct.pack("<3d", *vertex.co))
    for polygon in mesh.polygons:
        geometry.update(struct.pack("<I", len(polygon.vertices)))
        for index in polygon.vertices:
            geometry.update(struct.pack("<I", index))

    uv_digest = None
    if mesh.uv_layers.active:
        digest = hashlib.sha256()
        for loop in mesh.uv_layers.active.data:
            digest.update(struct.pack("<2d", *loop.uv))
        uv_digest = digest.hexdigest()

    bm = bmesh.new()
    bm.from_mesh(mesh)
    non_manifold = sum(1 for edge in bm.edges if not edge.is_manifold)
    components = connected_components(bm)
    bm.free()

    corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    bounds_min = [min(point[index] for point in corners) * 1000 for index in range(3)]
    bounds_max = [max(point[index] for point in corners) * 1000 for index in range(3)]
    return {
        "object": object_name,
        "mesh": mesh.name,
        "vertices": len(mesh.vertices),
        "faces": len(mesh.polygons),
        "materials": [slot.material.name if slot.material else None for slot in obj.material_slots],
        "uv_layers": [layer.name for layer in mesh.uv_layers],
        "geometry_digest": geometry.hexdigest(),
        "uv_digest": uv_digest,
        "non_manifold_edges": non_manifold,
        "connected_components": components,
        "bounds_mm": {
            "min": [round(value, 6) for value in bounds_min],
            "max": [round(value, 6) for value in bounds_max],
        },
    }


def blender_args():
    values = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--object", required=True)
    parser.add_argument("--json-out", type=Path)
    return parser.parse_args(values)


def main() -> int:
    args = blender_args()
    report = audit_object(args.object)
    payload = json.dumps(report, ensure_ascii=False, indent=2)
    print(payload)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(payload + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
