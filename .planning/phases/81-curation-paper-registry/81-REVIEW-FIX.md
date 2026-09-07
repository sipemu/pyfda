---
phase: 81-curation-paper-registry
fixed_at: 2026-09-07T00:00:00Z
review_path: .planning/phases/81-curation-paper-registry/81-REVIEW.md
iteration: 1
findings_in_scope: 4
fixed: 4
skipped: 0
status: all_fixed
---

# Phase 81: Code Review Fix Report

**Fixed at:** 2026-09-07
**Source review:** `.planning/phases/81-curation-paper-registry/81-REVIEW.md`
**Iteration:** 1

**Summary:**
- Findings in scope: 4 (1 Critical + 3 Warning; 2 Info findings out of scope per `fix_scope: critical_warning`)
- Fixed: 4
- Skipped: 0

## Fixed Issues

### CR-01: Wrong paper attributed to `outliers.outliergram`

**Files modified:** `python/fdars/_references_map.json`
**Commit:** 2730350
**Applied fix:**
- Removed `outliers.outliergram` from `sun_genton_2011.callables` (Sun & Genton introduced only the functional boxplot)
- Updated `sun_genton_2011.notes` to clarify it covers the functional boxplot only, explicitly noting the outliergram belongs to `arribas_gil_romo_2014`
- Added new paper entry `arribas_gil_romo_2014` (Arribas-Gil & Romo 2014, Biostatistics, DOI `10.1093/biostatistics/kxu006`, `curated:false` pending Phase-84 verify) with `callables: ["outliers.outliergram"]`
- Updated `callable_index["outliers.outliergram"]` from `["sun_genton_2011"]` to `["arribas_gil_romo_2014"]`
- GATE-05 A invariant maintained: 243 callables in papers == 243 in callable_index

### WR-01: `metric.soft_dtw_div_*` callables attributed to wrong primary paper

**Files modified:** `python/fdars/_references_map.json`
**Commit:** 2730350
**Applied fix:**
- Removed `metric.soft_dtw_div_self_1d` and `metric.soft_dtw_div_cross_1d` from `cuturi_blondel_2017.callables`; that entry now covers only the non-divergence soft-DTW callables (`soft_dtw_self_1d`, `soft_dtw_cross_1d`), remaining `curated:true`
- Added new paper entry `blondel_et_al_2021` (Blondel, Mensch & Vert, AISTATS 2021, arXiv:2201.12484, `curated:false`) with `callables: ["metric.soft_dtw_div_self_1d", "metric.soft_dtw_div_cross_1d"]`
- Updated `callable_index` for both div callables to point to `["blondel_et_al_2021"]`
- `arxiv.org` was already in `_ALLOWED_DOMAINS` in the test file; no test change needed
- GATE-05 A invariant maintained

### WR-02: `clustering.align_cluster_fd` was a single curated:true pick for a contested callable

**Files modified:** `python/fdars/_references_map.json`
**Commit:** 2730350
**Applied fix:**
- Removed `clustering.align_cluster_fd` from `srivastava_et_al_2011.callables` (that entry remains `curated:true` for the 10 alignment callables that genuinely originate there)
- Added new `_uncurated_align_cluster_fd_2026-09` sentinel paper entry with `callables: ["clustering.align_cluster_fd"]`, `curated:false`, and a `notes` field explaining the contest: primary candidate is Srivastava et al. 2011 (fdars-core module doc cites arXiv:1103.3817) but the clustering callable has no standalone unambiguous primary paper
- Updated `callable_index["clustering.align_cluster_fd"]` to `["_uncurated_align_cluster_fd_2026-09"]`
- The callable_index row now points to a `curated:false` entry, satisfying the milestone's no-force-pick rule
- GATE-05 A invariant maintained

### WR-03: `dabo_gijbels_2010` missing `doi` key entirely

**Files modified:** `python/fdars/_references_map.json`
**Commit:** 2730350
**Applied fix:**
- Added `"doi": ""` field to `dabo_gijbels_2010` paper entry for schema consistency
- No DOI fabricated — empty string matches the pattern of other unconfirmed entries (`nadaraya_watson_1964`, `cuturi_blondel_2017`)
- GATE-05 C passes: empty doi is skipped for `curated:false` entries

## Skipped Issues

None — all 4 in-scope findings were fixed.

## Final Test Results

Verification ran in the main checkout (workflow.use_worktrees=false).

```
tests/test_guard_sync_version_independent.py ..........  [100%]
10 passed in 0.72s
```

All 10 guard tests pass (Python 3.14.7):
- GATE-05 A: `frozenset(callable_index.keys()) == frozenset(union of papers[*].callables)` — PASS (243 == 243)
- GATE-05 B: all 243 callable_index keys resolve in `_capability_map.json` — PASS
- GATE-05 C: DOI regex + URL well-formedness — PASS
- Coverage fraction: printed at test runtime
- Anti-feature absence: PASS

## Post-Fix Registry Statistics

- Papers: 57 (was 54 — added 3 new entries: `arribas_gil_romo_2014`, `blondel_et_al_2021`, `_uncurated_align_cluster_fd_2026-09`)
- curated:true papers: 6 (unchanged — `fraiman_muniz_2001`, `lopez_pintado_romo_2009`, `srivastava_et_al_2011`, `ramsay_dalzell_1991`, `eilers_marx_1996`, `cuturi_blondel_2017`)
- callable_index entries: 243 (unchanged — same callables, correct attributions)
- GATE-05 A invariant: holds (243 == 243, 0 mismatches)

---

_Fixed: 2026-09-07_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_
