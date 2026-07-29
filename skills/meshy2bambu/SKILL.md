---
name: meshy2bambu
description: Use Meshy API as the upstream image-to-3D generator, then audit and repair the result with Blender MCP and deliver validated geometry or multicolor assets to Bambu Studio. Use this skill whenever a user wants to turn a render, concept description, reference image, or multiview set into a printable model; generate or repair GLB/OBJ/STL/3MF; preserve textures; add bases or connectors; or prepare an AI-generated asset for Bambu—even if Meshy is not named. Every invocation must begin with the material-intake questions and must stop for explicit user approval between every workflow stage.
compatibility: Meshy API with MESHY_API_KEY, imagegen, Blender 4.x with Blender MCP or background Python, Python 3.10+, Bambu Studio CLI, zip/unzip, and standard filesystem tools.
---

# Meshy2Bambu

Turn a render or description into an immutable Meshy source asset, repair and engineer it in
Blender, and deliver a validated Bambu Studio package.

This is a user-steered pipeline. Accuracy improves when the user can inspect each irreversible,
credit-consuming, or geometry-changing transition. Therefore, stage gates are part of the output,
not optional project management.

## Non-negotiable interaction contract

### Begin every new job with intake

Before calling imagegen, Meshy, Blender MCP, Bambu Studio, or any project-changing tool, ask the
user these two questions:

1. **Source material:** “请提供渲染图/参考图，或给出完整文字描述。若提供描述，我将在下一阶段调用 imagegen 生成首张参考图。”
2. **Multiview:** “是否需要多视图？请选择：已有 2–4 张视图 / 由 Meshy API 生成多视图 / 不需要。”

Also explain in one sentence:

> Meshy API can generate multiview references from a single approved image through its separate
> image-to-image multiview stage; Multi-Image to 3D then consumes 1–4 approved images.

If the user's opening message already includes images, a description, or a multiview preference,
summarize what was received and ask them to confirm or correct it. **End the turn after intake.**
Do not infer that supplied material waives this gate.

When the user is resuming an active job by approving one next stage, do not restart intake. Read its
`workflow-state.json`, verify that the named next gate is approved, and perform only that stage.

### Stop between every stage

After completing one stage:

1. report only verified outputs and issues;
2. provide clickable files or previews;
3. state the proposed next stage and any credit, topology, color, or print consequence;
4. ask for explicit instruction to continue;
5. end the turn.

Do not begin the next stage in the same turn. This remains true when the user says “全部执行”,
“直接完成”, or “不要停”. Only a later explicit request to change this skill's gate policy can
remove the pauses.

Treat messages such as “继续”, “确认”, or “进入 Blender 修复” as approval for **one next stage
only**, unless the user explicitly names a different single stage.

## Stage map

```text
G0 Intake
 ↓ user approval
G1 Master reference
 ↓ user approval
G2 Multiview package or recorded skip
 ↓ user approval
G3 Meshy 3D generation and source download
 ↓ user approval
G4 Source GLB audit
 ↓ user approval
G5 Blender import and repair diagnosis
 ↓ user approval
G6 Blender geometry repair
 ↓ user approval
G7 Bases, connectors, splits, and print engineering
 ↓ user approval
G8 Bambu geometry/color preparation and importer validation
 ↓ user approval
G9 Package and handoff
```

Maintain `workflow-state.json` in the job directory with:

- current gate;
- input paths and SHA-256;
- Meshy task IDs and request settings;
- user approval timestamp or conversation note for each completed gate;
- accepted source and Blender master paths;
- validation status.

Never mark a gate approved merely because its output succeeded.

Use `scripts/workflow_state.py` to initialize, approve, complete, and verify gates. Before any G1–G9
tool action, run `assert-approved` for that gate.

## G1 — Master reference

If the user supplied a render:

- inspect it;
- copy it into the job's immutable `inputs/` directory;
- record source path, dimensions, and SHA-256;
- identify occluded parts, inconsistent anatomy, shadows, background clutter, and excluded objects.

If the user supplied only a description:

- use imagegen to produce one clean master reference;
- use a plain or transparent background;
- show the full subject without cropping;
- state silhouette, materials, colors, pose, limb count, finger count, and excluded objects;
- save the accepted candidate locally.

Do not generate 3D in G1. Show the master image and stop for approval.

## G2 — Multiview

Read [references/meshy-api.md](references/meshy-api.md).

### Existing views

Accept 2–4 consistent views of the same object. Prefer front, back, left, and right. Normalize:

- canvas size and subject scale;
- neutral background;
- camera height and projection;
- pose, costume, proportions, accessories, and colors;
- excluded objects.

Keep top and bottom views as Blender diagnostic references when the four Meshy input slots are
already occupied.

### Meshy-generated views

Use Meshy's Image to Image API with `generate_multi_view: true` on the approved master image.
The API currently returns three angle images for a multiview task. Archive the request, task result,
images, and credits consumed.

Generated views are candidates, not facts. Check identity, limb count, fingers, accessories, and
backside invention. Show all views and stop for user approval before 3D generation.

### No multiview

Record the user's choice and explain that unseen geometry will be inferred from one image. Stop and
ask whether to proceed to Meshy 3D generation.

## G3 — Meshy 3D generation

Use:

- Image to 3D for one approved image;
- Multi-Image to 3D for 2–4 approved views.

For fidelity-first printable candidates, start with:

```json
{
  "ai_model": "latest",
  "should_texture": true,
  "enable_pbr": true,
  "texture_resolution": "4k",
  "image_enhancement": false,
  "remove_lighting": true,
  "should_remesh": false,
  "pose_mode": "",
  "auto_size": false,
  "target_formats": ["glb"],
  "moderation": true
}
```

Change a parameter only when the user approves the tradeoff. In particular:

- keep `should_remesh: false` until fingers, thin features, and silhouettes are accepted;
- keep `auto_size: false`; establish physical millimetres in Blender;
- do not request 8K textures unless the user accepts the additional credit cost;
- do not request 3MF as the only source format.

Use `scripts/meshy_api.py` for reproducible API requests. Never expose or persist
`MESHY_API_KEY`.

Download successful results immediately because returned URLs can expire. Preserve:

```text
JOB/meshy-source/
├── request.json
├── task-result.json
├── source.glb
├── previews/
└── SHA256SUMS
```

Treat `source.glb` as immutable. Show Meshy previews, task ID, consumed credits, and local source
path, then stop.

## G4 — Source audit

Run:

```bash
python scripts/inspect_glb.py SOURCE.glb --json-out source-glb-audit.json
```

Confirm:

- glTF 2.0;
- mesh/node/component counts;
- materials and embedded images;
- UVs, skins, and animations;
- accessor bounds and probable units;
- whether the source contains the expected complete subject.

When color is expected but missing, stop here. Do not let a geometry repair conceal a missing
texture pipeline.

Report the audit and stop before opening or changing the asset in Blender.

## G5 — Blender import and diagnosis

Use Blender MCP when connected. Import the immutable source into a new versioned `.blend` without
overwriting the GLB.

Run `scripts/blender_mesh_audit.py` and record:

- vertices, edges, faces, and connected components;
- material slots and UV layers;
- non-manifold edges, holes, degenerates, intersections, and normals;
- bounds and scale;
- anatomy or product-silhouette defects;
- geometry and UV digests.

Do not repair in this stage. Produce diagnosis renders and a proposed repair list, then stop.

## G6 — Blender geometry repair

Repair only the defects approved after G5:

- holes, non-manifold regions, internal faces, degenerates, and normals;
- jagged or unnatural transitions;
- incomplete fingers, limbs, thin parts, and occluded backside geometry;
- material and UV links when repair affects them.

Preserve every accepted version. If topology changes, record that historical Bambu face paint can
no longer be transferred by triangle order.

Re-run the Blender audit, produce before/after evidence, save the repaired master, and stop.

## G7 — Print engineering

Read [references/base-design.md](references/base-design.md) when adding a base or connector.

Keep the character/product separate from:

- character-side base;
- product-side mating insert;
- pins, magnets, fasteners, cutters, and render helpers.

Apply transforms, Boolean cleanup, triangulation, normal recalculation, BVH contact/clearance tests,
and one-connected-manifold-component checks for each printable part.

Do not let Meshy generate precision mating features. Build them parametrically in Blender.

Save the engineered master, export review renders, and stop before Bambu preparation.

## G8 — Bambu preparation and validation

Read [references/bambu-delivery.md](references/bambu-delivery.md).

Color rules:

- GLB PBR textures are screen-rendering data;
- Bambu multicolor printing requires face/region color data in 3MF;
- Meshy's Multi-Color Print output is a candidate 3MF, not an automatic replacement for validated
  Bambu painting;
- transfer historical paint only when vertex and triangle order are unchanged.

Export:

- assembly GLB with materials and embedded textures;
- one STL/GLB per printable base or insert;
- Bambu 3MF when requested.

Run `scripts/validate_delivery.py` and Bambu Studio's own importer. Confirm dimensions, facets,
parts, volumes, manifold status, 3MF integrity, and paint counts where applicable.

Never slice, map physical AMS slots, or send a print job unless the user explicitly authorizes that
separate action. Report importer results and stop.

## G9 — Package and handoff

Use:

```text
VERSION/
├── MASTER.blend
├── workflow-state.json
├── README.md
├── VALIDATION.md
├── inputs/
├── meshy-source/
├── exports/
├── renders/
├── reusable-parts/
└── bambu-studio-delivery/
```

Start documentation from `assets/`. Exclude secrets, scratch exports, temporary cutters, rejected
iterations, `.blend1`, and expired remote URLs. Calculate SHA-256 and test every ZIP.

Final handoff reports:

- accepted source and version lineage;
- Meshy task IDs, settings, and credits consumed;
- Blender repair scope and topology change status;
- dimensions, clearances, part/manifold counts, and color-preservation status;
- Bambu importer result;
- whether slicing, AMS mapping, and printer sending were performed;
- clickable links to the package, master, validation report, Bambu files, reusable parts, and key
  renders.

## Preserve these invariants

1. Keep Meshy source GLBs immutable.
2. Preserve accepted Blender masters and branch forward.
3. Keep precision bases and connectors separate from generated characters.
4. Treat GLB textures and Bambu paint metadata as different systems.
5. Validate in Blender and Bambu Studio.
6. Delete or overwrite only when the user explicitly names the target.
7. Never cross a stage gate without a new user instruction.
