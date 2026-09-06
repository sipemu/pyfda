---
phase: 74-deepen-regression-family-thin-pages
plan: 02
subsystem: docs/regression
tags: [docs, depth, function-on-function, fof, regression, fdars_fence_ok, predict_fof, fof_cv]
status: complete
completed: "2026-09-05"
duration_minutes: 2

dependency_graph:
  requires:
    - phase: 74-01
      provides: proven mature-page template (When-to-use + numbered sections + FDARS_FENCE_OK fences + html figure + See-also)
  provides:
    - function-on-function.md at mature-page parity (DEPTH-01)
  affects:
    - docs/regression/function-on-function.md

tech_stack:
  added: []
  patterns:
    - mature-page section template (When-to-use table + numbered sections + See-also)
    - FDARS_FENCE_OK sentinel fences (exec="1", html="1")
    - docs_fig.fig/render pattern for inline matplotlib heatmap figure
    - corrected predict_fof / fof_cv / fof_re_regression API calls

key_files:
  created: []
  modified:
    - docs/regression/function-on-function.md

key-decisions:
  - "predict_fof arg order: new_x is THIRD positional arg (before x_argvals, y_argvals) — verified src/regression_mod.rs:1339"
  - "fof_cv uses ncomp_x_max/ncomp_y_max integer ceilings — no range-list parameter; structural check reworded to avoid literal string match"
  - "fof_re_regression random-effects section left as prose + non-exec code block — RESEARCH Assumption A3 advises against tiny-n RE fence (convergence risk); API tables document the 13-key return dict accurately"
  - "beta_surface heatmap uses imshow with origin=lower, RdBu_r colormap — makes diagonal vs off-diagonal coefficient structure visible"

requirements-completed: [DEPTH-01]

coverage:
  - id: D1
    description: "function-on-function.md restructured to mature-page parity: When-to-use, numbered sections, corrected predict_fof/fof_cv/fof_re_regression API, interpretation section, See-also"
    requirement: DEPTH-01
    verification:
      - kind: other
        ref: "node structural gate: STRUCT OK fences=4 adm=8 html=1 (all 8 checks pass)"
        status: pass
      - kind: other
        ref: "scripts/run_page_fences.py: ALL 4 EXEC FENCES EMITTED FDARS_FENCE_OK"
        status: pass
    human_judgment: false

actuals:
  tokens: 4724
  tasks: 1
  commits: 1

metrics:
  duration_minutes: 2
  tasks_completed: 1
  tasks_total: 1
  commits: 1
  files_modified: 1

estimate:
  tokens: 58000
---

# Phase 74 Plan 02: function-on-function.md Parity Summary

`function-on-function.md` restructured to mature-page parity with all four confirmed API-error corrections applied, eight admonitions, four runnable FDARS_FENCE_OK fences (including a beta-surface heatmap figure), and both structural and fence gates passing.

## Performance

- **Duration:** 2 min
- **Started:** 2026-09-05T19:33:47Z
- **Completed:** 2026-09-05T19:35:49Z
- **Tasks:** 1
- **Files modified:** 1

## Accomplishments

- **`## When to use` decision table** — FoF vs concurrent vs SoF vs random-effects, with cross-links to `concurrent-regression.md` and `scalar-on-function.md`
- **Numbered method sections** — `fof_regression` (fit + 9-key return dict), `predict_fof` (corrected arg order), coefficient surface section (html heatmap), `fof_cv` (corrected params + 4-key return dict), interpretation, random-effects variant
- **Four API corrections** applied (all VERIFIED against `src/regression_mod.rs`):
  1. `predict_fof`: `new_x` is the THIRD positional argument (before argvals) — call and parameter table updated
  2. `fof_cv`: takes `ncomp_x_max`/`ncomp_y_max` integer ceilings, not a range list — rewritten call + warning admonition added
  3. `predict_fof_re`: `new_x` is FOURTH (after `subject_ids`) — documented in RE section
  4. `fof_re_regression`: `max_iter=50`, `tol=1e-10` params and 13-key return dict documented
- **8 admonitions** mixing `info` (non-square grids), `warning` × 3 (new_x arg order, no list param, predict_fof_re order), `note` × 2 (beta_surface orientation; excluded FPCA keys), `tip` (choosing ncomp_x_max/ncomp_y_max range)
- **4 runnable FDARS_FENCE_OK fences**: fof_regression fit, predict_fof (corrected arg order), html beta-surface heatmap, fof_cv with optimal result
- **`## See also`** linking concurrent-regression, function-on-scalar, scalar-on-function, cross-validation, and index
- **"Methods available in R but not (yet) in Python"** note covering basis-expansion FoF and historical covariance inspection tools

## Task Commits

1. **Task 1: Deepen function-on-function.md to parity + fix predict_fof/fof_cv API** — `9ec4443` (docs)

## Files Created/Modified

- `/home/simonm/projects/rust/pyfda/docs/regression/function-on-function.md` — restructured from 144 lines (thin) to 303 lines (mature parity); all API corrections applied

## Decisions Made

- **predict_fof warning phrasing**: Rewrote the structural-check admonition that mentioned the stale argument order to avoid using the literal old wrong signature as an exemplar — kept the fix visible via correct usage only.
- **fof_cv admonition title**: Initially titled "No ncomp_x_range parameter" — the structural gate `no_ncomp_range` checks for the literal string anywhere in the page (including warning text), so renamed to "Pass integer upper bounds, not a list" to clear the check while keeping the guidance.
- **Random-effects fence**: Per RESEARCH Assumption A3, `fof_re_regression` with tiny n/groups may not converge reliably. The RE section is prose + non-exec code block (the binding table documents the API accurately; no runnable fence). The four runnable fences satisfy the ≥3 requirement without the RE variant.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Structural check `no_ncomp_range` tripped by admonition title**
- **Found during:** Structural gate run (first attempt)
- **Issue:** The initial admonition `!!! warning "No ncomp_x_range parameter"` contained the literal `ncomp_x_range` string; the structural check `no_ncomp_range` tests `/ncomp_x_range/` anywhere in the page, including admonition titles.
- **Fix:** Renamed title to `"Pass integer upper bounds, not a list"` and rewrote body to describe the correct usage without the stale parameter name.
- **Files modified:** `docs/regression/function-on-function.md`
- **Commit:** `9ec4443` (inline with task commit, not separate)

---

**Total deviations:** 1 auto-fixed (Rule 1 — structural check false-positive in admonition title)
**Impact on plan:** Fix was correct and necessary — the check guards against stale API prose, and the warning text had reintroduced the string being guarded. Removing it is the right behaviour.

## Verification

Both required gates passed:

**Structural gate (node one-liner):**
```
STRUCT OK fences=4 adm=8 html=1
```
All 8 structural checks passed: `when_to_use`, `see_also`, `fences_ge3`, `adm_ge3`, `html_ge1`, `no_ncomp_range`, `has_ncomp_max`, `predict_newx_third`.

**Fence gate (run_page_fences.py):**
```
ALL 4 EXEC FENCES EMITTED FDARS_FENCE_OK in docs/regression/function-on-function.md
```

## Known Stubs

None — all fences are runnable and produce correct output. No placeholder text or TODO items remain.

## Threat Flags

None — docs-only edit to one markdown page; no new attack surface.

## Self-Check: PASSED

- [x] `docs/regression/function-on-function.md` exists and has the restructured content (303 lines)
- [x] Commit `9ec4443` exists in git log
- [x] Structural gate: PASSED (fences=4, adm=8, html=1, all 8 checks green)
- [x] Fence gate: PASSED (ALL 4 EXEC FENCES EMITTED FDARS_FENCE_OK)
