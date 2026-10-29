# Migration to HugoBlox Kit (Tailwind) — state of the `kit` branch

Phase 1 ("spike") result, 20 Oct 2026. The branch builds and is complete in
content; it is a proposal for you to judge on the Netlify preview. Nothing on
`draft` or `main` has changed.

## What is pinned

| What | Where | Value |
|---|---|---|
| Hugo (extended) | `.hugo-version`, `netlify.toml`, `hugoblox.yaml` | 0.164.0 |
| HugoBlox Kit module | `go.mod` / `go.sum` | `github.com/HugoBlox/kit/modules/blox` at the commit the Kit's own templates pin (2026-05-27) |
| Node.js | `.node-version`, `netlify.toml` | 22 |
| Tailwind CSS 4.1.12, @tailwindcss/typography 0.5.16, Pagefind 1.4.0, Preact 10.27.2 | `package.json` + `package-lock.json` | exact versions |

Building locally: Hugo + Node installed, then `npm ci`, `hugo server`.
Publishing: `scripts/publish.sh` now runs `npm ci` before Hugo and Pagefind
after it (search index). CI and Netlify do the same.

## Structure changes

- People: `data/authors/<identifier>.yaml` (Kit schema `hugoblox/author/v1`)
  + photo `assets/media/authors/<identifier>.jpg`. Same identifiers as before,
  so `authors:` lists in posts and publications are untouched. The long
  biography is the `bio:` field (Markdown; rendered on the profile page).
  Chengcai's Chinese name is `name.alternate`.
- `content/authors/<identifier>/_index.md` are now one-paragraph stubs: they
  set the page title and redirect the pre-2026 addresses (`/author/<id>/`,
  and the title-derived ones such as `/author/anna-petersen/`) to the Kit's
  `/authors/<id>/`. The Kit hard-codes `/authors/`, so the path change is
  unavoidable; every old profile URL redirects.
- Home, People, Contact and Tour pages are rewritten with Kit blocks
  (`markdown`, `content-collection`, `cta-card`, `logos`, `team-showcase`,
  `contact-info`, `map`, `hero`, `gallery`).
- Removed: the Decap CMS page (`content/admin`), the example event, the
  theme's demo images, the old SCSS file, eight unused old photos in author
  folders, the three duplicate placeholder avatars.
- `scripts/check_people.py` validates the YAML profiles; the sync script reads
  members from `data/authors/`. `docs/EDITING.md` and `docs/MAINTAINERS.md`
  still describe the old profile format: rewrite planned for Phase 2.

## URL parity (old build vs this build, 733 old URLs)

All content pages exist. Changed on purpose: `/admin/`, `/event/*` (removed);
profile pages (redirect); auto-generated pages of non-member co-authors moved
from `/author/<name>/` to `/authors/<name>/` without redirects (180 pages,
never linked from the site itself); tag/category pagination URLs.

## Site-level additions (not theme overrides)

The Kit allows a site to add its own blocks and views next to the theme's;
nothing of the theme is copied or shadowed. Added here (all in `layouts/`):

- `_partials/hbx/blocks/people/block.html` — compact people grid (small round
  photos, name, role, optional interests/links), grouped by `user_groups`.
  Options are documented in the file and in `content/people/index.md`.
- `_partials/hbx/blocks/publication-list/block.html` — full publication list
  with search box, filter buttons per publication type and a sort control;
  entries are rendered with the Kit's own citation view.
- `_partials/views/inline.html` — view for the `cite` shortcode: a short
  "Journal (Year)" link, as the previous site had.

They use five Kit helper partials (`functions/get_authors_data`,
`functions/get_author_profile`, `functions/resolve_publication`,
`functions/render_view`, `social_links`). If a Kit upgrade renames one, the
build fails with a clear template error — fix the name in our file.

Profile pages (`content/authors/<id>/_index.md`) are landing pages made of
Kit blocks: `resume-biography-3` (photo, bio, interests, education, links)
plus two `content-collection` blocks (the person's publications and news).
The data stays in `data/authors/<id>.yaml`.

Where a presentation has alternatives, the `.md` files carry them as comments
(`content/_index.md`, `content/people/index.md`, `content/post/_index.md`,
`content/publication/_index.md`, each profile page, and the projects using
`cite`).

## Gaps and findings — please read

1. **Look**: dark by default, green accent, "academic" typography (serif
   headings, Lora/Source Serif from Google Fonts — an external request the
   current site does not make; switchable to a system-font pack).
   Structure is the same; it is a different design system.
2. **Tour**: no full-screen slider in the Kit. Now a hero with the 2025 group
   photo and a lightbox gallery of the five project images.
3. **Kit bug with small images**: hero/gallery crash the build when an image
   is narrower than 480 px (no fallback in the theme's responsive-image
   helper). Two project images were 250 px: Nonlinear & Quantum Optics now
   uses `PhotoMontage.png`; the THz image was upscaled ×3 as a placeholder —
   please provide a real one (≥ 1200 px). Cards elsewhere tolerate small
   images; ~35 news posts have small `featured` images and rendered fine.
4. **Deprecation warnings** for every publication (`doi` → `hugoblox.ids.doi`,
   flat `publication` → structured). The Kit still reads the old fields. Phase
   2: the sync writes the new shape, warnings disappear.
5. **Documentation gaps in the Kit**: e.g. the `logos` block README says
   `logos:`, the current component wants `items:`. Expect more of this; the
   Kit is 0.x.
6. **Edit this page** links work (preview build only, as before).
7. **Math, search (Pagefind), RSS, sitemap, 404, citation view, `cite`
   shortcode, DOI/cite buttons, featured filter, reading time**: working.

## Phase 2 (after your go)

Rewrite both guides for the YAML profiles; make the sync write the Kit's
publication field shape; decide fonts/typography; replace the THz image;
PR `kit` → `draft`; Netlify's draft site becomes the Kit site; then draft →
main → publish.
