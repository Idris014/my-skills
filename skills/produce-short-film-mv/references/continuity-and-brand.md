# Continuity, identity, and brand controls

Apply these rules to image prompts, image edits, video prompts, and QA.

## Scope authorities

Assign each reference one scope and prevent cross-scope leakage.

| Authority | Controls | Must not control |
|---|---|---|
| shot/composition | camera, crop, subject count, placement, pose, gaze, expression intensity, hands, contact, props, lighting | an incorrect face, hairstyle, logo, or badge |
| identity | named person's facial structure, age, skin, hairline, hair, facial hair, build, identity-specific glasses/earrings | pose, camera, scene, other identities |
| scene | architecture, door/window/terminal positions, materials, floor, fixed lights | character placement or performance |
| prop/vehicle | geometry, proportions, distinctive construction | camera, weather, unrelated marks |
| state board | approved UI/light/effect/hologram state | scene redesign or identity |
| exact artwork | only its own mark topology, orientation, colour relation | garment design, placement on another person, scene decoration |

When authorities conflict, preserve each inside its assigned scope. Replace an incorrect visible identity even when the shot frame already contains it.

## Multi-character separation

- Name every visible character and map each screen position to one identity anchor.
- Never average or transfer face, hair, glasses, earrings, facial hair, age, build, uniform details, or marks.
- Preserve approved screen order, spacing, eyelines, and body-contact state.
- Keep intentionally blurred or distant characters blurred. Do not fabricate a detailed face from an identity board when the shot does not resolve it.
- For close or medium faces, treat identity correction as replacement inside the visible head/hair silhouette, while preserving the shot's head angle, gaze, and expression intensity.

## Anatomical left/right and occlusion

- Interpret `own left` and `own right` from the character's body, never the viewer's side.
- Interpret vehicle left/right from its established forward heading.
- Identify the physical arm/chest/wrist before placing a mark.
- Show a face, eye, ear, hand, limb, watch, patch, logo, or rank tab only when genuinely visible.
- Keep a correct but hidden detail hidden. Never move it to the wrong visible side.
- Never mirror the frame or artwork to fix side placement.

## Exact brand artwork

Use generative tools to prepare placement surfaces and integrate perspective, scale, cloth deformation, occlusion, material, and light. Use the user's exact artwork for final strokes when fidelity matters.

Do not redraw, reinterpret, mirror, thicken, thin, reconnect, simplify, recolour, or transform the topology of exact artwork. Do not accept a semantically similar compass, sphere, pyramid, shield, letter, or abstract emblem.

For a recurring vehicle mark, approve one master installation. Copy its normalized relationship, not its absolute pixel size:

- mark size relative to visible hull/body area;
- center relative to bow/stern, rail/deck, panel seams, windows, and edges;
- perspective direction and curvature;
- material, paint, reflection, shadow, wear, and occlusion.

If the master changes, re-audit dependent frames.

## Example role-specific uniform contract

When adapting this skill to the X26 project, use these exact project rules:

- Every visible X mark belongs only on that character's own left chest.
- Captain: shield patches on both upper arms only where visible; exactly four antique-gold rank bars on each shoulder, following perspective and occlusion; tactical watch only on own left wrist.
- Nautilus: rectangular glasses; Nautilus circular patch only on own right upper arm; mint-aqua/cyan and restrained sea-green palette, integrated into dark navy fabric, never neon.
- Solstice: approved tied-back hair, loose strands, and earrings; Solstice triangular/pyramid patch only on own right upper arm; her own left arm remains plain navy with no backing rectangle or patch.

For another project, replace this contract with the approved costume/brand manifest rather than copying these marks.

## Example project state contract

For X26, preserve these approved story-state rules unless a later adopted manifest explicitly replaces them:

- Within an overlapping scope, use: exact user brand artwork > named identity/THALASSA anchor > dedicated prop board > dedicated scene board > state/performance board. `PROP-DECK` controls the telescope/chair over the deck scene board; `PROP-TERM` controls the terminal/chair over the control-room scene board.
- Control-room geography keeps Nautilus screen left, Solstice screen right as the sole terminal operator, the central hologram on its fixed base, and the Captain on the established camera/door side except for a documented coverage exception. In Scene 6, Nautilus approaches only from screen left.
- The same SHIP-X appears in Scenes 1, 3, and 8 with the approved bow direction toward screen right; dependent hull-logo views inherit the canonical logo master.
- THALASSA progresses `TH-0 → TH-1 → TH-2 → TH-3 → TH-3D`; do not invent `TH-4`, detach the sphere from its fixed projection base, or jump to a success state.
- Track the D-01/data-deletion device, telescope, terminal chairs, prop owner, hand, pickup/use/release, and resting location as complete action chains. The Captain holds the deck telescope in his own right hand until `SC03-SH007`, where it is placed on the chair; it never reappears inside the control room.
- Control-room light progresses `L-C1 alarm → L-C2 → L-C3`; in `SC06-SH004` only the intended facial/profile shading deepens rather than redesigning the whole light state.
- `SC05-SH009` ends on the Captain's two-shoulder contact; `SH010` releases that contact; `SH011` begins with no contact.
- Both Scene 7 Captain turn-backs use the Captain's own left shoulder. The second stopping point is farther away and closer to the door.

Treat this as an example of a project-specific state contract, not a default story for other productions.

## Scene and state continuity ledger

Track states that can jump invisibly between image tasks:

```text
SHOT_ID | DOOR | TERMINAL | UI | LIGHT/ALARM | EFFECT/HOLOGRAM
WEATHER/OCEAN | VEHICLE | PROP_OWNER | BODY_CONTACT | HAND_STATE | NOTES
```

Use explicit codes for recurring states. State changes must occur in a named shot and be visible in its START/END or video action. Never let the generator choose a convenient success, alarm, deletion, activation, or lighting state.

## QA order

Review in this order so a beautiful frame does not hide a structural failure:

1. file opens, dimensions, name, and version;
2. character/object count and identity;
3. camera, axis, screen order, scene geometry;
4. pose, hands, gaze, contact, prop ownership;
5. START/END and adjacent-shot state continuity;
6. exact marks, side placement, occlusion, colour integration;
7. lighting, depth, text/watermark, and aesthetic polish.

Use overlays or rapid A/B switching when possible. If a requested correction changes a non-target region, mark `REVISE` even if the target improved.
