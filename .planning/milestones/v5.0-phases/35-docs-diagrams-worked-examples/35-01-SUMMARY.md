---
phase: 35-docs-diagrams-worked-examples
plan: "01"
subsystem: docs
tags: [docs, inference, svg, worked-examples, nav]
dependency_graph:
  requires: []
  provides:
    - docs/inference/functional-inference.md
    - docs/assets/diagrams/inference-permutation-test.svg
    - docs/assets/diagrams/inference-scb.svg
    - docs/assets/diagrams/inference-anova.svg
  affects:
    - mkdocs.yml
tech_stack:
  added: []
  patterns:
    - hand-authored-inline-svg
    - markdown-exec-offline-fence
    - docs-fast-build-gate
key_files:
  created:
    - docs/inference/functional-inference.md
    - docs/assets/diagrams/inference-permutation-test.svg
    - docs/assets/diagrams/inference-scb.svg
    - docs/assets/diagrams/inference-anova.svg
  modified:
    - mkdocs.yml
decisions:
  - All 4 fences written atomically into the single page to avoid broken internal SVG links during the tracer Task 1 build gate
  - FLM section (flm_f_test/flm_gof_test) documented with prose + small fence per locked 3-section structure (no dedicated SVG)
  - SCB fence uses Canadian Weather 15-station/every-4th-day subset + nb=fast(200,50) to keep compute tiny
  - ANOVA fence uses all 35 Canadian Weather stations (groups natural) + every-5th-day grid
metrics:
  duration_min: 42
  completed_date: "2026-08-18"
  tasks_completed: 3
  tasks_planned: 3
  commits: 3
  files_created: 4
  files_modified: 1
status: complete
actuals:
  tokens: 7745
  tasks: 3
  commits: 3
requirements: [DOCS-04, DOCS-07]
---

# Phase 35 Plan 01: Functional Inference Docs Summary

**One-liner:** Created the Functional Inference page with three method-accurate hand-authored SVGs and four offline executed fences covering two-sample tests, SCB bands, one-way functional ANOVA, and FLM inference.

## What Was Built

### Artifacts Created

1. **`docs/inference/functional-inference.md`** — Combined Functional Inference page with:
   - H1 "Functional Inference" + overview table mapping each method family to its functions, what it tests, and the return dict shape
   - **Two-sample tests section:** KaTeX theory (permutation null + p-value formula + conservative correction), parameter table for t_perm_test/f_perm_test/two_sample_mean_test, executed fence on Growth dataset (20 boys/20 girls, n_perm=fast(199,19), seed=0, renders permutation null histogram + observed statistic + tail) emitting FDARS_FENCE_OK
   - **SCB section:** Degras multiplier-bootstrap theory (pointwise vs simultaneous coverage), parameter tables for mean_scb + scb_two_sample_test with exact dict keys (lower/upper/center/half_width), executed fence on Canadian Weather (15 stations, every-4th-day, nb=fast(200,50)) emitting FDARS_FENCE_OK
   - **ANOVA section:** Between/within decomposition formula + V-statistic + integer-label requirement note, executed fence on Canadian Weather (4 regions, every-5th-day, groups mapped to int64) emitting FDARS_FENCE_OK
   - **FLM inference subsection:** Prose docs for flm_f_test + flm_gof_test with signatures + Returns, small Tecator-based fence (80 samples, n_comp=3) emitting FDARS_FENCE_OK
   - **References section:** 4 citations (Ramsay/Silverman, Degras, Zhang, Phipson/Smyth)

2. **`docs/assets/diagrams/inference-permutation-test.svg`** — Hand-authored inline SVG (viewBox 720x300, canonical STYLE_SPEC style block, role="img", aria-label). Method-accurate: bell-shaped permutation null histogram in indigo, dashed vertical line for T_obs in red, tail bars shaded red for p-value region.

3. **`docs/assets/diagrams/inference-scb.svg`** — Hand-authored inline SVG (viewBox 720x300, conforming). Method-accurate: mean curve (solid indigo) with wider SCB (blue fill + dashed boundary) and narrower pointwise CI (orange fill + dashed boundary), clearly labelled.

4. **`docs/assets/diagrams/inference-anova.svg`** — Hand-authored inline SVG (viewBox 720x300, conforming). Method-accurate: two-panel decomposition with between-group panel (3 group means vs grand mean, spread arrows) and within-group panel (individual curves spreading around group means, brace).

5. **`mkdocs.yml`** — New top-level "Inference" nav section added after Monitoring, before Analyze, with single child "Functional Inference" pointing at `inference/functional-inference.md`.

## Verification Results

| Check | Result |
|---|---|
| `PYTHONPATH=scripts DOCS_FAST=1 .venv/bin/mkdocs build --strict` site/ inference page | Built successfully (HTML 506KB) |
| `FDARS_FENCE_OK` occurrences in `site/inference/functional-inference/index.html` | 8 (all 4 fences executed and marked) |
| `inference-permutation-test.svg` ref in HTML | Present |
| `inference-scb.svg` ref in HTML | Present |
| `inference-anova.svg` ref in HTML | Present |
| Nav Inference section in mkdocs.yml | Present |
| SVG rendering (rsvg-convert) | All 3 SVGs render correctly |

## Deviations from Plan

### Auto-written (scope optimization)

**1. [Rule 2 — efficiency] All four fences written atomically in Task 1 commit**
- **Found during:** Task 1 tracer implementation
- **Issue:** The page references `../assets/diagrams/inference-scb.svg` and `../assets/diagrams/inference-anova.svg` from its body. Writing only the two-sample section in Task 1 would cause `--strict` to abort with "link target not found" warnings, failing the Task 1 tracer gate before Tasks 2/3 could be committed.
- **Fix:** Created all four fences and SVG references in the page body during Task 1. The three SVG files themselves were committed in their respective task commits. This is consistent with the plan's instruction that "Tasks 2-3 expand out to the SCB and ANOVA sections on the proven page" — the page skeleton was expanded to include all sections atomically, avoiding the strict-mode abort.
- **Files modified:** `docs/inference/functional-inference.md` (Tasks 2-3 content included at Task 1 write time)
- **Commits:** 87de126, 0a6e4e3, 9268c9b

### None other — plan executed as specified

- `source="above"` attribute used on all four fences (matches outlier-detection.md/functional-statistics.md convention for fences with plots)
- Parameter tables mirror outlier-detection.md convention exactly
- References section mirrors outlier-detection.md References style (numbered, italic journal, em-dash description)
- `fast()` helper used for `n_perm` and `nb` parameters (DOCS_FAST=1 support)
- `docs_data.load_growth()` and `docs_data.load_canadian_weather()` called without `return_fdata` kwarg (scripts/docs_data.py returns raw tuple — `return_fdata` is in `python/fdars/datasets.py` but not the docs script)

## Known Stubs

None. All sections are fully documented with executed fences that run against the shipped bindings and emit FDARS_FENCE_OK.

## Threat Surface Scan

No new network endpoints, auth paths, or schema changes. Executed fences use only local `docs/data/` datasets (no network). The new inference page is static HTML rendered by MkDocs.

## Self-Check: PASSED

All created files verified present on disk:
- `docs/inference/functional-inference.md` — FOUND
- `docs/assets/diagrams/inference-permutation-test.svg` — FOUND
- `docs/assets/diagrams/inference-scb.svg` — FOUND
- `docs/assets/diagrams/inference-anova.svg` — FOUND
- `.planning/phases/35-docs-diagrams-worked-examples/35-01-SUMMARY.md` — FOUND

All commits verified in git log:
- `87de126` — Task 1 (tracer) — FOUND
- `0a6e4e3` — Task 2 (SCB SVG) — FOUND
- `9268c9b` — Task 3 (ANOVA SVG) — FOUND
