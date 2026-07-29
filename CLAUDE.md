# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

This is **not an application** — it is the IMFD team's private [Claude Code](https://code.claude.com)
plugin **marketplace**. It packages the skills, subagents, connectors, and team standards that the
team installs into their own Claude Code sessions. Editing this repo changes the tooling other people
run; it does not run a service.

## Checks (the "build/test" of this repo)

There is no compiler. Correctness = the manifests are well-formed, every declared plugin resolves,
and our own conventions hold. Run all three before every commit and PR:

```bash
claude plugin validate .                          # manifest + plugin schema (syntax only)
bash scripts/test_check_conventions.sh            # proves the checker still detects violations
python3 scripts/check_conventions.py --base main  # our conventions, which the CLI cannot see
```

`claude plugin validate .` only checks schema and syntax. `scripts/check_conventions.py` covers
what it cannot: registration consistency, skill frontmatter, bundled-file references that actually
resolve, portable paths, missing version bumps, the injected-context budget, and hard-coded secrets.
Its own regression tests inject one violation at a time into a throwaway copy of the repo — if you
add a check, add a case there too, or the check is unverified.

CI (`.github/workflows/validate.yml`) runs all three on push to `main` and on every PR. On a PR it
passes the base SHA so the version-bump check is active; without `--base` that one check is skipped.

## Architecture

Three layers, top-down:

1. **`.claude-plugin/marketplace.json`** — the single source of truth. It lists every plugin
   (name, `source` path under `./plugins`, metadata). A plugin does not exist to consumers until it
   is registered here, even if its folder is present. Its `renames` map migrates plugin names on
   consumers' machines; it is append-only, and removing an entry without a mapping breaks installs.

2. **`plugins/<name>/.claude-plugin/plugin.json`** — one manifest per plugin. Its sibling folders are
   **auto-scanned** by convention (no need to list files): `skills/<name>/SKILL.md`, `agents/*.md`,
   `hooks/hooks.json`, `.mcp.json`. The `version` field controls update propagation (see Versioning).
   Skill scanning is **single-level** — `skills/<group>/<name>/SKILL.md` is never discovered, so group
   related skills with a name prefix (`backend-*`, `frontend-*`) instead of subfolders. Prefer `skills/`
   over `commands/`, which is legacy.

3. **Components** — the actual capabilities. Four plugins, split by reason-to-change:
   - **`team-standards`** — owns the standard *and* its enforcement. A SessionStart hook
     (`hooks/hooks.json`) `cat`s `context/team-standards.md` into every session: **that file is the
     team's engineering standard**, and editing it changes what every team member's Claude sees. It is
     tier 1 — always injected, so its size is a recurring per-session token cost; keep it lean and put
     detail in `references/`, which skills read on demand. The hook also emits the **resolved absolute
     paths** of those references, which is how skills in *other* plugins reach them —
     `${CLAUDE_PLUGIN_ROOT}` only resolves inside its own plugin. `pre-commit/` holds the git-side
     mechanical checks (named apart from `hooks/`, which means Claude Code hooks), installed into a
     consumer repo by the `setup-standards-lint` skill.
   - **`git-workflow`** — repository lifecycle: `git-commits`, `pr-description`, `pre-merge-review`.
   - **`dev-toolkit`** — development activities, named `<area>-<action>`: `frontend-handoff`,
     `backend-handoff`, `backend-scaffold`, `standards-audit`.
   - **`marketplace-authoring`** — meta-tooling to extend *this* repo: `new-plugin`, `new-skill`,
     `new-agent`, `new-connector`, `validate-marketplace`, `audit-marketplace`. When scaffolding
     anything here, prefer invoking these skills — they encode the conventions below. The frontmatter
     schema they follow lives in `plugins/marketplace-authoring/references/plugin-reference.md`.

   Each skill is a `SKILL.md` (auto-invoked by its `description`) plus optional `scripts/` and
   `references/`. Files shared by several skills of one plugin live at the plugin root.

## Conventions that must hold

- **Naming:** kebab-case for all plugin and skill names/folders.
- **Skill frontmatter:** every `SKILL.md` needs `name` + a precise `description`. The `description` is
  the *only* thing that makes Claude auto-invoke the skill — write concrete trigger phrases, not vague
  summaries. (Skill prose may be Spanish; code comments/docstrings are English — team standard.)
- **Portable references only:** a plugin must never reference files outside its own folder — `../` is
  blocked by validation. Point at a skill's own bundled files with `${CLAUDE_SKILL_DIR}/...`; point at
  files shared across the plugin with `${CLAUDE_PLUGIN_ROOT}/...` (valid inside a `SKILL.md`). Sharing
  a file *between* plugins is impossible — each installs into its own cache dir, so duplicate it.
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

Commits/PRs in this repo follow the same Platanus convention the `git-workflow` plugin ships:
`tipo(contexto): imperative english description`.
