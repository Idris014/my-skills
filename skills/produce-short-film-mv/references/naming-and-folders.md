# Naming, folders, and handoff

Adapt names to an existing project instead of forcing a migration. For a new project, use a single root with numbered phases so paths remain stable.

## Suggested project tree

```text
<PROJECT>/
  00_项目管理/
    brief.md
    asset_lock_manifest.csv
    project_status.md
  01_剧本与音乐/
    source/
    beat_sheet.md
    music_map.csv
  02_镜头设计/
    scene_list.csv
    shot_matrix.csv
    continuity_state.csv
  03_生成提示词/
    image2/
    video/
  04_视觉资产/
    P0资产/
      brand/
      characters/
      scenes/
      props/
      vehicles/
      states/
  05_分镜输出/
    candidates/
    revisions/
  06_分镜审核/
    approved/
    review_log.csv
  07_视频生成/
    prompts/
    candidates/
    accepted/
    generation_ledger.csv
  08_后期与交付/
    edit/
    audio/
    graphics/
    masters/
    manifests/
  99_归档/
```

Keep approved files separate from candidates. Never use a revision-output folder as proof of approval.

## Core names

Use fixed-width episode, scene, and shot numbers:

```text
EP01-SC07-SH011_KF-START_v01.png
EP01-SC07-SH011_KF-END_v02.png
EP01-SC07-SH011_KF-START_FACE_v03.png
EP01-SC07-SH011_KF-START_REGEN_v04.png
EP01-SC07-SH011_Seedance2.0_v02.md
EP01-SC07-SH011_RUN-003_v02.mp4
```

- Increment versions; do not overwrite.
- Do not infer adoption from the highest version. The lock/adopted-version manifest is authoritative only after its referenced file is verified on disk.
- Keep temporary operation tags such as `FACE`, `PATCH`, `SHIPLOGO`, `COMICRESET`, `CONTINUITY`, or `REGEN` in revision folders.
- For an approved folder, prefer the canonical shot/frame name plus version. Record the source candidate in the review log.
- If multiple shots are combined for one video request, retain a combined filename such as `EP01-SC06-SH005-SH006_Seedance2.0_v01.md` and keep individual shot prompts/index rows as the canonical records.

## Asset lock ID

Assign an immutable batch ID after P0 review, for example:

```text
<PROJECT>-P0-YYYYMMDD-R1
```

Record all anchor paths and hashes under that ID. A material identity, scene, costume, prop, logo-master, or style change creates a new revision. Do not reuse an old lock ID after changing its members.

## Review log

Use at least:

```text
SHOT_ID,FRAME,CANDIDATE,VERSION,ASSET_LOCK_ID,PREVIOUS_SHOT,NEXT_SHOT,
IDENTITY,COMPOSITION,ACTION,CONTINUITY,BRAND,TECHNICAL,STATUS,ISSUES,
ADOPTED_FILE,REVIEWER,REVIEWED_AT
```

Status values: `PENDING`, `SELF-QA`, `REVISE`, `BLOCKED`, `REVIEWED`, `LOCKED`.

## Video generation ledger

Use at least:

```text
SHOT_ID,TIMECODE,DURATION,MODEL,MODEL_VERSION,RUN_ID,PROMPT_FILE,
START_FRAME,END_FRAME,ASSET_LOCK_ID,OUTPUT_FILE,STATUS,REJECT_REASON,
ADOPTED_FILE,GENERATED_AT
```

## Package manifest

List relative path, role, version, byte size, checksum, status, and source authority for every delivered file. Include a status note that distinguishes:

- complete and adopted;
- generated but unapproved;
- prompt-ready but not generated;
- blocked by missing assets, permissions, quotas, or decisions;
- post-only work still required.

Compress the single clean project root after the manifest passes. Keep caches, `.DS_Store`, temporary exports, and superseded candidates out of the delivery archive unless the user asks for a full working archive.

Before packaging, perform a three-way reconciliation: actual filesystem paths and hashes, lock/adopted-version manifest entries, and shot/prompt/video index rows. Do not trust a README or historical completion note by itself.
