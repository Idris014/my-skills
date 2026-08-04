# Image2 prompt patterns

Use one pattern per output. Replace bracketed fields. Keep the prompt in English when the image engine follows technical constraints more reliably in English; keep the production notes and filenames in the project's working language.

## Reference budget and failure recovery

Preferred order:

1. for START: shot/composition; for END: the same shot's adopted START;
2. preceding adopted continuity frame or scene anchor, as required by the task;
3. only visible identity anchors;
4. only required exact artwork/uniform board;
5. one special prop/state reference if essential.

Generate an END by editing the adopted START from the same shot. Change only the formal action delta. Never ask the model to independently redraw an END from a broad scene description.

Do not upload irrelevant identities or assets. For localized edits, start with the current frame plus one identity or exact-art reference. If the request returns `Bad Request`, first test one small valid image and a minimal prompt. Then reduce input count, remove alpha channels, convert oversized PNGs to high-quality JPEG, shorten prompt, and retry. If separate references compete, build a single labeled anchor board around 3072×2048 JPEG quality 82–88.

Never diagnose a successful generation as a locked result until it passes continuity review.

## A. New or clean-regenerated storyboard frame

```text
IMAGE2 REGENERATION TASK — SINGLE ANCHOR BOARD / SHOT + SCENE + IDENTITY + BRAND LOCK

Generate exactly ONE clean cinematic storyboard frame. Output one image only, 16:9, [WIDTH]×[HEIGHT].

The uploaded image is a labeled ANCHOR BOARD, not the final layout. Do not reproduce labels, panels, borders, multiple views, gray reference backgrounds, or a contact sheet. Use it only as controlled source material and output one seamless cinematic frame.

TARGET
Shot: [SHOT_ID]
Frame: [KF-START / KF-END]
Output: [OUTPUT_FILENAME]
Scene: [SCENE_ID]
Visible characters: [NAMES]

AUTHORITY ORDER
1. SHOT COMPOSITION is the absolute camera, composition, performance, hand, contact, and prop lock.
2. SCENE ANCHOR is the absolute environment geometry and material lock.
3. Each named ID panel is the absolute identity lock for only that character.
4. Named prop, vehicle, uniform, and brand panels control only their labeled scope.
5. PREVIOUS APPROVED FRAME, if present, controls inherited continuity state.

RECREATE THE SHOT
- Match camera position, lens feeling, height, angle, crop, horizon, perspective, subject count, screen order, spacing, and negative space from SHOT COMPOSITION.
- Match pose, body orientation, head angle, gaze, expression intensity, hands, finger count, contact, and prop ownership.
- Depict one frozen instant appropriate to the named frame. Do not compress the full movement sequence into a still image.
- Use the scene anchor for architecture, fixed objects, materials, floor, doors/windows, terminals, lights, and effect platform.
- Transfer each named identity one-to-one into its assigned screen position. Use its facial proportions, age, skin, hairline, hair, facial hair, body build, and identity-specific eyewear/earrings. Never blend identities.

START/END CONTINUITY
- Preserve every approved lock shared by the pair.
- Change only this intentional delta: [ACTION_DELTA].
- The transition must be physically possible within [DURATION].

LEFT/RIGHT/OCCLUSION
- Left/right refers to each subject's own body or the vehicle's heading.
- Show marks, limbs, hands, watches, or facial details only where genuinely visible.
- Keep hidden, blurred, or off-frame details hidden. Never move a correct mark to a visible wrong side.

EXACT ARTWORK
- Use only the labeled exact-art panels for marks. Preserve topology, orientation, and colour relationship.
- Keep marks perspective-correct, fabric/material integrated, correctly scaled, and non-floating.
- If exact strokes cannot be preserved, produce a clean placement surface for non-generative compositing.

HARD NEGATIVES
no contact sheet, no labels, no panel borders, no multiple views, no new camera angle, no changed crop, no extra or missing subject, no identity blend, no identity swap, no beautification, no age drift, no hairstyle redesign, no missing required eyewear, no extra earring, no extra limb, no extra finger, no fused hand, no moved prop, no released or invented contact, no wrong-side mark, no mirrored image, no duplicate logo, no floating emblem, no scene redesign, no readable UI, no text, no subtitle, no watermark
```

## B. Local character identity/detail correction

```text
IMAGE2 EDIT TASK — LOCAL CHARACTER IDENTITY AND UNIFORM CORRECTION

Edit exactly ONE existing cinematic storyboard frame. Output one image only, 16:9, [WIDTH]×[HEIGHT]. Perform a localized correction, not a full-frame redraw.

TARGET
Shot: [SHOT_ID]
Frame: [KF-START / KF-END]
Input: [CURRENT_FRAME]
Output: [OUTPUT_FILENAME]
Visible characters: [NAMES]

TWO SEPARATE LOCKS
- Ref 1 is the SHOT LOCK: camera, lens, crop, composition, subject count, screen position, pose, head angle, gaze, expression intensity, hands, contact, props, background, lighting, depth, and continuity state.
- Each named identity reference is the IDENTITY LOCK for only its named character. Inside that character's genuinely visible face, hair, skin, and silhouette, it has higher authority than Ref 1.
- Named uniform or exact-art references control only their assigned garment detail.

EDIT ONLY
- Replace the visible incorrect identity with [CHARACTER]'s approved facial proportions, age, skin tone, hairline, hairstyle, facial hair, build, and identity-specific [GLASSES/EARRINGS].
- Preserve the exact head angle, gaze, expression intensity, pose, hands, and contact from Ref 1.
- Correct only these visible uniform details: [DETAILS].
- Place [LOGO/PATCH] only on [CHARACTER]'s own [LEFT CHEST / RIGHT UPPER ARM / OTHER APPROVED LOCATION].
- Keep a correct but occluded mark occluded. Do not move it to the other side.

ABSOLUTE CONTINUITY LOCK
Do not change camera, crop, subject count, screen order, pose, hands, fingers, contact, prop ownership, door/terminal/effect state, lighting, background, depth of field, or the intended START-to-END delta.

HARD NEGATIVES
no full-frame redraw, no generic replacement face, no face blending, no identity swap, no beautification, no age drift, no unrelated hairstyle redesign, no missing required eyewear, no extra earrings, no changed pose, no moved hand, no extra limb, no extra finger, no mirrored image, no wrong-side badge, no duplicate patch, no logo on the wrong chest, no background redesign, no readable text, no watermark
```

If both face identity and uniform marks are unstable, run two passes: identity/hair first, then marks. Do not overload one weak local edit.

## C. Recurring ship/vehicle logo correction

```text
IMAGE2 EDIT TASK — VEHICLE LOGO MASTER DEPENDENCY

Edit exactly ONE existing cinematic storyboard frame. Output one image only, 16:9, [WIDTH]×[HEIGHT]. Preserve the approved vehicle and shot; correct only logo placement and integration.

TARGET
Shot: [SHOT_ID]
Frame: [KF-START / KF-END]
Input: [CURRENT_FRAME]
Output: [OUTPUT_FILENAME]

REFERENCE LOCKS
- Ref 1 locks camera, crop, horizon, weather, vehicle position, scale, heading, wake/motion, lighting, and depth.
- Ref 2 is the approved logo master. It locks normalized logo-to-body size, installation zone, relative centre, edge distances, perspective, curvature, and material relationship.
- Ref 3 locks the vehicle geometry.
- Ref 4 is the exact logo artwork.

EDIT ONLY
- Preserve the same vehicle, geometry, paint divisions, windows, railings, antennas, panels, motion, reflections, and environment.
- Reproduce the master's spatial relationship. Scale logo pixels proportionally to the target vehicle's on-screen size; do not copy absolute pixel dimensions.
- Follow the target surface's perspective, curvature, occlusion, reflection, wear, and light.
- Preserve exact artwork topology. If generation cannot retain it, output a clean placement surface for non-generative compositing.

HARD NEGATIVES
no redesigned vehicle, no changed heading, no mirrored vehicle, no missing structure, no duplicate logo, no approximate logo, no new name or text, no changed weather, no changed horizon, no changed light, no watermark
```

Do not create dependent logo frames before the master passes. Re-audit them whenever the master changes.

## D. New comic-world reset

First create and approve separate identity anchors for every new comic-world object: vessel, captain/performer, ocean/environment, ruin/location, creature, or motif. A style board controls line, palette, shadows, and rendering only; it does not define object identity.

```text
IMAGE2 TASK — NEW COMIC-WORLD ASSET INTEGRATION

Generate or edit exactly ONE comic storyboard frame. Output one image only, 16:9, [WIDTH]×[HEIGHT]. Integrate only the approved NEW comic-world assets while preserving the requested shot composition.

TARGET
Shot: [SHOT_ID]
Frame: [KF-START / KF-END]
Output: [OUTPUT_FILENAME]
Objects: [NEW OBJECTS]

REFERENCE LOCKS
- SHOT COMPOSITION locks camera, crop, placement, movement direction, narrative emphasis, and negative space.
- Each named NEW ASSET locks only that object's identity, silhouette, proportions, and distinctive features.
- STYLE locks line weight, shape language, shadow blocks, palette, texture, and 2D/graphic treatment.
- Never infer a live-action project asset identity unless the brief explicitly requires a relationship.

INTEGRATION
- Use the same approved new silhouettes and geometry across all related frames.
- Preserve object count, screen position, hierarchy, perspective, and direction.
- Remove duplicates, melted edges, mixed rendering modes, meaningless symbols, and accidental modern equipment.
- Keep [DISTANT ENERGY/MOTIF] restrained and consistent with its state board.

HARD NEGATIVES
no live-action asset migration, no photorealistic insert, no 3D CGI unless specified, no new camera angle, no object duplication, no panel grid, no speech balloon, no caption, no readable text, no unrelated logo, no modern equipment, no watermark
```

## Output contract

For every prompt, provide:

```text
Output filename:
Reference 1:
Reference 2:
Reference 3:
Reference 4:
Reference 5:
Prompt:
Acceptance checks:
```

Omit unused reference rows. Keep the ordered list stable between retries and increment the version rather than overwriting.

The adopted/locked manifest selects the production input. A lexically or numerically highest filename is only a candidate until that manifest adopts it.
