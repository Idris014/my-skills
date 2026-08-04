# Script-first deck contract

Use this reference for every task that creates or materially changes visible slide content or layout. The purpose is to solve the teaching, persuasion, decision, or repair problem completely before visual composition begins.

## What may happen before the script

Only read-only discovery:

- Inventory supplied PPTX, Keynote, PDF, document, data, and image files.
- Inspect reference decks, masters, layouts, dimensions, fonts, notes, and slide counts.
- When reference style is requested or locally established, extract its writing and layout grammar into `00_inventory/reference-style-corpus.md`; exclude fonts, backgrounds, colors, and decorative surfaces unless separately requested.
- Research claims and primary sources. Note likely asset categories without collecting image candidates yet.
- Resolve audience, duration, language, goal, deliverables, and editability requirements.

Do not author or edit slides, place shapes, assign slide-specific layouts, write PPTX-generation code, or start a Keynote file.

Conversion-only and read-only inspection jobs may skip script creation because they do not change the content or layout.

## Required script artifact

Create a plain-text or Markdown file named `10_script/deck-script.md` or `10_script/deck-script.txt` under the single job root. This file is the canonical content record. It should be detailed enough that another presenter could teach from it and another designer could lay out the deck without guessing the intended argument.

Use this structure:

```markdown
# Deck script

## Production brief
- Working title:
- Audience:
- Audience starting knowledge:
- Desired audience change:
- Session length:
- Language and tone:
- Central question or idea:
- Required deliverables:
- Reference/content sources:
- Visual constraints:

## Narrative arc
- Opening:
- Development:
- Practice or evidence:
- Transfer or limitation:
- Closing:

## Internal timing ledger
| Slide | Minutes | Purpose |
|---|---:|---|
| 01 |  |  |

## Slide 01 — [audience-facing descriptive or claim-bearing title]
- Narrative job:
- Presenter narration:
  [Write the detailed talk track in complete sentences. Explain examples,
  transitions, caveats, and what the audience should notice.]
- Visible slide copy:
  - [Only the concise text the audience should read]
- Visual brief:
  - Visual purpose:
  - Preferred asset type:
  - Subject/composition:
  - Desired aspect ratio and crop:
  - Text-safe area:
  - Search queries:
- Evidence and sources:
- Presenter choreography, never visible:
- Transition from previous slide:
- Transition to next slide:
- Speaker-note requirements:

## Slide 02 — [...]
[Repeat for every slide]

## Closing movement
- Transfer to another case:
- Limitation or unresolved question:
- Possible next action:
```

For a template-matched edit, add `Reference constraints` to each slide only when the content must fit a known source family. Describe the constraint without assigning the final slide layout yet.

## Detail standard

The script is not complete when it is only a list of slide titles or bullets. Each slide needs:

- One clear narrative job.
- A descriptive or claim-bearing title that helps the audience enter the idea without forcing a slogan.
- Detailed presenter narration in complete sentences, with causal explanation, examples, distinctions, caveats, or counterexamples where useful.
- Concise visible copy separated from the narration.
- Timing recorded only in the internal timing ledger.
- Evidence, claims, and source needs.
- A visual brief with search terms and crop intent.
- The transition into and out of the slide.
- Any interaction, demonstration, reveal, or speaker-note requirement.

For a course or workshop, also include learning checks, questions to ask, expected answers, demonstration steps, and likely misconceptions. Keep interaction choreography in notes rather than labeling it on the visible slide. For an executive deck, include decision implications, evidence strength, objections, and the requested action.

## Prose quality gate

Read the script as prose, not as a slide inventory:

1. Replace mechanical phrases that merely announce a topic, summarize the previous slide, or describe the act of presenting.
2. Remove routine “one-sentence summary,” “key takeaway,” “summary,” and recap boxes unless the user explicitly asks for that form.
3. Keep timing metadata out of titles, visible copy, and narration. Use only the internal timing ledger.
4. Keep presenter actions internal. A visible question may stand on its own; labels such as “互动”, “讨论”, or “activity” should not appear.
5. Look for at least one genuine explanatory move in every substantive slide: a causal link, concrete example, contrast, misconception, limitation, or useful inference.
6. Vary syntax and slide rhythm. Repeated sentence templates make even correct material feel synthetic.

## Script completeness gate

Before asset collection or layout:

1. Check that every required topic and user instruction appears in the script.
2. Sum slide timings and reconcile them with the session length, including interaction and transition time.
3. Read only the titles in sequence; they should form a coherent argument.
4. Read only the narration in sequence; it should not rely on visuals that have not been defined.
5. Confirm visible copy is concise enough for projection.
6. Confirm every factual claim has a source or a clearly marked research need.
7. Confirm every slide that would benefit from imagery has a usable visual brief and search queries.
8. Confirm the close resolves the opening.
9. Confirm the prose quality gate passes and visible copy contains no production-language labels.

Record the result at the end of the script:

```text
[SCRIPT GATE]
Coverage: PASS
Timing: PASS
Narrative continuity: PASS
Prose quality: PASS
Visible-copy density: PASS
Audience-copy hygiene: PASS
Source needs resolved or tracked: PASS
Visual briefs complete: PASS
Approved for asset sweep: YES
```

If any item fails, revise the script before continuing.

## Compact change script for local repairs

For a narrowly scoped repair that does not introduce a new narrative, create `10_script/change-script.md` under the same job root before editing the deck. Use one entry per affected slide:

```markdown
## Slide [number]
- Existing defect:
- Intended audience-facing result:
- Content that must remain unchanged:
- Visible copy changes:
- Presenter-note changes:
- Editability requirements:
- Asset search or crop needs:
- Layout and hierarchy intent:
- Adjacent-slide constraints:
- Verification criteria:
```

This is still a stage gate: finish and review the change script before editing the PPTX. Use the full deck script whenever the repair changes the argument, timing, slide order, or teaching flow.

## Change control after the gate

The script remains the source of truth. If research, asset availability, layout, or conversion reveals a content problem:

1. Update the script first.
2. Record the reason in a short revision note.
3. Apply the same change to visible slide copy and speaker notes.
4. Re-run timing and continuity checks for affected slides.

Do not silently solve a content problem only inside the deck.

## Relationship to speaker notes

Move the presenter narration, interactions, and source blocks into speaker notes during authoring. Keep visible slides concise. The final notes may be lightly edited for delivery, but they must preserve the meaning, caveats, and sources in the script.
