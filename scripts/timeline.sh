#!/usr/bin/env bash
#
# Compute bar geometry for the community timeline ribbon.
#
#   1. Write real dates into _data/community.yml as  start: "YYYY-MM"  and
#      end: "YYYY-MM"  (or  end: "present"  for anything still running).
#   2. Run                ./scripts/timeline.sh
#   3. Paste the printed  x:/w:  values over the ones already in the file, and
#      the printed  axis:  block over the existing one.
#
# WHY THIS EXISTS
# Liquid has no date arithmetic, so bar positions can't be worked out at render
# time — the same reason the old map's map_x/map_y were baked in. This script
# is the thing that bakes them.
#
# WHAT IT COMPUTES
# A piecewise-linear, scale-preserving axis. Stretches of time where nothing at
# all was running collapse to a fixed sliver (a visible break in the ribbon);
# every live stretch keeps one shared %-per-month rate, so a two-year role is
# the same width wherever it sits. Compression removes dead time without
# distorting live time.
#
# Re-run this whenever you add a role. "present" resolves to today, so every
# number shifts slightly on each run — that's expected, not a bug.
#
# Pure awk. Nothing to install.

set -euo pipefail

cd "$(dirname "$0")/.."

DATA="_data/community.yml"

# An uncovered stretch shorter than this stays linear — only real voids get a
# break mark, otherwise the ribbon fills up with meaningless notches.
GAP_MIN_MONTHS=6

# How much of the axis one collapsed stretch is allowed to keep, in percent.
DEAD_WIDTH=3

if [[ ! -f "$DATA" ]]; then
  echo "No $DATA found. Run this from anywhere inside the repo." >&2
  exit 1
fi

awk -v now="$(date +%Y-%m)" \
    -v gapmin="$GAP_MIN_MONTHS" \
    -v deadw="$DEAD_WIDTH" '
  # ── month index: months since year 0, so arithmetic is plain integers ────
  function midx(s,   y, m) {
    if (s == "present") s = now
    y = substr(s, 1, 4) + 0
    m = substr(s, 6, 2) + 0
    return y * 12 + (m - 1)
  }
  function ylabel(m) { return int(m / 12) }

  # Position of the START of month m on the axis, in percent.
  function pos(m,   i, live, runs) {
    live = 0; runs = 0
    for (i = lo; i < m; i++) if (!dead[i]) live++
    for (i = 1; i <= nrun; i++) if (run_end[i] < m) runs++
    return live * rate + runs * deadw
  }

  # ── parse ────────────────────────────────────────────────────────────────
  # Only leadership: and mentorship: carry dates. Everything else in the file
  # (intro, workshops and their links) is skipped by the group guard.
  /^[a-z_]+:/ {
    group = ($0 ~ /^leadership:/) ? "leadership" \
          : ($0 ~ /^mentorship:/) ? "mentorship" : ""
    next
  }
  group == "" { next }

  # Exactly two spaces then "- title:" opens a record. Note bodies are indented
  # six, so they can never be mistaken for a key.
  /^  - title: / {
    n++
    grp[n] = group
    title[n] = strip($0)
    next
  }
  /^    venue: / { venue[n] = strip($0); next }
  /^    start: / { start[n] = strip($0); next }
  /^    end: /   { endd[n]  = strip($0); next }

  function strip(line,   v) {
    v = line
    sub(/^[^:]*: */, "", v)
    gsub(/^"|"$/, "", v)
    return v
  }

  END {
    if (n == 0) {
      print "No dated entries found — add start:/end: to " ARGV[1] > "/dev/stderr"
      exit 1
    }

    # ── span, coverage, and the voids in between ──────────────────────────
    for (i = 1; i <= n; i++) {
      if (start[i] == "" || endd[i] == "") {
        printf "Missing start/end on: %s\n", title[i] > "/dev/stderr"
        exit 1
      }
      s[i] = midx(start[i])
      # An entry ending in month E occupies through the end of E, so its right
      # edge sits at the start of E+1. A one-month role is one month wide.
      e[i] = midx(endd[i]) + 1
      if (lo == 0 || s[i] < lo) lo = s[i]
      if (e[i] > hi) hi = e[i]
    }
    for (i = 1; i <= n; i++)
      for (m = s[i]; m < e[i]; m++) covered[m] = 1

    # Maximal uncovered runs at or over the threshold become dead stretches.
    for (m = lo; m < hi; m++) {
      if (covered[m]) { runlen = 0; continue }
      runlen++
      if (m == hi - 1 || covered[m + 1]) {
        if (runlen >= gapmin) {
          nrun++
          run_start[nrun] = m - runlen + 1
          run_end[nrun]   = m
          for (k = run_start[nrun]; k <= run_end[nrun]; k++) dead[k] = 1
          deadtotal += runlen
        }
        runlen = 0
      }
    }

    livetotal = (hi - lo) - deadtotal
    rate = (100 - nrun * deadw) / livetotal

    # ── the x/w values ────────────────────────────────────────────────────
    print "# ═══ paste over the x:/w: lines in _data/community.yml ═══"
    print ""
    last = ""
    for (i = 1; i <= n; i++) {
      if (grp[i] != last) { printf "%s:\n", grp[i]; last = grp[i] }
      x = pos(s[i])
      w = pos(e[i]) - x
      printf "  # %s — %s\n", title[i], venue[i]
      printf "    x: %.2f\n", x
      printf "    w: %.2f\n", w
    }

    # ── the axis block ────────────────────────────────────────────────────
    print ""
    print "# ═══ paste over the axis: block in _data/community.yml ═══"
    print ""
    print "axis:"
    printf "  ticks:\n"
    # A tick per January that falls in live time. Januaries inside a collapsed
    # stretch are deliberately skipped — the break mark stands in for them.
    for (y = ylabel(lo); y <= ylabel(hi); y++) {
      m = y * 12
      if (m < lo || m > hi) continue
      if (dead[m]) continue
      printf "    - { label: \"%d\", x: %.2f }\n", y, pos(m)
    }
    printf "  breaks:\n"
    if (nrun == 0) printf "    []\n"
    for (i = 1; i <= nrun; i++)
      printf "    - { x: %.2f, w: %.2f }   # %d months, %d-%02d to %d-%02d\n",
             pos(run_start[i]), deadw, run_end[i] - run_start[i] + 1,
             ylabel(run_start[i]), (run_start[i] % 12) + 1,
             ylabel(run_end[i]),   (run_end[i] % 12) + 1

    # ── a short report, so the numbers are checkable by eye ───────────────
    printf "\n# span %d-%02d to %d-%02d · %d months, %d live, %d collapsed into %d break(s)\n",
           ylabel(lo), (lo % 12) + 1, ylabel(hi - 1), ((hi - 1) % 12) + 1,
           hi - lo, livetotal, deadtotal, nrun
    printf "# one month = %.3f%% of the axis\n", rate
  }
' "$DATA"
