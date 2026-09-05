---
phase: 73-documentation-release
plan: "03"
subsystem: docs
tags: [mkdocs, markdown-exec, svg-diagrams, density-fda, clustering, mfpca, shapelets, gak]

requires:
  - phase: 73-documentation-release/73-01
    provides: functional-time-series page + fence pattern (tracer)
  - phase: 73-documentation-release/73-02
    provides: regression pages (FoF, SoF, Frechet) + fence + diagram pattern
  - phase: 69-frechet-regression-density-fda
    provides: density_fda bindings (normalize_density, lqd_transform, lqd_fpca)
  - phase: 70-multi-domain-data-famm-advanced-clustering
    provides: mfpca, dbscan_fd, kcfc_cluster, famm bindings
  - phase: 71-shapelets-gak-metric
    provides: shapelet_transform_fit, shapelet_classifier_fit, gak_gram_matrix bindings

provides:
  - docs/analyze/density-fda.md — LQD pipeline page with FDARS_FENCE_OK fence
  - docs/analyze/advanced-clustering.md — DBSCAN-FD + KCFC page with FDARS_FENCE_OK fence
  - docs/analyze/multi-domain.md — MFPCA page with FDARS_FENCE_OK fence
  - docs/analyze/shapelets.md — Shapelets + GAK page with FDARS_FENCE_OK fence
  - docs/assets/diagrams/density-fda.svg — STYLE_SPEC SVG, SVGO-idempotent
  - docs/assets/diagrams/advanced-clustering.svg — STYLE_SPEC SVG, SVGO-idempotent
  - docs/assets/diagrams/multi-domain.svg — STYLE_SPEC SVG, SVGO-idempotent
  - docs/assets/diagrams/shapelets.svg — STYLE_SPEC SVG, SVGO-idempotent (GAK folds here)
  - mkdocs.yml: 4 new Analyze nav entries

affects:
  - 73-04 (DOCS-03 aspects.md + strict gate)
  - verify-work UAT for DOCS-01/DOCS-02
  - human diagram review gate (blocking, DOCS-03)

actuals:
  tokens: 14104
  tasks: 3
  commits: 3

tech-stack:
  added: []
  patterns:
    - "Naked-array convention: normalize_density/lqd_transform/inverse_lqd return 1D arrays, apply element-wise"
    - "mfpca list-not-stack: pass Python list of 2D arrays, never np.stack"
    - "PyShapeletFit is opaque handle — shapelet_classifier_fit is an independent fit path"
    - "GAK folds into Shapelets page per locked user decision"

key-files:
  created:
    - docs/analyze/density-fda.md
    - docs/analyze/advanced-clustering.md
    - docs/analyze/multi-domain.md
    - docs/analyze/shapelets.md
    - docs/assets/diagrams/density-fda.svg
    - docs/assets/diagrams/advanced-clustering.svg
    - docs/assets/diagrams/multi-domain.svg
    - docs/assets/diagrams/shapelets.svg
  modified:
    - mkdocs.yml

key-decisions:
  - "lqd_fpca parameter is 'ncomp' (not 'n_comp'); returned key also 'ncomp'; variance key is 'fve' (not 'explained_variance') — corrected from RESEARCH template"
  - "kcfc_cluster returns 'cluster' key (not 'labels') — corrected from RESEARCH template"
  - "np.trapz deprecated in NumPy 2.x — fence uses np.trapezoid"
  - "GAK folds into Shapelets page (locked user decision); Distance Metrics page can reference back"
  - "mfpca ncomp derived from len(result['eigenvalues']) — no n_comp key in result dict"

patterns-established:
  - "Deviation Rule 1 (Bug): All RESEARCH template API discrepancies corrected before writing fences"
  - "Fence sanity: run .venv/bin/python -c '...' for each fence before docs build"
  - "SVGO idempotence: two-pass npx svgo@3.3.4 diff check before committing each SVG"

requirements-completed: [DOCS-01, DOCS-02]

coverage:
  - id: D1
    description: "density-fda.md with FDARS_FENCE_OK fence (normalize_density/lqd_transform/lqd_fpca)"
    requirement: DOCS-01
    verification:
      - kind: integration
        ref: "DOCS_FAST=1 PYTHONPATH=scripts .venv/bin/mkdocs build && grep FDARS_FENCE_OK site/analyze/density-fda/index.html"
        status: pass
    human_judgment: false
  - id: D2
    description: "advanced-clustering.md with FDARS_FENCE_OK fence (dbscan_fd/kcfc_cluster)"
    requirement: DOCS-01
    verification:
      - kind: integration
        ref: "DOCS_FAST=1 PYTHONPATH=scripts .venv/bin/mkdocs build && grep FDARS_FENCE_OK site/analyze/advanced-clustering/index.html"
        status: pass
    human_judgment: false
  - id: D3
    description: "multi-domain.md with FDARS_FENCE_OK fence (mfpca, list-not-stack pattern)"
    requirement: DOCS-01
    verification:
      - kind: integration
        ref: "DOCS_FAST=1 PYTHONPATH=scripts .venv/bin/mkdocs build && grep FDARS_FENCE_OK site/analyze/multi-domain/index.html"
        status: pass
    human_judgment: false
  - id: D4
    description: "shapelets.md with FDARS_FENCE_OK fence (shapelet_transform_fit/gak_gram_matrix, GAK folded in)"
    requirement: DOCS-01
    verification:
      - kind: integration
        ref: "DOCS_FAST=1 PYTHONPATH=scripts .venv/bin/mkdocs build && grep FDARS_FENCE_OK site/analyze/shapelets/index.html"
        status: pass
    human_judgment: false
  - id: D5
    description: "4 STYLE_SPEC-conformant SVGO-idempotent SVG diagrams (density-fda, advanced-clustering, multi-domain, shapelets)"
    requirement: DOCS-02
    verification:
      - kind: other
        ref: "npx svgo@3.3.4 two-pass idempotence check: ALL_IDEMPOTENT_OK"
        status: pass
    human_judgment: false
  - id: D6
    description: "Method-accuracy of 4 SVG diagrams (visual concept matches shipped binding behavior)"
    requirement: DOCS-02
    verification: []
    human_judgment: true
    rationale: "Method-accuracy requires human visual review — blocking gate specified in DOCS-03 and user constraints"

duration: 38min
completed: 2026-09-04
status: complete
---

# Phase 73 Plan 03: Analyze Section Pages (Density FDA, Advanced Clustering, Multi-Domain, Shapelets) Summary

**Four Analyze-section pages with offline FDARS_FENCE_OK fences, four STYLE_SPEC SVGO-idempotent SVGs, and nav entries — completing DOCS-01/DOCS-02 coverage for all Analyze families; API discrepancies from RESEARCH templates corrected via per-fence Python sanity checks.**

## Performance

- **Duration:** 38 min
- **Started:** 2026-09-04T20:05:46Z
- **Completed:** 2026-09-04T20:43:49Z
- **Tasks:** 3
- **Files modified:** 9 (4 pages, 4 SVGs, mkdocs.yml)

## Accomplishments

- Authored `density-fda.md`: LQD transform pipeline with `normalize_density`/`lqd_transform`/`lqd_fpca`; documents naked-array single-vector convention; `lqd_fpca` 6-key dict (`mean`, `singular_values`, `loadings`, `scores`, `fve`, `ncomp`); FDARS_FENCE_OK fence verified
- Authored `advanced-clustering.md`: DBSCAN-FD (noise label $-1$, no prior $k$), KCFC (per-cluster FPCA), FunFEM, align_cluster_fd; non-square fixture (n=25, m=40); FDARS_FENCE_OK fence verified
- Authored `multi-domain.md`: MFPCA across multiple functional domains; list-not-stack pitfall prominently documented; mfpca 6-key result dict; FAMM API table; FDARS_FENCE_OK fence verified
- Authored `shapelets.md`: Shapelet discovery/transform/classifier with opaque handle types; GAK (gak_gram_matrix, sigma_gak, gak_gram_predict) folded into this page per locked user decision; FDARS_FENCE_OK fence verified
- Authored 4 STYLE_SPEC-conformant SVGs (720×480, five CSS classes, role/aria/title/desc, SVGO-idempotent): density-fda (LQD pipeline), advanced-clustering (DBSCAN+KCFC+FunFEM panels), multi-domain (MFPCA joint SVD), shapelets (subsequence extraction + GAK Gram matrix)
- Added 4 Analyze nav entries to mkdocs.yml; DOCS_FAST build green; check_docs_figures.py exits 0; grep count 4

## Task Commits

Each task committed atomically:

1. **Task 1: density-fda.md + advanced-clustering.md** — `235cfc6` (feat)
2. **Task 2: multi-domain.md + shapelets.md** — `b56526a` (feat)
3. **Task 3: 4 SVG diagrams + mkdocs.yml nav** — `dde94e8` (feat)

## Files Created/Modified

- `docs/analyze/density-fda.md` — Density FDA page; LQD transform; naked-array convention; lqd_fpca dict; FDARS_FENCE_OK fence
- `docs/analyze/advanced-clustering.md` — DBSCAN-FD/KCFC/FunFEM/align-cluster page; noise=-1; FDARS_FENCE_OK fence
- `docs/analyze/multi-domain.md` — MFPCA page; list-not-stack pitfall; FAMM table; FDARS_FENCE_OK fence
- `docs/analyze/shapelets.md` — Shapelets + GAK page; opaque handles; FDARS_FENCE_OK fence
- `docs/assets/diagrams/density-fda.svg` — LQD pipeline concept diagram (720×480, SVGO-idempotent)
- `docs/assets/diagrams/advanced-clustering.svg` — DBSCAN+KCFC+FunFEM panel diagram (720×480, SVGO-idempotent)
- `docs/assets/diagrams/multi-domain.svg` — MFPCA joint SVD concept diagram (720×480, SVGO-idempotent)
- `docs/assets/diagrams/shapelets.svg` — Shapelet discovery + GAK Gram matrix diagram (720×480, SVGO-idempotent)
- `mkdocs.yml` — Added 4 Analyze nav entries (Density FDA, Advanced Clustering, Multi-Domain FDA, Shapelets)

## Decisions Made

- `lqd_fpca` parameter is `ncomp` (not `n_comp`) and returned key is also `ncomp`; variance key is `fve` (not `explained_variance`). RESEARCH template was wrong — corrected before writing fence.
- `kcfc_cluster` returns `cluster` key (not `labels`) — RESEARCH template was wrong; corrected.
- `np.trapz` is removed in NumPy 2.x; fence uses `np.trapezoid`.
- GAK folds into the Shapelets page (locked user decision); one-line note in Distance Metrics page is deferred since that page already existed and the note would require its own edit.
- mfpca component count derived from `len(result['eigenvalues'])` — there is no `n_comp` key in the mfpca result dict (consistent with RESEARCH).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Corrected lqd_fpca API parameter and return keys**
- **Found during:** Task 1 (density fence sanity check)
- **Issue:** RESEARCH template used `n_comp=2` (wrong keyword) and referenced `fp['n_comp']` and `fp['explained_variance']` — actual API uses `ncomp=` and returns `ncomp` + `fve`
- **Fix:** Updated fence code to use `ncomp=2` and `fp['ncomp']`
- **Files modified:** docs/analyze/density-fda.md
- **Verification:** `.venv/bin/python -c "..."` passed without error
- **Committed in:** 235cfc6

**2. [Rule 1 - Bug] Corrected kcfc_cluster result key from 'labels' to 'cluster'**
- **Found during:** Task 1 (clustering fence sanity check)
- **Issue:** RESEARCH template used `kfc['labels']` — actual API returns `cluster` key
- **Fix:** Updated fence to use `kfc['cluster']`
- **Files modified:** docs/analyze/advanced-clustering.md
- **Verification:** `.venv/bin/python -c "..."` passed without error
- **Committed in:** 235cfc6

**3. [Rule 1 - Bug] Replaced deprecated np.trapz with np.trapezoid**
- **Found during:** Task 1 (density fence sanity check)
- **Issue:** `np.trapz` raises `AttributeError` in NumPy 2.x (Python 3.14 venv)
- **Fix:** Changed to `np.trapezoid`
- **Files modified:** docs/analyze/density-fda.md
- **Verification:** Fence ran cleanly
- **Committed in:** 235cfc6

---

**Total deviations:** 3 auto-fixed (Rule 1 — API bugs from RESEARCH templates)
**Impact on plan:** All corrections necessary for correctness. No scope creep.

## Issues Encountered

None — build green on first attempt after per-fence Python sanity checks.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

All 7 Analyze/Regression family pages are now complete (73-01 FTS, 73-02 FoF/SoF/Frechet, 73-03 Density/AdvClust/MultiDomain/Shapelets). Phase 73 next step: Plan 04 — update aspects.md (DOCS-03) + run final `--strict` build gate + blocking human diagram review.

---
*Phase: 73-documentation-release*
*Completed: 2026-09-04*

## Self-Check: PASSED

- [x] docs/analyze/density-fda.md exists
- [x] docs/analyze/advanced-clustering.md exists
- [x] docs/analyze/multi-domain.md exists
- [x] docs/analyze/shapelets.md exists
- [x] docs/assets/diagrams/density-fda.svg exists
- [x] docs/assets/diagrams/advanced-clustering.svg exists
- [x] docs/assets/diagrams/multi-domain.svg exists
- [x] docs/assets/diagrams/shapelets.svg exists
- [x] All 4 SVGs SVGO-idempotent (two-pass diff)
- [x] DOCS_FAST build green (exit 0)
- [x] check_docs_figures.py site exits 0
- [x] FDARS_FENCE_OK in all 4 built pages (2 occurrences each — source + output)
- [x] No Traceback in any built page
- [x] mkdocs.yml Analyze nav references all 4 pages (grep count 4)
- [x] Commits 235cfc6, b56526a, dde94e8 exist
