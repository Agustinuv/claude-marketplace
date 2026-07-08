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
  "plugins": [
    {
      "name": "dev-workflow",                 // REQUIRED, kebab-case, unique
      "source": "./plugins/dev-workflow",     // REQUIRED (relative path in same repo)
      "displayName": "Dev Workflow",
      "description": "…",
      "category": "productivity",
      "keywords": ["git", "pr"]
    }
  ]
}
```

`source` can also be a git/github/npm object for external plugins, but in this repo
every plugin lives under `./plugins/` and uses a relative path.

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
Reference bundled files with `${CLAUDE_PLUGIN_ROOT}/skills/my-skill/scripts/foo.sh`.
```

- `description` is the single most important field — write it as concrete triggers.
- Supporting files go in the skill folder (`scripts/`, `references/`, `templates/`).

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
- Inside a plugin, reference bundled files with `${CLAUDE_PLUGIN_ROOT}/…`. Never use
  paths outside the plugin folder — `../` is blocked for installed plugins.
- Never hard-code secrets. Use `userConfig` + `"sensitive": true` and `${user_config.KEY}`.

## Variables

- `${CLAUDE_PLUGIN_ROOT}` — the plugin's installed directory.
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
