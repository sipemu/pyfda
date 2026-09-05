---
phase: 74-deepen-regression-family-thin-pages
plan: 01
type: tracer
subsystem: docs/regression
tags: [docs, depth, frechet, regression, fdars_fence_ok]
status: complete
completed: "2026-09-05"
duration_minutes: 3

dependency_graph:
  requires: []
  provides:
    - frechet-regression.md at mature-page parity (DEPTH-01 tracer done)
  affects:
    - docs/regression/frechet-regression.md
    - .planning/REQUIREMENTS.md (DEPTH-01 progress)

tech_stack:
  added: []
  patterns:
    - mature-page section template (When-to-use table + numbered sections + See-also)
    - FDARS_FENCE_OK sentinel fences (exec="1", html="1")
    - docs_fig.fig/render/fast pattern for inline matplotlib figure
    - corrected Petersen-Muller density-response API calls

key_files:
  created: []
  modified:
    - docs/regression/frechet-regression.md

decisions:
  - Density-response simulation uses normalised Gaussian bumps (np.trapezoid) — verified
    frechet_global_reg accepts them without ValueError (Assumption A2 validated)
  - "no_bare_p_value" structural check requires rewording admonition titles to avoid
    the bare token even inside backtick spans — changed warning title to "Two separate
    significance keys" form
  - Local regression bandwidth set to 1.5 (≈ std of x in [-1.5, 1.5]) for the
    combined global+local fence — passes without ValueError

metrics:
  duration_minutes: 3
  tasks_completed: 1
  tasks_total: 1
  commits: 1
  files_modified: 1

estimate:
  tokens: 62000

actuals:
  tokens: 13000
  tasks: 1
  commits: 1
---

# Phase 74 Plan 01: frechet-regression.md Parity (Tracer) Summary

Brought `docs/regression/frechet-regression.md` to full mature-page parity (DEPTH-01 tracer) — one page carried end-to-end through prose restructure, all six confirmed API-error corrections, admonitions, four runnable fences (including one html figure), cross-refs, and offline fence verification — before the other four pages follow the same proven pattern.

## What Was Built

`docs/regression/frechet-regression.md` restructured end-to-end to mirror the mature scalar-on-function template:

- **`## When to use` decision section** — method table (frechet_mean / global / local / anova) plus quick rule contrasting Fréchet (non-Euclidean response) vs SoF (Euclidean response)
- **`## See also` block** — links to scalar-on-function, regression-diagnostics, uncertainty-quantification, and index
- **Six API corrections applied** (all VERIFIED against `src/frechet_mod.rs`):
  1. `frechet_anova` signature corrected: `(responses, argvals, group_labels, n_perm=999, seed=42)` — no `objects`, no `space`, no `d`
  2. `frechet_anova` default `n_perm` corrected: 99 → **999**
  3. `frechet_anova` return dict corrected: full 9-key list (`statistic`, `p_value_asymptotic`, `p_value_permutation`, `n_perm`, `group_frechet_variances`, `pooled_frechet_variance`, `fn_statistic`, `un_statistic`, `group_labels`) — no bare `p_value`
  4. `frechet_local_reg` return dict corrected: `predicted / xout / bandwidth` (not `x_bar`)
  5. `xout` documented as 2D `(n_out, p)` — warning admonition + reshape example in fence
  6. `predictors` described as `(n, p)` scalar matrix; `responses` as `(n, m)` density matrix
- **Four runnable `FDARS_FENCE_OK` fences** (up from 1):
  1. Existing `frechet_mean` SPD fence (preserved)
  2. Combined `frechet_global_reg` + `frechet_local_reg` fence with corrected return key printout
  3. `html="1"` figure fence: predicted density curves at three predictor values
  4. `frechet_anova` fence with corrected signature and `fast(999, 99)` for DOCS_FAST builds
- **Seven admonitions** mixing `info` (density-response constraint), `warning` (xout 2D; two significance keys), `tip` (bandwidth guidance), `note` (group label requirement; R-methods-not-in-Python)
- **Bandwidth selection subsection** explaining locality trade-off
- **Result interpretation section** for predicted density curves (negative weights in extrapolation)
- **"Methods available in R but not (yet) in Python"** note covering Wasserstein barycenter and SPD affine-invariant geodesic regression

## Verification

Both required gates passed:

**Structural gate (node one-liner):**
```
STRUCT OK fences=4 adm=7 html=1
```
All 10 structural checks passed: `when_to_use`, `see_also`, `fences_ge3`, `adm_ge3`, `html_ge1`, `no_stale_anova_sig`, `has_asymptotic`, `has_permutation`, `no_bare_p_value`, `local_no_same3`.

**Fence gate (run_page_fences.py):**
```
ALL 4 EXEC FENCES EMITTED FDARS_FENCE_OK in docs/regression/frechet-regression.md
```

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Structural check `no_bare_p_value` tripped by admonition title**
- **Found during:** Structural gate run (first attempt)
- **Issue:** The initial `!!! warning "No bare \`p_value\` key"` title contained the bare `p_value` token as a backtick code span; the node check's `noHash` filter only strips `#`-prefixed heading lines, so admonition titles are tested
- **Fix:** Rewrote title to `"Two separate significance keys — asymptotic and permutation"` (avoids the bare token)
- **Files modified:** `docs/regression/frechet-regression.md`
- **Commit:** a6bae87 (inline with task commit, not separate)

### Assumptions Validated

- **A2 (density-response input):** `frechet_global_reg` accepted normalised Gaussian-bump rows without raising `ValueError`. Confirmed rows integrate to 1 via `np.trapezoid` — the binding does not enforce normalisation, and the fence ran successfully.
- **Bandwidth 1.5 for local regression fence:** No `ValueError`; predicted shapes correct at `(3, 30)`.

## Known Stubs

None — all fences are runnable and produce correct output. No placeholder text or TODO items remain on the page.

## Threat Flags

None — docs-only edit to one markdown page; no new attack surface.

## Self-Check: PASSED

- [x] `docs/regression/frechet-regression.md` exists and has the restructured content
- [x] Commit `a6bae87` exists in git log
- [x] Structural gate: PASSED (fences=4, adm=7, html=1, all 10 checks green)
- [x] Fence gate: PASSED (ALL 4 EXEC FENCES EMITTED FDARS_FENCE_OK)
