---
name: new-agent
description: Add a specialized subagent to an existing plugin in this marketplace. Use when the user wants to create/add a subagent or custom agent, delegate a recurring role, or asks "agrega un agente", "create a subagent", "nuevo agente".
allowed-tools: Read, Write, Edit, Bash, Glob
---

# Add a subagent to a plugin

Create an `agents/<name>.md` subagent inside a chosen plugin. See the agent schema in
`${CLAUDE_PLUGIN_ROOT}/references/plugin-reference.md`.

## Steps

1. **Locate the marketplace root** and **pick the target plugin** (list `plugins/*/`).

2. **Gather inputs:**
   - `name` — kebab-case, unique within the plugin's `agents/`.
   - The agent's role/purpose and **when it should be auto-delegated** (becomes `description`).
   - Which tools it needs (`tools`) — omit to inherit all; restrict for read-only or
     narrow agents. Model override (`model`) only if there's a reason.

3. **Write** `plugins/<plugin>/agents/<name>.md`:
   ```markdown
   ---
   name: <name>
   description: <when to use / auto-delegate this agent>
   tools: Read, Grep, Bash
   ---

   <System prompt: the agent's role, its method step by step, and the exact
   output format it must return.>
   ```
   Keep the system prompt in English and make the output contract explicit.

4. **Bump** the plugin's `version` and **validate**: `claude plugin validate .`.
