# Phase 69: Fréchet Regression & Density FDA - Context

**Gathered:** 2026-09-03
**Status:** Ready for planning
**Mode:** Smart discuss (autonomous)

<domain>
## Phase Boundary

Two new submodules plus a shared conversion-layer refactor, sequenced so the refactor
lands first:

1. **FRE-03 (prerequisite, sequenced FIRST):** factor the ragged-list input helper out of
   `src/pace_fpca_mod.rs` (currently the private `extract_list_of_vecs`, pace_fpca_mod.rs:33)
   into `src/convert.rs` as a public `extract_ragged_vecs`, validated on non-uniform
   per-observation lengths, and consumed by the density/Fréchet inputs. Update the
   `pace_fpca_mod.rs` call site to use the relocated helper (single source of truth).
2. **FRE-01:** new `fdars.frechet` submodule — `frechet_mean`, `frechet_global_reg`,
   `frechet_local_reg`, `frechet_anova`, each returning a documented PyDict; metric-space
   backend chosen by string dispatch with an `Err` fallback arm.
3. **FRE-02:** new `fdars.density_fda` submodule — `lqd_transform` / `inverse_lqd`,
   `lqd_fpca`, `wasserstein_barycenter`, `normalize_density`.

Out of scope: advisor `frechet` aspect (ADV-01, diagnostics-only → Phase 72), docs
(DOCS-01 → Phase 73), MULTI-02 mixed-model bindings (Phase 70), FRE-RUN-01 (future),
network + point-process metric spaces (deferred, see decisions).

Parallelizable: new `src/frechet_mod.rs` + `src/density_fda_mod.rs`; the `convert.rs`
refactor is an internal prerequisite sequenced first within this phase.

</domain>

<decisions>
## Implementation Decisions

### Fréchet metric-space backend scope (user decision)
- **Density-default + common spaces.**
  - `frechet_global_reg`, `frechet_local_reg`, `frechet_anova`: bind the **non-generic
    density/distribution-response** variants (Petersen–Müller quantile averaging; clean
    numpy 2D I/O) as the default path.
  - `frechet_mean` (generic-only) + the string-dispatch backend: support the **3
    statistically-common spaces — SPD (covariance/PD matrices), spherical (directional /
    unit-norm data), correlation (correlation matrices)**. Each gets its own numpy input
    contract + validation (SPD symmetric-PD; spherical unit-norm; correlation unit-diagonal).
  - **Skip `network` + `point_process`** metric spaces (niche graph/event spaces with
    awkward bespoke input formats) — deferred to a dedicated later phase.
  - String dispatch: a `space_from_str`-style match with an **`Err`-returning wildcard arm**
    listing the valid backend names (`"spd"`, `"spherical"`, `"correlation"`) — mandatory
    for the metric-space selection (locked STATE enum-arm decision generalizes here).

### FRE-03 refactor shape (Claude's discretion — mechanical)
- **Fully relocate + rename**: move `extract_list_of_vecs` from `pace_fpca_mod.rs` into
  `convert.rs` as `pub fn extract_ragged_vecs`, update the single pace_fpca call site to
  import it. No re-export shim (single source of truth). Preserve/extend the non-uniform
  per-observation-length validation and add a unit/behavior test on ragged input.

### Claude's Discretion (convention-driven)
- **Return shape:** documented PyDict per result struct; confirm exact 0.33 field names
  against registry source before writing converters.
- **Transposition + argvals:** 2D matrix inputs via `convert::numpy2d_to_fdmatrix`;
  ragged/density inputs via the new `extract_ragged_vecs`; non-square fixtures where 2D.
- **density_fda functions** take `&[f64]` / vecs (vals, argvals) — route through the ragged
  helper / 1D converters; `normalize_density` returns a Vec<f64> (naked 1D array), the
  others return PyDicts (confirm per-function in research).
- **Determinism:** expose `seed` with a fixed default where an upstream fn takes one.
- **Error handling:** `FdarError` → `PyValueError` via `convert::to_pyresult`.

</decisions>

<code_context>
## Existing Code Insights

### fdars-core 0.33 API surface (from registry source)
- `frechet/mean.rs`: `frechet_mean<S: MetricSpace>` (:40, generic-only → needs string→space dispatch); `frechet_variance<S>` (:64).
- `frechet/regression.rs`: `frechet_global_reg` (:236, non-generic density-response), `frechet_global_reg_space<S>` (:278), `frechet_local_reg` (:317), `frechet_local_reg_space<S>` (:363).
- `frechet/anova.rs`: `frechet_anova` (:124, non-generic), `frechet_anova_space<S>` (:222).
- `frechet/spaces/`: `SpdMatrixSpace` (spd.rs:46), `SphericalSpace` (spherical.rs:31), `CorrelationMatrixSpace` (correlation.rs:25), `NetworkSpace` (deferred), `PointProcessSpace` (deferred).
- `density_fda.rs`: `normalize_density(vals, argvals)` (:127, → Vec<f64>), `lqd_transform` (:201), `inverse_lqd` (:301), `wasserstein_barycenter` (:407), `lqd_fpca` (:563).

### Reusable Assets
- `src/pace_fpca_mod.rs:33` — `extract_list_of_vecs` (the helper to relocate); note it accepts a `PyList` of 1-D numpy arrays / sequences.
- `src/convert.rs` — destination for `extract_ragged_vecs`; existing `numpy2d_to_fdmatrix`, `to_pyresult`, 1D helpers.
- Phase 67/68 modules — fresh worked examples of new-submodule registration + string→enum Err-arm dispatch (see `penalty_from_str` in `scalar_on_function_mod.rs`).

### Integration Points
- `src/convert.rs` (relocate helper); `src/pace_fpca_mod.rs` (update caller); NEW `src/frechet_mod.rs` + `src/density_fda_mod.rs`; `src/lib.rs` (2 register_submodule! lines); `python/fdars/__init__.py` (2 names); new tests.

</code_context>

<specifics>
## Specific Ideas

- Locate and confirm the exact input representation each of SpdMatrixSpace / SphericalSpace / CorrelationMatrixSpace expects (how a Python array becomes one "object" in that space) — this drives the per-space numpy marshalling.
- Confirm exact result-struct field names (`FrechetGlobalRegResult`, `FrechetLocalReg*`, `FrechetAnovaResult`, `FrechetMean*`, and the density result structs / lqd_fpca) against registry source.
- FND-02 guard (Phase 67 refactor) tolerates the two new submodule registrations — full suite must stay green.
- The `convert.rs` refactor MUST NOT change `pace_fpca` behavior — re-run its existing tests after the move.

</specifics>

<deferred>
## Deferred Ideas

- `network` + `point_process` metric spaces for Fréchet — dedicated later phase.
- FRE-RUN-01: promote the `frechet` advisor aspect from diagnostics-only to `_RUNNABLE_METHODS` (future).
- Advisor `frechet` aspect (ADV-01, diagnostics-only) — Phase 72; frechet docs page (DOCS-01) — Phase 73.

</deferred>
