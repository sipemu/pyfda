# Phase 27: Scoring Metrics & Alignment/Registration Bindings - Context

**Gathered:** 2026-08-14
**Status:** Ready for planning

<domain>
## Phase Boundary

Bind the fdars-core 0.17.0 scoring metrics and shift-registration / registration-quality / banded-elastic-alignment API into `fdars`, on the green 0.17.0 baseline (Phases 25–26 shipped; suite at 328 passed / 4 skipped). Every fallible input surfaces as a clean Python `ValueError`, never a Rust panic.

Delivers (STAT-03, ALGN-01/02/03):
- **Scoring metrics** (NEW `fdars.scoring` submodule): `functional_mae`, `functional_mse`, `functional_mape`, `functional_msle`, `functional_explained_variance` — Simpson-integrated scalars scoring predicted-vs-true curves.
- **Shift registration** (extend `fdars.alignment`): `least_squares_shift_registration` → `ShiftRegistrationResult` marshalled as a dict; plus `fd.shift_register()` Fdata method.
- **Registration-quality scores** (extend `fdars.alignment`): `least_squares_score`, `pairwise_correlation_score`, `sobolev_least_squares_score`.
- **Banded elastic alignment** (extend `fdars.alignment`): `karcher_mean_with_band`, `elastic_self_distance_matrix_with_band`, `elastic_cross_distance_matrix_with_band` with optional `band_frac`.

Out of this phase: advisor extension (28), diagrams/examples (29).
</domain>

<decisions>
## Implementation Decisions

### Namespace & Placement (user-decided)
- The 5 prediction-scoring metrics get a NEW `fdars.scoring` submodule (new `src/scoring_mod.rs`, registered via `register_submodule!` in `src/lib.rs` + added to `_submodule_names` in `python/fdars/__init__.py`), mirroring upstream `fdars_core::scoring`. Rationale: error-scoring of predicted-vs-true curves is conceptually distinct from `fdars.metric`'s geometric distances (lp/hausdorff); a clean separate namespace (consistent with the Phase 26 `fdars.represent` split).
- Shift registration, the 3 registration-quality scores, and the 3 banded-elastic functions all extend the existing `src/alignment_mod.rs` → `fdars.alignment.*` (they belong with the elastic/karcher family already there).

### Fdata Convenience Method (user-decided)
- `fd.shift_register()` — least-squares shift registration as an Fdata method returning the registered `Fdata` (+ per-curve shifts), alongside module-level `fdars.alignment.least_squares_shift_registration`.
- The 5 scoring metrics take TWO datasets (predicted + true), so they stay module-level functions only — not Fdata methods.

### Result Marshalling & Enums (research-grounded; Claude's discretion within these)
- `ShiftRegistrationResult` marshals as a Python `dict` (established convention — every compound result in the codebase returns a PyDict; e.g. `karcher_mean`, `elastic_align_pair`). Keys expose the registered curves and per-curve shifts (confirm exact fields from the 0.17.0 struct at execute time).
- `band_frac` is an `Option<f64>` param: `None` (or omitted) = unbanded (identical to `karcher_mean`); `Some(frac)` = Sakoe–Chiba corridor. Bind the `*_with_band` variants — NOT the 0.14-era `*_banded` (`f64`, where `0.0` does not disable the band).
- All fallible returns route through `to_pyresult()`; no `.unwrap()` on any `Result<_, FdarError>`.

### Correctness Requirements (mandatory)
- Banded distance matrices (`elastic_self/cross_distance_matrix_with_band`) are matrix returns → route through `fdmatrix_to_numpy2d` and carry a MULTI-CURVE round-trip transposition test (distinct per-curve values; #33 class).
- MAPE has NO epsilon guard upstream → near-zero true values raise `ValueError` (test `pytest.raises`). MSLE rejects values ≤ −1 → `ValueError`. `sobolev_least_squares_score` requires a UNIFORM grid → the requirement is surfaced clearly (a helpful `ValueError`, not a silent wrong answer).
- Where sensible, sanity-check a scoring metric against a hand/np-computed value on a small dataset (e.g. `functional_mse` of identical curves == 0).

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `src/lib.rs` — `register_submodule!` macro; add `scoring`.
- `src/alignment_mod.rs` — existing `elastic_align_pair`/`karcher_mean`/`elastic_self_distance_matrix`/`elastic_cross_distance_matrix` (lines ~29/70/216/231) are the direct analogs for the banded `*_with_band` variants and the registration additions.
- `src/convert.rs` — `fdmatrix_to_numpy2d`, `vec_to_numpy1d`, `to_pyresult`; PyDict construction pattern used by existing compound-result functions.
- `src/metric_mod.rs` — reference for scalar-returning metric pyfunctions (though scoring goes in its own module).
- `python/fdars/__init__.py` — `_submodule_names` tuple + registration loop; add `scoring`.
- `python/fdars/fdata_class.py` — add `shift_register()` next to the alignment-related methods / `mean()`.

### Established Patterns
- Thin `#[pyfunction]` wrappers; `#[pyo3(signature = (...))]` for `band_frac=None` default; PyReadonlyArray inputs; dict returns for compound results.
- Tests in `tests/` (pytest); `.venv/bin/maturin develop` to rebuild before testing. Current baseline: 328 passed / 4 skipped.

### Integration Points
- New `fdars.scoring` reachable as both `from fdars.scoring import functional_mae` and `fdars.scoring.functional_mae(...)` via the sys.modules loop.
- `fd.shift_register()` delegates to `_native.alignment.least_squares_shift_registration`, wrapping the returned registered-curve matrix back into an `Fdata` with the same argvals.

</code_context>

<specifics>
## Specific Ideas

- Confirm the exact `ShiftRegistrationResult` field names and the `least_squares_shift_registration` / `functional_*` / quality-score signatures against fdars-core 0.17.0 (docs.rs or `cargo doc`) BEFORE writing each wrapper — do not assume field names.
- `functional_explained_variance` is the correct name (not `explained_variance`).
- Banded `karcher_mean_with_band` result struct is identical to unbanded `karcher_mean` — reuse the same dict-marshalling.

</specifics>

<deferred>
## Deferred Ideas

- Advisor `scoring` diagnostics method + registration-quality diagnostics on the `alignment` aspect → Phase 28.
- Diagrams + worked examples for scoring/registration/banded alignment → Phase 29.
- Scoring metrics as Fdata methods — intentionally NOT done (they need two datasets).

</deferred>
