# Contributing to the IMFD marketplace

## Adding a new plugin

1. Create `plugins/<plugin-name>/.claude-plugin/plugin.json` (kebab-case name).
2. Add its components in the conventional folders (auto-scanned unless overridden in `plugin.json`):
   - `skills/<name>/SKILL.md` — invocable / auto-invoked skills (preferred)
   - `agents/*.md` — specialized subagents
   - `hooks/hooks.json` — event automations
   - `.mcp.json` — bundled MCP servers (connectors)
   - `commands/*.md` — legacy prompt slash-commands; prefer a skill instead
3. Register the plugin in `.claude-plugin/marketplace.json` under `plugins`.
4. Run the checks below locally, then open a PR.

Prefer scaffolding through the `marketplace-authoring` skills (`new-plugin`, `new-skill`,
`new-agent`, `new-connector`) — they already encode everything here.

## Checks (run all three before opening a PR)

```bash
claude plugin validate .                          # manifest + plugin schema (syntax only)
bash scripts/test_check_conventions.sh            # the checker still detects violations
python3 scripts/check_conventions.py --base main  # our conventions
```

If you add a check to `scripts/check_conventions.py`, add a case to
`scripts/test_check_conventions.sh` as well — an unverified check is worse than none, because
a green run then means nothing.

## Conventions

- **Naming:** kebab-case for plugin and skill names.
- **Skill frontmatter:** every `SKILL.md` needs `name` and `description`, and `name` must match its
  folder. Write a precise `description` — it is what makes Claude auto-invoke the skill.
- **No nested skills:** plugin skill scanning is single-level, so `skills/<group>/<name>/SKILL.md` is
  never discovered. Group related skills with a name prefix (`backend-*`, `frontend-*`).
- **Comments/docstrings in English** (team standard). Prose in skills may be in Spanish.
- **Portable references:** point at a skill's own files with `${CLAUDE_SKILL_DIR}/…`, and at files
  shared by several skills of the plugin with `${CLAUDE_PLUGIN_ROOT}/…` (valid inside a `SKILL.md`).
  A plugin must never reference files outside its own folder — `../` is blocked after install, and
  sharing a file *between* plugins is impossible, so duplicate it once per plugin.
- **Secrets:** never hard-code tokens. Use `userConfig` with `"sensitive": true`
  (stored in the OS keychain) and reference as `${user_config.KEY}`.

## Renaming or removing a plugin

Add the mapping to `renames` in `marketplace.json` **in the same change**: `"old-name": "new-name"`,
or `"old-name": null` if the plugin is gone. Without it, everyone who had it installed gets
`plugin-not-found`. The map is append-only — never delete an old entry, so rename chains keep
resolving for people who skipped a few updates.

## Versioning

- **Stable plugins:** set `version` in `plugin.json` and bump it on every change
  (Claude Code only pulls updates when the version changes). We do not tag releases —
  the `version` field is the only thing consumers resolve.
- **Actively developed plugins:** omit `version` so each commit SHA is treated as a
  new version.

## Releasing

Merging to `main` is the release. Consumers pick up changes on
`/plugin marketplace update imfd-marketplace` (or automatically in the background
when a `GITHUB_TOKEN` is set).
