# End-to-end workflow

Use this reference for multi-slide creation, substantial edits, course-deck extensions, and reference-template work.

## 0. Initialize the single build archive

Read [workspace-archive.md](workspace-archive.md) and run `scripts/workspace_guard.py init` before creating any intermediate file. Capture the returned absolute job-root path.

Use only these job-root descendants throughout this workflow:

- `00_inventory/` for input and template inspection records.
- `10_script/` for scripts and revisions.
- `20_research/` for source records.
- `30_assets/` for searched, generated, and selected images.
- `40_layout/` for the visual contract and layout map.
- `50_pptx/` for editable PPTX work.
- `55_demos/` for companion HTML.
- `60_renders/` for all render passes.
- `70_qa/` for QA reports.
- `80_keynote/` for Keynote conversion and review.
- `90_final-staging/` for verified handoff candidates.
- `logs/` and `tmp/` for diagnostics and controllable temporary files.

Do not create phase-specific scratch folders beside this root.

## 1. Inventory the inputs

Create a read-only inventory and store its records in `00_inventory/`:

- Source files, formats, page/slide counts, dimensions, and modification state.
- Which file contains content and which controls visual style.
- Existing final outputs that must be preserved.
- Fonts, images, logos, citations, notes, and interactive demos.

When the user requests style continuity or relevant local course materials exist, follow [text-and-layout-style.md](text-and-layout-style.md) and create `00_inventory/reference-style-corpus.md`. Analyze writing voice, explanatory moves, layout grammar, and pacing. Do not import fonts, backgrounds, colors, logos, or decoration unless the user separately asks for visual template matching.

For a PDF, render every page. For a PPTX, inspect every slide and its layouts. For a Keynote file, prefer an exported PPTX or PDF for systematic inspection while preserving the original `.key`.

This stage is read-only. Do not author slides, place shapes, assign slide-specific layouts, or start presentation-generation code.

## 2. Write the complete content script

Read and follow [script-first.md](script-first.md). Create `10_script/deck-script.md` or `10_script/deck-script.txt` before layout work begins.

The script must include:

- Production brief, audience change, duration, language, tone, central takeaway, and deliverables.
- Narrative arc and timing.
- A complete entry for every slide.
- Detailed presenter narration.
- Concise visible copy.
- Evidence, source needs, interactions, and transitions.
- A visual brief with search queries, desired composition, aspect ratio, crop, and text-safe area.
- A completed `[SCRIPT GATE]`.

The script replaces a title-only outline or lightweight content map. If the script cannot stand on its own as a teaching or presentation plan, it is not complete. Keep timing in the internal ledger, presenter choreography in notes, and mechanical production labels out of visible copy.

## 3. Pass the script gate

Check coverage, timing, title-sequence logic, narration continuity, visible-copy density, sources, visual briefs, and closing synthesis. Resolve failures in the script. Do not proceed to layout with an incomplete script.

For a multi-day course, preserve continuity while giving each day a distinct learning arc:

- Day opening: connect to prior knowledge.
- Core progression: one conceptual step per slide.
- Practice: demonstrations, questions, or small tasks.
- Closing: synthesis and bridge to the next session.

## 4. Build and inspect the asset candidate pool

Create `30_assets/asset-ledger.txt` or `30_assets/asset-ledger.md`. For every scripted slide with a visual opportunity:

1. Run several targeted searches with the available image-search capability (`image_query` or equivalent), derived from the visual brief.
2. Prefer primary or official sources, authentic archives, reputable libraries, and assets with clear reuse terms.
3. Do not stop at the first usable result. Collect at least 3–5 viable candidates per image-bearing slide when practical, and more for cover, hero, or other high-impact imagery when meaningful alternatives exist. Aim for choice, not final-slide clutter.
4. Record for each candidate:
   - Intended slide and visual purpose.
   - Source URL and creator or organization.
   - License, credit, or usage note.
   - File type, pixel dimensions, and aspect ratio.
   - Crop suitability and text-safe region.
   - Alt text.
   - Selection or rejection reason.
5. Download or rasterize candidate files into `30_assets/searched/` and inspect them at useful resolution.

Use `20_research/source-notes.txt` for claim provenance when required by the Presentations workflow.

If no searched candidate is visually, factually, and legally suitable, load and call `imagegen` to generate a bespoke asset. Record:

- Why search candidates were insufficient.
- The complete image-generation prompt.
- Intended aspect ratio, crop, composition, and text-safe area.
- Any post-generation edits.

Never generate fake official marks, product screenshots, documentary evidence, research results, citations, or identifiable real people.

Store generated images in `30_assets/generated/` and copied final selections in `30_assets/selected/`.

Do not reuse one image across several slides by default. Do not force every collected candidate into the deck.

## 5. Define the visual contract and layout map

Only after the script gate and asset sweep are complete, record the visual contract and layout map in `40_layout/`:

- Slide size and aspect ratio.
- Title, content, divider, comparison, timeline, demo, and closing families.
- Left/right margins, title baseline, body grid, footer, and page marker positions.
- Font families, sizes, weights, line spacing, and fallback fonts.
- Palette and permitted accent colors.
- Image crop, border, shadow, mask, and caption treatment.
- Density limits and typical words per slide.
- The source slide or layout assigned to each scripted slide.

When the user says “copy this format,” reuse these families rather than merely sampling the colors.

## 6. Author the canonical editable PPTX

Use the implementation route required by the installed Presentations skill.

Map each final slide to its script entry. Move detailed narration, interactions, and required source blocks into speaker notes; keep visible copy concise.

Keep draft PPTX files, authoring source, helper scripts, and presentation-object inspection output in `50_pptx/`.

For template following:

- Duplicate mapped source slides.
- Edit inherited text, media, charts, and tables in place.
- Preserve the source master/layout hierarchy.
- Avoid broad text clearing and overlay-based rebuilding.

For screenshot decomposition:

1. Render the screenshot at high resolution.
2. Identify textual fields, shapes, repeated chrome, and true raster regions.
3. Rebuild text and simple geometry natively.
4. Crop or regenerate only the irreducibly raster regions.
5. Match spacing and alignment to neighboring slides.
6. Verify editability by inspecting the final presentation objects.

If layout exposes a content defect, update the script first, record the revision, and then update the slide and its notes.

## 7. Produce demos when they add learning value

Create companion HTML only when interaction helps the audience form a mental model. Keep the complete demo and its assets in `55_demos/`. Keep slide copy focused on the observation and link or launch the demo separately.

Examples:

- Latent-space sampling and interpolation.
- Adversarial training balance and mode collapse.
- Diffusion denoising steps and conditioning.
- Model-history architecture comparison.
- Computer-vision task switching.

## 8. Run the PPTX render–inspect–revise loop

For each pass:

1. Export/render all slides into a new `60_renders/pass-<n>/` subdirectory.
2. Inspect full-size slides, not only a montage.
3. Record defects by slide number in `70_qa/`.
4. Fix the source objects.
5. Render again.

Do not deliver after only a programmatic build or only a contact-sheet review.

Confirm the final deck still matches the script and timing. Run `scripts/check_audience_copy.py` against the final PPTX and resolve any leaked summary, timing, interaction, or production labels. Run `scripts/validate_deliverables.py` as a structural smoke test after visual QA and store both outputs in `70_qa/`.

## 9. Convert after the PPTX is stable

When Keynote is requested:

1. Preserve the verified PPTX.
2. Convert a copy into `80_keynote/`.
3. Re-open the `.key` from `80_keynote/`.
4. Inspect every slide when practical and at minimum one representative of each slide family.
5. Fix conversion defects in the most appropriate source.
6. Re-run the affected visual and structural checks.

Copy verified delivery candidates into `90_final-staging/`. Deliver both the verified `.pptx` and converted `.key`; do not replace the PPTX with a Keynote-only handoff.

## 10. Handoff

Copy only verified files from `90_final-staging/` to the requested final destination. Run `scripts/workspace_guard.py audit`, passing each copied deliverable as an allowed final path.

Deliver only final artifacts and a compact summary. Mention:

- Slide count and main sections.
- Script completion and timing status.
- Asset search coverage and whether image generation was needed.
- Whether the deck was template-matched or created from scratch.
- Whether elements were reconstructed for editability.
- Companion demos created.
- PPTX/Keynote verification status.
- The absolute single job-root path containing all intermediates.
- Any unavoidable conversion or rendering limitation.

Retain the script and asset ledger as production records. Include them in the handoff when the user asks for a script, teaching package, provenance package, or editable production archive.
