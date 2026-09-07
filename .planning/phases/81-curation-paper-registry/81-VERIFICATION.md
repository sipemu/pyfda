---
phase: 81-curation-paper-registry
verified: 2026-09-07T12:00:00Z
status: passed
score: 5/5 must-haves verified
behavior_unverified: 0
overrides_applied: 0
---

# Phase 81: Curation Paper Registry Verification Report

**Phase Goal:** `_references_map.json` carries author-verified, sub-method-accurate paper provenance + cross-language pointers across the table-stakes and differentiator families, with anti-feature families wired to the curated:false sentinel and coverage reported honestly as N/437.
**Verified:** 2026-09-07
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Paper-level entries populate all required families (CURATE-01) | VERIFIED | 57 papers across 22 module families; all 17 CURATE-01 families present in callable_index |
| 2 | callable_index is sub-method-accurate; contested cases are curated:false-with-notes or co-primary, not force-picked (CURATE-02) | VERIFIED | band_1d vs modified_band_1d each map to lopez_pintado_romo_2009; fraiman_muniz vs band depth are separate papers; oneway_anova_vstat and align_cluster_fd are curated:false with detailed contested notes; elastic_changepoint resolved to tucker_yarger_2024 |
| 3 | Cross-language pointers with package+function+url+confidence land per covered paper; honest gaps recorded where no implementation exists (CURATE-03) | VERIFIED | 24 papers have cross_language entries; petersen_muller_2019 records honest gap in notes; srivastava_et_al_2011 has R/Python/Matlab; guard validates package/function/url/confidence presence; Matlab confidence:low used correctly |
| 4 | Six anti-feature families absent from callable_index; spm.mfpca is the sole spm exception (CURATE-04) | VERIFIED | test_references_map_anti_feature_families_absent PASSES; explain/metrics/scoring/conformal/seasonal entirely absent; spm.* absent except spm.mfpca; depth.functional_depth absent |
| 5 | Coverage emitted as N/437 with denominator derived from live _capability_map.json, numerator = curated:true-backed callables only (CURATE-05) | VERIFIED | test_references_map_coverage_fraction PASSES and emits COVERAGE: 28/437 (6.4%); denominator computed as sum(len(v) for v in cap_data.values()) not hardcoded; drift tripwire asserts 437 |

**Score:** 5/5 truths verified

### Note on Coverage Numerator (28 vs 31 in SUMMARY)

The 81-05 SUMMARY claims 31/437. The live codebase emits 28/437. The discrepancy is explained and correct: the code review (REVIEW.md iteration 2, commit 2730350) fixed three wrong attributions after the summaries were written:

- WR-01: `metric.soft_dtw_div_self_1d` and `metric.soft_dtw_div_cross_1d` moved from `cuturi_blondel_2017` (curated:true) to `blondel_et_al_2021` (curated:false) — these two callables drop from the curated numerator
- WR-02: `clustering.align_cluster_fd` moved from `srivastava_et_al_2011` (curated:true) to `_uncurated_align_cluster_fd_2026-09` (curated:false) — one callable drops from the curated numerator

The corrected 28/437 is the honest value and is what the live test emits. The SUMMARY's 31/437 is a pre-fix artifact. The live guard test is authoritative.

### Deferred Items

None — all five CURATE requirements are satisfied in this phase. The Phase 84 GATE-03 blocking human citation review is correctly deferred (human DOI landing-page verification for curated:false → curated:true promotion is explicitly out of scope for Phase 81).

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `python/fdars/_references_map.json` | 57 papers, 243 callable_index entries | VERIFIED | Exists, substantive (2700+ lines), wired via importlib.resources in tests |
| `tests/test_guard_sync_version_independent.py` | 5 new Guard Group 3 tests | VERIFIED | Exists; contains test_references_map_internal_consistency, test_references_map_cross_file_resolution, test_references_map_doi_url_structural_gate, test_references_map_coverage_fraction, test_references_map_anti_feature_families_absent |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| callable_index keys | papers[*].callables | frozenset equality (GATE-05 A) | VERIFIED | 243 == 243, empty symmetric difference — test passes |
| callable_index keys | _capability_map.json | module+callable lookup (GATE-05 B) | VERIFIED | All 243 keys resolve; test passes |
| cross_language[*].url domains | _ALLOWED_DOMAINS frozenset | domain string membership (GATE-05 C) | VERIFIED | 9 new domains added to allowlist; test passes |
| coverage denominator | _capability_map.json live count | sum(len(v) for v in cap_data.values()) | VERIFIED | 437 derived at test-time; not hardcoded |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|---------------|--------|--------------------|--------|
| `_references_map.json` | papers / callable_index | Committed JSON file | Yes — static JSON consumed by guard tests via importlib.resources | FLOWING |
| Guard tests | denominator | _capability_map.json live file | Yes — computed at test-time from live capability map | FLOWING |
| Guard tests | numerator | _references_map.json curated:true entries | Yes — computed from actual paper entries | FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| All 5 Guard Group 3 tests pass | `.venv/bin/python -m pytest tests/test_guard_sync_version_independent.py -v` | 10 passed in 0.72s | PASS |
| Coverage emits N/437 fraction | `.venv/bin/python -m pytest tests/test_guard_sync_version_independent.py -q -s` | COVERAGE: 28/437 callables curated (6.4% of fdars callable surface) | PASS |
| GATE-05 A: callable_index == union(papers[*].callables) | Python check via importlib.resources | 243 == 243, empty symmetric difference | PASS |
| GATE-05 B: all keys resolve in _capability_map.json | Python check | 0 unresolved keys | PASS |
| CURATE-04: anti-feature families absent | Python check | 0 violations; spm.mfpca present | PASS |
| Denominator derived (not hardcoded) | Inspect test source | Uses sum(len(v) for v in cap_data.values()) | PASS |

### Probe Execution

No conventional probe scripts found (this phase uses the guard test suite directly).

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|---------|
| CURATE-01 | 81-01/02/03/04 | Paper-level entries across table-stakes + differentiator families | SATISFIED | All 17 specified families present; 57 papers covering basis/smoothing, functional statistics, depth sub-methods, functional boxplot, FPCA/PACE, FLM/scalar-on-function, Fréchet, density/LQD, elastic/SRSF, shift/landmark, DTW/GAK/soft-DTW, clustering, classification, inference, FTS/DPCA, shapelets, MFPCA/FAMM |
| CURATE-02 | 81-01/02/03/04 | Sub-method-accurate callable_index; contested cases curated:false-with-notes | SATISFIED | band_1d vs modified_band_1d separate papers; FM vs band depth separate; oneway_anova_vstat contested-noted; align_cluster_fd sentinel; elastic_changepoint resolved |
| CURATE-03 | 81-01/02/03/04 | Cross-language pointers (R/Python/Matlab) per covered paper | SATISFIED | 24 papers with cross_language; honest gaps documented in notes; Matlab confidence:low used; GATE-05 C validates URL domains |
| CURATE-04 | 81-05 | Six anti-feature families absent from callable_index | SATISFIED | test_references_map_anti_feature_families_absent PASSES; explain/metrics/scoring/conformal/seasonal fully absent; non-mfpca spm absent; spm.mfpca present as the sole spm exception |
| CURATE-05 | 81-01/05 | Honest N/437 coverage with live-derived denominator; curated:true-only numerator | SATISFIED | test_references_map_coverage_fraction PASSES; emits 28/437; denominator from live _capability_map.json; drift tripwire at 437; no LLM-synthesized entry carries curated:true |

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| None | — | No TBD/FIXME/XXX markers found in modified files | — | — |

No debt markers, no stubs, no hardcoded data that should be dynamic.

### Code Review Status

The phase-level code review (81-REVIEW.md) ran two iterations. Iteration 1 found 4 issues (1 critical, 3 warning):

- **CR-01 (critical):** `outliers.outliergram` was wrongly attributed to `sun_genton_2011` (functional boxplot paper). Fixed: moved to new `arribas_gil_romo_2014` entry.
- **WR-01:** `metric.soft_dtw_div_*` callables attributed to Cuturi & Blondel 2017 (soft-DTW original); correct primary is Blondel et al. 2021 (divergence variant). Fixed: new `blondel_et_al_2021` entry.
- **WR-02:** `clustering.align_cluster_fd` was a single curated:true force-pick violating the contested-attribution rule. Fixed: moved to `_uncurated_align_cluster_fd_2026-09` sentinel.
- **WR-03:** `dabo_gijbels_2010` missing `doi` key. Fixed: `"doi": ""` added.

Iteration 2 is clean (0 findings, all prior findings resolved). All fixes committed in 2730350.

### Gaps Summary

No gaps found. All five CURATE requirements are structurally satisfied:

- The data exists, is structurally valid (57 papers, 243 callable_index entries), and passes all guards.
- Sub-method attribution is accurate; contested cases are handled honestly (curated:false with detailed notes).
- Cross-language pointers are present per covered paper with honest gap notation.
- Anti-feature families are absent from callable_index with a guard enforcing this.
- Coverage is honestly reported at 28/437 (6.4%) with a live-derived denominator — the low coverage fraction reflects strict author-verification discipline, NOT a gap (most entries are curated:false pending Phase 84 GATE-03 human review, which is the intended posture).

The Phase 84 blocking human citation review (GATE-03) will be where entries are promoted from curated:false to curated:true after human verification against DOI landing pages. That is out of scope for Phase 81 and correctly deferred.

---

_Verified: 2026-09-07T12:00:00Z_
_Verifier: Claude (gsd-verifier)_
