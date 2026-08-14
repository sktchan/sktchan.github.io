# sktchan.github.io

Personal academic site — [sktchan.github.io](https://sktchan.github.io).

Jekyll 4, no theme, no JS framework. All content lives in `_data/*.yml`; the
pages are thin templates over it, so adding a paper or a talk means editing one
YAML entry, never HTML.

---

## Running it locally

Ruby came from Homebrew (macOS system Ruby 2.6 is too old). Add it to your PATH
once, in `~/.zshrc` or `~/.bash_profile`:

```sh
export PATH="/usr/local/opt/ruby/bin:$PATH"
```

Then:

```sh
bundle install                          # first time only
bundle exec jekyll serve --livereload   # → http://localhost:4000
```

Edits to `_data/`, pages and CSS reload in the browser automatically. Changes to
`_config.yml` do **not** — restart the server after touching that file.

## Deploying

Push to `main`. `.github/workflows/deploy.yml` builds the site and publishes it,
usually within a minute or two. Watch it under the repo's **Actions** tab.

> **One-time setup:** on github.com go to
> **Settings → Pages → Build and deployment → Source** and choose
> **GitHub Actions**. Until that's switched over, pushes build but don't go live.

Why not the plain GitHub Pages build? It runs the `github-pages` gem, pinned to
Jekyll 3.9 / Liquid 4.0.3, which calls `String#tainted?` — removed in Ruby 3.2.
It can't run on a current Ruby at all. Building with Actions uses this repo's own
`Gemfile`, so local and live are the same Jekyll.

---

## What to fill in

Everything below is currently a `TODO` placeholder. The site builds and looks
right as-is; it just says TODO in a lot of places.

**Start here — biggest impact first:**

- [ ] `_config.yml` — `tagline`, `description` (these are your Google result)
- [ ] `index.html` — the two bio paragraphs. Most visitors read only these.
- [ ] `_data/links.yml` — email, Scholar, ORCID, LinkedIn. Blank lines are
      skipped automatically, so delete what you don't want rather than faking it.
- [ ] `_data/links.yml` → `photo:` — a real headshot in `assets/img/`
      (square, ~600×600). Currently a pink placeholder.
- [ ] `_data/research.yml` — `statement`, the paper, the posters
- [ ] `_data/cv.yml` — education, experience, awards, skills
- [ ] `_data/teaching.yml` — courses, talks, mentoring, service
- [ ] `_data/news.yml` — three or four recent things, newest first
- [ ] `_data/projects.yml` — or delete its contents and drop `projects` from
      `nav:` in `_config.yml`
- [ ] `_data/photos.yml` — real photographs (see below)

Search the repo for `TODO` to find anything missed:

```sh
grep -rn "TODO" _data _config.yml index.html
```

### Adding photographs

```sh
mkdir -p photos-originals        # git-ignored — originals never hit GitHub
# drop your full-size files in there, then:
./scripts/resize-photos.sh
```

It writes web-sized copies (longest edge 1600px) into `assets/img/photos/` and
prints YAML to paste into `_data/photos.yml`. **Write real `alt` text** — it's
what a blind visitor and Google both read. Then delete the two
`placeholder-*.svg` entries.

### The CV

`/cv/` **is** the CV — there is no separate PDF to keep in sync. The print
stylesheet strips the nav, footer and colour, so the "print / save as pdf"
button on the page produces a clean black-on-white document.

Teaching, talks, service and publications are pulled into `/cv/` from
`teaching.yml` and `research.yml` automatically, so you never type them twice.

---

## Layout of the repo

```
_config.yml          site metadata + the nav list
_data/               ← all content
_layouts/            default (page shell) and page (adds the <h1>)
_includes/           head, nav, footer, entry (one reusable record)
*.html               one file per page, thin templates over _data/
assets/css/main.scss design tokens at the top, then base/components/print
assets/js/lightbox.js gallery viewer, ~90 lines, no dependencies
scripts/             photo resizing
```

### Changing the design

Every colour, radius, font and width is a custom property at the top of
`assets/css/main.scss`. The palette is a soft pink (`#ffebef`) used only as a
*surface* — never for text — with a darkened `--accent` (`#a8415c`) for anything
that has to be readable. That pair, plus `--ink-muted`, clears WCAG AA (4.5:1)
on the page background; if you darken the background or lighten the accent,
re-check the contrast.

Fonts are Fraunces (headings) and Inter (body), self-hosted in `assets/fonts/`
so the site makes no third-party requests. See `assets/fonts/LICENSE.md`.

### Adding or removing a tab

Edit `nav:` in `_config.yml` and add or delete the matching `*.html` file. The
`url` must match the page's `permalink` exactly, trailing slash included, or the
active-tab highlight won't light up.

---

## Gotchas

- **Empty strings are truthy in Liquid.** Guard optional values with
  `{% if x and x != '' %}`, not `{% if x %}` and not `{% if x != blank %}` —
  Liquid's `blank` keyword calls `String#blank?`, which only exists under
  ActiveSupport, so under Jekyll it matches nothing and filters nothing.
- `_config.yml` changes need a server restart.
- `Gemfile.lock` **is** committed — it pins gem versions so the Actions build
  resolves to the same Jekyll you ran locally. Re-commit it after `bundle update`.
