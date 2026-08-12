---
phase: 21-per-aspect-advisor-coverage
verified: 2026-08-12T10:00:00Z
status: passed
score: 4/4 must-haves verified
behavior_unverified: 0
overrides_applied: 0
re_verification: false
---

# Phase 21: Per-Aspect Advisor Coverage — Verification Report

**Phase Goal:** Every fdars analysis aspect — not just clustering — has deterministic offline diagnostics and grounded advice task families, driven by the SAME schema, prompt, and grounding machinery with no per-aspect duplication.

**Verified:** 2026-08-12
**Status:** PASSED
**Re-verification:** No — initial verification

---

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `build_diagnostics` produces deterministic offline diagnostics for represent/basis, depth/outliers, classification, regression/regression-CV, and monitoring/SPM | VERIFIED | All 7 new aspect builders exist and are wired; full suite 225 passed, 4 skipped; determinism spot-checked live |
| 2 | Every aspect offers 3 grounded task families through shared schema + grounding machinery with no per-aspect duplication | VERIFIED | Single `_system_prompt(task, aspect)` in `_prompts.py`; single `Advice`/`Recommendation` schema in `_schema.py`; 36 aspect+task combinations all produce valid prompts; no per-aspect class or function defined in any `aspects/*.py` builder |
| 3 | Aspect is always caller-specified, never auto-detected from result keys | VERIFIED | No auto-detection path exists in dispatcher; `test_no_auto_detection` asserts `ValueError("unsupported method")` for unrecognized method string; `test_aspect_caller_specified` confirms routing is by method param only |
| 4 | Each new aspect's diagnostics pass an offline determinism test (byte-identical JSON, no numpy scalars) | VERIFIED | Determinism tests exist and pass for all 7 new aspects; SPM live `spe_moment_match_diagnostic` call confirmed deterministic; `check_no_numpy` recursive walker passes for all aspects |

**Score:** 4/4 truths verified (0 present, behavior-unverified)

---

## SC-1: Deterministic Offline Diagnostics — Per-Criterion Detail

### New Aspect Builder Files

All 8 new files exist under `python/fdars/advisor/aspects/`:

| File | Aspect | Status |
|------|--------|--------|
| `depth.py` | ASPECT-02 (partial) | VERIFIED |
| `outliers.py` | ASPECT-02 | VERIFIED |
| `classification.py` | ASPECT-03 | VERIFIED |
| `represent.py` | ASPECT-01 | VERIFIED |
| `regression.py` | ASPECT-04 | VERIFIED |
| `regression_cv.py` | ASPECT-04 | VERIFIED |
| `spm.py` | ASPECT-05 | VERIFIED |
| `_utils.py` | shared helper | VERIFIED |

### `_supported` Set (advisor/__init__.py line 124–132)

```python
_supported = {
    "alignment", "fpca", "basis", "smoothing", "clustering",  # existing
    "depth",          # ASPECT-02 (plan 21-01)
    "outliers",       # ASPECT-02 (plan 21-02)
    "classification", # ASPECT-03 (plan 21-02)
    "represent",      # ASPECT-01 (plan 21-03)
    "regression", "regression_cv",  # ASPECT-04 (plan 21-04)
    "spm",            # ASPECT-05 (plan 21-05)
}
```

All 12 aspects present. Each has a lazy-import dispatch branch.

### SC-1 Specifics Verified

| Check | Evidence |
|-------|----------|
| depth consumes raw ndarray | `np.asarray(raw, dtype=float)` in `depth.py:50`; array-safe guard in dispatcher (`hasattr(raw, "__array__")`); `test_depth_build_diagnostics_basic` PASSES |
| classification reads `error_rate` | `float(raw["error_rate"])` in `classification.py:117` with CV-path guard; `test_classification_cv_shape` PASSES |
| SPM uses `spe_moment_match_diagnostic` | Live call at `spm.py:140–148`; `excess_kurtosis` renamed to `spe_kurtosis_excess` (correction #8); `spe_kurtosis_excess` confirmed `float(-0.577...)` at runtime |
| SPM excludes `arl0_t2` | No `arl0_t2` anywhere in `spm.py`; "Stochastic ARL explicitly EXCLUDED" in docstring; confirmed `"arl0_t2" not in diag` at runtime |
| regression guards `r_squared` absence | `float(raw["r_squared"]) if "r_squared" in raw else None` at `regression.py:73–75`; `test_regression_fregre_l1_no_r_squared` PASSES |
| regression handles 2-D `fosr` residuals | `res.ndim == 1 and res.size > 0` guard at `regression.py:86`; 2-D case emits `residual_mean=None`; `test_regression_fosr_2d_residuals` PASSES |
| shared `_utils` eigenvalue helper reused | `fpca.py:14` and `spm.py:33` both import `from fdars.advisor.aspects._utils import _eigenvalues_to_variance_cumulative`; no copy |
| fpca behavior unchanged after refactor | `test_fpca_output_unchanged_after_refactor` asserts byte-identical JSON to pre-refactor expected dict; PASSES |

---

## SC-2: Shared Schema + Grounding Machinery — No Duplication

| Check | Evidence |
|-------|----------|
| Single `_system_prompt` function | One definition at `_prompts.py:102`; no per-aspect prompt function anywhere in `aspects/` |
| Single `Advice`/`Recommendation` schema | `_schema.py` only; grep of all `aspects/*.py` finds zero `class Advice`, `class Recommendation`, or `def _system_prompt` |
| `_ASPECT_PRIMERS` dict — all 7 new aspects | Keys: `depth`, `outliers`, `classification`, `represent`, `regression`, `regression_cv`, `spm`; `test_all_seven_aspect_primers_present` PASSES |
| `aspect` param in `advise()` | `aspect: str = ""` at `__init__.py:372`; `system = _system_prompt(task, aspect)` at line 427 |
| `aspect=""` reproduces base behavior | `_ASPECT_PRIMERS.get("", "")` returns `""`; `test_prompt_aspect_backward_compatible` asserts byte-identical output |
| 36 aspect+task combinations work | Runtime verification: all 12 aspects × 3 tasks produce non-empty prompts without error |
| Pre-existing aspects (clustering, smoothing, alignment, basis, fpca) have no dedicated primer | Intentional — they pre-date the primer mechanism. The 3 task clauses still flow through the shared `_system_prompt` for all of them. SC-2's "no duplication" contract is satisfied. |
| Provider layer (Phases 19–20) unchanged | Zero commits to `python/fdars/advisor/providers/` or `_schema.py` during Phase 21 commits; only additive `aspect=` param added to `advise()` |

---

## SC-3: Aspect Always Caller-Specified

| Check | Evidence |
|-------|----------|
| No auto-detection path in dispatcher | `__init__.py` grep finds no `auto`, `infer.*method`, `detect`, or key-shape inspection before routing |
| Wrong method raises `ValueError` | `build_diagnostics({"r_squared": 0.9}, method="not_a_real_method")` raises `ValueError("unsupported method")` |
| `test_no_auto_detection` exists and passes | `TestBuildDiagnosticsOffline::test_no_auto_detection` — PASSED |
| `test_aspect_caller_specified` exists and passes | `TestBuildDiagnosticsOffline::test_aspect_caller_specified` — PASSED |

---

## SC-4: Offline Determinism Tests

| Aspect | Test | Checks | Status |
|--------|------|--------|--------|
| depth | `test_depth_deterministic` | equal dicts + byte-identical JSON + no `np.generic` | PASSED |
| outliers | `test_outliers_deterministic` (×2 fixtures) | LRT + magnitude_shape paths | PASSED |
| classification | `test_classification_deterministic` (×2 fixtures) | point-estimate + CV paths | PASSED |
| represent | `test_represent_deterministic` | dict form + Fdata-like form + cross-form equality | PASSED |
| regression | `test_regression_deterministic` (×2 fixtures) | fregre_lm + fregre_l1 (r_squared=None) | PASSED |
| regression_cv | `test_regression_cv_deterministic` | fregre_cv with elbow_present=True | PASSED |
| spm | `test_spm_deterministic` (`pytest.importorskip("fdars.spm")`) | live `spe_moment_match_diagnostic` call; byte-identical JSON; `spe_kurtosis_excess` is native `float` | PASSED |
| fpca (regression guard) | `test_fpca_output_unchanged_after_refactor` | byte-identical JSON pre/post `_utils` refactor | PASSED |

---

## Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `python/fdars/advisor/aspects/depth.py` | ASPECT-02 depth builder | VERIFIED | 65 lines; pure NumPy; all values `float`/`int`/`list` |
| `python/fdars/advisor/aspects/outliers.py` | ASPECT-02 outliers builder | VERIFIED | 4 result shapes handled by key-presence guards |
| `python/fdars/advisor/aspects/classification.py` | ASPECT-03 classification builder | VERIFIED | point-estimate + CV paths; `n_classes` as explicit param |
| `python/fdars/advisor/aspects/represent.py` | ASPECT-01 represent builder | VERIFIED | dict + Fdata-like input; attribute-first lookup |
| `python/fdars/advisor/aspects/regression.py` | ASPECT-04 regression builder | VERIFIED | corrections #3/#4/#5 applied |
| `python/fdars/advisor/aspects/regression_cv.py` | ASPECT-04 regression-CV builder | VERIFIED | fregre_cv + model_selection_ncomp paths; correction #7 |
| `python/fdars/advisor/aspects/spm.py` | ASPECT-05 SPM builder | VERIFIED | live `spe_moment_match_diagnostic` call guarded by try/except; arl0_t2 excluded |
| `python/fdars/advisor/aspects/_utils.py` | shared eigenvalue→variance helper | VERIFIED | imported by fpca.py and spm.py; not copied |
| `python/fdars/advisor/__init__.py` | updated `_supported`, dispatcher, `advise(aspect=)` | VERIFIED | 12 aspects in `_supported`; `aspect: str = ""` in `advise()`; `n_classes` explicit param |
| `python/fdars/advisor/_prompts.py` | `_ASPECT_PRIMERS` dict; `_system_prompt(task, aspect)` | VERIFIED | 7 new aspects with primer clauses; aspect threading wired |
| `tests/test_advisor.py` | determinism + no-auto-detection + aspect-coverage tests | VERIFIED | 43 tests in test_advisor.py; 225 passed / 4 skipped full suite |

---

## Key Link Verification

| From | To | Via | Status |
|------|----|-----|--------|
| `advise()` | `_system_prompt(task, aspect)` | `system = _system_prompt(task, aspect)` at `__init__.py:427` | WIRED |
| `build_diagnostics(method="depth")` | `aspects/depth._build_depth_diagnostics` | lazy import at `__init__.py:175–176` | WIRED |
| `build_diagnostics(method="spm")` | `aspects/spm._build_spm_diagnostics` | lazy import at `__init__.py:198–200` | WIRED |
| `aspects/spm.py` | `_utils._eigenvalues_to_variance_cumulative` | `from fdars.advisor.aspects._utils import ...` at `spm.py:33` | WIRED |
| `aspects/fpca.py` | `_utils._eigenvalues_to_variance_cumulative` | `from fdars.advisor.aspects._utils import ...` at `fpca.py:14` | WIRED |
| `aspects/spm.py` | `fdars.spm.spe_moment_match_diagnostic` | live call inside `try/except Exception` at `spm.py:138–148` | WIRED |

---

## Data-Flow Trace (Level 4)

| Aspect | Data Variable | Source | Produces Real Data | Status |
|--------|---------------|--------|-------------------|--------|
| depth | `depth_q10` | `np.percentile(np.asarray(raw, dtype=float), 10)` | Yes — from caller-supplied score array | FLOWING |
| spm | `spe_kurtosis_excess` | `float(mmd["excess_kurtosis"])` from live `spe_moment_match_diagnostic` call | Yes — confirmed `float(-0.577...)` at runtime | FLOWING |
| regression | `r_squared` | `float(raw["r_squared"]) if "r_squared" in raw else None` | Yes — from caller-supplied result dict; None when absent | FLOWING |
| represent | `is_uniform_grid` | `bool(spacing_std / spacing_mean < 0.01)` from `np.diff(argvals)` | Yes — from caller-supplied argvals | FLOWING |

---

## Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| depth accepts ndarray, computes n_obs | `build_diagnostics(np.array([...]), method="depth")` | `method="depth"`, `n_obs=5` | PASS |
| classification CV reads `error_rate` key | `build_diagnostics({"error_rate": 0.15, ...}, method="classification")` | `cv_error_rate=0.15`, `accuracy=0.85` | PASS |
| SPM excludes `arl0_t2` | `"arl0_t2" not in build_diagnostics({...}, method="spm")` | `True` | PASS |
| SPM uses `spe_kurtosis_excess` | `build_diagnostics({...}, method="spm")["spe_kurtosis_excess"]` | `float(-0.577...)` | PASS |
| SPM deterministic (live call) | two calls → byte-identical JSON | `True` | PASS |
| regression `r_squared` absent → None | fregre_l1 fixture | `r_squared is None` | PASS |
| regression 2-D fosr residuals → None stats | fosr fixture | `residual_mean is None, has_fosr=True` | PASS |
| 1-D "fitted" key → `has_fosr=False` | not_fosr fixture | `has_fosr=False` | PASS |
| fpca output unchanged after `_utils` refactor | byte-identical JSON | `True` | PASS |
| Full test suite | `pytest tests/ -q` | 225 passed, 4 skipped | PASS |

---

## Probe Execution

No probes declared in PLAN files for this phase. Behavioral spot-checks above serve as functional verification. Step 7c: SKIPPED (no declared probes).

---

## Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|---------|
| ASPECT-01 | 21-03 | `build_diagnostics` supports represent/basis | SATISFIED | `represent.py` created; `basis.py` pre-existing from Phase 19; both in `_supported`; implementation confirmed. Note: REQUIREMENTS.md checkbox is unchecked — tracking omission, not implementation gap (see below) |
| ASPECT-02 | 21-01, 21-02 | depth and outliers builders | SATISFIED | `depth.py`, `outliers.py` created; in `_supported`; tests pass |
| ASPECT-03 | 21-02 | classification builder | SATISFIED | `classification.py` created; in `_supported`; tests pass |
| ASPECT-04 | 21-04 | regression and regression-CV builders | SATISFIED | `regression.py`, `regression_cv.py` created; in `_supported`; tests pass |
| ASPECT-05 | 21-05 | SPM monitoring builder | SATISFIED | `spm.py` created; live `spe_moment_match_diagnostic` call; `arl0_t2` excluded; tests pass |
| ASPECT-06 | 21-01..05 | no per-aspect schema/prompt duplication | SATISFIED | Single `_system_prompt`, single `Advice`; `_ASPECT_PRIMERS` covers all 7 new aspects |
| ASPECT-07 | 21-01 | caller-specified aspect, no auto-detection | SATISFIED | No auto-detection path; two tests assert this contract |

### ASPECT-01 Tracking Note

REQUIREMENTS.md line 29 shows `- [ ] **ASPECT-01**` (unchecked). This is a **tracking omission**, not an implementation gap:

- `represent` aspect: implemented in plan 21-03 (`represent.py` + dispatch + `_ASPECT_PRIMERS["represent"]`); all `TestRepresent` tests pass.
- `basis` aspect: pre-existing since Phase 19 (`basis.py` created in commit `8e571e5`); was already in `_supported` before Phase 21.
- ROADMAP.md Plan section confirms `21-03-PLAN.md` is checked off with `[ASPECT-01, ASPECT-06]`.

The REQUIREMENTS.md checkbox was simply not updated when the plan committed. The implementation fully satisfies ASPECT-01.

---

## Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| None found | — | — | — | All 7 new aspect files were scanned; no TBD/FIXME/XXX/placeholder/stub patterns found |

No debt markers in any Phase 21 created or modified files. No hardcoded empty data in the computation paths.

---

## Human Verification Required

None. All truths are fully verifiable offline through code inspection and test execution. No visual behavior, real-time behavior, or external service integration requires human testing in this phase (provider/LLM surface exposure is deferred to Phase 22).

---

## Gaps Summary

No gaps found. All four success criteria are verified through code inspection, runtime spot-checks, and test execution.

The one noteworthy discrepancy — ASPECT-01 unchecked in REQUIREMENTS.md — is a tracking omission (the checkbox was not updated after the implementation commit). The implementation exists, is wired, and is tested. No corrective action needed for the phase goal to be considered achieved; the REQUIREMENTS.md checkbox should be updated as routine housekeeping.

---

_Verified: 2026-08-12T10:00:00Z_
_Verifier: Claude (gsd-verifier)_
