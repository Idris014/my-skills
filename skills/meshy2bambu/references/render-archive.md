# Render Generation and Archive

## Required views

Choose views that prove decisions:

- `01_front_threequarter.png`: overall character and base;
- `02_side_clearance.png`: foot clearance, contact, or silhouette;
- `03_connection_or_plan.png`: underside cavities, magnetic exploded view, or base outline;
- optional standing pose, multiview, source audit, or design comparison.

Use a neutral background and balanced exposure. Keep the full character and support visible. Avoid render-only objects in GLB/STL exports.

## Generated character renders

For image-generated pose references:

- use the accepted character render as identity/costume reference;
- preserve distinctive colors and features;
- state pose, framing, limb count, finger count, and excluded objects;
- save the selected result into the project rather than leaving it only in a generated-image cache;
- label AI-generated references separately from Blender geometry renders.

## Archive policy

Copy, do not move, accepted renders into:

```text
render-archive/VERSION/
├── images/
├── manifest.json
└── README.md
```

The manifest records:

- filename;
- semantic role;
- pixel dimensions when detectable;
- byte size;
- SHA-256;
- original source path;
- archive timestamp.

Do not mix rejected design renders into an accepted-version archive. If comparison images are valuable, put them in a separately named comparison archive.
