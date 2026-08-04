# Single build-archive contract

Use this reference for every Slides task that creates or changes files. The goal is to make the work reproducible and keep the project clean: all agent-created intermediate state belongs to one job root.

## Create the job root first

Before the first write, run:

```bash
python scripts/workspace_guard.py init \
  --project-dir "/absolute/path/to/project" \
  --deck-slug "descriptive-deck-name"
```

If the user names a specific archive parent, add `--build-parent "/absolute/path/to/archive-parent"`. Otherwise the script creates:

```text
<project>/.slides-work/<deck-slug>-<timestamp>/
```

Capture the absolute `job_root` returned by the script and use it for the entire task. Do not create a second build root for a later phase.

## Required structure

The initializer creates:

```text
<job-root>/
├── 00_inventory/
├── 10_script/
├── 20_research/
├── 30_assets/
│   ├── searched/
│   ├── generated/
│   └── selected/
├── 40_layout/
├── 50_pptx/
├── 55_demos/
├── 60_renders/
├── 70_qa/
├── 80_keynote/
├── 90_final-staging/
├── logs/
└── tmp/
```

Subdirectories within these folders are allowed. All of them remain descendants of the same job root.

## Path rules

All agent-created intermediate files must stay under the job root, including:

- Inventories, extracted text, template inspection output, and source ledgers.
- `deck-script.md`, `change-script.md`, revision notes, and timing calculations.
- Search result notes, downloaded candidates, generated images, crops, masks, and selected assets.
- Layout maps, design tokens, wireframes, theme files, and font reports.
- Build scripts, generated source code, dependency caches that can be redirected, and logs.
- Draft PPTX files, temporary exports, speaker-note injection files, and object-inspection dumps.
- HTML demos and their assets.
- Slide renders, montages, thumbnails, screenshots, and visual-diff files.
- QA reports, overflow or overlap reports, validation JSON, and review notes.
- Keynote conversions, Keynote exports, conversion screenshots, and repair copies.
- Final artifacts before handoff.

Use the job root as the working directory whenever practical. Point tool output arguments to descendants of the root. For commands that honor a temporary-directory setting, direct it to `<job-root>/tmp/`. If a tool cannot keep its explicit artifacts inside the job root, choose another route rather than accepting scattered output.

The only files allowed outside the job root are:

- User-supplied source files, which remain in place and read-only unless in-place editing was explicitly requested.
- Verified final deliverables copied to the exact user-requested destination.

Do not use the project root, current working directory, Downloads, the installed skill directory, or an unrelated temporary directory for convenience.

## Phase mapping

- Store read-only inventory records in `00_inventory/`.
- Store the canonical detailed script and revisions in `10_script/`.
- Store claim research and source notes in `20_research/`.
- Store all image candidates and prompts in `30_assets/`.
- Store the visual contract and slide-to-layout map in `40_layout/`.
- Store editable PPTX source, draft generations, and authoring helpers in `50_pptx/`.
- Store companion HTML work in `55_demos/`.
- Store all render passes in `60_renders/pass-<n>/`.
- Store structural and visual QA in `70_qa/`.
- Store Keynote conversions and conversion review in `80_keynote/`.
- Copy only verified handoff candidates into `90_final-staging/`.
- Store command output and diagnostics in `logs/`.

## Final staging and handoff

1. Complete PPTX, Keynote, demo, and PDF verification inside the job root.
2. Place the exact verified files in `90_final-staging/`.
3. Copy only the requested final artifacts from staging to the user’s final destination.
4. Run the workspace audit, listing each copied final file with `--allow-final`.
5. If the audit reports an unexpected file outside the archive, investigate it. Move only files known to be created by this Slides job into the appropriate job-root folder; never move or delete unrelated user files.
6. Re-run the audit until it passes or report a specific external-tool limitation.
7. Include the absolute job-root path in the final response.

Do not delete the job root by default. It is the production archive. Remove it only when the user explicitly requests cleanup and the exact target has been revalidated.

## Audit example

```bash
python scripts/workspace_guard.py audit \
  --build-root "/absolute/path/to/job-root" \
  --allow-final "/absolute/path/to/final-deck.pptx" \
  --allow-final "/absolute/path/to/final-deck.key"
```

The audit compares the project against the baseline recorded at initialization. A nonzero exit means that new or modified project files exist outside the job root and the explicitly allowed final paths.
