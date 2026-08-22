#!/usr/bin/env bash
# Guard: this plan touched ONLY new ex-*.svg files and example .md pages in its own
# batch — no pre-existing method-page diagram and no other example page's SVG changed.
# Usage: check-noregress.sh <slug1> <slug2> ...   (the batch's page slugs)
# Passes if: every changed docs/assets/diagrams/*.svg is one of ex-<slug>.svg (all NEW),
# and every changed docs/examples/*.md is one of <slug>.md.
set -euo pipefail
cd /home/simonm/projects/rust/pyfda
allowed_svg=""; allowed_md=""
for s in "$@"; do
  allowed_svg="${allowed_svg} docs/assets/diagrams/ex-${s}.svg"
  allowed_md="${allowed_md} docs/examples/${s}.md"
done
changed=$(git status --porcelain -- docs/assets/diagrams docs/examples | awk '{print $2}')
bad=0
for f in $changed; do
  case "$f" in
    docs/assets/diagrams/*.svg)
      echo "$allowed_svg" | grep -qw "$f" || { echo "UNEXPECTED SVG CHANGE: $f"; bad=1; } ;;
    docs/examples/*.md)
      echo "$allowed_md" | grep -qw "$f" || { echo "UNEXPECTED MD CHANGE: $f"; bad=1; } ;;
  esac
done
test "$bad" -eq 0
echo "OK no-regression: only batch files changed"
