# Phase 70: Multi-Domain Data, FAMM & Advanced Clustering - Context

**Gathered:** 2026-09-03
**Status:** Ready for planning
**Mode:** Smart discuss (autonomous)

<domain>
## Phase Boundary

Construct multi-domain functional data and feed it to mixed-model (FAMM) and multivariate
SPM bindings; plus the advanced clustering methods added at 0.33. Four requirements with a
HARD internal ordering constraint.

In scope:
- **MULTI-01 (FIRST):** new `PyMultiFunData` opaque `#[pyclass]` handle mirroring the
  existing `PyIrregFdata` (pace_fpca_mod.rs), plus a builder from component curves; a new
  `fdars.multi_fdata` submodule; registered + constructible from Python.
- **MULTI-02:** mixed-model bindings `dense_flmm`, `fast_fmm`, `multi_famm` → a new
  `fdars.famm` submodule; consume `PyMultiFunData` where required; documented PyDicts.
- **MULTI-03 (AFTER MULTI-01):** multivariate SPM extends `fdars.spm` — bind `mfpca`
  (multivariate FPCA over multiple variables) + `spe_multivariate` (multivariate SPE
  monitoring statistic). User decision: this pair, a coherent multi-domain-monitoring story;
  NOT the broader frcc/other-monitor set.
- **MULTI-04 (independent):** advanced clustering `dbscan_fd`, `kcfc_cluster`,
  `funfem_cluster`, `align_cluster_fd` → extend `fdars.clustering`; each returns a
  labels/result PyDict, transposition-guarded.

Internal sequencing (hard): **PyMultiFunData (MULTI-01) MUST land before the FAMM (MULTI-02)
and SPM (MULTI-03) bindings that consume it.** Clustering (MULTI-04) is independent and can
come any time after the crate baseline. This is the ONLY phase touching `src/spm_mod.rs`.

Out of scope: advisor `spm`/`clustering` aspect extensions (ADV-01 → Phase 72), docs
(DOCS-01 → Phase 73), other binding families.

Parallelizable: NO within itself (internal sequential dep + shared spm_mod.rs); worktrees
disabled here anyway (sequential on main).

</domain>

<decisions>
## Implementation Decisions

### MULTI-03 multivariate-SPM scope (user decision)
- **Bind `mfpca` + `spe_multivariate`** into `fdars.spm`. `mfpca` (spm/mfpca.rs:246) takes
  `variables: &[&FdMatrix]` + `MfpcaConfig`; `spe_multivariate` (spm/stats.rs:275) is the
  multivariate SPE monitoring statistic. Together = complete multi-domain-monitoring pair.
  Skip `frcc` and other multi-domain monitors (deferred).

### Claude's Discretion (convention-driven)
- **PyMultiFunData handle:** mirror `PyIrregFdata` exactly (opaque `#[pyclass]`, constructed
  via a `#[pyfunction]` builder that takes component curves from Python — likely a list of 2D
  numpy arrays, one FdMatrix per variable/domain — routed through `numpy2d_to_fdmatrix` /
  `extract_ragged_vecs` as the `MultiFunData` constructor requires). Confirm the exact
  `MultiFunData::from_*` constructor signature (multi_fdata.rs:86) in research.
- **Submodule organization:** new `fdars.multi_fdata` (handle + builder) and new `fdars.famm`
  (mixed models); `fdars.spm` and `fdars.clustering` extended in place.
- **Return shape:** documented PyDicts from result structs (mfpca → MfpcaResult; famm →
  their result structs; clustering → labels/result dicts). Confirm exact 0.33 field names.
- **Transposition:** every 2D input via `numpy2d_to_fdmatrix`; multi-variable inputs as a list
  of 2D arrays; non-square (`n_obs ≠ n_points`) fixtures throughout (MULTI-04 explicitly
  transposition-guarded).
- **Enum/`#[non_exhaustive]` args:** clustering/famm/mfpca configs likely `#[non_exhaustive]`
  → `Default::default()` + field mutation; any enum arg via string dispatch with an
  `Err`-returning wildcard arm (locked STATE decision).
- **Determinism:** `seed` default where an upstream fn takes one (dbscan/kcfc/funfem may).
- **Error handling:** `FdarError` → `PyValueError` via `convert::to_pyresult`.

</decisions>

<code_context>
## Existing Code Insights

### Pattern to mirror
- `src/pace_fpca_mod.rs` — `PyIrregFdata` opaque `#[pyclass]` (:25) + `irreg_fdata_from_lists` builder (:54) with guarded ragged extraction (uses `convert::extract_ragged_vecs`, panic-guards before `from_lists`). PyMultiFunData follows this template exactly (this is pyfda's 2nd opaque handle).

### fdars-core 0.33 API surface (from registry source)
- `multi_fdata.rs:86` — `pub struct MultiFunData` (+ its constructor(s) — confirm in research).
- `famm.rs`: `dense_flmm` (:1039), `multi_famm` (:1340), `fast_fmm` (:1524).
- `spm/mfpca.rs:246` — `mfpca(variables: &[&FdMatrix], config: &MfpcaConfig) -> MfpcaResult`.
- `spm/stats.rs:275` — `spe_multivariate(...)`.
- `clustering_advanced.rs`: `dbscan_fd` (:157), `kcfc_cluster` (:371), `funfem_cluster` (:701), `align_cluster_fd` (:1335).

### Reusable Assets
- `src/convert.rs` — `numpy2d_to_fdmatrix`, `extract_ragged_vecs`, `to_pyresult`.
- `src/spm_mod.rs` — existing spm bindings + `register` (extend for mfpca + spe_multivariate).
- `src/clustering_mod.rs` — existing clustering bindings + `register` (extend for the 4 advanced fns).
- Phases 68/69 modules — fresh examples of string→enum Err-arm dispatch, `#[non_exhaustive]` config handling, multi-predictor `Vec<&FdMatrix>` ref-collection (relevant for `mfpca`'s `&[&FdMatrix]`).

### Integration Points
- NEW `src/multi_fdata_mod.rs` + `src/famm_mod.rs`; MODIFY `src/spm_mod.rs` + `src/clustering_mod.rs`; MODIFY `src/lib.rs` (2 new submodules) + `python/fdars/__init__.py` (2 names); new tests.

</code_context>

<specifics>
## Specific Ideas

- Confirm the `MultiFunData` constructor signature + how component curves + per-variable argvals are supplied — this drives the PyMultiFunData builder's Python input contract.
- `mfpca` takes `&[&FdMatrix]` (multiple variables) — use the multi-predictor `Vec<FdMatrix>` → `Vec<&FdMatrix>` ref-collection pattern from `concurrent_regression`/phase-68.
- Which FAMM functions actually REQUIRE `PyMultiFunData` vs. plain matrices? Confirm per-function in research (MULTI-02 says "where required").
- FND-02 guard (Phase 67) tolerates the 2 new submodule registrations — full suite must stay green.

</specifics>

<deferred>
## Deferred Ideas

- `frcc` + other multi-domain SPM monitors — deferred (MULTI-03 scoped to mfpca + spe_multivariate).
- Advisor `spm`/`clustering` aspect extensions for the new methods (ADV-01) — Phase 72.
- multi-domain/FAMM + clustering docs pages (DOCS-01) — Phase 73.

</deferred>
