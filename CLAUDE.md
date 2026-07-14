# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

This is **not an application** — it is the IMFD team's private [Claude Code](https://code.claude.com)
plugin **marketplace**. It packages the skills, subagents, connectors, and team standards that the
team installs into their own Claude Code sessions. Editing this repo changes the tooling other people
run; it does not run a service.

## Validate (the only "build/test")

There is no compiler, test runner, or linter. Correctness = the manifests are well-formed and every
declared plugin resolves. Validate before every commit and PR:

```bash
claude plugin validate .        # validates marketplace.json + every plugin it declares
```

CI (`.github/workflows/validate.yml`) runs exactly this on push to `main` and on every PR.
There is no single-test command because there are no tests — validation is all-or-nothing.

## Architecture

Three layers, top-down:

1. **`.claude-plugin/marketplace.json`** — the single source of truth. It lists every plugin
   (name, `source` path under `./plugins`, metadata). A plugin does not exist to consumers until it
   is registered here, even if its folder is present.

2. **`plugins/<name>/.claude-plugin/plugin.json`** — one manifest per plugin. Its sibling folders are
   **auto-scanned** by convention (no need to list files): `skills/<name>/SKILL.md`, `commands/*.md`,
   `agents/*.md`, `hooks/hooks.json`, `.mcp.json`. The `version` field controls update propagation
   (see Versioning).

3. **Components** — the actual capabilities. Currently three plugins:
   - **`dev-workflow`** — git/PR lifecycle skills: `git-commits`, `pr-description`, `pre-merge-review`,
     `frontend-handoff`. Each is a `SKILL.md` (auto-invoked by its `description`) plus optional
     `scripts/` and `references/`.
   - **`marketplace-authoring`** — meta-tooling to extend *this* repo: `new-plugin`, `new-skill`,
     `new-agent`, `new-connector`, `validate-marketplace`. When scaffolding anything here, prefer
     invoking these skills — they encode the conventions below. The frontmatter schema they follow
     lives in `plugins/marketplace-authoring/references/plugin-reference.md`.
   - **`team-standards`** — a SessionStart hook (`hooks/hooks.json`) that `cat`s
     `context/team-standards.md` into every session. **That file is the team's engineering standard**
     (commit convention, tooling, architecture rules); editing it changes what every team member's
     Claude sees. It must stay under 10,000 chars (SessionStart injection limit).

## Conventions that must hold

- **Naming:** kebab-case for all plugin and skill names/folders.
- **Skill frontmatter:** every `SKILL.md` needs `name` + a precise `description`. The `description` is
  the *only* thing that makes Claude auto-invoke the skill — write concrete trigger phrases, not vague
  summaries. (Skill prose may be Spanish; code comments/docstrings are English — team standard.)
- **Portable references only:** a plugin must never reference files outside its own folder — `../` is
  blocked by validation. Point at bundled files with `${CLAUDE_PLUGIN_ROOT}/...`; point at a skill's
  own bundled files with `${CLAUDE_SKILL_DIR}/...`.
- **Secrets:** never hard-code tokens. Use `userConfig` with `"sensitive": true` and reference as
  `${user_config.KEY}`.

## Versioning drives updates — bump on every change

Consumers only pick up a plugin change when its `plugin.json` `version` is **bumped**; plain commits are
invisible to `claude plugin update`. So: **any change to a plugin requires bumping that plugin's
`version`** (unless the plugin intentionally omits `version`, in which case each commit SHA counts as a
new version — used for actively-developed plugins). Tag stable releases `<plugin-name>--v<version>`.

## Team flow

Edit → `claude plugin validate .` → PR (CI validates) → merge to `main` (merging *is* the release) →
consumers run `claude plugin marketplace update imfd-marketplace` + `claude plugin update <name>` and
restart. See `CONTRIBUTING.md` for the full add-a-plugin checklist and `README.md` for install details.

Commits/PRs in this repo follow the same Platanus convention the `dev-workflow` plugin ships:
`tipo(contexto): imperative english description`.
