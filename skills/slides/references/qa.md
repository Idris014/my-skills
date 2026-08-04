# Delivery QA

Use this checklist after the deck is content-complete.

## Workspace containment

- Exactly one Slides job root was created before the first intermediate write.
- The workspace manifest exists in `00_inventory/workspace-manifest.json`.
- Scripts, research, assets, layout files, authoring code, drafts, demos, renders, QA, Keynote files, logs, and temporary files are descendants of that job root.
- No sibling scratch folders or loose intermediate files were created in the project root, current working directory, Downloads, installed skill directory, or unrelated temporary directories.
- All final artifacts were verified inside `90_final-staging/` before being copied out.
- The workspace audit passes with only the exact copied final deliverables allowed outside the job root.
- The job root is preserved and its absolute path is reported at handoff.

## Script gate

- A detailed `deck-script.md` or `deck-script.txt` exists.
- The script records audience, desired change, duration, language, central question or idea, and deliverables.
- Every slide has a narrative job, audience-facing descriptive or claim-bearing title, detailed narration, visible copy, evidence, visual brief, and transition.
- Slide timing lives in the internal timing ledger and does not leak into audience-facing text.
- Slide timings reconcile with the requested session length.
- The title sequence forms a coherent argument.
- Every final slide maps to a script entry.
- Material content changes made during production were first reflected in the script.
- The script ends with a passing `[SCRIPT GATE]`.

## Narrative

- The opening establishes a worthwhile question or goal.
- Every slide has one clear job and an audience-facing descriptive or claim-bearing title.
- Adjacent slides build on each other.
- Requested topics are present without duplicated beats.
- The close resolves the opening and does not end on an incidental detail.
- Visible copy does not use routine summary labels, timing labels, interaction labels, or production commentary.
- Explanations contain concrete reasoning, examples, distinctions, caveats, or useful inferences rather than mechanically announcing topics.

## Visual system

- Title, content, divider, and closing slides belong to one system.
- Margins, title baselines, footer positions, and page markers are consistent.
- Adjacent slides vary composition without changing the design language.
- No slide is a dense dashboard of cards unless the user explicitly requested one.
- Empty space is intentional, not a sign of missing content.
- The page feels compact but unforced: related items sit close, unrelated items have separation, and the main focal region remains obvious.
- On ordinary content slides, the union of meaningful title, body, visual, chart, table, diagram, and callout regions occupies 65–75% of the safe content rectangle, targeting 70%.
- Master chrome, page numbers, footers, decorative dots, rules, shadows, and background textures are excluded from the occupancy estimate.
- Slides outside the 65–75% band were repaired or documented as intentional title, divider, full-bleed, or minimal-transition exceptions.
- Dense slides are followed by lighter visual, example, or transition slides when the narrative permits.

## Asset sweep

- An asset ledger records image searches and candidate decisions.
- Image-bearing slides have at least 3–5 searched candidates when practical, with broader coverage for hero imagery.
- Source URLs, creator or organization, usage notes, dimensions, aspect ratios, and intended crops are recorded.
- Selected images were inspected at useful resolution rather than chosen from thumbnails alone.
- Image generation was used only where search could not supply a suitable asset.
- Generated-image prompts, aspect ratios, compositions, crops, and text-safe areas are recorded.
- No generated asset impersonates an official logo, product screenshot, citation, evidence, or identifiable real person.
- Repeated images are intentional and justified.

## Typography

- Template font sizes and line spacing are preserved.
- Otherwise, the minimum sizes required by the Presentations skill are met.
- For a 1280×720 authoring canvas, ordinary content slides target 44–56 px titles, 24–30 px body text, 18–22 px labels or captions, and 14–16 px sources or footnotes; these values scale only when the slide coordinate system scales proportionally.
- Intended one-line titles do not wrap.
- Body copy is shortened before fonts are reduced.
- Type is not reduced to manufacture whitespace. When occupancy is below target, the focal visual and readable text are enlarged or the composition is rebalanced before decorative elements are added.
- Chinese and Latin fallback fonts render consistently.
- Equations use a real math-rendering path or high-quality vector fallback; raw LaTeX delimiters and broken baseline approximations are absent.
- Formula-heavy slides have been checked for grouping, superscript/subscript alignment, and legible variable definitions.

## Editability

- Titles, body text, labels, and callouts are native text.
- Simple diagrams use native presentation objects.
- Charts and tables remain editable when practical.
- Screenshot-based source slides have been decomposed.
- Raster images are used only where raster content is appropriate.

## Technical

- Every slide renders.
- There are no unintended overlaps, clipping, or off-slide objects.
- Connectors do not cross labels or nodes.
- Images are sharp and correctly cropped.
- Placeholders and authoring prompts are resolved.
- Speaker notes contain required `[Sources]` blocks.
- The final PPTX opens after export.
- `scripts/check_audience_copy.py` reports no unresolved production-language, timing, or interaction labels in visible slide text.

## Companion demos

- Index links work.
- Local assets exist.
- Remote runtime dependencies are absent.
- Controls update the intended model.
- Desktop/projector mode fits without vertical scrolling.
- Narrow screens remain usable.

## Keynote

- The verified PPTX is preserved and included with the `.key`.
- The `.key` file opens after conversion.
- Representative layout families have been reviewed.
- Font, wrapping, crop, effect, and note changes are resolved.

## Final handoff

- Source files were preserved unless in-place editing was requested.
- Only final artifacts are presented.
- The final response identifies the one job-root archive containing every intermediate file.
- The response states script completion and asset-search or image-generation status.
- The response states what changed and what was verified.
- Any remaining limitation is specific and honest.
