"""Append a Blender base mesh to a topology-compatible painted Bambu 3MF."""

from __future__ import annotations

import argparse
import bmesh
import bpy
import os
import re
import sys
import tempfile
import zipfile
from pathlib import Path


def transformed_point(point, profile: str, offset_y_mm: float):
    if profile == "xyz-mm":
        return (
            point.x * 1000.0,
            point.y * 1000.0 + offset_y_mm,
            point.z * 1000.0,
        )
    if profile == "meow-v1":
        return (
            point.x * 1000.0,
            point.z * 1000.0 + offset_y_mm,
            -point.y * 1000.0,
        )
    raise ValueError(f"Unknown coordinate profile: {profile}")


def base_geometry(object_name: str, profile: str, offset_y_mm: float):
    obj = bpy.data.objects[object_name]
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.triangulate(bm, faces=list(bm.faces))
    bm.verts.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    world = obj.matrix_world
    vertices = [
        transformed_point(world @ vertex.co, profile, offset_y_mm)
        for vertex in bm.verts
    ]
    triangles = [tuple(vertex.index for vertex in face.verts) for face in bm.faces]
    bm.free()
    return vertices, triangles


def rewrite_object(
    source_stream,
    output_stream,
    character_vertex_count,
    character_triangle_count,
    base_vertices,
    base_triangles,
):
    vertex_index = 0
    triangle_index = 0
    section = None
    for raw_line in source_stream:
        line = raw_line.decode("utf-8")
        stripped = line.strip()
        if stripped == "<vertices>":
            section = "vertices"
            output_stream.write(line)
            continue
        if stripped == "</vertices>":
            for x, y, z in base_vertices:
                output_stream.write(
                    f'     <vertex x="{x:.7f}" y="{y:.7f}" z="{z:.7f}"/>\n'
                )
            output_stream.write(line)
            section = None
            continue
        if stripped == "<triangles>":
            section = "triangles"
            output_stream.write(line)
            continue
        if stripped == "</triangles>":
            for v1, v2, v3 in base_triangles:
                offset = character_vertex_count
                output_stream.write(
                    f'     <triangle v1="{offset + v1}" '
                    f'v2="{offset + v2}" v3="{offset + v3}"/>\n'
                )
            output_stream.write(line)
            section = None
            continue
        if section == "vertices" and stripped.startswith("<vertex "):
            if vertex_index < character_vertex_count:
                output_stream.write(line)
            vertex_index += 1
            continue
        if section == "triangles" and stripped.startswith("<triangle "):
            if triangle_index < character_triangle_count:
                output_stream.write(line)
            triangle_index += 1
            continue
        output_stream.write(line)

    if vertex_index < character_vertex_count:
        raise RuntimeError(
            f"Source has only {vertex_index} vertices; "
            f"expected at least {character_vertex_count}"
        )
    if triangle_index < character_triangle_count:
        raise RuntimeError(
            f"Source has only {triangle_index} triangles; "
            f"expected at least {character_triangle_count}"
        )


def build(
    source_3mf: Path,
    output_3mf: Path,
    base_object: str,
    character_vertex_count: int,
    character_triangle_count: int,
    coordinate_profile: str,
    offset_y_mm: float,
    source_model_name: str | None = None,
    output_model_name: str | None = None,
):
    base_vertices, base_triangles = base_geometry(
        base_object, coordinate_profile, offset_y_mm
    )
    output_3mf.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="bambu-pet-delivery-") as temp:
        object_xml = Path(temp) / "object_1.model"
        with zipfile.ZipFile(source_3mf, "r") as source_zip:
            with source_zip.open("3D/Objects/object_1.model", "r") as source:
                with object_xml.open("w", encoding="utf-8", newline="\n") as target:
                    rewrite_object(
                        source,
                        target,
                        character_vertex_count,
                        character_triangle_count,
                        base_vertices,
                        base_triangles,
                    )

            with zipfile.ZipFile(
                output_3mf,
                "w",
                compression=zipfile.ZIP_DEFLATED,
                compresslevel=6,
            ) as output_zip:
                for info in source_zip.infolist():
                    if info.filename == "3D/Objects/object_1.model":
                        continue
                    data = source_zip.read(info.filename)
                    if info.filename == "Metadata/model_settings.config":
                        text = data.decode("utf-8")
                        if source_model_name and output_model_name:
                            text = text.replace(source_model_name, output_model_name)
                        total_faces = character_triangle_count + len(base_triangles)
                        text = re.sub(
                            r'face_count="\d+"',
                            f'face_count="{total_faces}"',
                            text,
                        )
                        data = text.encode("utf-8")
                    output_zip.writestr(info, data)
                output_zip.write(
                    object_xml,
                    "3D/Objects/object_1.model",
                    compress_type=zipfile.ZIP_DEFLATED,
                    compresslevel=6,
                )
    return {
        "output": str(output_3mf),
        "base_vertices": len(base_vertices),
        "base_triangles": len(base_triangles),
        "total_triangles": character_triangle_count + len(base_triangles),
    }


def blender_args():
    values = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-3mf", required=True, type=Path)
    parser.add_argument("--output-3mf", required=True, type=Path)
    parser.add_argument("--base-object", required=True)
    parser.add_argument("--character-vertex-count", required=True, type=int)
    parser.add_argument("--character-triangle-count", required=True, type=int)
    parser.add_argument(
        "--coordinate-profile",
        choices=["xyz-mm", "meow-v1"],
        default="xyz-mm",
    )
    parser.add_argument("--offset-y-mm", type=float)
    parser.add_argument("--source-model-name")
    parser.add_argument("--output-model-name")
    return parser.parse_args(values)


def main() -> int:
    args = blender_args()
    offset = args.offset_y_mm
    if offset is None:
        offset = -58.5 if args.coordinate_profile == "meow-v1" else 0.0
    result = build(
        args.source_3mf,
        args.output_3mf,
        args.base_object,
        args.character_vertex_count,
        args.character_triangle_count,
        args.coordinate_profile,
        offset,
        args.source_model_name,
        args.output_model_name,
    )
    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
