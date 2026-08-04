# my-skills

Reusable, production-focused agent skills for ChatGPT and Codex.

This repository collects self-contained workflows for 3D-print production, portrait retouching,
and AI short-film or music-video production. Each skill combines a focused `SKILL.md` with the
references, scripts, assets, and UI metadata needed to execute the workflow consistently.

> [!NOTE]
> These are standalone skills, not a plugin bundle. A skill provides instructions and supporting
> resources; it does not include access to paid models, third-party applications, or external APIs.

## Available skills

| Skill | Best for | Highlights |
| --- | --- | --- |
| [`meshy2bambu`](skills/meshy2bambu/) | Turning images, descriptions, multiview references, or existing meshes into printable Blender and Bambu Studio deliverables | Meshy generation, non-destructive mesh repair, texture preservation, multicolor preparation, parameterized bases, magnets and locating holes, export validation |
| [`portrait`](skills/portrait/) | Gated portrait retouching across Lightroom and Photoshop | Global tone, subject/background masks, identity-preserving facial geometry, neutral-gray dodge and burn, controlled clothing and makeup stages, A/B review gates |
| [`produce-short-film-mv`](skills/produce-short-film-mv/) | Planning, generating, auditing, and packaging narrative shorts, MVs, opening films, trailers, and episodic short-form video | Asset locking, Image2 storyboard prompts, START/END keyframes, continuity review, Seedance 2.0 shot prompts, generation ledgers, edit plans, QA and handoff |

## Quick start

### Install with Codex

Use the built-in skill installer and give it the URL of the skill you want:

```text
$skill-installer Install the skill from https://github.com/Idris014/my-skills/tree/main/skills/<skill-name>
```

Replace `<skill-name>` with one of:

- `meshy2bambu`
- `portrait`
- `produce-short-film-mv`

Codex normally detects newly installed skills automatically. If the skill does not appear, restart
Codex and open a new task.

### Install manually

Clone the repository and copy one skill into your user-level skill directory:

```bash
git clone https://github.com/Idris014/my-skills.git
mkdir -p "$HOME/.agents/skills"
cp -R "my-skills/skills/<skill-name>" "$HOME/.agents/skills/"
```

To make a skill available only inside one repository, copy it to
`<your-repository>/.agents/skills/` instead.

## Use a skill

Invoke a skill explicitly by mentioning it in your prompt:

```text
$meshy2bambu Turn these reference images into a printable multicolor model with a magnetic base.

$portrait Continue retouching the open portrait non-destructively and pause after each review gate.

$produce-short-film-mv Turn this screenplay into locked visual assets, START/END storyboards, and reviewed video prompts.
```

ChatGPT and Codex can also select a skill automatically when a request matches the skill's
frontmatter `description`.

## Requirements

### `meshy2bambu`

- `MESHY_API_KEY` when automated Meshy generation is requested;
- image-generation capability when the source is a text description;
- Blender 4.x with Blender MCP or background Python;
- Python 3.10+ with NumPy for fallback 3MF audits;
- Bambu Studio CLI plus standard archive and filesystem tools for final delivery checks.

The skill preserves source meshes, supports circular, elliptical, and rounded-rectangle bases, and
can emit machine-readable manifold and contact evidence. It must not start paid generation without
the user's approval.

### `portrait`

- Adobe Lightroom desktop;
- Adobe Photoshop;
- a supported UI or computer-control capability for operating the applications.

The workflow is deliberately gated and non-destructive. It pauses after each stage so the user can
review or adjust the result before continuing.

### `produce-short-film-mv`

- image-generation or image-editing capability when visual assets are requested;
- access to the selected video engine when video generation is requested;
- Python 3 for the bundled deterministic storyboard audit.

The skill can prepare copy-paste prompts and exact filenames when a generation service is available
only through a web interface. It does not bundle or grant access to Seedance or any other commercial
generation service.

## Repository layout

```text
my-skills/
├── skills/
│   ├── meshy2bambu/
│   │   ├── SKILL.md
│   │   ├── assets/
│   │   ├── evals/
│   │   ├── references/
│   │   └── scripts/
│   ├── portrait/
│   │   ├── SKILL.md
│   │   ├── agents/
│   │   ├── evals/
│   │   └── references/
│   └── produce-short-film-mv/
│       ├── SKILL.md
│       ├── agents/
│       ├── references/
│       └── scripts/
├── CONTRIBUTING.md
├── SECURITY.md
└── README.md
```

Only `SKILL.md` is required. The other directories are optional and remain scoped to their owning
skill:

- `agents/openai.yaml` — display metadata and invocation defaults;
- `references/` — detailed guidance loaded only when relevant;
- `scripts/` — deterministic helpers and audits;
- `assets/` — reusable templates or source resources;
- `evals/` — trigger and behavior evaluation cases.

## Update an installed skill

If you installed from a local clone, pull the latest version and copy the skill again:

```bash
git -C my-skills pull --ff-only
cp -R "my-skills/skills/<skill-name>" "$HOME/.agents/skills/"
```

Review the skill's Git history before updating if you depend on a pinned workflow or production
environment.

## Contributing

Contributions should keep each skill focused, self-contained, and auditable. Before opening a change:

1. confirm the frontmatter `name` matches the directory name and the `description` clearly states
   when the skill should trigger;
2. keep all references, scripts, assets, and evals inside `skills/<skill-name>/`;
3. check for credentials, private URLs, machine-specific paths, and generated output;
4. compile Python helpers and run relevant deterministic tests or dry-runs;
5. validate `SKILL.md` and update the skills table above.

See [CONTRIBUTING.md](CONTRIBUTING.md) for the repository checks and expected structure.

## Security and credentials

Never commit API keys, access tokens, generated credential files, or private production assets.
`meshy2bambu` reads the Meshy credential only from the `MESHY_API_KEY` environment variable.

For vulnerability reports and sensitive disclosures, follow [SECURITY.md](SECURITY.md).

## License

No open-source license has been selected for this repository. Public visibility does not grant
additional reuse rights beyond those provided by applicable law or an individual file's notice.

## References

- [OpenAI: Build skills](https://developers.openai.com/codex/skills)
- [Agent Skills specification](https://agentskills.io/)
