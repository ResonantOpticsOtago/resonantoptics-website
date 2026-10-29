---
# Profile page of Harald G. L. Schwefel. The data (name, role, bio, interests, education,
# links, photo) lives in data/authors/harald-g.-l.-schwefel.yaml - edit it there.
# This file only chooses the page layout and keeps the old address working.
title: Harald G. L. Schwefel
aliases:
  - /author/harald-g.-l.-schwefel/

# Layout: a landing page made of blocks (photo, bio, interests, education,
# then the person's publications and news). To use the Kit's plain profile
# page instead (photo, bio, links, then a card list of their content),
# delete `type: landing` and the whole `sections` list.
type: landing
sections:
  - block: resume-biography-3
    content:
      username: harald-g.-l.-schwefel
      headings:
        about: About
        interests: Interests
        education: Education
    design:
      name:
        size: compact           # compact | default
      avatar:
        shape: square         # circle | square (follows site setting by default)
  - block: content-collection
    content:
      title: Publications
      count: 0                  # 0 = all
      filters:
        folders:
          - publication
        author: harald-g.-l.-schwefel
    design:
      view: citation            # citation | card | date-title-summary
  - block: content-collection
    content:
      title: News
      count: 6                  # 0 = all
      filters:
        folders:
          - post
        author: harald-g.-l.-schwefel
    design:
      view: card                # card (with pictures) | date-title-summary
      columns: 2
      show_read_time: false
---
