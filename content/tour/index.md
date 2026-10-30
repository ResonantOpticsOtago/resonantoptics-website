---
title: Tour
date: 2022-10-24
type: landing

# A visual tour through the group's projects.
sections:
  - block: hero
    content:
      eyebrow: Resonant Optics
      title: 👋 Welcome to the group
      text: Take a look at what we're working on…
      media:
        src: Group2025.jpg
        alt: The Resonant Optics group in 2025
      primary_action:
        text: Join us
        url: /contact/
        icon: hero/academic-cap
      secondary_action:
        text: Our projects
        url: /projects/
    design:
      alignment: center
      size: large
  - block: gallery
    content:
      title: Our projects
      items:
        - src: CubeSat.png
          title: Photonic Radiometers
          caption: Quantum-technology-inspired photonic radiometers for climate gas monitoring
          link: /projects/photonic-radiometers/
        - src: OpticalFrequencyCombs.png
          title: Optical Frequency Combs
          caption: Exploring electro-optic and Kerr-nonlinearity based optical frequency combs
          link: /projects/optical-frequency-combs/
        - src: Exceptional.png
          title: Non-Hermitian physics and magnons
          caption: Exceptional points in coupled magnon–photon systems
          link: /projects/magnon-polaritons/
        - src: PhotoMontage.png
          title: Nonlinear Quantum Optics
          caption: Resonantly enhanced nonlinear and quantum optics
          link: /projects/nonlinear-and-quantum-optics/
        - src: THzPhotonicMolecules.jpg
          title: THz resonators
          caption: Resonators for the terahertz domain
          link: /projects/thzdomain/
    design:
      layout: masonry
      columns: 3
      lightbox: true
      caption_position: overlay
  # Group photos (Group2023.jpg and Group2025.jpg are in assets/media/).
  # Alternatives: `layout: masonry | grid | carousel`, `columns: 1 | 2 | 3`,
  # `lightbox: true | false`, `caption_position: overlay | below`.
  - block: gallery
    content:
      title: Group photos
      items:
        - src: Group2025.jpg
          title: The group in 2025
          caption: Resonant Optics group, 2025
        - src: Group2023.jpg
          title: The group in 2023
          caption: Resonant Optics group, 2023
    design:
      layout: carousel
      columns: 2
      lightbox: true
      caption_position: below
---
