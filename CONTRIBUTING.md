# Contributing

## Add or update a skill

Use one directory per skill:

```text
skills/<skill-name>/
├── SKILL.md
├── assets/
├── evals/
├── references/
└── scripts/
```

Only `SKILL.md` is mandatory. Keep the frontmatter name in kebab-case or lowercase alphanumeric
form accepted by the Codex skill validator.

Before committing:

1. confirm the skill contains no credentials, access tokens, private URLs, or machine-specific
   absolute paths;
2. compile Python helper scripts;
3. validate `SKILL.md`;
4. run relevant deterministic tests or dry-runs;
5. update the skill table in the root README.

Do not commit generated models, Blender recovery files, Meshy task downloads, Bambu print jobs, or
other large outputs unless the repository is deliberately expanded to manage those artifacts.
