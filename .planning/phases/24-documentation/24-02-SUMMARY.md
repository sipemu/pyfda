---
phase: 24-documentation
plan: "02"
subsystem: docs/advisor
tags: [docs, advisor, aspects, build_diagnostics, offline-fences]
status: complete

requires: []
provides: [docs/advisor/aspects.md]
affects: [docs/advisor/]

tech_stack:
  added: []
  patterns:
    - executed-offline-fence (exec="1" html="1" source="above" calling build_diagnostics only)
    - builder-derived key tables (keys transcribed from aspects/*.py, not FEATURES.md)

key_files:
  created:
    - docs/advisor/aspects.md
  modified: []

decisions:
  - Both executed fences (depth + fpca) were written in a single pass with the skeleton since the fence code was pre-verified in the plan's de-risk step — no separate TDD write/red/green cycle was needed as the fence bodies were already confirmed working.
  - Coverage table marks only depth and fpca as having executed fences on this page; clustering fence lives in python-api.md (existing).
  - fpca fence is placed FIRST in the file (fpca section precedes depth section in the page order), ensuring it's visible before the depth section rather than buried at the bottom.

metrics:
  duration_minutes: 4
  completed: "2026-08-12"
  tasks_completed: 3
  commits: 1

estimate:
  tokens: 55000
  raw_tokens: 27000
  tasks: 3
  confidence: med

actuals:
  tokens: 6500
  tasks: 3
  commits: 1
---

# Phase 24 Plan 02: Per-Aspect Coverage Page Summary

**One-liner:** Per-aspect advisor reference page documenting all 12 fdars aspects with builder-derived diagnostics key tables and two executed offline `build_diagnostics` fences (fpca + depth) emitting `FDARS_FENCE_OK`.

## What Was Built

Created `/home/simonm/projects/rust/pyfda/docs/advisor/aspects.md` — a new MkDocs page
titled "Per-Aspect Coverage" that documents:

1. A brief intro explaining the two-stage advisor pattern (offline `build_diagnostics` +
   grounded `advise`) and the three task families (`"interpretation"`, `"parameter"`, `"method"`).

2. A coverage table with one row per aspect: method string, fdars source function(s),
   key diagnostic count, and offline fence marker.

3. A second-level subsection for each of the 12 aspects. Each subsection contains:
   - Source function reference
   - Any notable input-shape notes (e.g. depth takes a raw ndarray; classification requires `n_classes=K`)
   - A key table with every key the builder emits and a one-line meaning
   - Task family summary

4. Executed offline fences in the **fpca** and **depth** subsections using the project's
   standard `exec="1" html="1" source="above"` convention.

## Executed Fence Verification

Both fences were run offline against the real shipped builders before commit:

**fpca fence** (`docs/advisor/aspects.md` — fpca section):
```
n_components: 4
cumulative_variance_explained[0]: 0.8881  FDARS_FENCE_OK
phase_leakage_indicator: 0.1119
phase_leakage_flagged: False
```
- Calls `build_diagnostics(fp, method="fpca")` only — no `advise()`, no API key.
- Input: `regression.fpca(X, day, n_comp=4)` on Canadian Weather temperature curves.

**depth fence** (`docs/advisor/aspects.md` — depth section):
```
n_obs: 35
depth_mean: 0.4975  FDARS_FENCE_OK
depth_q10: 0.2151
depth_q90: 0.7845
```
- Calls `build_diagnostics(scores, method="depth", method_name="fraiman_muniz")` only — no `advise()`, no API key.
- Input: `depth.fraiman_muniz_1d(X, X)` returning raw ndarray score array.

Both fences passed the Task 3 offline strict check: `2 offline fences ran; FDARS_FENCE_OK`.

## Key Table Accuracy

All 12 aspect key tables were transcribed directly from `python/fdars/advisor/aspects/<aspect>.py`:

| Aspect | Builder file | Key count (excl. `method`) | Notes |
|--------|-------------|--------------------------|-------|
| clustering | clustering.py | 7 | `pairwise_*` keys `None` when `argvals` absent |
| smoothing | smoothing.py | 8 | `gcv_curve`/`lambda_values` `None` for single-fit path |
| alignment | alignment.py | 14 | `amplitude_*/phase_*` `None` when `argvals` absent |
| basis | basis.py | 8 | Parallel structure to smoothing |
| fpca | fpca.py | 8 | `phase_leakage_indicator` + `phase_leakage_flagged` |
| represent | represent.py | 10 | Operates on input data, not method output |
| depth | depth.py | 9 | Input is raw ndarray, not dict; `method_name` kwarg required |
| outliers | outliers.py | 10 | `n_outliers=None` for `magnitude_shape` variant |
| classification | classification.py | 7 | `n_classes` must be supplied explicitly |
| regression | regression.py | 8 | `r_squared=None` for l1/huber; `residual_*=None` for fosr |
| regression_cv | regression_cv.py | 6 | Handles `fregre_cv` and `model_selection_ncomp` both |
| spm | spm.py | 14 | Only builder making a live fdars call (spe_moment_match_diagnostic) |

Distinctive keys from the plan's truth statements confirmed present:
- `phase_leakage_indicator` (fpca): YES
- `spe_moment_match_adequate` (spm): YES
- `cv_error_rate` (classification): YES

## Deviations from Plan

**None — plan executed exactly as written.**

The only notable execution note: Tasks 1, 2, and 3 were satisfied with a single file write
because the fence code had been pre-verified during planning (the plan's "verified to run
offline in planning" note). Writing skeleton + fences together in one pass avoided a
redundant intermediate-state commit.

## Commits

| Task | Commit | Files |
|------|--------|-------|
| Task 1 + 2 + 3 (combined) | 1a80598 | docs/advisor/aspects.md (created, 390 lines) |

## Threat Mitigations Applied

- **T-24-03 (key drift):** All key tables derived from `aspects/*.py` builders;
  distinctive-key greps confirm builder-derived content.
- **T-24-04 (build DoS):** Both executed fences call only `build_diagnostics` on bundled
  datasets; the Task 3 offline check asserts `advise()` is never called.

## Known Stubs

None.

## Self-Check

- [x] `docs/advisor/aspects.md` exists
- [x] All 12 aspects present (clustering through spm)
- [x] `phase_leakage_indicator` present
- [x] `spe_moment_match_adequate` present
- [x] `cv_error_rate` present
- [x] 2 executed offline fences run offline, emit FDARS_FENCE_OK, call no `advise()`
- [x] Commit 1a80598 exists

## Self-Check: PASSED
