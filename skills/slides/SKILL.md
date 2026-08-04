---
name: slides
description: Create, extend, repair, restyle, and convert professional presentation decks while preserving editability and the visual language of supplied references. Use this skill whenever the user asks for slides, a deck, PPT/PPTX, Keynote, lecture or workshop materials, Day 1/Day 2/Day 3 course decks, slide-template matching, screenshot-to-editable reconstruction, deck-wide restyling, generated slide imagery, interactive HTML demos for a presentation, or conversion between PowerPoint and Keynote—even when they only ask to “add pages,” “fix these slides,” or “copy the format.”
---

# Slides Studio

Use this skill as the production workflow around the installed `presentations:Presentations` skill. The Presentations skill remains authoritative for PPTX implementation, font constraints, notes citations, template fidelity, rendering, and overlap testing. This skill adds the orchestration needed for script-first authorship, natural explanatory writing, reference-deck continuity, editable reconstruction, Keynote delivery, and companion HTML demos.

## Start by resolving the job

Infer these from the request and supplied files before asking questions:

- Audience, session length, language, teaching or decision goal.
- Whether the user wants a new deck, an in-place edit, a copied draft, or a converted deliverable.
- Which file is the content source and which file is the visual source.
- The canonical visual system when several decks disagree.
- Required deliverables: PPTX, Keynote, PDF preview, images, HTML demos, or some combination.
- Whether the user expects every visible element to remain editable.

Ask only when a missing choice would materially change the result. Preserve confidential source files and never publish or upload them without explicit permission.

## Create one build archive before writing anything

Every Slides job that writes files must use exactly one job root for all agent-created intermediate state. Read and follow [references/workspace-archive.md](references/workspace-archive.md) before creating a script, render, download, extracted asset, generated image, build script, log, PPTX draft, Keynote conversion, demo, or QA file.

Initialize the root with `scripts/workspace_guard.py init`. Unless the user provides another archive location, use:

```text
<project>/.slides-work/<deck-slug>-<timestamp>/
```

Subdirectories are allowed inside this root; sibling scratch folders are not. Use descendant paths of this root for every explicit output path and use its `tmp/` directory for controllable temporary files. Do not scatter intermediates into the project root, current working directory, Downloads, the installed skill directory, or unrelated `/tmp` locations.

Stage final artifacts inside `90_final-staging/`, verify them there, and then copy only the requested final deliverables to the user’s destination. Preserve the job root as the single production archive unless the user explicitly requests cleanup. Run `scripts/workspace_guard.py audit` before handoff to detect unexpected new or modified project files outside the job root and allowed final paths.

## Load the right supporting workflows

1. Load and follow `presentations:Presentations` for every PPTX operation.
2. Load the PDF skill when a PDF is a reference, content source, or review target.
3. Use the available image-search capability (`image_query` or equivalent) for the asset sweep after the content script is complete. Load and call the `imagegen` skill only when the search cannot supply a suitable, usable asset.
4. Load frontend design for companion HTML demos.
5. Load browser automation only for real interactive QA; if local-page security prevents it, report that limitation and perform static validation instead.
6. Use Keynote automation only when `.key` delivery or native Keynote inspection is requested.

## Separate reference language from surface styling

When the user asks for a style reference, or nearby local decks clearly define the expected teaching voice, inspect relevant local PDF, Keynote, and PPTX files before writing the script. Read and follow [references/text-and-layout-style.md](references/text-and-layout-style.md).

Create `00_inventory/reference-style-corpus.md` inside the job archive. Capture only:

- Text voice: sentence rhythm, explanatory depth, use of examples, questions, analogies, caveats, and transitions.
- Information architecture: title behavior, paragraph/bullet balance, visual-to-text ratio, pacing, and recurring composition families.
- Representative short excerpts or faithful paraphrases that make the pattern concrete.
- Patterns worth adopting, patterns to avoid, and how they apply to this audience.

Do not retain or imitate fonts, background fills, gradients, colors, logos, decorative textures, or other surface styling unless the user separately requests visual template matching. A reference corpus informs writing and composition; it does not silently replace the chosen visual system.

## Enforce the script-first production contract

The content script is the source of truth for the deck, not a disposable outline. For every task that creates or materially changes visible slide content or layout, read and follow [references/script-first.md](references/script-first.md). Use the full deck script for new decks, multi-slide creation, substantial extensions, and structural rewrites; use the compact change-script variant for a narrowly scoped repair with no new narrative content. Conversion-only and read-only inspection jobs do not require a new script.

The order is strict:

1. Create the single build archive.
2. Inspect supplied files and references read-only.
3. Write the complete, detailed deck script inside the archive.
4. Pass the script completeness gate.
5. Search for and inspect visual assets inside the archive; generate only unresolved assets.
6. Define the visual contract and map layouts inside the archive.
7. Author and verify the editable PPTX inside the archive.
8. Convert and verify a Keynote copy inside the archive when requested.
9. Copy only verified final deliverables out of the archive.

Before the script passes its gate, do not author slides, place shapes, choose slide-specific compositions, edit a PPTX, or start a Keynote file. Read-only template inspection is allowed because the script may need to respect existing length, tone, or slide families. The script must still be complete before those families are assigned to individual slides.

If the later visual pass exposes a content problem, revise the script first and then propagate the revision to the deck. Keep detailed narration in speaker notes; do not paste the whole script onto visible slides.

## Write like a thoughtful teacher, not a slide generator

The script and visible copy should explain, not merely label. Prefer causal reasoning, concrete examples, useful distinctions, and moments that change how the audience sees the topic. Vary sentence length and cadence. Let one idea develop far enough to become intelligible before moving on.

Avoid mechanical deck language:

- Do not manufacture a slogan, “one-sentence summary,” repeated takeaway, or recap box for every idea.
- Do not use headings such as “一句话总结”, “核心结论”, “Key takeaway”, or “Summary” as a routine device.
- Do not expose timing scaffolds such as “时长 5 min”, “5-minute activity”, or production notes on visible slides.
- Do not label audience interaction with visible text such as “互动”, “讨论环节”, “Think–Pair–Share”, or “请举手”. Put presenter choreography in notes and let the question or example itself appear naturally when it belongs on the slide.
- Do not write agenda-like noun piles when a short explanatory sentence would reveal the relationship.
- Do not end every section by restating it. Close by transferring the idea to a new case, exposing a limitation, or opening the next question.

Run a prose pass before layout: remove template-like phrases, generic intensifiers, redundant conclusions, and content that only describes what the slide is doing. Preserve uncertainty and caveats where they teach better judgment.

## Choose the production route

### Existing deck or reference template

Treat the source deck as a structural contract, not a mood board. Inspect every slide, master, layout, placeholder, font, color, spacing rule, footer, and recurring visual motif. Duplicate appropriate source slides and edit inherited elements in place.

If the visual reference is a PDF or Keynote rather than a PPTX, first determine whether an editable PPTX/Keynote source exists. If only a flattened reference exists, reconstruct a small reusable layout system that matches it, record the limitation, and keep new content editable.

### New deck with explicit art direction

Build from scratch using the requested direction. After the script and asset sweep are complete, define typography, palette, margins, image treatment, and slide families before authoring slides.

### New deck without visual direction

Use the default visual route required by the Presentations skill.

Read [references/workflow.md](references/workflow.md) for the detailed sequence and working artifacts.

## Preserve editability

Editability is part of correctness:

- Keep titles, body copy, labels, captions, tables, charts, timelines, and simple diagrams as native presentation objects.
- Use raster images only for photographs, generated illustrations, complex textures, screenshots that must remain screenshots, or artwork that is inherently raster.
- When a source slide is one large screenshot, decompose it into editable text fields, native shapes, and newly cropped or regenerated images. Do not place the screenshot back as the finished slide.
- Preserve master → layout → slide inheritance when editing an existing PPTX.
- Reuse the source deck’s exact title, content, divider, and closing patterns before inventing new layouts.
- If copy does not fit, shorten it, split the slide, or choose a more suitable layout before reducing type.

## Build the narrative in the script

Define one communication job and one cumulative learning or decision arc before touching layout. For course decks, the script should:

1. Establish the question and why it matters.
2. Introduce the conceptual model.
3. Show history or progression only when it explains the present.
4. Move from recognition to application.
5. Add hands-on demonstrations, discussion beats, or checks for understanding.
6. Close with transfer, a limitation, or a productive next question rather than a labeled summary.

Give every scripted slide one narrative job, an audience-facing descriptive or claim-bearing title, detailed narration, visible copy, evidence, and a visual brief. Keep timing in the internal timing ledger, never in audience-facing copy. Avoid agenda-like topic inventories, repeated summaries, and dense card dashboards. Title slides should be minimal. Content slides should be readable from the back of a room.

## Typeset equations and difficult text deliberately

Raw formulas and overfull text boxes are production defects, not acceptable compromises.

- Use the equation or math-rendering path supported by the presentation runtime for formulas, then place the rendered result as an editable equation when available or a high-quality vector asset with accessible alt text.
- Do not leave raw LaTeX delimiters, ASCII approximations, broken Unicode fractions, or baseline-misaligned superscripts on the slide.
- Keep equation numbers, variable definitions, and explanatory annotations as separate aligned objects when that improves legibility.
- Measure text, preserve line breaks that carry meaning, and use safe text-box padding. If a box cannot fit at the intended size, rewrite, split the idea, or change composition before shrinking type.
- Render every formula-heavy and text-dense slide at full size. Repair clipping, line wrapping, baseline drift, ambiguous grouping, and overlaps in the source, then render again.

## Compose with compact ease

Aim for slides that feel close-knit without feeling compressed. Use a clear focal region, a secondary explanation region, and enough negative space for the eye to change levels. Align to an underlying grid, but avoid a page full of equal cards.

- On ordinary content slides, make the union of audience-facing titles, body text, meaningful visuals, diagrams, charts, tables, and callouts occupy 70% of the safe content rectangle. Treat 65–75% as the production tolerance around that target.
- Measure the safe content rectangle after excluding master chrome, page numbers, footers, decorative dots, rules, shadows, and background textures. Decorative filler never counts toward the 70% target.
- Do not interpret the target as “text must cover 70% of the page.” Reach it by strengthening the focal visual, enlarging readable type, widening useful text measures, rebalancing columns, or splitting the idea across slides.
- Unless a supplied template intentionally establishes a larger scale, use these 1280×720 authoring targets: content title 44–56 px, body 24–30 px, label or caption 18–22 px, and source or footnote 14–16 px. Scale these targets proportionally only when the slide coordinate system itself scales.
- Title, divider, full-bleed visual, and deliberately minimal transition slides may depart from the occupancy target. The departure must be intentional, visually verified, and recorded in the QA notes.
- Keep related items close and unrelated items visibly separated.
- Prefer two density zones over many small boxes.
- Let paragraph width, line spacing, and whitespace create rhythm; avoid shrinking everything to make empty margins look “efficient.”
- Preserve a safe gap between text, images, equations, captions, and recurring chrome.
- Treat accidental overlap as a defect. Treat deliberate overlap as an exception that must remain readable in both PowerPoint and Keynote.
- Review the deck as a sequence: alternate denser explanation with lighter visual or example slides so the audience can recover attention.

## Research and source discipline

- Search current primary sources for claims that may have changed or are technically precise.
- Prefer original papers, official documentation, official demos, and authentic product assets.
- Maintain a source ledger from the start.
- Put `[Sources]` blocks in speaker notes as required by the Presentations skill.
- Never fabricate metrics, screenshots, product UI, logos, citations, or model architecture details.

## Search first, then generate missing visuals

After the script is approved internally and before layout authoring, create an asset ledger and search broadly for relevant images. Do not stop at the first usable result. Collect at least 3–5 credible candidates for every image-bearing slide when practical, and more for hero or cover imagery when meaningful alternatives exist. More candidates improve selection; they do not justify crowding the final slide.

Prefer original papers, official documentation, authentic product assets, reputable archives, and clearly reusable photography or illustration. Record the source URL, credit or license, dimensions, aspect ratio, crop suitability, intended slide, and alt text. Download or rasterize candidates and inspect the actual files rather than trusting thumbnails.

If search does not produce a visually and legally suitable asset, load and call `imagegen` to fill that specific gap. Write the prompt for the intended aspect ratio, composition, crop, and text-safe area; record the prompt in the asset ledger. Never generate fake logos, product screenshots, documentary evidence, citations, or identifiable real people.

Plan each selected image around its slide crop and text placement. Use distinct visuals rather than repeating one image across the deck by default. Use native shapes for simple explanatory structure, Graphviz only for genuinely relational diagrams, and image generation for aesthetic or scientific illustrations. A visual should clarify a claim, not decorate empty space.

## Companion HTML demos

When a concept benefits from manipulation, build an offline HTML lab rather than overloading the slide with controls. Follow [references/html-demos.md](references/html-demos.md).

By default:

- Use plain HTML, CSS, and JavaScript with no install step.
- Match the deck’s visual language without turning slides into web dashboards.
- Fit common 16:9 desktop/projector viewports without vertical scrolling.
- Keep narrow screens responsive and scrollable rather than clipping content.
- Make labels, values, and explanations audience-facing.
- State clearly when the demo is a conceptual simulation rather than a real model.

## Keynote delivery

The verified, editable PPTX is the canonical production artifact. When the user asks for Keynote or for both formats, deliver both the `.pptx` and a separately converted `.key`; do not hand off a Keynote-only result. Create and fully verify the PPTX first, then convert a copy to Keynote. Do not use Keynote conversion as a substitute for PPTX QA. Follow [references/keynote.md](references/keynote.md).

After conversion, inspect representative title, content, image-heavy, chart, and closing slides in Keynote. Fix font substitution, crop changes, wrapping, and unsupported effects before delivery.

## Quality gates

Before handoff, follow [references/qa.md](references/qa.md) and the stricter requirements of the Presentations skill:

1. Confirm the detailed script exists and every final slide maps back to it.
2. Confirm the asset ledger records searched candidates, selections, sources, and any image-generation prompts.
3. Render every slide.
4. Inspect every slide individually at full size.
5. Use a montage only for deck rhythm and consistency.
6. Run overflow and overlap checks.
7. Confirm all intended fields remain editable.
8. Confirm source notes are present and accurate.
9. Verify companion demos, local assets, navigation, and viewport behavior.
10. Re-open converted Keynote files when `.key` is a deliverable.
11. Run `scripts/check_audience_copy.py` and resolve production-language or timing labels found in visible text.
12. Inspect formula-heavy and text-dense slides for correct math rendering, baseline alignment, wrapping, and safe padding.
13. Measure ordinary content slides against the 70% safe-frame occupancy target. Repair slides below 65% or above 75%, unless an allowed exception is documented and visually justified.

Use `scripts/validate_deliverables.py` for a final structural smoke test. It supplements visual review; it does not replace it.

## Revision behavior

Treat concise visual feedback as authoritative evidence:

- “This is crowded” means restore hierarchy and breathing room, not merely shrink everything.
- “Match Day 2” means identify the canonical slide families and apply them consistently, including title and contents pages.
- “Remove the VAE/GAN boxes” means remove the comparison elements and any now-irrelevant copy or citations.
- “No scrolling” means make desktop height viewport-driven while retaining a safe responsive fallback.
- “Fix slide 10–12” means inspect those slides and adjacent layouts, make the requested local repair, and avoid unrelated deck-wide changes.

Re-render after every material revision.

## Deliverables

Preserve source files unless the user explicitly requests in-place editing. Keep every intermediate under the one job root and copy only verified final outputs from `90_final-staging/` to the requested destination.

Return:

- The final PPTX.
- The final Keynote copy when requested, alongside the verified PPTX.
- Companion HTML and its asset directory when requested.
- A short summary of representative changes and any verification limitation.

Keep the detailed script and asset ledger as production records. Do not hand them off by default, but include them when the user asks for the script, instructor materials, provenance, or an editable course package. Do not hand off temporary renders, rejected asset candidates, extracted source assets, or build scripts unless the user asks.

Report the absolute job-root path in the final response so the user can find the complete intermediate archive. Do not delete or disperse that archive after delivery.
