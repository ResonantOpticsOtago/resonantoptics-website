---
title: ''
date: 2024-04-24
type: landing

# Home page: a list of blocks (sections). Block reference: https://hugoblox.com/blocks/
sections:
  - block: markdown
    content:
      title: About us
      subtitle: Resonant Optics
      text: |
        ![Illuminated whispering-gallery-mode resonator](Cavity_Illumination.jpg)

        Welcome to the **Resonant Optics** research group within the [Physics Department](https://www.otago.ac.nz/physics/) of the [University of Otago](https://www.otago.ac.nz/) and as part of the [Dodd-Walls Centre for Photonic and Quantum Technologies](https://www.doddwalls.ac.nz). Our team is lead by [Professor Harald Schwefel](/author/harald-g.-l.-schwefel/). Our research is centered around resonantly enhanced nonlinear interactions. Currently we investigate optical frequency combs, coherent microwave to optics conversion, and other fundamental aspects.

        High quality optical resonators can confine, store, and therefore intensify light on a very small foot-print. Of particular interest to us are resonators based on the Whispering Gallery Mode (WGM) concept. Our group is known to make some of the world's highest quality WGM resonators. We like to address some fundamental questions with analytical and numerical solutions associated with such optical resonators.

        One of the central interests currently is to use these resonators to enhance the optical field in order to stimulate strong nonlinear interactions. These interactions can lead to the generation of new colours of light (e.g. through second harmonic generation) or to the mixing of two different frequencies (e.g. sum-frequency generation). We use these effects to generate optical frequency combs and to coherently convert microwave and THz radiation into the optical domain. Such conversion will be necessary for connecting future superconducting quantum computers as well as novel airborne microwave detectors for mapping the cosmic microwave background and measuring temperature in the atmosphere. In other works we study third harmonic generation and selective coupling as well as some sensing. [Some of our Projects are described here](#projects)
    design:
      columns: '2'

  - block: content-collection
    id: news
    content:
      title: Latest News
      count: 5
      page_type: post
      filters:
        folders:
          - post
      order: desc
      archive:
        enable: true
        text: All news
    design:
      view: date-title-summary
      columns: '2'
      show_date: true
      show_read_time: false

  - block: content-collection
    id: projects
    content:
      title: Projects
      count: 6
      page_type: projects
      filters:
        folders:
          - projects
      order: desc
    design:
      view: card
      columns: '2'
      fill_image: true
      show_date: false
      show_read_time: false
      show_read_more: true

  - block: content-collection
    id: featured
    content:
      title: Featured Publications
      count: 5
      page_type: publication
      filters:
        folders:
          - publication
        featured_only: true   # publications with `featured: true` in their front matter
    design:
      view: article-grid
      columns: '2'
      show_read_time: false

  - block: content-collection
    id: publications
    content:
      title: Recent Publications
      count: 5
      page_type: publication
      filters:
        folders:
          - publication
      archive:
        enable: true
        text: All publications
    design:
      view: citation
      columns: '2'

  - block: cta-card
    content:
      title: Meet the team
      text: Principal investigators, researchers, students and visitors of the Resonant Optics group.
      button:
        text: People
        url: /people/
        icon: hero/user-group
    design:
      card:
        css_class: 'bg-primary-700'
        text_color: 'light'

  - block: logos
    content:
      title: Funding
      text: We thank all of our funding agencies
      items:
        - name: MBIE Endeavour Fund
          image: MBIE.png
          url: https://www.mbie.govt.nz/science-and-technology/science-and-innovation/funding-information-and-opportunities/investment-funds/endeavour-fund/
        - name: Marsden Fund, Royal Society Te Apārangi
          image: MarsdenRSNZ.png
          url: https://royalsociety.org.nz/what-we-do/funds-and-opportunities/marsden
        - name: Julius von Haast Fellowship
          image: JvH.png
          url: https://de.wikipedia.org/wiki/Julius_von_Haast_Fellowship_Award
        - name: Dodd-Walls Centre
          image: DWCnewBlack.png
          url: https://www.doddwalls.ac.nz/
        - name: Innosuisse
          image: InnoSuisse.png
          url: https://www.innosuisse.ch/inno/en/home.html
    design:
      display_mode: grid
---
