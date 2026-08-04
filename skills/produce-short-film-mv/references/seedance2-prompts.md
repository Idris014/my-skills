# Seedance 2.0 shot prompts

Use only current, approved frames. Verify the platform's current duration, input-count, audio, aspect-ratio, and account constraints at execution time; do not rely on stale product assumptions.

When a shot has no independent END frame, state that explicitly, bind only START, define the intended finishing state in words, and forbid the model from inventing a new light, prop, contact, UI, or effect state. Never fabricate an END filename.

## One-shot document contract

Create one Markdown file per final shot with:

1. metadata and status;
2. approved START/END paths and other reference assets;
3. full copy-paste prompt;
4. compact prompt;
5. hard negatives;
6. timeline and sound;
7. incoming/outgoing continuity;
8. post-only elements;
9. failure-degradation plan;
10. QA checklist.

## Narrative short template

```text
【镜头身份】[SHOT_ID]，[DURATION] 秒，16:9，[SHOT SIZE]，[LENS FEELING]，[CAMERA HEIGHT/ANGLE]。[ONE-SENTENCE PURPOSE].

【首尾帧绑定】0 秒严格匹配 [KF-START APPROVED FILE]。[若有尾帧：最后一帧严格抵达 KF-END APPROVED FILE。] 锁定 [IDENTITIES / COSTUME / SCREEN ORDER / PROPS / SCENE / LIGHT / EFFECT STATE]；不得镜像。

【主体与动作】[SUBJECT-BY-SUBJECT ACTION, GAZE, HAND, CONTACT, PROP OWNERSHIP]. Only [SPEAKER] speaks from [TIME]; all other visible mouths remain closed/natural. [EXPRESSION AND PERFORMANCE INTENSITY].

【摄影机】[STATIC / PAN / TILT / DOLLY / TRACK / HANDHELD] from [START] to [END] at [SPEED]. Keep the established axis and do not pass through subjects, furniture, or effects.

【环境动态】[WEATHER / WATER / HAIR / CLOTH / PRACTICAL LIGHT / UI / EFFECT]. Keep [STATE CODES] stable. Exact UI, text, numbers, code, logos, subtitles, and controlled flashes are post-only.

【连续性】Inherit [PREVIOUS SHOT END STATE]. Preserve [IDENTITY / SCREEN ORDER / HAND / CONTACT / PROP / DOOR / EFFECT / LIGHT]. End at [NEXT-SHOT HANDOFF STATE]. Change only [ACTION DELTA].

【时间轴】
0.0–[T1]s: [ACTION]
[T1]–[T2]s: [ACTION / DIALOGUE]
[T2]–[END]s: [LAND ON END STATE OR HOLD]

【声音】[DIALOGUE/VOICE] at [TIME]; [AMBIENCE]; [FOLEY]; [MUSIC CUE]. No generated subtitles. Mark dialogue that will be replaced or refined in post.

【禁止】no identity swap, no face or age drift, no costume change, no screen-order reversal, no axis crossing, no mirrored image, no wrong hand, no changed contact, no moved prop ownership, no extra limb/finger, no body intersection, no scene redesign, no approximate logo, no readable UI/text/code/numbers, no subtitle, no uncontrolled flash, no watermark.

【后期】[EXACT BRAND / UI / SUBTITLE / DIALOGUE REPLACEMENT / HAND MASK / VFX / COLOUR / SOUND].
```

## MV template

```text
【音乐时间】[TRACK TITLE/ID] [IN–OUT TIMECODE]，[SECTION]，[BAR/BEAT RANGE]，[ENERGY 1–5]。
【镜头身份】[SHOT_ID]，[DURATION] 秒，16:9；visual function: [PERFORMANCE / NARRATIVE / B-ROLL / ABSTRACT MOTIF]；motif: [MOTIF].

【参考绑定】0 秒匹配 [START]. [Optional END binding.] Lock performer identity, wardrobe, hair, makeup, instrument/mic, set, screen direction, and light state from approved references.

【画面与表演】[PERFORMANCE OR ACTION]. If lip sync is required, use only the supplied vocal segment and specify the exact time window; non-singing people keep natural closed mouths. Preserve the approved performance intensity.

【节奏设计】Land [ACTION/CAMERA/LIGHT ACCENT] on [BAR/BEAT OR TIMECODE]. Let movement breathe between accents; do not create a cut or pose change on every beat.

【摄影机】[CAMERA PATH AND SPEED], ending at [COMPOSITION]. Preserve axis and avoid model-invented whip pans unless explicitly designed.

【环境与视觉动机】[LIGHT / PARTICLES / WEATHER / CLOTH / CROWD / ABSTRACT FORM]. Continue the section's palette and motif transformation: [RULE].

【时间轴】
[IN–T1]: [ACTION]
[T1–T2]: [ACCENT / LIP SYNC / CAMERA]
[T2–OUT]: [RESOLVE / HOLD / MATCH CUT]

【声音】Use the supplied master audio segment as timing authority. Preserve music; generate only [FOLEY/AMBIENCE] if requested. Do not invent lyrics or subtitles.

【连续性】Inherit [PREVIOUS TIMECODE STATE]; hand off [WARDROBE / SET / LIGHT / PROP / MOTIF / PERFORMANCE] to [NEXT SHOT].

【禁止】no identity or wardrobe drift, no instrument/mic swap, no uncontrolled lip movement, no invented lyrics, no random beat cuts, no mirrored performance, no extra performers, no approximate branding, no readable text/subtitle, no watermark.

【后期】final music sync, lip-sync refinement, exact brand, lyrics/subtitles if authorized, edit transitions, VFX, grade, sound mix.
```

## Compact prompt

After the full prompt, provide one compact paragraph containing only frame binding, main action, camera, timeline beats, speaker/audio, continuity locks, and the five highest-risk negatives. Use it when the platform has a short prompt field; never let it replace the audited full prompt in the project.

## Failure-degradation ladder

Design a lower-risk alternative before generation:

1. reduce gesture amplitude or walking distance;
2. remove secondary hand interaction while preserving story meaning;
3. lock the camera or shorten its movement;
4. split multi-character dialogue/action into coverage;
5. use START-only low-motion generation and cut to an approved insert/reaction;
6. use interpolation or a post transition between approved frames;
7. move exact lips, hands, UI, text, logos, flashes, and complex effects to post.

Every degradation must preserve identity, screen direction, prop ownership, required state, narrative/music beat, and final timeline duration.

## Video QA

- first and final frames match required bindings without a flash or identity reset;
- identity, face, hair, costume, visible marks, and recurring objects do not drift;
- camera follows one plausible path and respects the axis;
- hands, contact, props, doors, UI/effect, weather, and light follow the timeline;
- only the specified speaker sings/speaks; timing and expression are usable;
- no unwanted text, subtitle, logo approximation, code, number, flash, or watermark;
- duration, frame rate, aspect ratio, resolution, audio presence, and file integrity match the project;
- incoming and outgoing frames cut cleanly with adjacent shots.

Record model/version, run ID, prompt version, reference versions, output filename, pass/reject reason, and accepted replacement in the generation ledger.
