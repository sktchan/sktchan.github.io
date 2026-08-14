source "https://rubygems.org"

# Jekyll 4, not the `github-pages` gem.
#
# `github-pages` pins Jekyll 3.9 / Liquid 4.0.3, which calls String#tainted? —
# removed in Ruby 3.2 — so it cannot run on any current Ruby. Instead we build
# with Jekyll 4 and deploy via .github/workflows/deploy.yml, which is GitHub's
# own recommended path now. Local and live builds use this exact same Gemfile,
# so what you see at localhost:4000 is what ships.
gem "jekyll", "~> 4.4"

group :jekyll_plugins do
  gem "jekyll-seo-tag", "~> 2.8"   # <title>, meta description, Open Graph tags
  gem "jekyll-sitemap", "~> 1.4"   # /sitemap.xml for search engines
end

# Ruby 3.4+ dropped these from the standard library; Jekyll still needs them.
gem "csv"
gem "base64"
gem "bigdecimal"
gem "logger"
gem "webrick"
