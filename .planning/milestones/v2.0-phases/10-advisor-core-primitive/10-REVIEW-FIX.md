---
phase: 10-advisor-core-primitive
fixed_at: 2026-08-09T19:10:00Z
review_path: .planning/phases/10-advisor-core-primitive/10-REVIEW.md
iteration: 1
findings_in_scope: 8
fixed: 8
skipped: 0
status: all_fixed
---

# Phase 10: Code Review Fix Report

**Fixed at:** 2026-08-09T19:10:00Z
**Source review:** .planning/phases/10-advisor-core-primitive/10-REVIEW.md
**Iteration:** 1

**Summary:**
- Findings in scope: 8 (5 Critical + 3 Warning)
- Fixed: 8
- Skipped: 0

## Fixed Issues

### CR-01 + WR-03: NaN values in diagnostics / broken selfcheck equality

**Files modified:** `python/fdars/advisor.py`
**Commit:** e650d8a
**Applied fix:** Replaced `float("nan")` with `None` in both exception fallbacks —
`_build_alignment_diagnostics` (lines 302-303) and `_build_clustering_diagnostics`
(lines 645-646). Updated all aggregate callers (`amplitude_mean`, `amplitude_max`,
`phase_mean`, `phase_max`, `mean_amplitude_separation`, `mean_phase_separation`) to
filter `None` via a list comprehension before calling `np.mean`/`np.max` instead of
`np.nanmean`/`np.nanmax`, which cannot handle Python `None`. WR-03 is resolved as a
corollary: `None == None` is `True` in Python dict equality, so the
`_selfcheck_alignment_diagnostics` assertion is now sound.

---

### CR-02: `response.parsed_output` unchecked `None` return

**Files modified:** `python/fdars/advisor.py`
**Commit:** d79c290
**Applied fix:** Added an explicit `None` check after `response.parsed_output` in
`advise()`. When `parsed` is `None`, raises `ValueError` with a descriptive message
citing `response.stop_reason`, so callers get an actionable error instead of an
`AttributeError` on `.interpretation`/`.recommendations`/`.caveats`.

---

### CR-03: `np.argmin()` crashes on empty GCV list

**Files modified:** `python/fdars/advisor.py`
**Commit:** 2555a6b
**Applied fix:** Added an empty-list guard before `np.argmin(gcv_values)` in both
`_build_basis_diagnostics` (Branch A) and `_build_smoothing_diagnostics` (Branch A).
When `gcv_values` is empty, all optimal/AIC/BIC keys are set to `None` and the
function returns early rather than raising `ValueError: attempt to get argmin of an
empty sequence`.

---

### CR-04: `ADVISOR_ANTHROPIC_MIN_VERSION` never enforced at runtime

**Files modified:** `python/fdars/advisor.py`
**Commit:** a8c66e4
**Applied fix:** Extended `_require_anthropic()` to perform a tuple-comparison version
check after a successful import. Splits `anthropic.__version__` and
`ADVISOR_ANTHROPIC_MIN_VERSION` into `(major, minor, patch)` tuples and raises a
clear `ImportError` with a `pip install` hint when the installed version is below
`0.72.0`. Uses a string-split tuple approach (no `packaging` dependency required).

---

### CR-05: Missing pydantic guard — opaque SDK error when pydantic absent

**Files modified:** `python/fdars/advisor.py`
**Commit:** 03abc28
**Applied fix:** Added `_require_pydantic()` function (mirrors `_require_anthropic()`
in structure) that imports `pydantic` or raises `ImportError` naming
`pip install fdars[advisor]`. Called from `advise()` immediately after
`_require_anthropic()`, before `client = anthropic.Anthropic()`, so the user
receives a clear error before any SDK call is made.

---

### WR-01: AIC/BIC keys use `log(GCV)` — misleading label

**Files modified:** `python/fdars/advisor.py`
**Commit:** e48fa6e
**Applied fix:** Renamed `"aic"` to `"gcv_aic_approx"` and `"bic"` to
`"gcv_bic_approx"` in all locations within `_build_basis_diagnostics` and
`_build_smoothing_diagnostics`: the normal computation path, the CR-03 empty-list
early-return path, and the no-input fallback path. Added a clarifying comment
explaining that these are GCV-based approximations and differ from standard AIC/BIC
by the `(1 - edf/n)^2` factor.

---

### WR-02: Dead `cumulative` variable in FPCA branch

**Files modified:** `python/fdars/advisor.py`
**Commit:** d6aa918
**Applied fix:** Removed the standalone `cumulative = float(np.cumsum(evr)[-1]) if n_comp > 0 else 0.0`
line (was line 378). The same value is already available as `cum_list[-1]`, which is
correctly stored in `diag["cumulative_variance_explained"]`.

---

## Skipped Issues

None — all 8 findings were fixed.

---

## Verification

- **Tier 1 (re-read):** Each modified section was visually confirmed after every edit.
- **Tier 2 (syntax):** `python -m py_compile python/fdars/advisor.py` passed after every commit.
- **Tier 2 (offline selfcheck):** `advisor._selfcheck_alignment_diagnostics()` run with mocked
  `fdars.alignment` (no compiled extension required); passed cleanly, confirming the CR-01/WR-03
  None-equality fix resolves the spurious AssertionError.
- **Verification environment:** Main checkout (no worktree; `workflow.use_worktrees` not applicable
  for direct-edit path per prompt commit_discipline).

---

_Fixed: 2026-08-09T19:10:00Z_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_
