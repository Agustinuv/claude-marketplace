---
name: validate-marketplace
description: Validate the whole marketplace and run the release checklist before publishing changes. Use when the user wants to validate/check the marketplace, verify a plugin is well-formed, prepare a release, or asks "valida el marketplace", "está listo para publicar", "check the manifest".
allowed-tools: Read, Bash, Glob, Edit
---

# Validate the marketplace before publishing

Run the mechanical validation plus a conventions checklist over every plugin.

## Steps

1. **Locate the marketplace root** (dir with `.claude-plugin/marketplace.json`).

2. **Run the validator:** `claude plugin validate .`. Report and fix any failure before
   continuing.

3. **Cross-check registration:** every directory under `plugins/` must have a matching
   entry in `marketplace.json` `plugins[]`, and every entry's `source` must point to an
   existing folder. Flag mismatches.

4. **Conventions checklist** (report violations, offer to fix):
   - Names are kebab-case (plugins, skills, agents).
   - Every `SKILL.md` has `name` + a concrete, trigger-oriented `description`.
   - Every subagent `.md` has `name` + `description`.
   - No hard-coded secrets anywhere; credentials go through `userConfig` + `${user_config.*}`.
   - No `../` references or paths outside a plugin folder; bundled files use `${CLAUDE_PLUGIN_ROOT}`.
   - Code comments/docstrings are in English.

5. **Version bump:** for any plugin that changed, confirm its `version` in `plugin.json`
   was bumped (otherwise consumers won't receive the update). Offer to bump it.

6. **Summary:** report the result as PASS/FAIL with the exact items to fix, and remind the
   user to open a PR — CI (`.github/workflows/validate.yml`) re-runs this on every PR.
