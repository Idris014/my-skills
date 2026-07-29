#!/usr/bin/env python3
"""Add a non-destructive, parameterized print base to an open Blender file.

Run with Blender:
    blender --background accepted.blend --python blender_add_print_base.py -- \
      --object Character --shape circle --output-blend master_with_base.blend

All dimensional arguments are millimetres. The script creates and edits only the
base and temporary cutters; protected source mesh objects are fingerprinted before
and after the operation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import struct
import sys
from pathlib import Path
from typing import Iterable

import bmesh
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree


def parse_args() -> argparse.Namespace:
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--object", dest="anchor_object", help="Anchor/protected mesh object")
    parser.add_argument("--protected-objects", help="Comma-separated protected mesh objects")
    parser.add_argument("--support-objects", help="Comma-separated objects used for fit/contact")
    parser.add_argument("--float-objects", help="Comma-separated objects that must not overlap base")
    parser.add_argument("--assembly-objects", help="Comma-separated objects included in GLB")
    parser.add_argument("--base-name", default="Print_Base")
    parser.add_argument("--shape", choices=("circle", "ellipse", "rounded-rect"), default="circle")
    parser.add_argument("--fit-mode", choices=("auto", "explicit"), default="auto")
    parser.add_argument("--diameter-mm", type=float)
    parser.add_argument("--width-mm", type=float)
    parser.add_argument("--depth-mm", type=float)
    parser.add_argument("--height-mm", type=float, default=8.0)
    parser.add_argument("--margin-mm", type=float, default=4.0)
    parser.add_argument("--margin-x-mm", type=float)
    parser.add_argument("--margin-y-mm", type=float)
    parser.add_argument("--rearward-offset-mm", type=float, default=0.0)
    parser.add_argument("--offset-x-mm", type=float, default=0.0)
    parser.add_argument("--top-z-mm", type=float)
    parser.add_argument("--contact-overlap-mm", type=float, default=0.3)
    parser.add_argument("--bevel-mm", type=float, default=0.6)
    parser.add_argument("--radial-segments", type=int, default=160)
    parser.add_argument("--base-color-hex", default="#E8E2D9")

    parser.add_argument("--magnet-pocket", action="store_true")
    parser.add_argument("--magnet-diameter-mm", type=float, default=12.0)
    parser.add_argument("--magnet-thickness-mm", type=float, default=3.0)
    parser.add_argument("--magnet-diameter-clearance-mm", type=float, default=0.4)
    parser.add_argument("--magnet-depth-clearance-mm", type=float, default=0.3)
    parser.add_argument("--minimum-roof-mm", type=float, default=1.2)

    parser.add_argument("--locating-holes", action="store_true")
    parser.add_argument("--pin-hole-diameter-mm", type=float, default=3.0)
    parser.add_argument("--pin-hole-depth-mm", type=float, default=3.5)
    parser.add_argument("--pin-spacing-mm", type=float, default=18.0)
    parser.add_argument("--pin-axis", choices=("X", "Y"), default="X")

    parser.add_argument("--output-blend", required=True)
    parser.add_argument("--output-stl")
    parser.add_argument("--output-glb")
    parser.add_argument("--report-json")
    return parser.parse_args(argv)


def split_names(value: str | None) -> list[str]:
    return [part.strip() for part in value.split(",") if part.strip()] if value else []


def mesh_objects(names: Iterable[str], label: str) -> list[bpy.types.Object]:
    result: list[bpy.types.Object] = []
    missing: list[str] = []
    for name in names:
        obj = bpy.data.objects.get(name)
        if obj is None or obj.type != "MESH":
            missing.append(name)
        else:
            result.append(obj)
    if missing:
        raise ValueError(f"{label} mesh object(s) not found: {', '.join(missing)}")
    return result


def choose_anchor(name: str | None) -> bpy.types.Object:
    if name:
        found = mesh_objects([name], "anchor")
        return found[0]
    selected = [obj for obj in bpy.context.selected_objects if obj.type == "MESH"]
    candidates = selected or [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
    if not candidates:
        raise ValueError("No mesh object is available; pass --object.")

    def volume(obj: bpy.types.Object) -> float:
        dims = obj.dimensions
        return abs(dims.x * dims.y * dims.z)

    return max(candidates, key=volume)


def scene_mm_per_bu() -> float:
    scale = bpy.context.scene.unit_settings.scale_length
    return (scale if scale > 0 else 1.0) * 1000.0


def mm_to_bu(value: float) -> float:
    return value / scene_mm_per_bu()


def bu_to_mm(value: float) -> float:
    return value * scene_mm_per_bu()


def world_bounds(objects: Iterable[bpy.types.Object]) -> tuple[Vector, Vector]:
    points = [obj.matrix_world @ Vector(corner) for obj in objects for corner in obj.bound_box]
    if not points:
        raise ValueError("Cannot calculate bounds for an empty object list.")
    minimum = Vector((min(p.x for p in points), min(p.y for p in points), min(p.z for p in points)))
    maximum = Vector((max(p.x for p in points), max(p.y for p in points), max(p.z for p in points)))
    return minimum, maximum


def geometry_digest(obj: bpy.types.Object) -> dict[str, object]:
    mesh = obj.data
    digest = hashlib.sha256()
    for vertex in mesh.vertices:
        digest.update(struct.pack("<3d", *vertex.co))
    for polygon in mesh.polygons:
        digest.update(struct.pack("<II", len(polygon.vertices), polygon.material_index))
        digest.update(struct.pack(f"<{len(polygon.vertices)}I", *polygon.vertices))
    uv_count = 0
    for layer in mesh.uv_layers:
        digest.update(layer.name.encode("utf-8"))
        uv_count += len(layer.data)
        for item in layer.data:
            digest.update(struct.pack("<2d", *item.uv))
    return {
        "name": obj.name,
        "vertices": len(mesh.vertices),
        "edges": len(mesh.edges),
        "polygons": len(mesh.polygons),
        "materials": len(obj.material_slots),
        "uv_layers": len(mesh.uv_layers),
        "uv_loops": uv_count,
        "sha256": digest.hexdigest(),
    }


def parse_hex_color(value: str) -> tuple[float, float, float, float]:
    text = value.strip().lstrip("#")
    if len(text) not in (6, 8):
        raise ValueError("--base-color-hex must be RRGGBB or RRGGBBAA.")
    channels = [int(text[i : i + 2], 16) / 255.0 for i in range(0, len(text), 2)]
    if len(channels) == 3:
        channels.append(1.0)
    return tuple(channels)  # type: ignore[return-value]


def add_base_material(obj: bpy.types.Object, name: str, color: str) -> None:
    material = bpy.data.materials.new(name=f"{name}_Material")
    material.diffuse_color = parse_hex_color(color)
    material.use_nodes = True
    principled = material.node_tree.nodes.get("Principled BSDF") if material.node_tree else None
    if principled is not None:
        principled.inputs["Base Color"].default_value = material.diffuse_color
        principled.inputs["Roughness"].default_value = 0.55
    obj.data.materials.append(material)


def apply_transform(obj: bpy.types.Object) -> None:
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.select_set(False)


def add_bevel(obj: bpy.types.Object, width_bu: float) -> None:
    if width_bu <= 0:
        return
    modifier = obj.modifiers.new(name="Print_Edge_Bevel", type="BEVEL")
    modifier.width = width_bu
    modifier.segments = 4
    modifier.limit_method = "ANGLE"
    modifier.angle_limit = math.radians(30)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier=modifier.name)


def create_base(
    args: argparse.Namespace,
    support_min: Vector,
    support_max: Vector,
) -> tuple[bpy.types.Object, dict[str, float]]:
    margin_x = args.margin_x_mm if args.margin_x_mm is not None else args.margin_mm
    margin_y = args.margin_y_mm if args.margin_y_mm is not None else args.margin_mm
    auto_width = bu_to_mm(support_max.x - support_min.x) + 2 * margin_x
    auto_depth = bu_to_mm(support_max.y - support_min.y) + 2 * margin_y

    if args.shape == "circle":
        diameter = args.diameter_mm if args.diameter_mm is not None else max(auto_width, auto_depth)
        if args.fit_mode == "explicit" and args.diameter_mm is None:
            raise ValueError("--diameter-mm is required for an explicit circle.")
        width_mm = depth_mm = diameter
    else:
        width_mm = args.width_mm if args.width_mm is not None else auto_width
        depth_mm = args.depth_mm if args.depth_mm is not None else auto_depth
        if args.fit_mode == "explicit" and (args.width_mm is None or args.depth_mm is None):
            raise ValueError("--width-mm and --depth-mm are required for an explicit non-circle.")

    if min(width_mm, depth_mm, args.height_mm) <= 0:
        raise ValueError("Base width, depth, and height must be positive.")
    if args.radial_segments < 96:
        raise ValueError("--radial-segments must be at least 96 for printable circular geometry.")

    center_x = (support_min.x + support_max.x) / 2 + mm_to_bu(args.offset_x_mm)
    center_y = (
        (support_min.y + support_max.y) / 2
        - mm_to_bu(args.rearward_offset_mm)
    )
    if args.top_z_mm is None:
        top_z = support_min.z + mm_to_bu(args.contact_overlap_mm)
    else:
        top_z = mm_to_bu(args.top_z_mm)
    height_bu = mm_to_bu(args.height_mm)
    center_z = top_z - height_bu / 2

    bpy.ops.object.select_all(action="DESELECT")
    if args.shape in ("circle", "ellipse"):
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=args.radial_segments,
            radius=0.5,
            depth=1.0,
            location=(center_x, center_y, center_z),
        )
        base = bpy.context.active_object
        base.scale = (mm_to_bu(width_mm), mm_to_bu(depth_mm), height_bu)
    else:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(center_x, center_y, center_z))
        base = bpy.context.active_object
        base.scale = (mm_to_bu(width_mm), mm_to_bu(depth_mm), height_bu)
    base.name = args.base_name
    apply_transform(base)
    add_bevel(base, mm_to_bu(args.bevel_mm))
    add_base_material(base, args.base_name, args.base_color_hex)
    for polygon in base.data.polygons:
        polygon.use_smooth = args.shape in ("circle", "ellipse")

    return base, {
        "width_mm": width_mm,
        "depth_mm": depth_mm,
        "height_mm": args.height_mm,
        "center_x_mm": bu_to_mm(center_x),
        "center_y_mm": bu_to_mm(center_y),
        "top_z_mm": bu_to_mm(top_z),
        "bottom_z_mm": bu_to_mm(top_z - height_bu),
    }


def boolean_difference(base: bpy.types.Object, cutter: bpy.types.Object, label: str) -> None:
    bpy.context.view_layer.objects.active = base
    modifier = base.modifiers.new(name=label, type="BOOLEAN")
    modifier.operation = "DIFFERENCE"
    modifier.solver = "EXACT"
    modifier.object = cutter
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    bpy.data.objects.remove(cutter, do_unlink=True)


def add_cylinder_cutter(
    name: str,
    diameter_mm: float,
    depth_mm: float,
    location: tuple[float, float, float],
    segments: int,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=segments,
        radius=mm_to_bu(diameter_mm) / 2,
        depth=mm_to_bu(depth_mm),
        location=location,
    )
    cutter = bpy.context.active_object
    cutter.name = name
    return cutter


def cut_precision_features(
    base: bpy.types.Object,
    args: argparse.Namespace,
    dimensions: dict[str, float],
) -> dict[str, object]:
    center = base.location
    base_bottom = mm_to_bu(dimensions["bottom_z_mm"])
    base_top = mm_to_bu(dimensions["top_z_mm"])
    result: dict[str, object] = {"magnet_pocket": None, "locating_holes": []}

    if args.magnet_pocket:
        cavity_diameter = args.magnet_diameter_mm + args.magnet_diameter_clearance_mm
        cavity_depth = args.magnet_thickness_mm + args.magnet_depth_clearance_mm
        roof = args.height_mm - cavity_depth
        if cavity_diameter <= 0 or cavity_depth <= 0:
            raise ValueError("Magnet cavity dimensions must be positive.")
        if roof < args.minimum_roof_mm:
            raise ValueError(
                f"Magnet pocket leaves {roof:.3f} mm roof; minimum is "
                f"{args.minimum_roof_mm:.3f} mm."
            )
        epsilon = 0.05
        cutter_depth = cavity_depth + epsilon
        cutter_z = base_bottom + mm_to_bu(cutter_depth / 2 - epsilon)
        cutter = add_cylinder_cutter(
            "CUTTER_Magnet_Pocket",
            cavity_diameter,
            cutter_depth,
            (center.x, center.y, cutter_z),
            max(96, args.radial_segments),
        )
        boolean_difference(base, cutter, "CUT_Magnet_Pocket")
        result["magnet_pocket"] = {
            "magnet_diameter_mm": args.magnet_diameter_mm,
            "magnet_thickness_mm": args.magnet_thickness_mm,
            "cavity_diameter_mm": cavity_diameter,
            "cavity_depth_mm": cavity_depth,
            "roof_mm": roof,
            "opening": "bottom",
        }

    if args.locating_holes:
        if args.pin_hole_depth_mm <= 0 or args.pin_hole_depth_mm >= args.height_mm:
            raise ValueError("Pin-hole depth must be positive and less than base height.")
        if args.pin_hole_diameter_mm <= 0 or args.pin_spacing_mm <= 0:
            raise ValueError("Pin-hole diameter and spacing must be positive.")
        epsilon = 0.05
        cutter_depth = args.pin_hole_depth_mm + epsilon
        cutter_z = base_top - mm_to_bu(cutter_depth / 2 - epsilon)
        for sign in (-1, 1):
            dx = mm_to_bu(sign * args.pin_spacing_mm / 2) if args.pin_axis == "X" else 0
            dy = mm_to_bu(sign * args.pin_spacing_mm / 2) if args.pin_axis == "Y" else 0
            cutter = add_cylinder_cutter(
                f"CUTTER_Pin_Hole_{'A' if sign < 0 else 'B'}",
                args.pin_hole_diameter_mm,
                cutter_depth,
                (center.x + dx, center.y + dy, cutter_z),
                96,
            )
            boolean_difference(base, cutter, f"CUT_Pin_Hole_{sign}")
            result["locating_holes"].append(
                {
                    "diameter_mm": args.pin_hole_diameter_mm,
                    "depth_mm": args.pin_hole_depth_mm,
                    "center_x_mm": bu_to_mm(center.x + dx),
                    "center_y_mm": bu_to_mm(center.y + dy),
                    "opening": "top",
                }
            )
    return result


def mesh_audit(obj: bpy.types.Object) -> dict[str, int]:
    mesh = obj.data
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.verts.ensure_lookup_table()
    non_manifold = sum(1 for edge in bm.edges if not edge.is_manifold)

    unvisited = set(bm.verts)
    components = 0
    while unvisited:
        components += 1
        stack = [unvisited.pop()]
        while stack:
            vertex = stack.pop()
            for edge in vertex.link_edges:
                other = edge.other_vert(vertex)
                if other in unvisited:
                    unvisited.remove(other)
                    stack.append(other)
    bm.free()
    return {
        "vertices": len(mesh.vertices),
        "edges": len(mesh.edges),
        "polygons": len(mesh.polygons),
        "non_manifold_edges": non_manifold,
        "connected_components": components,
    }


def overlap_count(first: bpy.types.Object, second: bpy.types.Object) -> int:
    depsgraph = bpy.context.evaluated_depsgraph_get()
    first_tree = BVHTree.FromObject(first, depsgraph)
    second_tree = BVHTree.FromObject(second, depsgraph)
    if first_tree is None or second_tree is None:
        return 0
    return len(first_tree.overlap(second_tree))


def contact_report(
    base: bpy.types.Object,
    support_objects: Iterable[bpy.types.Object],
    float_objects: Iterable[bpy.types.Object],
) -> dict[str, object]:
    return {
        "required_supports": {
            obj.name: overlap_count(base, obj) for obj in support_objects
        },
        "expected_floating": {
            obj.name: overlap_count(base, obj) for obj in float_objects
        },
    }


def ensure_parent(path: str | None) -> Path | None:
    if not path:
        return None
    resolved = Path(path).expanduser().resolve()
    resolved.parent.mkdir(parents=True, exist_ok=True)
    return resolved


def select_only(objects: Iterable[bpy.types.Object]) -> None:
    bpy.ops.object.select_all(action="DESELECT")
    objects = list(objects)
    for obj in objects:
        obj.select_set(True)
    if objects:
        bpy.context.view_layer.objects.active = objects[0]


def export_stl(base: bpy.types.Object, path: Path) -> None:
    select_only([base])
    scale_to_mm = scene_mm_per_bu()
    if hasattr(bpy.ops.wm, "stl_export"):
        bpy.ops.wm.stl_export(
            filepath=str(path),
            export_selected_objects=True,
            global_scale=scale_to_mm,
        )
    elif hasattr(bpy.ops.export_mesh, "stl"):
        bpy.ops.export_mesh.stl(
            filepath=str(path),
            use_selection=True,
            global_scale=scale_to_mm,
        )
    else:
        raise RuntimeError("No STL exporter is available in this Blender build.")


def export_glb(objects: Iterable[bpy.types.Object], path: Path) -> None:
    select_only(objects)
    bpy.ops.export_scene.gltf(
        filepath=str(path),
        export_format="GLB",
        use_selection=True,
        export_apply=True,
    )


def main() -> None:
    args = parse_args()
    anchor = choose_anchor(args.anchor_object)

    protected_names = split_names(args.protected_objects) or [anchor.name]
    support_names = split_names(args.support_objects) or [anchor.name]
    float_names = split_names(args.float_objects)
    protected = mesh_objects(protected_names, "protected")
    supports = mesh_objects(support_names, "support")
    floating = mesh_objects(float_names, "floating")
    before = {obj.name: geometry_digest(obj) for obj in protected}

    support_min, support_max = world_bounds(supports)
    base, dimensions = create_base(args, support_min, support_max)
    features = cut_precision_features(base, args, dimensions)
    base_audit = mesh_audit(base)
    contacts = contact_report(base, supports, floating)
    after = {obj.name: geometry_digest(obj) for obj in protected}
    protected_unchanged = all(before[name] == after[name] for name in before)

    if not protected_unchanged:
        raise RuntimeError("A protected mesh signature changed during base creation.")
    if base_audit["non_manifold_edges"] != 0 or base_audit["connected_components"] != 1:
        raise RuntimeError(f"Base mesh audit failed: {base_audit}")

    output_blend = ensure_parent(args.output_blend)
    output_stl = ensure_parent(args.output_stl)
    output_glb = ensure_parent(args.output_glb)
    report_path = ensure_parent(
        args.report_json
        or str(Path(args.output_blend).with_name("BASE-REPORT.json"))
    )

    if output_stl is not None:
        export_stl(base, output_stl)
    if output_glb is not None:
        assembly_names = split_names(args.assembly_objects)
        if assembly_names:
            assembly = mesh_objects(assembly_names, "assembly")
        else:
            assembly = list(dict.fromkeys([*protected, *supports, *floating]))
        export_glb([*assembly, base], output_glb)

    bpy.ops.wm.save_as_mainfile(filepath=str(output_blend))

    report = {
        "schema": "meshy2bambu.base-report.v1",
        "scene_mm_per_blender_unit": scene_mm_per_bu(),
        "anchor_object": anchor.name,
        "protected_objects": protected_names,
        "support_objects": support_names,
        "float_objects": float_names,
        "base": {
            "name": base.name,
            "shape": args.shape,
            "fit_mode": args.fit_mode,
            **dimensions,
            "bevel_mm": args.bevel_mm,
            "color_hex": args.base_color_hex,
        },
        "features": features,
        "protected_before": before,
        "protected_after": after,
        "protected_unchanged": protected_unchanged,
        "base_mesh_audit": base_audit,
        "contacts": contacts,
        "validation": {
            "required_supports_overlap": all(
                value > 0 for value in contacts["required_supports"].values()
            ),
            "expected_floating_clear": all(
                value == 0 for value in contacts["expected_floating"].values()
            ),
            "base_closed_single_component": (
                base_audit["non_manifold_edges"] == 0
                and base_audit["connected_components"] == 1
            ),
        },
        "outputs": {
            "blend": str(output_blend),
            "base_stl": str(output_stl) if output_stl else None,
            "assembly_glb": str(output_glb) if output_glb else None,
            "report_json": str(report_path),
        },
    }
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
