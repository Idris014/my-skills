---
name: produce-short-film-mv
description: End-to-end AI production workflow for narrative shorts, music videos, opening films, trailers, and episodic short-form video. Use when Codex needs to turn a script, treatment, song, lyrics, storyboard, or an existing media project into locked visual assets, Image2-ready storyboard prompts, continuity-reviewed keyframes, Seedance 2.0-ready shot prompts, generation ledgers, edit plans, QA reports, or a packaged handoff; also use to resume, audit, repair, or standardize an in-progress AI film project with identity, scene, prop, logo, badge, START/END, and cross-shot continuity requirements.
---

# Produce Short Film / MV

## Work as the production controller

Own the route from source material to auditable shot assets. Treat every approved image, identity, scene, prop, costume mark, sound cue, and state transition as a controlled production asset rather than an informal reference.

Lead with the current outcome and next gate. Make reasonable recommendations when the user delegates choices. Ask only about missing choices that materially alter story, music timing, legal authority, budget, aspect ratio, delivery format, or external publishing.

Preserve user originals. Create versioned siblings, never silently overwrite an input or delete history. Never label a frame `LOCKED`, a prompt `PASS`, or a project complete without checking the corresponding files and gate evidence.

When actual image generation or editing is requested, use the available image-generation capability. When generation must occur in a web-only product, prepare one copy-paste prompt, an ordered reference-photo list, and an exact output filename per image.

## Route the request

1. For a new project, begin at intake and asset planning.
2. For an existing project, inspect the project tree, manifests, adopted-version records, approved outputs, and unfinished gates before changing anything. Treat filenames and README status as claims: reconcile the filesystem, lock manifest, and adopted-version record before selecting an input.
3. For storyboard creation, use the Image2 workflow and produce only the required START/END frames.
4. For face, hair, badge, logo, ship, or comic corrections, choose a local edit or clean regeneration based on the repair threshold below.
5. For video generation, use only reviewed frames and generate one shot task at a time.
6. For an MV, derive the shot structure from the music map as well as the visual narrative.
7. For delivery, audit names, dimensions, versions, prompt coverage, video coverage, and package manifests before declaring completion.

Read the resource that matches the task:

- Read [references/workflow-and-gates.md](references/workflow-and-gates.md) for phase gates, START/END decisions, short-film versus MV planning, and final delivery.
- Read [references/continuity-and-brand.md](references/continuity-and-brand.md) for identity, left/right, occlusion, scene-state, prop, logo, badge, and exact-artwork rules.
- Read [references/image2-prompts.md](references/image2-prompts.md) before writing Image2 prompts, editing storyboards, building a single anchor board, or diagnosing reference failures.
- Read [references/seedance2-prompts.md](references/seedance2-prompts.md) before writing or revising Seedance 2.0 prompts, timelines, dialogue, sound, or failure-degradation plans.
- Read [references/naming-and-folders.md](references/naming-and-folders.md) before scaffolding, reorganizing, moving approved files, merging prompts, or packaging a project.

## Run the production workflow

### 0. Lock the brief

Record the following in a brief or manifest:

- project type: narrative short, MV, opening film, trailer, or hybrid;
- source authority: script version, song/audio version, treatment, lyrics, brand package;
- target duration, aspect ratio, resolution, frame rate, language, dialogue/voice plan, delivery platform;
- visual grammar, realism level, camera language, colour arc, prohibited content, and exact brand assets;
- intended image and video engines, their current input limits, and which work remains manual or post-produced.

For an MV, also record timecode, BPM if known, section boundaries, beat accents, performance/lip-sync requirements, and recurring visual motifs. Do not quote or invent lyrics that were not provided or licensed by the user.

### 1. Break down story and sound

Create a scene list, beat sheet, shot matrix, asset registry, and continuity-state table. Give each shot one clear narrative purpose and one primary motion. Separate complex multi-character actions into shots that a video model can execute reliably.

For each shot specify:

- shot ID, duration, story or musical beat, scene, characters, props, state before, state after;
- camera size, lens feeling, height, angle, movement, axis, screen direction, and negative space;
- performance, hands, gaze, contact, prop ownership, dialogue/sound timing, and post-only elements;
- required `KF-START`, optional `KF-END`, and the exact intentional delta between them.

Use START only for a static hold, insert, dialogue beat with no material geometry change, or a shot whose ending can safely be derived from motion instructions. Use START+END when the shot changes position, contact, hand/prop state, door state, screen direction, camera endpoint, lighting/alarm state, hologram state, transformation, or any geometry that must land precisely.

For high-risk contact or transformation, add a production `KF-MID` or split the generation into smaller units without inventing a new story beat. Keep the canonical shot ID and record the production split.

### 2. Build and approve P0 anchors

Create identity turnarounds and face anchors, expression/state boards, scene-space boards, props, vehicles, costumes, brand artwork, UI style, lighting states, and special-effect states before mass storyboard generation.

Assign one authority to each scope. A face anchor controls identity, not pose. A shot frame controls composition and performance, not an incorrect face. A scene board controls architecture, not character placement. Exact logos and badge artwork control their own pixels and must not leak into unrelated objects.

Do not batch dependent frames until the master anchor passes. For a ship logo, approve one canonical hull installation first; use that frame for every later ship view so normalized size, position, perspective, edge distances, and material relationship remain consistent.

### 3. Generate Image2 storyboard frames

Generate one image per task. Default to 16:9 and the project resolution; do not reproduce contact-sheet labels, reference-board borders, or multiple views in the output.

Order references by authority. For an END task, make the same shot's adopted START the first reference and derive the END from it; never redraw an END independently. For a START task, use:

1. current shot or composition panel;
2. preceding adopted continuity frame when needed;
3. approved scene anchor;
4. only the visible characters' named identity anchors;
5. only the relevant uniform or brand assets.

Keep reference count minimal. If multiple high-resolution inputs cause request errors or identity-weight conflicts, create one compressed labeled anchor board and submit that single image. The board is a source map, never the target layout.

Generate scene-by-scene. Review the first representative shot before starting a large batch. Freeze the approved reference set and `ASSET_LOCK_ID` for the batch.

### 4. Repair with the smallest stable method

Choose the repair path deliberately:

- Use a localized edit when composition, scene, pose, hands, contact, and identities are already stable and only a visible face detail, hair detail, badge surface, logo surface, or colour integration is wrong.
- Use staged local edits when identity and uniform details both need work: correct the face/hair first, review, then correct badge/logo placement.
- Use a clean single-anchor regeneration when the wrong identity, scene geometry, character count, pose, contact, brand side, or multiple correlated details cannot be isolated reliably.
- Use exact non-generative compositing for final logo and badge strokes whenever pixel fidelity matters. Generated approximations may establish placement and fabric integration but are not final brand masters.

Apply the three correction categories independently:

1. **Character:** distinguish every named person; lock face, hair, age, build, glasses/earrings, uniform, chest logo, sleeve badge, rank tabs, and watch only in genuinely visible areas.
2. **Ship:** preserve the approved vessel; inherit logo size, position, perspective, and spatial relation from the canonical ship-logo master.
3. **Comic world:** create new comic-world objects first. Do not transform or migrate live-action ship, captain, ocean, ruin, UI, or plot assets unless the brief explicitly calls for that relationship.

### 5. Review continuity and approve

Compare each frame against its shot specification, identity/asset anchors, paired START/END frame, preceding shot, and following shot. Check:

- identity, hair, costume, visible marks, left/right, occlusion, and body proportions;
- axis, screen order, camera, crop, horizon, scene geometry, lighting, and depth;
- pose, hands, fingers, gaze, body contact, prop ownership, and intended action delta;
- door, terminal, UI, alarm, hologram, weather, vehicle, and special-effect state;
- image size, filename, version, openability, and absence of unwanted text or watermark.

Use `PASS`, `REVISE`, or `BLOCKED`. Move or copy a candidate to the approved folder only after `PASS`; keep the original and earlier accepted versions. A visual improvement is not a pass if it introduces a continuity jump.

Run the bundled audit when appropriate:

```bash
python3 scripts/audit_storyboards.py --root <storyboard-or-approved-folder> \
  --expected-csv <frame-slot-or-lock-manifest.csv> \
  --expected-width <manifest-width> --expected-height <manifest-height>
```

Use `--prefix EP01-SC07` to audit a scene and `--json` for machine-readable output. Treat START-without-END as informational; only the shot matrix can decide whether an END is required.

### 6. Write video prompts

Create one prompt document per shot. Bind the latest approved START and, when specified, END frame. Include metadata, reference list, action, camera, performance, environment dynamics, exact timeline, dialogue/sound, continuity, hard negatives, post-only elements, failure degradation, and QA.

Keep the requested motion smaller than the visual locks can support. For dialogue, identify exactly who speaks and when; keep non-speakers' mouths still. Leave exact logos, readable UI, numbers, code, subtitles, controlled flashes, and long-form dialogue refinement to post unless the user explicitly accepts generation risk.

For an MV, bind every shot to a time range and musical function. Use section-level motifs and beat accents without forcing a cut on every beat. Separate performance, narrative, environment/B-roll, and abstract-motif shots; maintain wardrobe, set, light, and lip-sync continuity across repeats.

### 7. Calibrate, generate, assemble, and package

Test a low-risk establishing shot, one representative character shot, and one effect-heavy shot before a full video batch. Record run ID, model/version, inputs, prompt version, output, status, rejection reason, and adopted file.

Generate in narrative or music-time order when state continuity matters. Review each shot before using it as a reference for a dependent shot. Assemble picture, dialogue/voice, music, sound design, exact brand compositing, UI, subtitles, colour, and finishing as separate controlled layers.

Before delivery:

- reconcile the physical files, lock/adopted-version manifest, shot matrix, prompt index, generated video ledger, and edit timeline;
- confirm every used asset is the latest approved version and every claimed output exists;
- archive superseded candidates without mixing them into the final package;
- include a project-status note listing complete, pending, blocked, and post-only items;
- package the complete project with a manifest and checksums when required.

## Guardrails

- Never mirror an image to solve a badge-side problem.
- Interpret left/right as the subject's own body or the vehicle's defined heading, not the viewer's screen side.
- Do not reveal hidden details or sharpen deliberately distant/blurred characters.
- Do not let a character identity reference change pose, expression intensity, camera, or scene.
- Do not let a shot reference preserve an incorrect identity when an approved identity anchor exists.
- Do not accept approximate brand marks as exact final artwork.
- Do not invent readable UI, code, subtitles, lyrics, or production status.
- Do not select a frame merely because it has the highest version number; use the adopted/locked record and verify that file exists.
- Do not reorganize or delete project history without explicit authorization; prefer a clean delivery view plus an archive.
