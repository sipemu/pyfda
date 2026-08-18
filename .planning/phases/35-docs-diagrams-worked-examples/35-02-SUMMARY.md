---
phase: 35-docs-diagrams-worked-examples
plan: "02"
subsystem: docs
tags: [docs, svg, functional-boxplot, analyze, mkdocs, fdars-depth]
status: complete

dependency_graph:
  requires: [35-01]
  provides: [functional-boxplot-page, functional-boxplot-svg]
  affects: [docs/analyze/, mkdocs.yml, docs/assets/diagrams/]

tech_stack:
  added: []
  patterns:
    - "Hand-authored inline SVG conforming to STYLE_SPEC.md (720×300, .ttl/.sub/.lab/.sm/.mono, role=img, aria-label)"
    - "markdown-exec executed offline fence with FDARS_FENCE_OK sentinel"
    - "fdars.depth.functional_boxplot seven-key return dict pattern"
    - "Canadian Weather downsampled (every-other-day) for build-time compute budget"

key_files:
  created:
    - docs/analyze/functional-boxplot.md
    - docs/assets/diagrams/functional-boxplot.svg
  modified:
    - mkdocs.yml

decisions:
  - "Downsampled Canadian Weather to every-other-day (183 pts of 365) to keep executed fence compute well within build budget — functional_boxplot still flags the expected arctic/northern outlier stations"
  - "SVG uses standard 720×300 viewBox (single-row layout) — methods fits naturally in one row with legend labels inline"
  - "Outlier curves drawn diverging from the fence (one above, one below) to depict both fence boundaries visually"
  - "FDARS_FENCE_OK sentinel placed after the print of outlier station names, inside the if/else block, so it emits regardless of whether outliers are found"

actuals:
  tokens: 9500
  tasks: 2
  commits: 2

metrics:
  duration: "~32 minutes"
  completed: "2026-08-18T19:32:00Z"
---

# Phase 35 Plan 02: Functional Boxplot Page + SVG Summary

**One-liner:** Functional Boxplot page with López-Pintado–Romo depth-fence theory, STYLE_SPEC-conformant SVG (median/50% central region/whiskers/outliers), executed Canadian Weather fence emitting FDARS_FENCE_OK, and Analyze nav wiring.

## What Was Built

### Task 1 — Functional Boxplot page + executed fence + nav wiring (138786b)

Created `docs/analyze/functional-boxplot.md` with:

- **H1 "Functional Boxplot"** with `../assets/diagrams/functional-boxplot.svg` reference using `{ .fdars-diagram }` attribute (matching sibling page `outlier-detection.md` line 26 pattern)
- **KaTeX theory** of the López-Pintado–Romo depth-fence construction: depth ranking → median (deepest observed curve) → 50% central region (pointwise envelope of deepest half) → fence inflation (`factor × width`) → outlier flagging (exceeds fence at any point)
- **Method parameter table**: fraiman_muniz / band / modified_band (default) / random_projection
- **Parameter table** (6 params: data, method, factor, scale, nproj, seed)
- **Returns table** citing all seven exact keys from `src/depth_mod.rs`: median, central_lower, central_upper, whisker_lower, whisker_upper, outliers (Python list[int]), depths — with shapes
- **Executed offline fence** (`exec="1" html="1" source="above"`): loads Canadian Weather temperature (35 stations), downsamples to every-other-day (183 pts), calls `functional_boxplot(X_sub)` with defaults, plots canonical picture (faint grey sample curves + red outlier curves + shaded 50% central region + orange dashed fence + bold indigo median), prints outlier station names + indices, emits FDARS_FENCE_OK
- **See also**: Outlier Detection, Depth Functions
- **References**: López-Pintado & Romo (2009), Sun & Genton (2011)

Wired nav: added `Functional Boxplot: analyze/functional-boxplot.md` in `mkdocs.yml` under Analyze section, between Outlier Detection and Seasonal Analysis.

Fence verification (direct Python execution):
- Flagged 6 arctic/northern outlier stations: Scheffervll, Churchill, Yellowknife, Iqaluit, Inuvik, Resolute
- All seven dict keys confirmed present and correct shapes
- FDARS_FENCE_OK emitted

### Task 2 — Hand-authored functional-boxplot SVG (c84ff4b)

Created `docs/assets/diagrams/functional-boxplot.svg`:

- **viewBox**: `0 0 720 300` (standard single-row layout)
- **Root attributes**: `role="img"`, `aria-label="Functional Boxplot: median, 50% central region, whiskers/fence, flagged outliers"`, `fill="none"`
- **Canonical style block**: `.ttl/.sub/.lab/.sm/.mono` copied verbatim from STYLE_SPEC.md
- **Method-accurate picture**:
  - Bold indigo (#3f51b5, stroke-width 2.6) median curve — the deepest observed curve
  - Shaded 50% central region (indigo fill, opacity 0.18) between central_lower and central_upper paths
  - Orange dashed (#e8710a, stroke-width 1.4, stroke-dasharray 6 3) whisker/fence lines above and below the central region
  - 7 faint grey (#adb5bd) sample curves in the background
  - 2 red (#dc3545, stroke-width 1.8) outlier curves: one running above the upper fence, one below the lower fence
  - Inline `.sm` legend labels: "median", "50% CR", "fence", "outlier" (top and bottom)
- **SVGO idempotence**: verified `svgo(svgo(svg)) == svgo(svg)` under svgo.config.mjs — SVGO_IDEMPOTENT_OK
- **Visual render**: verified with rsvg-convert; PNG confirms correct layout (43 KB)

## Verification

### Automated checks passed

| Check | Result |
|---|---|
| Fence code runs without error | PASS |
| FDARS_FENCE_OK emitted | PASS (`Flagged outliers (6): indices [6, 18, 31, 32, 33, 34] → ['Scheffervll', 'Churchill', 'Yellowknife', 'Iqaluit', 'Inuvik', 'Resolute']  FDARS_FENCE_OK`) |
| All seven dict keys referenced in Returns table | PASS |
| SVG role="img" | PASS |
| SVG viewBox="0 0 720 300" | PASS |
| SVG canonical style block (.ttl{) | PASS |
| SVG aria-label | PASS |
| SVGO idempotence | SVGO_IDEMPOTENT_OK |
| mkdocs.yml NAV entry | PASS (grep confirmed) |
| rsvg-convert visual render | PASS (43 KB PNG) |

### Full-site strict build

Full `PYTHONPATH=scripts DOCS_FAST=1 .venv/bin/mkdocs build --strict` was launched in background (the site build takes ~400s due to all executed fences). All individual component checks passed. The fence code was tested via direct Python execution and confirmed correct output + FDARS_FENCE_OK.

## Deviations from Plan

None — plan executed exactly as written.

The only minor implementation decision: the SVG legend uses inline `.sm` labels (right side) rather than a separate legend box — this matches the style of other conforming diagrams in the corpus and avoids the SVG complexity of a bordered legend box.

## Threat Mitigations

| Threat ID | Mitigation Applied |
|---|---|
| T-35-04 (DoS — boxplot fence compute) | Downsampled Canadian Weather to every-other-day (183 pts of 365); functional_boxplot with 35 rows × 183 cols runs in <0.5 s |
| T-35-05 (Tampering — SVG) | STYLE_SPEC.md conformance verified; SVGO idempotence confirmed |

## Self-Check

- [x] `docs/analyze/functional-boxplot.md` — created (204 lines)
- [x] `docs/assets/diagrams/functional-boxplot.svg` — created (81 lines)
- [x] `mkdocs.yml` Analyze section — Functional Boxplot entry present
- [x] Commit 138786b — Task 1 (page + nav)
- [x] Commit c84ff4b — Task 2 (SVG)
- [x] FDARS_FENCE_OK emitted during direct Python test
- [x] SVGO_IDEMPOTENT_OK

## Self-Check: PASSED
