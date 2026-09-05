---
phase: 73-documentation-release
plan: "02"
subsystem: docs
tags: [mkdocs, markdown-exec, svg, fdars-fence-ok, regression, fof, sof, frechet, docs]

requires:
  - phase: 73-documentation-release
    plan: "01"
    provides: "73-01 tracer: fts page + diagram + nav pattern proven; DOCS_FAST build loop established"
  - phase: 68-function-on-function-scalar-on-function-regression
    provides: "fof_regression (9-key dict, dual 2D path), fof_re_regression, predict_fof, fof_cv; fdars.scalar_on_function with fam/gkam/gsam/variable_selection"
  - phase: 69-frechet-regression-density-fda
    provides: "fdars.frechet with frechet_mean (naked array for SPD), frechet_global_reg, frechet_local_reg, frechet_anova"

provides:
  - "docs/regression/function-on-function.md: FoF + FoF-RE page with offline FDARS_FENCE_OK fence (n=25, mx=20, my=15 non-square)"
  - "docs/regression/additive-sof.md: FAM / gkam / gsam / variable_selection page with offline FDARS_FENCE_OK fence"
  - "docs/regression/frechet-regression.md: Frechet Regression page with SPD fixture, np.asarray() naked-array handling"
  - "docs/assets/diagrams/function-on-function.svg: STYLE_SPEC 720x480 beta-surface concept, SVGO-idempotent"
  - "docs/assets/diagrams/additive-sof.svg: STYLE_SPEC 720x480 additive partial-effects concept, SVGO-idempotent"
  - "docs/assets/diagrams/frechet-regression.svg: STYLE_SPEC 720x480 metric-space barycenter concept, SVGO-idempotent"
  - "mkdocs.yml: 3 Regression nav entries (Function-on-Function, Additive Scalar-on-Function, Frechet Regression)"

affects:
  - 73-03 (diagram review gate — these 3 diagrams are part of the blocking human review)
  - Any consumer of DOCS-01/DOCS-02 regression coverage

actuals:
  tokens: 27000
  tasks: 3
  commits: 3

tech-stack:
  added: []
  patterns:
    - "DOCS_FAST=1 single build validates all 3 pages at once — do NOT run one build per page"
    - "Per-fence sanity: .venv/bin/python -c '...' before the full build catches import/runtime errors cheaply"
    - "SVGO two-pass idempotence confirmed before committing each SVG batch"
    - "frechet_mean naked-array pattern: np.asarray(frechet_mean(spds, space='spd', d=d)) — never index as dict"

key-files:
  created:
    - docs/regression/function-on-function.md
    - docs/regression/additive-sof.md
    - docs/regression/frechet-regression.md
    - docs/assets/diagrams/function-on-function.svg
    - docs/assets/diagrams/additive-sof.svg
    - docs/assets/diagrams/frechet-regression.svg
  modified:
    - mkdocs.yml

key-decisions:
  - "frechet_mean treated as naked array (not dict) per Pitfall 7 — np.asarray() wrapping shown in fence and warned in page"
  - "All 3 SVGs use viewBox 720x480 (two-row layout) to accommodate method concept + function API strip"
  - "All fences tested with .venv/bin/python -c before site build to catch errors before 29-min DOCS_FAST run"
  - "SoF page uses fdars.scalar_on_function.fam as the primary fence (fregre_gkam/gsam/variable_selection in API table)"
  - "SPD fixture built via A @ A.T + I pattern to guarantee positive-definite diagonal (not just random symmetric)"

requirements-completed: [DOCS-01, DOCS-02]

coverage:
  - id: D1
    description: "docs/regression/function-on-function.md renders with fof_regression fence printing FDARS_FENCE_OK"
    requirement: DOCS-01
    verification:
      - kind: integration
        ref: "DOCS_FAST build + check_docs_figures.py site: FDARS_FENCE_OK found in site/regression/function-on-function/index.html"
        status: pass
    human_judgment: false
  - id: D2
    description: "docs/regression/additive-sof.md renders with fam fence printing FDARS_FENCE_OK"
    requirement: DOCS-01
    verification:
      - kind: integration
        ref: "DOCS_FAST build + check_docs_figures.py site: FDARS_FENCE_OK found in site/regression/additive-sof/index.html"
        status: pass
    human_judgment: false
  - id: D3
    description: "docs/regression/frechet-regression.md renders with frechet_mean fence treating return as naked array, printing FDARS_FENCE_OK"
    requirement: DOCS-01
    verification:
      - kind: integration
        ref: "DOCS_FAST build + check_docs_figures.py site: FDARS_FENCE_OK found in site/regression/frechet-regression/index.html"
        status: pass
    human_judgment: false
  - id: D4
    description: "Three STYLE_SPEC SVGs (function-on-function, additive-sof, frechet-regression) are SVGO@3.3.4 two-pass idempotent"
    requirement: DOCS-02
    verification:
      - kind: other
        ref: "npx svgo@3.3.4 two-pass diff — zero diff on second pass for all 3 diagrams"
        status: pass
    human_judgment: false
  - id: D5
    description: "Regression nav in mkdocs.yml references all three new pages (count=3)"
    verification:
      - kind: other
        ref: "grep -c ... mkdocs.yml == 3"
        status: pass
    human_judgment: false
  - id: D6
    description: "Method accuracy of SVG diagrams (FoF beta-surface, SoF partial effects, Frechet barycenter) is visually correct"
    verification: []
    human_judgment: true
    rationale: "Diagram method-accuracy requires human review against the shipped binding semantics — this is the DOCS-03 blocking gate"

duration: 37min
completed: 2026-09-04
status: complete
---

# Phase 73 Plan 02: Regression Documentation Pages Summary

**Three Regression-section doc pages (FoF, Additive SoF, Frechet) with offline FDARS_FENCE_OK fences, three STYLE_SPEC 720x480 SVGO-idempotent SVG diagrams, and Regression nav entries — DOCS_FAST build green, check_docs_figures exit 0**

## Performance

- **Duration:** 37 min
- **Started:** 2026-09-04T19:25:18Z
- **Completed:** 2026-09-04T20:02:39Z
- **Tasks:** 3
- **Files modified:** 7 (3 new pages, 3 new SVGs, mkdocs.yml)

## Accomplishments

- `docs/regression/function-on-function.md`: FoF regression page with `fof_regression` fence (n=25, mx=20, my=15 non-square; ncomp_x=3/ncomp_y=3; beta_surface shape printed). Full API table: 9-key dict, `predict_fof`, `fof_cv`, RE variant. Pitfall 7 (fpca_x/fpca_y exclusion) noted.
- `docs/regression/additive-sof.md`: Additive SoF page with `fam` fence (n=25, m=30; kernel=gaussian). 7-key dict documented. `fregre_gkam`, `fregre_gsam`, `variable_selection`, `model_selection_ncomp` in API table.
- `docs/regression/frechet-regression.md`: Frechet Regression page with SPD `frechet_mean` fence (A@A.T+I fixture, d=2). Prominent warning: `frechet_mean` returns a naked array, not a dict — `np.asarray()` required. `frechet_global_reg`, `frechet_local_reg`, `frechet_anova` in API table.
- Three STYLE_SPEC-conformant SVG diagrams (720x480): FoF beta-surface concept, SoF additive partial effects, Frechet metric-space barycenter. All SVGO@3.3.4 two-pass idempotent.
- Three Regression nav entries added to mkdocs.yml (Function-on-Function, Additive Scalar-on-Function, Fréchet Regression).
- DOCS_FAST build: exit 0 in 1768 s (~29 min). `check_docs_figures.py site`: exit 0. FDARS_FENCE_OK found in all three built HTML pages. No Tracebacks.

## Task Commits

Each task was committed atomically:

1. **Task 1: FoF page** - `5be14f9` (feat)
2. **Task 2: Additive SoF + Frechet pages** - `a2c0cd1` (feat)
3. **Task 3: 3 SVG diagrams + mkdocs.yml nav** - `f5a5792` (feat)

## Files Created/Modified

- `/home/simonm/projects/rust/pyfda/docs/regression/function-on-function.md` — FoF + FoF-RE page (143 lines)
- `/home/simonm/projects/rust/pyfda/docs/regression/additive-sof.md` — Additive SoF page (163 lines)
- `/home/simonm/projects/rust/pyfda/docs/regression/frechet-regression.md` — Frechet Regression page (153 lines)
- `/home/simonm/projects/rust/pyfda/docs/assets/diagrams/function-on-function.svg` — 720x480 beta-surface diagram
- `/home/simonm/projects/rust/pyfda/docs/assets/diagrams/additive-sof.svg` — 720x480 additive partial-effects diagram
- `/home/simonm/projects/rust/pyfda/docs/assets/diagrams/frechet-regression.svg` — 720x480 metric-space barycenter diagram
- `/home/simonm/projects/rust/pyfda/mkdocs.yml` — 3 Regression nav entries added after Functional GLM

## Decisions Made

- **frechet_mean naked-array pattern**: page prominently warns that `frechet_mean` returns the mean object directly (array, not dict). Fence uses `np.asarray(frechet_mean(...))`. This is the primary user-facing gotcha documented in the research (Pitfall 7).
- **SPD fixture construction**: `A @ A.T + np.eye(d)` pattern guarantees genuinely positive-definite matrix — random symmetric matrices are not reliably PD.
- **All SVGs at 720x480**: two-row layout accommodates both the method concept panel (top half) and the function API card strip (bottom half), consistent with functional-time-series.svg precedent.
- **Single DOCS_FAST build for all 3 pages**: per the execution context directive — author all pages + fences + verify per-fence with python -c first, then one build, not one build per page.
- **fam as primary SoF fence**: `fam` is the simplest single-predictor entry point; `fregre_gkam/gsam/variable_selection/model_selection_ncomp` covered in API table without live fences.

## Deviations from Plan

None - plan executed exactly as written. All three pages, three diagrams, and nav entries delivered per spec. Pre-fence sanity checks (`.venv/bin/python -c`) confirmed all three fences before the site build.

## Issues Encountered

None. Build took ~29 min as expected. All fences passed on first attempt.

## User Setup Required

None - no external service configuration required.

## Known Stubs

None. All three fences execute live fdars API calls with deterministic fixtures and print FDARS_FENCE_OK.

## Next Phase Readiness

- DOCS-01/DOCS-02 complete for the Regression section (FoF, SoF, Frechet).
- The three diagrams are authored and SVGO-idempotent — they are part of the DOCS-03 blocking human diagram method-accuracy review gate (not yet executed).
- Ready for 73-03 (remaining Analyze-section pages) or any subsequent plan in the phase.

## Self-Check: PASSED

- `docs/regression/function-on-function.md` — FOUND
- `docs/regression/additive-sof.md` — FOUND
- `docs/regression/frechet-regression.md` — FOUND
- `docs/assets/diagrams/function-on-function.svg` — FOUND
- `docs/assets/diagrams/additive-sof.svg` — FOUND
- `docs/assets/diagrams/frechet-regression.svg` — FOUND
- `mkdocs.yml` nav count: 3 — CONFIRMED
- SVGO idempotence: ALL_IDEMPOTENT_OK — CONFIRMED
- DOCS_FAST build exit: 0 — CONFIRMED
- `check_docs_figures.py site`: exit 0 — CONFIRMED
- FDARS_FENCE_OK in all 3 HTML pages — CONFIRMED
- No Traceback in any of the 3 HTML pages — CONFIRMED
- Commit `5be14f9` — FOUND
- Commit `a2c0cd1` — FOUND
- Commit `f5a5792` — FOUND

---
*Phase: 73-documentation-release*
*Completed: 2026-09-04*
