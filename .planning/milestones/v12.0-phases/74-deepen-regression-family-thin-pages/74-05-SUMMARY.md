---
phase: 74-deepen-regression-family-thin-pages
plan: "05"
subsystem: documentation
tags: [mkdocs, functional-glm, regression, fdars, DEPTH-01]

requires:
  - phase: 74-deepen-regression-family-thin-pages
    provides: frechet-regression.md tracer page pattern (74-01)

provides:
  - functional-glm.md at full parity (DEPTH-01): When-to-use + See-also + 4 fences + 5 admonitions
  - Gaussian-family comparison fence proving family="gaussian" == fregre_lm
  - Parameter-selection subsection using model_selection_ncomp
  - Gamma family example with domain constraint warning
  - See-also block linking scalar-on-function, classification, uncertainty-quantification, cross-validation, index

affects: [74-DEPTH-01, phase-79-gate, docs-regression]

actuals:
  tokens: 2967
  tasks: 1
  commits: 1

tech-stack:
  added: []
  patterns:
    - "FPC-score construction pattern for well-conditioned synthetic fences (scores @ phi basis)"
    - "model_selection_ncomp used as a pre-selection step before fitting the non-Gaussian GLM"

key-files:
  created: []
  modified:
    - docs/regression/functional-glm.md

key-decisions:
  - "Used FPC-score construction (scores @ phi basis) instead of RESEARCH Fence-3 pattern to avoid Cholesky singularity in fregre_lm with n_comp=3; n_comp=3 works with explicit FPC basis"
  - "family=gaussian comparison fence uses correlation of fitted values as the equivalence proof (not r_squared, which differs between GLM deviance and OLS)"
  - "Preserved all four existing references; sections renumbered from Theory straight into numbered examples (1. Binomial/Poisson, 2. Gaussian, 3. Parameter selection, 4. Gamma)"

patterns-established:
  - "FPC-score basis construction: scores @ phi + noise gives good FPCA conditioning for synthetic examples"

requirements-completed: [DEPTH-01]

coverage:
  - id: D1
    description: "functional-glm.md has ## When to use decision section and ## See also block"
    requirement: DEPTH-01
    verification:
      - kind: other
        ref: "node structural check: STRUCT OK fences=4 adm=5 html=1 fams=4"
        status: pass
    human_judgment: false
  - id: D2
    description: "All 4 exec fences emit FDARS_FENCE_OK offline under .venv"
    requirement: DEPTH-01
    verification:
      - kind: other
        ref: "PYTHONPATH=scripts DOCS_FAST=1 .venv/bin/python scripts/run_page_fences.py docs/regression/functional-glm.md"
        status: pass
    human_judgment: false

duration: 3min
completed: 2026-09-05
status: complete
---

# Phase 74 Plan 05: Functional GLM Parity Summary

**functional-glm.md brought to full parity (DEPTH-01): When-to-use decision section, gaussian-reduces-to-linear-SoF comparison fence, parameter-selection subsection via model_selection_ncomp, gamma family example, 5 admonitions, 4 FDARS_FENCE_OK fences (1 html)**

## Performance

- **Duration:** 3 min
- **Started:** 2026-09-05T19:50:42Z
- **Completed:** 2026-09-05T19:54:00Z
- **Tasks:** 1
- **Files modified:** 1

## Accomplishments

- Added `## When to use` decision section with method table (functional_glm vs functional_logistic vs fregre_lm) and quick rule
- Added `info` admonition: when functional_logistic is preferred over binomial GLM (returns predicted_classes, supports bootstrap_ci)
- Added Section 2: Gaussian family fence — proves `family="gaussian"` gives same fitted values as `fregre_lm` (correlation ~1.0); resolves conditioning issue from RESEARCH Fence-3 via explicit FPC-score basis construction
- Added Section 3: Parameter selection subsection using `model_selection_ncomp` (GCV/AIC/BIC profile) + `tip` admonition with 4 selection heuristics including the n_comp <= n/5 rule
- Added Section 4: Gamma family example (`y > 0` construction) with `warning` admonition covering all domain constraints and lowercase-only family strings (Pitfall 6 from RESEARCH)
- Preserved existing binomial+poisson html figure (Section 1), two-stage theory, link table, both verbatim admonitions (gamma inverse-link, AIC-not-comparable), full 15-key return dict table, and all 4 references
- Added `## See also` block: 5 links (scalar-on-function, classification, uncertainty-quantification, cross-validation, regression index)

## Task Commits

1. **Task 1: Bring functional-glm.md to full parity** - `734a301` (docs)

## Files Created/Modified

- `docs/regression/functional-glm.md` — Brought to full parity: When-to-use, gaussian/gamma examples, parameter selection, See-also

## Decisions Made

- Used FPC-score construction (`scores @ phi` basis) instead of RESEARCH Fence-3 pattern for the gaussian comparison fence. The RESEARCH pattern (`rng.standard_normal() * sin + cos`) produced near-singular FPC score matrices causing Cholesky failure in `fregre_lm` at `n_comp=3`. Explicit basis construction gives well-conditioned FPCA scores and allows `n_comp=3` for both estimators.
- family="gaussian" equivalence is demonstrated via correlation of fitted values (≈1.0 with explicit basis), not r_squared, because the GLM deviance and OLS r_squared use different denominators.
- Renumbered sections (1. Binomial/Poisson figure, 2. Gaussian, 3. Parameter selection, 4. Gamma) so the html figure stays in Section 1 and the new material builds naturally on top.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed RESEARCH Fence-3 Cholesky singularity**
- **Found during:** Task 1 (writing gaussian comparison fence)
- **Issue:** RESEARCH Section 7 Fence-3 data construction (`rng.standard_normal() * sin + cos` curves) produces near-singular FPC scores at `n_comp=3`, causing `fregre_lm` to raise `ValueError: Cholesky factorization failed`
- **Fix:** Replaced with explicit FPC-score construction (`scores = rng.standard_normal((n, 3)); phi = sin basis; X = scores @ phi + noise`), which gives well-conditioned FPCA scores. Both estimators now work at `n_comp=3` and the correlation of fitted values is ~1.0 as expected.
- **Files modified:** docs/regression/functional-glm.md
- **Verification:** Fence passes both structural gate and run_page_fences.py gate
- **Committed in:** 734a301

---

**Total deviations:** 1 auto-fixed (Rule 1 — data construction bug in research fence pattern)
**Impact on plan:** Necessary correction; the gaussian fence still demonstrates the same claim ("reduces to linear SoF") via correlation of fitted values. No scope change.

## Issues Encountered

None beyond the Cholesky singularity addressed above.

## User Setup Required

None — docs-only edit to one tracked page.

## Next Phase Readiness

- Phase 74 (Deepen Regression-Family Thin Pages) is complete: all 5 pages (frechet-regression, function-on-function, additive-sof, concurrent-regression, functional-glm) are at full parity (DEPTH-01)
- Phase 79 (--strict gate) will prove all fences green site-wide; per-page gates are already green
- No blockers for Phase 75 (analyze-family thin pages)

---

## Self-Check: PASSED

- docs/regression/functional-glm.md: FOUND
- Commit 734a301: FOUND
- Structural gate: STRUCT OK fences=4 adm=5 html=1 fams=4
- Fence gate: ALL 4 EXEC FENCES EMITTED FDARS_FENCE_OK

---
*Phase: 74-deepen-regression-family-thin-pages*
*Completed: 2026-09-05*
