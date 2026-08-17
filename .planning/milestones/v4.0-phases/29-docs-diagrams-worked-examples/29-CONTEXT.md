# Phase 29: Docs — Diagrams & Worked Examples - Context

**Gathered:** 2026-08-16
**Status:** Ready for planning

<domain>
## Phase Boundary

Document every new v4.0 capability (Phases 26–28) to the project's method-accurate standard: new hand-authored inline SVG concept diagrams + runnable offline worked examples across `represent/`, `analyze/`, `align/`, and updated advisor pages — with the full `mkdocs build --strict` green against the real shipped bindings. This is the FINAL phase of v4.0.

Delivers (DOCS-01/02/03):
- **New dedicated docs pages** (one per capability, wired into `mkdocs.yml` nav) for: spline interpolation + extrapolation policy, missing-value imputation, functional statistics (variance/std/covariance + depth-median + trim-mean), scoring metrics, least-squares shift registration, banded elastic alignment (+ registration-quality scores).
- **~6 new hand-authored inline SVG concept diagrams**, method-accurate, passing the SVGO idempotence + build-determinism gates and a human PNG review.
- **Runnable offline worked examples** against existing `docs/data/` datasets — executed `markdown-exec` fences that stay network-free/deterministic (fixed seeds, base extras only) and emit `FDARS_FENCE_OK`.
- **Advisor docs update** (`docs/advisor/aspects.md`) for the new `scoring` aspect + imputation-quality (represent) + registration-quality (alignment) diagnostics.
</domain>

<decisions>
## Implementation Decisions

### Page Structure (user-decided: NEW dedicated pages)
- New pages, one per capability, wired into `mkdocs.yml` nav:
  - `docs/represent/interpolation.md` — `spline_interpolate` / `*_with_policy` + `ExtrapolationPolicy` (Boundary/Exception/Fill/Periodic).
  - `docs/represent/imputation.md` — `impute_missing_values` + `ImputationMethod` (Linear/Mean/Constant).
  - `docs/analyze/functional-statistics.md` — `functional_variance/std/covariance`, `depth_based_median`, `trim_mean` (+ the `fd.var/std/cov/median` methods).
  - `docs/analyze/scoring-metrics.md` — the 5 `fdars.scoring` prediction-scoring metrics.
  - `docs/align/shift-registration.md` — `least_squares_shift_registration` (+ `fd.shift_register()`) and the 3 registration-quality scores.
  - `docs/align/banded-alignment.md` — banded elastic alignment (`*_with_band`, `band_frac`, Sakoe–Chiba corridor).
  (Exact page split is Claude's discretion — the planner may merge two closely-related ones if that reads better, as long as every new capability is documented and nav-wired.)
- Update `docs/advisor/aspects.md` for the new advisor coverage (scoring aspect + imputation/registration diagnostics) — extend, don't create a new advisor page.

### Diagram Scope (user-decided: FULL set ~6)
- ~6 new hand-authored inline SVG concept diagrams, one per concept:
  1. Interpolation + extrapolation policy — off-grid query points + the 4 policy behaviors.
  2. Missing-value imputation — NaN gaps filled by linear/mean/constant.
  3. Functional statistics — pointwise variance band / covariance surface / depth-median-vs-mean (the diagram must make depth-median ≠ geometric-median clear).
  4. Scoring metrics — predicted-vs-true curves with the residual the metric integrates.
  5. Shift registration — a RIGID HORIZONTAL SHIFT to the cross-sectional mean (must be visually distinct from elastic warping — a common confusion the diagram must avoid).
  6. Banded elastic alignment — the Sakoe–Chiba diagonal corridor over the DP grid.
- All diagrams follow `STYLE_SPEC.md` (viewBox 0 0 720 300, inline `<style>` classes `.ttl/.sub/.lab/.sm/.mono`, system-ui fonts, muted palette, `role="img"` + `aria-label`), pass the SVGO idempotence lint + build-determinism gates, and are method-accurate (verified via the build recipe + `rsvg-convert`/PNG human review).

### Method-Accuracy Emphasis (mandatory — the project's core value)
- Every diagram faithfully depicts what the method ACTUALLY does. Specific traps to avoid: shift registration is a horizontal translation (NOT a warp); `depth_based_median` returns an OBSERVED curve (a data row), not an averaged curve; `ExtrapolationPolicy::Exception` raises rather than extrapolating; MAPE/MSLE have domain restrictions.
- Correctness is validated by section review on the built site (human PNG review of each new SVG) — a human-verify checkpoint at the end of this phase, consistent with the v1.0/v2.1 review-gate precedent.

### Executed Fences (offline & deterministic)
- Worked-example `markdown-exec` fences run against the REAL shipped bindings; they must be network-free (no API key — advisor `advise()` interpretation shown as an illustrative/non-executed fence, or env-gated like v2.1's Python API page), use fixed seeds and base extras only, and emit the `FDARS_FENCE_OK` sentinel. Figures use the existing `docs_fig` mechanism (`PYTHONPATH=scripts`).

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `docs/STYLE_SPEC.md` (or `.planning/`-referenced style spec) — the shared SVG style contract; the SVGO check-only lint gate (idempotence, all diagrams) + build-determinism (`svg.hashsalt`, `<dc:date>` suppression).
- `docs/assets/diagrams/*.svg` (45 existing) — style exemplars to match; new SVGs land here.
- `docs/represent/`, `docs/analyze/`, `docs/align/`, `docs/advisor/` — existing section pages + `index.md` per section; `mkdocs.yml` nav.
- `scripts/docs_fig.py` + `markdown-exec` — inline executed figures/fences (`PYTHONPATH=scripts`); the `FDARS_FENCE_OK` sentinel pattern from v2.1.
- Datasets: `docs/data/` — canadian_weather, growth, phoneme, tecator, sonar, wine (research FEATURES.md mapped the best dataset per method).
- `DOCS_FAST` helper + the docs build recipe (memory: venv + PYTHONPATH + DOCS_FAST; `rsvg-convert` for visual SVG checks).

### Established Patterns
- Diagrams stay HAND-AUTHORED inline SVG (no programmatic generation) — a hard project constraint.
- New pages wired into `mkdocs.yml` nav; `mkdocs build --strict` must exit 0 offline.
- Executed fences deterministic + `FDARS_FENCE_OK`; only pages that need it carry executed fences (v2.1 kept MCP/Skill fences illustrative).

### Integration Points
- Each new page references its new SVG via `![...](../assets/diagrams/NAME.svg){ .fdars-diagram }` and runs worked examples against `docs/data/`.
- `docs/advisor/aspects.md` extends the per-aspect coverage table/prose for the scoring/imputation/registration additions.

</code_context>

<specifics>
## Specific Ideas

- Dataset mapping (from research FEATURES.md — confirm at author time): interpolation/imputation → growth or canadian_weather (irregular/missing-friendly); functional statistics → canadian_weather (temperature curves); scoring metrics → a predict-vs-true setup (e.g. growth or tecator); shift/banded registration → growth or a peak-aligned dataset.
- Reuse the v2.1 `FDARS_FENCE_OK` executed-fence proof and the per-page human-review gate.
- Keep advisor `advise()` (LLM) fences non-executed/illustrative or env-gated so the build stays offline.

</specifics>

<deferred>
## Deferred Ideas

- Accessibility long-form `<title>`/`<desc>` (A11Y-01) — still deferred (Deferred Items in STATE.md).
- Editorial consolidation of overlapping example pages (EX2-01) — deferred.

</deferred>
