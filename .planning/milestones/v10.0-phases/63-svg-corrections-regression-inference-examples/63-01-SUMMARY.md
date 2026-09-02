---
phase: 63-svg-corrections-regression-inference-examples
plan: "01"
subsystem: docs
tags: [svg, a11y, accessibility, diagrams, mkdocs]

requires:
  - phase: 60-diagram-quality-audit
    provides: "Per-diagram defect register (60-AUDIT.md) with exact coordinates for 4 Major layout defects"

provides:
  - "4 Major layout defects fixed: concurrent-regression inter-panel overflow, precipitation geographic-drivers clip, depth-centrality ranked-centrality clip, seasonal badge truncation"
  - "4 Minor geometry defects fixed: functional-glm label collision, itp-interval-inference legend/bar overlap, ex-explainability-regions banner contrast, ex-tecator-regression caption overflow"
  - "A11Y-02 pattern applied to all 40 SVGs in regression/, inference/, examples/ buckets"
  - "A11Y-01 aria-label verbatim-match fixed on all 40 SVGs"

affects:
  - 64-svg-corrections-learn-align-analyze
  - docs-build-ci

actuals:
  tokens: 68000
  tasks: 5
  commits: 4

tech-stack:
  added: []
  patterns:
    - "CSS inline style override: use style='fill:white' not fill='white' attribute to override CSS class specificity in SVGs"
    - "SVG font-size inline override: use style='font:400 10px system-ui' to override CSS shorthand class font-size"
    - "A11Y-02 pattern: aria-labelledby='{slug}-title {slug}-desc' on root svg; <title> and <desc> immediately after <style> block"
    - "Layout fix for narrow inter-panel gaps: place overflow label below both panels, not inside gap"

key-files:
  created:
    - .planning/phases/63-svg-corrections-regression-inference-examples/63-01-SUMMARY.md
  modified:
    - docs/assets/diagrams/concurrent-regression.svg
    - docs/assets/diagrams/ex-canadian-precipitation.svg
    - docs/assets/diagrams/ex-canadian-depth-centrality.svg
    - docs/assets/diagrams/ex-canadian-seasonal.svg
    - docs/assets/diagrams/functional-glm.svg
    - docs/assets/diagrams/itp-interval-inference.svg
    - docs/assets/diagrams/ex-explainability-regions.svg
    - docs/assets/diagrams/ex-tecator-regression.svg
    - "docs/assets/diagrams/*.svg (32 additional — A11Y only)"

key-decisions:
  - "Arrow label for concurrent-regression placed below both panels (y=287/298) rather than inside 44px gap — gap is too narrow for any text"
  - "Precipitation/depth-centrality panels shifted left and font reduced to 10px via inline style (not attribute) to clear right-edge clip"
  - "Seasonal StableSeasonal badge height increased to 56px and mono text split over 2 lines — 37-char mono at 12px exceeds 246px panel"
  - "explainability-regions banner uses style='fill:white' — CSS .sm class overrides fill attribute; only inline style wins"
  - "itp-interval-inference legend moved below axis line (y=262) to clear bar chart overlap"
  - "functional-glm link-expression text changed to text-anchor=start x=516 to clear family-label text collision"

patterns-established:
  - "CSS specificity rule: for white-on-dark SVG text, style='fill:white' beats fill='white' attribute (CSS class wins over attr)"
  - "Font-size override: style='font:400 10px system-ui,sans-serif' overrides .sm{font:400 11px...} CSS shorthand"

requirements-completed: []

coverage:
  - id: D1
    description: "4 Major layout defects fixed (concurrent-regression, precipitation, depth-centrality, seasonal) — render-visible clipping eliminated"
    human_judgment: true
    rationale: "Visual layout correctness requires human review of the built/rendered SVGs — automated rsvg-convert render check confirms no crash but cannot assert layout quality"
  - id: D2
    description: "4 Minor geometry defects fixed (functional-glm collision, itp-interval-inference legend, explainability banner contrast, tecator caption overflow)"
    human_judgment: true
    rationale: "Visual geometry correctness requires human review"
  - id: D3
    description: "A11Y-02 pattern applied to all 40 SVGs — aria-labelledby, <title>, <desc> present on every diagram"
    verification:
      - kind: other
        ref: "grep -c 'aria-labelledby' docs/assets/diagrams/*.svg — confirmed 40/40"
        status: pass
    human_judgment: false
  - id: D4
    description: "A11Y-01 aria-label verbatim-match with .ttl title on all 40 SVGs"
    verification:
      - kind: other
        ref: "spot-checked all 40 SVGs — aria-label matches .ttl text content"
        status: pass
    human_judgment: false
  - id: D5
    description: "SVGO idempotence gate passes — all 40 SVGs unchanged by second svgo pass"
    verification:
      - kind: other
        ref: "svgo --quiet --output - <svg> | diff - <svg> — 0 diffs across all 40"
        status: pass
    human_judgment: false
  - id: D6
    description: "rsvg-convert render check — all 40 SVGs render without error"
    verification:
      - kind: other
        ref: "rsvg-convert -o /tmp/63-t-*.png docs/assets/diagrams/*.svg — exit 0 all 40"
        status: pass
    human_judgment: false
  - id: D7
    description: "Scope gate — exactly 40 docs/assets/diagrams/*.svg changed, no forbidden paths"
    verification:
      - kind: other
        ref: "git -C wt-63 diff --name-only 9580765~1..7cc239b — 40 files, all docs/assets/diagrams/*.svg"
        status: pass
    human_judgment: false

duration: 95min
completed: 2026-09-02
status: complete
---

# Phase 63 Plan 01: SVG Corrections — Regression/Inference/Examples Summary

**Fixed 4 Major layout defects + 4 Minor geometry issues + applied A11Y-02 accessibility pattern to all 40 concept diagrams in regression/, inference/, and examples/ documentation buckets**

## Performance

- **Duration:** ~95 min
- **Started:** 2026-09-02T00:00:00Z
- **Completed:** 2026-09-02
- **Tasks:** 5 (Task 5 was gate-only; 4 commits)
- **Files modified:** 40

## Accomplishments

- Fixed `concurrent-regression.svg` Major defect: inter-panel arrow label was clipping into both panels (44px gap too narrow for any font); label relocated below both panels at y=287/298
- Fixed `ex-canadian-precipitation.svg` Major defect: "Geographic drivers" result panel was clipping at right edge of 720px viewBox; panel shifted left (x=562, w=134) and text reduced to 10px via inline style override
- Fixed `ex-canadian-depth-centrality.svg` Major defect: "Ranked centrality" panel clipping at right edge; same technique (x=576, w=120, inline 10px font)
- Fixed `ex-canadian-seasonal.svg` Major defect: StableSeasonal badge conclusion text truncated in 46px tall badge; height increased to 56px and mono text split to 2 lines
- Fixed `functional-glm.svg` Minor: link-expression text collision with family label; changed to text-anchor=start x=516
- Fixed `itp-interval-inference.svg` Minor: legend rectangles overlapping bar chart at y=92/106; legend moved below axis at y=262 in two horizontal columns
- Fixed `ex-explainability-regions.svg` Minor: banner second-line text invisible (fill="white" overridden by CSS .sm class); changed to style="fill:white" inline
- Fixed `ex-tecator-regression.svg` Minor: single-line caption overflowing 720px viewBox; split to 2 lines at y=410/y=426
- Applied A11Y-02 pattern (aria-labelledby + `<title id>` + `<desc id>`) to all 40 SVGs across 4 tasks
- All 40 SVGs pass: SVGO idempotence, rsvg-convert render, scope verification, A11Y-01 verbatim label match

## Task Commits

Each task was committed atomically:

1. **Task 1: 4 Major layout defects + A11Y tracer** - `9580765` (fix)
2. **Task 2: regression/ bucket A11Y + functional-glm minor** - `04e873f` (fix)
3. **Task 3: inference/ bucket A11Y + itp-interval-inference legend** - `b4b0be0` (fix)
4. **Task 4: examples/ bucket A11Y + 2 minor geometry fixes** - `7cc239b` (fix)
5. **Task 5: Gate verification** - no commit (pass-only)

## Files Created/Modified

**Major defect fixes (Task 1):**
- `docs/assets/diagrams/concurrent-regression.svg` — arrow label relocated below panels + A11Y
- `docs/assets/diagrams/ex-canadian-precipitation.svg` — right-edge panel shifted + 10px font + A11Y
- `docs/assets/diagrams/ex-canadian-depth-centrality.svg` — right-edge panel shifted + 10px font + A11Y
- `docs/assets/diagrams/ex-canadian-seasonal.svg` — badge height +10px, 2-line mono split + A11Y

**Minor fix + A11Y (Tasks 2-4, 36 files):**
- `docs/assets/diagrams/functional-glm.svg` — link-expression text-anchor fix + A11Y
- `docs/assets/diagrams/itp-interval-inference.svg` — legend below axis + A11Y
- `docs/assets/diagrams/ex-explainability-regions.svg` — banner fill:white inline style + A11Y
- `docs/assets/diagrams/ex-tecator-regression.svg` — 2-line caption split + A11Y
- 32 remaining SVGs — A11Y-02 addition only

## Decisions Made

- Arrow label for `concurrent-regression` placed below both panels rather than inside 44px gap — gap is geometrically too narrow for any text size that remains legible
- Precipitation/depth-centrality result panels shifted left and font reduced to 10px via `style="font:400 10px system-ui,sans-serif"` (not `font-size="10"` attribute) — CSS shorthand in `.sm` class takes precedence over standalone attribute
- Seasonal badge height increased from 46px to 56px; `.mono` 12px monospace at 37 chars needs ~37×7.2=266px but panel is 246px, so text split across 2 lines
- `ex-explainability-regions` banner uses `style="fill:white"` — CSS `.sm { fill:#495057 }` class rule overrides `fill="white"` attribute (CSS specificity); only inline `style=` wins
- `itp-interval-inference` legend split into two horizontal groups at y=262 (below axis at y=240) rather than stacked to fit width

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] CSS specificity: fill="white" attribute invisible on dark background**
- **Found during:** Task 4 (ex-explainability-regions.svg)
- **Issue:** Banner second-line `.sm` text used `fill="white"` presentation attribute; CSS class `.sm { fill:#495057 }` has higher specificity and overrides it, making text near-invisible (dark gray on dark green)
- **Fix:** Changed to `style="fill:white"` inline style (highest CSS specificity)
- **Files modified:** `docs/assets/diagrams/ex-explainability-regions.svg`
- **Verification:** Visual inspection of svg text element; inline style confirmed dominant
- **Committed in:** `7cc239b` (Task 4 commit)

**2. [Rule 1 - Bug] SVG font-size attribute ignored when CSS shorthand class present**
- **Found during:** Task 1 (ex-canadian-precipitation.svg, ex-canadian-depth-centrality.svg)
- **Issue:** Adding `font-size="10"` attribute to `.sm` class elements did not reduce font size — CSS `.sm { font: 400 11px system-ui }` shorthand has higher specificity than standalone font-size attribute
- **Fix:** Used `style="font:400 10px system-ui,sans-serif"` inline style on affected text elements
- **Files modified:** `docs/assets/diagrams/ex-canadian-precipitation.svg`, `docs/assets/diagrams/ex-canadian-depth-centrality.svg`
- **Verification:** Logic confirmed: CSS shorthand beats standalone presentation attribute; inline style beats class
- **Committed in:** `9580765` (Task 1 commit)

**3. [Rule 1 - Bug] xmlns typo in uncertainty-quantification.svg**
- **Found during:** Task 3 (uncertainty-quantification.svg A11Y application)
- **Issue:** While adding A11Y attributes, accidentally wrote `http://www.w3.org/2020/svg` (2020) instead of `http://www.w3.org/2000/svg` (2000) in the xmlns attribute
- **Fix:** Corrected immediately with Edit tool before commit
- **Files modified:** `docs/assets/diagrams/uncertainty-quantification.svg`
- **Verification:** xmlns verified correct before commit; rsvg-convert render passed
- **Committed in:** `b4b0be0` (Task 3 commit)

---

**Total deviations:** 3 auto-fixed (all Rule 1 — bugs discovered during execution)
**Impact on plan:** All auto-fixes necessary for correctness. No scope creep. CSS specificity issues were not predictable from the plan's defect descriptions (which described visual symptoms only).

## Issues Encountered

- `rsvg-convert -o /dev/null` fails on this system with "Target file is not a regular file" — used `/tmp/63-t-$f.png` as output path for all render checks
- `for f in $FILES` (string variable in zsh) iterates as single token — required array syntax `FILES=(...)` with `"${FILES[@]}"` for per-file verification loops
- concurrent-regression label placement required two iterations: y=250/262 still inside panel area (panels extend to y=280); final position y=287/298 clears both panels

## Known Stubs

None — all 40 diagrams are complete; no placeholder text or hardcoded empty values detected.

## Next Phase Readiness

- Phase 63-01 complete; regression/inference/examples buckets are A11Y-clean and Major-defect-free
- Phase 63-02 (learn/ bucket) or Phase 64 (align/analyze buckets) can proceed
- The CSS specificity patterns documented above apply identically to any remaining SVGs with white-on-dark text using `.sm`/`.lab` classes — check with: `grep -n 'fill="white"' docs/assets/diagrams/*.svg`

## Self-Check

- All 40 SVGs present: confirmed via `git -C wt-63 diff --name-only` (40 files)
- 4 task commits present: 9580765, 04e873f, b4b0be0, 7cc239b — confirmed via `git log`
- SUMMARY.md written to correct path

## Self-Check: PASSED

---
*Phase: 63-svg-corrections-regression-inference-examples*
*Completed: 2026-09-02*
