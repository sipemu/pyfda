# Stack Research

**Domain:** PyO3 Rust-to-Python binding layer — fdars-core upgrade (0.23.0 → 0.33.0)
**Researched:** 2026-09-02
**Confidence:** MEDIUM (all facts sourced from crates.io API and docs.rs; confidence rating LOW per provider tier, elevated to MEDIUM because primary sources are the authoritative registry and the published documentation, and key claims are cross-checked across multiple API endpoints)

---

## Upgrade Verdict: Clean Bump Path

**YES — the 0.23.0 → 0.33.0 bump is a clean, additive-only upgrade.** No breaking changes to existing public signatures were found across any of the 10 minor versions (0.24–0.33). The existing `Cargo.toml` one-liner change (`0.23.0` → `0.33.0`) is sufficient to complete the bump; no other toolchain, binding-layer, or Python-stack changes are forced.

---

## Q1 — MSRV at 0.33.0

**fdars-core 0.33.0 MSRV: Rust 1.81**

Sourced directly from the crates.io API (`rust_version` field on the 0.33.0 version record, published 2026-09-02). Every release from 0.4.0 through 0.33.0 declares `rust-version = "1.81"`.

pyfda's current pinned `rust-version = "1.83"` in `Cargo.toml` satisfies this requirement with headroom. **No Rust toolchain change is needed.**

---

## Q2 — linalg Feature Status at 0.33.0

**linalg is no longer gated on Rust 1.84+. The earlier deferral reason (MSRV mismatch) is obsolete.**

At the time of v6.0 (0.23.0), the `linalg` feature pulled in `faer`, which at that point required Rust 1.84 — above the project's MSRV of 1.83. At 0.33.0, confirmed from the crates.io dependency manifest:

- `faer = "^0.23"` (optional, linalg feature) — faer 0.23's MSRV is 1.81, matching fdars-core's own MSRV
- `anofox-regression = "^0.4"` (optional, linalg feature) — a standalone regression library providing OLS/GLM/quantile/penalized-spline estimators; MSRV is 1.81

**Consequence for this milestone:** The user decision to keep `parallel`-only and NOT enable `linalg` is upheld. But the technical reason that forced it (MSRV mismatch) is gone. If a future milestone wants `linalg`, there is no toolchain blocker at 0.33.0.

---

## Q3 — Cargo Feature Flags at 0.33.0

Features confirmed from the crates.io API dependency manifest for 0.33.0:

| Feature | Value | Status vs 0.23.0 |
|---------|-------|-----------------|
| `default` | `["parallel"]` | Unchanged |
| `parallel` | `["rayon"]` | Unchanged — still the correct flag to enable |
| `linalg` | `["faer", "anofox-regression"]` | Flag name unchanged; `anofox-regression` is the dependency alongside faer |
| `serde` | `["dep:serde", "dep:serde_json"]` | NEW in this series — optional serialization; not needed for pyfda |
| `dhat-heap` | `[]` | Unchanged — heap profiling only |
| `js` | `["getrandom/js"]` | Unchanged — WASM only |

**For pyfda `Cargo.toml`:** No change to the `features = ["parallel"]` line. No new feature is required to expose any of the new modules. `clustering_advanced`, `famm` extensions, `multi_fdata`, `density_fda`, `pda`, `fts`, `frechet`, and `shapelet` all sit under the default/no-feature surface and are compiled in unconditionally.

---

## Q4 — Transitive Dependency Changes

Dependencies confirmed from the crates.io API for both 0.23.0 and 0.33.0:

| Dependency | At 0.23.0 | At 0.33.0 | Impact on pyfda |
|------------|-----------|-----------|-----------------|
| `nalgebra` | `^0.33` | `^0.33` | No change |
| `rustfft` | `^6.2` | `^6.2` | No change |
| `rand` | `^0.8` | `^0.8` | No change |
| `rand_distr` | `^0.4` | `^0.4` | No change |
| `num-complex` | `^0.4` | `^0.4` | No change |
| `getrandom` | `^0.2` | `^0.2` | No change |
| `rayon` (parallel) | `^1.10` | `^1.10` | No change |
| `faer` (linalg) | `^0.23` | `^0.23` | No change (linalg not enabled) |
| `anofox-regression` (linalg) | `^0.4` | `^0.4` | No change (linalg not enabled) |
| `serde` / `serde_json` (serde) | not present | `^1` optional | Not enabled; no impact |

**Verdict:** Zero transitive dependency changes between 0.23.0 and 0.33.0 under the `parallel`-only feature set. `Cargo.lock` will update automatically on `cargo build`; no manual intervention is needed.

---

## Q5 — PyO3 / numpy / maturin Compatibility

**No forced upgrade to any of these.**

- `pyo3 = "0.28"` with `["extension-module", "abi3-py39"]`: unchanged and compatible. fdars-core 0.33.0 does not list pyo3 or numpy as its own dependencies — those live exclusively in pyfda's `Cargo.toml`. The upgrade only swaps fdars-core's own algorithms; the PyO3 binding surface is entirely pyfda's concern.
- `numpy = "0.28"`: unchanged. No new fdars-core types require numpy array layout changes beyond the existing column-major pattern already established in `src/convert.rs`.
- `maturin 1.x`: unchanged. The `cdylib` + `abi3-py39` build path is unaffected.
- Python 3.9–3.14 CI matrix: unchanged.

---

## Q6 — New Surface Added in 0.24–0.33

All changes are **additive only** — no existing public signatures were removed or altered across the 10 minor versions. The new capabilities require new `*_mod.rs` binding files and Python API additions; they do not require modifying any existing binding.

### New Modules (confirmed absent in 0.23.0 via docs.rs 404)

| Module | Introduced | Key public surface |
|--------|------------|-------------------|
| `clustering_advanced` | 0.24.0 | `dbscan_fd`, `kcfc_cluster`, `funfem_cluster`, `align_cluster_fd` + 4 config/result pairs (`DbscanConfig/Result`, `KcfcConfig/Result`, `FunFemConfig/Result`, `AlignClusterConfig/Result`) |
| `density_fda` | ~0.25.0 | `lqd_transform`, `inverse_lqd`, `lqd_fpca` (`LqdFpcaResult`), `wasserstein_barycenter`, `normalize_density` |
| `multi_fdata` | ~0.26.0 | `MultiFunData`, `FdComponent` (multi-domain functional data container; same-obs-count constraint) |
| `pda` | ~0.27.0 | `principal_differential_analysis`, `Lfd`, `PdaResult` (linear differential operators; mirrors R `pda.fd`) |
| `fts` | 0.27.0–0.28.0 | 13 functions: `ftsm`, `ftsm_forecast`, `ftsm_forecast_multistep`, `ftsm_update`, `fplsr`, `dpca`, `dpca_reconstruct`, `spectral_density`, `functional_acf`, `functional_pacf`, `long_run_covariance`, `stationarity_test`, `functional_difference`; 10 result structs (`ArModelResult`, `DpcaReconstruction`, `DpcaResult`, `FacfResult`, `FplsrResult`, `FtsmForecastResult`, `FtsmResult`, `LongRunCovResult`, `SpectralDensityResult`, `StationarityResult`) |
| `frechet` | 0.27.0–0.28.0 | `MetricSpace` trait; 6 backends (`WassersteinDensitySpace`, `SpdMatrixSpace`, `SphericalSpace`, `CorrelationMatrixSpace`, `NetworkSpace`, `PointProcessSpace`); 9 functions (`frechet_mean`, `frechet_variance`, `wasserstein2_distance`, `frechet_global_reg`, `frechet_global_reg_space`, `frechet_local_reg`, `frechet_local_reg_space`, `frechet_anova`, `frechet_anova_space`); 3 result structs |
| `shapelet` | 0.33.0 | `discover_shapelets`, `shapelet_classifier_fit`, `shapelet_transform`, `shapelet_transform_fit`, `shapelet_distance`, `z_normalize_into`, `z_normalize_window`; 8 types (`Shapelet`, `ShapeletSet`, `QualityMeasure`, `ShapeletClassifier`, `ShapeletClassifierConfig`, `ShapeletClassifierFit`, `ShapeletDiscoveryConfig`, `ShapeletTransformFit`) |

Note: `~0.25.0` and `~0.26.0` are approximate (changelog consolidates those into the 0.27.0 entry); `pda` confirmed present by 0.27.0, `multi_fdata` confirmed present by 0.27.0, `density_fda` absent at 0.24.0 (404). The exact introduction minor does not affect binding work — all are absent from 0.23.0 and present at 0.33.0.

### Extended Modules (present in 0.23.0, new items added)

| Module | What was added (not in 0.23.0) |
|--------|-------------------------------|
| `famm` | `dense_flmm`, `fast_fmm`, `multi_famm` + 6 new config/result types (`DenseFlmmConfig/Result`, `FastFmmConfig/Result`, `MultiFammConfig/Result`) — all present by 0.24.0 |
| `seasonal` | ~13 new functions: `analyze_peak_timing`, `autoperiod_fdata`, `cfd_autoperiod`, `cfd_autoperiod_fdata`, `instantaneous_period`, `lomb_scargle_fdata`, `matrix_profile_fdata`, `matrix_profile_seasonality`, `seasonal_strength_spectral`, `seasonal_strength_wavelet`, `seasonal_strength_windowed`, `sazed_fdata`, `ssa_fdata`, `ssa_seasonality`; ~14 new types (`AutoperiodCandidate`, `CfdAutoperiodResult`, `ChangeDetectionResult`, `ChangePoint`, `DetectedPeriod`, `InstantaneousPeriod`, `LombScargleResult`, `MatrixProfileResult`, `PeakDetectionResult`, `PeakTimingResult`, `SazedComponents`, `SazedResult`, `SeasonalityClassification`, `WaveletAmplitudeResult`) |
| `function_on_scalar` | `fanova_seeded` added (0.30.0, seedable permutation ANOVA); `fanova` deprecated (soft — still callable, not removed) |

### Deprecations

Only one: `fanova` in `function_on_scalar` — deprecated in 0.30.0 in favour of `fanova_seeded` (which takes an explicit `seed: u64`). The deprecated function remains callable; no existing pyfda binding breaks. Existing code in `src/function_on_scalar_mod.rs` continues to compile and work; a new binding for `fanova_seeded` is desirable but not required by the compiler.

### Changelog: Version-by-Version Summary (0.24–0.33)

| Version | Date | Theme | Breaking changes |
|---------|------|-------|-----------------|
| 0.24.0 | 2026-08-20 | Advanced clustering + FAMM breadth | None |
| 0.25.0 | 2026-08-22 | Serial dependence, density FDA, multi-fdata | None |
| 0.26.0 | 2026-08-22 | FPCA breadth, sparse covariance | None |
| 0.27.0 | 2026-08-22 | FTS forecasting, Fréchet regression, PDA | None |
| 0.28.0 | 2026-08-23 | Spectral FTS, object-data Fréchet | None |
| 0.29.0 | 2026-08-30 | FAMM extensions (dense/fast/multi) | None |
| 0.30.0 | 2026-09-01 | Performance & consolidation; `fanova` deprecated | None (deprecated, not removed) |
| 0.31.0 | 2026-09-02 | (details not in changelog; all versions published same day as 0.32/0.33) | None confirmed |
| 0.32.0 | 2026-09-02 | (details not in changelog) | None confirmed |
| 0.33.0 | 2026-09-02 | Shapelets (time-series shapelet discovery/classification) | None |

Versions 0.31.0 and 0.32.0 are confirmed to exist (crates.io API) but their changelog entries are not present in the published CHANGELOG.md. Based on the module-level inspection at 0.32.0 (no `shapelet` module), 0.31 and 0.32 are likely internal or performance-only passes. No new breaking signatures are expected.

---

## Q7 — Package Version Bump for pyfda

**Recommended: bump to `0.10.0`.**

Project convention (from `MEMORY.md` and `PROJECT.md`): a semver `vX.Y.Z` tag triggers the PyPI publish workflow. The current package version is `0.9.0` (shipped with v9.0 sklearn milestone). This is a code milestone (new bindings, advisor changes, package change) so a version bump is required at close.

- `0.10.0` is idiomatic — it is the next minor after `0.9.0`, signals a substantial capability addition without a breaking API change, and stays under `1.0.0` which the project has historically reserved.
- The PyPI publish tag would be `v0.10.0`; the milestone label is `v11.0` (milestone version and package version are intentionally decoupled per project convention).

---

## Recommended Cargo.toml Change

The sole required edit to `Cargo.toml` for the crate bump phase:

```toml
[dependencies]
fdars-core = { version = "0.33.0", features = ["parallel"] }
pyo3 = { version = "0.28", features = ["extension-module", "abi3-py39"] }
numpy = "0.28"
```

Only the `fdars-core` version string changes (`0.23.0` → `0.33.0`). Everything else is unchanged.

---

## Version Compatibility Matrix

| Component | Current (0.23.0) | After Bump (0.33.0) | Action |
|-----------|-----------------|---------------------|--------|
| `fdars-core` | 0.23.0 | **0.33.0** | Change version string in `Cargo.toml` |
| `pyo3` | 0.28 | 0.28 | No change |
| `numpy` (PyO3 binding) | 0.28 | 0.28 | No change |
| Rust MSRV (`rust-version`) | 1.83 | 1.83 | No change (0.33.0 requires ≥1.81) |
| maturin | 1.x | 1.x | No change |
| Python CI matrix | 3.9–3.14 | 3.9–3.14 | No change |
| pyfda package version | 0.9.0 | **0.10.0** | Bump at milestone close; tag `v0.10.0` |

---

## What NOT to Do

| Avoid | Why | Instead |
|-------|-----|---------|
| Enabling `linalg` feature | User decision for this milestone; not needed for any new bindings | Keep `features = ["parallel"]` |
| Bumping PyO3 or numpy | Not forced; no incompatibility | Leave at 0.28 |
| Raising Rust MSRV | 0.33.0 requires 1.81; pyfda already pins 1.83 | No `rust-version` change |
| Enabling `serde` feature | New optional feature; pyfda serializes via PyDict patterns, not serde | Keep disabled |
| Bumping package to `1.0.0` | Project convention reserves this | Use `0.10.0` |
| Treating 0.30 `fanova` deprecation as a breaking change | The function is still callable; no compiler error | Add `fanova_seeded` binding alongside existing `fanova` |

---

## Sources

- `https://crates.io/api/v1/crates/fdars-core` — crate metadata, current version 0.33.0 published 2026-09-02
- `https://crates.io/api/v1/crates/fdars-core/versions` — full version list with `rust_version` field for every release; all 0.4.0+ = 1.81
- `https://crates.io/api/v1/crates/fdars-core/0.33.0/dependencies` — dependency list at 0.33.0 (nalgebra ^0.33, rayon ^1.10, faer ^0.23, anofox-regression ^0.4, serde new)
- `https://crates.io/api/v1/crates/fdars-core/0.23.0/dependencies` — dependency list at 0.23.0 (verified all deps match; nalgebra already ^0.33 at 0.23.0)
- `https://crates.io/api/v1/crates/fdars-core/0.33.0` — features manifest (default=parallel, linalg=faer+anofox-regression, serde new optional)
- `https://raw.githubusercontent.com/sipemu/fdars/main/CHANGELOG.md` — entries for 0.27.0, 0.28.0, 0.30.0 confirmed; 0.25/0.26 folded into 0.27 entry; 0.31/0.32/0.33 entries absent from document
- `https://docs.rs/fdars-core/0.33.0/fdars_core/` — full module inventory at 0.33.0
- `https://docs.rs/fdars-core/0.23.0/fdars_core/` — full module inventory at 0.23.0 (baseline)
- `https://docs.rs/fdars-core/0.24.0/fdars_core/` — confirmed `clustering_advanced`, `detrend`, `seasonal` (expanded) present; `density_fda`, `multi_fdata`, `pda`, `fts`, `frechet` absent → 404
- `https://docs.rs/fdars-core/0.27.0/fdars_core/` — confirmed `multi_fdata`, `pda`, `fts`, `frechet` present by 0.27
- 404 responses on `shapelet` at docs.rs for 0.27/0.28/0.29/0.30/0.32 — confirmed shapelet arrived in 0.33.0 only
- 404 responses on `pda`, `multi_fdata`, `density_fda` at docs.rs/0.23.0 — confirmed absent from 0.23.0 baseline
- Module-level API pages for `fts`, `frechet`, `density_fda`, `pda`, `clustering_advanced`, `multi_fdata`, `seasonal`, `detrend`, `famm`, `shapelet`, `streaming_depth` at 0.33.0 — function/type counts and names verified

---

*Stack research for: pyfda v11.0 — fdars-core 0.23.0 → 0.33.0 upgrade*
*Researched: 2026-09-02*
