#!/usr/bin/env bash
#
# Resize full-size photographs for the web gallery.
#
#   1. Drop originals into  photos-originals/   (git-ignored, stays off GitHub)
#   2. Run                  ./scripts/resize-photos.sh
#   3. Copy the YAML this prints into _data/photos.yml and write real alt text
#
# Writes TWO sizes. assets/img/photos/ holds the web-sized copy the lightbox
# opens; assets/img/photos/thumbs/ holds a 288px-tall version for the strip on
# the home page. Both are committed. The strip is only 144px tall, so serving
# it the large copies meant shipping megabytes to draw thumbnails.
#
# Uses `sips`, which ships with macOS — nothing to install.

set -euo pipefail

SRC="photos-originals"
OUT="assets/img/photos"
MAX_EDGE=1600      # longest side, in pixels
THUMB_EDGE=288     # thumbnail height for the home-page strip (2x its 144px render)
QUALITY=70         # sips JPEG quality: low | normal | high | best, or 0-100

cd "$(dirname "$0")/.."

if [[ ! -d "$SRC" ]]; then
  echo "No $SRC/ directory. Create it and put your full-size photos inside:"
  echo "  mkdir -p $SRC"
  exit 1
fi

mkdir -p "$OUT" "$OUT/thumbs"

shopt -s nullglob nocaseglob
originals=("$SRC"/*.{jpg,jpeg,png,heic,tif,tiff})
shopt -u nocaseglob

if [[ ${#originals[@]} -eq 0 ]]; then
  echo "No images found in $SRC/"
  exit 1
fi

echo "# Paste into _data/photos.yml under 'photos:' — then replace every TODO."
echo

for f in "${originals[@]}"; do
  base=$(basename "${f%.*}")
  # Lowercase, spaces and underscores to hyphens — keeps URLs clean.
  slug=$(echo "$base" | tr '[:upper:]' '[:lower:]' | tr ' _' '--' | tr -cd 'a-z0-9-')
  dest="$OUT/$slug.jpg"

  sips --setProperty format jpeg \
       --setProperty formatOptions "$QUALITY" \
       --resampleHeightWidthMax "$MAX_EDGE" \
       "$f" --out "$dest" >/dev/null 2>&1

  # The strip on the home page renders these 144px tall, so it gets its own
  # copy rather than downscaling the big one in the browser.
  sips --setProperty format jpeg \
       --setProperty formatOptions "$QUALITY" \
       --resampleHeight "$THUMB_EDGE" \
       "$dest" --out "$OUT/thumbs/$slug.jpg" >/dev/null 2>&1

  # Read back the real output dimensions so photos.yml can carry width/height,
  # which is what stops the gallery jumping around as images load. Taken from
  # the full-size copy; the thumbnail is a proportional resize of it, so the
  # ratio those attributes encode is the same for both.
  w=$(sips -g pixelWidth  "$dest" | awk '/pixelWidth/  {print $2}')
  h=$(sips -g pixelHeight "$dest" | awk '/pixelHeight/ {print $2}')

  printf -- '  - file: "%s.jpg"\n' "$slug"
  printf -- '    alt: "TODO: describe what is in this photograph"\n'
  printf -- '    width: %s\n' "$w"
  printf -- '    height: %s\n' "$h"
  echo
done

echo "# Wrote $(ls -1 "$OUT"/*.jpg 2>/dev/null | wc -l | tr -d ' ') photo(s) to $OUT/ and $OUT/thumbs/"
echo "# Delete the placeholder-*.svg entries once you have real photos."
