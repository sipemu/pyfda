---
phase: 31-group-a-fdars-inference-bindings
verified: 2026-08-17T14:30:00Z
status: passed
score: 15/15
behavior_unverified: 0
overrides_applied: 0
re_verification: false
---

# Phase 31: Group A fdars Inference Bindings — Verification Report

**Phase Goal:** Users can run the full functional-inference surface (two-sample tests, simultaneous confidence bands, FLM post-hoc inference, one-way ANOVA V-statistic) from a new, importable `fdars.inference` submodule with deterministic, reproducible results.
**Verified:** 2026-08-17T14:30:00Z
**Status:** PASSED
**Re-verification:** No — initial verification

---

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `import fdars.inference` succeeds; `from fdars.inference import t_perm_test` succeeds — INFER-09 | VERIFIED | Live: `python -c "import fdars.inference; from fdars.inference import t_perm_test"` exits 0 |
| 2 | All 8 functions importable via both `fdars.inference.<fn>` and `from fdars.inference import <fn>` — INFER-09 | VERIFIED | Live: all 8 imported successfully in one-liner; `callable()` confirmed for each |
| 3 | `t_perm_test(data_a, data_b, argvals, n_perm=999, seed=None)` returns `{statistic, p_value, n_perm}` — INFER-01 | VERIFIED | Live: `set(result.keys()) == {"statistic","p_value","n_perm"}` confirmed; types: `float,float,int` |
| 4 | `f_perm_test(...)` returns the same `{statistic, p_value, n_perm}` dict shape — INFER-02 | VERIFIED | Live: keys confirmed; n_perm round-trip (23→23) asserted; seed determinism confirmed |
| 5 | `two_sample_mean_test(data_a, data_b, argvals, ncomp=5)` returns `{statistic, p_value, n_perm}` with `n_perm==0` — INFER-03 | VERIFIED | Live: `result["n_perm"] == 0` confirmed; no seed parameter exposed; deterministic |
| 6 | `mean_scb(...)` returns `{lower, upper, center, half_width}` where each is a 1-D ndarray of length `m` with all-finite values — INFER-04 | VERIFIED | Live: `set(scb.keys())` confirmed; shape `(m,)` per field; `np.all(np.isfinite(...))` passes; `lower <= center <= upper` ordering invariant passes |
| 7 | `multiplier` selected by string; unknown string raises `ValueError` — INFER-04 | VERIFIED | Live: `mean_scb(..., multiplier="bogus")` raises `ValueError`; `match=multiplier` confirmed by test |
| 8 | `scb_two_sample_test(...)` returns `{statistic, p_value, n_perm}` with `n_perm==0` — INFER-05 | VERIFIED | Live: keys confirmed, `result["n_perm"] == 0` confirmed |
| 9 | `flm_f_test(data, response, n_comp=5)` re-fits `fregre_lm` internally (no handle), returns `{statistic, p_value, n_perm}` — INFER-06 | VERIFIED | Code: `fregre_lm(&mat, &resp, None, n_comp)` in Rust, result passes `&fit` to `flm_f_test`; `FregreLmResult` never crosses boundary; live: keys confirmed |
| 10 | `flm_gof_test(data, response, n_comp=5)` symmetric with `flm_f_test`, returns same dict shape — INFER-07 | VERIFIED | Code: identical re-fit pattern; live: keys confirmed |
| 11 | `oneway_anova_vstat(data, groups, argvals)` accepts 0-indexed `i64` array, returns `{statistic, p_value, n_perm}` with `n_perm==0` — INFER-08 | VERIFIED | Code: `PyReadonlyArray1<i64>` binding + `numpy1d_to_usize_vec`; live: `result["n_perm"] == 0` confirmed |
| 12 | Seed determinism: `seed=None` byte-identical to `seed=0`; two explicit same-seed calls byte-identical — INFER-09 | VERIFIED | Live: `json.dumps(r_none, sort_keys=True) == json.dumps(r_zero, sort_keys=True)` for both `t_perm_test` and `f_perm_test`; explicit same-seed confirmed |
| 13 | Degenerate inputs raise `ValueError`, no panics — INFER-09 | VERIFIED | Live: `n_perm=0` → ValueError; mismatched argvals → ValueError; unknown multiplier → ValueError; single ANOVA group → ValueError; FLM n<3 → ValueError; FLM GoF n<=4 → ValueError |
| 14 | `FregreLmResult` never crosses the Python boundary — INFER-06/07 | VERIFIED | Live: `hasattr(fdars.inference, "FregreLmResult")` is False; code confirms re-fit-internally pattern |
| 15 | Full existing test suite still passes without regressions — phase goal "without breaking existing bindings" | VERIFIED | Live: `pytest -q` → 491 passed, 4 skipped (same 4 as pre-phase baseline) |

**Score:** 15/15 truths verified

---

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `src/inference_mod.rs` | New PyO3 submodule with all 8 bindings | VERIFIED | 549 lines; all 8 `#[pyfunction]`s present; `pub fn register()` registers all 8 |
| `tests/test_inference.py` | 65+ tests covering all 8 functions | VERIFIED | 687 lines; 65 tests pass in 0.38s |
| `.planning/phases/31-group-a-fdars-inference-bindings/31-SIGNATURES.md` | Authoritative signatures for all 8 functions | VERIFIED | File exists; contains `MultiplierDistribution`, `FregreLmResult`, `TestResult`, `ToleranceBand` |
| `src/lib.rs` (modified) | `mod inference_mod` + `register_submodule!(m, "inference", ...)` | VERIFIED | `mod inference_mod` present alphabetically; `register_submodule!(m, "inference", inference_mod::register)` after scoring |
| `python/fdars/__init__.py` (modified) | `"inference"` in `_submodule_names` | VERIFIED | `"inference"` is the last entry in the tuple |

---

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `src/inference_mod.rs` | `fdars._native.inference` | `register_submodule!(m, "inference", inference_mod::register)` in `src/lib.rs` line 60 | VERIFIED | Wiring confirmed in `lib.rs` |
| `fdars._native.inference` | `fdars.inference` (Python import path) | `"inference"` in `_submodule_names` loop in `python/fdars/__init__.py` | VERIFIED | Loop at line 56-61 registers it in `sys.modules["fdars.inference"]` |
| `mean_scb` / `scb_two_sample_test` | `fdars_core::tolerance::MultiplierDistribution` | `multiplier_from_str()` private helper with `_ => PyValueError` wildcard arm | VERIFIED | Code at lines 225-233; wildcard arm mandatory for non-exhaustive enum |
| `flm_f_test` / `flm_gof_test` | `fdars_core::inference::flm_f_test/flm_gof_test` | `fregre_lm(&mat, &resp, None, n_comp)` internal re-fit; `&FregreLmResult` passed to test fn | VERIFIED | Code at lines 419-423, 475-480; `FregreLmResult` stays in Rust |
| `oneway_anova_vstat` groups | `Vec<usize>` | `PyReadonlyArray1<i64>` → `numpy1d_to_usize_vec` | VERIFIED | Code at line 528; float arrays rejected at binding boundary |

---

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|---------------|--------|--------------------|--------|
| `t_perm_test` | `mat_a`, `mat_b`, `av` | `numpy2d_to_fdmatrix`, `numpy1d_to_vec` from caller-supplied numpy arrays | Yes — passes to `fdars_core::inference::t_perm_test` | FLOWING |
| `mean_scb` | `band.lower/.upper/.center/.half_width` | `fdars_core::inference::mean_scb` returns `ToleranceBand`; each field converted via `vec_to_numpy1d` | Yes — real computation, no static fallback | FLOWING |
| `flm_f_test` | `fit` (FregreLmResult) | `fdars_core::scalar_on_function::fregre_lm(&mat, &resp, None, n_comp)` | Yes — real fit; `&fit` passed to `flm_f_test` | FLOWING |
| `oneway_anova_vstat` | `grp` (Vec<usize>) | `numpy1d_to_usize_vec` from caller-supplied `i64` array | Yes — real group labels | FLOWING |

---

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| All 8 functions importable | `python -c "from fdars.inference import t_perm_test, f_perm_test, two_sample_mean_test, mean_scb, scb_two_sample_test, flm_f_test, flm_gof_test, oneway_anova_vstat"` | "all 8 imports ok" | PASS |
| `t_perm_test` seed=None == seed=0 | json.dumps comparison | byte-identical | PASS |
| `f_perm_test` seed determinism | json.dumps comparison, explicit seed | byte-identical | PASS |
| `mean_scb` band shape and finiteness | shape==(m,) per field, np.all(np.isfinite(...)) | all pass | PASS |
| `two_sample_mean_test` n_perm==0 | `result["n_perm"] == 0` | True | PASS |
| `oneway_anova_vstat` n_perm==0 | `result["n_perm"] == 0` | True | PASS |
| All ValueError guards | 6 degenerate input cases | all raised ValueError | PASS |
| Full inference test suite | `pytest tests/test_inference.py -q` | 65 passed in 0.38s | PASS |
| Full regression suite | `pytest -q` | 491 passed, 4 skipped | PASS |

---

### Probe Execution

Step 7c: SKIPPED (no `scripts/*/tests/probe-*.sh` probes declared for this phase).

---

### Requirements Coverage

| Requirement | Phase Plans | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| INFER-01 | 31-01 | `t_perm_test` returns `{statistic, p_value, n_perm}` | SATISFIED | Live: keys confirmed, values are plain Python float/int |
| INFER-02 | 31-01 | `f_perm_test` returns same dict shape | SATISFIED | Live: keys confirmed, seed determinism verified |
| INFER-03 | 31-01 | `two_sample_mean_test` returns dict with n_perm==0, no seed | SATISFIED | Live: n_perm==0 confirmed, no seed param in signature |
| INFER-04 | 31-02 | `mean_scb` returns `{lower,upper,center,half_width}` 1-D arrays with multiplier string dispatch | SATISFIED | Live: 8 tests pass; shape/finite/ordering invariants confirmed |
| INFER-05 | 31-02 | `scb_two_sample_test` returns TestResult dict | SATISFIED | Live: keys confirmed, n_perm==0 confirmed |
| INFER-06 | 31-03 | `flm_f_test` re-fits internally, returns TestResult dict | SATISFIED | Code: internal re-fit pattern verified; live: keys confirmed |
| INFER-07 | 31-03 | `flm_gof_test` symmetric with INFER-06 | SATISFIED | Code: identical re-fit path; live: keys confirmed |
| INFER-08 | 31-03 | `oneway_anova_vstat` accepts i64 groups, returns dict n_perm==0 | SATISFIED | Live: dtype binding verified; n_perm==0 confirmed |
| INFER-09 | 31-01 | Submodule registered; seed=None→0 byte-identical; no unwrap; ValueError for degenerate inputs | SATISFIED | Live: all checks pass; no `.unwrap()` in code (only in doc comment) |

**Note on REQUIREMENTS.md traceability table:** INFER-01, INFER-02, INFER-03, and INFER-09 are still marked `[ ] Pending` in REQUIREMENTS.md and the traceability table. This is a documentation-only omission — the implementations are fully in place and verified above. The executor did not update the requirement checkboxes after completing these. This is a WARNING-level cosmetic gap; it does not affect phase goal achievement.

---

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `src/inference_mod.rs` | 12 | `\.unwrap()` mention in doc comment (not code) | Info | False-positive from grep; actual code has zero `.unwrap()` calls — all fallible paths use `to_pyresult()` |

No blockers found. No `TBD`, `FIXME`, or `XXX` markers. No stubs.

---

### Human Verification Required

None. All truths are verifiable programmatically and all checks passed.

---

### Gaps Summary

No gaps blocking goal achievement.

**Cosmetic documentation note (non-blocking):** REQUIREMENTS.md still shows INFER-01, INFER-02, INFER-03, and INFER-09 as `[ ]` Pending in both the requirement list and the traceability table. The implementations are fully functional and verified. Recommend updating these to `[x]` Complete / `| INFER-0x | Phase 31 | Complete |` in a follow-up commit.

---

### Commit Evidence

| Commit | Description | Status |
|--------|-------------|--------|
| `d6e5642` | docs(31-01): spike — record confirmed 0.20.0 signatures for all 8 Group A inference functions | FOUND |
| `519b20a` | test(31-01): add failing tests for fdars.inference t_perm_test, f_perm_test, two_sample_mean_test (RED) | FOUND |
| `74aca22` | feat(31-01): implement fdars.inference submodule with t_perm_test, f_perm_test, two_sample_mean_test | FOUND |
| `c5eb991` | test(31-02): add failing tests for mean_scb and scb_two_sample_test (RED) | FOUND |
| `ef7d197` | feat(31-02): bind mean_scb and scb_two_sample_test (INFER-04, INFER-05) | FOUND |
| `35c4e2d` | test(31-03): add failing tests for flm_f_test, flm_gof_test, oneway_anova_vstat (RED) | FOUND |
| `98300a1` | feat(31-03): bind flm_f_test, flm_gof_test, oneway_anova_vstat (INFER-06, INFER-07, INFER-08) | FOUND |

---

_Verified: 2026-08-17T14:30:00Z_
_Verifier: Claude (gsd-verifier)_
