#!/usr/bin/env python3
"""Validate the people profiles in content/authors/.

One folder per person: content/authors/<slug>/_index.md (+ avatar.jpg/png).
This script checks the things that silently break the People page or a
profile page.  It is run by CI on every pull request and can be run locally:

    python3 scripts/check_people.py            # from the repository root

Exit status 1 = at least one error (fix before merging); warnings never fail.
A person may be in several groups (e.g. Alumni and Visitors); that is not flagged.
Messages use the GitHub Actions annotation format so they show up inline
on the "Files changed" tab of a pull request.

Only dependency: PyYAML (pip install pyyaml).
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("PyYAML is required: pip install pyyaml")

ROOT = Path(__file__).resolve().parent.parent
AUTHORS_DIR = ROOT / "content" / "authors"
PEOPLE_PAGE = ROOT / "content" / "people" / "index.md"
AVATAR_NAMES = ("avatar.jpg", "avatar.jpeg", "avatar.png", "avatar.webp")
LINK_RE = re.compile(r"^(https?://|mailto:|#)")

errors = 0
warnings = 0


def report(level: str, path: Path, msg: str) -> None:
    global errors, warnings
    if level == "error":
        errors += 1
    else:
        warnings += 1
    rel = path.relative_to(ROOT) if path.is_relative_to(ROOT) else path
    # ::error file=...::msg is understood by GitHub Actions; plain text elsewhere.
    if os.environ.get("GITHUB_ACTIONS"):
        print(f"::{level} file={rel}::{msg}")
    else:
        print(f"{level.upper():7} {rel}: {msg}")


def front_matter(path: Path) -> dict | None:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        report("error", path, "file does not start with a '---' YAML front matter block")
        return None
    parts = text.split("\n---", 2)
    if len(parts) < 2:
        report("error", path, "unterminated front matter (missing closing '---')")
        return None
    try:
        data = yaml.safe_load(parts[0][3:]) or {}
    except yaml.YAMLError as exc:
        report("error", path, f"front matter is not valid YAML: {exc}".replace("\n", " "))
        return None
    if not isinstance(data, dict):
        report("error", path, "front matter must be a mapping of key: value")
        return None
    return data


def allowed_groups() -> list[str]:
    """The groups shown on the People page, in display order."""
    data = front_matter(PEOPLE_PAGE) or {}
    for section in data.get("sections", []):
        if section.get("block") == "people":
            return list(section.get("content", {}).get("user_groups", []))
    report("warning", PEOPLE_PAGE, "no 'people' block found; group names cannot be validated")
    return []


def main() -> int:
    groups = allowed_groups()
    seen_titles: dict[str, Path] = {}

    folders = sorted(p for p in AUTHORS_DIR.iterdir() if p.is_dir())
    for folder in folders:
        index = folder / "_index.md"
        if not index.exists():
            report("error", folder, "missing _index.md")
            continue
        fm = front_matter(index)
        if fm is None:
            continue
        slug = folder.name

        # --- identity -------------------------------------------------------
        title = str(fm.get("title") or "").strip()
        if not title:
            report("error", index, "'title' (display name) is missing")
        elif title in seen_titles:
            report("warning", index, f"same display name as {seen_titles[title].relative_to(ROOT)}")
        else:
            seen_titles[title] = index

        authors = fm.get("authors")
        if not isinstance(authors, list) or not authors:
            report("error", index, "'authors' must be a list containing the folder name")
        elif str(authors[0]).strip() != slug:
            report(
                "error",
                index,
                f"'authors' first entry is '{authors[0]}' but the folder is '{slug}' "
                "(they must match, or posts and publications will not link to this profile)",
            )

        if not str(fm.get("last_name") or "").strip():
            report("error", index, "'last_name' is missing (the People page sorts by it)")
        if not str(fm.get("role") or "").strip():
            report("warning", index, "'role' is empty (shown under the name on the People page)")

        # --- groups ---------------------------------------------------------
        ug = fm.get("user_groups")
        if ug is None or ug == []:
            report("warning", index, "no 'user_groups' - this person is not shown on the People page")
        elif not isinstance(ug, list):
            report("error", index, "'user_groups' must be a list, e.g.\n  user_groups:\n    - PhD Students")
        else:
            for g in ug:
                if groups and g not in groups:
                    report(
                        "error",
                        index,
                        f"user_group '{g}' is not one of the groups on the People page: {', '.join(groups)}",
                    )
            if len(ug) != len(set(ug)):
                report("warning", index, "duplicate entries in 'user_groups'")

        # --- links ----------------------------------------------------------
        for i, s in enumerate(fm.get("social") or []):
            link = str((s or {}).get("link") or "")
            if not LINK_RE.match(link):
                report("error", index, f"social[{i}] link '{link}' must start with https://, http://, mailto: or #")
        for i, org in enumerate(fm.get("organizations") or []):
            url = str((org or {}).get("url") or "")
            if url and not LINK_RE.match(url):
                report("error", index, f"organizations[{i}] url '{url}' must start with https:// or http://")

        # --- avatar ---------------------------------------------------------
        if not any((folder / n).exists() for n in AVATAR_NAMES):
            report("warning", index, "no avatar.jpg/png in the folder - a placeholder silhouette will be shown")

    print(f"\nchecked {len(folders)} profiles: {errors} error(s), {warnings} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
