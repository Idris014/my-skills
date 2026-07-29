---
name: meshy2bambu
description: Convert reference images, text descriptions, multiview sets, or existing AI-generated GLB/OBJ/STL/3MF assets into repaired, printable Blender and Bambu Studio deliverables. Use this skill whenever the user wants image-to-3D, Meshy generation or Multi-Color Print, Blender mesh repair, texture preservation, texture-to-print-color conversion, multicolor face regions or 3MF preparation, or a printable base, plinth, stand, pedestal, magnetic base, support platform, connector, mounting feature, or Bambu delivery—even if Meshy is not named. Includes a non-destructive parameterized base builder with auto-fit round/elliptical/rounded-rectangle plates, magnet pockets, locating holes, contact checks, separate exports, and a machine-readable report. Default to a compact three-phase workflow and continue autonomously; pause only for unapproved paid generation, consequential geometry/design choices outside the request, or physical print actions.
compatibility: Meshy API with MESHY_API_KEY when generation is needed, imagegen, Blender 4.x with Blender MCP or background Python, Python 3.10+ with NumPy for 3MF fallback audits, Bambu Studio CLI, zip/unzip, and standard filesystem tools.
---

# Meshy2Bambu

Turn a description, reference, multiview set, or existing mesh into a validated Blender/Bambu
deliverable with as little ceremony as the risk allows.

## Operating style

Use one continuous workflow when the request is sufficiently clear. Do not force the user through
an intake questionnaire or stop after routine inspections.

- Reuse information already present in the conversation or project.
- If a missing choice materially changes the result, ask one short bundled question.
- Treat an explicit request such as “用 Meshy 生成并交付给 Bambu” as authorization for the normal
  generation, repair, validation, and packaging operations it names.
- Group related findings and fixes. Avoid separate approval turns for reference intake, multiview
  skip, source audit, Blender import, validation, and packaging.
- Keep the user informed during long operations, but continue working unless a checkpoint below is
  triggered.

## Three-phase workflow

```text
Phase 1  Source and generation
    ↓
Phase 2  Blender repair and print engineering
    ↓
Phase 3  Bambu validation and handoff
```

Complete all applicable phases in the same task unless the user asks for only one phase or a
checkpoint requires a decision.

### Phase 1 — Source and generation

Choose the shortest valid route:

1. **Existing 3D asset:** archive an immutable copy and inspect it.
2. **Approved image(s):** use Image to 3D for one image or Multi-Image to 3D for 2–4 consistent
   images.
3. **Description only:** generate one clean full-subject reference with imagegen, then continue to
   Meshy when the user's request already authorizes 3D generation.

Ask about multiview only when it is genuinely undecidable and affects the requested fidelity.
Otherwise:

- use supplied 2–4 views when consistent;
- use Meshy-generated multiview when requested;
- use the best single image when the user accepts inference or no multiview is available.

When calling Meshy, read [references/meshy-api.md](references/meshy-api.md). Prefer textured GLB,
PBR enabled, 4K textures, no auto-size, and no remesh until thin parts and anatomy are accepted.
Archive the request, task result, downloaded source, task ID, settings, credits, and SHA-256. Never
persist `MESHY_API_KEY`.

Run a compact source check before Blender:

- file parses and is the expected format;
- subject is present and not obviously truncated;
- mesh/node counts and bounds are plausible;
- materials, UVs, and embedded textures exist when color is expected.

Use `scripts/inspect_glb.py` for GLB. If required color or geometry is missing, stop once with a
clear blocker instead of continuing into repair.

For a colored asset bound for Bambu, also run `scripts/inspect_color_partition.py`. Classify it as
texture-only, multi-material, vertex-colored, face-painted 3MF, or unpainted. A GLB that looks
colored but has one textured material and no `COLOR_0` is a texture source, not a pre-partitioned
print file.

### Phase 2 — Blender repair and print engineering

Prefer Blender MCP when connected; otherwise use versioned Blender background Python. Never
overwrite the immutable source.

Import, diagnose, repair, and engineer in one phase when the changes are already within the user's
request. Check only what affects the intended result:

- readable geometry, normals, degenerates, gross holes, and obvious non-manifold defects;
- requested anatomy or silhouette corrections;
- material/UV links when textures must be preserved;
- units, dimensions, applied transforms, centering, and print-bed contact;
- contact and clearance for bases, magnets, pins, inserts, splits, or mating parts.

Use `scripts/blender_mesh_audit.py` for a full audit only when the asset is damaged, generated,
high-risk, or intended for final printing. A simple material edit or already-validated branch does
not need the entire audit repeated.

Repair principles:

- preserve accepted source versions and branch forward;
- avoid global remesh or decimation when a local repair is sufficient;
- keep characters/products separate from precision bases, inserts, pins, magnets, and cutters;
- build precision mating features parametrically in Blender, not in Meshy;
- record topology changes because historical Bambu face paint can transfer by triangle order only
  when vertex and triangle order remain compatible.

#### Base addition module

When the request includes a base, plinth, stand, pedestal, support platform, magnet pocket, or
mounting interface, read [references/base-design.md](references/base-design.md) and create a
`BASE-SPEC.json` from [assets/BASE-SPEC.template.json](assets/BASE-SPEC.template.json).

Use `scripts/blender_add_print_base.py` for a plate that can be expressed as a circle, ellipse, or
rounded rectangle. It auto-fits the chosen support objects, keeps the character/product geometry
untouched, can cut a bottom-opening magnet pocket and top locating holes, exports the base
separately, saves a new Blender master, and writes a geometry/contact report. Use Blender MCP for
a hidden saddle, sculpted support, asymmetric silhouette, hand/hair/skirt contact, or any design
that needs semantic surface selection; still record the same base specification and validation
fields.

Apply these defaults only when they do not contradict the request:

- round display base, `8 mm` high, `4 mm` XY margin, `0.6 mm` edge bevel, and `0.3 mm` intentional
  support overlap;
- separate `Print_Base` object with a neutral material; do not Boolean-union it into the character;
- no magnet pocket or locating holes unless the user requests a detachable or magnetic interface;
- for an explicitly magnetic small-character base with no dimensions supplied, propose the proven
  `Ø12 × 3 mm` interface from the reference and pause before cutting it because magnet inventory
  and mating-side constraints are physical design choices.

Never auto-fit from the whole character when feet must float. Fit from named support objects or a
reviewed low-contact footprint, shift the base as required, and list feet/shoes in
`float_objects`. A successful base operation must prove:

- the protected character/product mesh signatures are unchanged;
- the base is a closed, single-component solid;
- required support contacts intersect and expected-floating parts do not;
- magnet and pin clearances match the recorded specification;
- the standalone base export and the new Blender master reopen/import successfully.

Run BVH/contact/clearance analysis only for interacting parts. Produce one orthographic side or
three-quarter render that makes contact and foot clearance visible; a full turntable is optional.

### Phase 3 — Bambu validation and handoff

Read [references/bambu-delivery.md](references/bambu-delivery.md) when delivering 3MF, transferring
paint, or preparing multicolor output.

When the source is a colored GLB without Bambu face paint, read
[references/texture-to-print-color.md](references/texture-to-print-color.md). Preserve two distinct
outputs:

1. a correctly scaled, embedded-texture `*_TEXTURE_SOURCE.glb` as the canonical editable and
   appearance master;
2. a face-colored 3MF candidate for Bambu Studio.

Prefer Meshy's separate **Multi-Color Print API** when the user authorizes its 10-credit task:

1. finish geometry repair and physical scale before color conversion;
2. call `POST /openapi/v1/print/multi-color` with the successful upstream `input_task_id`, or the
   final GLB as `model_url`;
3. set an intentional `max_colors` from 1–16 and record it;
4. preserve the returned 3MF as a raw Meshy candidate;
5. audit face-color coverage and palette counts, import it in Bambu Studio, clean semantic errors
   and small islands, then save a new final 3MF.

The ordinary `target_formats: ["3mf"]` option on Meshy generation endpoints is not a substitute
for `print-multi-color`; it may produce a geometry/container export without printable face-color
regions. If paid Meshy conversion is not authorized or available, use Bambu Studio's native
`Texture-to-Color Painting / 纹理转颜色` branch instead. Save its automatic output as a candidate
before cleanup.

Transfer character paint to a later base only when vertex and triangle order remain compatible.
If geometry or topology changes after conversion, regenerate the candidate from the new final GLB
instead of assuming old face indices still match.

If a task succeeds but local download or archiving fails, resume the same task ID with
`meshy_api.py multi-color-resume`; never submit a replacement paid task merely to recover an
existing result.

Automatic texture clustering is a starting point. It does not replace semantic review of eyes,
hair/skin boundaries, fingers, clothing edges, shoe soles, and small accessories. If the user wants
specific regions merged—such as eyes into skin—apply that rule before final validation.

Export only the formats the user needs:

- textured assembly GLB for appearance and archival;
- flat-color GLB when useful for color review;
- STL/GLB for genuinely separate printable parts;
- Bambu 3MF when Bambu face/region color or project delivery is requested; keep raw automatic and
  cleaned final versions separate.

Remember that GLB PBR textures and Bambu face paint are different systems. Do not claim that a
textured GLB is automatically multicolor-print ready.

Run one final validation pass:

- reopen the final Blender master;
- confirm dimensions, object/part counts, triangles, and applied transforms;
- run `scripts/inspect_color_partition.py` on the source and final 3MF when color is involved;
- run `scripts/validate_delivery.py` and Bambu Studio's importer;
- if Bambu's headless `--info` path crashes but the GUI loads the project, record the GUI evidence
  and run `scripts/audit_3mf_mesh.py` for an independent edge-manifold audit instead of
  misreporting the importer crash as non-manifold geometry;
- test 3MF/ZIP integrity;
- verify paint counts only for multicolor output;
- verify per-part manifold/contact/clearance only where those properties matter.

Package the result after validation. Start documentation from `assets/`, but include only relevant
folders and files:

```text
VERSION/
├── MASTER.blend
├── README.md
├── VALIDATION.md or VALIDATION.json
├── inputs/
├── exports/
├── renders/
├── bambu-studio-delivery/   # when applicable
└── SHA256SUMS
```

Do not create empty `meshy-source`, `reusable-parts`, or connector folders when they do not apply.
Exclude secrets, `.blend1`, scripts, scratch exports, temporary cutters, rejected iterations, and
expired remote URLs. Test the final ZIP and report its SHA-256.

## Checkpoints: pause only when needed

Pause and request one explicit decision in these cases:

1. **Unapproved cost:** a Meshy/API call will consume credits and the user did not already ask to
   run that generation.
2. **Consequential choice outside scope:** the next action would delete accepted data, replace
   textures, globally remesh/decimate, alter accepted anatomy, invalidate historical paint, or
   commit an ambiguous base/magnet/connector design not specified by the user.
3. **Physical print action:** slicing for a specific printer, mapping physical AMS slots, or sending
   a print job always needs separate authorization.
4. **Blocking evidence:** required source geometry/color is absent, validation fails in a way that
   changes the design, or an external service cannot continue.

Do not pause merely because a phase ended. A user request for an end-to-end result authorizes
continuing from Phase 1 through validated packaging, subject to the checkpoints above.

## Proportional checks

Always check:

- immutable input and SHA-256;
- final dimensions and intended scale;
- final master reopens;
- required materials/textures or Bambu colors are present;
- the color-source classification for colored Bambu-bound assets;
- Bambu importer result for Bambu-bound deliverables;
- archive integrity and hashes for the final package.

Check only when relevant:

- multiview identity consistency — when multiview is used;
- geometry/UV digests — when preserving textures or transferring historical paint;
- complete non-manifold/component analysis — when repairing or claiming print readiness;
- BVH contact and clearance — for interacting parts;
- per-color triangle counts — for multicolor 3MF;
- before/after close-ups — for visible geometry repair.

Avoid repeating an expensive check when the exact validated geometry has not changed. Reuse the
prior audit and verify the changed layer only.

## Lightweight job record

For long, paid, or multi-session jobs, maintain a concise `JOB-RECORD.json` containing:

- immutable inputs and hashes;
- Meshy task IDs, settings, and credits when used;
- accepted source and final Blender master;
- geometry/topology and color changes;
- final dimensions and validation results;
- output paths and whether slicing, AMS mapping, or printer sending occurred.

Do not require a per-step approval ledger for new jobs. `scripts/workflow_state.py` remains only for
resuming legacy projects that already use the old G0–G9 state format.

## Final response

Lead with the deliverable. Include clickable links to the final package, Blender master, Bambu
file, validation record, and key render when available. Summarize:

- source route and Meshy credits/task ID, if any;
- repair and topology impact;
- dimensions, parts, manifold result, color-source classification, and print-color status;
- whether Meshy Multi-Color Print or Bambu Texture-to-Color was actually run, its palette size,
  and whether its raw candidate was cleaned;
- whether slicing, AMS mapping, and printer sending were performed.

## Invariants

1. Keep source GLBs immutable.
2. Preserve accepted Blender masters and branch forward.
3. Keep precision parts separable and dimensioned.
4. Treat textures and printable color metadata as different systems.
5. Validate final Bambu-bound assets in Bambu Studio.
6. Delete or overwrite only when the user clearly names the target.
