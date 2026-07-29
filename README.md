# my-skills

A public collection of reusable Codex skills.

## Skills

| Skill | Description |
| --- | --- |
| [`meshy2bambu`](skills/meshy2bambu/) | Converts images, descriptions, multiview references, or existing AI-generated models into repaired Blender assets and validated Bambu Studio deliveries. |

## Repository layout

```text
my-skills/
├── skills/
│   └── meshy2bambu/
│       ├── SKILL.md
│       ├── assets/
│       ├── evals/
│       ├── references/
│       └── scripts/
├── CONTRIBUTING.md
└── SECURITY.md
```

Each skill is self-contained under `skills/<skill-name>/`, so more skills can be added without
changing the structure of existing ones.

## Install a skill

Ask Codex to install the skill from:

```text
https://github.com/Idris014/my-skills/tree/main/skills/meshy2bambu
```

Or clone and copy it manually:

```bash
git clone https://github.com/Idris014/my-skills.git
cp -R my-skills/skills/meshy2bambu ~/.codex/skills/
```

Restart or begin a new Codex task after installation so the skill catalog refreshes.

## Meshy2Bambu requirements

- `MESHY_API_KEY` for automated Meshy API stages;
- image generation capability when the input is a text description;
- Blender 4.x and Blender MCP, or Blender background Python;
- Bambu Studio for final importer validation and printing handoff.

Never commit API keys or generated credential files. The skill reads the Meshy key only from the
`MESHY_API_KEY` environment variable.

## Adding another skill

1. Create `skills/<new-skill-name>/SKILL.md`.
2. Keep bundled scripts, references, assets, and evals inside that directory.
3. Validate the skill before committing.
4. Add it to the table in this README.

See [CONTRIBUTING.md](CONTRIBUTING.md) for the expected structure and checks.

## License

No open-source license has been selected for this repository yet. Public visibility does not grant
additional reuse rights beyond those provided by applicable law or an individual file's notice.
