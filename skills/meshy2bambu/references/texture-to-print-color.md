# Texture to Bambu Print Color

Use this workflow when a GLB looks colored in Blender or a viewer but Bambu Studio imports it as
one unpainted part.

## 1. Classify the source color

Run:

```bash
python scripts/inspect_color_partition.py SOURCE.glb \
  --json-out source-color-audit.json
```

Interpret the classification:

| Classification | Meaning | Next action |
|---|---|---|
| `texture_only_glb` | Color comes from a UV base-color texture; no Bambu face paint exists | Run Texture-to-Color Painting |
| `material_regions_glb` | Multiple material-backed primitives exist | Import and verify whether regions remain usable |
| `vertex_color_glb` | `COLOR_0` exists | Import and verify; do not assume Bambu converts it to face paint |
| `uniform_or_uncolored_glb` | No usable detailed color source was found | Obtain a palette/reference or paint manually |
| `face_painted_3mf` | Triangle-level `paint_color` already exists | Validate, clean, or transfer safely |
| `unpainted_3mf` | 3MF geometry exists without triangle paint | Paint or assign part colors before claiming multicolor readiness |

GLB display color and Bambu print color are different:

- UV textures describe pixels used for rendering.
- Multiple materials describe rendering regions or primitives.
- Bambu 3MF stores printable face assignments on triangles, commonly in `paint_color`.

Keep the source GLB immutable and preserve its embedded base-color texture even after producing a
painted 3MF.

## 2. Prepare the texture source

Before conversion:

1. Preserve a SHA-256 copy of the textured GLB.
2. Confirm its base-color texture, UVs, vertex count, triangle count, and triangle order.
3. Apply the intended physical scale in a versioned Blender branch without changing topology.
4. Keep precision bases or inserts as separate objects.
5. Export a `*_TEXTURE_SOURCE.glb` with embedded textures.

If Bambu Studio asks whether a metre-scale glTF should be converted to millimetres, accept only
after checking the intended dimensions. Record the resulting millimetre size.

## 3. Generate the print-color candidate

Choose one route. Keep the texture-source GLB regardless of route.

### Route A — Meshy Multi-Color Print

Use this route when the user has authorized the current 10-credit conversion.

```bash
python scripts/meshy_api.py multi-color \
  --model-file CHARACTER_TEXTURE_SOURCE.glb \
  --max-colors 3 \
  --output-dir meshy-source/multi-color
```

The script submits `POST /openapi/v1/print/multi-color`, waits for completion, archives a
secret-free request and task record, and downloads `multicolor.3mf`.

If the task succeeded but download was interrupted, run `multi-color-resume --task-id TASK_ID`.
Do not resubmit the paid conversion.

Alternatively, use `--input-task-id` when the final geometry is exactly the successful Meshy task
output. Prefer `--model-file` after Blender repair or scaling so the conversion sees the actual
final geometry.

Preserve the result as `*_meshy_multicolor_candidate.3mf`. Import it into Bambu Studio, verify its
dimensions and face colors, clean small islands and semantic mistakes, and save the cleaned result
under a new name.

### Route B — Bambu Studio Texture-to-Color

In Bambu Studio:

1. Import `*_TEXTURE_SOURCE.glb`.
2. Confirm dimensions, part count, triangle count, and orientation.
3. Choose a provisional palette size appropriate to the desired result.
4. Run `Texture-to-Color Painting / 纹理转颜色`.
5. Save immediately as `*_texture_to_color_candidate.3mf`.

Menu placement and wording can vary by Bambu Studio version. Use the native texture-to-color
feature rather than pretending that the GLB already contains print regions.

Automatic clustering produces a starting point, not semantic truth. Its colors may be influenced
by shadows, highlights, antialiasing, texture compression, and small decorative pixels.

Ordinary Meshy generation with `target_formats: ["3mf"]` is not Route A. Only the separate
`print/multi-color` task is intended to create the multicolor-print candidate described here.

## 4. Audit the candidate

Run:

```bash
python scripts/inspect_color_partition.py CANDIDATE.3mf \
  --expect-classification face_painted_3mf \
  --json-out candidate-color-audit.json
```

When every character triangle should be painted, also use:

```bash
python scripts/inspect_color_partition.py CANDIDATE.3mf \
  --expect-classification face_painted_3mf \
  --expected-painted-triangles CHARACTER_TRIANGLES \
  --require-full-paint \
  --json-out candidate-color-audit.json
```

Then run `scripts/validate_delivery.py` and Bambu Studio's importer. Confirm:

- 3MF ZIP integrity;
- intended dimensions;
- unchanged character triangle count;
- painted and unpainted triangle totals;
- `paint_color` counts;
- parts and manifold result.

Do not equate “paint attributes exist” with “the palette is correct.”

## 5. Clean the regions

Review the candidate visually and in sliced preview. Prioritize:

- eyes, lashes, pupils, brows, and mouth;
- hair tips and hair/skin boundaries;
- inner ears, blush, fingers, and thin limbs;
- clothing edges, shoe soles, and small accessories;
- isolated one-face or tiny color islands.

Merge or repaint noisy islands according to the approved semantic palette. For example, when the
eyes will be hand-painted after printing, merge all eye faces into the skin region before final
validation.

Save the cleaned result as a new version, not over the raw texture-to-color candidate.

## 6. Transfer paint to a derived version

Transfer an existing character's `paint_color` data only when:

- vertex count and order match;
- triangle count and order match;
- coordinate differences are explained by a documented rigid/scale transform or 3MF rounding;
- the character triangles occupy a known range in the source 3MF.

Copy painted character triangles verbatim. Append new bases or inserts with an index offset and
leave them as separate unpainted or uniformly assigned parts. Update the 3MF face count and verify
the result.

If topology changed, do not transfer by triangle index. Re-run texture-to-color conversion or
create a new approved region map.

## 7. Deliverables

Preserve:

```text
inputs/SOURCE.IMMUTABLE.glb
exports/CHARACTER_TEXTURE_SOURCE.glb
bambu-studio-delivery/CHARACTER_meshy_multicolor_candidate.3mf
or
bambu-studio-delivery/CHARACTER_texture_to_color_candidate.3mf
bambu-studio-delivery/CHARACTER_color_cleaned.3mf
audits/source-color-audit.json
audits/candidate-color-audit.json
audits/final-bambu-validation.json
```

The final report must state:

- source classification;
- whether Meshy Multi-Color Print or Bambu Texture-to-Color was actually run;
- Meshy task ID, credits, and `max_colors` when Route A was used;
- provisional and final palette;
- painted triangle coverage and counts;
- cleanup decisions;
- topology compatibility and any paint transfer;
- whether physical AMS slots, slicing, or printer sending occurred.

## Automation boundary

If Bambu Studio's GUI conversion cannot be operated in the current environment, do not fabricate
`paint_color` claims. Deliver the validated texture-source GLB and clearly mark the conversion as
pending, or use a separately approved reproducible UV-sampling/face-classification implementation
that records its palette, sampling method, thresholds, and face counts.
