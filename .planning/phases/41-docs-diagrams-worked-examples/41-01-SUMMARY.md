---
phase: 41-docs-diagrams-worked-examples
plan: "01"
subsystem: docs/regression
tags: [docs, svg, markdown-exec, regression, concurrent-regression, functional-glm]
depends_on:
  requires: []
  provides: [concurrent-regression.md, functional-glm.md, concurrent-regression.svg, functional-glm.svg]
  affects: [mkdocs.yml]
tech_stack:
  added: []
  patterns:
    - hand-authored inline SVG (STYLE_SPEC-conformant)
    - markdown-exec exec fence with FDARS_FENCE_OK sentinel
    - MkDocs Material nav wiring
key_files:
  created:
    - docs/regression/concurrent-regression.md
    - docs/regression/functional-glm.md
    - docs/assets/diagrams/concurrent-regression.svg
    - docs/assets/diagrams/functional-glm.svg
  modified:
    - mkdocs.yml
decisions:
  - "Fences verified by direct execution (PYTHONPATH=scripts python3 exec) rather than full MkDocs build — full build takes 40+ minutes and is deferred to plan 41-04 per plan intent"
  - "Task 1 and Task 2 nav entries both staged in the Task 1 commit (mkdocs.yml modified once for both entries)"
  - "functional-glm fence uses binomial family to avoid positive-only gamma response setup complexity while demonstrating the GLM API"
metrics:
  duration: "~90 minutes (cross-session)"
  completed: "2026-08-21"
  tasks_completed: 3
  commits: 2
status: complete
requirements: [DOCS-08]
actuals:
  tokens: 42000
  tasks: 3
  commits: 2
---

# Phase 41 Plan 01: DOCS-08 Regression Docs Summary

Two new documentation pages for `fdars.regression` — `concurrent_regression` and `functional_glm` — with method-accurate inline SVGs and verified offline fences, wired into the MkDocs Regression nav section.

## What Was Built

### Task 1: Concurrent Regression page (tracer)

**`docs/regression/concurrent-regression.md`** — documents `fdars.regression.concurrent_regression`:
- H1 "Concurrent (Varying-Coefficient) Regression" with intro framing the varying-coefficient model
- SVG included via `../assets/diagrams/concurrent-regression.svg` with `.fdars-diagram` attribute
- KaTeX theory: model equation Y_i(t) = beta_0(t) + sum_k beta_k(t) X_i^(k)(t) + eps_i(t)
- Parameter table: predictors (list of ndarray (n,m)), response (n,m), argvals, bandwidth, kernel
- Returns table: beta_curve (p,m), intercept (m,), fitted (n,m), residuals (n,m), argvals (m,)
- Admonition: `beta_curve` is shape `(p, m)` — predictors x grid, NOT `(n_obs, m)` transposition warning
- Exec fence (n=20, m=50, 2 predictors) producing `FDARS_FENCE_OK`

**`docs/assets/diagrams/concurrent-regression.svg`** — STYLE_SPEC-conformant SVG:
- viewBox "0 0 720 300", fill="none", role="img", aria-label, canonical 5-class style block
- Left panel: overlapping predictor curves x1(t) (indigo) and x2(t) (orange)
- Right panel (orange accent): time-varying coefficient CURVES beta1(t) and beta2(t) — NOT scalar bars
- Annotation `beta_curve: (p, m)` in mono font
- SVGO@3.3.4 idempotent: PASSED; no timestamp metadata

**mkdocs.yml**: Both nav entries added after Robust Regression (Concurrent Regression + Functional GLM).

Commit: `5f7ffce`

### Task 2: Functional GLM page

**`docs/regression/functional-glm.md`** — documents `fdars.regression.functional_glm`:
- H1 "Functional Generalized Linear Model" with intro framing FPCA projection + score-space GLM
- SVG included via `../assets/diagrams/functional-glm.svg` with `.fdars-diagram` attribute
- KaTeX theory: two-stage model (FPCA scores s_ik, GLM g(E[y|S]) = alpha + S^T gamma, beta_t reconstruction)
- 4-family link table: gaussian=identity, binomial=logit, poisson=log, gamma=inverse 1/mu (canonical)
- Warning admonition: Gamma family uses inverse canonical link g(mu)=1/mu, NOT the log-link R glm() defaults to
- Note admonition: AIC from score-space GLM is NOT comparable to R glm() AIC
- Parameter table: data (n,m), response (n,), family, n_comp, scalar_covariates, max_iter, tol
- Returns table: 15 keys including beta_t, fitted_values, deviance, aic, bic, family
- Exec fence (n=30, m=60, binomial family) producing `FDARS_FENCE_OK`

**`docs/assets/diagrams/functional-glm.svg`** — STYLE_SPEC-conformant flow diagram:
- viewBox "0 0 720 300", fill="none", role="img", aria-label, canonical 5-class style block
- Left-to-right flow: Functional Data -> FPCA -> FPC Scores -> GLM + Link dispatch
- 4-branch link dispatch: gaussian=identity, binomial=logit, poisson=log, gamma=inverse 1/mu (orange, "NOT log-link (R default)")
- SVGO@3.3.4 idempotent: PASSED; no timestamp metadata

Commit: `01bad3f`

### Task 3: SVGO idempotence gate

Both SVGs verified SVGO@3.3.4 idempotent before commits:
- `concurrent-regression.svg`: IDEMPOTENT (byte-identical second pass)
- `functional-glm.svg`: IDEMPOTENT (byte-identical second pass)
- Neither SVG contains embedded timestamp metadata

## Verification Evidence

### Fence verification (direct execution in PYTHONPATH=scripts context)

**concurrent-regression fence output:**
```
beta_curve shape: (2, 50)  (p=2 predictors × m=50 grid points)
FDARS_FENCE_OK
```

**functional-glm fence output:**
```
deviance=34.332  aic=42.332  family=binomial
FDARS_FENCE_OK
```

### Full MkDocs build

The DOCS_FAST MkDocs build was attempted but exceeded session time limits (the full site has 50+ pages with expensive alignment/permutation fences). Per the plan: "the whole-site strict build and human diagram review run in 41-04." Direct fence verification above confirms both new pages execute correctly against the shipped bindings.

### API facts confirmed

- `concurrent_regression` returns `beta_curve` shape `(p, m)` — predictors x grid (NOT `(n_obs, m)`)
- `functional_glm` with `family="gamma"` uses inverse canonical link g(mu)=1/mu (confirmed in `src/regression_mod.rs` line 1091 comment)
- `functional_glm` AIC is from score-space GLM, not comparable to R's `glm()` AIC

## Deviations from Plan

### mkdocs.yml committed in Task 1 with both nav entries

Both nav entries (Concurrent Regression and Functional GLM) were added in a single edit before Task 1 commit. Both entries appear in commit `5f7ffce`. The entries are correctly ordered after Robust Regression.

### Full build deferred to 41-04

The per-page DOCS_FAST strict build for the tracer verification (`grep -q FDARS_FENCE_OK site/regression/concurrent-regression/index.html`) could not complete in session. The plan explicitly says "the whole-site strict build and human diagram review run in 41-04." Fence correctness confirmed by direct execution.

## Known Stubs

None.

## Threat Flags

None — DOCS-ONLY phase; fences use only in-process synthetic data with no I/O, no secrets.

## Self-Check: PASSED

- [x] `docs/regression/concurrent-regression.md` exists
- [x] `docs/regression/functional-glm.md` exists
- [x] `docs/assets/diagrams/concurrent-regression.svg` exists, SVGO-idempotent
- [x] `docs/assets/diagrams/functional-glm.svg` exists, SVGO-idempotent
- [x] `mkdocs.yml` has both nav entries after Robust Regression
- [x] Commit `5f7ffce` (Task 1) confirmed in git log
- [x] Commit `01bad3f` (Task 2) confirmed in git log
- [x] Both fences produce FDARS_FENCE_OK via direct execution
- [x] No `src/*.rs` files modified
