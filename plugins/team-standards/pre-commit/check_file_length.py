#!/usr/bin/env python3
"""Fail when a source file grows past the team's maximum length.

Part of the IMFD team standard. `pre-commit` passes only the files a commit
touches, so pre-existing long files never block unrelated work -- they surface
the next time someone edits them.

Usage:
    check_file_length.py [--warn N] [--max N] <file>...

Thresholds default to the team standard (300 warn / 400 max) and can be
overridden per repo with --warn/--max or the STANDARDS_WARN_LINES and
STANDARDS_MAX_LINES environment variables.

A long file is a signal that a module has taken on a second responsibility;
splitting it is the fix, not raising the limit.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

DEFAULT_WARN = int(os.environ.get("STANDARDS_WARN_LINES", "300"))
DEFAULT_MAX = int(os.environ.get("STANDARDS_MAX_LINES", "400"))


def count_lines(path: Path) -> int:
    with path.open("rb") as handle:
        return sum(1 for _ in handle)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--warn", type=int, default=DEFAULT_WARN)
    parser.add_argument("--max", dest="maximum", type=int, default=DEFAULT_MAX)
    parser.add_argument("files", nargs="*")
    args = parser.parse_args()

    # Lowering only the maximum is the common case, so clamp rather than
    # rejecting the combination: a warning above the hard limit is meaningless.
    warn = min(args.warn, args.maximum)
    if warn != args.warn:
        print(f"note: warning threshold clamped to the {warn}-line limit")

    failed = False
    for name in args.files:
        path = Path(name)
        if not path.is_file():
            continue
        lines = count_lines(path)
        if lines > args.maximum:
            print(f"{path}: {lines} lines, over the {args.maximum}-line limit")
            failed = True
        elif lines > warn:
            print(f"{path}: {lines} lines, past the {warn}-line warning")

    if failed:
        print(
            "\nSplit the file by responsibility. If the length is genuinely "
            "justified, raise the limit for the repo in .pre-commit-config.yaml "
            "with a comment explaining why."
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
