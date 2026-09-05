---
phase: quick-260905-htx
plan: "01"
subsystem: api
tags: [fdata, interpolation, resampling, convenience-methods, docs, pytest, tdd]

requires: []
provides:
  - Fdata.resample(n_points=N|factor=F) delegates to interpolate() with linspace grid
  - Fdata.upsample(factor) — ceil-based, factor > 1 guard
  - Fdata.downsample(factor) — int-floor-based, max(2,...), factor > 1 guard
  - Extended interpolation.md docs page with Resampling convenience methods section
  - 22 new pytest cases in TestFdataResampleMethods
affects: [docs-represent, fdata-api, represent-tests]

actuals:
  tokens: 9200
  tasks: 3
  commits: 3

tech-stack:
  added: [math (stdlib, added to fdata_class.py imports)]
  patterns:
    - "resample/upsample/downsample follow the same delegate-to-interpolate() pattern as impute()"
    - "TDD RED/GREEN cycle: failing tests committed first, then implementation"
    - "boundary policy default for linspace grids whose endpoints coincide with domain edges"

key-files:
  created: []
  modified:
    - python/fdars/fdata_class.py
    - docs/represent/interpolation.md
    - tests/test_represent.py

key-decisions:
  - "policy='boundary' default for resample/upsample/downsample: linspace endpoints coincide with domain edges so boundary avoids floating-point edge exceptions"
  - "upsample uses math.ceil, downsample uses max(2, int(//)) to guarantee correct direction and minimum 2 points"
  - "resample(factor=F) uses round() for neutral rounding; upsample uses ceil() to guarantee strictly more points"

patterns-established:
  - "Pure-Python convenience wrappers on Fdata build grid with np.linspace and call self.interpolate() — no new Rust required"

requirements-completed: [QUICK-RESAMPLE]

coverage:
  - id: D1
    description: "Fdata.resample(n_points=N) returns Fdata with exactly N points on uniform linspace over rangeval"
    requirement: QUICK-RESAMPLE
    verification:
      - kind: unit
        ref: "tests/test_represent.py#TestFdataResampleMethods::test_resample_n_points_count"
        status: pass
      - kind: unit
        ref: "tests/test_represent.py#TestFdataResampleMethods::test_resample_n_points_argvals_linspace"
        status: pass
    human_judgment: false
  - id: D2
    description: "Fdata.resample(factor=F) returns Fdata with round(n_points * F) points"
    requirement: QUICK-RESAMPLE
    verification:
      - kind: unit
        ref: "tests/test_represent.py#TestFdataResampleMethods::test_resample_factor_count"
        status: pass
    human_judgment: false
  - id: D3
    description: "resample raises ValueError when both/neither of n_points/factor given, or target < 2"
    requirement: QUICK-RESAMPLE
    verification:
      - kind: unit
        ref: "tests/test_represent.py#TestFdataResampleMethods::test_resample_neither_arg_raises"
        status: pass
      - kind: unit
        ref: "tests/test_represent.py#TestFdataResampleMethods::test_resample_both_args_raises"
        status: pass
      - kind: unit
        ref: "tests/test_represent.py#TestFdataResampleMethods::test_resample_target_less_than_2_raises"
        status: pass
    human_judgment: false
  - id: D4
    description: "Fdata.upsample(factor) returns Fdata with ceil(n * factor) points; factor > 1 enforced"
    requirement: QUICK-RESAMPLE
    verification:
      - kind: unit
        ref: "tests/test_represent.py#TestFdataResampleMethods::test_upsample_count_ceil"
        status: pass
      - kind: unit
        ref: "tests/test_represent.py#TestFdataResampleMethods::test_upsample_strictly_greater"
        status: pass
      - kind: unit
        ref: "tests/test_represent.py#TestFdataResampleMethods::test_upsample_factor_equal_1_raises"
        status: pass
      - kind: unit
        ref: "tests/test_represent.py#TestFdataResampleMethods::test_upsample_factor_less_than_1_raises"
        status: pass
    human_judgment: false
  - id: D5
    description: "Fdata.downsample(factor) returns Fdata with max(2, int(n/factor)) points; factor > 1 enforced"
    requirement: QUICK-RESAMPLE
    verification:
      - kind: unit
        ref: "tests/test_represent.py#TestFdataResampleMethods::test_downsample_count"
        status: pass
      - kind: unit
        ref: "tests/test_represent.py#TestFdataResampleMethods::test_downsample_strictly_fewer"
        status: pass
      - kind: unit
        ref: "tests/test_represent.py#TestFdataResampleMethods::test_downsample_large_factor_clamps_to_2"
        status: pass
    human_judgment: false
  - id: D6
    description: "interpolation.md Resampling convenience methods section with table and markdown-exec fence"
    requirement: QUICK-RESAMPLE
    verification:
      - kind: other
        ref: "grep -q 'Resampling convenience methods' docs/represent/interpolation.md && echo OK"
        status: pass
      - kind: other
        ref: "Direct Python fence execution: upsample(4)=124pts, downsample(3)=10pts, FDARS_FENCE_OK printed"
        status: pass
    human_judgment: true
    rationale: "Full MkDocs build visual confirmation of the rendered page (figures, fence HTML output) requires human review. Fence was executed directly in Python and produced correct output (upsample(4)=124>31, downsample(3)=10<31, FDARS_FENCE_OK), but rendered HTML/figure appearance in the built site requires human eyes."

duration: 55min
completed: 2026-09-05
status: complete
---

# Quick Task 260905-HTX: Resample / Upsample / Downsample Convenience Methods Summary

**Three pure-Python Fdata convenience methods (`resample`, `upsample`, `downsample`) delegating to `interpolate()` via linspace grid, with 22 new pytest cases (TDD) and extended interpolation.md docs page.**

## Performance

- **Duration:** ~55 min (includes background docs build wait)
- **Started:** 2026-09-05T12:55Z
- **Completed:** 2026-09-05T13:50Z
- **Tasks:** 3 (Task 1 TDD complete, Task 2 complete, Task 3 partially automated — see below)
- **Files modified:** 3

## Accomplishments

- Added `Fdata.resample(n_points=N|factor=F)` — validates exactly-one arg, builds np.linspace grid, delegates to `self.interpolate()` with `policy="boundary"` default
- Added `Fdata.upsample(factor)` — factor > 1 guard, `math.ceil` rounding, returns strictly more points
- Added `Fdata.downsample(factor)` — factor > 1 guard, `max(2, int(n/factor))`, returns fewer points (minimum 2)
- Added `import math` to `fdata_class.py` (not previously imported)
- All three carry full NumPy-style docstrings (Parameters, Returns, Raises, Examples)
- 22 new pytest cases in `TestFdataResampleMethods` — all pass (TDD RED/GREEN cycle)
- Extended `docs/represent/interpolation.md` with "Resampling convenience methods" section: prose, method-summary table, and runnable markdown-exec fence using `load_growth()` + `Fdata.upsample(4)` / `Fdata.downsample(3)`

## Task Commits

1. **Task 1 RED: Failing tests** — `addd550` (test)
2. **Task 1 GREEN: Implementation** — `88f8626` (feat)
3. **Task 2: Docs** — `364910b` (docs)

## Files Created/Modified

- `/home/simonm/projects/rust/pyfda/python/fdars/fdata_class.py` — added `import math` and three new methods (`resample`, `upsample`, `downsample`) after `interpolate()`
- `/home/simonm/projects/rust/pyfda/tests/test_represent.py` — appended `TestFdataResampleMethods` class (22 test cases)
- `/home/simonm/projects/rust/pyfda/docs/represent/interpolation.md` — new "Resampling convenience methods" section with method table and markdown-exec fence

## Decisions Made

- **policy="boundary" default:** linspace endpoints coincide with domain edges; boundary safely handles floating-point edge cases where the computed endpoint barely overshoots the domain. Confirmed that `spline_interpolate_with_policy` supports this value.
- **resample uses round(), upsample uses ceil():** `round()` gives neutral rounding for `resample(factor=F)`; `math.ceil()` guarantees the result is *strictly more* than source for `upsample`.
- **downsample clamps to max(2, ...):** prevents target < 2 even with extreme factors, consistent with ValueError behavior in `resample`.
- **No 2-D handling:** follows same 1-D limitation as `interpolate()`.

## Deviations from Plan

None — plan executed exactly as specified.

## Task 3: Docs Build Status

Task 3 is a `checkpoint:human-verify` with `gate="blocking-human"`. The following was completed automatically:

**Automated checks passed:**
- `grep -q "Resampling convenience methods" docs/represent/interpolation.md` — OK
- `grep -c "FDARS_FENCE_OK" docs/represent/interpolation.md` — 1 occurrence found
- Direct Python fence execution (no MkDocs, raw Python against current API):
  - `upsample(4)` on 31-point growth data → 124 points (124 > 31, correct)
  - `downsample(3)` on 31-point growth data → 10 points (10 < 31, correct)
  - `FDARS_FENCE_OK` sentinel printed, no tracebacks

**Requires human confirmation:**
The full MkDocs build (`PYTHONPATH=scripts DOCS_FAST=1 .venv/bin/mkdocs build`) was started as a background process and was still running at task completion time. The human should:
1. Wait for the background build to complete (or run it fresh)
2. Open the rendered `site/represent/interpolation/index.html`
3. Confirm: (a) "Resampling convenience methods" section renders, (b) the fence executed (figures + FDARS_FENCE_OK visible, no tracebacks), (c) n_points printout shows upsample=124 > 31 and downsample=10 < 31

## Issues Encountered

None — all methods implemented cleanly without blocking issues.

## Next Phase Readiness

- `Fdata.resample/upsample/downsample` are immediately available to users
- No Rust rebuild required (pure Python)
- QUICK-RESAMPLE requirement satisfied
- Human docs-build confirmation is the only remaining step

---
*Quick task: 260905-htx*
*Completed: 2026-09-05*
