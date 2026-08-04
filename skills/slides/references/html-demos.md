# Companion HTML demos

Use this reference when a presentation needs an interactive concept lab, simulator, or offline classroom demonstration.

Keep all demo HTML, CSS, JavaScript, images, test screenshots, and diagnostic output under the current Slides job root. Use `55_demos/` for the deliverable demo tree, `60_renders/` for demo screenshots, and `70_qa/` for validation reports. Do not create a separate demo workspace beside the Slides job root.

## Product shape

Prefer one self-contained lab per concept plus an index page. Keep assets in a sibling `assets/` directory and shared styling in one CSS file.

The demo should:

- Open locally without installing dependencies.
- Work without network access except optional citation links.
- Use visible controls that map directly to the concept.
- Provide a concise “what to observe” explanation.
- Distinguish simulation from real inference or training.
- Match the deck’s typography, palette, and illustration treatment.

## Viewport contract

For desktop screens at least 981 px wide:

- Fit the primary lab inside `100vh`.
- Reserve a compact top bar and let the main stage consume the remaining height.
- Use `minmax(0, 1fr)` and `min-height: 0` so canvas/grid children can shrink.
- Make canvas height derive from the available grid area rather than a fixed 500–600 px value.
- Add a compact mode for common 768–820 px projector heights.

For narrow screens:

- Restore normal document scrolling.
- Collapse multi-column layouts.
- Avoid `overflow: hidden` when it would make content unreachable.

## Interaction design

- Give each control a visible label and live value.
- Use tabs only when switching between genuinely different conceptual modes.
- Keep automatic animations stoppable or resettable.
- Respect `prefers-reduced-motion`.
- Preserve keyboard focus and native control semantics.
- Use `aria-live` for changing explanatory states, not for every animation frame.

## Canvas guidance

Size the canvas backing store from its current CSS rectangle and device pixel ratio. Redraw after resize and after a hidden tab becomes visible.

Conceptual diagrams may use canvas. Do not imply that a simulation is running a real neural network unless it actually is.

## Offline validation

Check:

- Local CSS, JavaScript, images, and navigation targets exist.
- No remote script, stylesheet, font, or image is required.
- IDs are unique.
- Inline JavaScript parses.
- Every interaction has an event target.
- Desktop layout does not create vertical scrolling at the target viewport.
- Mobile layout remains reachable.

When browser security blocks `file://` testing, do not attempt policy workarounds. Perform static checks and state the limitation.
