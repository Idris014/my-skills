# Reference text and layout style

Use this reference when the user asks to follow a deck’s style, points to local teaching materials, or when a nearby course family supplies the expected voice and pacing.

## Purpose

The output is a compact Markdown corpus that helps the writer and designer learn how the references explain and arrange ideas. It deliberately separates semantic style from surface styling.

Capture:

- How titles frame ideas: question, observation, claim, contrast, or example.
- How explanations unfold: definition → mechanism → consequence, example → pattern, misconception → correction, or another recurring move.
- Sentence cadence, paragraph length, use of questions, analogy, caveat, and transition.
- How much visible copy appears relative to narration and visuals.
- Recurrent composition grammar: hero image with a short thought, one large equation with annotations, two-column contrast, progressive example, sparse divider, and so on.
- Deck-level rhythm: where density rises, where it releases, and how sections turn.

Exclude unless explicitly requested:

- Font families and font files.
- Background colors, gradients, textures, and decorative imagery.
- Brand colors, logos, icon sets, shadows, and ornamental rules.
- Pixel-perfect duplication of a reference slide.

## Inspecting local reference formats

Keep all exports and extracted files under the current job root.

- PPTX: inspect every slide, extract visible text in reading order, record slide dimensions and object geometry, and render representative slides.
- PDF: render every page and extract text when possible. Use visual inspection to recover reading order when extraction is unreliable.
- Keynote: preserve the original `.key`; export a copy to PDF or PPTX inside the job archive, then inspect that export. Record conversion limitations.

Prefer a small, relevant corpus over a dump of every local deck. Include the references that match the audience, subject depth, and teaching mode. Treat confidential files as read-only and never upload them.

## Required Markdown artifact

Create `00_inventory/reference-style-corpus.md`:

```markdown
# Reference style corpus

## Sources inspected
- [absolute local path] — why it is relevant; pages/slides inspected

## Writing voice
- Dominant explanatory moves:
- Sentence rhythm:
- Use of examples and analogy:
- Treatment of uncertainty and caveats:
- Transitions:

## Layout grammar
- Title behavior:
- Text-to-visual ratio:
- Main-content footprint: target 70% of the safe content rectangle on ordinary content slides; note any intentional sparse or full-bleed exceptions:
- Recurring composition families:
- Density rhythm:
- Caption and annotation behavior:

## Representative patterns
### Pattern: [name]
- Source location:
- Short excerpt or faithful paraphrase:
- What makes it work:
- How to adapt it without copying surface style:

## Patterns to avoid
- [pattern and reason]

## Application to this deck
- Writing choices:
- Composition choices:
- What will intentionally remain different:
```

Short excerpts are evidence for analysis, not content to paste into the new deck. Paraphrase when an excerpt would be long or when the reference is confidential.

## Style application check

Before approving the script:

1. Confirm its explanations exhibit the selected reasoning patterns rather than imitating catchphrases.
2. Confirm the proposed layouts use the reference’s hierarchy and pacing without importing excluded surface styling.
3. Confirm the new deck still sounds appropriate for its own subject and audience.
4. Record any intentional departure from the corpus.
5. Confirm ordinary content slides allocate about 70% of the safe content rectangle to meaningful audience-facing content. Exclude master chrome, page numbers, decorative marks, and background texture from this estimate.
6. Identify intentional title, divider, full-bleed, or minimal compositions as exceptions; do not use them to justify undersized type or accidental dead zones.
