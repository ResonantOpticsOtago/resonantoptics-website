#!/usr/bin/env python3
"""Validate the people profiles in data/authors/.

One file per person: data/authors/<identifier>.yaml (HugoBlox Kit schema
`hugoblox/author/v1`) plus a square photo assets/media/authors/<identifier>.jpg
(or .png/.jpeg/.webp). The identifier is stable and is what `authors:` lists in
posts and publications contain; the display name is `name.display`.

Run locally from the repository root (needs PyYAML):

    python3 scripts/check_people.py

Exit status 1 = at least one error (fix before merging); warnings never fail.
Messages use the GitHub Actions annotation format so they appear inline on
the "Files changed" tab of a pull request.
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
AUTHORS_DIR = ROOT / "data" / "authors"
AVATAR_DIR = ROOT / "assets" / "media" / "authors"
PEOPLE_PAGE = ROOT / "content" / "people" / "index.md"
AVATAR_EXT = (".jpg", ".jpeg", ".png", ".webp")
LINK_RE = re.compile(r"^(https?://|mailto:|#)")
SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9.\-]*$")

errors = 0
warnings = 0


def report(level: str, path: Path, msg: str) -> None:
    global errors, warnings
    if level == "error":
        errors += 1
    else:
        warnings += 1
    rel = path.relative_to(ROOT) if path.is_relative_to(ROOT) else path
    if os.environ.get("GITHUB_ACTIONS"):
        print(f"::{level} file={rel}::{msg}")
    else:
        print(f"{level.upper():7} {rel}: {msg}")


def front_matter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}
    try:
        data = yaml.safe_load(text.split("\n---", 2)[0][3:]) or {}
    except yaml.YAMLError:
        return {}
    return data if isinstance(data, dict) else {}


def allowed_groups() -> list[str]:
    """The groups shown on the People page, in display order."""
    for section in front_matter(PEOPLE_PAGE).get("sections", []):
        if section.get("block") == "team-showcase":
            groups = []
            for g in section.get("content", {}).get("user_groups", []):
                groups.append(g["name"] if isinstance(g, dict) else str(g))
            return groups
    report("warning", PEOPLE_PAGE, "no 'team-showcase' block found; group names cannot be validated")
    return []


def main() -> int:
    groups = allowed_groups()
    seen_names: dict[str, Path] = {}
    files = sorted(AUTHORS_DIR.glob("*.yaml")) + sorted(AUTHORS_DIR.glob("*.yml"))
    if not files:
        report("error", AUTHORS_DIR, "no profiles found")
        return 1

    for f in files:
        slug = f.stem
        try:
            d = yaml.safe_load(f.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError as exc:
            report("error", f, f"not valid YAML: {exc}".replace("\n", " "))
            continue
        if not isinstance(d, dict):
            report("error", f, "file must be a mapping of key: value")
            continue

        # --- identity -------------------------------------------------------
        if not SLUG_RE.match(slug):
            report("error", f, "file name must be lower case letters, digits, dots and hyphens (it is the person's identifier)")
        if str(d.get("slug") or "").strip() not in ("", slug):
            report("error", f, f"'slug' is '{d.get('slug')}' but the file is '{slug}.yaml' (they must match)")
        name = d.get("name") if isinstance(d.get("name"), dict) else {}
        display = " ".join(str(name.get("display") or "").split())
        if not display:
            report("error", f, "'name.display' (the name as shown) is missing")
        elif display in seen_names:
            report("warning", f, f"same display name as {seen_names[display].relative_to(ROOT)}")
        else:
            seen_names[display] = f
        if not str(name.get("family") or "").strip():
            report("error", f, "'name.family' (last name) is missing: the People page sorts by it and publications are matched by it")
        if not str(name.get("given") or "").strip():
            report("warning", f, "'name.given' (first name) is missing: used to match this person's name on publications")
        if not str(d.get("role") or "").strip():
            report("warning", f, "'role' is empty (shown under the name on the People page)")

        # --- groups ---------------------------------------------------------
        ug = d.get("user_groups")
        if not ug:
            report("warning", f, "no 'user_groups': this person is not shown on the People page")
        elif not isinstance(ug, list):
            report("error", f, "'user_groups' must be a list, e.g.\n  user_groups:\n    - PhD Students")
        else:
            for g in ug:
                if groups and g not in groups:
                    report("error", f, f"user_group '{g}' is not one of the groups on the People page: {', '.join(groups)}")
            if len(ug) != len(set(ug)):
                report("warning", f, "duplicate entries in 'user_groups'")

        # --- links ----------------------------------------------------------
        for i, link in enumerate(d.get("links") or []):
            url = str((link or {}).get("url") or "")
            if not LINK_RE.match(url):
                report("error", f, f"links[{i}] url '{url}' must start with https://, http://, mailto: or #")
            if not str((link or {}).get("icon") or "").strip():
                report("warning", f, f"links[{i}] has no icon")
        for i, org in enumerate(d.get("affiliations") or []):
            url = str((org or {}).get("url") or "")
            if url and not LINK_RE.match(url):
                report("error", f, f"affiliations[{i}] url '{url}' must start with https:// or http://")

        # --- avatar ---------------------------------------------------------
        avatars = [AVATAR_DIR / f"{slug}{ext}" for ext in AVATAR_EXT if (AVATAR_DIR / f"{slug}{ext}").exists()]
        if not avatars:
            report("warning", f, f"no photo: add a square assets/media/authors/{slug}.jpg (a placeholder is shown)")
        elif len(avatars) > 1:
            report("warning", f, "more than one photo file for this identifier; keep one: " + ", ".join(a.name for a in avatars))

    for a in AVATAR_DIR.glob("*"):
        if a.suffix.lower() in AVATAR_EXT and not (AUTHORS_DIR / f"{a.stem}.yaml").exists():
            report("warning", a, "photo has no matching profile in data/authors/")

    print(f"\nchecked {len(files)} profiles: {errors} error(s), {warnings} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
