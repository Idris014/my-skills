# Bambu Studio Delivery

## Color sources

GLB materials and Bambu face painting are independent.

- GLB can preserve base colors and embedded JPEG/PNG textures.
- Bambu 3MF stores paint assignments on triangles, often as `paint_color` attributes.
- Importing a colored GLB does not guarantee the same Bambu paint regions.

Run `scripts/inspect_color_partition.py` before deciding whether an asset is texture-only,
multi-material, vertex-colored, already face-painted, or unpainted.

When a GLB is `texture_only_glb`, follow
[texture-to-print-color.md](texture-to-print-color.md) to create a Meshy Multi-Color Print or
Bambu Texture-to-Color candidate, then clean it in Bambu Studio before delivery. Preserve the
texture-source GLB and raw automatic candidate separately.

## Safe paint transfer

Transfer existing paint metadata only when:

- the character vertex order is unchanged;
- the character triangle order is unchanged;
- the character vertex and triangle counts match;
- the painted character triangles form a known leading range in the source 3MF.

Copy the character vertices and painted triangles verbatim. Append the new base vertices and unpainted triangles with a vertex-index offset.

Update `Metadata/model_settings.config`:

- model filename;
- total `face_count`.

Copy all other source 3MF members unchanged unless a specific metadata update is required.

## Coordinate profiles

The bundled script supports:

- `xyz-mm`: Blender X/Y/Z metres converted directly to millimetres;
- `meow-v1`: `X = Blender X`, `Y = Blender Z - 58.5 mm`, `Z = -Blender Y`.

Use `meow-v1` only for successors of the validated Meow v1 3MF. For a different source project, derive and document its coordinate mapping instead of guessing.

## Validation

Use Bambu Studio's CLI importer:

```bash
/Applications/BambuStudio.app/Contents/MacOS/BambuStudio --info FILE
```

Check:

- dimensions;
- facet count;
- `manifold = yes`;
- number of parts;
- volume.

For 3MF:

- run `unzip -t`;
- run `scripts/inspect_color_partition.py`;
- count every `paint_color` value;
- verify the painted sum equals the unchanged character triangle count;
- verify total triangles equal character triangles plus new base triangles;
- confirm the base is a separate, unpainted region.

Do not claim that a file is sliced merely because Bambu Studio imported it.

If the headless `--info` command crashes on a 3MF that the Bambu GUI successfully opens, treat the
CLI result as an importer-path failure, not automatic proof of non-manifold geometry. Record the
GUI-open evidence and run:

```bash
python scripts/audit_3mf_mesh.py FILE.3mf --json-out mesh-audit.json
```

The fallback audit checks triangle indices, zero-area faces, boundary edges, and edges shared by
more than two triangles. Keep the CLI failure visible in the final validation record.
