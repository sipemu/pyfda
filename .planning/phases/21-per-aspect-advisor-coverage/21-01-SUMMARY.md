---
phase: 21-per-aspect-advisor-coverage
plan: "01"
subsystem: advisor
tags: [advisor, depth, build_diagnostics, aspect-threading, determinism]
status: complete

depends_on: []
provides:
  - depth aspect in build_diagnostics (ASPECT-02 partial)
  - _ASPECT_PRIMERS dict in _prompts.py (ASPECT-06)
  - aspect param in advise() (ASPECT-06)
  - caller-specified method enforcement test (ASPECT-07)
affects:
  - python/fdars/advisor/__init__.py
  - python/fdars/advisor/_prompts.py
  - python/fdars/advisor/aspects/depth.py (new)
  - tests/test_advisor.py

tech_stack:
  added: []
  patterns:
    - "Builder file pattern: aspects/depth.py with _build_depth_diagnostics accepting raw ndarray"
    - "Array-safe dispatcher: guard skips dict(raw) when __array__ or .data present"
    - "_ASPECT_PRIMERS dict: aspect -> FDA clause, injected in _system_prompt after FDA primer"

key_files:
  created:
    - python/fdars/advisor/aspects/depth.py
  modified:
    - python/fdars/advisor/__init__.py
    - python/fdars/advisor/_prompts.py
    - tests/test_advisor.py

decisions:
  - "depth branch accepts raw ndarray directly (not dict) — all fdars depth functions return PyArray1<f64>"
  - "_ASPECT_PRIMERS seeded with depth + 6 future aspects; aspect='' returns '' from .get, preserving backward compat"
  - "aspect param added to advise() as keyword-only after provider; threads to _system_prompt(task, aspect)"
  - "Array-coercion guard uses __array__ (ndarray) and .data (Fdata-like) to skip dict(raw); dict inputs unchanged"

metrics:
  duration: "~5 minutes"
  completed: "2026-08-12"
  tasks_completed: 3
  commits: 4

actuals:
  tokens: 9000
  tasks: 3
  commits: 4

requirements: [ASPECT-02, ASPECT-06, ASPECT-07]
---

# Phase 21 Plan 01: Depth Aspect Tracer Summary

End-to-end depth aspect (ASPECT-02 partial) + shared plumbing for per-aspect advisor coverage. The depth tracer proves the full vertical slice from raw ndarray input through the `build_diagnostics` dispatcher into the builder, with a deterministic JSON-serialisable output and backward-compatible prompt threading.

## One-liner

Depth aspect with `_build_depth_diagnostics(ndarray)` + array-safe dispatcher fix + `_ASPECT_PRIMERS` prompt threading + 4 Nyquist tests — all green, no regressions.

## What Was Built

### Task 1: Depth builder + array-safe dispatcher (tracer)

**`python/fdars/advisor/aspects/depth.py`** (new):
- `_build_depth_diagnostics(raw, *, method_name="unknown", **kwargs) -> dict`
- Accepts raw depth score ndarray `(n,)` directly — NOT a dict (per RESEARCH §1a)
- Computes: `method`, `method_name`, `n_obs`, `depth_min`, `depth_max`, `depth_mean`, `depth_median`, `depth_q10`, `depth_q90`, `depth_histogram` (10-bucket)
- Pure NumPy; all scalars wrapped `float()`/`int()` — no numpy scalar leaks

**`python/fdars/advisor/__init__.py`** changes:
- Added `"depth"` to `_supported` set
- Fixed BLOCKER #2 array-coercion guard: changed `if not isinstance(raw, dict):` to also skip `dict(raw)` when `hasattr(raw, "__array__")` (ndarray) or `hasattr(raw, "data")` (Fdata-like) — existing five aspects (all dict inputs) are byte-identical; depth score array and future Fdata input reach their builders safely
- Added depth dispatch branch: `if method_lc == "depth": from fdars.advisor.aspects.depth import _build_depth_diagnostics; return _build_depth_diagnostics(raw, **kwargs)`

**Verify (Task 1):**
```
.venv/bin/python -c "... build_diagnostics(np.array([...]), method='depth', method_name='fraiman_muniz') ..." -> OK
```

### Task 2: aspect param threading + _ASPECT_PRIMERS

**`python/fdars/advisor/_prompts.py`** changes:
- Added `_ASPECT_PRIMERS` module-level dict (depth clause + 6 future aspects) immediately after `_GROUNDING_INVARIANT` block
- Depth clause contains `depth_q10` token (test-assertable)
- Wired existing `aspect` stub param in `_system_prompt`: `aspect_primer = _ASPECT_PRIMERS.get(aspect.lower(), "")` then `base = base + aspect_primer`
- `aspect=""` returns `""` from `.get` — no primer injected, backward compat exact

**`python/fdars/advisor/__init__.py`** changes:
- Added `aspect: str = ""` keyword-only param to `advise()` (placed after `provider`)
- Changed `system = _system_prompt(task)` to `system = _system_prompt(task, aspect)`
- Documented param in docstring

**Verify (Task 2):** `_system_prompt('interpretation') == _system_prompt('interpretation','')` — PASS; `'depth_q10' in _system_prompt('interpretation','depth')` — PASS

### Task 3: Determinism + no-auto-detection tests

**`tests/test_advisor.py`** additions (within existing classes):

- `TestBuildDiagnosticsOffline.test_depth_build_diagnostics_basic` (Task 1 RED gate — now GREEN)
- `TestBuildDiagnosticsOffline.test_depth_deterministic` — two calls on fixed 10-element array produce equal dicts + byte-identical `json.dumps(sort_keys=True)`; recursive `check_no_numpy` walker asserts no `np.generic` leaks
- `TestBuildDiagnosticsOffline.test_no_auto_detection` — `build_diagnostics({"r_squared":0.9}, method="not_a_real_method")` raises `ValueError` matching `"unsupported method"`
- `TestBuildDiagnosticsOffline.test_aspect_caller_specified` — depth score array + `method="depth"` routes to depth branch; `diag["method"]=="depth"`
- `TestPrompts.test_prompt_aspect_backward_compatible` — `_system_prompt('interpretation') == _system_prompt('interpretation','')` and depth clause appears only when `aspect='depth'`

## Backward Compatibility

- `aspect=""` default in both `_system_prompt` and `advise()` — zero-change for all existing callers
- Dict-based dispatcher coercion path (`dict(raw)`) unchanged for existing five aspects (alignment, fpca, basis, smoothing, clustering) — none expose `__array__` or `.data`
- All 76 pre-existing advisor tests pass (0 regressions)

## Test Results

```
tests/test_advisor.py tests/test_advisor_providers.py tests/test_advisor_openai.py
tests/test_advisor_ollama.py tests/test_advisor_gemini*.py
=> 76 passed, 1 skipped
```

The skipped test is the LLM integration test (requires `ANTHROPIC_API_KEY`, expected CI skip).

## Commits

| Hash | Message |
|------|---------|
| 2531e94 | test(21-01): add failing RED test for depth branch in build_diagnostics |
| dbae6a7 | feat(21-01): depth builder + array-safe dispatcher + 'depth' in _supported |
| 0abe984 | feat(21-01): thread aspect param through advise() + add _ASPECT_PRIMERS in _prompts.py |
| 547d3f8 | test(21-01): add depth determinism + no-auto-detection + aspect-threading tests |

## Deviations from Plan

None — plan executed exactly as written. The array-coercion guard fix, builder file, dispatcher extension, prompt threading, and four tests were all implemented per plan specification.

## Known Stubs

None. All depth diagnostics fields are fully computed from the input ndarray.

## Threat Flags

None. T-21-01 (tamper guard via `np.asarray(raw, dtype=float)`) is implemented. T-21-02 (aspect selects static string, no user data in prompt path) is accepted as stated.

## Self-Check: PASSED

- `python/fdars/advisor/aspects/depth.py` — FOUND
- `python/fdars/advisor/__init__.py` — modified, `"depth"` in `_supported`, array guard fixed
- `python/fdars/advisor/_prompts.py` — `_ASPECT_PRIMERS` present, `aspect_primer` wired
- `tests/test_advisor.py` — 4 new test methods present
- Commits 2531e94, dbae6a7, 0abe984, 547d3f8 — all in `git log`
- `pytest tests/test_advisor.py` — 9 passed, 1 skipped
- Full suite (76 passed, 1 skipped) — confirmed
