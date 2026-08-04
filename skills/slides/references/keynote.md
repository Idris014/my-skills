# Keynote conversion

Use this reference only when the user requests a `.key` deliverable or native Keynote inspection.

## Conversion policy

Treat PPTX as the verified authoring artifact unless the user explicitly requires native Keynote authoring. Preserve the source PPTX and create a separate `.key` copy.

When `.key` is requested, the normal handoff contains both:

- The fully verified editable `.pptx`.
- The separately converted and inspected `.key`.

Do not begin Keynote conversion before the script is complete, the assets are resolved, and the PPTX passes its visual and structural QA. Do not use Keynote as the only surviving source or deliverable.

If the user explicitly requires native Keynote authoring, still complete the script and asset sweep first. Preserve the native `.key`, export an editable `.pptx` copy when feasible, and verify both formats before handoff. State any conversion-only loss that prevents full editability in one format.

Keynote conversion can change:

- Font metrics and fallback fonts.
- Line wrapping and text-box height.
- Image crops and masks.
- Gradients, shadows, transparency, and blend effects.
- Charts, media, speaker notes, and unsupported PowerPoint features.

Therefore conversion is followed by inspection, not treated as a file-extension change.

## Automated conversion

The bundled script accepts an input PPTX and output `.key` path:

```bash
osascript scripts/convert_to_keynote.applescript \
  "/absolute/path/input.pptx" \
  "/absolute/path/output.key"
```

The script refuses to overwrite an existing output. Remove or rename an existing target only when the user has explicitly authorized replacement.

Keynote must be installed, and macOS may request Automation permission.

Keep the input copy used for conversion, `.key` output, Keynote exports, screenshots, and repair variants under the same job root, normally in `80_keynote/`. Copy the verified `.key` into `90_final-staging/` before handoff.

## Verification

Open the converted deck and inspect every slide when practical. At minimum inspect:

- Title slide.
- Contents/agenda slide.
- A dense content slide.
- An image-heavy slide.
- A chart or diagram slide.
- Closing slide.

If the deck uses several layout families, inspect one of each.

Check that:

- Titles remain on their intended line count.
- Body copy is not clipped.
- Images retain the intended crop.
- Fonts have not been substituted unexpectedly.
- Page numbers, footers, and repeated chrome remain consistent.
- Notes and links required for delivery are present.

Fix defects in the PPTX source when the problem will recur across conversions. Use Keynote-local edits only for conversion-specific exceptions, then re-check the affected slide.

After a PPTX-source repair, reconvert to a new output path or replace the old conversion only with the user’s authorization. Re-open the resulting `.key` and verify the repaired slide plus adjacent slides.
