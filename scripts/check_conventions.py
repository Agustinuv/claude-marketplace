#!/usr/bin/env python3
"""Convention checks for the IMFD Claude Code marketplace.

`claude plugin validate .` only checks manifest schema and syntax. This script
covers the conventions this repo documents but the CLI cannot see: registration
consistency, skill frontmatter, bundled-file references, portable paths, version
bumps, the injected-context budget, and hard-coded secrets.

Usage:
    python3 scripts/check_conventions.py [--base <git-ref>]

Exits 1 if any check fails. Pass --base to enable the version-bump check (CI
supplies the pull request base ref); without it, that single check is skipped.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

# Budget for the SessionStart-injected standard. This is a self-imposed limit,
# not a documented platform one: the file is re-injected into every session, so
# its size is a recurring token cost.
MAX_STANDARDS_BYTES = 10_000

# Below this, a skill description rarely carries enough trigger phrases for
# Claude to auto-invoke it reliably.
MIN_DESCRIPTION_CHARS = 60

KEBAB_CASE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

TEXT_SUFFIXES = {".md", ".json", ".sh", ".yaml", ".yml", ".py"}

SKILL_DIR_REF = re.compile(r"\$\{CLAUDE_SKILL_DIR\}/([A-Za-z0-9._/-]+)")
PLUGIN_ROOT_REF = re.compile(r"\$\{CLAUDE_PLUGIN_ROOT\}/([A-Za-z0-9._/-]+)")

# A plugin variable followed by a parent-directory escape. The lookahead keeps
# a documentation ellipsis ("${CLAUDE_SKILL_DIR}/...") from matching.
VARIABLE_ESCAPE = re.compile(
    r"\$\{CLAUDE_(?:SKILL_DIR|PLUGIN_ROOT|PLUGIN_DATA)\}/\.\.(?![.\w])"
)

# A quoted literal assigned to a secret-looking key. The negative lookahead
# skips variable references such as "${user_config.api_token}".
SECRET_ASSIGNMENT = re.compile(
    r"""(?ix)
    (token|secret|password|passwd|api[_-]?key|access[_-]?key)
    \s* [:=] \s*
    ["'] (?! \s* \$ )
    ([^"']{8,})
    ["']
    """
)

# This checker and its tests necessarily contain the detection patterns and a
# realistic-looking credential fixture, so they exempt themselves.
SELF_REFERENTIAL = {"check_conventions.py", "test_check_conventions.sh"}

PLACEHOLDER_HINTS = (
    "xxx",
    "your-",
    "your_",
    "changeme",
    "example",
    "placeholder",
    "redacted",
    "dummy",
    "fake",
    "<",
)


class Report:
    """Collects failures and warnings across all checks."""

    def __init__(self) -> None:
        self.failures: list[tuple[str, str]] = []
        self.warnings: list[tuple[str, str]] = []

    def fail(self, check: str, message: str) -> None:
        self.failures.append((check, message))

    def warn(self, check: str, message: str) -> None:
        self.warnings.append((check, message))


def git(root: Path, *args: str) -> subprocess.CompletedProcess:
    """Run a git command inside the repo, never raising on failure."""
    return subprocess.run(
        ["git", "-C", str(root), *args],
        capture_output=True,
        text=True,
        check=False,
    )


def parse_frontmatter(text: str) -> dict[str, str]:
    """Extract top-level scalar fields from a YAML frontmatter block."""
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    fields: dict[str, str] = {}
    for line in text[3:end].splitlines():
        if not line.strip() or line.startswith(("#", " ", "\t")):
            continue
        key, separator, value = line.partition(":")
        if separator:
            fields[key.strip()] = value.strip()
    return fields


def plugin_dirs(root: Path) -> list[Path]:
    plugins = root / "plugins"
    if not plugins.is_dir():
        return []
    return sorted(path for path in plugins.iterdir() if path.is_dir())


def text_files(base: Path) -> list[Path]:
    return sorted(
        path
        for path in base.rglob("*")
        if path.is_file() and path.suffix in TEXT_SUFFIXES
    )


def check_registration(root: Path, report: Report) -> None:
    """Every plugin folder is registered, and every entry resolves."""
    manifest_path = root / ".claude-plugin" / "marketplace.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    registered: dict[Path, str] = {}

    for entry in manifest.get("plugins", []):
        name = entry.get("name")
        source = entry.get("source")
        if not isinstance(source, str):
            # External git/npm sources are out of scope for this repo.
            report.warn("registration", f"{name}: non-path source, not checked")
            continue
        source_dir = (root / source).resolve()
        registered[source_dir] = name
        if not source_dir.is_dir():
            report.fail("registration", f"{name}: source '{source}' does not exist")
            continue
        plugin_json = source_dir / ".claude-plugin" / "plugin.json"
        if not plugin_json.is_file():
            report.fail("registration", f"{name}: missing .claude-plugin/plugin.json")
            continue
        declared = json.loads(plugin_json.read_text(encoding="utf-8")).get("name")
        if declared != name:
            report.fail(
                "registration",
                f"{name}: plugin.json declares name '{declared}'",
            )

    for plugin_dir in plugin_dirs(root):
        if plugin_dir.resolve() not in registered:
            report.fail(
                "registration",
                f"plugins/{plugin_dir.name}/ exists but is not registered "
                "in marketplace.json — consumers cannot see it",
            )
            continue
        components = ("skills", "agents", "commands", "hooks", ".mcp.json")
        if not any((plugin_dir / part).exists() for part in components):
            report.warn(
                "registration",
                f"plugins/{plugin_dir.name}/ declares no components",
            )

    known_names = set(registered.values())
    for old, new in (manifest.get("renames") or {}).items():
        if new is not None and new not in known_names:
            report.fail(
                "renames",
                f"'{old}' maps to '{new}', which is not a registered plugin",
            )


def check_skills_and_agents(root: Path, report: Report) -> None:
    """Skill and agent frontmatter carries the fields that drive invocation."""
    for plugin_dir in plugin_dirs(root):
        skills_dir = plugin_dir / "skills"
        if skills_dir.is_dir():
            for skill_md in sorted(skills_dir.rglob("SKILL.md")):
                _check_skill(root, skills_dir, skill_md, report)

        agents_dir = plugin_dir / "agents"
        if agents_dir.is_dir():
            for agent_md in sorted(agents_dir.glob("*.md")):
                fields = parse_frontmatter(agent_md.read_text(encoding="utf-8"))
                rel = agent_md.relative_to(root)
                for field in ("name", "description"):
                    if not fields.get(field):
                        report.fail("agents", f"{rel}: missing '{field}'")


def _check_skill(root: Path, skills_dir: Path, skill_md: Path, report: Report) -> None:
    rel = skill_md.relative_to(root)

    # Plugin skill discovery scans a single level: skills/<name>/SKILL.md.
    if len(skill_md.relative_to(skills_dir).parts) != 2:
        report.fail(
            "skills",
            f"{rel}: nested skill directories are not discovered inside a "
            "plugin — flatten to skills/<name>/SKILL.md and group by name prefix",
        )
        return

    fields = parse_frontmatter(skill_md.read_text(encoding="utf-8"))
    folder = skill_md.parent.name
    name = fields.get("name", "")
    description = fields.get("description", "")

    if not name:
        report.fail("skills", f"{rel}: missing 'name' in frontmatter")
    elif name != folder:
        report.fail("skills", f"{rel}: name '{name}' does not match folder '{folder}'")
    elif not KEBAB_CASE.match(name):
        report.fail("skills", f"{rel}: name '{name}' is not kebab-case")

    if not description:
        report.fail("skills", f"{rel}: missing 'description' in frontmatter")
    elif len(description) < MIN_DESCRIPTION_CHARS:
        report.warn(
            "skills",
            f"{rel}: description is only {len(description)} chars — "
            "auto-invocation depends on concrete trigger phrases",
        )


def check_bundled_references(root: Path, report: Report) -> None:
    """Every ${CLAUDE_SKILL_DIR}/${CLAUDE_PLUGIN_ROOT} target actually exists.

    This is the check that catches a moved or renamed bundled script, which
    otherwise fails silently at runtime.
    """
    for plugin_dir in plugin_dirs(root):
        targets = [
            *sorted((plugin_dir / "skills").rglob("SKILL.md")),
            *sorted((plugin_dir / "agents").glob("*.md")),
            plugin_dir / "hooks" / "hooks.json",
            plugin_dir / ".mcp.json",
        ]
        for path in targets:
            if not path.is_file():
                continue
            content = path.read_text(encoding="utf-8")
            rel = path.relative_to(root)
            is_skill = path.name == "SKILL.md"

            if is_skill:
                for ref in SKILL_DIR_REF.findall(content):
                    _check_ref(root, path.parent, ref, rel, "CLAUDE_SKILL_DIR", report)
            elif SKILL_DIR_REF.search(content):
                report.fail(
                    "references",
                    f"{rel}: ${{CLAUDE_SKILL_DIR}} only resolves inside a SKILL.md",
                )

            for ref in PLUGIN_ROOT_REF.findall(content):
                _check_ref(root, plugin_dir, ref, rel, "CLAUDE_PLUGIN_ROOT", report)


def _check_ref(
    root: Path, anchor: Path, ref: str, rel: Path, variable: str, report: Report
) -> None:
    # Skip documentation placeholders such as "${CLAUDE_SKILL_DIR}/..." or
    # paths containing a <token> stand-in.
    if ".." in ref or "<" in ref or ref.endswith("/"):
        return
    if not (anchor / ref).exists():
        report.fail("references", f"{rel}: ${{{variable}}}/{ref} does not exist")


def check_portable_paths(root: Path, report: Report) -> None:
    """No reference escapes its own plugin folder."""
    for plugin_dir in plugin_dirs(root):
        for path in text_files(plugin_dir):
            rel = path.relative_to(root)
            for number, line in enumerate(
                path.read_text(encoding="utf-8").splitlines(), start=1
            ):
                if VARIABLE_ESCAPE.search(line):
                    report.fail(
                        "portability",
                        f"{rel}:{number}: path escapes the plugin folder",
                    )
                    continue
                # In executable/config files a bare ../ is a real path; in
                # markdown it is usually prose about the rule itself.
                if path.suffix in {".sh", ".json"} and "../" in line:
                    if path.suffix == ".sh" and line.lstrip().startswith("#"):
                        continue
                    report.fail(
                        "portability",
                        f"{rel}:{number}: '../' is blocked after install",
                    )


def check_version_bumps(root: Path, base: str | None, report: Report) -> None:
    """A changed plugin without a version bump never reaches consumers."""
    if not base:
        report.warn("version", "skipped — pass --base <ref> to enable")
        return
    if git(root, "rev-parse", "--verify", base).returncode != 0:
        report.warn("version", f"skipped — base ref '{base}' not found")
        return

    for plugin_dir in plugin_dirs(root):
        rel_plugin = plugin_dir.relative_to(root).as_posix()
        changed = git(root, "diff", "--name-only", f"{base}...HEAD", "--", rel_plugin)
        if changed.returncode != 0 or not changed.stdout.strip():
            continue

        manifest_rel = f"{rel_plugin}/.claude-plugin/plugin.json"
        manifest_path = root / manifest_rel
        if not manifest_path.is_file():
            continue
        current = json.loads(manifest_path.read_text(encoding="utf-8")).get("version")
        if current is None:
            # Omitting version is a deliberate choice: each commit SHA counts
            # as a new version for actively developed plugins.
            continue

        previous_blob = git(root, "show", f"{base}:{manifest_rel}")
        if previous_blob.returncode != 0:
            continue  # New plugin on this branch.
        previous = json.loads(previous_blob.stdout).get("version")
        if previous == current:
            report.fail(
                "version",
                f"{rel_plugin} changed but version is still {current} — "
                "consumers will not receive the update",
            )


def check_standards_budget(root: Path, report: Report) -> None:
    """The always-injected standard stays within its token budget."""
    path = root / "plugins" / "team-standards" / "context" / "team-standards.md"
    if not path.is_file():
        report.warn("budget", "team-standards.md not found")
        return
    size = len(path.read_bytes())
    if size > MAX_STANDARDS_BYTES:
        report.fail(
            "budget",
            f"team-standards.md is {size} bytes, over the "
            f"{MAX_STANDARDS_BYTES}-byte budget — move detail into references/",
        )


def check_no_secrets(root: Path, report: Report) -> None:
    """No credential literals anywhere; secrets go through userConfig."""
    scanned = [*text_files(root / "plugins"), *text_files(root / "scripts")]
    for path in scanned:
        if path.name in SELF_REFERENTIAL:
            continue
        rel = path.relative_to(root)
        for number, line in enumerate(
            path.read_text(encoding="utf-8").splitlines(), start=1
        ):
            match = SECRET_ASSIGNMENT.search(line)
            if not match:
                continue
            value = match.group(2)
            if any(hint in value.lower() for hint in PLACEHOLDER_HINTS):
                continue
            if "${" in value:
                continue
            report.fail(
                "secrets",
                f"{rel}:{number}: possible hard-coded credential — "
                "use userConfig + ${user_config.KEY}",
            )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--base",
        help="git ref to compare against for the version-bump check",
    )
    parser.add_argument(
        "--root",
        default=".",
        help="marketplace root (defaults to the current directory)",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not (root / ".claude-plugin" / "marketplace.json").is_file():
        print(f"error: {root} is not a marketplace root", file=sys.stderr)
        return 2

    report = Report()
    check_registration(root, report)
    check_skills_and_agents(root, report)
    check_bundled_references(root, report)
    check_portable_paths(root, report)
    check_version_bumps(root, args.base, report)
    check_standards_budget(root, report)
    check_no_secrets(root, report)

    for check, message in report.warnings:
        print(f"WARN  [{check}] {message}")
    for check, message in report.failures:
        print(f"FAIL  [{check}] {message}")

    if report.failures:
        print(f"\n{len(report.failures)} convention check(s) failed.")
        return 1
    print(f"\nConventions OK ({len(report.warnings)} warning(s)).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
