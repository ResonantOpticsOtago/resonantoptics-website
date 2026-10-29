---
title: People
date: 2024-04-24
type: landing

# Two ways to show the team. The active one is `people` (compact, like the old
# site: small round photos, name, role). To try the Kit's own block instead,
# comment the `people` block out and uncomment `team-showcase` below.
sections:
  - block: people
    content:
      title: Our Team
      text: ''
      user_groups:
        - Principal Investigators
        - Researchers
        - PhD Students
        - Visitors
        - Alumni
      sort_by: name_family        # or: weight | graduation_year
      sort_ascending: true
    design:
      columns: 5                  # people per row on a wide screen: 3 | 4 | 5 | 6
      avatar_size: 160            # photo diameter in px (e.g. 96 small, 128 medium, 160 large)
      show_role: true
      show_interests: false       # true shows the first `max_interests` under the role
      max_interests: 3
      show_social: true           # icons under the name (email, Scholar, ORCID …)

  # - block: team-showcase        # Kit's own block: large square photos + card with bio excerpt
  #   content:
  #     title: Our Team
  #     user_groups:
  #       - Principal Investigators
  #       - Researchers
  #       - PhD Students
  #       - Visitors
  #       - Alumni
  #     sort_by: name_family
  #   design:
  #     show_role: true
  #     show_organizations: false
  #     show_interests: true
  #     max_interests: 3
  #     show_social: true
  #     max_columns: 4            # 2 | 3 | 4 (the photo is as wide as the card)
---
