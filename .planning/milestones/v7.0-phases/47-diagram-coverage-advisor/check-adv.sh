#!/usr/bin/env bash
# Per-diagram gate for Phase 47 advisor concept SVGs.
# Usage: check-adv.sh <page-slug> <expected-viewbox-height>
# Verifies: SVG exists with 720-width viewBox at the given height, role=img,
# aria-label, the five canonical CSS classes; the page embeds the SVG via
# .fdars-diagram; svgo@3.3.4 idempotence (2nd pass byte-identical); rsvg PNG non-empty.
set -euo pipefail
cd /home/simonm/projects/rust/pyfda
slug="$1"; h="$2"
S="docs/assets/diagrams/advisor-${slug}.svg"
P="docs/advisor/${slug}.md"
SCRATCHPAD="/tmp/claude-1000/-home-simonm-projects-rust-pyfda/81d3a2ad-9c69-4845-a299-2219a3a880f5/scratchpad/p47"
test -f "$S"
grep -q "viewBox=\"0 0 720 ${h}\"" "$S"
grep -q 'role="img"' "$S"
grep -q 'aria-label=' "$S"
for c in ttl sub lab sm mono; do grep -q "\.${c}{" "$S"; done
grep -Fq "](../assets/diagrams/advisor-${slug}.svg){ .fdars-diagram }" "$P"
FIRST=$(npx svgo@3.3.4 --config svgo.config.mjs --quiet --input "$S" --output -)
SECOND=$(printf '%s' "$FIRST" | npx svgo@3.3.4 --config svgo.config.mjs --quiet --input - --output -)
diff <(printf '%s' "$FIRST") <(printf '%s' "$SECOND")
mkdir -p "$SCRATCHPAD"
rsvg-convert "$S" -o "${SCRATCHPAD}/${slug}.png"
test -s "${SCRATCHPAD}/${slug}.png"
echo "OK advisor-${slug}.svg"
