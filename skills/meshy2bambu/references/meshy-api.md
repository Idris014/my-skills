# Meshy API for Meshy2Bambu

Checked against official Meshy documentation on 2026-07-28.

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

For Bambu, do not confuse a geometry-only 3MF with a multicolor face-assigned 3MF.

## Official references

- API overview: <https://docs.meshy.ai/en/api>
- Image to Image: <https://docs.meshy.ai/en/api/image-to-image>
- Image to 3D: <https://docs.meshy.ai/en/api/image-to-3d>
- Multi-Image to 3D: <https://docs.meshy.ai/en/api/multi-image-to-3d>
- Retexture: <https://docs.meshy.ai/en/api/retexture>
- Pricing: <https://docs.meshy.ai/en/api/pricing>
