# Contributing to the IMFD marketplace

## Adding a new plugin

1. Create `plugins/<plugin-name>/.claude-plugin/plugin.json` (kebab-case name).
2. Add its components in the conventional folders (auto-scanned unless overridden in `plugin.json`):
   - `skills/<name>/SKILL.md` — invocable / auto-invoked skills
   - `commands/*.md` — simple prompt slash-commands
   - `agents/*.md` — specialized subagents
   - `hooks/hooks.json` — event automations
   - `.mcp.json` — bundled MCP servers (connectors)
3. Register the plugin in `.claude-plugin/marketplace.json` under `plugins`.
4. Run `claude plugin validate .` locally, then open a PR.

## Conventions

- **Naming:** kebab-case for plugin and skill names.
- **Skill frontmatter:** every `SKILL.md` needs `name` and `description`. Write a
  precise `description` — it is what makes Claude auto-invoke the skill.
- **Comments/docstrings in English** (team standard). Prose in skills may be in Spanish.
- **Portable references:** inside a plugin use `${CLAUDE_PLUGIN_ROOT}` to point at
  bundled scripts/files. A plugin must never reference files outside its own folder (`../` is blocked).
- **Secrets:** never hard-code tokens. Use `userConfig` with `"sensitive": true`
  (stored in the OS keychain) and reference as `${user_config.KEY}`.

## Versioning

- **Stable plugins:** set `version` in `plugin.json` and bump it on every change
  (Claude Code only pulls updates when the version changes). Tag releases
  `<plugin-name>--v<version>`.
- **Actively developed plugins:** omit `version` so each commit SHA is treated as a
  new version.

## Releasing

Merging to `main` is the release. Consumers pick up changes on
`/plugin marketplace update imfd-marketplace` (or automatically in the background
when a `GITHUB_TOKEN` is set).
