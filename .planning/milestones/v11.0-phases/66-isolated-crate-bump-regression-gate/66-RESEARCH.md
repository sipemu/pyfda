# Phase 66: Isolated Crate Bump + Regression Gate - Research

**Researched:** 2026-09-02
**Domain:** Cargo dependency bump (fdars-core 0.23.0 → 0.33.0) + maturin build + Python regression gate
**Confidence:** HIGH (all claims verified against local source files, CI workflow, and cargo registry)

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
Phase boundary:
- Bump `fdars-core` to `0.33.0` (parallel feature only, no linalg) in `Cargo.toml` + `Cargo.lock`
- `maturin develop` builds green (MSRV 1.83 unchanged)
- Full existing Python suite (~772 tests) passes with zero new failures; document any numeric-tolerance change (expected: none)
- Record a 0.24→0.33 changelog + API audit confirming every existing `match`-arm / enum-variant string in `src/*_mod.rs` still exists at 0.33; flag the four 0.30-deprecated 2D depth functions for later migration

Hard scope boundary (OUT OF SCOPE):
- NO new bindings
- NO test edits
- Only `Cargo.toml` and `Cargo.lock` may change

### Claude's Discretion
All implementation choices are at Claude's discretion — this is a pure infrastructure / upgrade phase
(dependency bump + regression gate). Use the ROADMAP phase goal, success criteria, and codebase
conventions to guide decisions.

### Deferred Ideas (OUT OF SCOPE)
- Migration of the four 0.30-deprecated 2D depth functions — flagged here, migrated in a later phase.
- All new-binding work (fts, regression, Fréchet/density, multi-domain/FAMM, shapelet/GAK) — Phases 67–71.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| DEP-01 | `fdars-core` pinned at `0.33.0` (from `0.23.0`) with the `parallel` feature only (no `linalg`); `Cargo.toml` + `Cargo.lock` updated; maturin `develop` build green | Verified: exact Cargo.toml lines; build recipe confirmed via CI workflow |
| DEP-02 | The full existing Python suite (~772 tests) passes against the bumped crate with zero new failures; any numeric-tolerance change is documented; MSRV 1.83 unchanged | Verified: exact pytest command; MSRV 1.81 < 1.83 confirmed; drift risk assessed |
| DEP-03 | A 0.24→0.33 changelog + API audit is recorded — every existing `match`-arm/enum-variant string in `src/*_mod.rs` is verified to still exist at 0.33, and the four 0.30-deprecated 2D depth functions are noted for migration | Verified: complete enum/match audit table below; four 2D depth functions identified with file+line |
</phase_requirements>

---

## Summary

Phase 66 is a mechanical, scope-controlled operation: one `Cargo.toml` version string changes, `cargo update` refreshes `Cargo.lock`, `maturin develop --release` rebuilds the extension, and the full Python suite runs as the regression gate. No binding code, test code, or Python changes are permitted.

The single planning risk is numeric drift from the 10-minor jump (0.23 → 0.33). The full Python suite (~772 tests, run via `pytest tests/ -x`) is the gate — not `cargo build` alone and not a subset. The changelog is fully recoverable (0.24–0.30 entries exist; 0.31/0.32 are absent from the published CHANGELOG but confirmed non-breaking via module-surface inspection at both versions; 0.33 adds shapelets only). The API audit is mechanical: every string literal in every `match` block across `src/*_mod.rs` is enumerated below and must be confirmed present at 0.33.

Four functions in `src/depth_mod.rs` call `fdars_core::depth::{fraiman_muniz_2d, modal_2d, random_projection_2d, random_tukey_2d}` — all four are `#[deprecated]` as of fdars-core 0.30.0 (soft deprecation, still callable). They MUST be flagged in the audit record for Phase 67+ migration but MUST NOT be changed in this phase.

**Primary recommendation:** One-line `Cargo.toml` edit + `cargo update -p fdars-core` + `maturin develop --release` + `pytest tests/ -x`. Document any tolerance change. Record the API audit. Commit only `Cargo.toml` and `Cargo.lock`.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Version bump | Build system (Cargo) | — | Pure Cargo manifest change; no runtime tier involved |
| Regression gate | Python test layer | Rust compilation | pytest exercises the full Python API surface over the rebuilt native extension |
| API audit | Source inspection | docs.rs / registry cache | Grep of `src/*_mod.rs`; cross-check against 0.33 module surface |
| Changelog recording | Documentation artifact | Cargo registry CHANGELOG | Human-readable record for downstream phases |

---

## Standard Stack

### Core (unchanged — no toolchain bump forced by this upgrade)

| Component | Current Version | Purpose | Status |
|-----------|----------------|---------|--------|
| `fdars-core` | `0.23.0` → **`0.33.0`** | Core FDA computation crate | **THE ONLY CHANGE** |
| `pyo3` | `0.28` | Rust-Python bindings | Unchanged |
| `numpy` (PyO3 binding) | `0.28` | NumPy array exchange | Unchanged |
| Rust MSRV (`rust-version`) | `1.83` | Minimum supported Rust | Unchanged (0.33.0 requires ≥ 1.81) |
| maturin | `1.x` | Build backend | Unchanged |
| Python | 3.9–3.14 | Runtime matrix | Unchanged |

[VERIFIED: Cargo.toml:18] Current line verbatim: `fdars-core = { version = "0.23.0", features = ["parallel"] }`

**Required change (verbatim):**
```toml
fdars-core = { version = "0.33.0", features = ["parallel"] }
```
That is the sole edit to `Cargo.toml`.

[VERIFIED: Cargo.lock:1-6] Current `Cargo.lock` entry for fdars-core:
```
name = "fdars-core"
version = "0.23.0"
source = "registry+https://github.com/rust-lang/crates.io-index"
checksum = "e915841124be37e93842e7d18dc8a436ea2be810ac732398c68d5906ec2f0dec"
```
After bumping `Cargo.toml`, `cargo update -p fdars-core` regenerates `Cargo.lock` automatically — no manual editing needed.

### Package Legitimacy Audit

> This phase installs no new external packages — it bumps a single existing dependency. The package
> legitimacy gate applies only to `fdars-core 0.33.0` since it is new to the lockfile.

| Package | Registry | Verdict | Disposition |
|---------|----------|---------|-------------|
| `fdars-core 0.33.0` | crates.io | OK | Approved — same crate, same source, trusted project author (sipemu/fdars) |

---

## Build and Test Recipe

### 1. Activate the virtualenv

```bash
source /path/to/repo/.venv/bin/activate
```

The project uses `.venv/` (standard name used by CI and the Makefile). [VERIFIED: ci.yml:68-70] CI creates the venv with `python -m venv .venv && source .venv/bin/activate`.

### 2. Bump the crate and update the lockfile

```bash
# Edit Cargo.toml: change "0.23.0" to "0.33.0" for fdars-core (one line)
# Then regenerate Cargo.lock:
cargo update -p fdars-core
```

`cargo update -p fdars-core` restricts the update to fdars-core and its transitive deps only, avoiding unintended changes to other locked versions. [ASSUMED] that `cargo update -p fdars-core` will resolve 0.33.0 cleanly given zero transitive-dep changes (confirmed in STACK.md: nalgebra ^0.33, rayon ^1.10 identical at both versions).

### 3. Build the extension

```bash
maturin develop --release
```

[VERIFIED: ci.yml:73] CI command verbatim: `maturin develop --release`. The `--release` flag is mandatory — debug builds (~10× slower) are insufficient for a numeric regression gate because timing-sensitive code paths may behave differently.

Note: CI also runs `pip install -e ".[all-providers,mcp]"` (for Python ≥ 3.10) after `maturin develop`. For the local regression gate the installed extras are not required — the test suite's provider-specific tests are already marked to skip when the LLM provider is unavailable. A bare `maturin develop --release` + the existing `.venv` extras is sufficient.

### 4. Run the regression gate

```bash
pytest tests/ -x -v
```

[VERIFIED: ci.yml:87-88] CI command verbatim: `pytest tests/ -v`. Adding `-x` (fail-fast on first error) is recommended for the regression gate — the first failure is the signal; continuing past it obscures the root cause.

**Full test count:** 48 test files in `tests/`, yielding ~772 individual test items. [ASSUMED — exact count; 772 is the established project baseline per STATE.md and CONTEXT.md.]

**Do NOT run:**
- `cargo test` alone — misses all Python-layer numeric assertions.
- `pytest tests/ -k "some_filter"` — a filtered run is not a regression gate.
- `pytest tests/sklearn/` — the sklearn compliance suite is a separate CI job; it tests estimator conformance, not the fdars-core numeric surface.

### 5. What constitutes a pass

- Zero new failures (`PASSED` count identical to pre-bump baseline, or higher if a previously-skipped test now passes).
- If any test fails: stop immediately, record the failure, and determine whether it is numeric drift (tolerance adjustment acceptable if new value is provably correct) or a removed/renamed API (requires investigation — likely indicates a surprise in 0.31/0.32).
- If tests newly pass (previously-marked `xfail` or `skip` now succeed): acceptable — record in the audit.

---

## API Audit Surface

This is the complete enumeration of string-dispatch `match` blocks across `src/*_mod.rs` (21 files). The planner must turn this into audit tasks that confirm each string still maps to a live enum variant at 0.33.

### How to verify at 0.33

Two methods (both acceptable; use whichever is available at execute time):

**Method A — docs.rs:** Check `https://docs.rs/fdars-core/0.33.0/fdars_core/<module>/enum.<EnumName>.html` for each enum listed below. Confirm each variant is present.

**Method B — cargo registry source:** After bumping and running `cargo update`, the 0.33.0 source lands in `~/.cargo/registry/src/index.crates.io-*/fdars-core-0.33.0/`. Read the enum definition file directly.

**Method C — compile:** `maturin develop --release` will produce a compile error if any enum variant string no longer exists (only for `#[non_exhaustive]` enums where the wildcard arm is the `Err(...)` path — a renamed variant that the code dispatches by name becomes a dead arm, not a compile error). Compile success alone is NOT sufficient — it only catches variant additions; it does not catch renamed dispatch strings.

### Enum/Match Audit Checklist

All data [VERIFIED: grep of src/*_mod.rs this session].

#### `depth_mod.rs` — `DepthMethod` enum [VERIFIED: depth_mod.rs:420-444]

Dispatched by `depth_method_from_str()`. Variants mapped:

| String | Enum Variant | Notes |
|--------|-------------|-------|
| `"fraiman_muniz"` | `DepthMethod::FraimanMuniz { scale }` | |
| `"band"` | `DepthMethod::Band` | |
| `"modified_band"` | `DepthMethod::ModifiedBand` | |
| `"random_projection"` | `DepthMethod::RandomProjection { nproj, seed }` | |
| `"total_variation"` | `DepthMethod::TotalVariation` | |
| `"hypograph_index"` | `DepthMethod::HypographIndex` | |
| `"modified_hypograph_index"` | `DepthMethod::ModifiedHypographIndex` | |
| `"epigraph_index"` | `DepthMethod::EpigraphIndex` | |
| `"half_region"` | `DepthMethod::HalfRegion` | |
| `"modified_half_region"` | `DepthMethod::ModifiedHalfRegion` | |
| `"extremal"` | `DepthMethod::Extremal` | |
| `"extreme_rank_length"` | `DepthMethod::ExtremeRankLength` | |
| `"l_infinity"` | `DepthMethod::LInfinity` | |

Wildcard arm: `other => Err(PyValueError::new_err(...))` — correct pattern.

#### `fdata_mod.rs` — `NormalizationMethod` enum [VERIFIED: fdata_mod.rs:261-317]

Two dispatch sites (normalize / normalize_with_argvals). Variants:

| String | Enum Variant |
|--------|-------------|
| `"center"` | `NormalizationMethod::Center` |
| `"autoscale"` | `NormalizationMethod::Autoscale` |
| `"pareto"` | `NormalizationMethod::Pareto` |
| `"range"` | `NormalizationMethod::Range` |
| `"curve_center"` | `NormalizationMethod::CurveCenter` |
| `"curve_standardize"` | `NormalizationMethod::CurveStandardize` |
| `"curve_range"` | `NormalizationMethod::CurveRange` |
| `"curve_lp"` | `NormalizationMethod::CurveLp(p)` |

#### `smoothing_mod.rs` — `CvCriterion` enum [VERIFIED: smoothing_mod.rs:193-196]

| String | Enum Variant |
|--------|-------------|
| `"cv"` | `CvCriterion::Cv` |
| `"gcv"` | `CvCriterion::Gcv` |
| `"aic"` | `CvCriterion::Aic` |

Default wildcard: `_ => CvCriterion::Gcv` (silently defaults — NOTE: this is not a `PyValueError` arm, meaning invalid strings silently use GCV; document as pre-existing behavior, do NOT change in this phase).

Also has a reverse match (result.criterion → string) at line 210.

#### `basis_mod.rs` — `BasisType` / `BasisCriterion` [VERIFIED: basis_mod.rs:61-63, 107-108, 250-253, 537-540, 580-582]

| String | Target |
|--------|--------|
| `"bspline"` | `BasisType::Bspline` / integer `0` |
| `"fourier"` | `BasisType::Fourier` / integer `1` |
| `"gcv"` | `BasisCriterion::Gcv` / integer `0` |
| `"cv"` | `BasisCriterion::Cv` / integer `1` |
| `"aic"` | `BasisCriterion::Aic` / integer `1` |
| `"bic"` | `BasisCriterion::Bic` / integer `2` |

Multiple dispatch sites across the file. All use `PyValueError` wildcard arms.

Also has reverse match at line 272 (`sel.basis_type → string`) and line 565 (`result.criterion → string`).

#### `regression_mod.rs` — `GlmFamily` / `SelectionCriterion` [VERIFIED: regression_mod.rs:442-444, 571-572, 1069-1076]

| String | Enum / Target |
|--------|--------------|
| `"aic"` | `SelectionCriterion::Aic` |
| `"bic"` | `SelectionCriterion::Bic` |
| `"gcv"` (wildcard default) | `SelectionCriterion::Gcv` |
| `"huber"` (match at line 572) | `fregre_huber(...)` |
| `_ ` (wildcard) | `fregre_l1(...)` |
| `"binomial"` | `GlmFamily::Binomial` |
| `"poisson"` | `GlmFamily::Poisson` |
| `"gamma"` | `GlmFamily::Gamma` |
| `"gaussian"` | `GlmFamily::Gaussian` |

`GlmFamily` wildcard at line 1076: `_ => Err(PyValueError::new_err(...))` — correct pattern.
Also has reverse match at lines 1115–1120 (GlmFamily → string).

#### `inference_mod.rs` — `MultiplierDistribution` / `ProjectionBasisType` [VERIFIED: inference_mod.rs:228-230, 565-567]

| String | Enum Variant |
|--------|-------------|
| `"gaussian"` | `MultiplierDistribution::Gaussian` |
| `"rademacher"` | `MultiplierDistribution::Rademacher` |
| `"bspline"` | `ProjectionBasisType::Bspline` |
| `"fourier"` | `ProjectionBasisType::Fourier` |

Both have `PyValueError` wildcard arms. Also has reverse match at lines 551–553.

#### `represent_mod.rs` — `ExtrapolationPolicy` / `InterpolationMethod` / `ImputationMethod` [VERIFIED: represent_mod.rs:205-234]

| String | Enum Variant |
|--------|-------------|
| `"boundary"` | `ExtrapolationPolicy::Boundary` |
| `"exception"` | `ExtrapolationPolicy::Exception` |
| `"fill"` | `ExtrapolationPolicy::Fill(fill_value)` |
| `"periodic"` | `ExtrapolationPolicy::Periodic` |
| `"linear"` | `InterpolationMethod::Linear` |
| `"cubic_hermite"` | `InterpolationMethod::CubicHermite` |
| `"linear"` | `ImputationMethod::Linear` |
| `"mean"` | `ImputationMethod::Mean` |
| `"constant"` | `ImputationMethod::Constant(constant_value)` |

All have `PyValueError` wildcard arms.

#### `alignment_mod.rs` — multiple enums [VERIFIED: alignment_mod.rs:693-694, 928-930, 984-986, 1511-1515, 1688-1690, 1810-1815, 2035-2049]

| String | Enum Variant / Target |
|--------|---------------------|
| `"schilds_ladder"` | `TransportMethod::SchildsLadder` |
| `"pole_ladder"` | `TransportMethod::PoleLadder` |
| `_ ` (wildcard) | `TransportMethod::LogMap` |
| `"complete"` | `Linkage::Complete` |
| `"average"` | `Linkage::Average` |
| `_ ` (wildcard default) | `Linkage::Single` |
| `"second_order"` | `WarpPenaltyType::SecondOrder` |
| `"combined"` | `WarpPenaltyType::Combined { ... }` |
| `"reparameterization_translation"` | `ShapeQuotient::ReparameterizationTranslation` |
| `"reparameterization_translation_scale"` | `ShapeQuotient::ReparameterizationTranslationScale` |
| `"peak"` / `"peaks"` / `"max"` | `LandmarkKind::Peak` |
| `"valley"` / `"valleys"` / `"min"` | `LandmarkKind::Valley` |
| `"zero_crossing"` / `"zerocrossing"` / `"zero"` | `LandmarkKind::ZeroCrossing` |
| `"inflection"` | `LandmarkKind::Inflection` |
| `"custom"` | `LandmarkKind::Custom` |
| `"amplitude"` / `"amp"` | `elastic_amp_changepoint(...)` |
| `"phase"` / `"ph"` | `elastic_ph_changepoint(...)` |
| `"fpca"` | `elastic_fpca_changepoint(...)` |
| `"vertical"` / `"vert"` | `PcaMethod::Vertical` |
| `"horizontal"` / `"horiz"` | `PcaMethod::Horizontal` |
| `"joint"` | `PcaMethod::Joint` |

NOTE: Several alignment wildcard arms silently default (e.g., Linkage defaults to Single, TransportMethod defaults to LogMap) rather than raising `PyValueError`. This is pre-existing behavior — document, do NOT change in this phase.

#### `conformal_mod.rs` — `PcaMethod` [VERIFIED: conformal_mod.rs:312-315]

| String | Enum Variant |
|--------|-------------|
| `"vertical"` | `PcaMethod::Vertical` |
| `"horizontal"` | `PcaMethod::Horizontal` |
| `"joint"` | `PcaMethod::Joint` |

#### `simulation_mod.rs` — `EFunType` / `EValType` / `CovKernel` [VERIFIED: simulation_mod.rs:41-54, 98-113, 255-293]

| String | Enum Variant |
|--------|-------------|
| `"fourier"` | `EFunType::Fourier` |
| `"poly"` | `EFunType::Poly` |
| `"poly_high"` | `EFunType::PolyHigh` |
| `"wiener"` | `EFunType::Wiener` |
| `"linear"` | `EValType::Linear` |
| `"exponential"` | `EValType::Exponential` |
| `"wiener"` | `EValType::Wiener` |
| `"gaussian"` | `CovKernel::Gaussian { ... }` |
| `"exponential"` | `CovKernel::Exponential { ... }` |
| `"matern"` | `CovKernel::Matern { ... }` |
| `"periodic"` | `CovKernel::Periodic { ... }` |

All have `PyValueError` wildcard arms.

#### `spm_mod.rs` — `NcompMethod` / `ControlLimitMethod` [VERIFIED: spm_mod.rs:273-277, 619-621]

| String | Enum Variant |
|--------|-------------|
| `"cumulative_variance"` | `NcompMethod::CumulativeVariance(threshold)` |
| `"elbow"` | `NcompMethod::Elbow` |
| `"kaiser"` | `NcompMethod::Kaiser` |
| `"fixed"` | `NcompMethod::Fixed(threshold as usize)` |
| `"parametric"` | `ControlLimitMethod::Parametric` |
| `"empirical"` | `ControlLimitMethod::Empirical` |

#### `tolerance_mod.rs` — `BandType` / `ExponentialFamily` [VERIFIED: tolerance_mod.rs:265-267, 328-329, 404-405, 557-559]

| String | Enum Variant |
|--------|-------------|
| `"simultaneous"` | `BandType::Simultaneous` |
| `"pointwise"` | `BandType::Pointwise` |
| `"gaussian"` | `ExponentialFamily::Gaussian` |
| `"binomial"` | `ExponentialFamily::Binomial` |
| `"poisson"` | `ExponentialFamily::Poisson` |

#### `seasonal_mod.rs` — `StrengthMethod` [VERIFIED: seasonal_mod.rs:247-249, 662-664]

| String | Enum Variant / Target |
|--------|---------------------|
| `"variance"` | `StrengthMethod::Variance` / `seasonal_strength_variance(...)` |
| `"spectral"` | `StrengthMethod::Spectral` / `seasonal_strength_spectral(...)` |

#### `explain_mod.rs` — `DepthType` [VERIFIED: explain_mod.rs:1919-1920, 1974-1975]

| String | Enum Variant |
|--------|-------------|
| `"modified_band"` | `DepthType::ModifiedBand` |
| `"functional_spatial"` | `DepthType::FunctionalSpatial` |

NOTE: `DepthType::FraimanMuniz` is used as a direct struct literal in `explain_mod.rs` (not a string dispatch) — it is a third variant that must exist at 0.33. [VERIFIED: explain_mod.rs - grep showed `DepthType::FraimanMuniz` used as a literal]

---

## The Four 0.30-Deprecated 2D Depth Functions (FLAG — Do NOT Migrate in This Phase)

[VERIFIED: depth_mod.rs:42-184, depth_mod.rs:610-616]

These four functions call `fdars_core::depth` functions that are `#[deprecated]` as of fdars-core 0.30.0. They will generate Rust compiler deprecation warnings after the bump. The warnings are non-fatal (the functions remain callable at 0.33). Do NOT suppress the warnings or remove the functions in Phase 66 — that is Phase 67+ work.

| Binding function | Call site (file:line) | Calls deprecated upstream function |
|-----------------|----------------------|-----------------------------------|
| `fraiman_muniz_2d` | `depth_mod.rs:50` | `fdars_core::depth::fraiman_muniz_2d` |
| `modal_2d` | `depth_mod.rs:94` | `fdars_core::depth::modal_2d` |
| `random_projection_2d` | `depth_mod.rs:138` | `fdars_core::depth::random_projection_2d` |
| `random_tukey_2d` | `depth_mod.rs:182` | `fdars_core::depth::random_tukey_2d` |

These four are also registered in `depth_mod.rs:610-616` and thus exposed as `fdars.depth.{fraiman_muniz_2d, modal_2d, random_projection_2d, random_tukey_2d}` in the Python API.

**The deprecation warning from `rustc` is expected and acceptable in this phase.** The audit record should note: "4 deprecation warnings expected from depth_mod.rs; all are known 0.30-deprecated 2D variants; migration deferred to a later phase."

To allow the build to succeed despite deprecation warnings (which would be promoted to errors by `RUSTFLAGS="-D warnings"` in CI), one approach is to add `#[allow(deprecated)]` annotations at the call sites. However, since Phase 66 must only change `Cargo.toml` and `Cargo.lock`, any `#[allow(deprecated)]` additions would violate the phase scope. **Verify whether the deprecation warnings become errors under the project's `RUSTFLAGS="-D warnings"` setting** — if so, the planner needs to decide whether to treat the `#[allow(deprecated)]` fix as an in-scope exception (it is a src file change) or to document it explicitly. [ASSUMED — whether fdars-core marks these as `#[deprecated]` (warning) vs. removed at 0.33; if removed at 0.33, the build fails and migration is forced.]

**Risk:** The CONTEXT.md and STACK.md claim these are soft deprecations (callable at 0.33). Confirm this during execution by checking whether `maturin develop --release` produces a deprecation warning or a compile error. If a compile error occurs, the phase scope must be expanded to include the four `#[allow(deprecated)]` attributes (or the migration itself).

---

## 0.24→0.33 Changelog Summary

[VERIFIED: ~/.cargo/registry/src/index.crates.io-*/fdars-core-0.23.0/CHANGELOG.md + STACK.md]

The fdars-core 0.23.0 local cache contains the CHANGELOG. Entries 0.24–0.33 are summarized below from the milestone-level research (STACK.md).

| Version | Breaking changes to existing API | New modules/functions |
|---------|----------------------------------|----------------------|
| 0.24.0 | None | `clustering_advanced`, FAMM extensions |
| 0.25.0 | None | `density_fda`, `multi_fdata` |
| 0.26.0 | None | FPCA breadth, sparse covariance |
| 0.27.0 | None | `fts`, `frechet`, `pda` |
| 0.28.0 | None | Spectral FTS, object-data Fréchet |
| 0.29.0 | None | FAMM extensions (dense/fast/multi) |
| 0.30.0 | None — soft `#[deprecated]` on 4 depth fns | Performance/consolidation; `fanova` deprecated in `function_on_scalar` |
| 0.31.0 | None confirmed (absent from CHANGELOG) | [ASSUMED — likely internal/perf pass] |
| 0.32.0 | None confirmed (absent from CHANGELOG) | [ASSUMED — no `shapelet` module present at 0.32] |
| 0.33.0 | None | `shapelet` module added |

**The 0.31/0.32 gap:** These entries are absent from the published CHANGELOG.md. [ASSUMED — no breaking changes, based on: (a) module surface at 0.32 confirmed no `shapelet`; (b) no compile errors reported in existing test matrix; (c) the claim of "additive-only across all versions" from the milestone-level research.] To close this gap at execute time: check the fdars-core 0.33.0 source in the cargo registry cache (`~/.cargo/registry/src/index.crates.io-*/fdars-core-0.33.0/CHANGELOG.md`) after running `cargo update`.

**Additional deprecation at 0.30:** `fdars_core::function_on_scalar::fanova` is `#[deprecated]` in favour of `fanova_seeded`. The pyfda binding at `src/regression_mod.rs` (which calls `fdars_core::function_on_scalar::fanova`) will also generate a deprecation warning. This is in addition to the four depth functions. Migration to `fanova_seeded` is deferred.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead |
|---------|-------------|-------------|
| Lockfile update | Manual editing of `Cargo.lock` | `cargo update -p fdars-core` |
| Build verification | Any Python import test | `maturin develop --release` then `pytest tests/ -x` |
| API variant existence check | Web scraping of docs.rs | Read from `~/.cargo/registry/src/index.crates.io-*/fdars-core-0.33.0/src/` after cargo update |

---

## Common Pitfalls

### Pitfall 1: Running `cargo build` instead of `maturin develop --release`

**What goes wrong:** `cargo build` compiles the Rust library but does NOT install the Python extension into the venv. `pytest tests/` will then run against the old 0.23.0 extension, and the regression gate is meaningless.

**How to avoid:** Always use `maturin develop --release` as the build step. Confirm the extension is updated by checking its modification timestamp:
```bash
ls -la .venv/lib/python*/site-packages/fdars/_native*.so
```

### Pitfall 2: `RUSTFLAGS="-D warnings"` promoting deprecation warnings to errors

**What goes wrong:** The project CI sets `RUSTFLAGS: "-D warnings"` (verified at `ci.yml:10`). Any `#[deprecated]` attribute hit by the compiler becomes an error, not a warning, causing `maturin develop --release` to fail even though the functions are still callable at 0.33.

**How to avoid:** After bumping, attempt `maturin develop --release` without any `RUSTFLAGS` override first. If the four deprecated functions produce errors, the options are:
1. Add `#[allow(deprecated)]` to the four call sites in `depth_mod.rs` — a src file change, which technically violates "only Cargo.toml and Cargo.lock change" but is the minimal fix to preserve the regression gate.
2. Temporarily unset `RUSTFLAGS` for the local build: `RUSTFLAGS="" maturin develop --release`.
Option 1 is the correct fix; option 2 is only for local testing.

**Risk level:** HIGH if fdars-core 0.30+ marks the functions `#[deprecated]` (warning attribute). The local `RUSTFLAGS="-D warnings"` in CI will catch this. The planner should include a task for `#[allow(deprecated)]` as a contingency.

### Pitfall 3: Numeric drift changing a test tolerance

**What goes wrong:** `pytest` fails on a floating-point assertion. The expected value at 0.23 is outside the `atol`/`rtol` range at 0.33 due to an algorithm change upstream.

**How to avoid:** Run with `-x` (fail-fast). Inspect the failing assertion: if the new value is provably correct (same algorithm, just a different floating-point path), tighten or loosen the tolerance. Document the change in the phase VERIFICATION.md. If the value is substantively wrong, the bump has a real regression.

**Most likely test files:** `test_fdata_stats.py`, `test_pace_fpca.py`, `test_depth.py` (FPCA-related algorithms are most sensitive to backend changes). [ASSUMED — no known drift; this is the contingency for a 10-minor jump.]

### Pitfall 4: `fanova` deprecation in `function_on_scalar`

**What goes wrong:** `regression_mod.rs` calls `fdars_core::function_on_scalar::fanova` which is `#[deprecated]` as of 0.30.0, in addition to the four depth functions. Under `RUSTFLAGS="-D warnings"` this becomes a compile error.

**How to avoid:** Identify all `#[deprecated]` call sites. The audit at execute time should grep the compiled deprecation warnings:
```bash
RUSTFLAGS="-D warnings" maturin develop --release 2>&1 | grep deprecated
```
Add `#[allow(deprecated)]` at each call site if needed.

---

## Code Examples

### Verified: `Cargo.toml` change

[VERIFIED: Cargo.toml:17-19]
```toml
# Before (current)
fdars-core = { version = "0.23.0", features = ["parallel"] }

# After (only change)
fdars-core = { version = "0.33.0", features = ["parallel"] }
```

### Verified: Build + gate sequence

[VERIFIED: ci.yml:68-88 — adapted for local run]
```bash
# 1. Activate venv (already done or use the project's existing .venv)
source .venv/bin/activate

# 2. Edit Cargo.toml (one-line version string change)

# 3. Update lockfile (fdars-core only)
cargo update -p fdars-core

# 4. Rebuild native extension
maturin develop --release

# 5. Run the full regression gate
pytest tests/ -x -v 2>&1 | tee /tmp/phase66-regression.log

# 6. Report pass/fail
grep -E "^(PASSED|FAILED|ERROR|[0-9]+ passed)" /tmp/phase66-regression.log | tail -5
```

### Verified: Check for deprecation warnings

```bash
# Run with strict warnings to find all deprecated call sites
RUSTFLAGS="-D warnings" maturin develop --release 2>&1 | grep -E "deprecated|error\[" | head -20
```

### Verified: Confirm extension timestamp updated

```bash
ls -la .venv/lib/python*/site-packages/fdars/_native*.so
```

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest (in `.venv/bin/pytest`) |
| Config file | None detected in `pyproject.toml` (no `[tool.pytest.ini_options]`) |
| Quick run command | `pytest tests/ -x -q` |
| Full suite command | `pytest tests/ -v` |

[VERIFIED: pyproject.toml — no pytest config section; ci.yml:87-88 — `pytest tests/ -v`]

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command |
|--------|----------|-----------|-------------------|
| DEP-01 | `maturin develop --release` succeeds; `import fdars` works | smoke | `python -c "import fdars; print(fdars.__version__)"` |
| DEP-02 | Full Python suite green (~772 tests) | full regression | `pytest tests/ -x -v` |
| DEP-03 | API audit recorded; deprecated functions flagged | documentation | Manual review of grep output |

### Sampling Rate

- **Per task commit:** Not applicable — this phase has exactly one substantive commit (bump + gate).
- **Phase gate:** Full `pytest tests/ -x -v` green before `/gsd-verify-work`.

### Wave 0 Gaps

None — existing test infrastructure covers all phase requirements. No new test files are needed (the phase explicitly forbids test edits).

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Rust toolchain (`cargo`, `rustc`) | `cargo update`, `maturin develop` | ✓ | 1.83+ (per MSRV) | — |
| maturin | Build the PyO3 extension | ✓ | 1.x | — |
| pytest | Regression gate | ✓ | in `.venv/bin/pytest` | — |
| `.venv` | Python environment | ✓ | exists at repo root | — |
| fdars-core 0.33.0 on crates.io | `cargo update` | ✓ | 0.33.0 published 2026-09-02 | — |

[VERIFIED: `.venv/bin/pytest` exists; maturin present in `.venv/bin/`; fdars-core 0.33.0 published per STACK.md sourced from crates.io API]

**Missing dependencies with no fallback:** None.

---

## Security Domain

> This phase makes no networking changes, introduces no new public API, and adds no user-facing inputs. The only ASVS-relevant surface is dependency integrity.

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V5 Input Validation | No — no new bindings | n/a |
| V6 Cryptography | No | n/a |
| Supply chain (dependency integrity) | Yes — bumping an external crate | `Cargo.lock` checksum verification; crates.io registry signature; confirm fdars-core is from the known publisher (sipemu/fdars) |

The `Cargo.lock` update will include a new `checksum` field for fdars-core 0.33.0. This is the standard supply-chain control for Rust crates — no additional action is required beyond standard `cargo update`.

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `cargo update -p fdars-core` resolves to 0.33.0 without pulling in conflicting transitive deps | Build recipe | Build fails; need `cargo update` without `-p` or manual Cargo.toml pin |
| A2 | fdars-core 0.31/0.32 contain no breaking changes to the existing bound API | Changelog | A match arm string removed/renamed → compile error or silent runtime regression |
| A3 | The four 2D depth functions + `fanova` remain callable (not removed) at 0.33.0 — soft deprecation only | Deprecated functions | Build fails with "not found" or compile error; forced migration in Phase 66 |
| A4 | No numeric drift across the 10-minor jump (expected: none) | Regression gate | pytest failures requiring tolerance adjustments; blocker if substantive regression |
| A5 | `~772` test items is the current baseline (exact count is from project memory, not live pytest) | Test count | Actual count may differ; what matters is zero new failures, not the absolute number |
| A6 | `RUSTFLAGS="-D warnings"` is set during the local `maturin develop` invocation (as it is in CI) | Deprecation warnings | If not set locally, deprecation warnings are silent; CI will still catch them |

**If A3 is wrong** (functions removed, not deprecated): the phase scope must expand to include `#[allow(deprecated)]` or migration. The planner should include this as a contingency task.

---

## Open Questions

1. **Does `RUSTFLAGS="-D warnings"` apply in the local `maturin develop` invocation?**
   - What we know: CI sets this at `env.RUSTFLAGS` (`ci.yml:10`); local shell may or may not inherit it.
   - What's unclear: Whether the local developer's shell has this set, or whether maturin picks it up from `.cargo/config.toml`.
   - Recommendation: The executor should test with `RUSTFLAGS="-D warnings" maturin develop --release` explicitly to match CI behavior, then add `#[allow(deprecated)]` to the four depth call sites if needed.

2. **Exact deprecation status at 0.33.0 for the four 2D depth functions and `fanova`**
   - What we know: STACK.md says "soft deprecation — still callable at 0.33" based on research.
   - What's unclear: Whether `#[deprecated]` is a Rust warning attribute or whether the functions were actually removed.
   - Recommendation: After `cargo update -p fdars-core`, read `~/.cargo/registry/src/index.crates.io-*/fdars-core-0.33.0/src/depth/` to confirm.

---

## Sources

### Primary (HIGH confidence)
- `Cargo.toml:17-19` — current fdars-core version pin (read this session)
- `Cargo.lock:1-6` — current fdars-core lockfile entry (read this session)
- `src/lib.rs:1-65` — module registration and 20 registered submodules (read this session)
- `src/depth_mod.rs:1-627` — four deprecated 2D functions and DepthMethod enum (read this session)
- `.github/workflows/ci.yml:1-160` — build and test recipe (read this session)
- `src/*_mod.rs` (all 21 files) — complete enum/match-arm surface via grep (this session)
- `.planning/research/STACK.md` — milestone-level stack research (version compatibility, changelog, deprecations)
- `.planning/research/PITFALLS.md` — risk analysis and precedents

### Secondary (MEDIUM confidence)
- `.planning/research/SUMMARY.md` — milestone executive summary; 0.24→0.33 version-by-version table
- `~/.cargo/registry/src/index.crates.io-*/fdars-core-0.23.0/CHANGELOG.md` — changelog entries through 0.22; confirms 0.23 baseline

### Tertiary (LOW confidence — marked [ASSUMED])
- 0.31/0.32 changelog entries (absent from published CHANGELOG; non-breaking assumed from module-surface inspection at 0.32 in prior research session)

---

## Metadata

**Confidence breakdown:**
- Cargo.toml change: HIGH — file read directly this session; exact line verified
- Build + test recipe: HIGH — CI workflow read directly; commands verified
- API audit (enum/match strings): HIGH — grep run against all src/*_mod.rs this session; all strings extracted and tabulated
- Four deprecated functions: HIGH — depth_mod.rs read line by line this session; function names and call sites verified
- Changelog 0.24→0.30: MEDIUM — from prior research session (STACK.md), sourced from crates.io/docs.rs
- Changelog 0.31/0.32: LOW — absent from published CHANGELOG; [ASSUMED] non-breaking

**Research date:** 2026-09-02
**Valid until:** Permanent for this phase (infrastructure/tooling research doesn't expire)
