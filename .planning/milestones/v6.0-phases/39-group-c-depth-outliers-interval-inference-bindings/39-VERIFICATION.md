---
phase: 39-group-c-depth-outliers-interval-inference-bindings
verified: 2026-08-21T11:00:00Z
status: passed
score: 9/9 must-haves verified
behavior_unverified: 0
overrides_applied: 0
re_verification: false
---

# Phase 39: Group C — Depth / Outliers / Interval-Inference Bindings Verification Report

**Phase Goal:** Users gain 9 new functional-depth methods, 4 functional-outlier detectors, and 3 interval-wise tests — extending `fdars.depth`, `fdars.outliers`, and `fdars.inference` — all deterministic offline and layout-correct.
**Verified:** 2026-08-21T11:00:00Z
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `fdars.depth.functional_depth(data, method=X)` accepts all 9 new DepthMethod tokens and returns finite `(n,)` ndarray for each — DEPTH-03 | VERIFIED | Live run: all 9 tokens (hypograph_index, modified_hypograph_index, epigraph_index, half_region, modified_half_region, extremal, extreme_rank_length, l_infinity, total_variation) return `(10,)` finite arrays; 9 parametrized tests green |
| 2 | `fdars.depth.functional_boxplot(data, method=X)` accepts the 9 new tokens and returns 7-key dict — DEPTH-03 | VERIFIED | Live run: `total_variation`, `hypograph_index`, `extremal` each return exactly the 7 expected keys; `TestFunctionalBoxplotNewMethods` (3 parametrized cases) green |
| 3 | Unknown method string raises ValueError listing all 13 supported methods — DEPTH-03 | VERIFIED | Live run: `bad_method` raises ValueError with message containing all 9 new tokens and phrase "13 supported methods"; `test_unknown_method_lists_new_tokens` and `test_unknown_method_boxplot_lists_new_tokens` green |
| 4 | No signature change to `functional_depth`/`functional_boxplot`; 9 new arms are parameter-free — DEPTH-03 | VERIFIED | Rust source at `src/depth_mod.rs:519-531` and `:587-604`: signatures unchanged; new arms match existing function signatures; no `.unwrap()`/`.expect()` added |
| 5 | `fdars.outliers.tvdmss`/`muod`/`sequential_transform_outliers`/`depthgram` each return dicts with index sets as `list[int]` + 1-D numpy scores; `transforms` string-dispatch with ValueError wildcard; no seed kwarg and no argvals; degenerate inputs raise ValueError — OUTL-01..04 | VERIFIED | Live run: all 4 detectors return correct dict shapes; invalid transform `'bad'` raises `ValueError("transform must be one of 't0', 't1', 't2', 'd1', 'd2', got 'bad'")`; `tvdmss` n=2 and `depthgram` n=1 both raise ValueError; 4 test classes (TestTvdMss/TestMuod/TestSeqTransform/TestDepthgram) green including degenerate tests |
| 6 | All 4 outlier detectors registered in `outliers_mod::register()`, `depth_method_from_str` reused via `pub(crate)`, no `.unwrap()`/`.expect()` — OUTL-01..04 | VERIFIED | `src/outliers_mod.rs:497-506`: all 4 in register(); `use crate::depth_mod::depth_method_from_str` at line 4; grep for `.unwrap()`/`.expect()` in outliers_mod.rs returns empty |
| 7 | `fdars.inference.itp_one_pop`/`itp_two_pop`/`itp_flm` return 5-key ItpResult dict with `adjusted_pvalues`/`raw_pvalues` as 1-D arrays (len==n_basis), `basis_type` string, `n_basis`/`n_perm` ints; `basis_type` dispatches bspline/fourier with ValueError wildcard; invalid basis raises ValueError; `itp_flm` re-fits internally — ITP-01..03 | VERIFIED | Live run: `itp_one_pop` returns `{'adjusted_pvalues': (6,), 'raw_pvalues': (6,), 'basis_type': 'bspline', 'n_basis': 6, 'n_perm': 49}`; fourier round-trips; `basis_type='bad'` raises `ValueError("basis_type must be 'bspline' or 'fourier', got 'bad'")`; all 3 TestItp* classes (12 tests) green |
| 8 | `seed=None` resolves to 0 (byte-identical); `itp_result_to_pydict` distinct from `test_result_to_pydict`; all fallible calls via `to_pyresult()` — ITP-04 | VERIFIED | Live run: `itp_two_pop(..., seed=None)` byte-equals `itp_two_pop(..., seed=0)` on identical inputs; both `fn itp_result_to_pydict` and `fn test_result_to_pydict` exist at distinct lines in `inference_mod.rs`; no `.unwrap()`/`.expect()` in new code |
| 9 | Full suite 681 passed / 4 skipped / 0 failed; `cargo fmt --check` + `cargo clippy -- -D warnings` clean (confirmed by REVIEW-FIX.md); all 5 code-review findings (WR-01, WR-02, IN-01, IN-02, IN-03) addressed — phase gate | VERIFIED | Live run of `pytest tests/ -q`: 681 passed, 4 skipped, 0 failed; REVIEW-FIX.md confirms commit f852db3 added all 5 missing tests; grep for `.unwrap()`/`.expect()` across all 3 new modules returns empty |

**Score:** 9/9 truths verified (0 present, behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `src/depth_mod.rs` | Extended `depth_method_from_str` with 9 new arms + rewritten wildcard error; `pub(crate)` visibility | VERIFIED | 9 new arms at lines 428-436; wildcard at lines 437-443 lists all 13; `pub(crate)` at line 414 |
| `src/outliers_mod.rs` | 4 new `#[pyfunction]`s + 4 `*_to_pydict` converters + `seq_transform_from_str` dispatcher + variant-str helper | VERIFIED | All present; `tvdmss` line 213, `muod` line 290, `sequential_transform_outliers` line 399, `depthgram` line 482; converters at lines 165, 237, 342, 429 |
| `src/inference_mod.rs` | 3 new `#[pyfunction]`s + `itp_result_to_pydict` + `basis_type_from_str`/`basis_type_variant_str` | VERIFIED | All present; `itp_one_pop` line 639, `itp_two_pop` line 709, `itp_flm` line 773; `itp_result_to_pydict` line 583; `basis_type_from_str` line 564; `basis_type_variant_str` line 550 |
| `tests/test_depth.py` | `TestFunctionalDepthNewVariants` + `TestFunctionalBoxplotNewMethods` + extended invalid-method coverage | VERIFIED | Both classes present; 9-parametrized `test_new_variant_finite`; 3 boxplot cases; invalid-method tests check for new token in error message |
| `tests/test_outliers.py` | `TestTvdMss`, `TestMuod`, `TestSeqTransform`, `TestDepthgram` incl. degenerate tests | VERIFIED | All 4 classes present with 10 tests total; WR-01 degenerate tests (`test_tvdmss_degenerate_n_too_small`, `test_depthgram_degenerate_n_too_small`) added via review fix |
| `tests/test_inference.py` | `TestItpOnePop`, `TestItpTwoPop`, `TestItpFlm` with mu0/seed/determinism coverage | VERIFIED | All 3 classes present with 12 ITP tests; WR-02 `test_itp_two_pop_seed_none_equals_seed_zero`; IN-01 `test_itp_one_pop_with_mu0`; IN-02 determinism tests for one_pop and flm — all added via review fix |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `depth_mod.rs::depth_method_from_str` | 9 new `DepthMethod` variants | 9 new match arms | VERIFIED | Arms 428-436 in `depth_mod.rs` |
| `outliers_mod.rs::sequential_transform_outliers` | `depth_method_from_str` | `use crate::depth_mod::depth_method_from_str` + line 411 call | VERIFIED | Import at line 4; usage at line 411 |
| `outliers_mod.rs::register()` | 4 new `#[pyfunction]`s | `m.add_function(wrap_pyfunction!(...))` | VERIFIED | Lines 502-505 in `register()` |
| `inference_mod.rs::itp_one_pop/itp_two_pop/itp_flm` | `itp_result_to_pydict` (distinct from `test_result_to_pydict`) | Call at end of each fn | VERIFIED | All 3 fns call `itp_result_to_pydict(py, r)` at their return; `test_result_to_pydict` untouched at line 32 |
| `inference_mod.rs::register()` | 3 ITP `#[pyfunction]`s | `m.add_function(wrap_pyfunction!(...))` | VERIFIED | Lines 807-809 in `register()` |

### Data-Flow Trace (Level 4)

All bindings follow the established fdars pattern: `PyReadonlyArray2` → `numpy2d_to_fdmatrix()` → `fdars_core::<module>::<fn>()` → `to_pyresult()` → converter → `PyDict`. No static returns, no hardcoded literals, no mocks. Data flows from real fdars-core computation in all cases.

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|---------------|--------|-------------------|--------|
| `tvdmss` result dict | `magnitude_outliers`, `shape_outliers`, `tvd`, `mss` | `fdars_core::outliers::tvdmss(&mat, config)` | Yes — live outlier detection | FLOWING |
| `muod` result dict | 3 index sets + 3 score vectors | `fdars_core::outliers::muod(&mat, config)` | Yes | FLOWING |
| `sequential_transform_outliers` result dict | `per_transform_outliers`, `union_outliers` | `fdars_core::outliers::sequential_transform_outliers(&mat, &seq, config)` | Yes | FLOWING |
| `depthgram` result dict | 10 keys (8 vectors + 2 index sets) | `fdars_core::outliers::depthgram(&mat, config)` | Yes | FLOWING |
| `itp_one_pop`/`itp_two_pop`/`itp_flm` result dict | `adjusted_pvalues`, `raw_pvalues`, `basis_type`, `n_basis`, `n_perm` | `fdars_core::inference::itp_{one_pop,two_pop,flm}(...)` | Yes — live permutation test | FLOWING |
| `functional_depth` new tokens | 9 new arms | `fdars_core::depth::functional_depth(&d, DepthMethod::*)` | Yes | FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| All 9 new depth tokens return finite `(10,)` arrays | Python: loop over 9 tokens, call `functional_depth`, assert shape+finite | All 9 pass | PASS |
| Invalid method raises ValueError listing all 13 | Python: `functional_depth(data, method='bad_method')` | ValueError with "13 supported methods" and "total_variation" | PASS |
| `tvdmss` returns 4-key dict with `list[int]` + `(n,)` arrays | Python smoke run | `{'tvd','shape_outliers','magnitude_outliers','mss'}` — correct types | PASS |
| `muod` returns 6-key dict | Python smoke run | `{'shape_outliers','magnitude_outliers','amplitude_outliers','shape_index','magnitude_index','amplitude_index'}` | PASS |
| `sequential_transform_outliers` returns `per_transform_outliers` as `list[dict]` | Python smoke run with `["t0","t1","d1"]` | `[{'transform':'t0','outliers':[...]}, ...]` — correct | PASS |
| `depthgram` returns 10-key dict | Python smoke run | All 10 keys present, 8 arrays shape `(15,)`, 2 `list[int]` | PASS |
| `itp_one_pop` returns 5-key ItpResult dict, p-values in [0,1] | Python smoke run | `adjusted_pvalues.shape == (6,)`, all in [0,1] | PASS |
| `itp_two_pop` seed=None == seed=0 | Python: compare `seed=None` vs `seed=0` on identical inputs | `np.array_equal` True | PASS |
| `itp_flm` fourier basis round-trips | Python: call with `basis_type="fourier"`, check result | `result["basis_type"] == "fourier"` | PASS |
| Full test suite | `pytest tests/ -q` | 681 passed / 4 skipped / 0 failed | PASS |
| Phase 39 test files specifically | `pytest tests/test_depth.py tests/test_outliers.py tests/test_inference.py -q` | 136 passed / 0 failed | PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|---------|
| DEPTH-03 | 39-01-PLAN.md | 9 new DepthMethod variants in `functional_depth`/`functional_boxplot`, 13-token error message | SATISFIED | 9 arms in `depth_method_from_str`; all 9 tokens tested; error lists all 13 |
| OUTL-01 | 39-02-PLAN.md | `fdars.outliers.tvdmss` → 4-key dict | SATISFIED | `tvdmss` registered, correct keys, `list[int]` index sets, degenerate ValueError |
| OUTL-02 | 39-02-PLAN.md | `fdars.outliers.muod` → 6-key dict | SATISFIED | `muod` registered, correct keys, degenerate ValueError |
| OUTL-03 | 39-02-PLAN.md | `fdars.outliers.sequential_transform_outliers` → dict with `per_transform_outliers` as `list[dict]`, SeqTransform dispatch | SATISFIED | `sequential_transform_outliers` registered; invalid transform raises ValueError; depth_method reuse confirmed |
| OUTL-04 | 39-02-PLAN.md | `fdars.outliers.depthgram` → 10-key dict; all 4 detectors deterministic, no seed | SATISFIED | `depthgram` registered; 10-key dict verified; no seed in any outlier fn; degenerate ValueError |
| ITP-01 | 39-03-PLAN.md | `fdars.inference.itp_one_pop` → ItpResult dict with vector p-values | SATISFIED | `itp_one_pop` registered; 5-key dict; `adjusted_pvalues`/`raw_pvalues` are 1-D arrays |
| ITP-02 | 39-03-PLAN.md | `fdars.inference.itp_two_pop` → ItpResult dict; seed=None determinism | SATISFIED | `itp_two_pop` registered; seed=None==seed=0 proven |
| ITP-03 | 39-03-PLAN.md | `fdars.inference.itp_flm` → ItpResult dict; basis dispatch; internal re-fit | SATISFIED | `itp_flm` registered; fourier round-trips; raw data/response in, no handle |
| ITP-04 | 39-03-PLAN.md | All 3 ITP fns via `itp_result_to_pydict` (distinct from `test_result_to_pydict`); fallible via `to_pyresult()`; degenerate ValueError | SATISFIED | Both converters exist at distinct fn definitions; `nbasis=1` raises ValueError; no `.unwrap()`/`.expect()` |

### Anti-Patterns Found

Scanned `src/depth_mod.rs`, `src/outliers_mod.rs`, and `src/inference_mod.rs` for unsafe patterns in new code:

| File | Pattern | Severity | Impact |
|------|---------|----------|--------|
| All 3 modules | `.unwrap()`/`.expect()` | None found | Safe — all new code routes through `to_pyresult()` |
| All 3 modules | TBD/FIXME/XXX/PLACEHOLDER | None found | Clean |
| `outliers_mod.rs` | `_ => "unknown"` in `seq_transform_variant_str` | Info | Required wildcard for `#[non_exhaustive]` SeqTransform; not a runtime concern — unknown variants produce a Python `"unknown"` string token, which a caller can detect |
| `inference_mod.rs` | `_ => "unknown"` in `basis_type_variant_str` | Info | Same pattern; required for `#[non_exhaustive]` ProjectionBasisType |

No blockers or warnings found.

### ROADMAP Success Criteria Mapping

| SC | Criterion | Status | Evidence |
|----|-----------|--------|---------|
| SC-1 | `functional_depth`/`functional_boxplot` accept 9 new DepthMethod variants (13 total); wildcard error lists all | PASS | Live: all 9 tokens dispatch; error message verified |
| SC-2 | All 4 outlier detectors return `list[int]` index sets + scores; `transforms` SeqTransform dispatch with ValueError; any random component takes `seed=None` → fixed default | PASS | Live: all 4 return correct types; invalid transform raises ValueError; no seed (deterministic) |
| SC-3 | All 3 ITP fns return ItpResult dict with vector p-values + `basis_type` string dispatch with ValueError; `itp_flm` re-fits internally | PASS | Live: all 3 fns return 5-key dicts; basis dispatch verified; `itp_flm` accepts raw data/response |
| SC-4 | 3 ITP fns registered via NEW `itp_result_to_pydict` (distinct from `test_result_to_pydict`); all fallible via `to_pyresult()`; degenerate ValueError | PASS | Both converters confirmed at separate line numbers; no `.unwrap()`; degenerate input tests pass |

### Human Verification Required

None. All must-haves are fully verifiable via automated checks and live code inspection. The behavioral tests (determinism, degenerate guards, type contracts) are all exercised by the test suite.

### Gaps Summary

None. All 9 must-haves are verified. All 9 requirements (DEPTH-03, OUTL-01..04, ITP-01..04) are satisfied. The review's 5 findings (2 warnings, 3 info) were all addressed in commit f852db3 before submission for verification. Full suite: 681 passed / 4 skipped / 0 failed.

---

_Verified: 2026-08-21T11:00:00Z_
_Verifier: Claude (gsd-verifier)_
