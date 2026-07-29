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
claude plugin install team-standards@imfd-marketplace
claude plugin install git-workflow@imfd-marketplace
claude plugin install dev-toolkit@imfd-marketplace
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
    "team-standards@imfd-marketplace": true,
    "git-workflow@imfd-marketplace": true
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

### Renamed plugins

`dev-workflow` was split into `git-workflow` (repository lifecycle) and `dev-toolkit`
(development activities). The `renames` map in `marketplace.json` migrates this for you:
after `marketplace update`, a session that had `dev-workflow` enabled loads it as
`git-workflow`, shows a one-line notice, and rewrites the key in your settings. On a GitHub
source you may need `claude plugin install git-workflow@imfd-marketplace` once to fetch it
under the new name. `dev-toolkit` is a new plugin — install it explicitly if you want it.

Never delete a plugin entry without adding its `renames` mapping first, or consumers get
`plugin-not-found`. The map is append-only: keep old entries so rename chains keep resolving.

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
| `team-standards` | The team's engineering standard, injected into every session (SessionStart hook), plus the mechanical pre-commit checks that enforce it. Edit `plugins/team-standards/context/team-standards.md` to change the standard |
| `git-workflow` | Repository lifecycle: `git-commits`, `pr-description`, `pre-merge-review` |
| `dev-toolkit` | Development activities, named by area: `frontend-handoff`, `backend-handoff`, `backend-scaffold`, `standards-audit` |
| `marketplace-authoring` | Meta-tooling to extend the marketplace: `new-plugin`, `new-skill`, `new-agent`, `new-connector`, `validate-marketplace`, `audit-marketplace` + a bundled schema reference |

## Repository layout

```
claude-marketplace/
├── .claude-plugin/
│   └── marketplace.json            # Single source of truth: lists all plugins + renames
├── plugins/
│   ├── team-standards/
│   │   ├── .claude-plugin/plugin.json
│   │   ├── hooks/                  # SessionStart -> injects tier 1 + the tier 2 paths
│   │   ├── pre-commit/             # git-side mechanical checks + config template
│   │   ├── context/                # tier 1: always injected, kept small
│   │   ├── references/             # tier 2: detail, read on demand by skills
│   │   └── skills/                 # setup-standards-lint
│   ├── git-workflow/
│   │   ├── .claude-plugin/plugin.json
│   │   ├── scripts/                # shared across this plugin's skills
│   │   └── skills/                 # git-commits, pr-description, pre-merge-review
│   ├── dev-toolkit/
│   │   ├── .claude-plugin/plugin.json
│   │   ├── scripts/                # shared across this plugin's skills
│   │   └── skills/                 # frontend-handoff, backend-handoff, backend-scaffold, standards-audit
│   └── marketplace-authoring/
│       ├── .claude-plugin/plugin.json
│       ├── skills/                 # new-plugin, new-skill, new-agent, new-connector, validate-marketplace, audit-marketplace
│       └── references/             # bundled schema reference
├── scripts/
│   ├── check_conventions.py        # conventions the CLI validator cannot see
│   └── test_check_conventions.sh   # proves the checker still detects violations
├── .github/workflows/
│   └── validate.yml                # CI: plugin validate + checker tests + conventions
├── CONTRIBUTING.md                 # Conventions for adding/updating plugins
└── README.md
```

## Checks

```bash
claude plugin validate .                          # manifest + plugin schema
bash scripts/test_check_conventions.sh            # the checker still catches violations
python3 scripts/check_conventions.py --base main  # our own conventions
```

CI runs all three on every PR. The `--base` argument enables the version-bump check;
without it that single check is skipped.

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md). In short: add or edit a plugin under
`plugins/`, register it in `marketplace.json`, bump the plugin `version`, and open
a PR — CI validates the manifest and our conventions before merge.
