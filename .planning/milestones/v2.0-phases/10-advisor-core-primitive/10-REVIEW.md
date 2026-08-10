---
phase: 10-advisor-core-primitive
reviewed: 2026-08-09T18:52:32Z
depth: standard
files_reviewed: 1
files_reviewed_list:
  - python/fdars/advisor.py
findings:
  critical: 5
  warning: 3
  info: 0
  total: 8
status: issues_found
---

# Phase 10: Code Review Report

**Reviewed:** 2026-08-09T18:52:32Z
**Depth:** standard
**Files Reviewed:** 1
**Status:** issues_found

## Summary

Reviewed `python/fdars/advisor.py` — the new pure-Python `fdars.advisor` module implementing the grounded AI analysis advisor. The module architecture is sound: the offline/deterministic split, lazy imports, Pydantic fallback, and the `describe_cluster_differences` specialization are all coherent. The Anthropic SDK usage is broadly correct (`thinking={"type": "adaptive"}` is a valid SDK type as of 0.72.0; `messages.parse(output_format=Advice)` and `response.parsed_output` match the SDK's `ParsedMessage` interface).

Five critical defects were found that must be fixed before this ships:

1. NaN values returned by the fallback distance computation are stored in the diagnostics dict and then serialised with `json.dumps`, producing non-RFC-7159 output that can corrupt the LLM call.
2. `response.parsed_output` is `Optional[Advice]` — it returns `None` when the SDK cannot parse the response — and the return value is never checked before being handed to callers.
3. `np.argmin()` crashes on an empty GCV list, giving a hard `ValueError` with no guard.
4. The declared SDK version floor (`ADVISOR_ANTHROPIC_MIN_VERSION = "0.72.0"`) is never verified at runtime.
5. When pydantic is absent but anthropic is present, `advise()` passes a plain Python class as `output_format`, producing an opaque SDK error rather than a clear `ImportError`.

Three warnings cover a misleading AIC/BIC diagnostic label, a dead variable in the FPCA branch, and a broken determinism check in the selfcheck helper.

---

## Critical Issues

### CR-01: NaN values in diagnostics violate JSON contract and corrupt the LLM user message

**File:** `python/fdars/advisor.py:302-313, 645-646, 899`

**Issue:** When `fdars.alignment.amplitude_distance` or `phase_distance` raises an exception, the fallback stores `float("nan")` in `amp_dists` / `phase_dists` (lines 302-303, 645-646). These values propagate into `diag["amplitude_distances"]`, `diag["amplitude_mean"]`, `diag["phase_distances"]`, `diag["mean_amplitude_separation"]`, etc. The module docstring explicitly guarantees "JSON-serialisable values" and the `_selfcheck` calls `json.dumps(d1)` to assert this, yet `float("nan")` is a Python float that `json.dumps` serialises as the bare token `NaN` — which is not valid per RFC 7159 and is rejected by strict parsers. When `advise()` calls `json.dumps(diagnostics, ...)` at line 899 to build the user message, the resulting string contains `NaN` literals that may cause the Anthropic API to return an error or silently pass a malformed payload to the model. The `_selfcheck` does not catch this because Python's `json.loads` is permissive about `NaN`, masking the contract break.

**Fix:** Replace `float("nan")` sentinel values with `None`, which serialises to `null` (valid JSON). Apply the replacement at all fallback sites:

```python
# In _build_alignment_diagnostics, line 302-303:
except Exception:
    amp = None   # was: float("nan")
    phase = None  # was: float("nan")

# Adjust nanmean/nanmax callers to handle None in the list:
amp_finite = [v for v in amp_dists if v is not None]
diag["amplitude_mean"] = float(np.mean(amp_finite)) if amp_finite else None
diag["amplitude_max"] = float(np.max(amp_finite)) if amp_finite else None
# Similarly for phase_dists and clustering pairwise distances (lines 645-646, 668-672).
```

---

### CR-02: `response.parsed_output` is `Optional[Advice]` — `None` return is never checked

**File:** `python/fdars/advisor.py:911`

**Issue:** The `ParsedMessage.parsed_output` property (confirmed in SDK 0.121.0 source) is typed `Optional[ResponseFormatT]` and returns `None` when no content block of type `"text"` has a truthy `parsed_output`. This happens when the model returns only a thinking block (no final text), when the response is a refusal, or when structured output parsing fails inside the SDK. Line 911 returns this value directly:

```python
return response.parsed_output
```

Callers typed to receive `Advice` will receive `None` and immediately get `AttributeError` on `.interpretation`, `.recommendations`, or `.caveats` — an opaque crash with no actionable error message.

**Fix:** Add an explicit guard and raise a descriptive error:

```python
parsed = response.parsed_output
if parsed is None:
    raise ValueError(
        "advise: the Anthropic API did not return a parseable Advice object. "
        "The model may have responded with only a thinking block or a refusal. "
        f"Raw response stop_reason: {response.stop_reason!r}"
    )
return parsed
```

---

### CR-03: `np.argmin()` raises `ValueError` on empty GCV list — no guard

**File:** `python/fdars/advisor.py:445, 524`

**Issue:** In `_build_basis_diagnostics` (line 445) and `_build_smoothing_diagnostics` (line 524), when a result dict is present with the keys `"n_basis_values"`/`"gcv"` (or `"lambda_values"`/`"gcv"`) but those lists are empty, the code proceeds to:

```python
min_gcv_idx = int(np.argmin(gcv_values))  # raises ValueError if gcv_values == []
```

`np.argmin([])` raises `ValueError: attempt to get argmin of an empty sequence`. This is an unguarded crash on valid-looking input and violates the contract that Branch A is a clean pass-through.

**Fix:** Add a guard before the argmin call in both functions:

```python
if not gcv_values:
    diag["n_basis_values"] = n_basis_values
    diag["gcv_curve"] = gcv_values
    diag["edf"] = edf_values
    diag["aic"] = None
    diag["bic"] = None
    diag["optimal_n_basis"] = None  # or optimal_lambda for smoothing
    diag["optimal_gcv"] = None
    diag["optimal_edf"] = None
    return diag
```

---

### CR-04: `ADVISOR_ANTHROPIC_MIN_VERSION` is declared but never enforced

**File:** `python/fdars/advisor.py:53, 695-714`

**Issue:** The module declares a minimum SDK version:

```python
ADVISOR_ANTHROPIC_MIN_VERSION = "0.72.0"
```

But `_require_anthropic()` only checks that `anthropic` is importable — it does not verify the installed version against this floor. With `anthropic < 0.72.0` (which predates `messages.parse(output_format=...)` and structured output support), the import succeeds, and the error surfaces later as an `AttributeError` or `TypeError` from the SDK with no actionable message. The version floor is the *only* enforcement point for the Phase 10 RESOLVED decision, and it is not enforced.

**Fix:** Add a version check inside `_require_anthropic()`:

```python
def _require_anthropic():
    try:
        import anthropic
    except ImportError as exc:
        raise ImportError(
            "The fdars advisor requires the anthropic SDK. "
            f"Install it with: pip install fdars[advisor]\n"
            f"Requires: anthropic>={ADVISOR_ANTHROPIC_MIN_VERSION}"
        ) from exc

    from packaging.version import Version
    if Version(anthropic.__version__) < Version(ADVISOR_ANTHROPIC_MIN_VERSION):
        raise ImportError(
            f"fdars advisor requires anthropic>={ADVISOR_ANTHROPIC_MIN_VERSION}; "
            f"found {anthropic.__version__}. Run: pip install 'anthropic>={ADVISOR_ANTHROPIC_MIN_VERSION}'"
        )
    return anthropic
```

If `packaging` is not a declared dependency, use a simple string-comparison tuple approach:

```python
installed = tuple(int(x) for x in anthropic.__version__.split(".")[:3])
floor = tuple(int(x) for x in ADVISOR_ANTHROPIC_MIN_VERSION.split(".")[:3])
if installed < floor:
    raise ImportError(...)
```

---

### CR-05: Missing pydantic guard — opaque SDK error when pydantic absent but anthropic present

**File:** `python/fdars/advisor.py:65-173, 907`

**Issue:** The module comment (lines 62-65) correctly notes that the Pydantic-backed `Advice` class is required for `advise()`, and asserts both missing-dependency paths "converge at the same `_require_anthropic()` guard." This is false. `_require_anthropic()` guards only against a missing `anthropic` package. If `pydantic` is absent but `anthropic` is present, `advise()` proceeds past the guard, then calls:

```python
response = client.messages.parse(
    ...
    output_format=Advice,   # Advice is the plain-Python fallback class, not a Pydantic model
    ...
)
```

The Anthropic SDK's `messages.parse` expects `output_format` to be a Pydantic `BaseModel` subclass and will raise an internal error (likely `AttributeError` or `TypeError` from inspecting Pydantic metadata on the fallback class). The user sees a cryptic SDK error rather than a clear `ImportError` naming `pip install fdars[advisor]`.

**Fix:** Add a `_require_pydantic()` guard function and call it from `advise()`:

```python
def _require_pydantic():
    try:
        import pydantic  # noqa: PLC0415
        return pydantic
    except ImportError as exc:
        raise ImportError(
            "The fdars advisor requires pydantic for structured output. "
            "Install it with: pip install fdars[advisor]"
        ) from exc

def advise(diagnostics, *, task, domain_context, model="claude-opus-4-8"):
    anthropic = _require_anthropic()
    _require_pydantic()   # <-- add this
    ...
```

---

## Warnings

### WR-01: AIC/BIC diagnostic keys use `log(GCV)` instead of `log(RSS/n)` — systematically biased label

**File:** `python/fdars/advisor.py:460-468, 537-543`

**Issue:** The `aic` and `bic` values are computed as:

```python
aic = n_obs * log(GCV) + 2 * edf
bic = n_obs * log(GCV) + log(n_obs) * edf
```

Standard AIC/BIC for linear smoothers use `log(RSS/n)`, not `log(GCV)`. GCV and RSS/n differ by a `(1 - edf/n)^2` denominator factor, so the `aic`/`bic` values returned are systematically offset from their standard definitions. A code comment acknowledges "AIC approximation from GCV + edf" but the diagnostic keys `aic` and `bic` are passed verbatim to the LLM system prompt context and cited in `Recommendation.evidence`, where they will be interpreted as standard AIC/BIC values by the model and users alike. This degrades the accuracy of the grounded recommendations.

**Fix:** Rename the keys to make the approximation explicit — e.g. `gcv_aic_approx` and `gcv_bic_approx` — and add a clarifying note in the diagnostics dict or docstring. If real AIC/BIC is desired, the relationship `RSS/n = GCV * (1 - edf/n)^2` can be used to recover an unbiased estimate when `n_obs` and `edf` are both available.

---

### WR-02: Dead variable `cumulative` in FPCA diagnostics branch — never stored in `diag`

**File:** `python/fdars/advisor.py:378`

**Issue:** Line 378 computes:

```python
cumulative = float(np.cumsum(evr)[-1]) if n_comp > 0 else 0.0
```

This variable is never assigned to `diag`. The intended diagnostic `diag["cumulative_variance_explained"]` is correctly populated from `cum_list` (line 385), and `cum_list[-1]` equals `cumulative` when `n_comp > 0`. The standalone `cumulative` variable is therefore dead code that adds confusion — it looks like a missing `diag["cumulative_variance_explained_scalar"] = cumulative` assignment.

**Fix:** Either remove the standalone `cumulative` variable entirely (since `cum_list[-1]` serves the same purpose) or add the missing assignment if a scalar summary was intended alongside the list:

```python
# Remove line 378 entirely, OR:
diag["cumulative_variance_explained_total"] = (
    float(np.cumsum(evr)[-1]) if n_comp > 0 else 0.0
)
```

---

### WR-03: `_selfcheck_alignment_diagnostics` assertion breaks when distance computation produces all-NaN results

**File:** `python/fdars/advisor.py:1059`

**Issue:** The determinism check at line 1059 asserts:

```python
assert d1 == d2, ...
```

Python dict equality for dicts containing `float("nan")` values always returns `False` because `float("nan") != float("nan")`. If `fdars.alignment.amplitude_distance` or `phase_distance` raises for all curves (putting `float("nan")` in `amp_dists` / `phase_dists`), then `d1["amplitude_mean"]` is `nan`, `d2["amplitude_mean"]` is also `nan`, and `d1 == d2` is `False` — the selfcheck fires a spurious `AssertionError` even though the function IS deterministic. The selfcheck also silently does nothing in environments where `fdars.alignment` is not importable (the import exception is swallowed by the per-curve `try/except Exception`, the values are `nan`, and then the assertion fails).

This is compounded by CR-01: once NaN is replaced with `None`, dict equality works correctly and the selfcheck becomes reliable.

**Fix:** This defect is fully resolved as a corollary of fixing CR-01 (replacing `float("nan")` with `None`). Once the distances return `None` on failure, dict equality works and the assertion is sound. No independent fix is needed beyond CR-01.

---

_Reviewed: 2026-08-09T18:52:32Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
