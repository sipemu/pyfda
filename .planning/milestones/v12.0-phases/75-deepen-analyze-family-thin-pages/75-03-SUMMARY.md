---
phase: 75-deepen-analyze-family-thin-pages
plan: "03"
subsystem: docs/analyze
tags: [docs, mfpca, famm, multi-domain, DEPTH-02]
status: complete

dependency_graph:
  requires: ["75-02"]
  provides: ["docs/analyze/multi-domain.md (parity-grade)"]
  affects: ["docs/analyze/index.md (cross-ref target)"]

tech_stack:
  added: []
  patterns:
    - "UNNUMBERED analyze template (plain ## headings, method-selector table near top)"
    - "MFPCA list-of-arrays input pattern with corrected standalone-container note"
    - "dense_flmm/multi_famm plain numpy array inputs (not PyMultiFunData)"
    - "html figure fence: MFPCA scores scatter"
    - "docs_fig.fig()/render() inline SVG pattern"

key_files:
  created: []
  modified:
    - docs/analyze/multi-domain.md

decisions:
  - "Use synthetic simulation only (no real dataset: none in docs/data/ fits multi-variable co-observed design)"
  - "Include MFPCA scores scatter as the html figure (natural 2-component visualization)"
  - "dense_flmm fence: 8 subjects x 3 visits (24 rows) — smallest realistic longitudinal design"
  - "multi_famm fence: 6 subjects x 3 visits, 2 dimensions — minimal but demonstrates list-of-arrays input"
  - "PyMultiFunData documented as standalone-only, not removed — it exists as a container utility"

metrics:
  completed_date: "2026-09-05"
  duration_minutes: 3
  tasks_completed: 1
  tasks_planned: 1
  commits: 1

actuals:
  tokens: 4778    # 19112 diff chars / 4
  tasks: 1
  commits: 1
---

# Phase 75 Plan 03: Multi-Domain FDA — Summary

Brought `docs/analyze/multi-domain.md` to full mature-page parity (DEPTH-02) by restructuring to the UNNUMBERED analyze template, correcting the confirmed API errors (PyMultiFunData handle misuse), and adding all required structural sections, admonitions, and runnable fences.

## What Was Built

The page now delivers:

- **Method-selector table** near the top covering mfpca, dense_flmm, multi_famm, and multi_fdata_from_components
- **When to use** decision section: MFPCA vs per-variable FPCA, FLMM for longitudinal designs, multi_famm for multi-dimension longitudinal data
- **MFPCA section**: theory, syntax block, exec fence (prints scores shape + eigenfunction shapes), parameters + returns table, "Pass a list" warning
- **MFPCA figure fence** (html="1"): MFPCA scores scatter across 2 components for two simulated groups
- **dense_flmm section**: theory (REML-EM FLMM), corrected signature, exec fence (8 subjects x 3 visits), full 14-key return dict table, convergence note admonition
- **multi_famm section**: corrected signature (list of arrays), exec fence (6 subjects x 3 visits, 2 dims), 4-key return dict table
- **PyMultiFunData standalone-container note**: info admonition stating no FAMM/MFPCA function consumes it in fdars-core 0.33
- **Result interpretation** subsection: reading eigenfunctions, reading stacked_fitted and random_effects
- **"Methods available in R" note**: tensor-product basis not replicated, multi_famm uses per-dimension FLMM
- **See also** block: clustering.md, functional-statistics.md, outlier-detection.md, index.md
- Retained both original references verbatim

## Verify Gates

Both verify gates passed:

1. **Structural check (node one-liner):** `STRUCT OK fences=4 adm=5 html=1`
   - `## When to use`: present
   - `## See also`: present
   - FDARS_FENCE_OK sentinels: 4 (>= 3)
   - Admonitions (`!!! note|tip|warning|info`): 5 (>= 3)
   - html="1" fences: 1 (>= 1)
   - `standalone` statement near PyMultiFunData: present
   - No `dense_flmm`/`multi_famm` call passing a PyMultiFunData handle: 0 matches
   - `multi_famm(data_list` form: present
   - `dense_flmm(data, subject_ids` form: present

2. **Fence runner:** `ALL 4 EXEC FENCES EMITTED FDARS_FENCE_OK in docs/analyze/multi-domain.md`

## Deviations from Plan

**None** — plan executed exactly as written.

The four fences match the RESEARCH Section 6.3 / Section 8 "Multi-domain" minimal fence patterns.
`dense_flmm` converged on n=24 (Assumption A3 confirmed valid).

## Commits

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Bring multi-domain.md to full parity | 7a944ee | docs/analyze/multi-domain.md |

## Known Stubs

None — all sections are wired to runnable fences with real fdars API calls.

## Self-Check: PASSED

- docs/analyze/multi-domain.md: FOUND
- commit 7a944ee: present in git log
- Both verify gates: PASS
