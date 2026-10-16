#!/usr/bin/env python3
"""Regenerate content/publication/ from the group's Zotero library.

Zotero is the source of truth for bibliographic data; this repository is the
source of truth for everything curated by hand around a publication: the
`featured` flag, a `featured.jpg` image, extra links, and any text written
below the front matter.  The script merges the two:

  1. download the library as BibTeX (Zotero Web API, no key needed if the group
     library is public) and store it, sorted by key, as publications.bib;
  2. run the `academic` converter into a temporary folder;
  3. for every entry, write content/publication/<key>/index.md with the fresh
     bibliographic fields plus the curated fields and body text taken from the
     existing file (if any), and refresh cite.bib;
  4. remove folders that are no longer in the library, but only if they contain
     nothing except the generated index.md and cite.bib; folders with extra
     files (images, PDFs) are kept and reported.

Usage (from the repository root):

    python3 scripts/sync_publications.py                  # fetch and sync
    python3 scripts/sync_publications.py --dry-run        # report only
    python3 scripts/sync_publications.py --bib export.bib # use a file exported
                                                          # from Zotero instead of the API

Environment: ZOTERO_API_KEY (optional; required if the group library is private).
Dependencies: academic==0.11.2, pyyaml.
Exit codes: 0 = ok, 1 = error, 2 = refused (library looks truncated, see --allow-shrink).
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("PyYAML is required: pip install pyyaml")

ROOT = Path(__file__).resolve().parent.parent
PUB_DIR = ROOT / "content" / "publication"
BIB_FILE = ROOT / "publications.bib"
API = "https://api.zotero.org"
GROUP_ID = "6718035"  # https://www.zotero.org/groups/6718035/

# Front-matter keys that are maintained by hand in this repository and must
# survive a regeneration. Everything else comes from Zotero.
CURATED_KEYS = [
    "featured", "image", "projects", "summary", "publication_short",
    "author_notes", "url_pdf", "url_code", "url_dataset", "url_poster",
    "url_project", "url_slides", "url_source", "url_video", "slides", "draft",
]
# Written by the converter at run time; dropping it keeps the output stable.
EPHEMERAL_KEYS = ["publishDate"]
# Files a folder may contain and still count as "generated only".
GENERATED_FILES = {"index.md", "cite.bib"}
# Canonical key order in the written front matter.
KEY_ORDER = [
    "title", "subtitle", "authors", "author_notes", "date", "publication_types",
    "publication", "publication_short", "doi", "abstract", "summary", "tags",
    "links", "url_pdf", "url_code", "url_dataset", "url_poster", "url_project",
    "url_slides", "url_source", "url_video", "slides", "featured", "image",
    "projects", "draft",
]


# --------------------------------------------------------------------------- #
# Zotero
# --------------------------------------------------------------------------- #
def fetch_bibtex(group: str, collection: str | None, api_key: str | None, page_size: int = 100) -> str:
    """Download the whole library (or one collection) as BibTeX."""
    path = f"groups/{group}/" + (f"collections/{collection}/items/top" if collection else "items/top")
    params = {
        "format": "bibtex",
        "limit": page_size,
        "itemType": "-attachment || note",
    }
    chunks: list[str] = []
    start = 0
    total: int | None = None
    while True:
        url = f"{API}/{path}?" + urllib.parse.urlencode({**params, "start": start}, quote_via=urllib.parse.quote)
        req = urllib.request.Request(
            url,
            headers={"Zotero-API-Version": "3", "User-Agent": "resonantoptics-website publication sync"},
        )
        if api_key:
            req.add_header("Zotero-API-Key", api_key)
        for attempt in range(6):
            try:
                with urllib.request.urlopen(req, timeout=90) as resp:
                    body = resp.read().decode("utf-8")
                    headers = resp.headers
                break
            except urllib.error.HTTPError as exc:
                if exc.code in (429, 500, 502, 503) and attempt < 5:
                    wait = int(exc.headers.get("Retry-After") or exc.headers.get("Backoff") or 10)
                    print(f"Zotero answered {exc.code}; waiting {wait}s", file=sys.stderr)
                    time.sleep(wait)
                    continue
                if exc.code in (401, 403):
                    sys.exit(
                        f"Zotero refused the request ({exc.code}). The group library is private: either make it "
                        "readable (Group Settings > Library Reading: Anyone) or set ZOTERO_API_KEY to a key with "
                        "read access to the group."
                    )
                if exc.code == 404:
                    sys.exit(
                        f"Zotero group {group} not found (404). Check the group id: it is the number in the group's "
                        "URL on zotero.org (https://www.zotero.org/groups/<id>/...). Pass --group <id> or set the "
                        "repository variable ZOTERO_GROUP_ID."
                    )
                raise
        if total is None:
            total = int(headers.get("Total-Results") or 0)
        if body.strip():
            chunks.append(body.strip())
        start += page_size
        if not body.strip() or (total and start >= total):
            break
    text = "\n\n".join(chunks) + "\n"
    print(f"fetched {total if total else 'unknown number of'} items from Zotero group {group}")
    return text


def split_entries(bibtex: str) -> list[tuple[str, str]]:
    """Return [(key, entry_text), ...] in file order."""
    entries = []
    for block in re.split(r"(?m)^(?=@)", bibtex):
        block = block.strip()
        if not block.startswith("@"):
            continue
        m = re.match(r"@(\w+)\s*\{\s*([^,\s]+)\s*,", block)
        if not m:
            continue
        kind = m.group(1).lower()
        if kind in ("comment", "preamble", "string"):
            continue
        # Drop local-file references; they are meaningless outside one computer.
        block = re.sub(r"(?m)^\s*file\s*=\s*\{.*\},?\n", "", block)
        entries.append((m.group(2), block))
    return entries


def normalise_bibtex(bibtex: str) -> str:
    """Sort entries by key and drop duplicate keys (first occurrence wins)."""
    seen: set[str] = set()
    unique = []
    for key, text in split_entries(bibtex):
        if key.lower() in seen:
            print(f"warning: duplicate citation key {key} - keeping the first", file=sys.stderr)
            continue
        seen.add(key.lower())
        unique.append((key, text))
    unique.sort(key=lambda e: e[0].lower())
    return "\n\n".join(text for _, text in unique) + "\n"


# --------------------------------------------------------------------------- #
# Markdown bundles
# --------------------------------------------------------------------------- #
def read_bundle(index: Path) -> tuple[dict, str]:
    text = index.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}, text
    parts = text.split("\n---", 2)
    fm = yaml.safe_load(parts[0][3:]) or {}
    body = parts[1] if len(parts) > 1 else ""
    return (fm if isinstance(fm, dict) else {}), body.lstrip("\n")


def write_bundle(index: Path, fm: dict, body: str) -> None:
    ordered = {k: fm[k] for k in KEY_ORDER if k in fm}
    ordered.update({k: fm[k] for k in sorted(fm) if k not in ordered})
    front = yaml.safe_dump(ordered, sort_keys=False, allow_unicode=True, width=100000)
    text = f"---\n{front}---\n"
    if body.strip():
        text += "\n" + body.rstrip("\n") + "\n"
    index.write_text(text, encoding="utf-8")


def merge(generated: dict, old: dict | None) -> dict:
    fm = {k: v for k, v in generated.items() if k not in EPHEMERAL_KEYS}
    # `featured` used to be expressed as an extra entry in publication_types.
    types = [t for t in (fm.get("publication_types") or []) if t != "featured"]
    fm["publication_types"] = types
    if old:
        for key in CURATED_KEYS:
            val = old.get(key)
            if val is None or val is False or val in ("", [], {}):
                continue
            if key == "image" and isinstance(val, dict) and not any(v for v in val.values()):
                continue
            fm[key] = val
        if "featured" in (old.get("publication_types") or []):
            fm["featured"] = True
    if fm.get("featured") is not True:
        fm.pop("featured", None)
    return fm


def run_converter(bib: Path, out: Path) -> None:
    exe = shutil.which("academic")
    cmd = [exe] if exe else [sys.executable, "-m", "academic.cli"]
    cmd += ["import", str(bib), str(out) + "/", "--compact"]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(res.stdout, res.stderr, file=sys.stderr)
        sys.exit("the academic converter failed")
    for line in (res.stdout + res.stderr).splitlines():
        if "ERROR" in line or "WARN" in line:
            print("converter:", line.strip())


# --------------------------------------------------------------------------- #
def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--group", default=os.environ.get("ZOTERO_GROUP_ID") or GROUP_ID,
                    help=f"Zotero group id (default: $ZOTERO_GROUP_ID or {GROUP_ID})")
    ap.add_argument("--collection", default=None, help="restrict to one Zotero collection key")
    ap.add_argument("--bib", type=Path, default=None, help="use this BibTeX file instead of the Zotero API")
    ap.add_argument("--dry-run", action="store_true", help="report what would change; write nothing")
    ap.add_argument("--allow-shrink", action="store_true",
                    help="proceed even if the library has far fewer entries than the site")
    ap.add_argument("--summary", type=Path, default=None, help="write a Markdown summary to this file")
    args = ap.parse_args()

    if not PUB_DIR.is_dir():
        sys.exit(f"{PUB_DIR} not found; run from the repository")

    raw = args.bib.read_text(encoding="utf-8") if args.bib else fetch_bibtex(
        args.group, args.collection, os.environ.get("ZOTERO_API_KEY") or None
    )
    bibtex = normalise_bibtex(raw)
    entries = split_entries(bibtex)
    if not entries:
        sys.exit("no BibTeX entries found; refusing to continue")

    existing = {p.name: p for p in PUB_DIR.iterdir() if p.is_dir()}
    if len(entries) < 0.8 * len(existing) and not args.allow_shrink:
        print(
            f"REFUSED: the library has {len(entries)} entries but the site has {len(existing)} publication folders. "
            "If that is really intended, run again with --allow-shrink.",
            file=sys.stderr,
        )
        return 2

    with tempfile.TemporaryDirectory() as tmp:
        tmp_bib = Path(tmp) / "publications.bib"
        tmp_bib.write_text(bibtex, encoding="utf-8")
        gen_dir = Path(tmp) / "out"
        gen_dir.mkdir()
        run_converter(tmp_bib, gen_dir)

        added, updated, unchanged, removed, kept = [], [], [], [], []
        generated = {p.name: p for p in gen_dir.iterdir() if p.is_dir()}

        for slug, gpath in sorted(generated.items()):
            gfm, _ = read_bundle(gpath / "index.md")
            target = PUB_DIR / slug
            old_fm, old_body = (read_bundle(target / "index.md") if (target / "index.md").exists() else (None, ""))
            fm = merge(gfm, old_fm)
            # Render to a string to compare before touching anything.
            probe = Path(tmp) / "probe.md"
            write_bundle(probe, fm, old_body)
            new_text = probe.read_text(encoding="utf-8")
            new_cite = (gpath / "cite.bib").read_text(encoding="utf-8")
            if not target.exists():
                added.append(slug)
            else:
                same_md = (target / "index.md").exists() and (target / "index.md").read_text(encoding="utf-8") == new_text
                same_bib = (target / "cite.bib").exists() and (target / "cite.bib").read_text(encoding="utf-8") == new_cite
                (unchanged if same_md and same_bib else updated).append(slug)
            if not args.dry_run:
                target.mkdir(exist_ok=True)
                (target / "index.md").write_text(new_text, encoding="utf-8")
                (target / "cite.bib").write_text(new_cite, encoding="utf-8")

        for slug, path in sorted(existing.items()):
            if slug in generated:
                continue
            extra = sorted(set(os.listdir(path)) - GENERATED_FILES)
            if extra:
                kept.append(f"{slug} (has {', '.join(extra)})")
            else:
                removed.append(slug)
                if not args.dry_run:
                    shutil.rmtree(path)

    if not args.dry_run:
        BIB_FILE.write_text(bibtex, encoding="utf-8")

    lines = [f"Publication sync from Zotero group {args.group}" + (" (dry run)" if args.dry_run else ""), ""]
    lines.append(f"- {len(entries)} entries in the library, {len(existing)} folders on the site before the sync")
    for label, items in (("Added", added), ("Updated", updated), ("Removed (no longer in Zotero)", removed)):
        if items:
            lines.append(f"- **{label}** ({len(items)}): " + ", ".join(f"`{s}`" for s in items))
    if kept:
        lines.append(f"- **Kept although not in Zotero** ({len(kept)}, they contain extra files - check whether the "
                     "citation key changed and move the files): " + ", ".join(f"`{s}`" for s in kept))
    lines.append(f"- Unchanged: {len(unchanged)}")
    summary = "\n".join(lines)
    print(summary)
    if args.summary:
        args.summary.write_text(summary + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
