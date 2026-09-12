---
phase: 88-front-matter-design-architecture-capability-tour
plan: "02"
subsystem: paper-pipeline
status: complete
tags: [snippets, capability-tour, fpca-pace, sklearn, advisor, listings, determinism]
completed: 2026-09-09

dependency_graph:
  requires:
    - 88-01 (gen_snippets.py harness + represent tracer + paper scaffold)
    - paper/code/paper_utils.py (data_path injected into exec namespace)
    - paper/snippets/represent.tex (tracer from Plan 01)
    - docs/data/growth.csv, phoneme.csv, tecator.csv, canadian_weather.csv
    - fdars 0.12.0 (compiled, importable in .venv)
  provides:
    - paper/code/gen_snippets.py (extended with 13 additional family entries)
    - paper/snippets/basis.tex
    - paper/snippets/depth.tex
    - paper/snippets/fpca.tex (includes PACE sparse/irregular path — MANU-05)
    - paper/snippets/clustering.tex
    - paper/snippets/classification.tex
    - paper/snippets/regression.tex
    - paper/snippets/fts.tex
    - paper/snippets/spm.tex
    - paper/snippets/tolerance.tex
    - paper/snippets/metric.tex
    - paper/snippets/alignment.tex
    - paper/snippets/advisor_diag.tex
    - paper/snippets/sklearn.tex
    - paper/sections/capabilities.tex (complete breadth-first family walk)
  affects:
    - All downstream plans that \input capabilities.tex (88-03 intro/stmt-of-need, 88-05 conclusion)
    - Phase 90 GATE-02 validates snippet drift gate for the full set

tech_stack:
  added:
    - 13 new family entries in gen_snippets.py SNIPPETS list
    - 13 new paper/snippets/*.tex generated fragments
  patterns:
    - exec() in fresh namespace with data_path injected (PIPE-01)
    - int64 ndarray labels for fclassif_knn (Pitfall 2 / GOTCHA #6)
    - Unpacked positional args for spm_monitor (not the result dict, GOTCHA #9)
    - Raw-data-not-model for ftsm_forecast (GOTCHA #8)
    - n_components (not n_comp) for FPCATransformer (GOTCHA #14)
    - LLM-free build_diagnostics only for advisor (never advise(), PITFALL 7)
    - Round scalars / print shapes/keys only — never raw float arrays (Pitfall 4)

key_files:
  modified:
    - paper/code/gen_snippets.py (SNIPPETS extended from 1 to 14 entries)
    - paper/sections/capabilities.tex (complete: 14 subsections + \input per family)
  created:
    - paper/snippets/basis.tex
    - paper/snippets/depth.tex
    - paper/snippets/fpca.tex
    - paper/snippets/clustering.tex
    - paper/snippets/classification.tex
    - paper/snippets/regression.tex
    - paper/snippets/fts.tex
    - paper/snippets/spm.tex
    - paper/snippets/tolerance.tex
    - paper/snippets/metric.tex
    - paper/snippets/alignment.tex
    - paper/snippets/advisor_diag.tex
    - paper/snippets/sklearn.tex

decisions:
  - Use Fdata.depth(method="fraiman_muniz") over module-level fraiman_muniz_1d — cleaner and avoids the contiguous-float64 GOTCHA
  - Metric family represented by lp_self_1d + dtw_self_1d; frechet_mean/density_fda mentioned in prose per RESEARCH note (plumbing-heavy, no clean one-liner)
  - FoF regression mentioned in prose under the regression subsection (SoF is the runnable representative — no natural functional response in docs/data/)
  - advisor_diag uses build_diagnostics only (LLM-free, offline, deterministic); advise() shown in prose
  - sklearn subsection placed after advisor_diag (14th family) — natural flow: provenance -> estimator layer
  - density/Frechet prose note references Table~\ref{tab:comparison} per the research recommendation

metrics:
  duration_minutes: 5
  completed: 2026-09-09T06:11:38Z
  tasks_completed: 3
  commits: 3

actuals:
  tokens: 22000
  tasks: 3
  commits: 3
---

# Phase 88 Plan 02: Capability Tour Snippets + capabilities.tex Summary

13 additional family snippets added to gen_snippets.py (basis, depth, fpca+PACE, clustering, classification, regression, fts, spm, tolerance, metric, alignment, advisor_diag, sklearn); all 14 families byte-stable and drift-gate clean; capabilities.tex completed as a breadth-first walk with per-family prose + \input resolving to committed fragments.

## What Was Built

### Task 1: Core-Family Snippets (basis, depth, fpca, clustering, classification, regression)

Six new entries appended to `paper/code/gen_snippets.py` SNIPPETS, each using the verified call shapes from RESEARCH.md:

- **basis**: `fdata_to_basis_1d(X[:5], ARG, n_basis=8, basis_type="bspline")` returns a `(coefs, nbasis)` tuple (unpacked); `smooth_basis_gcv` returns a dict — both shapes demonstrated. Output: `coefficients shape: (5, 8) | n_basis: 8` / `fitted shape: (5, 31)`.
- **depth**: `Fdata.depth(method="fraiman_muniz")` (safe over module-level call); `outliers.muod(X)` (no argvals). Output: `depths shape: (93,) | most central obs: 43` / `shape outliers: [41, 55, 70]`.
- **fpca**: Dense `fd.to_pc(n_comp=3)` + sparse/irregular PACE path with `irreg_fdata_from_lists` and `pace_fpca(irreg, ncomp=2)`. This doubles as the MANU-05 irregular-representation snippet. Output: `FPCA scores shape: (93, 3) | singular values: [227.54, 93.02, 43.73]` / `PACE scores shape: (30, 2) | ncomp: 2`.
- **clustering**: `kmeans_fd(X, ARG, k=3, seed=42)` — prints `np.bincount(km["cluster"]).tolist()` + `km["converged"]` (not the float `tot_withinss`).
- **classification**: phoneme.csv; int64 ndarray labels via dict lookup; `fclassif_knn(Xp[:100], y[:100], ncomp=3, k=5)`. Output: `accuracy: 0.9`.
- **regression**: tecator.csv; `fregre_lm(Xt, yfat, n_comp=5)` SoF; Output: `R^2: 0.9287`.

All six byte-stable across re-runs; `gen_snippets.py --check` passes clean.

### Task 2: Remaining-Family Snippets (fts, spm, tolerance, metric, alignment, advisor_diag, sklearn)

Seven more entries added:

- **fts**: `ftsm_forecast(Xfts, ARGd, h=3, ncomp=3)` — raw data + argvals (NOT a fitted model). Canadian weather: `(35, 365)` stations × days. Output: `forecast shape: (3, 365) | h: 3`.
- **spm**: `spm_phase1` + `spm_monitor(p1["mean"], p1["loadings"], ...)` with components unpacked as positional args (not the dict). Output: T2 and SPE alarm counts as ints.
- **tolerance**: `fpca_tolerance_band(X, ncomp=3, nb=200, coverage=0.95, seed=42)` — no argvals, no alpha kwarg. Output: `tolerance keys: ['upper', 'lower', 'center', 'half_width'] | band width shape: (31,)`.
- **metric**: `lp_self_1d(X, ARG, p=2.0)` for L2 distance matrix + `dtw_self_1d(X[:10])` (no argvals) with rounded DTW scalar. Output: `L2 distance matrix shape: (93, 93)` / `DTW[0,1]: 1813.09`.
- **alignment**: `karcher_mean(X[:10], ARG)` (10-obs subset for speed). Output: karcher keys + `converged` + `aligned shape: (10, 31)`.
- **advisor_diag**: `build_diagnostics(pc, "fpca", argvals=ARG)` LLM-free; `cumulative_variance_explained` printed rounded. Output: `[0.831, 0.969, 1.0]`. No `advise()` call.
- **sklearn**: `FPCATransformer(n_components=5)` from `fdars.sklearn._skeletons`; `Pipeline + RidgeCV + cross_val_score`; rounded mean R². Output: `mean R^2 (5-fold): 0.784`.

Full 14-snippet set byte-stable; `gen_snippets.py --check` passes clean.

### Task 3: capabilities.tex — Breadth-First Family Walk

`paper/sections/capabilities.tex` completed with 14 subsections plus intro paragraph:

- Intro cites `\npubliccallables`, `\nsubmodules`, `\ncoverage`, and `Table~\ref{tab:comparison}`.
- Each family subsection: 2–4 sentences of accurate, under-claiming prose + `\input{snippets/<family>}`.
- Family order: represent → basis → depth → fpca → clustering → classification → regression → fts → spm → tolerance → metric → alignment → advisor_diag → sklearn.
- Density/Fréchet mentioned in prose under the metric subsection (citing comparison table); no fabricated snippet.
- FoF regression mentioned in prose under the regression subsection (SoF is the runnable representative).
- `\nsklearnestimators{}` macro used for sklearn estimator count (machine-derived, distinct from `\ncoverage`).
- No hardcoded count integers, no placeholder text, no timestamp.
- All 14 `\input` paths resolve to committed `paper/snippets/*.tex` fragments.

## Deviations from Plan

None — plan executed exactly as written. Every signature gotcha from RESEARCH.md was honoured without fallback:
- Pitfall 2 (float64/int64 arrays): applied throughout.
- Pitfall 3 (non-obvious signatures): spm_monitor unpacked, ftsm_forecast raw data, fclassif_knn int64 ndarray, fpca_tolerance_band no argvals/alpha, FPCATransformer n_components.
- Pitfall 4 (float drift): shapes/keys/rounded scalars throughout; no raw float arrays printed.
- Pitfall 7 (advisor advise()): build_diagnostics only; advise() mentioned in prose.

## Known Stubs

None in this plan. All snippet files are complete, machine-generated, and non-stub. The capabilities.tex section is fully authored.

Previously deferred stubs from Plan 88-01 (abstract.tex, advisor.tex, conclusion.tex) remain and are tracked in 88-01-SUMMARY.md.

## Self-Check: PASSED

- `paper/code/gen_snippets.py`: FOUND (extended to 14 entries)
- `paper/snippets/basis.tex`: FOUND
- `paper/snippets/depth.tex`: FOUND
- `paper/snippets/fpca.tex`: FOUND (contains "PACE scores" output)
- `paper/snippets/clustering.tex`: FOUND
- `paper/snippets/classification.tex`: FOUND (contains "accuracy" output)
- `paper/snippets/regression.tex`: FOUND
- `paper/snippets/fts.tex`: FOUND (contains "forecast" output)
- `paper/snippets/spm.tex`: FOUND
- `paper/snippets/tolerance.tex`: FOUND
- `paper/snippets/metric.tex`: FOUND
- `paper/snippets/alignment.tex`: FOUND
- `paper/snippets/advisor_diag.tex`: FOUND (build_diagnostics, no advise())
- `paper/snippets/sklearn.tex`: FOUND (FPCATransformer, n_components)
- `paper/sections/capabilities.tex`: FOUND (all 13 \input families present, macros cited, no hardcoded counts)
- `98c17b8` (core-family snippets): FOUND
- `e04f2f9` (remaining-family snippets): FOUND
- `8eeef73` (capabilities.tex): FOUND
- `gen_snippets.py --check` exits 0 on clean repo: VERIFIED
- All 14 fragment files byte-stable on consecutive re-runs: VERIFIED
- All `\input` paths resolve to committed `.tex` files: VERIFIED
