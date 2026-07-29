# Meshy API for Meshy2Bambu

Checked against official Meshy documentation on 2026-07-29.

## Authentication

Use:

```text
Authorization: Bearer $MESHY_API_KEY
```

Never write the key into requests archived on disk. Redact authorization headers from logs.

Base URL:

```text
https://api.meshy.ai
```

## Can Meshy generate multiview images?

Yes, as a separate image-generation stage.

For a supplied master image:

```text
POST /openapi/v1/image-to-image
```

Set:

```json
{
  "generate_multi_view": true
}
```

The completed task returns three image URLs representing different viewing angles. Show and approve
them before 3D generation.

Meshy Multi-Image to 3D does not need to generate the views itself. It consumes either:

- `image_urls`: 1–4 approved images; or
- `input_task_id`: a successful Meshy image-generation or multiview task.

Prefer explicit downloaded images for reproducible archives.

## Image to Image multiview

Create:

```text
POST /openapi/v1/image-to-image
```

Retrieve:

```text
GET /openapi/v1/image-to-image/{TASK_ID}
```

Required create fields:

- `ai_model`;
- `prompt`;
- `reference_image_urls`.

With `generate_multi_view: true`, do not set `aspect_ratio`.

## Single Image to 3D

Create:

```text
POST /openapi/v1/image-to-3d
```

Retrieve:

```text
GET /openapi/v1/image-to-3d/{TASK_ID}
```

Use when the user explicitly accepts single-view inference.

## Multi-Image to 3D

Create:

```text
POST /openapi/v1/multi-image-to-3d
```

Retrieve:

```text
GET /openapi/v1/multi-image-to-3d/{TASK_ID}
```

Use 1–4 images of the same object. For Meshy 6, `latest` resolves to Meshy 6.

Recommended fidelity-first defaults:

- `should_texture: true`;
- `enable_pbr: true`;
- `texture_resolution: 4k`;
- `image_enhancement: false` for already accepted references;
- `remove_lighting: true`;
- `should_remesh: false`;
- `auto_size: false`;
- `target_formats: ["glb"]`.

## Task handling

Possible status values include:

- `PENDING`;
- `IN_PROGRESS`;
- `SUCCEEDED`;
- `FAILED`;
- `CANCELED`.

Do not silently retry a failed credit-consuming generation with changed parameters. Report the
failure and stop at the same gate.

On success, save:

- task ID;
- request payload without secrets;
- full result JSON;
- consumed credits;
- timestamps;
- downloaded files and SHA-256.

## Upload and export notes

Supported 3D uploads include GLB, glTF, OBJ, FBX, and STL, subject to current Meshy limits.
Generated endpoints can return GLB, OBJ, FBX, STL, USDZ, and opt-in 3MF depending on the task.

For Blender handoff, GLB is the canonical source because it can keep geometry, materials, UVs, and
embedded textures in one file.

For Bambu, do not confuse an ordinary generation-endpoint 3MF with a multicolor face-assigned 3MF.

## Multi-Color Print

Meshy's printer-oriented color conversion is a separate paid task:

```text
POST /openapi/v1/print/multi-color
GET  /openapi/v1/print/multi-color/{TASK_ID}
```

Use exactly one source:

- `input_task_id`: a successful Image-to-3D, Multi-Image-to-3D, Text-to-3D, Remesh, or Retexture
  task; or
- `model_url`: a public URL or data URI containing a `.glb` or `.fbx`.

Set:

```json
{
  "model_url": "data:model/gltf-binary;base64,…",
  "max_colors": 3
}
```

`max_colors` accepts 1–16 and defaults to 4. A successful task costs 10 credits. The completed
result exposes `model_urls.3mf`.

Run this after geometry repair, scale, and topology are final. Preserve:

- the final textured GLB as the canonical editable/appearance source;
- the exact secret-free request record and source SHA-256;
- create/task result JSON and credits;
- the returned raw multicolor 3MF candidate;
- a separately named Bambu-cleaned final 3MF.

If the paid task already exists, recover it without creating a new task:

```bash
python scripts/meshy_api.py multi-color-resume \
  --task-id TASK_ID \
  --output-dir meshy-source/multi-color
```

Do not add `target_formats: ["3mf"]` to an upstream generation request and call that equivalent.
The ordinary export and `print-multi-color` are different tasks. If the final geometry is edited
after conversion, rerun Multi-Color Print or re-establish topology compatibility before
transferring any triangle paint.

## Official references

- API overview: <https://docs.meshy.ai/en/api>
- Image to Image: <https://docs.meshy.ai/en/api/image-to-image>
- Image to 3D: <https://docs.meshy.ai/en/api/image-to-3d>
- Multi-Image to 3D: <https://docs.meshy.ai/en/api/multi-image-to-3d>
- Retexture: <https://docs.meshy.ai/en/api/retexture>
- Multi-Color Print: <https://docs.meshy.ai/en/api/multi-color-print>
- Changelog: <https://docs.meshy.ai/en/api/changelog>
- Pricing: <https://docs.meshy.ai/en/api/pricing>
