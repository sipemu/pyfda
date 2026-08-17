# Phase 33: Group C — Basis/Smoothing Quick Wins - Context

**Gathered:** 2026-08-17
**Status:** Ready for planning
**Mode:** Smart discuss (autonomous) — additive quick-wins fully determined by research + existing-binding precedent; no open user decisions

<domain>
## Phase Boundary

Additive extensions to the existing `fdars.basis` and `fdars.smoothing` submodules from fdars-core 0.20: `constant_basis` (all-ones intercept column), AIC-based basis roughness selection (`smooth_basis_aic` + `criterion="aic"` in `basis_nbasis_cv` / `BasisCriterion::Aic`), and AIC-based kernel-bandwidth selection (`aic_smoother` and/or `criterion="aic"` on the existing bandwidth-selection binding / `CvCriterion::Aic`). Covers BASIS-01, BASIS-02, BASIS-03. Depends on Phase 30 (green 0.20 baseline; the `CvCriterion` `#[non_exhaustive]` wildcard arm is already present in `optim_bandwidth`). Does NOT include docs (Phase 35, DOCS-06) or any advisor change.

</domain>

<decisions>
## Implementation Decisions (locked by research + existing-binding precedent)

### BASIS-01 — `constant_basis`
- `fdars.basis.constant_basis(argvals)` → an all-ones intercept-column `ndarray`. Read the exact 0.20 signature from vendored source `basis/constant.rs` (param name, return dimension: plain `Vec<f64>` of length m → 1-D ndarray via `vec_to_numpy1d`, OR `(m,1)` matrix). Bind to match the real signature; keep it a thin wrapper alongside the existing `bspline_basis`/`fourier_basis` bindings in `src/basis_mod.rs`. Add a test asserting the output is all ones with the expected length/shape.

### BASIS-02 — AIC basis smoothing
- `fdars.smoothing.smooth_basis_aic(...)` → PyDict. Structurally identical to the existing `smooth_basis_gcv` binding — copy that binding, swap the fdars-core call to `smooth_basis_aic`, keep the same param set and `SmoothBasisResult`→PyDict field mapping (`coefficients`, `fitted`, `edf`, `aic`, `gcv`, `bic`, `nbasis`). `smooth_basis_aic` returns `Option<...>` → map `None` to `PyValueError` (mirror `smooth_basis_gcv`'s None handling). Confirm exact signature + fields against vendored `smooth_basis.rs`.
- `basis_nbasis_cv` gains `criterion="aic"`: the existing binding already dispatches a `criterion: &str` to `BasisCriterion`; add `"aic" => BasisCriterion::Aic` to that match (`BasisCriterion` is NOT `#[non_exhaustive]`, per research — no wildcard needed there, but keep the existing fallback). Confirm the existing accepted criterion strings before adding.

### BASIS-03 — AIC kernel bandwidth
- Add AIC as a kernel-bandwidth-selection criterion. Read `smoothing.rs` to determine the real surface: (a) if a distinct `aic_smoother` function exists, bind it (thin, mirroring `optim_bandwidth`); AND/OR (b) extend the existing `optim_bandwidth` binding to accept `criterion="aic"` on input (dispatch to `CvCriterion::Aic`) and, on the OUTPUT side, replace the Phase-30 stopgap `CvCriterion::Aic => "unknown"` arm in `src/smoothing_mod.rs` with `CvCriterion::Aic => "aic"` so an AIC-selected result reports its real criterion. The `_ =>` forward-compat fallback added in Phase 30 stays for any future non_exhaustive variant.
- Prefer binding whatever the crate actually exposes; the goal (per BASIS-03) is that a user can select an AIC-optimal kernel bandwidth. Add a test that AIC selection runs and returns a sane bandwidth/criterion.

### Conventions (from Phase 30–32 precedent)
- Compound results → PyDict; `Vec<f64>` → `vec_to_numpy1d`; matrices → `fdmatrix_to_numpy2d` (with a shape round-trip check if any matrix crosses the boundary). No `.unwrap()` (route via `to_pyresult()` / map `Option::None` → `ValueError`). `pytest.raises(ValueError)` for degenerate inputs (e.g. unknown criterion string, degenerate smoothing). rustfmt + clippy `-D warnings` clean; Cargo.lock not committed.

### Claude's Discretion
- Exact placement (`constant_basis` in `basis_mod.rs`; AIC smoothing in `smoothing_mod.rs`), test file layout, and whether BASIS-03 binds a new `aic_smoother` vs only extending `optim_bandwidth`'s criterion — decided at plan/execute time from the vendored source, following the closest existing analog.

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `src/basis_mod.rs` — existing `bspline_basis`/`fourier_basis` + `basis_nbasis_cv` (with its `criterion: &str` → `BasisCriterion` dispatch). Extend here for `constant_basis` + `"aic"` criterion.
- `src/smoothing_mod.rs` — existing `smooth_basis_gcv` (copy for `smooth_basis_aic`) and `optim_bandwidth` (the `CvCriterion` match with the Phase-30 `_ => "unknown"` output arm to update to `Aic => "aic"`; and its input `criterion` dispatch to extend with `"aic"`).
- `src/convert.rs` — `vec_to_numpy1d`, `fdmatrix_to_numpy2d`, `to_pyresult`.

### Established Patterns
- Phases 30–32 precedent: string-criterion dispatch, PyDict compound results, `Option::None`/`Result::Err` → `PyValueError`, no `.unwrap()`.
- Vendored 0.20.0 source (authoritative): `.../fdars-core-0.20.0/src/basis/constant.rs` (constant_basis), `.../basis/auto_select.rs` (basis_nbasis_cv + BasisCriterion variants incl. Aic), `.../smooth_basis.rs` (smooth_basis_aic + SmoothBasisResult), `.../smoothing.rs` (optim_bandwidth + CvCriterion + any aic_smoother). Phase 31's `31-SIGNATURES.md` and research FEATURES.md sections C1–C3 also record these.

### Integration Points
- Edits confined to `src/basis_mod.rs`, `src/smoothing_mod.rs`, `tests/`. Build via `maturin develop`; test via pytest. Both submodules already registered — no new submodule.

</code_context>

<specifics>
## Specific Ideas

- Test datasets (from research): Canadian Weather (35×365) or Tecator (240×100) for `smooth_basis_aic` / AIC bandwidth. A natural comparison test: run `smooth_basis_gcv` and `smooth_basis_aic` on the same small data and assert both return valid dicts (AIC-selected λ/EDF may differ from GCV — do not assert equality, just validity). `constant_basis` demonstrated inline (all-ones vector).
- Keep test data small; AIC/GCV grid searches can be slow on large inputs.

</specifics>

<deferred>
## Deferred Ideas

- Docs page + worked example for the basis/smoothing additions → Phase 35 (DOCS-06).
- `*_with_config` API variants — explicitly out of scope (bind only the primary functions).

</deferred>
