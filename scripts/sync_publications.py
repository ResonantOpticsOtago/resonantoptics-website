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


def hugo_urlize(s: str) -> str:
    """Approximation of Hugo's urlize(), which turns an author name into its taxonomy slug."""
    import unicodedata
    s = unicodedata.normalize("NFC", s.strip().lower())
    s = re.sub(r"\s+", "-", s)
    s = "".join(c for c in s if c.isalnum() or c in ".-_/+~@#")
    return re.sub(r"-{2,}", "-", s).strip("-")


def load_profiles() -> list[tuple[str, str, list[str]]]:
    """Group members: (identifier, last name, given-name tokens).
    Read from data/authors/<id>.yaml (HugoBlox Kit); falls back to the older
    content/authors/<id>/_index.md layout. The identifier is what `authors:`
    lists contain; the display name comes from the profile, so file names are free."""
    out = []
    data_dir = ROOT / "data" / "authors"
    if data_dir.is_dir() and any(data_dir.glob("*.y*ml")):
        for f in sorted(list(data_dir.glob("*.yaml")) + list(data_dir.glob("*.yml"))):
            d = yaml.safe_load(f.read_text(encoding="utf-8")) or {}
            name = d.get("name") if isinstance(d.get("name"), dict) else {}
            display = " ".join(str(name.get("display") or "").split())
            last = str(name.get("family") or "").strip() or (display.split()[-1] if display else "")
            first = str(name.get("given") or "").strip()
            if not last:
                continue
            given = first.split() if first else (display[: len(display) - len(last)].split() if display.lower().endswith(last.lower()) else [])
            out.append((f.stem, last, given))
        return out
    authors_dir = ROOT / "content" / "authors"
    if not authors_dir.is_dir():
        return out
    for d in sorted(p for p in authors_dir.iterdir() if p.is_dir()):
        f = d / "_index.md"
        if not f.exists():
            continue
        fm, _ = read_bundle(f)
        title = " ".join(str(fm.get("title") or "").split())
        last = str(fm.get("last_name") or "").strip() or (title.split()[-1] if title else "")
        first = str(fm.get("first_name") or "").strip()
        if not last:
            continue
        given = first.split() if first else (title[: len(title) - len(last)].split() if title.lower().endswith(last.lower()) else [])
        out.append((d.name, last, given))
    return out


def _name_tok(t: str) -> str:
    return t.strip("().,").lower()


def _latin(t: str) -> bool:
    return bool(re.search(r"[A-Za-z\u00C0-\u024F]", t))


def _tok_compatible(author_tok: str, profile_tok: str) -> bool:
    a, p = _name_tok(author_tok), _name_tok(profile_tok)
    if not a or not p:
        return False
    if len(a) == 1:  # an initial
        return p.startswith(a)
    return a == p


def normalise_author(name: str, profiles: list[tuple[str, str, list[str]]]) -> str:
    """Replace a group member's name by the member's profile slug when exactly
    one member fits: same last name and a compatible first name (a full name
    must be equal, an initial must match); middle names/initials are ignored,
    as are tokens without Latin letters. The theme then links the author to the
    profile and displays the profile's title, whatever spelling Zotero had.
    Non-members are returned unchanged."""
    name = " ".join(name.split())
    if not name:
        return name
    matches = []
    for slug, last, given in profiles:
        if name.lower() == slug:
            return slug
        if not name.lower().endswith(" " + last.lower()):
            continue
        atoks = [t for t in name[: len(name) - len(last)].split() if _latin(t)]
        ptoks = [t for t in given if _latin(t)]
        if not atoks or not ptoks or not _tok_compatible(atoks[0], ptoks[0]):
            continue
        i, ok = 1, True
        for ptok in ptoks[1:]:  # further profile given names must appear in order
            while i < len(atoks) and not _tok_compatible(atoks[i], ptok):
                i += 1
            if i == len(atoks):
                ok = False
                break
            i += 1
        if ok:
            matches.append(slug)
    return matches[0] if len(matches) == 1 else name


def content_references(slug: str) -> list[Path]:
    """Content files that link to a publication folder (ref/relref shortcodes or plain links)."""
    hits = []
    pat = re.compile(r"publication/" + re.escape(slug) + r"(?![\w-])")
    for f in (ROOT / "content").rglob("*.md"):
        if f.parent == PUB_DIR / slug:
            continue
        try:
            if pat.search(f.read_text(encoding="utf-8")):
                hits.append(f)
        except UnicodeDecodeError:
            pass
    return hits


def rewrite_references(old: str, new: str, dry_run: bool) -> list[Path]:
    """Point links at a renamed publication folder to its new name."""
    pat = re.compile(r"publication/" + re.escape(old) + r"(?![\w-])")
    changed = []
    for f in content_references(old):
        text = f.read_text(encoding="utf-8")
        new_text = pat.sub("publication/" + new, text)
        if new_text != text:
            changed.append(f)
            if not dry_run:
                f.write_text(new_text, encoding="utf-8")
    return changed


def identity(fm: dict) -> tuple[str | None, str | None]:
    """(doi, normalised title) used to recognise the same paper under a new citation key."""
    doi = str(fm.get("doi") or "").strip().lower() or None
    title = re.sub(r"[^a-z0-9]+", " ", str(fm.get("title") or "").lower()).strip() or None
    return doi, title


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


MIN_ACADEMIC = (0, 10, 0)  # first release with the `academic import <bib> <out>` syntax


def check_converter_version() -> None:
    """Refuse to run with an old `academic` whose CLI silently ignores our arguments."""
    py = ".".join(str(n) for n in sys.version_info[:3])
    try:
        from importlib.metadata import version
        v = version("academic")
    except Exception:  # noqa: BLE001
        sys.exit(f"The 'academic' package is not installed for {sys.executable} (Python {py}). "
                 "academic >= 0.10 needs Python >= 3.11.5. With a recent Python run: "
                 "python3.12 -m pip install academic==0.11.2 pyyaml, then start this script with python3.12.")
    parts = tuple(int(x) for x in re.findall(r"\d+", v)[:3])
    if parts < MIN_ACADEMIC:
        sys.exit(f"academic {v} is too old (need >= 0.10.0): its command line is different and ignores our "
                 f"arguments without any error. Newer releases need Python >= 3.11.5; this is Python {py} "
                 f"at {sys.executable}. Install Python 3.12 and run: python3.12 -m pip install academic==0.11.2 pyyaml")
    print(f"using academic {v} from {sys.executable} (Python {py})")


def run_converter(bib: Path, out: Path) -> None:
    # Always the interpreter running this script, never whatever `academic` is
    # first on PATH: an old copy there silently does nothing (see check above).
    cmd = [sys.executable, "-m", "academic.cli", "import", str(bib), str(out) + "/", "--compact"]
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
    ap.add_argument("--save-bib", type=Path, default=None,
                    help="also write the fetched (normalised) BibTeX to this file, even in a dry run")
    args = ap.parse_args()
    check_converter_version()

    if not PUB_DIR.is_dir():
        sys.exit(f"{PUB_DIR} not found; run from the repository")

    raw = args.bib.read_text(encoding="utf-8") if args.bib else fetch_bibtex(
        args.group, args.collection, os.environ.get("ZOTERO_API_KEY") or None
    )
    bibtex = normalise_bibtex(raw)
    entries = split_entries(bibtex)
    if args.save_bib:
        args.save_bib.write_text(bibtex, encoding="utf-8")
        print(f"saved the fetched BibTeX to {args.save_bib}")
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

    mapped: dict[str, str] = {}
    with tempfile.TemporaryDirectory() as tmp:
        tmp_bib = Path(tmp) / "publications.bib"
        tmp_bib.write_text(bibtex, encoding="utf-8")
        gen_dir = Path(tmp) / "out"
        gen_dir.mkdir()
        run_converter(tmp_bib, gen_dir)

        added, updated, unchanged, removed, kept = [], [], [], [], []
        renamed: list[tuple[str, str, list[Path]]] = []
        duplicates: list[tuple[str, str]] = []
        generated = {p.name: p for p in gen_dir.iterdir() if p.is_dir()}
        # The converter must have produced a page for (nearly) every entry;
        # otherwise every existing folder would look "removed".  Never go on.
        if not generated:
            sys.exit(f"the converter produced no pages from {len(entries)} BibTeX entries; nothing was changed. "
                     "Run with --save-bib FILE and inspect the file, or send it to the maintainer.")
        if len(generated) < 0.8 * len(entries) and not args.allow_shrink:
            sys.exit(f"the converter produced only {len(generated)} pages from {len(entries)} entries; "
                     "nothing was changed. Check the BibTeX (--save-bib FILE) or use --allow-shrink.")

        # --- same paper, new citation key? (matched by DOI, else by title) ---
        gen_ids = {slug: identity(read_bundle(gp / "index.md")[0]) for slug, gp in generated.items()}
        seen_doi: dict[str, str] = {}
        for slug, (doi, _) in sorted(gen_ids.items()):
            if doi and doi in seen_doi:
                duplicates.append((seen_doi[doi], slug))
            elif doi:
                seen_doi[doi] = slug
        old_ids = {slug: identity(read_bundle(path / "index.md")[0])
                   for slug, path in existing.items() if (path / "index.md").exists()}
        for slug in sorted(generated):
            if slug in existing:
                continue
            doi, title = gen_ids[slug]
            taken = {n for _, n, _ in renamed}
            cands = [o for o, (od, ot) in old_ids.items()
                     if o not in generated and o not in taken
                     and ((doi and od == doi) or (not doi and title and ot == title))]
            if len(cands) == 1:
                old_slug = cands[0]
                refs = rewrite_references(old_slug, slug, args.dry_run)
                renamed.append((old_slug, slug, refs))
                if not args.dry_run:
                    shutil.move(str(existing[old_slug]), str(PUB_DIR / slug))
                existing[slug] = existing.pop(old_slug)
                old_ids.pop(old_slug, None)

        profiles = load_profiles()
        for slug, gpath in sorted(generated.items()):
            gfm, _ = read_bundle(gpath / "index.md")
            if gfm.get("authors"):
                fixed = []
                for a in gfm["authors"]:
                    n = normalise_author(str(a), profiles)
                    if n != " ".join(str(a).split()):
                        mapped[str(a)] = n
                    fixed.append(n)
                gfm["authors"] = fixed
            target = PUB_DIR / slug
            old_fm, old_body = (read_bundle(target / "index.md") if (target / "index.md").exists() else (None, ""))
            fm = merge(gfm, old_fm)
            # Render to a string to compare before touching anything.
            probe = Path(tmp) / "probe.md"
            write_bundle(probe, fm, old_body)
            new_text = probe.read_text(encoding="utf-8")
            new_cite = (gpath / "cite.bib").read_text(encoding="utf-8")
            renamed_to = {n for _, n, _ in renamed}
            if slug in renamed_to:
                pass  # reported under "Renamed"
            elif not target.exists():
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
            refs = content_references(slug)
            note = (" - still linked from " + ", ".join(str(r.relative_to(ROOT)) for r in refs)) if refs else ""
            if extra:
                kept.append(f"{slug} (has {', '.join(extra)}){note}")
            else:
                removed.append(slug + note)
                if not args.dry_run:
                    shutil.rmtree(path)

    if not args.dry_run:
        BIB_FILE.write_text(bibtex, encoding="utf-8")

    lines = [f"Publication sync from Zotero group {args.group}" + (" (dry run)" if args.dry_run else ""), ""]
    lines.append(f"- {len(entries)} entries in the library, {len(existing)} folders on the site before the sync")
    if renamed:
        lines.append(f"- **Renamed** (same paper, new citation key; folder contents moved along) ({len(renamed)}): "
                     + ", ".join(f"`{o}` → `{n}`" + (f" (links updated in {', '.join(str(r.relative_to(ROOT)) for r in refs)})" if refs else "")
                                 for o, n, refs in renamed))
    for label, items in (("Added", added), ("Updated", updated), ("Removed (no longer in Zotero)", removed)):
        if items:
            lines.append(f"- **{label}** ({len(items)}): " + ", ".join(f"`{s}`" for s in items))
    if duplicates:
        lines.append(f"- **Possible duplicates in Zotero** (same DOI) ({len(duplicates)}): "
                     + ", ".join(f"`{a}` and `{b}`" for a, b in duplicates))
    if kept:
        lines.append(f"- **Kept although not in Zotero** ({len(kept)}, they contain extra files - check whether the "
                     "citation key changed and move the files): " + ", ".join(f"`{s}`" for s in kept))
    lines.append(f"- Unchanged: {len(unchanged)}")
    if mapped:
        lines.append(f"- Member names replaced by their profile identifier ({len(mapped)}): "
                     + ", ".join(f"{a} → {b}" for a, b in sorted(mapped.items())))
    summary = "\n".join(lines)
    print(summary)
    if args.summary:
        args.summary.write_text(summary + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
