# Workflow and phase gates

Use this reference to plan or audit a complete short-film or MV production.

## Production state model

| Phase | Required outputs | Exit gate |
|---|---|---|
| 0. Brief | approved source list, delivery spec, visual/audio intent, constraints | material choices that change scope are resolved |
| 1. Breakdown | beat sheet, scene list, shot matrix, continuity state table, asset registry | every shot has one purpose, duration, state delta, and required keyframes |
| 2. P0 assets | identity, scene, prop, vehicle, costume/brand, UI/light/effect anchors | representative boards pass identity and geometry review |
| 3. Storyboards | Image2 prompts, reference lists, generated START/END frames, frame manifest | every required frame exists and is reviewable |
| 4. Review | issue log, revisions, approved frames, lock manifest | all used frames pass identity, spatial, action, state, and technical QA |
| 5. Video prompts | one prompt per shot, prompt index, failure-degradation plan | every planned shot has valid approved references and a complete prompt |
| 6. Generation/edit | calibration outputs, run ledger, accepted clips, edit timeline | every timeline slot has an accepted clip or documented substitute |
| 7. Delivery | final master, stems/versions if requested, manifests, status note, package | all claims reconcile to existing files and all blockers are disclosed |

Do not skip a gate by relabeling a draft. If a later phase begins early, mark the output `TEST` or `SELF-QA`, not `LOCKED`.

## Shot matrix minimum fields

Use at least:

```text
SHOT_ID | SCENE | DURATION | PURPOSE_OR_MUSIC_BEAT | CHARACTERS | PROPS
CAMERA | AXIS_AND_SCREEN_DIRECTION | START_STATE | END_STATE | ACTION_DELTA
KF_START | KF_END_REQUIRED | DIALOGUE_OR_LYRIC_TIME | SOUND | POST_ONLY
ASSET_LOCK_ID | STATUS | NOTES
```

Keep a separate row for each final video task, even if two tasks will later be merged into one generation request. Record merges explicitly so the one-to-one shot index remains auditable.

## Decide START versus END

Require `KF-START` for every visual shot. Add `KF-END` when any of these must land precisely:

- subject or camera moves to a different spatial endpoint;
- a hand picks up, transfers, releases, deletes, presses, points to, or reveals something;
- body contact begins, ends, or changes;
- a door, hatch, terminal, screen, alarm, light, weather, vehicle, or effect changes state;
- composition, scale, screen direction, or focus target changes materially;
- a transformation, reveal, or match cut depends on a specific final silhouette.

Use only START when the shot is a stable hold, insert, dialogue/reaction with no material geometry delta, atmospheric loop, or camera motion whose endpoint is not composition-critical.

An absent END is not automatically an error. The shot matrix is authoritative. An END without a START is an error.

## Continuity pass test

A pair passes only when the intentional delta is easy to state and every other lock remains stable.

1. **Identity lock:** same person/vehicle/object; no age, face, hair, build, costume, or mark drift.
2. **Camera lock:** same lens logic, axis, height, crop logic, horizon, and movement path.
3. **Spatial lock:** same scene geometry, screen order, negative space, and prop locations.
4. **Performance lock:** hands, gaze, pose, contact, and ownership change only as scripted.
5. **State lock:** door, UI, hologram, alarm, light, weather, and effect state follow the state table.
6. **Delta lock:** START can physically and narratively reach END within the shot duration.

Reject a technically attractive frame when any non-target lock changes.

## Narrative short planning

- Build the beat sheet from cause, decision, consequence, and emotional turn.
- Divide dialogue by reaction and action; avoid asking one generation to perform a long multi-speaker scene.
- Preserve eyelines, screen direction, prop ownership, and body contact through coverage.
- Give dialogue shots a precise speaking character, time window, mouth state for listeners, and post-dubbing plan.
- Use inserts or reaction shots to hide difficult hand, lip-sync, or continuity transitions.

## MV planning

Create a music map before the shot list:

```text
TIMECODE | SECTION | BAR_OR_BEAT | ENERGY | VOCAL | LYRIC_THEME | VISUAL_FUNCTION | MOTIF
```

- Map intro, verse, pre-chorus, chorus/drop, bridge, breakdown, solo, and outro as applicable.
- Establish a visual rule for each section and a controlled transformation across repeats.
- Alternate performance, narrative, environmental/B-roll, and abstract motif shots.
- Reserve the strongest scale, motion, colour, or VFX changes for genuine musical peaks.
- Use beat accents for action/camera endpoints; do not cut mechanically on every beat.
- Track wardrobe, instrument, microphone, stage/set, light state, and lip-sync continuity.
- If lyrics are supplied, use their meaning and timecode without reproducing more text than needed in production documents.

## Calibration and batch strategy

Before a large batch, test:

1. one low-risk establishing/environment shot;
2. one representative close or multi-character identity shot;
3. one demanding motion/effect or lip-sync shot.

Freeze the accepted settings and reference order. Generate in scene order or music time order when outputs depend on previous state. Parallelize only independent shots after the same `ASSET_LOCK_ID`, naming rules, reference mapping, and acceptance rubric are shared.

## Delivery gate

Reconcile the following counts and paths:

- unique final shot IDs;
- required START/END frame slots versus approved files;
- prompt documents versus shot IDs;
- generated/accepted clips versus edit timeline slots;
- source audio and final audio duration;
- exact brand/UI/subtitle assets used in post;
- final master, alternate versions, status note, manifest, and checksums.

Use `COMPLETE` only when every required deliverable exists. Otherwise report `PROMPT-READY`, `FRAME-READY`, `VIDEO-PARTIAL`, `BLOCKED`, or another evidence-backed status.
