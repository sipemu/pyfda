---
phase: 29-docs-diagrams-worked-examples
plan: 02
subsystem: docs/analyze
tags: [docs, svg, functional-statistics, scoring-metrics, markdown-exec]
status: complete

requires:
  - Phase 29 Plan 01 (represent tracer toolchain proven)
  - fdars 0.17 bindings: fdars.fdata (functional_variance/std/covariance/depth_based_median/trim_mean) and fdars.scoring (functional_mae/mse/mape/msle/explained_variance) shipped

provides:
  - docs/analyze/functional-statistics.md (functional variance/std/covariance + depth-based median + trim_mean)
  - docs/analyze/scoring-metrics.md (5 functional scoring metrics)
  - docs/assets/diagrams/functional-statistics.svg (4-panel 720x480 concept diagram)
  - docs/assets/diagrams/scoring-metrics.svg (2-panel 720x300 concept diagram)

affects:
  - docs/analyze/ (2 new pages)
  - docs/assets/diagrams/ (2 new SVGs)

tech-stack:
  added: []
  patterns:
    - hand-authored inline SVG conforming to STYLE_SPEC.md (720x480 for stats, 720x300 for metrics)
    - markdown-exec executed fence with FDARS_FENCE_OK sentinel
    - SVGO idempotence gate (npx svgo@3.3.4 --config svgo.config.mjs)
    - fdars.fdata.* data-only signatures (no argvals parameter for stats)
    - fdars.scoring.* uniform signature (y_true, y_pred, argvals)

key-files:
  created:
    - docs/analyze/functional-statistics.md
    - docs/analyze/scoring-metrics.md
    - docs/assets/diagrams/functional-statistics.svg
    - docs/assets/diagrams/scoring-metrics.svg
  modified: []

decisions:
  - "Used canadian_weather (35x365) for functional-statistics fence — shows structurally meaningful variance (winter high, summer low), positive method-accuracy signal for depth_based_median in-sample assertion"
  - "Used Tecator NIR spectra (240x100, all values positive) for scoring-metrics fence — safe for all 5 metrics including MAPE/MSLE; mean baseline predictor used deterministically"
  - "Executed only MAE/MSE/explained_variance in fence; MAPE and MSLE documented in prose with domain restriction warnings — avoids triggering raises on data that crosses zero"
  - "functional-statistics SVG uses 720x480 two-row layout (4 panels): mean+std band | depth score bars | median vs mean distinction | trim_mean strip — more informative than a single-row"
  - "scoring-metrics SVG uses 720x300 two-panel layout: pred+true curves with shaded residual | domain-integrated scalar scores panel — matches FEATURES.md diagram concept"
  - "depth_based_median Python binding returns the actual curve (not an index) — documented in prose as 'deepest observed curve'; in-sample assertion verifies this"
  - "functional_variance/std/covariance signatures are data-only (no argvals) — confirmed via API inspection and used correctly in fence"

metrics:
  duration: "~130 minutes (including two full mkdocs build --strict runs)"
  completed: "2026-08-17"
  tasks_completed: 2
  tasks_total: 2
  commits: 2

actuals:
  tokens: 18000
  tasks: 2
  commits: 2
---

# Phase 29 Plan 02: Analyze Docs — Functional Statistics + Scoring Metrics Summary

**One-liner:** Two new analyze section pages (functional summary statistics and scoring metrics) each with a STYLE_SPEC-conforming hand-authored SVG and an executed offline FDARS_FENCE_OK worked example against the real shipped fdars.fdata and fdars.scoring bindings.

## What Was Built

### Task 1: functional-statistics.md + functional-statistics.svg

**Page:** `docs/analyze/functional-statistics.md`

Covers `functional_variance`, `functional_std`, `functional_covariance`, `depth_based_median`, and `trim_mean`. Key sections:
- Bessel-corrected pointwise variance and std (functions of t, not scalars); requirement n≥2
- m×m covariance surface (diagonal = variance; O(n·m²) performance warning)
- Depth-based median: the deepest **observed** curve, explicitly contrasted with `geometric_median` (synthetic) and `mean_1d` (averaged) — the critical method-accuracy distinction
- Depth-trimmed mean: alpha=0 equals plain mean, alpha=0.2 excludes 20% peripheral curves
- Worked example against canadian_weather: asserts std²=var, cov_diagonal=var, depth-median is in-sample, trim_mean(alpha=0)=mean; emits FDARS_FENCE_OK

**SVG:** `docs/assets/diagrams/functional-statistics.svg` — 4-panel 720×480 layout:
1. Overlaid curves with bold mean and shaded ±1 std band (visibly wider on left, narrower on right)
2. Depth score bar chart — deepest bar highlighted red ("obs 3 ★"), lower bars grey
3. Three-curve panel showing mean (blue dashed) vs depth-median (red solid, one of the observed curves) vs geometric_median (green dotted, new curve) — the depth-median trap explicitly visualised
4. trim_mean strip — excluded peripheral curves faded, trim_mean (orange bold) vs naive mean (grey dashed)

### Task 2: scoring-metrics.md + scoring-metrics.svg

**Page:** `docs/analyze/scoring-metrics.md`

Covers `functional_mae`, `functional_mse`, `functional_mape`, `functional_msle`, and `functional_explained_variance`. Key sections:
- Why functional metrics: domain-integrated (Simpson) vs column-wise average — genuine functional extension
- Exact formulas for all five metrics
- **MAPE domain restriction:** raises ValueError when any |y_true| < ε (no epsilon fallback) — use MAE/MSE for zero-crossing data
- **MSLE domain restriction:** raises ValueError when any value ≤ −1
- Uniform signature: `(y_true, y_pred, argvals)` → scalar
- Worked example against Tecator NIR spectra: MAE/MSE/explained_variance against mean baseline; emits FDARS_FENCE_OK

**SVG:** `docs/assets/diagrams/scoring-metrics.svg` — 2-panel 720×300 layout:
1. Predicted vs true curves with shaded red region between them (the integrated absolute error), annotated |ε(t)| bracket, Simpson annotation
2. Domain-integrated scores panel (orange accent): five metric rows with formulas; MAPE and MSLE grayed out with ⚠ domain restriction warnings

## Verification Results

| Check | Result |
|-------|--------|
| `mkdocs build --strict` (first, b3lki9lp9) | exit 0 (1082s) |
| `mkdocs build --strict` (second, bogfdiwzt) | exit 0 |
| functional-statistics page FDARS_FENCE_OK | PASS (confirmed via grep on site/) |
| scoring-metrics page FDARS_FENCE_OK | PASS (confirmed via grep on site/) |
| functional-statistics.svg SVGO idempotence | PASS |
| scoring-metrics.svg SVGO idempotence | PASS |
| functional-statistics.svg role="img" count | 1 |
| functional-statistics.svg viewBox="0 0 720 480" count | 1 |
| scoring-metrics.svg role="img" count | 1 |
| scoring-metrics.svg viewBox="0 0 720 300" count | 1 |
| functional-statistics.md references SVG | 1 occurrence |
| scoring-metrics.md references SVG | 1 occurrence |
| MAPE in scoring-metrics.md | 4 occurrences |
| MSLE in scoring-metrics.md | 3 occurrences |
| depth_based_median drawn as observed curve | Yes (method-accuracy confirmed) |
| Fence code direct run (both) | PASS (functional-statistics FDARS_FENCE_OK, scoring-metrics FDARS_FENCE_OK) |

## Commits

| Task | Commit | Description |
|------|--------|-------------|
| 1 | `6b596f1` | feat(29-02): Task 1 — functional-statistics.md + functional-statistics.svg |
| 2 | `d064dcf` | feat(29-02): Task 2 — scoring-metrics.md + scoring-metrics.svg |

## Deviations from Plan

### Auto-fixed: API signature discovery

**Found during:** Task 1 setup

**Issue:** FEATURES.md described `depth_based_median` as returning a usize index. The Python binding actually returns the 1-D curve array directly (the binding resolves the index internally). The docstring confirms: "The upstream usize index is resolved to the actual curve row — a bare integer is never returned."

**Fix:** Updated fence code to treat the return value as a 1-D array and validate it is in the sample via `any(np.allclose(median_curve, X[i]) for i in range(len(X)))`. Page prose updated to accurately describe the Python binding behavior.

**Rule:** Rule 1 (auto-fix bug) — the FEATURES.md description was accurate for the Rust core but the Python binding wraps the index; prose and fence corrected accordingly.

### Note: scoring-metrics page timing

The first build (b3lki9lp9) started before scoring-metrics.md was written (the file was created at 07:34 while the build started at 07:28). Both pages were confirmed in the second build (bogfdiwzt, exit 0).

## Known Stubs

None. Both pages are fully wired to real shipped fdars.fdata and fdars.scoring bindings. All assertions in the fences pass against the actual API.

## Threat Surface Scan

No new network endpoints, auth paths, or trust-boundary changes introduced. Executed fences:
- Network-free (no API key, no HTTP calls)
- Fixed seeds (seed=42 for scoring-metrics, no seed needed for stats fence — deterministic data)
- Base extras only (numpy, fdars, docs_data)
- FDARS_FENCE_OK sentinel confirmed in both built pages

T-29-04 (network disclosure via executed fences): mitigated — both fences are offline.
T-29-05 (SVG tampering): mitigated — SVGO gate is check-only idempotence (not rewrite).
T-29-06 (non-deterministic fence output): mitigated — fixed seed in scoring fence; stats fence is deterministic by construction.

## Self-Check

| Check | Result |
|-------|--------|
| docs/analyze/functional-statistics.md exists | FOUND |
| docs/analyze/scoring-metrics.md exists | FOUND |
| docs/assets/diagrams/functional-statistics.svg exists | FOUND |
| docs/assets/diagrams/scoring-metrics.svg exists | FOUND |
| Commit 6b596f1 exists | FOUND |
| Commit d064dcf exists | FOUND |
| site/analyze/functional-statistics/index.html contains FDARS_FENCE_OK | FOUND |
| site/analyze/scoring-metrics/index.html contains FDARS_FENCE_OK | FOUND |

## Self-Check: PASSED
