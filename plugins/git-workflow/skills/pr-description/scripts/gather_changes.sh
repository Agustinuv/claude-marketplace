#!/usr/bin/env bash
# Recolecta la información necesaria para redactar una descripción de PR:
# rama actual, rama destino resuelta, commits, diff stat y diff completo.
#
# Uso: gather_changes.sh [rama-destino]
# Si no se pasa rama destino, intenta usar main y si no existe, master.

set -uo pipefail

TARGET="${1:-}"
CURRENT_BRANCH=$(git branch --show-current)

if [ -z "$CURRENT_BRANCH" ]; then
  echo "ERROR: no se pudo determinar la rama actual (¿estás en detached HEAD?)" >&2
  exit 1
fi

# Resolver rama destino si no se especificó
if [ -z "$TARGET" ]; then
  for candidate in main master; do
    if git show-ref --verify --quiet "refs/heads/$candidate" || \
       git show-ref --verify --quiet "refs/remotes/origin/$candidate"; then
      TARGET="$candidate"
      break
    fi
  done
fi

if [ -z "$TARGET" ]; then
  echo "ERROR: no existe 'main' ni 'master'. Indica explícitamente la rama destino." >&2
  exit 1
fi

if [ "$TARGET" = "$CURRENT_BRANCH" ]; then
  echo "ERROR: la rama destino ('$TARGET') es la misma que la rama actual." >&2
  exit 1
fi

# Intento best-effort de traer referencias actualizadas
git fetch origin "$TARGET" "$CURRENT_BRANCH" --quiet 2>/dev/null || true

# Preferir origin/<target> si existe, si no, la rama local
if git show-ref --verify --quiet "refs/remotes/origin/$TARGET"; then
  BASE="origin/$TARGET"
elif git show-ref --verify --quiet "refs/heads/$TARGET"; then
  BASE="$TARGET"
else
  echo "ERROR: la rama destino '$TARGET' no existe ni localmente ni en origin." >&2
  exit 1
fi

echo "=== CURRENT_BRANCH ==="
echo "$CURRENT_BRANCH"

echo
echo "=== TARGET_BRANCH (resuelta) ==="
echo "$BASE"

echo
echo "=== COMMITS (merge-base..HEAD) ==="
git log "${BASE}..HEAD" --pretty=format:'%h %s'
echo

echo
echo "=== DIFF STAT ==="
git diff --stat "${BASE}...HEAD"

echo
echo "=== CHANGED_FILES ==="
git diff --name-only "${BASE}...HEAD"

echo
echo "=== FULL_DIFF ==="
git diff "${BASE}...HEAD"
