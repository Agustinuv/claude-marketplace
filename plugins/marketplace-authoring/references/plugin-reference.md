# Claude Code plugin & marketplace — schema reference

Authoritative, condensed reference for authoring items in this marketplace.
Official docs: https://code.claude.com/docs/en/plugins-reference

## Repository layout

```
<marketplace-repo>/
├── .claude-plugin/marketplace.json     # lists every plugin
└── plugins/<plugin-name>/
    ├── .claude-plugin/plugin.json      # plugin manifest
    ├── skills/<name>/SKILL.md          # skills (auto-scanned)
    ├── agents/<name>.md                # subagents (auto-scanned)
    ├── commands/<name>.md              # prompt slash-commands (auto-scanned)
    ├── hooks/hooks.json                # event automations
    └── .mcp.json                       # bundled MCP servers (connectors)
```

Component folders are auto-scanned unless `plugin.json` overrides their path.

## marketplace.json

```json
{
  "name": "imfd-marketplace",
  "owner": { "name": "IMFD", "email": "agustin.urrutia@imfd.cl" },
  "description": "…",
  "metadata": { "pluginRoot": "./plugins" },
  "renames": { "old-name": "new-name", "removed-plugin": null },
  "plugins": [
    {
      "name": "git-workflow",                 // REQUIRED, kebab-case, unique
      "source": "./plugins/git-workflow",     // REQUIRED (relative path in same repo)
      "displayName": "Git Workflow",
      "description": "…",
      "category": "productivity",
      "keywords": ["git", "pr"]
    }
  ]
}
```

`source` can also be a git/github/npm object for external plugins, but in this repo
every plugin lives under `./plugins/` and uses a relative path.

`renames` migrates plugin names on consumers' machines: Claude Code loads the plugin under
its new name and rewrites the key in their settings. Map to `null` for a removed plugin.
**Always add the mapping in the same change that renames or removes a plugin** — otherwise
existing installs fail with `plugin-not-found`. The map is append-only: keep old entries so
chains (`old` → `newer` → `current`) still resolve for anyone who skipped updates.

## plugin.json

```json
{
  "name": "plugin-name",          // REQUIRED, kebab-case
  "displayName": "Plugin Name",
  "version": "0.1.0",             // set + bump for stable plugins; omit to track commit SHA
  "description": "…",
  "author": { "name": "IMFD", "email": "agustin.urrutia@imfd.cl" },
  "keywords": ["…"],
  "license": "MIT",

  // Prompted at enable time; sensitive values go to the OS keychain, not settings.json
  "userConfig": {
    "api_token": { "type": "string", "title": "API token", "sensitive": true, "required": true }
  }
}
```

Reference user config from any component as `${user_config.api_token}`.

## SKILL.md

```markdown
---
name: my-skill                    # kebab-case; defaults to folder name
description: Precise trigger sentence — this is what makes Claude auto-invoke the skill. Include the phrases a user would say.
allowed-tools: Read, Bash, Grep   # optional; omit to allow all tools
---

# My Skill

Step-by-step instructions for Claude. Use `$ARGUMENTS` for user input.
Reference bundled files with `${CLAUDE_SKILL_DIR}/scripts/foo.sh`.
```

- `description` is the single most important field — write it as concrete triggers.
- Supporting files go in the skill folder (`scripts/`, `references/`, `templates/`).
- **Files owned by one skill** → `${CLAUDE_SKILL_DIR}/…` (the skill's own directory,
  resolved at load time). Works for personal, project-level, and plugin skills alike.
- **Files shared by several skills of the same plugin** → `${CLAUDE_PLUGIN_ROOT}/…`. This
  is valid inside a `SKILL.md`; use it instead of duplicating a script per skill.
- **Across plugins, sharing is impossible.** Each plugin installs into its own cache
  directory and `../` breaks after install, so a file needed by two plugins must be
  duplicated once per plugin.

## agents/<name>.md (subagent)

```markdown
---
name: my-agent
description: When to use this agent (used for auto-delegation).
tools: Read, Grep, Bash          # optional; omit to inherit all tools
model: sonnet                     # optional
---

System prompt describing the agent's role, method, and output format.
```

## .mcp.json (connector)

```json
{
  "mcpServers": {
    "my-connector": {
      "command": "npx",
      "args": ["-y", "@company/mcp-server"],
      "env": { "API_TOKEN": "${user_config.api_token}" }
    },
    "my-http-connector": {
      "type": "http",
      "url": "https://api.example.com/mcp",
      "headers": { "Authorization": "Bearer ${user_config.api_token}" }
    }
  }
}
```

Transports: `stdio` (default, via `command`/`args`), `http`, `sse`, `websocket`.

## Portability rules (enforced)

- **kebab-case** for all plugin/skill/agent names.
- Comments & docstrings in **English** (team standard).
- Reference a skill's own files with `${CLAUDE_SKILL_DIR}/…`, and files shared across the
  plugin — plus anything in hooks/MCP configs — with `${CLAUDE_PLUGIN_ROOT}/…`. Never use
  paths outside the plugin folder — `../` is blocked.
- Never hard-code secrets. Use `userConfig` + `"sensitive": true` and `${user_config.KEY}`.

## Variables

- `${CLAUDE_SKILL_DIR}` — a skill's own directory (`<plugin>/skills/<name>/`), resolved at
  skill load time. Use for files that belong to that skill alone.
- `${CLAUDE_PLUGIN_ROOT}` — the plugin's installed directory. Valid in `SKILL.md`, agents,
  hooks and MCP configs. Use for files shared by several skills of the plugin.
- `${CLAUDE_PLUGIN_DATA}` — persistent data dir (survives updates).
- `${CLAUDE_PROJECT_DIR}` — the current project root.
- `${user_config.KEY}` — a value from the plugin's `userConfig`.

## Versioning

- Stable plugin: set `version`, bump on every change (updates only pull on a version change).
- Active development: omit `version` so each commit SHA counts as a new version.

## Validate (always run before finishing)

```bash
claude plugin validate .        # from the marketplace repo root
```
