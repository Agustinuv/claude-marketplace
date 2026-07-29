#!/usr/bin/env bash
# SessionStart hook: inject the team standard into every session.
#
# It prints two things:
#   1. Tier 1 -- context/team-standards.md, the rules that apply to every line.
#   2. The *resolved absolute paths* of the tier 2 references, discovered by
#      globbing references/ so this list can never go stale.
#
# The second part matters because ${CLAUDE_PLUGIN_ROOT} only resolves inside the
# plugin that owns the file, and a plugin cannot reference another plugin's
# files. Emitting the paths here is what lets skills in git-workflow and
# dev-toolkit read this plugin's references on demand instead of carrying
# duplicated copies that drift.
set -u

ROOT="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"

cat "$ROOT/context/team-standards.md"

# Each reference's own H1 doubles as its description, so adding or renaming a
# file needs no change here.
printf '\n---\n\n## Tier 2 references — read on demand, not upfront\n\n'
printf 'Absolute paths, readable from this session. Open one only when the task calls for\n'
printf 'it; loading them all defeats the point of keeping tier 1 small.\n\n'

for reference in "$ROOT"/references/*.md; do
  [ -f "$reference" ] || continue
  title="$(sed -n 's/^# //p' "$reference" | head -1)"
  printf -- '- `%s`%s\n' "$reference" "${title:+ — $title}"
done
