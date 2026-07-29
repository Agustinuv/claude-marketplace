#!/usr/bin/env python3
"""Flag comments and docstrings that are not written in English.

Part of the IMFD team standard: the codebase is in English even when the
conversation is not. `pre-commit` passes only the files a commit touches, so
pre-existing Spanish comments never block unrelated work.

Usage:
    check_comment_language.py <file>...

Detection is deliberately conservative -- a comment is flagged only when it
contains a Spanish-specific character (á, ñ, ¿ ...) or at least two distinct
Spanish function words. To keep a non-English comment on purpose, add the marker
`standards: allow-non-english` to that same comment.

Known limitation: a '#' or '//' inside a string literal is treated as starting a
comment. That costs a rare false positive but keeps this dependency-free.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ALLOW_MARKER = "standards: allow-non-english"

SPANISH_CHARS = re.compile(r"[áéíóúÁÉÍÓÚñÑ¿¡]")

# Function words with no English homograph, so a single-word match stays cheap
# and two of them is strong evidence.
SPANISH_WORDS = frozenset(
    """
    que para pero porque cuando donde según también así aunque
    del los las una unos unas este esta esto estos estas
    desde hasta sobre entre cada cual cuales quien
    debe puede tiene tienen hay son está están sea
    siempre nunca cualquier además entonces mientras
    archivo campo tabla consulta cambio usuario fecha
    devuelve retorna guarda elimina crea actualiza obtiene
    """.split()
)

WORD_RE = re.compile(r"[a-záéíóúñü]+", re.IGNORECASE)

LINE_COMMENT_PREFIXES = {
    ".py": ("#",),
    ".sh": ("#",),
    ".bash": ("#",),
    ".yaml": ("#",),
    ".yml": ("#",),
    ".sql": ("--",),
    ".js": ("//",),
    ".jsx": ("//",),
    ".ts": ("//",),
    ".tsx": ("//",),
    ".vue": ("//",),
    ".css": (),
    ".scss": (),
}

BLOCK_DELIMITERS = {
    ".js": ("/*", "*/"),
    ".jsx": ("/*", "*/"),
    ".ts": ("/*", "*/"),
    ".tsx": ("/*", "*/"),
    ".vue": ("/*", "*/"),
    ".css": ("/*", "*/"),
    ".scss": ("/*", "*/"),
}

TRIPLE_QUOTES = ('"""', "'''")


def extract_comments(path: Path) -> list[tuple[int, str]]:
    """Return (line number, comment text) for every comment in the file."""
    suffix = path.suffix
    prefixes = LINE_COMMENT_PREFIXES.get(suffix, ())
    block = BLOCK_DELIMITERS.get(suffix)
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (UnicodeDecodeError, OSError):
        return []

    comments: list[tuple[int, str]] = []
    in_block = False
    in_docstring: str | None = None

    for number, line in enumerate(lines, start=1):
        stripped = line.strip()

        if in_block and block:
            comments.append((number, stripped))
            if block[1] in stripped:
                in_block = False
            continue

        if in_docstring:
            comments.append((number, stripped))
            if in_docstring in stripped:
                in_docstring = None
            continue

        # Python docstrings and any triple-quoted block used as documentation.
        if suffix == ".py":
            opener = next((q for q in TRIPLE_QUOTES if q in stripped), None)
            if opener:
                comments.append((number, stripped))
                # Closed on the same line?
                if stripped.count(opener) < 2:
                    in_docstring = opener
                continue

        if block and block[0] in stripped:
            comments.append((number, stripped))
            if block[1] not in stripped.split(block[0], 1)[1]:
                in_block = True
            continue

        for prefix in prefixes:
            index = line.find(prefix)
            if index != -1:
                comments.append((number, line[index:].strip()))
                break

    return comments


def looks_spanish(text: str) -> bool:
    if ALLOW_MARKER in text:
        return False
    if SPANISH_CHARS.search(text):
        return True
    words = {word.lower() for word in WORD_RE.findall(text)}
    return len(words & SPANISH_WORDS) >= 2


def main() -> int:
    findings: list[str] = []
    for name in sys.argv[1:]:
        path = Path(name)
        if not path.is_file():
            continue
        for number, text in extract_comments(path):
            if looks_spanish(text):
                excerpt = text if len(text) <= 70 else text[:67] + "..."
                findings.append(f"{path}:{number}: {excerpt}")

    if findings:
        print("Comments and docstrings must be written in English:\n")
        for finding in findings:
            print(f"  {finding}")
        print(
            f"\nTranslate them, or append '{ALLOW_MARKER}' to a comment that "
            "must stay as it is."
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
