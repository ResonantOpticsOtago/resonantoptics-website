---
# Leave the homepage title empty to use the site title
title:
date: 2024-04-24
type: landing

sections:
  - block: markdown
    design:
      columns: '2'
      spacing:
        padding: 
          - 20px
          - '0'
          - 20px
          - '0'
    content:
      title: About us
      subtitle: Resonant Optics
      image:
        filename: Cavity_Illumination.jpg
      text: |
        <br>
        
        {{< figure library="1" src="Cavity_Illumination.jpg" title="" >}} Welcome to the **Resonant Optics** research group within the [Physics Department](https://www.otago.ac.nz/physics/) of the [University of Otago](https://www.otago.ac.nz/) and as part of the [Dodd-Walls Centre for Photonic and Quantum Technologies](https://www.doddwalls.ac.nz). Our team is lead by [Associate Professor Harald Schwefel](./author/harald-g.-l.-schwefel/). Our research is centered around resonantly enhanced nonlinear interactions. Currently we investigate optical frequency combs, coherent microwave to optics conversion, and other fundamental aspects. 
        ## Optical Resonators
        High quality optical resonators can confine, store, and therefore intensify light on a very small foot-print. Of particular interest to us are resonators based on the Whispering Gallery Mode (WGM) concept. Our group is known to make some of the world's highest quality WGM resonators. We like to address some fundamental questions with analytical and numerical solutions associated with such optical resonators. 

        ## Nonlinear Optics
        One of the central interests currently is to use these resonators to enhance the optical field in order to stimulate strong nonlinear interactions. These interactions can lead to the generation of new colours of light (e.g. through second harmonic generation) or to the mixing of two different frequencies (e.g. sum-frequency generation). We use these effects to generate optical frequency combs and to coherently convert microwave and THz radiation into the optical domain. Such conversion will be necessary for connecting future superconducting quantum computers as well as novel airborne microwave detectors for mapping the cosmic microwave background and measuring temperature in the atmosphere. In other works we study third harmonic generation and selective coupling as well as some sensing. [Some of our Projects are described here](#projects)

  
  - block: collection
    content:
      title: Latest News
      subtitle:
      text:
      count: 5
      filters:
        author: ''
        category: ''
        exclude_featured: false
        publication_type: ''
        tag: ''
      offset: 0
      order: desc
      page_type: post
    design:
      view: 2
      columns: '2'
  
  - block: collection
    content:
      title: Projects
      subtitle:
      text:
      count: 6
      filters:
        author: ''
        category: ''
        exclude_featured: false
        publication_type: ''
        tag: ''
      offset: 0
      order: desc
      page_type: projects
    design:
      view: 5
      columns: '2'
      flip_alt_rows: true
      spacing:
    # Customize the section spacing. Order is top, right, bottom, left.
        padding: ['20px', '0', '20px', '0']
      background:
        # Choose colors such as from https://html-color-codes.info
 #       gradient_start: '#4bb4e3'
 #       gradient_end: '#2b94c3'
        # The gradient angle from 0-360 degrees
        gradient_angle: 180
        # Text color (true=light, false=dark, or remove for the dynamic theme color).
        text_color_light: 

  # - block: markdown
  #   content:
  #     title:
  #     subtitle: ''
  #     text:
  #   design:
  #     columns: '1'
  #     background:
  #       image: 
  #         filename: #coders.jpg
  #         filters:
  #           brightness: 1
  #         parallax: false
  #         position: center
  #         size: cover
  #         text_color_light: true
  #     spacing:
  #       padding: ['20px', '0', '20px', '0']
  #     css_class: fullscreen

  - block: collection
    content:
      title: Featured Publications
      text: ""
      count: 5
      filters:
        folders:
          - publication
        featured: true
        publication_type: 'featured'
    design:
      view: 2
      columns: '2'

  - block: collection
    content:
      title: Recent Publications
      text: ""
      count: 5
      filters:
        folders:
          - publication
        publication_type: ''
    design:
      view: citation
      columns: '2'

  - block: markdown
    content:
      title:
      subtitle:
      text: |
        {{% cta cta_link="./people/" cta_text="Meet the team →" %}}
    design:
      columns: '1'

  - block: markdown
    content:
      title: Funding
      subtitle: 
      image:
        filename: MBIE.png
      text: |
        We thank all of our funding agencies
        [{{< figure library="1" src="MBIE.png" title="" >}}](https://www.mbie.govt.nz/science-and-technology/science-and-innovation/funding-information-and-opportunities/investment-funds/endeavour-fund/)
        [{{< figure library="1" src="MarsdenRSNZ.png" title="" >}}](https://royalsociety.org.nz/what-we-do/funds-and-opportunities/marsden)
        [{{< figure library="1" src="JvH.png" title="" >}}](https://de.wikipedia.org/wiki/Julius_von_Haast_Fellowship_Award)
        [{{< figure library="1" src="DWCnewBlack.png" title="" >}}](https://www.doddwalls.ac.nz/)
        [{{< figure library="1" src="InnoSuisse.png" title="" >}}](https://www.innosuisse.ch/inno/en/home.html)


    design:
      columns: '2'
---
