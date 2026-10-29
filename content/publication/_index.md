---
title: Publications
type: landing

# Full publication list with search, type filters and sorting (custom block
# `publication-list`, defined in layouts/_partials/hbx/blocks/). To fall back
# to the Kit's plain list, delete `type: landing` and the `sections` block and
# use the two lines at the bottom instead.
sections:
  - block: publication-list
    content:
      title: Publications
      text: ''
      folders:
        - publication
    design:
      view: citation              # citation | card | date-title-summary
      show_search: true
      show_filters: true          # buttons per publication type
      show_sort: true             # newest / oldest / title

# Plain list alternative (remove `type: landing` and `sections` above):
# view: citation
# pagination: 20
---
