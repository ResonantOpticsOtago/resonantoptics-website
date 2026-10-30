---
# Profile page of Josh Christensen. The data (name, role, bio, interests, education,
# links, photo) lives in data/authors/josh-t.-christensen.yaml - edit it there.
# This file only chooses the page layout and keeps the old address working.
title: Josh Christensen
aliases:
  - /author/josh-t.-christensen/
  - /author/josh-christensen/

# Layout: a landing page made of blocks (photo, bio, interests, education,
# then the person's publications and news). To use the Kit's plain profile
# page instead (photo, bio, links, then a card list of their content),
# delete `type: landing` and the whole `sections` list.
type: landing
sections:
  # Photo, name, role, affiliation, biography and links (Kit block).
  - block: resume-biography
    content:
      username: josh-t.-christensen
    design:
      name:
        size: compact           # compact | default
  # Interests and education as simple lists (site block; see
  # layouts/_partials/hbx/blocks/author-details/). Alternative: the Kit's
  # `resume-biography-3` block shows both in a larger timeline style - replace
  # the two blocks above/below with:
  # - block: resume-biography-3
  #   content:
  #     username: josh-t.-christensen
  - block: author-details
    content:
      username: josh-t.-christensen
      headings:
        interests: Interests
        education: Education
      show_year: true
    design:
      columns: 2                # 2 (side by side) | 1
  - block: content-collection
    content:
      title: Publications
      count: 0                  # 0 = all
      filters:
        folders:
          - publication
        author: josh-t.-christensen
    design:
      view: citation            # citation | card | date-title-summary
  - block: content-collection
    content:
      title: News
      count: 6                  # 0 = all
      filters:
        folders:
          - post
        author: josh-t.-christensen
    design:
      view: card-grid           # card-grid (pictures, `columns` wide) | card (one wide column) | date-title-summary
      columns: 2
      show_read_time: false
---
