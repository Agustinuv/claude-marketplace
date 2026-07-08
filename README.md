# IMFD Claude Code Marketplace

Private [Claude Code](https://code.claude.com) plugin marketplace for the IMFD team.
It standardizes the skills, subagents, and connectors we use so everyone develops
with the same tools and conventions.

## Install

You can drive this from the TUI (`/plugin …`) or from the shell (`claude plugin …`) —
both are equivalent.

```bash
# 1. Add this marketplace (once per machine)
claude plugin marketplace add imfd/claude-marketplace     # from GitHub
# or, for local development of the marketplace itself:
claude plugin marketplace add /path/to/claude-marketplace # from a local directory

# 2. Install the plugins you want (marketplace name is "imfd-marketplace")
claude plugin install dev-workflow@imfd-marketplace
claude plugin install team-standards@imfd-marketplace
claude plugin install marketplace-authoring@imfd-marketplace
```

Restart your Claude Code session afterwards — plugins (skills, hooks) load at session start.

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

## Updating

When this repo changes (a new skill, an edited standard, a new plugin):

```bash
claude plugin marketplace update imfd-marketplace   # pull the latest from the source
claude plugin update <plugin-name>                  # update a plugin (restart to apply)
```

When does a change become visible?

- **GitHub source:** `marketplace update` does a `git pull` of the clone. A plugin only
  counts as a new version when its `plugin.json` `version` is **bumped** (plain commits are
  not enough) — that's why bumping is required in [CONTRIBUTING.md](./CONTRIBUTING.md). If a
  plugin omits `version`, every commit SHA counts as a new version.
- **Local directory source:** the marketplace is referenced in place, so `marketplace update`
  re-reads your working copy — your edits show up after update + restart. Ideal while
  developing the marketplace.

Team flow: edit → PR (CI validates) → merge to `main` → everyone runs `marketplace update`
+ `plugin update` and restarts.

## Where it lives on your machine

| What | Location |
|------|----------|
| Registered marketplaces | `~/.claude/plugins/known_marketplaces.json` |
| Installed plugins | `~/.claude/plugins/installed_plugins.json` |
| Enabled state + known marketplaces | `~/.claude/settings.json` (`enabledPlugins`, `extraKnownMarketplaces`) |
| GitHub-source content | cloned to `~/.claude/plugins/marketplaces/<name>/` |
| Local-directory content | referenced in place (your repo path — not copied) |

## Plugins

| Plugin | What it provides |
|--------|------------------|
| `dev-workflow` | Skills for the git/PR/review lifecycle: `git-commits`, `pr-description`, `pre-merge-review`, `frontend-handoff` |
| `marketplace-authoring` | Meta-tooling to extend the marketplace: skills `new-plugin`, `new-skill`, `new-agent`, `new-connector`, `validate-marketplace` + a bundled schema reference |
| `team-standards` | Injects the team's coding standards & PR conventions into every session (SessionStart hook). Edit `plugins/team-standards/context/team-standards.md` to change the standard |

## Repository layout

```
claude-marketplace/
├── .claude-plugin/
│   └── marketplace.json            # Single source of truth: lists all plugins
├── plugins/
│   ├── dev-workflow/
│   │   ├── .claude-plugin/plugin.json
│   │   └── skills/                 # git-commits, pr-description, pre-merge-review, frontend-handoff
│   ├── marketplace-authoring/
│   │   ├── .claude-plugin/plugin.json
│   │   ├── skills/                 # new-plugin, new-skill, new-agent, new-connector, validate-marketplace
│   │   └── references/             # bundled schema reference
│   └── team-standards/
│       ├── .claude-plugin/plugin.json
│       ├── hooks/hooks.json        # SessionStart -> injects the standard
│       └── context/team-standards.md
├── .github/workflows/
│   └── validate.yml                # CI: runs `claude plugin validate .` on every PR
├── CONTRIBUTING.md                 # Conventions for adding/updating plugins
└── README.md
```

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md). In short: add or edit a plugin under
`plugins/`, register it in `marketplace.json`, bump the plugin `version`, and open
a PR — CI validates the manifest before merge.
