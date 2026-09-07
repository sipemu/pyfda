---
phase: 81-curation-paper-registry
reviewed: 2026-09-07T00:00:00Z
depth: standard
files_reviewed: 2
files_reviewed_list:
  - python/fdars/_references_map.json
  - tests/test_guard_sync_version_independent.py
findings:
  critical: 0
  warning: 0
  info: 0
  total: 0
status: clean
iteration: 2
---

# Phase 81: Code Review Report (Re-review — Iteration 2)

**Reviewed:** 2026-09-07
**Depth:** standard
**Files Reviewed:** 2
**Iteration:** 2 (post-fix re-review; overwrites iteration 1)
**Status:** clean

## Summary

Re-review of Phase 81 after all four prior findings (CR-01 + WR-01 + WR-02 + WR-03) were addressed in commit 2730350. All fixes verified correct by direct JSON inspection and independent Python computation. Test suite passes 10/10. No new issues introduced by the edits.

All reviewed files meet quality standards. No issues found.

---

## Prior Findings — Verification Results

### CR-01: outliergram wrong attribution — RESOLVED

`callable_index["outliers.outliergram"]` now resolves to `["arribas_gil_romo_2014"]`.
`sun_genton_2011.callables` contains only `["depth.functional_boxplot"]` — outliergram absent.
`arribas_gil_romo_2014` is a well-formed new entry: `curated:false`, DOI `10.1093/biostatistics/kxu006`, URL `https://academic.oup.com/biostatistics/article/15/4/603/269095` (domain `academic.oup.com` is in `_ALLOWED_DOMAINS`). GATE-05 A holds.

### WR-01: soft-DTW divergence wrong primary — RESOLVED

`callable_index["metric.soft_dtw_div_self_1d"]` and `callable_index["metric.soft_dtw_div_cross_1d"]` both resolve to `["blondel_et_al_2021"]`.
`cuturi_blondel_2017.callables` retains only `["metric.soft_dtw_self_1d", "metric.soft_dtw_cross_1d"]` and remains `curated:true`.
`blondel_et_al_2021` is a well-formed new entry: `curated:false`, URL `https://arxiv.org/abs/2201.12484` (domain `arxiv.org` already in `_ALLOWED_DOMAINS`). GATE-05 A holds.

### WR-02: align_cluster_fd single curated:true force-pick — RESOLVED

`callable_index["clustering.align_cluster_fd"]` resolves to `["_uncurated_align_cluster_fd_2026-09"]`.
`_uncurated_align_cluster_fd_2026-09` is a new `curated:false` sentinel with a detailed contest note.
`srivastava_et_al_2011.callables` contains its 10 genuine alignment callables only — `clustering.align_cluster_fd` absent. GATE-05 A holds.

### WR-03: dabo_gijbels_2010 missing doi key — RESOLVED

`dabo_gijbels_2010` now carries `"doi": ""` — key present, empty value, consistent with other unconfirmed entries (`nadaraya_watson_1964`, `cuturi_blondel_2017`). Allowed by GATE-05 C for `curated:false` entries.

---

## GATE-05 Invariant Checks (verified independently)

| Gate | Description | Result |
|------|-------------|--------|
| GATE-05 A | `frozenset(callable_index.keys()) == frozenset(union of papers[*].callables)` | PASS — 243 == 243, empty symmetric diff |
| GATE-05 B | every `callable_index` key resolves in `_capability_map.json` | PASS (all 10 tests green) |
| GATE-05 C | DOI regex + URL domain allowlist structural gate | PASS — new entries' domains (`arxiv.org`, `academic.oup.com`) already in `_ALLOWED_DOMAINS` |
| CURATE-04 | anti-feature families absent from `callable_index` | PASS — `spm.mfpca` present as sole spm exception |
| Coverage | denominator derived from live `_capability_map.json` (= 437) | PASS — numerator in `[0, 437]` |

---

## Registry Statistics (post-fix)

- Papers: 57 (was 54 — added `arribas_gil_romo_2014`, `blondel_et_al_2021`, `_uncurated_align_cluster_fd_2026-09`)
- `curated:true` papers: 6 (unchanged: `fraiman_muniz_2001`, `lopez_pintado_romo_2009`, `srivastava_et_al_2011`, `ramsay_dalzell_1991`, `eilers_marx_1996`, `cuturi_blondel_2017`)
- `callable_index` entries: 243 (unchanged — same callable surface, corrected attributions)

## Test Run

```
tests/test_guard_sync_version_independent.py ..........  [100%]
10 passed in 0.74s
```

---

_Reviewed: 2026-09-07_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
_Iteration: 2 (post-fix re-review)_
