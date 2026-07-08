---
name: new-plugin
description: Scaffold a brand-new plugin in this Claude Code marketplace and register it. Use when the user wants to create/add a new plugin, start a new bundle of skills/agents/connectors, or asks "crea un plugin nuevo", "add a plugin to the marketplace", "nuevo plugin".
allowed-tools: Read, Write, Edit, Bash, Glob
---

# Create a new plugin

Scaffold a new plugin under `plugins/` and register it in the marketplace manifest,
following the team conventions in `${CLAUDE_PLUGIN_ROOT}/references/plugin-reference.md`
(read it first if you are unsure about any schema).

## Steps

1. **Locate the marketplace root.** Find the directory containing
   `.claude-plugin/marketplace.json` (search upward from the cwd). All paths below are
   relative to it. If not found, tell the user this must be run inside the marketplace repo.

2. **Gather inputs** (ask only for what's missing):
   - `name` — kebab-case, unique. Verify `plugins/<name>/` does not already exist.
   - `displayName` — human-readable.
   - `description` — one precise sentence on what the plugin bundles.
   - keywords (optional).

3. **Create the manifest** `plugins/<name>/.claude-plugin/plugin.json`:
   ```json
   {
     "name": "<name>",
     "displayName": "<displayName>",
     "version": "0.1.0",
     "description": "<description>",
     "author": { "name": "IMFD", "email": "agustin.urrutia@imfd.cl" },
     "keywords": [],
     "license": "MIT"
   }
   ```
   Reuse the `author` from a sibling plugin's `plugin.json` so it stays consistent.

4. **Register it** in `.claude-plugin/marketplace.json` — append to the `plugins` array:
   ```json
   { "name": "<name>", "source": "./plugins/<name>", "displayName": "<displayName>", "description": "<description>" }
   ```

5. **Validate:** run `claude plugin validate .` from the marketplace root. Fix any error.

6. **Next steps:** tell the user the plugin is empty and offer to add components with the
   `new-skill`, `new-agent`, or `new-connector` skills. Remind them to bump `version` and
   open a PR (CI validates it).
