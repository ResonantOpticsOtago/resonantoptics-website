# Editing the Resonant Optics website

Everything on the site is a text file in the GitHub repository
<https://github.com/ResonantOpticsOtago/resonantoptics-website>. You edit the
files in your browser; you do not need git or Hugo installed.

**How a change goes live**

1. You edit on the `draft` branch (the default: the branch selector at the top
   left of the file list shows `draft`). Each commit is checked automatically
   (a green tick or red cross appears next to the commit on GitHub; red =
   something is broken, click *Details* to see what).
2. A few minutes later your change appears on the preview site,
   <https://draft-resonantoptics.netlify.app/>. Each news post there has an
   "Edit this page" link at the bottom that opens the right file on GitHub
   (the published site does not show these links).
3. Harald merges `draft` into `main` and publishes. Nothing is live until then,
   so you cannot break the public site.

Files you will edit: `content/post/…` (news) and `content/authors/…`
(profiles). Publications are not edited here at all (see below). Please leave
everything else alone, in particular `config/`, `go.mod`, `go.sum`,
`netlify.toml`, `publications.bib`, `.github/` and `scripts/`.

## Adding a news item

1. Open <https://github.com/ResonantOpticsOtago/resonantoptics-website/tree/draft/content/post>.
2. *Add file → Create new file*. In the file name box type
   `2026_10_short-title/index.md` — the slash creates a new folder. Use the
   year, month and a few words; no spaces, no special characters.
3. Paste the template below and fill it in, then *Commit changes…* →
   *Commit directly to the draft branch*.
4. Pictures: open the new folder, *Add file → Upload files*. A file named
   `featured.jpg` (or `.png`) becomes the thumbnail in the news list. Other
   images go in the same folder and are shown in the text with
   `{{< figure src="name.jpg" title="caption" >}}`.

```yaml
---
title: 'Short, informative title'
date: '2026-10-15'
summary: One or two sentences shown in the news list.
authors:
  - harald-g.-l.-schwefel      # identifiers = folder names in content/authors/
tags: []
image:
  preview_only: true          # true: featured.jpg is used only as thumbnail
---

Text of the news item in Markdown. Paragraphs are separated by blank lines.
**Bold**, *italic*, [a link](https://www.otago.ac.nz/physics/).

{{< figure src="featured.jpg" title="Optional caption" >}}
```

Rules that bite:

- A title containing a colon must be in quotes: `title: 'Result: it works'`.
- Indentation in the block between the `---` lines is significant; copy the
  template rather than retyping it. Two spaces, never tabs.
- Dates: `'2026-10-15'` is enough. A date in the future hides the item until
  that day.
- Image file names are case-sensitive (`Featured.JPG` is not `featured.jpg`).
- Keep images under about 1 MB; the site does not need print resolution.

## Editing your profile

Open `content/authors/<your-identifier>/_index.md` on the `draft` branch and
click the pencil icon. Fields:

| Field | Meaning |
|---|---|
| `title` | display name, exactly as it appears on your papers (it links your publications to you) |
| `first_name`, `last_name` | used for sorting the People page |
| `role` | one line under your name, e.g. `PhD Student` |
| `bio` | one sentence, shown under posts you author |
| `interests` | a short list |
| `education.courses` | degree, institution, year |
| `social` | links: `envelope` + `mailto:…`, `google-scholar`, `orcid`, `github`, `linkedin` … Links must start with `https://` or `mailto:` |
| `user_groups` | which section of the People page you appear in (see the list in `content/people/index.md`); when you leave, this becomes `- Alumni` |

Below the second `---` you can write a longer biography in Markdown.

Photo: upload a square JPEG named `avatar.jpg` into your folder (*Add file →
Upload files*); it replaces the old one. 400×400 pixels is plenty.

Do not rename your folder. Its name is your identifier; posts and the People
page use it.

## Adding a person

Create `content/authors/firstname-lastname/_index.md` (lower case, hyphens)
with this template, then upload `avatar.jpg` into the folder:

```yaml
---
title: Firstname Lastname
first_name: Firstname
last_name: Lastname
authors:
  - firstname-lastname        # must equal the folder name
role: PhD Student
organizations:
  - name: Department of Physics, University of Otago
    url: 'https://www.otago.ac.nz/physics/'
bio: ''
interests:
  - Resonant Optics
education:
  courses:
    - course: BSc(Hons) in Physics
      institution: University of Otago
      year: 2025
social:
  - icon: envelope
    icon_pack: fas
    link: 'mailto:firstname.lastname@otago.ac.nz'
user_groups:
  - PhD Students
---

A paragraph or two about yourself (optional).
```

## Publications

The publication list is generated from the group's Zotero library
(<https://www.zotero.org/groups/6718035/>). To add a paper, add it to the
Zotero group with complete metadata (authors as on the paper, journal, year,
DOI, abstract); it appears on the site after the next weekly sync, as a pull
request that Harald merges. Corrections to authors, title or journal are
also made in Zotero, never in the repository — the next sync would undo them.

Three things are done in the repository, in the paper's folder
`content/publication/<key>/` (the key looks like `lambert-coherent-2025`):

- put the paper in "Featured Publications" on the home page: add the line
  `featured: true` to the front matter of `index.md`;
- give it a thumbnail: upload `featured.jpg` (or `.png`) into the folder;
- say something about it: write Markdown below the closing `---` of `index.md`.

These survive future syncs. Your name links to your profile when it is
written exactly as in your profile's `title`.

## Checking your work

- GitHub: the commit gets a green tick within a minute or two. A red cross
  means the site did not build or a profile check failed — click *Details*,
  the message names the file and the problem.
- Preview: the Netlify site rebuilds `draft` automatically after each commit
  (two to five minutes).
- If you are stuck, do nothing drastic: the public site is unaffected until
  someone publishes. Tell Harald what you changed.

## Markdown in 30 seconds

```
## Heading
A paragraph. Another sentence in the same paragraph.

A new paragraph after a blank line. **bold**, *italic*, `code`.
- a bullet
- another bullet
[link text](https://example.org)
```

Maths works in text with `$E = \hbar \omega$`; display equations with `$$ … $$`.
