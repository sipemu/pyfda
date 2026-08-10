---
phase: 11-python-api-surface
reviewed: 2026-08-09T20:10:00Z
depth: standard
files_reviewed: 5
files_reviewed_list:
  - examples/advisor_recipe.py
  - pyproject.toml
  - python/fdars/__init__.py
  - tests/test_advisor.py
  - tests/test_basic.py
findings:
  critical: 2
  warning: 2
  info: 3
  total: 7
status: issues_found
---

# Phase 11: Code Review Report

**Reviewed:** 2026-08-09T20:10:00Z
**Depth:** standard
**Files Reviewed:** 5
**Status:** issues_found

## Summary

Reviewed all five files changed in Phase 11. The scope is the Python API surface layer: the `fdars.advisor` module with its Phase 10 bug fixes applied, the new `fdars.results` wrapper module, `__init__.py` wiring, `pyproject.toml`, and the test suite.

**Phase 10 bug fixes verified as applied:** All eight Phase 10 findings (CR-01 through CR-05, WR-01 through WR-03) are confirmed fixed in the Phase 11 code. The NaN→None sentinel replacement, the `parsed_output` guard, the empty-GCV guard, the Anthropic version floor enforcement, the pydantic guard, the AIC/BIC label rename, the dead `cumulative` variable removal, and the selfcheck reliability fix are all present and correct.

**New defects found in Phase 11 additions:**

The version enforcement fix introduced in Phase 11 (CR-04 fix) contains a crash of its own: `int("0rc1")` raises `ValueError` for any pre-release Anthropic SDK version string, converting a useful version-floor error into an opaque unhandled exception. The new `results.py` module has two bugs: `FPCAResult.transform()` uses a broken `None` guard for the weights array, and `SPMResult.is_ooc()` crashes with `TypeError` when `t2_alarm` is in the result dict but neither `t2` nor `spe` is present.

Two warnings cover missing test coverage for the new result wrappers and a stale internal planning note left in the public module docstring.

---

## Critical Issues

### CR-01: `_require_anthropic()` version parser crashes on pre-release SDK versions

**File:** `python/fdars/advisor.py:742-748`

**Issue:** The version-floor check splits on `.` and calls `int()` on each segment:

```python
installed = tuple(
    int(x) for x in anthropic.__version__.split(".")[:3]
)
```

Any pre-release Anthropic SDK version string such as `"0.72.0rc1"` or `"0.73.0b2"` produces a third segment like `"0rc1"` that cannot be parsed as an integer. `int("0rc1")` raises `ValueError` — an unhandled exception with no actionable message. The user sees a raw traceback from inside `_require_anthropic()` instead of the clear `ImportError` the function is designed to produce. This is a regression introduced when the Phase 10 version-floor enforcement was added: prior to that fix the function simply returned the module, so no crash was possible.

**Fix:** Strip any non-numeric suffix from each version segment before conversion:

```python
import re as _re

def _parse_version_tuple(version_str: str) -> tuple:
    segments = version_str.split(".")[:3]
    result = []
    for seg in segments:
        m = _re.match(r"(\d+)", seg)
        result.append(int(m.group(1)) if m else 0)
    return tuple(result)

# In _require_anthropic():
installed = _parse_version_tuple(anthropic.__version__)
floor = _parse_version_tuple(ADVISOR_ANTHROPIC_MIN_VERSION)
```

---

### CR-02: `FPCAResult.transform()` weights guard is broken — `np.asarray(None) is not None`

**File:** `python/fdars/results.py:325-327`

**Issue:** When the underlying dict has no `"weights"` key, `self.raw.get("weights")` returns `None`. The code immediately wraps it:

```python
weights = np.asarray(self.raw.get("weights"))   # line 325
if weights is not None and weights.size == centered.shape[1]:
```

`np.asarray(None)` does not return `None` — it returns `array(None, dtype=object)`, a 0-dimensional object array. This value is not `None`, so the first condition is always `True`. The second guard (`weights.size == centered.shape[1]`) saves the common case (size=1 never equals a typical grid length like 50 or 365), but fails when `m=1` (a single-evaluation-point grid): `size == 1 == m` evaluates `True`, and the subsequent `weights[None, :]` indexing crashes with `IndexError: too many indices for array: array is 0-dimensional, but 1 were indexed`. Users calling `transform()` on FPCA results from a length-1 grid hit an opaque `IndexError` instead of computing the correct projection.

**Fix:** Check the raw dict value before wrapping with `np.asarray`:

```python
weights_raw = self.raw.get("weights")
if weights_raw is not None:
    weights = np.asarray(weights_raw, dtype=float)
    if weights.size == centered.shape[1]:
        return (centered * weights[None, :]) @ self.components
return centered @ self.components
```

---

## Warnings

### WR-01: `SPMResult.is_ooc()` crashes with `TypeError` when `t2_alarm` is present but `t2`/`spe` arrays are absent

**File:** `python/fdars/results.py:462`

**Issue:** The Phase-II branch of `is_ooc()` triggers when `"t2_alarm" in self.raw or "spe_alarm" in self.raw`. It then computes `n` via:

```python
n = len(np.asarray(self.raw.get("t2", self.raw.get("spe"))))
```

If neither `"t2"` nor `"spe"` is in the result dict — a scenario that arises with partial or synthetic Phase-II dicts containing only alarm masks — `raw.get("t2", raw.get("spe"))` returns `None`. `np.asarray(None)` produces a 0-dimensional array and `len()` on a 0-dimensional array raises `TypeError: len() of unsized object`. The crash surfaces with no useful message.

**Fix:** Derive `n` from the alarm arrays themselves, which are guaranteed to be present when the branch is entered:

```python
if "t2_alarm" in self.raw or "spe_alarm" in self.raw:
    alarm_key = "t2_alarm" if "t2_alarm" in self.raw else "spe_alarm"
    alarm_arr = np.asarray(self.raw[alarm_key], dtype=bool)
    n = len(alarm_arr)
    mask = np.zeros(n, dtype=bool)
    if "t2_alarm" in self.raw:
        mask |= np.asarray(self.raw["t2_alarm"], dtype=bool)
    if "spe_alarm" in self.raw:
        mask |= np.asarray(self.raw["spe_alarm"], dtype=bool)
    return mask
```

---

### WR-02: `results.py` wrappers (`FPCAResult.transform`, `SPMResult`, `FregreResult.predict`) have zero test coverage

**File:** `python/fdars/results.py` — all wrapper classes

**Issue:** The new `fdars.results` module is wired into `__init__.py` (line 61) and exported in `__all__` (line 79). None of its public methods are exercised by the test suite. `test_r_parity.py` calls `wrap_fregre` and checks `repr(wrapped)` but does not call `.predict()`, `.coef()`, `.summary()`, or `.fitted_values`. No test exercises `FPCAResult.transform()`, `FPCAResult.explained_variance_ratio`, `SPMResult.is_ooc()`, `SPMResult.limits`, `AlignmentResult.aligned`, or `DictResult.__getattr__` with a missing key. The two correctness bugs above (CR-02, WR-01) were not caught by the test suite because no test exercises those code paths.

**Fix:** Add tests for the documented public API of each wrapper class, covering at minimum: `FPCAResult.transform(newdata)`, `SPMResult.is_ooc()` for both Phase I and Phase II dicts, `FregreResult.predict(newdata)` for each method, and the `DictResult` attribute/item access protocol.

---

## Info

### IN-01: Stale internal planning note in public module docstring of `advisor.py`

**File:** `python/fdars/advisor.py:30-33`

**Issue:** The module docstring contains a planning-phase instruction that was never removed:

> The `[advisor]` optional extra (declaring `anthropic>=0.72.0` in `pyproject.toml`) is DECLARED and TESTED in Phase 11 per the phase split — do not add the extra to pyproject.toml in this phase.

Phase 11 has already added the `advisor` extra to `pyproject.toml` (line 41). This note is now factually incorrect and is visible to any user who reads the module docstring (e.g. via `help(fdars.advisor)` or API doc generators).

**Fix:** Remove the planning-phase paragraph (lines 30-33) from the module docstring. The `ADVISOR_ANTHROPIC_MIN_VERSION` constant and the `[advisor]` extra are now both present; the historical phase-split rationale is irrelevant to users.

---

### IN-02: `dev` extra does not include `anthropic` or `pydantic` — offline test isolation is implicit, not explicit

**File:** `pyproject.toml:40`

**Issue:** The `[dev]` extra used for local development and CI is `["pytest", "matplotlib>=3.6"]`. The `[advisor]` optional extra (`anthropic>=0.72.0`, `pydantic>=2.0`) is separate. `test_advisor.py` runs its offline tests without those packages, relying on the `monkeypatch.setitem(sys.modules, "anthropic", None)` trick and the `pytest.importorskip` guards. This is correct, but a developer who installs `fdars[dev]` and runs the full test suite will never exercise the integration path even if they have an API key, because neither `anthropic` nor `pydantic` is pulled in by `[dev]`. The isolation is accidental rather than documented.

**Fix:** Add a comment to `pyproject.toml` documenting that integration tests require `fdars[advisor]` in addition to `fdars[dev]`, or create a combined `dev-full` extra:

```toml
dev-full = ["pytest", "matplotlib>=3.6", "anthropic>=0.72.0", "pydantic>=2.0"]
```

---

### IN-03: `examples/advisor_recipe.py` line 43 accesses `ds.argvals` but `ds.data.data` is redundant nesting

**File:** `examples/advisor_recipe.py:42-43`

**Issue:** The comment on line 42 reads `# ds.data is an Fdata object (35 stations × 365 daily observations)` and `X = np.asarray(ds.data.data, dtype=float)`. The inner `.data` attribute on `Fdata` returns the raw matrix, so `ds.data.data` is the correct two-step access (`Dataset.data` → `Fdata`, `Fdata.data` → `np.ndarray`). This is not a bug — it works correctly — but the double `.data` is a confusing pattern that several early readers in Phase 11 research flagged as a readability hazard. Users skimming the example may assume `ds.data` is already the numpy matrix and write `ds.data` directly (getting an `Fdata` object instead), then be confused when array operations fail.

**Fix:** Add an inline clarification comment or introduce a named intermediate:

```python
fdata_obj = ds.data           # Fdata object (35 stations × 365 daily obs)
X = np.asarray(fdata_obj.data, dtype=float)   # shape (35, 365)
```

---

_Reviewed: 2026-08-09T20:10:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
