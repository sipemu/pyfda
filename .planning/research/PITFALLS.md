# Pitfalls Research

**Domain:** PyO3 binding upgrade — fdars-core 0.17 → 0.20 (functional inference + depth/boxplot + AIC smoothing)
**Researched:** 2026-08-17
**Confidence:** HIGH (docs.rs signatures verified against 0.20.0; codebase read directly; v4.0 retrospective confirmed)

---

## Critical Pitfalls

### Pitfall 1: `seed` Is `u64` Not `Option<u64>` — Forced Exposure Breaks Optional Semantics

**What goes wrong:**
`t_perm_test` and `f_perm_test` take `seed: u64` (required, non-optional in Rust). The wrapper must make it optional at the Python boundary (`seed: Option<u64>`) and pick a documented default (e.g. `42`) when `None`. If the wrapper accepts an optional Python value but passes it straight through to a non-optional Rust parameter, the compiler will reject it. If the wrapper hard-codes a magic constant without documenting it, docs fences will produce non-reproducible byte streams across runs (CI false-negatives on the determinism test). `two_sample_mean_test` is seedless (uses chi-squared asymptotic distribution) — no seed parameter should be exposed for it.

**Why it happens:**
Upstream Rust API takes `u64` directly (uses `StdRng::seed_from_u64(seed)` internally). Developers mirroring the Rust signature forget that Python callers expect `seed=None` as a reproducibility opt-in, not a mandatory integer.

**How to avoid:**
- In the wrapper: `#[pyo3(signature = (data_a, data_b, argvals, n_perm=999, seed=None))]`; inside, resolve `seed.unwrap_or(42)` and document the default explicitly in the docstring.
- For `two_sample_mean_test` (no seed): expose `ncomp: usize` with a documented default (e.g. `3`). Do not add a spurious `seed` parameter.
- Determinism test: assert that calling the wrapper twice with identical `seed` returns byte-identical `json.dumps` output; assert that the result dict contains only plain Python `float` values, not `np.float64` scalars.

**Warning signs:**
- Compiler error "expected `u64`, found `Option<u64>`" in the wrapper.
- Determinism CI test sees different p-values across two consecutive calls with `seed=None` after the default is set (exposes a non-deterministic default).
- The offline docs fence emits a different `statistic` value on each docs build.

**Phase to address:**
Group A bindings phase (inference submodule). Determinism tests must be written in the same phase before docs fences are authored.

---

### Pitfall 2: `CvCriterion`, `DepthMethod`, and `MultiplierDistribution` Are `#[non_exhaustive]` — Missing Wildcard Arm Blocks Compilation

**What goes wrong:**
`fdars_core::smoothing::CvCriterion` (variants: `Cv`, `Gcv`, `Aic`) and `fdars_core::tolerance::MultiplierDistribution` (variants: `Gaussian`, `Rademacher`) and `fdars_core::depth::dispatch::DepthMethod` (variants: `FraimanMuniz { scale }`, `Band`, `ModifiedBand`, `RandomProjection { nproj, seed }`) are all `#[non_exhaustive]`. The existing `optim_bandwidth` binding in `smoothing_mod.rs` has a two-arm match (`"cv" => CvCriterion::Cv`, `"gcv" => CvCriterion::Gcv`) and a result-stringify match (`CvCriterion::Cv => "cv"`, `CvCriterion::Gcv => "gcv"`) with no wildcard arm. After bumping to 0.20 the crate reports `Aic` as a third variant. Rust will refuse to compile any exhaustive match on a `#[non_exhaustive]` enum from another crate. The same pattern recurs for the `mean_scb`/`scb_two_sample_test` wrappers that accept a `MultiplierDistribution` string param and for `functional_depth`/`functional_boxplot` that accept a `DepthMethod` string param.

**Why it happens:**
The v4.0 bindings were written against 0.14→0.17 where `CvCriterion` only had `Cv`/`Gcv`. The bump to 0.20 adds `Aic` to `CvCriterion` and introduces `DepthMethod` and `MultiplierDistribution` as `#[non_exhaustive]` enums.

**How to avoid:**
- All match arms on `CvCriterion` (both string-to-enum and enum-to-string directions): add `_ => return Err(PyValueError::new_err("criterion must be 'cv', 'gcv', or 'aic'"))` and `_ => "unknown"` respectively.
- `MultiplierDistribution` wrappers: `"gaussian" => MultiplierDistribution::Gaussian`, `"rademacher" => MultiplierDistribution::Rademacher`, `_ => return Err(PyValueError...)`.
- `DepthMethod` wrappers: `"fraiman_muniz"` → `FraimanMuniz { scale }`, `"band"` → `Band`, `"modified_band"` → `ModifiedBand`, `"random_projection"` → `RandomProjection { nproj, seed }`, `_` → `PyValueError`.
- `BasisCriterion` in `smooth_basis` is NOT `#[non_exhaustive]` — no wildcard needed there (confirmed from docs.rs).

**Warning signs:**
- `cargo build` error: `non-exhaustive patterns: _ not covered` on any match touching `CvCriterion`, `DepthMethod`, or `MultiplierDistribution`.
- Clippy `-D warnings` (enforced in CI) will promote this to a hard failure if rustc does not catch it first.

**Phase to address:**
Crate bump phase (Phase 1 regression gate). The existing `optim_bandwidth` binding already has the missing wildcard for `CvCriterion` — it must be fixed as part of the bump itself before any new bindings are written, or the compile will fail and block all downstream phases.

---

### Pitfall 3: `FunctionalBoxplotResult` and `TestResult` Are `#[non_exhaustive]` — Struct-Literal Construction Blocked in Tests

**What goes wrong:**
Both `FunctionalBoxplotResult` (fields: `median Vec<f64>`, `central_lower Vec<f64>`, `central_upper Vec<f64>`, `whisker_lower Vec<f64>`, `whisker_upper Vec<f64>`, `outliers Vec<usize>`, `depths Vec<f64>`) and `TestResult` (fields: `statistic f64`, `p_value f64`, `n_perm usize`) are `#[non_exhaustive]`. Field access via `.field` is safe. The pitfall is constructing test fixtures using struct literals (`TestResult { statistic: 1.0, p_value: 0.05, n_perm: 999 }`) — the compiler will refuse. Future upstream fields would also be silently dropped from the PyDict if the wrapper manually hard-codes the field list.

**Why it happens:**
Developers copy the Rust struct-literal test pattern from intra-crate tests (valid within the defining crate). The same literal syntax fails in external crates like pyfda.

**How to avoid:**
- In PyO3 wrappers: access each field individually (`result.median`, `result.central_lower`, etc.) — safe for `#[non_exhaustive]` structs.
- In test fixtures: construct `TestResult` via the public functions that return it (call `t_perm_test` with minimal synthetic data of 5 curves × 3 grid points), not via struct literals.
- `FunctionalBoxplotResult` complete dict mapping: `median`, `central_lower`, `central_upper`, `whisker_lower`, `whisker_upper`, `outliers` (Vec<usize> → i64 numpy array via `usize_vec_to_numpy1d`), `depths`.
- `TestResult` complete dict mapping: `statistic` (f64 → float), `p_value` (f64 → float), `n_perm` (usize → int).

**Warning signs:**
- Compiler error: "cannot create non-exhaustive struct using struct expression."
- Missing dict key at runtime (Python `KeyError`) if a field is omitted from the `dict.set_item` block.

**Phase to address:**
Group A and Group B binding phases. Field-name list must be verified against docs.rs before writing wrapper code.

---

### Pitfall 4: FLM Inference Takes `&FregreLmResult` — Python Has No Handle to a Rust Struct

**What goes wrong:**
`flm_f_test(fit: &FregreLmResult)` and `flm_gof_test(fit: &FregreLmResult)` take a reference to a Rust struct. The existing Python binding for `fregre_lm` converts the Rust result to a PyDict and discards the Rust struct. A naive wrapper for `flm_f_test` cannot reconstruct `FregreLmResult` from a Python dict because `FregreLmResult` is `#[non_exhaustive]` and cannot be built with struct literals from outside the crate. `FregreLmResult` is in `fdars_core::scalar_on_function`, not `fdars_core::regression` — the module path must be verified.

**Why it happens:**
Rust's ownership model means Rust structs live on the Rust side; PyO3 does not automatically create Python-side handles to arbitrary Rust structs unless they are wrapped in `#[pyclass]`. `FregreLmResult` is not a `#[pyclass]`.

**How to avoid:**
- Preferred pattern: expose `flm_f_test` as a Python function that accepts the same inputs as `fregre_lm` (data + response + n_comp), re-runs `fdars_core::scalar_on_function::fregre_lm` internally, then calls `flm_f_test` on the Rust result. Return a dict with both the fit fields and the `TestResult` fields.
- Alternative: a combined `fregre_lm_with_inference` wrapper that bundles fit + f-test + gof-test in one call.
- Do NOT expose a Python-callable `flm_f_test(fit_dict)` that tries to reconstruct `FregreLmResult` from a Python dict — it will not compile.
- `FregreLmResult` confirmed fields: `intercept`, `beta_t`, `beta_se`, `gamma`, `fitted_values`, `residuals`, `r_squared`, `r_squared_adj`, `std_errors`, `ncomp`, `fpca` (FpcaResult nested), `coefficients`, `residual_se`, `gcv`, `aic`, `bic`.

**Warning signs:**
- Compiler error about struct literal on `#[non_exhaustive]` struct.
- The `flm_f_test` docstring says "pass the fitted model" with no explanation of how Python callers obtain one.

**Phase to address:**
Group A bindings phase. The design decision (re-run vs. combined wrapper) must be made before writing the code — it affects the Python API surface visible to users.

---

### Pitfall 5: Permutation Tests in Executed Docs Fences — `n_perm=999` Blows Up the 18-Minute Build

**What goes wrong:**
A standard `t_perm_test` call with `n_perm=999` on even a 50-curve dataset adds several seconds of compute per fence. Multiplied across five or six worked-example fences (permutation test, SCB band, two-sample test, ANOVA), the existing ~18-minute wall time could double or triple. `mkdocs build` already caused timeouts and process pile-ups in v4.0.

**Why it happens:**
Developers use production-quality `n_perm` values (999 or 1999) in examples to show credible p-values. The docs build runs every fence sequentially, so each example contributes additively.

**How to avoid:**
- All executed docs fences for inference functions: `n_perm=19` (enough to avoid degenerate p-values; keeps per-fence compute under 0.5s).
- Use small synthetic datasets (20 curves × 10 grid points) embedded inline in the fence — not loaded from `docs/data/` CSV.
- Use the illustrative-vs-executed fence split (established in v2.1): show a full-resolution reference fence in a collapsible tab (not executed) and only run the cheap version.
- Wire inference fences behind the `DOCS_FAST` env var check already established in the project.
- For SCB fences: `nb=50` bootstrap replicates instead of `nb=1000`.

**Warning signs:**
- A fence takes > 5 seconds in local `mkdocs serve`.
- `mkdocs build` takes 30+ minutes in CI.
- `n_perm >= 100` appears in any executed fence.

**Phase to address:**
Docs phase (last). But the constraint must be documented in the binding-phase plan so worked-example authors know the limit before writing.

---

### Pitfall 6: `mean_scb` Returns `ToleranceBand` Not `TestResult` — Layout Is 1×m, Not n×m

**What goes wrong:**
`mean_scb` returns `Result<ToleranceBand, FdarError>`. `ToleranceBand` is a tolerance-band struct with `lower` and `upper` fields of type `Vec<f64>` (length m each) — not an FdMatrix, not a `TestResult`. `scb_two_sample_test` returns `Result<TestResult, FdarError>` (scalar: statistic, p-value, n_perm=0 fixed). Conflating the two leads to a wrong return type in the wrapper. If the wrapper passes `ToleranceBand`'s flat Vec to `fdmatrix_to_numpy2d`, the call will panic on the shape mismatch.

**Why it happens:**
The name `mean_scb` suggests it returns a "test" but it actually returns the band itself. The two SCB functions have different return types and require separate wrapper strategies.

**How to avoid:**
- `mean_scb` wrapper: return a dict with `lower: ndarray(m,)` and `upper: ndarray(m,)` extracted from `ToleranceBand.lower` and `ToleranceBand.upper` as 1-D arrays via `vec_to_numpy1d`. Verify `ToleranceBand` field names against docs.rs before writing.
- `scb_two_sample_test` wrapper: return a dict with `statistic`, `p_value`, `n_perm` (always 0 for this function).
- Shape assertion test: `assert result["lower"].shape == (m,)`.

**Warning signs:**
- `fdmatrix_to_numpy2d` panics on a 1-D flat vector.
- The returned array has shape `(1, m)` or `(m, 1)` instead of `(m,)`.

**Phase to address:**
Group A bindings phase. Shape assertions must be part of the binding test before the docs fence is authored.

---

### Pitfall 7: `functional_depth` Dispatcher — `DepthMethod::RandomProjection` Carries `seed: u64` In the Variant

**What goes wrong:**
`functional_depth(data: &FdMatrix, method: DepthMethod) -> Result<Vec<f64>, FdarError>`. `DepthMethod::RandomProjection { nproj: usize, seed: u64 }` carries the seed inside the enum variant, not as a separate function argument. The Python wrapper must accept `seed` as a top-level Python kwarg (`seed=None`) and route it into the enum construction: `DepthMethod::RandomProjection { nproj, seed: seed_val.unwrap_or(42) }`. If the wrapper accepts `method="random_projection"` with no `seed` kwarg and silently defaults to `seed=0`, results differ from the named `random_projection_1d` function (which uses a different default). Consistency test: `functional_depth(data, method="fraiman_muniz", scale=True)` must equal `fraiman_muniz_1d(data, data, scale=True)` (self-depth on all curves).

**Why it happens:**
Per-variant fields are invisible from the Python side. Developers unfamiliar with the `DepthMethod` enum shape may omit `nproj` and `seed` from the Python signature entirely.

**How to avoid:**
- Wrapper signature: `#[pyo3(signature = (data, method="fraiman_muniz", scale=True, nproj=50, seed=None))]`.
- String-to-enum dispatch with wildcard: `"fraiman_muniz"` → `FraimanMuniz { scale }`, `"band"` → `Band`, `"modified_band"` → `ModifiedBand`, `"random_projection"` → `RandomProjection { nproj, seed: seed.unwrap_or(42) }`, `_` → `PyValueError`.
- Determinism test for `method="random_projection"`: two calls with same `seed` return identical depth vectors.
- Self-depth consistency test: `functional_depth(data, "fraiman_muniz", scale=True)` == `fraiman_muniz_1d(data, data, scale=True)`.

**Warning signs:**
- Non-exhaustive match compile error on `DepthMethod`.
- Depth values from `functional_depth(method="fraiman_muniz")` diverge from `fraiman_muniz_1d` (scale default mismatch).

**Phase to address:**
Group B bindings phase.

---

### Pitfall 8: `functional_boxplot` `factor` Has No Rust Default — Python Default Must Be `1.5`; `outliers` Is `Vec<usize>` Not `Vec<f64>`

**What goes wrong:**
`functional_boxplot(data: &FdMatrix, method: DepthMethod, factor: f64) -> Result<FunctionalBoxplotResult, FdarError>` — `factor` is required in Rust with no default. If the Python default is `1.0` or `2.0`, the outlier classification diverges from the López-Pintado–Romo canonical value and from R's `fBoxplot` default. Additionally, `FunctionalBoxplotResult.outliers` is `Vec<usize>` (row indices) — passing it to `vec_to_numpy1d` (which handles only `f64`) will cause a type error; the correct converter is `usize_vec_to_numpy1d`.

**Why it happens:**
Rust makes `factor` required; the canonical default `1.5` is documented only in the method paper and docs.rs description. The type mismatch on `outliers` is easy to miss because all other `FunctionalBoxplotResult` fields are `Vec<f64>`.

**How to avoid:**
- `#[pyo3(signature = (data, method="fraiman_muniz", factor=1.5, scale=True, nproj=50, seed=None))]`.
- Convert `result.outliers` with `usize_vec_to_numpy1d(py, result.outliers)` — same pattern as existing alignment_mod.rs usage.
- Write a test that with a clean dataset (no outliers) `factor=1.5` returns an empty `outliers` array, and that with a spike-contaminated dataset it flags the spike.
- Docstring: cite López-Pintado and Romo (2009) for `factor=1.5`.

**Warning signs:**
- Type error at runtime from passing a `Vec<usize>` to `vec_to_numpy1d`.
- Outlier set differs from reference implementation for the same dataset.

**Phase to address:**
Group B bindings phase.

---

### Pitfall 9: `oneway_anova_vstat` Groups Parameter — Python `ndarray` Must Be `i64` Not `f64`

**What goes wrong:**
`oneway_anova_vstat(data: &FdMatrix, groups: &[usize], argvals: &[f64]) -> Result<TestResult, FdarError>`. `groups` is `&[usize]` in Rust. The pyfda convention for integer arrays uses `PyReadonlyArray1<'py, i64>` on the Python side and `numpy1d_to_usize_vec` to convert (already established in the codebase). If the wrapper uses `PyReadonlyArray1<'py, f64>` for groups, the conversion is lossy and may silently produce wrong group assignments. Numpy callers may also pass 1-indexed groups (Python convention) while Rust expects 0-indexed.

**Why it happens:**
Functional inference is new territory; the groups-as-integer-array input pattern appears only in clustering outputs in the existing code. An integer array input requires explicit handling.

**How to avoid:**
- Use `PyReadonlyArray1<'py, i64>` for the Python-facing `groups` parameter.
- Convert with the existing `numpy1d_to_usize_vec` utility from `convert.rs`.
- Validation guard: if `groups` is empty or contains indices ≥ `data.nrows()`, raise `PyValueError` before calling the Rust function.
- Document that groups are 0-indexed.
- Test with two groups (8+7 curves) to verify correct group parsing and that the returned `TestResult.n_perm > 0`.

**Warning signs:**
- Python caller passes `groups=np.array([1,2,1,2,...], dtype=float)` and the binding silently accepts it.
- Group indices are off-by-one.

**Phase to address:**
Group A bindings phase.

---

### Pitfall 10: Advisor Guard-Sync Broken If `inference` Aspect Lands in Two Commits

**What goes wrong:**
The `test_diagnostics_methods_match_advisor_supported` test (`tests/test_mcp_server.py:503`) asserts that `_DIAGNOSTICS_METHODS` in `mcp/server.py` equals the `_supported` set inferred from `advisor/__init__.py:build_diagnostics`. Adding `"inference"` to `build_diagnostics._supported` in one commit and updating `_DIAGNOSTICS_METHODS` in a second commit leaves a window where the test fails in CI between the two commits. The v4.0 retrospective explicitly called out that guard-sync edits must land in one atomic commit.

**Why it happens:**
Advisor work and MCP server work are in different files, tempting developers to separate them into separate commits.

**How to avoid:**
- Write both the `build_diagnostics` `"inference"` branch and the `_DIAGNOSTICS_METHODS` frozenset update in a single atomic commit.
- Run `pytest tests/test_mcp_server.py::test_diagnostics_methods_match_advisor_supported` locally before the commit to catch drift.
- The plan for the advisor phase must explicitly name this as a single-task commit, not two separate tasks.
- Decision required during the advisor discuss phase: `inference` should be diagnostics-only (not in `_RUNNABLE_METHODS`) because two-sample tests require two datasets and the single-dataset MCP runner cannot dispatch them.

**Warning signs:**
- CI goes red on `test_diagnostics_methods_match_advisor_supported` between two commits.
- The `aspects/inference.py` file exists but `_DIAGNOSTICS_METHODS` has not been updated.

**Phase to address:**
Advisor extension phase.

---

### Pitfall 11: Grounding-Invariant Violation — p-Values and Statistics Must Be Plain Python `float`, Not `np.float64`

**What goes wrong:**
`TestResult.statistic` and `TestResult.p_value` arrive in Python as `f64` converted by PyO3 to Python `float`. However, if the inference diagnostics aspect assembles these with `np.float64` intermediates (e.g. `result["statistic"]` extracted from a dict holding a numpy scalar), the `json.dumps` call in the offline determinism test fails with `TypeError: Object of type float64 is not JSON serializable`. Additionally, the grounding check (`_check_grounding`) walks the diagnostics dict looking for numbers to cross-reference against the LLM's advice; a numpy scalar is not found by a `str(float_val)` substring search.

**Why it happens:**
The inference aspect builder receives a Python dict. If a value was produced via numpy arithmetic, it arrives as `np.float64`. The builder inserts it without an explicit `float()` cast.

**How to avoid:**
- In `aspects/inference.py`: wrap every numeric field with `float(...)` before inserting into the diagnostics dict.
- Add the standard determinism assertion to the inference advisor test: `json.dumps(diag, sort_keys=True)` must not raise, and two calls must produce byte-identical output.
- Add the numpy-scalar leakage walk (same pattern as `test_advisor_registration_quality.py:229`): `assert not isinstance(val, np.generic)` for every leaf value.

**Warning signs:**
- `TypeError: Object of type float64 is not JSON serializable` in the offline advisor test.
- `json.dumps(diag)` raises in the docs fence (fence silently fails instead of printing `FDARS_FENCE_OK`).

**Phase to address:**
Advisor extension phase. The test must be written in the same task as the inference aspect, not after.

---

### Pitfall 12: Numeric Drift on the Existing 426-Test Suite From the 0.17 → 0.20 Bump

**What goes wrong:**
The existing suite (426 tests) uses floating-point tolerance comparisons for FPCA, elastic alignment, smoothing, and depth values. The 0.18 release was audit-only and 0.19 added the inference suite; 0.20 added quick wins. If any of these releases incidentally changed the numerical path for existing algorithms (reordered rayon task scheduling, changed tolerance epsilon), existing tolerance assertions could fail.

**Why it happens:**
The v4.0 bump (0.14→0.17) showed zero drift — but that was confirmed experimentally, not guaranteed. The 0.20 path passes through two additional releases. Even an audit-only pass can change LLVM optimization paths, leading to ULP-level differences.

**How to avoid:**
- The crate bump must be its own isolated phase (Phase 1), committed and CI-green before any new binding work.
- After the bump, run `cargo test` and `pytest` and capture the full result. Any failures are drift regressions, not new-binding bugs.
- If tolerance assertions fail, widen by one ULP at a time (do not blindly add `rtol=1e-5`); document the specific function that drifted.
- Do NOT widen tolerances in the same commit that adds new bindings — it hides the regression source.

**Warning signs:**
- `pytest` shows failures in `test_basic.py` or `test_r_parity.py` immediately after `cargo build` with the new crate version, before any new code was written.
- The failure involves an existing function (not one of the three new groups).

**Phase to address:**
Crate bump phase (Phase 1). This phase has one and only one success criterion: the existing 426-test suite passes unchanged.

---

### Pitfall 13: `constant_basis` Output Is `Vec<f64>` of Ones — Python Shape Should Be `(m, 1)` for Concatenation

**What goes wrong:**
`constant_basis(t: &[f64]) -> Vec<f64>` returns a flat `Vec<f64>` of length `m` (all ones). All other basis functions (`bspline_basis`, `fourier_basis`) return `(m, nbasis)` 2-D arrays. If the wrapper returns a 1-D numpy array of shape `(m,)`, users cannot horizontally stack it with `bspline_basis` output without a reshape. If the wrapper uses `fdmatrix_to_numpy2d` on the flat vec (wrong: it expects an FdMatrix, not a plain Vec), the call panics.

**Why it happens:**
The natural API for a single-column intercept basis is a 1-D vector, but the usage context (basis concatenation) requires a 2-D column.

**How to avoid:**
- Return `(m, 1)` numpy array: `PyArray2::from_vec2(py, &v.iter().map(|&x| vec![x]).collect::<Vec<_>>()).unwrap()`.
- Write a test: `np.hstack([fdars.basis.constant_basis(av).reshape(-1,1), fdars.basis.bspline_basis(av, nknots=3)])` produces shape `(m, 4)`.
- Alternatively, document explicitly that the returned `(m,)` array must be reshaped by the caller — but the `(m, 1)` default is safer.

**Warning signs:**
- User reports `ValueError: all input arrays must have the same number of dimensions` when concatenating `constant_basis` with `bspline_basis` output.
- The wrapper uses `fdmatrix_to_numpy2d` on a plain Vec (panics).

**Phase to address:**
Group C bindings phase (basis/smoothing).

---

### Pitfall 14: AIC Smoother Is in `fdars_core::smoothing`, Not `fdars_core::basis` — Wrong Module Placement

**What goes wrong:**
The existing `basis_nbasis_cv` binding already handles `criterion="aic"` via `BasisCriterion::Aic` (not `#[non_exhaustive]`). The new `aic_smoother` in `fdars_core::smoothing` is a separate function returning a scalar AIC score for a kernel smoother — a different concept. Binding `aic_smoother` in `basis_mod.rs` instead of `smoothing_mod.rs` causes a path lookup failure (`fdars_core::basis::aic_smoother` does not exist). `smooth_basis_aic` is mentioned in the milestone context but does not appear in the `smoothing` module index on docs.rs 0.20.0 — its existence must be verified before the plan is written.

**Why it happens:**
The name collision ("aic" appears in both `BasisCriterion` and `smoothing::CvCriterion`) creates a mental model where AIC is "already handled." `smoothing::CvCriterion::Aic` (new in 0.20) is a separate enum variant from `smooth_basis::BasisCriterion::Aic` (which already existed and is not `#[non_exhaustive]`).

**How to avoid:**
- `aic_smoother` goes in `smoothing_mod.rs` — it is a kernel smoother score function parallel to `cv_smoother` and `gcv_smoother` (confirmed from docs.rs: `pub fn aic_smoother(x: &[f64], y: &[f64], bandwidth: f64, kernel: &str) -> f64`).
- `CvCriterion::Aic` expands the accepted string values in the `optim_bandwidth` binding in `smoothing_mod.rs` (fix the non-exhaustive match in Phase 1).
- `smooth_basis_aic` — verify its existence and exact module path against docs.rs 0.20.0 before the plan is written. Do not bind a function that does not exist.

**Warning signs:**
- `fdars_core::basis::aic_smoother` path lookup failure at compile time.
- A plan task references `smooth_basis_aic` without a verified docs.rs link.

**Phase to address:**
Group C bindings phase. Verify exact module path for each new function against docs.rs 0.20.0 before the plan is written.

---

### Pitfall 15: SCB Band `nb` and `confidence` Parameters — Undocumented Defaults and Validation Gaps

**What goes wrong:**
`mean_scb(data, argvals, bandwidth, nb, confidence, multiplier)` — all parameters required in Rust. If the Python wrapper exposes them all as required positional arguments, the function is unusable without reading the paper. Using `nb=1000` in a docs fence would add ~5 seconds to the build (Pitfall 5). The `multiplier` parameter requires string-to-enum conversion for `MultiplierDistribution` (Pitfall 2, which is `#[non_exhaustive]`). If `confidence` is passed outside (0, 1), the Rust function may panic or return a nonsensical band without a clear Python error.

**How to avoid:**
- Wrapper: `#[pyo3(signature = (data, argvals, bandwidth, nb=200, confidence=0.95, multiplier="gaussian"))]`.
- Validation guard: if `confidence <= 0.0 || confidence >= 1.0`, return `PyValueError`.
- Validation guard: if `nb == 0`, return `PyValueError`.
- Docs fences: `nb=50` to bound build time.
- Write an input-validation test: `mean_scb(..., nb=0, confidence=0.95)` → `ValueError`.

**Warning signs:**
- The function is exposed with all parameters positional-only, making it a 6-argument required call.
- `nb=1000` appears in any executed docs fence.

**Phase to address:**
Group A bindings phase. Input-validation tests and default-parameter design must be in the binding plan.

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Add `inference` to `_DIAGNOSTICS_METHODS` in a follow-up commit | Cleaner git log | Guard-sync test fails in CI between commits | Never — must be atomic |
| Use `np.float64` in diagnostics dict without `float()` cast | One less line per key | `json.dumps` TypeError; grounding check misses values | Never |
| Default `n_perm=999` in docs fences | Credible p-values in examples | Docs build time doubles or triples | Never in executed fences; acceptable in illustrative (non-executed) code blocks |
| Skip multi-curve transposition round-trip test for SCB bands | Faster PR | Silent row/column swap bug on band arrays | Never |
| Expose `flm_f_test` accepting a Python dict of fit fields | Simpler API surface | Does not compile (cannot reconstruct `#[non_exhaustive]` struct from outside crate) | Never |
| Omit wildcard arm on `DepthMethod`, `CvCriterion`, or `MultiplierDistribution` match | Shorter code | Compile failure on bump (blocking CI) | Never |
| Bind `aic_smoother` in `basis_mod.rs` | Seems thematically close | Compile error — wrong module path | Never |

---

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| `functional_depth` dispatcher + existing per-method depth fns | Expose `functional_depth` and assume it replaces `fraiman_muniz_1d` etc. | Keep both; `functional_depth` is a convenience dispatcher; per-method fns remain for fine-grained control |
| FLM inference via `flm_f_test` | Pass Python dict from `fregre_lm` to `flm_f_test` | Re-run `fregre_lm` inside the Rust wrapper and pass the Rust struct directly |
| MCP `fdars_run_method` + inference | Add `"inference"` to `_RUNNABLE_METHODS` | Inference tests require two datasets; keep inference diagnostics-only, not in `_RUNNABLE_METHODS` |
| `mean_scb` result + advisor grounding | Treat `ToleranceBand` as a matrix (n×m) | Return as two 1-D arrays (`lower`, `upper`) of shape (m,); document as pointwise mean bounds |
| `CvCriterion` back-conversion in `optim_bandwidth` result dict | Stringify via exhaustive match | Add `_ => "unknown"` wildcard arm to avoid compile failure on `#[non_exhaustive]` |
| `FregreLmResult` module path | Import from `fdars_core::regression` | Correct path is `fdars_core::scalar_on_function::FregreLmResult` |

---

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| `n_perm=999` in executed docs fence | `mkdocs build` takes 30+ min; CI timeout | `n_perm=19` in all executed fences | Any fence with permutation test |
| `nb=1000` bootstrap replicates in SCB fence | Same as above | `nb=50` in fences | Any SCB fence |
| `functional_boxplot` on the full Canadian Weather dataset (35×365) | Each docs build adds ~2s per fence | Use 20 curves × 20 grid points synthetic data | Always when data is large |
| Calling `optim_bandwidth` inside `mean_scb` in a fence to auto-select bandwidth | Adds 0.5–2s per call | Hard-code a bandwidth value in fences | Any executed fence |

---

## "Looks Done But Isn't" Checklist

- [ ] **`CvCriterion` match in `optim_bandwidth`:** Has `_ => return Err(PyValueError...)` wildcard — verify both string-to-enum and enum-to-string directions.
- [ ] **`DepthMethod` match in `functional_depth` and `functional_boxplot`:** Has `_ => return Err(PyValueError...)` wildcard.
- [ ] **`MultiplierDistribution` match in `mean_scb`:** Has `_ => return Err(PyValueError...)` wildcard.
- [ ] **`TestResult` PyDict:** All three fields mapped — `statistic` (float), `p_value` (float), `n_perm` (int).
- [ ] **`FunctionalBoxplotResult` PyDict:** All seven fields mapped — `outliers` converted via `usize_vec_to_numpy1d` (not `vec_to_numpy1d`).
- [ ] **Inference diagnostics aspect:** `float()` cast on every numeric value before insertion into the diagnostics dict.
- [ ] **Guard-sync atomic commit:** `_supported` in `build_diagnostics` and `_DIAGNOSTICS_METHODS` in `mcp/server.py` updated in a single commit; `test_diagnostics_methods_match_advisor_supported` passes.
- [ ] **Seed determinism test:** Two calls to `t_perm_test`/`f_perm_test`/`functional_depth(method="random_projection")` with identical seed return byte-identical `json.dumps` output.
- [ ] **`constant_basis` shape:** Returns `(m, 1)` numpy array, compatible with `np.hstack` concatenation with `(m, nbasis)` basis matrices.
- [ ] **`aic_smoother` module:** In `smoothing_mod.rs`, not `basis_mod.rs`.
- [ ] **Inference aspect NOT in `_RUNNABLE_METHODS`:** Two-dataset inference tests cannot be dispatched by `fdars_run_method`; they are diagnostics-only.
- [ ] **FLM wrapper strategy:** `flm_f_test` and `flm_gof_test` re-run `fregre_lm` internally (via `fdars_core::scalar_on_function::fregre_lm`) and return enriched dicts.
- [ ] **`mean_scb` return shape:** `lower.shape == (m,)` and `upper.shape == (m,)` — not `(1, m)` or `(n, m)`.

---

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Compile failure from missing `#[non_exhaustive]` wildcard arm | LOW | Add wildcard arm; `cargo build` passes immediately |
| Guard-sync drift caught by CI | LOW | Add missing aspect to `_DIAGNOSTICS_METHODS` in same commit that updates `_supported` |
| NumPy scalar leak in diagnostics | LOW | Wrap each value in `float()`; re-run determinism test |
| Docs build timeout from high `n_perm` | LOW | Reduce `n_perm` to 19 in executed fences; rebuild |
| `FregreLmResult` reconstruction fails at compile time | MEDIUM | Redesign wrapper to re-run `fregre_lm` and pass Rust struct directly |
| Transposition bug in SCB band output | MEDIUM | Add shape assertion test; fix return to use `vec_to_numpy1d` for each field |
| Regression drift in existing 426 tests after bump | MEDIUM | Identify drifted function; widen tolerance by one ULP; document in commit |
| `aic_smoother` in wrong module | LOW | Move to `smoothing_mod.rs`; update `register()` call |

---

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| Numeric drift on existing suite (Pitfall 12) | Phase 1: crate bump + regression gate | `pytest` shows 426+ passed / 0 failed before any new bindings |
| `#[non_exhaustive]` wildcard on `CvCriterion` in existing `optim_bandwidth` (Pitfall 2) | Phase 1: crate bump | `cargo build` passes with no exhaustiveness errors |
| `seed: u64` vs `Option<u64>` for permutation tests (Pitfall 1) | Phase 2: Group A inference bindings | Determinism test: two calls with same seed → byte-identical output |
| FLM wrapper strategy — re-run vs. dict reconstruction (Pitfall 4) | Phase 2: Group A inference bindings | Compile succeeds; `flm_f_test` returns valid dict from Python |
| `mean_scb` returns `ToleranceBand` not `TestResult` (Pitfall 6) | Phase 2: Group A inference bindings | Shape assertion: `lower.shape == (m,)` |
| `oneway_anova_vstat` groups parameter type (Pitfall 9) | Phase 2: Group A inference bindings | Test with int64 array input; verify group assignment is correct |
| SCB `nb`/`confidence` validation (Pitfall 15) | Phase 2: Group A inference bindings | `pytest.raises(ValueError)` on `nb=0` and `confidence=1.1` |
| `DepthMethod` enum variants and wildcard arm (Pitfall 7) | Phase 3: Group B depth/boxplot bindings | Exhaustive method-string test; self-depth consistency test |
| `functional_boxplot` factor default and `outliers` type (Pitfall 8) | Phase 3: Group B depth/boxplot bindings | `outliers` dtype is int64; factor=1.5 matches reference results |
| `TestResult` / `FunctionalBoxplotResult` non-exhaustive struct field access (Pitfall 3) | Phase 2+3: Group A+B bindings | All expected dict keys present in Python result |
| `constant_basis` shape — 1-D vs 2-D (Pitfall 13) | Phase 4: Group C basis/smoothing bindings | `np.hstack([constant_basis(av).reshape(-1,1), bspline_basis(av, nknots=3)])` succeeds |
| `aic_smoother` module placement (Pitfall 14) | Phase 4: Group C basis/smoothing bindings | `from fdars.smoothing import aic_smoother` succeeds |
| `MultiplierDistribution` wildcard arm in `mean_scb` (Pitfall 2 extension) | Phase 2: Group A inference bindings | `cargo build` passes; `pytest.raises(ValueError)` on unknown multiplier string |
| Grounding-invariant numpy scalar leak (Pitfall 11) | Phase 5: advisor extension | `json.dumps(diag)` does not raise; no `isinstance(val, np.generic)` in leaf values |
| Guard-sync atomic commit (Pitfall 10) | Phase 5: advisor extension | `test_diagnostics_methods_match_advisor_supported` passes on the commit |
| Executed-fence `n_perm` cost (Pitfall 5) | Phase 6: docs | No executed fence has `n_perm >= 100`; docs build delta < 3 min vs pre-inference baseline |

---

## Sources

- `docs.rs/fdars-core/0.20.0` — verified signatures for `t_perm_test`, `f_perm_test`, `two_sample_mean_test`, `mean_scb`, `scb_two_sample_test`, `flm_f_test`, `flm_gof_test`, `oneway_anova_vstat`, `functional_depth`, `functional_boxplot`, `aic_smoother`, `constant_basis` (HIGH confidence — official crate docs)
- `docs.rs/fdars-core/0.20.0` — verified `#[non_exhaustive]` on `DepthMethod` (variants: `FraimanMuniz { scale }`, `Band`, `ModifiedBand`, `RandomProjection { nproj, seed }`), `CvCriterion` (variants: `Cv`, `Gcv`, `Aic`), `MultiplierDistribution` (variants: `Gaussian`, `Rademacher`), `TestResult` (fields: `statistic f64`, `p_value f64`, `n_perm usize`), `FunctionalBoxplotResult` (fields: `median`, `central_lower`, `central_upper`, `whisker_lower`, `whisker_upper`, `outliers Vec<usize>`, `depths`), `FregreLmResult` (in `scalar_on_function` module)
- `BasisCriterion` confirmed NOT `#[non_exhaustive]` (variants: `Gcv`, `Cv`, `Aic`, `Bic`)
- `src/depth_mod.rs`, `src/basis_mod.rs`, `src/smoothing_mod.rs`, `src/convert.rs`, `src/regression_mod.rs` — existing binding patterns (read directly from codebase, HIGH confidence)
- `python/fdars/mcp/server.py` — `_DIAGNOSTICS_METHODS` frozenset and guard-sync pattern
- `python/fdars/advisor/__init__.py` — `_supported` set and `build_diagnostics` dispatch pattern
- `tests/test_mcp_server.py:503` — `test_diagnostics_methods_match_advisor_supported` guard-sync test
- `tests/test_advisor_registration_quality.py` — numpy-scalar leak pattern and `json.dumps` determinism pattern
- `.planning/RETROSPECTIVE.md` — v4.0 lessons: isolated bump phase, 18-min docs build cost, atomic guard-sync commit requirement

---
*Pitfalls research for: pyfda v5.0 — fdars-core 0.20 upgrade (functional inference + depth/boxplot + AIC-smoothing)*
*Researched: 2026-08-17*
