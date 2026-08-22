#!/usr/bin/env bash
# Per-diagram gate for Phase 46 example concept SVGs.
# Usage: check-ex.sh <page-slug> <expected-viewbox-height>
# Verifies: SVG exists with 720-width viewBox at the given height, role=img,
# aria-label, the five canonical CSS classes; the page embeds the SVG via
# .fdars-diagram; svgo@3.3.4 idempotence (2nd pass byte-identical); rsvg PNG non-empty.
set -euo pipefail
cd /home/simonm/projects/rust/pyfda
slug="$1"; h="$2"
S="docs/assets/diagrams/ex-${slug}.svg"
P="docs/examples/${slug}.md"
test -f "$S"
grep -q "viewBox=\"0 0 720 ${h}\"" "$S"
grep -q 'role="img"' "$S"
grep -q 'aria-label=' "$S"
for c in ttl sub lab sm mono; do grep -q "\.${c}{" "$S"; done
grep -Fq "](../assets/diagrams/ex-${slug}.svg){ .fdars-diagram }" "$P"
FIRST=$(npx svgo@3.3.4 --config svgo.config.mjs --quiet --input "$S" --output -)
SECOND=$(printf '%s' "$FIRST" | npx svgo@3.3.4 --config svgo.config.mjs --quiet --input - --output -)
diff <(printf '%s' "$FIRST") <(printf '%s' "$SECOND")
rsvg-convert "$S" -o "/tmp/ex-${slug}.png"
test -s "/tmp/ex-${slug}.png"
echo "OK ex-${slug}.svg"
