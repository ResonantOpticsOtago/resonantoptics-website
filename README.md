# Resonant Optics group website

Source of <https://resonantoptics.physics.otago.ac.nz>, the website of the
Resonant Optics research group, Department of Physics, University of Otago.

- **Want to add a news item or edit your profile?** Read
  [docs/EDITING.md](docs/EDITING.md). You only need a browser.
- **Maintaining the machinery (builds, publishing, upgrades)?** Read
  [docs/MAINTAINERS.md](docs/MAINTAINERS.md).

How it works in one paragraph: the site is generated with
[Hugo](https://gohugo.io) and the Hugo Blox "Research Group" theme. Edits go
to the `draft` branch and show up on a Netlify preview; a maintainer merges
`draft` into the protected `main` branch by pull request and publishes to the
university web server with `scripts/publish.sh`. Every commit is built and
checked automatically by GitHub Actions. The Hugo version used everywhere is
pinned in `.hugo-version`.

Quick local build (optional; editors do not need this):

```
# Hugo extended, version as in .hugo-version, must be installed
hugo server          # http://localhost:1313, rebuilds on every save
python3 scripts/check_people.py   # validate people profiles (needs: pip install pyyaml)
```

Theme: [Hugo Blox Builder](https://hugoblox.com) (MIT licence, see LICENSE.md).
Content © Resonant Optics group, licensed CC BY-NC-ND 4.0 as stated in the
site footer.
