---
phase: 72-advisor-extension
verified: 2026-09-04T00:00:00Z
status: passed
score: 10/10 must-haves verified
behavior_unverified: 0
overrides_applied: 0
re_verification: false
---

# Phase 72: advisor-extension Verification Report

**Phase Goal:** The AI advisor produces grounded diagnostics for the new capability families, with the grounding invariant and MCP guard-sync held as hard constraints.
**Verified:** 2026-09-04
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | New fts + frechet advisor aspects exist with every diagnostic a real fdars-computed native float/int scalar (no numpy scalars) | ✓ VERIFIED | `python/fdars/advisor/aspects/fts.py` and `frechet.py` exist; live calls to `fts.ftsm()` and `frechet.frechet_mean()` routed through `build_diagnostics()` return `json.dumps`-able dicts; `no_numpy()` assertion passes on all outputs |
| 2 | Extensions of regression/classification/spm for new methods exist with grounded native scalars | ✓ VERIFIED | `fof_regression` branch in `regression.py` returns `has_fof_regression=True` with `beta_surface_shape=[15,20]` (int list); mfpca branch in `spm.py` returns `has_mfpca=True` with `mfpca_ncomp=2`; all as native Python types confirmed by `no_numpy()` |
| 3 | `_DIAGNOSTICS_METHODS` / `_RUNNABLE_METHODS` guard-sync stays consistent — updated atomically; `fts` and `frechet` in `_DIAGNOSTICS_METHODS`, absent from `_RUNNABLE_METHODS` | ✓ VERIFIED | `server.py:52-60` `_RUNNABLE_METHODS = frozenset({"alignment","fpca","basis","smoothing","clustering","depth"})` — fts/frechet absent; `server.py:66-87` `_DIAGNOSTICS_METHODS` has both; neither appears in `_runner.py` or `_pipeline.py` |
| 4 | `test_guard_sync_version_independent.py` passes | ✓ VERIFIED | Ran `.venv/bin/pytest tests/test_guard_sync_version_independent.py -q` → **2 passed** |
| 5 | Per-aspect `json.dumps(build_diagnostics(...))` serialization tests pass for fts, frechet, spm_v11 | ✓ VERIFIED | `test_advisor_fts.py` → 37 passed; `test_advisor_frechet.py` → 37 passed; `test_advisor_spm_v11.py` → 29 passed |
| 6 | MCP compute path is provably LLM-free; frechet stays diagnostics-only (NOT in `_RUNNABLE_METHODS`) | ✓ VERIFIED | No `anthropic` or `openai` import in `fts.py` or `frechet.py`; subprocess + in-process fallback LLM-free assertions in `test_advisor_grounding.py` (lines 539-692) pass; 54 grounding tests pass |
| 7 | CR-01 fixed: shapelet classifier does not spuriously trigger `has_elastic_multinomial = True` | ✓ VERIFIED | `classification.py:150` reads `"train_accuracy" in raw and "n_shapelets" not in raw`; `test_advisor_group_b.py` → 57 passed including `test_shapelet_has_elastic_multinomial_false` and `test_shapelet_and_elastic_mutually_exclusive_synthetic` |
| 8 | WR-01 fixed: mfpca input does not populate spm_phase1 `ncomp`/`eigenvalues` fields | ✓ VERIFIED | `has_mfpca` computed early at `spm.py:132`; `ncomp` and `eigenvalues` gated on `not has_mfpca` at lines 142/190-196; live check confirms `d.get('ncomp') is None` for mfpca input |
| 9 | WR-02 fixed: `fts.py` acf/dpca branches use guarded key access | ✓ VERIFIED | `fts.py:107` uses `raw["lags"] if "lags" in raw else np.array([])`; `fts.py:134` uses `raw.get("eigenvalues")` with explicit None branch |
| 10 | Full test suite is regression-free | ✓ VERIFIED | `.venv/bin/pytest tests/ -q` → **5650 passed, 10 skipped, 120 warnings, 0 failures** |

**Score:** 10/10 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `python/fdars/advisor/aspects/fts.py` | fts diagnostics builder | ✓ VERIFIED | 224 lines; 6 discriminated branches (stationarity/acf/dpca/fplsr/ftsm/forecast); numpy-only imports |
| `python/fdars/advisor/aspects/frechet.py` | frechet diagnostics builder | ✓ VERIFIED | 186 lines; array-first guard + 3 dict discriminators (anova/global_reg/local_reg) |
| `tests/test_advisor_fts.py` | per-aspect serialization + grounding tests | ✓ VERIFIED | 37 tests; 5 fixture classes; json.dumps + check_no_numpy + determinism |
| `tests/test_advisor_frechet.py` | per-aspect serialization + grounding tests | ✓ VERIFIED | 37 tests; 4 shapes (array + 3 dict); all assertions pass |
| `tests/test_advisor_spm_v11.py` | mfpca + spe_multivariate tests | ✓ VERIFIED | 29 tests; includes WR-01 regression guard |
| `tests/test_advisor_grounding.py` | LLM-free proof + grounding harness | ✓ VERIFIED | 54 tests; subprocess + in-process fallback (lines 539-692); both anthropic and openai checked |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `advisor.__init__._supported` | `server._DIAGNOSTICS_METHODS` | Both sets contain `"fts"` and `"frechet"` | ✓ WIRED | `__init__.py:151-152`; `server.py:85-86`; guard-sync test at line 56-57 |
| `advisor.__init__._supported` | `test_guard_sync_version_independent.py._EXPECTED_DIAGNOSTICS_METHODS` | Literal set in test | ✓ WIRED | Test checks all three are equal; passes 2/2 |
| `method_lc == "fts"` dispatch | `_build_fts_diagnostics` in `fts.py` | `__init__.py:240-243` lazy import | ✓ WIRED | Dispatch branch exists; builder returns correct dict |
| `method_lc == "frechet"` dispatch | `_build_frechet_diagnostics` in `frechet.py` | `__init__.py:244-247` lazy import | ✓ WIRED | Dispatch branch exists; builder handles all 4 result shapes |
| shapelet opaque handle coercion | `dict(raw)` in `__init__.py` | Guard at line 169 before `dict(raw)` at line 180 | ✓ WIRED | `GUARD_LINE=169 < DICT_LINE=180`; confirmed by grep |
| `frechet`/`fts` NOT in `_RUNNABLE_METHODS` | `_runner.py` / `_pipeline.py` | Absence confirmed | ✓ WIRED | Neither file contains `"fts"` or `"frechet"` |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|---------------|--------|--------------------|--------|
| `fts.py:_build_fts_diagnostics` | All numeric fields | Raw fdars result dict from `ftsm`, `stationarity_test`, `functional_acf`, `dpca`, `fplsr` | Yes — live fdars call via `.venv` confirms real values | ✓ FLOWING |
| `frechet.py:_build_frechet_diagnostics` | All numeric fields | Raw fdars result (dict or numpy array) from `frechet_mean`, `frechet_anova`, `frechet_global/local_reg` | Yes — live fdars call confirms real values | ✓ FLOWING |
| `regression.py` (fof branches) | `beta_surface_shape`, `fof_r_squared` | fdars `fof_regression` PyDict result | Yes — live call returns `beta_surface_shape=[15,20]` | ✓ FLOWING |
| `spm.py` (mfpca branch) | `mfpca_ncomp`, `mfpca_eigenvalues` | fdars `mfpca` PyDict result | Yes — live call returns `mfpca_ncomp=2` | ✓ FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| ftsm diagnostics: grounded native scalars, json serializable | `.venv/bin/python -c "...fts.ftsm() ... json.dumps() ... no_numpy()"` | `method='fts' has_ftsm=True ncomp=3 n_ar_models=3 json OK numpy-free OK` | ✓ PASS |
| frechet_mean array path: non-dict handled without crash | `.venv/bin/python -c "...frechet_mean() ... build_diagnostics(mean, ...)"` | `has_frechet_mean=True ndim=2 json OK numpy-free OK` | ✓ PASS |
| fof_regression extended branch: beta_surface_shape is [int,int] list | `.venv/bin/python -c "...fof_regression() ... build_diagnostics(raw, method='regression')"` | `has_fof_regression=True beta_surface_shape=[15, 20] json OK numpy-free OK` | ✓ PASS |
| mfpca extended branch: spm_phase1 sentinel fields are None (WR-01) | `.venv/bin/python -c "...mfpca() ... build_diagnostics(raw, method='spm')"` | `has_mfpca=True mfpca_ncomp=2 spm_phase1 ncomp=None: True json OK numpy-free OK` | ✓ PASS |
| LLM-free: importing fts/frechet aspects does not load anthropic/openai | `.venv/bin/python -c "import fdars.advisor.aspects.fts; assert 'anthropic' not in sys.modules"` | `LLM-free: OK` | ✓ PASS |
| guard-sync test | `.venv/bin/pytest tests/test_guard_sync_version_independent.py -q` | 2 passed | ✓ PASS |
| per-aspect serialization tests | `.venv/bin/pytest tests/test_advisor_fts.py tests/test_advisor_frechet.py tests/test_advisor_spm_v11.py tests/test_advisor_group_b.py tests/test_advisor_regression_v6.py tests/test_advisor_grounding.py -q` | 274 passed total | ✓ PASS |
| Full suite regression check | `.venv/bin/pytest tests/ -q` | **5650 passed, 10 skipped, 120 warnings, 0 failures** | ✓ PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| ADV-01 | 72-01, 72-02, 72-03, 72-04 | New/extended advisor aspects with every diagnostic a real fdars-computed native float/int scalar | ✓ SATISFIED | `fts.py`, `frechet.py` created; `regression.py`, `classification.py`, `spm.py` extended; all values float/int/bool/list/None; numpy-scalar grounding confirmed by live checks and 274 test assertions |
| ADV-02 | 72-01, 72-04 | MCP guard-sync stays consistent; atomic commit; serialization tests pass; LLM-free compute path | ✓ SATISFIED | `_DIAGNOSTICS_METHODS`/`_supported`/guard-sync test updated atomically (commit `15a8e71`); guard-sync test 2/2; LLM-free subprocess + in-process assertions in `test_advisor_grounding.py` pass (54 tests) |

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| None found | — | — | — | No TBD/FIXME/XXX markers; no stub return patterns; no numpy scalars in output dicts |

### Human Verification Required

None. All phase truths are verifiable programmatically and all automated checks pass.

### Gaps Summary

No gaps. All 10 must-have truths are verified against the actual codebase:

- Both new aspect files exist, are substantive (not stubs), and are wired through the dispatch table.
- Guard-sync is consistent across all three locations with confirmed atomic registration.
- CR-01 (elastic/shapelet mutual exclusivity), WR-01 (mfpca spm_phase1 field isolation), WR-02 (guarded key access), and WR-03 (docstring counts) are all applied and confirmed.
- Full suite: 5650 passed, 0 failures — no regressions introduced.

---

_Verified: 2026-09-04_
_Verifier: Claude (gsd-verifier)_
