---
name: new-connector
description: Add or configure an MCP server (external connector) inside a plugin in this marketplace, handling secrets safely. Use when the user wants to add an MCP server, wire up an external API/database/service, bundle a connector, or asks "agrega un conector", "add an MCP server", "conectar un servidor externo".
allowed-tools: Read, Write, Edit, Bash, Glob
---

# Add an MCP connector to a plugin

Add an MCP server to a plugin's `.mcp.json`, routing any credentials through
`userConfig` (never hard-coded). See `${CLAUDE_PLUGIN_ROOT}/references/plugin-reference.md`.

## Steps

1. **Locate the marketplace root** and **pick the target plugin** (list `plugins/*/`).

2. **Gather inputs:**
   - Connector key (kebab-case).
   - Transport: `stdio` (a `command`/`args` subprocess) or `http`/`sse` (a `url`).
   - How it launches or its endpoint URL.
   - Which secrets/config it needs (tokens, endpoints, DB URLs).

3. **Declare secrets as user config** in the plugin's `plugin.json`, so they are prompted
   at enable time and stored in the OS keychain:
   ```json
   "userConfig": {
     "api_token": { "type": "string", "title": "API token", "sensitive": true, "required": true }
   }
   ```

4. **Create/extend** `plugins/<plugin>/.mcp.json`. Reference config as `${user_config.KEY}`:
   ```json
   {
     "mcpServers": {
       "<key>": {
         "command": "npx",
         "args": ["-y", "@company/mcp-server"],
         "env": { "API_TOKEN": "${user_config.api_token}" }
       }
     }
   }
   ```
   For HTTP: use `{ "type": "http", "url": "…", "headers": { "Authorization": "Bearer ${user_config.api_token}" } }`.

5. **Never commit real tokens.** Confirm no secret literal was written to any file.

6. **Bump** the plugin's `version` and **validate**: `claude plugin validate .`.
