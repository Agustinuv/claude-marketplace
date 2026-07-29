#!/usr/bin/env bash
# Regression tests for scripts/check_conventions.py.
#
# A checker that passes on a clean repo proves nothing, so this injects one
# violation at a time into a throwaway copy of the marketplace and asserts the
# matching check fires. The real repo is never modified.
#
# Usage: bash scripts/test_check_conventions.sh
set -u

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

FIXTURE="$WORK/marketplace"
cp -R "$ROOT" "$FIXTURE"
cd "$FIXTURE" || exit 1

# Commit whatever state the repo is in, then pin a baseline ref of our own.
# Relying on "main" would make the version-bump test depend on which branches
# happen to exist locally or on the CI checkout.
git add -A >/dev/null 2>&1
git -c user.email=test@local -c user.name=test commit -qm "fixture baseline" >/dev/null 2>&1
git branch -f test-base HEAD >/dev/null 2>&1

CHECK="python3 scripts/check_conventions.py --base test-base"
pass=0
missed=0

# replace <file> <search> <replacement>
replace() {
  python3 -c "
import sys
from pathlib import Path
path = Path(sys.argv[1])
path.write_text(path.read_text().replace(sys.argv[2], sys.argv[3]))
" "$1" "$2" "$3"
}

# expect <category> <description> -- the mutation must already be applied
expect() {
  local category="$1" description="$2" output
  output="$($CHECK 2>&1)"
  if grep -q "FAIL  \[$category\]" <<<"$output"; then
    printf 'ok    %-14s %s\n' "[$category]" "$description"
    pass=$((pass + 1))
  else
    printf 'MISS  %-14s %s\n' "[$category]" "$description"
    printf '      got: %s\n' "$(head -2 <<<"$output" | tr '\n' ' ')"
    missed=$((missed + 1))
  fi
  git reset -q --hard test-base
  git clean -qfd
}

first_skill() {
  find plugins -path '*/skills/*/SKILL.md' | sort | head -1
}

# 1. A plugin folder nobody registered in marketplace.json.
mkdir -p plugins/ghost-plugin/.claude-plugin
echo '{"name":"ghost-plugin","version":"0.1.0"}' \
  >plugins/ghost-plugin/.claude-plugin/plugin.json
expect registration "unregistered plugin folder"

# 2. Frontmatter name that disagrees with its folder.
target="$(first_skill)"
replace "$target" "$(sed -n 's/^name: //p' "$target" | head -1)" "renamed-skill"
expect skills "skill name does not match folder"

# 3. Nested skill directory: plugin skill scanning is single-level.
nested="$(dirname "$(dirname "$(first_skill)")")/grouped/deep-skill"
mkdir -p "$nested"
printf -- '---\nname: deep-skill\ndescription: %s\n---\n\nBody.\n' \
  "Long enough a description to clear the minimum-length warning threshold." \
  >"$nested/SKILL.md"
expect skills "nested skill directory"

# 4. A bundled-file reference pointing at something that does not exist.
printf '\nRun ${CLAUDE_SKILL_DIR}/scripts/does_not_exist.sh\n' >>"$(first_skill)"
expect references "broken bundled-file reference"

# 5. A path escaping the plugin folder.
printf '\nSee ${CLAUDE_PLUGIN_ROOT}/../elsewhere/scripts/x.sh\n' >>"$(first_skill)"
expect portability "path escaping the plugin folder"

# 6. Plugin content changed, version left untouched.
printf '\nAn extra line that changes this plugin.\n' \
  >>plugins/team-standards/context/team-standards.md
git add -A >/dev/null 2>&1
git -c user.email=test@local -c user.name=test commit -qm "change without bump" >/dev/null 2>&1
expect version "changed plugin without a version bump"

# 7. Injected context over its byte budget.
python3 -c "
from pathlib import Path
path = Path('plugins/team-standards/context/team-standards.md')
path.write_text(path.read_text() + '\npadding to exceed the budget.' * 500)
"
expect budget "team-standards.md over byte budget"

# 8. A hard-coded credential literal.
printf '\napi_key: "sk-live-9f3b7c2a4e8d1f6b0a5c"\n' >>"$(first_skill)"
expect secrets "hard-coded credential literal"

echo
if [ "$missed" -eq 0 ]; then
  echo "All $pass checker tests passed."
else
  echo "passed=$pass missed=$missed"
fi
[ "$missed" -eq 0 ]
