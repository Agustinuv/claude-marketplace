---
name: new-skill
description: Add a new skill to an existing plugin in this marketplace, with correct SKILL.md frontmatter. Use when the user wants to create/add a skill, encode a repeatable workflow, or asks "agrega una skill", "create a skill", "nueva skill en el plugin X".
allowed-tools: Read, Write, Edit, Bash, Glob
---

# Add a skill to a plugin

Create a well-formed `skills/<name>/SKILL.md` inside a chosen plugin. Follow
`${CLAUDE_PLUGIN_ROOT}/references/plugin-reference.md` for the frontmatter schema.

## Steps

1. **Locate the marketplace root** (dir with `.claude-plugin/marketplace.json`).

2. **Pick the target plugin.** List `plugins/*/` and confirm which plugin the skill
   belongs to. If none fits, suggest running `new-plugin` first.

3. **Gather inputs:**
   - `name` — kebab-case, unique within the plugin. Verify the folder doesn't exist.
   - What the skill does, and the **exact phrases a user would say to trigger it** — you
     will turn these into the `description`.
   - Whether it must restrict tools (`allowed-tools`) — omit unless there's a reason.

4. **Write** `plugins/<plugin>/skills/<name>/SKILL.md`:
   ```markdown
   ---
   name: <name>
   description: <precise trigger sentence with the phrases a user would say>
   ---

   # <Title>

   <Step-by-step instructions for Claude. Use $ARGUMENTS for user input.
   Reference bundled files as ${CLAUDE_PLUGIN_ROOT}/skills/<name>/...>
   ```
   The `description` is what makes Claude auto-invoke the skill — make it concrete, not vague.

5. **Supporting files (optional):** create `scripts/`, `references/`, or `templates/`
   subfolders as needed and reference them from the SKILL.md with
   `${CLAUDE_SKILL_DIR}/...` (the skill's own directory; never `../`, never
   `${CLAUDE_PLUGIN_ROOT}` for skill files). Write code comments/docstrings in English.

6. **Bump** the plugin's `version` in `plugin.json`, then **validate**:
   `claude plugin validate .`.
