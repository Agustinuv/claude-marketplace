# IMFD Claude Code Marketplace

Private [Claude Code](https://code.claude.com) plugin marketplace for the IMFD team.
It standardizes the skills, subagents, and connectors we use so everyone develops
with the same tools and conventions.

## Install

```bash
# 1. Add this marketplace (once per machine)
/plugin marketplace add imfd/claude-marketplace

# 2. Install the plugins you want
/plugin install dev-workflow@imfd-marketplace
```

> Replace `imfd/claude-marketplace` with the real `owner/repo` once this is pushed to GitHub.

### Zero-click install per project

Commit this to a project's `.claude/settings.json` and everyone who clones it
gets the plugins enabled automatically:

```json
{
  "extraKnownMarketplaces": {
    "imfd-marketplace": {
      "source": { "source": "github", "repo": "imfd/claude-marketplace" }
    }
  },
  "enabledPlugins": {
    "dev-workflow@imfd-marketplace": true
  }
}
```

### Private repo access

- **Manual install / update:** `gh auth login` or an SSH key with access to the repo.
- **Background auto-update:** set `GITHUB_TOKEN` in your environment.

## Plugins

| Plugin | What it provides |
|--------|------------------|
| `dev-workflow` | Skills for the git/PR/review lifecycle: `git-commits`, `pr-description`, `pre-merge-review`, `frontend-handoff` |

## Repository layout

```
claude-marketplace/
├── .claude-plugin/
│   └── marketplace.json        # Single source of truth: lists all plugins
├── plugins/
│   └── dev-workflow/
│       ├── .claude-plugin/
│       │   └── plugin.json      # Plugin manifest
│       └── skills/              # Auto-scanned; each skill is <name>/SKILL.md
│           ├── git-commits/
│           ├── pr-description/
│           ├── pre-merge-review/
│           └── frontend-handoff/
├── .github/workflows/
│   └── validate.yml            # CI: runs `claude plugin validate .` on every PR
└── CONTRIBUTING.md             # Conventions for adding/updating plugins
```

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md). In short: add or edit a plugin under
`plugins/`, register it in `marketplace.json`, bump the plugin `version`, and open
a PR — CI validates the manifest before merge.
