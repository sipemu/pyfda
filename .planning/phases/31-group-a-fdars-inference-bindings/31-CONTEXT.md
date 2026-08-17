# Phase 31: Group A — `fdars.inference` Bindings - Context

**Gathered:** 2026-08-17
**Status:** Ready for planning
**Mode:** Smart discuss (autonomous) — grey areas accepted by user

<domain>
## Phase Boundary

Expose the full fdars-core 0.20 functional-inference surface (8 functions) through a NEW `fdars.inference` PyO3 submodule + Python API: two-sample permutation tests (`t_perm_test`, `f_perm_test`), asymptotic two-sample mean test (`two_sample_mean_test`), simultaneous confidence bands (`mean_scb`, `scb_two_sample_test`), functional-linear-model post-hoc inference (`flm_f_test`, `flm_gof_test`), and one-way functional ANOVA V-statistic (`oneway_anova_vstat`). Covers INFER-01…09. Depends on Phase 30 (green 0.20 baseline). Does NOT include the advisor `inference` aspect (Phase 34) or docs (Phase 35).

</domain>

<decisions>
## Implementation Decisions

### FLM inference ergonomics
- `flm_f_test` / `flm_gof_test` **re-fit the model internally**: the Python wrapper accepts raw `data + response + n_comp` (mirroring the existing `fdars.regression` FLM-fit param names/order), calls `fdars_core::scalar_on_function::fregre_lm` to build a `FregreLmResult` in Rust, then passes `&FregreLmResult` to the upstream test. Rationale: `FregreLmResult` is a non-pyclass Rust struct that cannot cross to Python; re-fit matches the v4.0 `predict_fregre_lm` precedent and avoids a handle registry. Bind the two FLM tests symmetrically. (Confirm the exact 0.20 `flm_f_test`/`flm_gof_test` signature + the `scalar_on_function` module path at plan-time — a flagged spike.)

### Parameter defaults & determinism
- Permutation count default `n_perm=999` (upstream `DEFAULT_N_PERM`, matches R `fda`).
- All `u64` seeds exposed to Python as `seed=None`, resolved to a **fixed default (0)** internally so two calls with the same args are byte-identical (required for offline advisor/docs determinism). `two_sample_mean_test` and `oneway_anova_vstat` are asymptotic/seedless (`n_perm=0` in their result).
- `two_sample_mean_test` FPC component count default `ncomp=5`, docstring notes to keep it small relative to `min(n_a, n_b)`.
- `mean_scb`/`scb_two_sample_test` `multiplier` selected by **string** (e.g. `"gaussian"`/`"rademacher"`) with a `ValueError` fallback arm; exact `MultiplierDistribution` variant names verified at plan-time (docs.rs 404 — flagged spike). Also confirm the SCB param set (`bandwidth`, `nb`, `confidence`).

### Result & submodule conventions (locked by roadmap + research — recorded, not re-litigated)
- Every function returns a **PyDict**. `TestResult` → `{statistic, p_value, n_perm}`. `mean_scb` returns a `ToleranceBand` → `{lower, upper, center, half_width}` (each a 1-D ndarray of length m). `scb_two_sample_test` returns `TestResult`. (Confirm whether a `toleranceband_to_pydict` helper already exists in `convert.rs` from the `fdars.tolerance` bindings and reuse it.)
- New submodule: `src/inference_mod.rs` + `register_submodule!` in `src/lib.rs` + `"inference"` added to `_submodule_names` in `python/fdars/__init__.py` — mirroring the v4.0 `fdars.represent`/`fdars.scoring` new-submodule pattern. Importable both as `fdars.inference.fn` and `from fdars.inference import fn`.
- `oneway_anova_vstat` accepts a Python int array/list of group labels (`groups`), converted to `Vec<usize>`; documented **0-indexed** (confirm 0- vs 1-base at plan-time — flagged spike).
- All fallible fns routed through `to_pyresult()`; NO `.unwrap()`. Degenerate inputs (mismatched grids, too-few curves, invalid `ncomp`/`multiplier`) raise `ValueError`, with `pytest.raises(ValueError)` tests.
- Any matrix/band field crossing numpy↔FdMatrix uses the established conversion helpers; `TestResult` is scalar-only (no transposition risk), but SCB band arrays get a shape/finite round-trip assertion.
- Bind ALL 8 Group A functions this phase (full inference surface — no partial launch).

### Claude's Discretion
- Exact test file layout, per-function test data construction, and internal helper factoring are at Claude's discretion, guided by the existing `src/*_mod.rs` + `tests/` conventions.

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `src/lib.rs` — `register_submodule!` macro + submodule registration list (add `inference_mod`).
- `python/fdars/__init__.py` — `_submodule_names` tuple (add `"inference"`).
- `src/convert.rs` — `numpy2d_to_fdmatrix`, `fdmatrix_to_numpy2d`, `to_pyresult()`/`to_pyerr()`; check for an existing `ToleranceBand`→PyDict helper (from `fdars.tolerance`).
- `src/represent_mod.rs` / `src/scoring_mod.rs` — the v4.0 new-submodule precedent to copy structurally.
- The existing `fdars.regression` FLM-fit binding — source the param names/order for the re-fit wrapper and confirm which `fdars_core` module (`scalar_on_function`) exposes `fregre_lm` + `FregreLmResult`.

### Established Patterns (from research `.planning/research/{FEATURES,ARCHITECTURE,PITFALLS}.md`)
- String-enum dispatch + `#[non_exhaustive]` `_ => PyValueError` fallback; compound results → PyDict; `TestResult { statistic:f64, p_value:f64, n_perm:usize }` and `ToleranceBand { lower, upper, center, half_width }` are BOTH `#[non_exhaustive]` structs → field access OK, no struct-literal construction in tests.
- Verified 0.20 signatures (docs.rs): `t_perm_test(data_a, data_b, argvals, n_perm, seed)`, `f_perm_test(...)`, `two_sample_mean_test(data_a, data_b, argvals, ncomp)`, `mean_scb(data, argvals, bandwidth, nb, confidence, multiplier)`, `scb_two_sample_test(data_a, data_b, argvals, bandwidth, nb, confidence, multiplier)`, `oneway_anova_vstat(data, groups, argvals)`.

### Integration Points
- New `src/inference_mod.rs`; edits to `src/lib.rs` + `python/fdars/__init__.py`. Build via `maturin develop`; tests via pytest. rustfmt + clippy `-D warnings` must stay clean.

</code_context>

<specifics>
## Specific Ideas

- Dataset choices for tests (from research): Growth (boys/girls) for two-sample tests; Canadian Weather (single group / by region) for `mean_scb` and `oneway_anova_vstat`; Tecator (NIR → fat%) for FLM inference. Keep test data small for fast CI.
- Two plan-time verification spikes MUST be resolved before coding the affected bindings: (1) `MultiplierDistribution` variant names + SCB return (`ToleranceBand`) — before `mean_scb`/`scb_two_sample_test`; (2) exact `flm_f_test`/`flm_gof_test` signature + `scalar_on_function::fregre_lm`/`FregreLmResult` fields + `oneway_anova_vstat` group-label base — before those bindings.

</specifics>

<deferred>
## Deferred Ideas

- Advisor `inference` diagnostics aspect → Phase 34 (ADV-03).
- Docs pages + SVG diagrams + worked examples for inference → Phase 35 (DOCS-04).
- A persistent `FregreLmResult` handle / pyclass — explicitly rejected (re-fit internally instead).

</deferred>
