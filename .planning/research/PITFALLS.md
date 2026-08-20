# Pitfalls Research

**Domain:** PyO3 binding layer upgrade — fdars-core 0.20 → 0.23 (Regression, PACE-FPCA, Depth/Outliers/Interval Inference)
**Researched:** 2026-08-20
**Confidence:** HIGH (all pitfalls derived from v0.23.0 source inspection, prior-milestone code-review fix reports, and pyfda's established patterns)

---

## Critical Pitfalls

### Pitfall 1: `ConcurrentRegrResult.beta_curve` transposition — predictor axis vs. curve axis

**What goes wrong:**
`beta_curve` in `ConcurrentRegrResult` has FdMatrix shape `(p, m)` — `nrows=p` (predictor count), `ncols=m` (grid points). When converted through `fdmatrix_to_numpy2d`, the Python caller receives shape `(p, m)` — correct. However if a binding author confuses this with the standard `(n_obs, m)` convention and transposes it (as happened with multi-curve returns in v4.0 Phases 26 and 27), Python receives shape `(m, p)` and the β(t) curves are indexed on the wrong axis. `fitted` and `residuals` are `(n, m)` — the usual convention — making the mismatch non-obvious when `p == n`.

**Why it happens:**
`beta_curve` breaks pyfda's dominant `(n_obs, m)` convention. Almost every other FdMatrix is `(n_obs, n_points)`. `beta_curve` has `nrows = p` (number of predictors, typically 1–5), not `nrows = n`. Under time pressure the binding author applies `fdmatrix_to_numpy2d` assuming `nrows=n_obs` and documents Python shape as `(n_obs, m)`, which is subtly wrong.

**How to avoid:**
In the binding comment for `beta_curve`, write explicitly: `# shape (p, m): p predictors × m grid points, NOT (n_obs, m)`. Write a multi-predictor transposition test (`p >= 2`) asserting `result["beta_curve"].shape == (p, m)` and checking each row is a smooth curve over the grid. This is the standard multi-curve transposition guard pattern from v4.0.

**Warning signs:**
Tests that only exercise `p == 1` will not catch this — `(1, m)` is indistinguishable from `(n_obs, m)` when `n_obs == 1`. Always write a `p >= 2` test.

**Phase to address:** Bindings — Group A (Regression).

---

### Pitfall 2: `pace_fpca` requires `IrregFdata`, not a 2-D numpy array — new container type with no Python binding yet

**What goes wrong:**
`pace_fpca` accepts `&IrregFdata` (a CSR-like struct: offset vector + flat argvals/values arrays), not an `FdMatrix`. There is no existing `PyClass` for `IrregFdata` in pyfda. If the binding exposes `pace_fpca(data: np.ndarray, ...)` with a regular array shim, it silently reconstructs a fake regular grid and the sparse-FPCA computation is meaningless.

**Why it happens:**
`IrregFdata` has never been exposed to Python (it lives in `fdars_core::irreg_fdata` and has only been used internally). The binding author may improvise a regular-array shim that pads or zeroes missing observations, which destroys PACE semantics.

**How to avoid:**
Create a builder function `irreg_fdata_from_lists(argvals_list: list[list[float]], values_list: list[list[float]])` returning an opaque handle (or a `PyIrregFdata` pyclass wrapper), and require it as the sole input type for `pace_fpca`. Accept Python lists-of-arrays and construct `IrregFdata::from_lists` inside the binding. Document: each sublist is one curve's (argvals, values); curves need not share observation times; each curve must have at least 2 points (core enforces this with `FdarError::InvalidDimension`).

**Warning signs:**
Any `pace_fpca` binding signature accepting a single 2-D numpy array is wrong. The test dataset must use curves with different lengths — a regular matrix cannot test the PACE path.

**Phase to address:** Bindings — Group B (FPCA & Classification). Must be resolved at plan-time before coding.

---

### Pitfall 3: `PaceFpcaResult.eigenfunctions` is `(m, ncomp)` in FdMatrix — transpose differs from `FpcaResult.scores` convention

**What goes wrong:**
`PaceFpcaResult.eigenfunctions` has FdMatrix shape `(m, ncomp)` (rows = grid points, columns = components). `fdmatrix_to_numpy2d` produces `(m, ncomp)` in Python — correct. If the binding author inverts this to follow a "components are rows" model, Python receives `(ncomp, m)` and eigenfunction plots are transposed. In addition, `scores` is `(n, ncomp)` (consistent with existing FPC convention). A binding author who incorrectly transposes `eigenfunctions` may also transpose `scores` to be "symmetric," compounding the error.

**Why it happens:**
`eigenfunctions[(j, k)]` is accessed as `(grid_point, component)` in Rust — the mathematical convention (columns = eigenvectors). This conflicts with the intuitive "rows are things" Python reading where each row might be expected to be one eigenfunction.

**How to avoid:**
Document Python shape explicitly in the binding: `eigenfunctions: np.ndarray, shape (m, ncomp) — each column is one eigenfunction`. Write a test asserting `result["eigenfunctions"].shape == (m, ncomp)` and column orthonormality: `np.allclose(ef.T @ ef, np.eye(ncomp), atol=0.1)`. Access the k-th eigenfunction as `ef[:, k]`, not `ef[k, :]`.

**Warning signs:**
A sign-convention test that uses `pearson_corr(ef[0, :], true_phi1)` (row access) rather than `pearson_corr(ef[:, 0], true_phi1)` (column access) is wrong and will silently pass on transposed output.

**Phase to address:** Bindings — Group B (FPCA & Classification).

---

### Pitfall 4: `PaceFpcaResult.ncomp` may be less than requested — binding must not hardcode the requested component count

**What goes wrong:**
`pace_fpca` returns `actual_ncomp` which may be less than `config.ncomp` when the smoothed covariance surface yields fewer positive eigenvalues (a documented finite-sample artifact). If the binding preallocates a `(n, config.ncomp)` numpy array or extracts `scores[:, :config.ncomp]`, it will index out of bounds or silently zero-pad when `actual_ncomp < config.ncomp`.

**Why it happens:**
Callers naturally assume "I asked for 3 components, I get 3." The divergence is only documented in `PaceFpcaResult`'s struct docstring ("ncomp in the result may be less than the requested config.ncomp"). Small datasets (typical for docs worked examples) hit this frequently.

**How to avoid:**
Always read `result.ncomp` (the actual count), not the input `config.ncomp`. Assert in tests: `assert result["ncomp"] <= config_ncomp`. Use `result.ncomp` for all matrix dimension extractions. Write a test where the synthetic dataset is small enough to produce `actual_ncomp < 3` when `config.ncomp == 3`.

**Warning signs:**
Tests with large, dense synthetic data will never exercise `actual_ncomp < requested`. Always include a small-dataset test where the covariance surface is degenerate.

**Phase to address:** Bindings — Group B (FPCA & Classification).

---

### Pitfall 5: `elastic_multinomial` requires contiguous 0-indexed labels — negative-label guard from v5.0 CR-01 must be applied here too

**What goes wrong:**
`elastic_multinomial` enforces labels forming the contiguous range `0..K` (validated in core with `FdarError::InvalidParameter`). The binding accepts `y: &[usize]` from a Python `i64` numpy array. If the conversion uses `numpy1d_to_usize_vec` directly (which casts `i64 → usize` without sign checking), negative labels wrap to `usize::MAX` — the same bug fixed in v5.0 Phase 31 for `oneway_anova_vstat` (CR-01 fix). Additionally, users passing `[1, 2, 3]` (1-indexed) or `[0, 2, 4]` (gap) get a cryptic Rust error rather than a clear Python `ValueError`.

**Why it happens:**
The v5.0 CR-01 fix was applied to `inference_mod.rs` (for `oneway_anova_vstat`). It was NOT applied to `classification_mod.rs` because `elastic_multinomial` is new in 0.23. The same unchecked `numpy1d_to_usize_vec` path will reintroduce the bug.

**How to avoid:**
In the `elastic_multinomial` binding: (1) iterate the raw `i64` array and raise `PyValueError` if any value is `< 0` (mirrors CR-01); (2) validate that the `usize` values form `0..K`; (3) emit a helpful message: "labels must be contiguous 0-indexed integers (0..K); remap before calling." Add `pytest.raises(ValueError)` tests for negative labels (`[-1, 0, 1]`) and non-contiguous labels (`[0, 2]`).

**Warning signs:**
Any classification test that only uses labels `{0, 1, 2}` will not catch the `usize::MAX` wrapping. Explicitly test the negative-label path.

**Phase to address:** Bindings — Group B (FPCA & Classification). Same fix class as v5.0 CR-01.

---

### Pitfall 6: `DepthMethod` is `#[non_exhaustive]` with 9 new variants in 0.23 — Python string dispatcher must be extended

**What goes wrong:**
The existing `functional_depth` binding dispatches a Python string to `DepthMethod` variants. In v5.0 the binding was written for 4 variants (FraimanMuniz, Band, ModifiedBand, RandomProjection). The 0.23 `DepthMethod` enum adds 9 more: HypographIndex, ModifiedHypographIndex, EpigraphIndex, HalfRegion, ModifiedHalfRegion, Extremal, ExtremeRankLength, LInfinity, TotalVariation. If the Python-side string-to-variant map is not extended, any call to `functional_depth(data, method="half_region")` returns a confusing `ValueError("unknown depth method")`.

**Why it happens:**
The `#[non_exhaustive]` attribute on the Rust enum requires a wildcard `_ =>` arm in Rust match expressions — but the Python-side dispatcher is an `if/else if` chain or dict that is not protected by the Rust compiler. Omitting new variant strings from the Python chain silently falls through to the error branch.

**How to avoid:**
Add all 9 new variant strings to the Python-side dispatcher: `"hypograph_index"` → `DepthMethod::HypographIndex`, `"modified_hypograph_index"` → `DepthMethod::ModifiedHypographIndex`, `"epigraph_index"` → `DepthMethod::EpigraphIndex`, `"half_region"` → `DepthMethod::HalfRegion`, `"modified_half_region"` → `DepthMethod::ModifiedHalfRegion`, `"extremal"` → `DepthMethod::Extremal`, `"extreme_rank_length"` → `DepthMethod::ExtremeRankLength`, `"l_infinity"` → `DepthMethod::LInfinity`, `"total_variation"` → `DepthMethod::TotalVariation`. The Rust wildcard arm must raise `PyValueError("unknown depth method: {}; supported: [...]")`. Add a smoke test for each new variant.

**Warning signs:**
`cargo build` succeeds but `pytest` shows `ValueError: unknown depth method: half_region` for any new variant. The `#[non_exhaustive]` guard only fires for Rust pattern exhaustiveness — it does not catch missing Python string mappings.

**Phase to address:** Bindings — Group C (Depth/Outliers/Interval Inference).

---

### Pitfall 7: `SeqTransform` is `#[non_exhaustive]` and has 5 variants including a surprising `D2` ("identical to D1") — Python sequence encoding must cover all 5

**What goes wrong:**
`sequential_transform_outliers` takes a `&[SeqTransform]` slice. The binding accepts a Python list of strings and maps them to variants. The enum has 5 variants: T0, T1, T2, D1, D2 — where D2 is documented as "Identical to D1; included for R parity." Missing D2 or mishandling the default lowercase mapping will silently drop transforms from the sequence. The `#[non_exhaustive]` attribute requires a Rust wildcard arm; without it, the binding fails to compile.

**How to avoid:**
Accept lowercase strings from Python: `"t0"`, `"t1"`, `"t2"`, `"d1"`, `"d2"`. Map case-insensitively. In the Rust wildcard arm: `_ => return Err(PyValueError::new_err(format!("unknown transform: {v}; supported: t0, t1, t2, d1, d2")))`. Test all 5 variants individually. Document D2 in the Python docstring: "D2 applies the same lag-1 difference as D1; included for parity with R `fdaoutlier`."

**Warning signs:**
Tests that only use `["T1", "D1"]` (the common R defaults) will not catch broken T0/T2/D2. Write an explicit test for each variant.

**Phase to address:** Bindings — Group C (Depth/Outliers/Interval Inference).

---

### Pitfall 8: `GlmFamily` is `#[non_exhaustive]` and `Gamma` uses inverse canonical link — docstring accuracy risk

**What goes wrong:**
`functional_glm` takes `family: GlmFamily`. Two problems:

1. The enum is `#[non_exhaustive]`: the Rust `match` in the binding must have a wildcard arm (`_ => return Err(PyValueError::new_err(...))`), or compilation fails when a new family is added upstream.
2. `GlmFamily::Gamma` uses the **inverse canonical link** (`g(μ) = 1/μ`), NOT the log link that Python's `statsmodels` and R's `glm()` default to. The core docstring explicitly flags this: "Gamma uses inverse link (g(μ)=1/μ), NOT log-link." If the Python binding docstring says "Gamma uses log link" or omits this, users will misinterpret β(t) coefficients.

**How to avoid:**
Include the wildcard arm: `_ => return Err(PyValueError::new_err(format!("unknown family: {f}; supported: binomial, poisson, gamma, gaussian")))`. In the Python docstring, include a link-function table matching the core's table. Add a note: "Gamma uses the inverse canonical link g(μ)=1/μ — the coefficient β(t) represents the effect on 1/E[Y], not log(E[Y])." Write a test asserting `result["iterations"] == 1` for Gaussian family (the single-IRLS-step invariant is documented in the core).

**Warning signs:**
A docs worked example for `functional_glm(family="gamma")` that interprets β(t) as a log-rate effect — this is wrong and misleads users.

**Phase to address:** Bindings — Group A (Regression) for the enum guard; Docs phase for the link-function clarification.

---

### Pitfall 9: ITP functions take `seed: u64` — must default to 0 for offline determinism, not a random value

**What goes wrong:**
`itp_one_pop`, `itp_two_pop`, and `itp_flm` all take `seed: u64`. If the Python binding resolves `seed=None` to `time.time_ns()` (or any non-deterministic value), ITP results are non-reproducible across calls. This violates the advisor grounding invariant (two `build_diagnostics` calls on the same data must return byte-identical JSON) and breaks offline `FDARS_FENCE_OK` docs fences.

**Why it happens:**
v5.0 Phase 31 established: `seed=None` resolves to fixed default `0`. But the ITP entry points are new in this milestone — the pattern may not be carried forward from the existing inference binding if the binding author treats them as separate from the existing permutation tests.

**How to avoid:**
Mirror the v5.0 pattern exactly: `seed: u64 = 0` in the `#[pyo3(signature = (...))]` decorator. Docstring: "seed=0 is the fixed offline default; pass a different value only for sensitivity analysis." Add a determinism test: call `itp_one_pop` twice with identical args and assert `result1["adjusted_pvalues"] == result2["adjusted_pvalues"]` elementwise. Add a `json.dumps(result, sort_keys=True)` equality test (matching the WR-02 pattern from v5.0 Phase 31).

**Warning signs:**
Any ITP test that only asserts `0 <= p_value <= 1.0` without asserting exact value equality across calls does not catch non-determinism.

**Phase to address:** Bindings — Group C (Depth/Outliers/Interval Inference).

---

### Pitfall 10: `ItpResult.n_basis` may differ from the requested `nbasis` — always read from result dict, not from the argument

**What goes wrong:**
`ItpResult` carries `n_basis` (actual basis functions used after B-spline knot clamping) which may be less than the `nbasis` argument. `adjusted_pvalues` and `raw_pvalues` have length `n_basis`, not `nbasis`. If the binding preallocates a numpy array of length `nbasis` and writes `result.adjusted_pvalues` into it, the lengths may mismatch and trailing slots are zeroed or garbage. `ItpResult` is `#[non_exhaustive]` — struct-literal test helpers cannot construct it; all tests go through a real call.

**How to avoid:**
Convert `adjusted_pvalues` and `raw_pvalues` directly via `vec_to_numpy1d` (vector length determines array size). Always include `n_basis` and `n_perm` in the PyDict. Write a test asserting `len(result["adjusted_pvalues"]) == result["n_basis"]` (not `== nbasis`) with a B-spline call where knot clamping is likely.

**Warning signs:**
Tests using only Fourier basis (where `n_basis == nbasis` always) will not catch B-spline knot clamping. Include at least one B-spline test.

**Phase to address:** Bindings — Group C (Depth/Outliers/Interval Inference).

---

### Pitfall 11: All four new outlier detectors return outlier indices as `Vec<usize>`, not `Vec<bool>` — wrong converter reuse

**What goes wrong:**
`TvdMssOutliers`, `MuodResult`, `SeqTransformOutliers`, and `DepthgramResult` return outlier sets as `Vec<usize>` (sorted row indices), not `Vec<bool>`. The existing `detect_outliers_lrt` binding returns a `Vec<bool>`. If a binding author copies the `bool_vec_to_numpy1d` converter from the existing outlier binding, the index vectors are silently mistyped. `MuodResult` has three outlier index vectors (`shape_outliers`, `magnitude_outliers`, `amplitude_outliers`) plus three continuous score arrays — all six must appear in the PyDict.

**How to avoid:**
Use `usize_vec_to_numpy1d` (not `bool_vec_to_numpy1d`) for all `*_outliers` fields in the new detector results. In tests, assert `result["shape_outliers"].dtype == np.int64` and each element is a valid row index `< n`. Include all continuous score arrays in the PyDict (e.g., `MuodResult.shape_index`, `magnitude_index`, `amplitude_index`).

**Warning signs:**
A test that only asserts `len(result["shape_outliers"]) >= 0` does not catch a dtype error. Assert dtype and bounds.

**Phase to address:** Bindings — Group C (Depth/Outliers/Interval Inference).

---

### Pitfall 12: `outliers_threshold_lrt` / `outliers_threshold_lrt_with_dist` take `seed: u64` — audit existing binding for omission

**What goes wrong:**
Both bootstrap-based functions take `seed: u64`. If the existing `outliers_mod.rs` binding (from pre-0.23 work) exposed these without a `seed` parameter (resolving to 0 internally without telling the user), extending them for the new detector bootstrap paths will produce non-deterministic results when users change the seed expectation.

**How to avoid:**
Before writing any new outlier bindings, audit `src/outliers_mod.rs` to confirm whether `seed` is already exposed. If not, add `seed: u64 = 0` with a fixed default and a determinism test. This audit belongs at the start of the Group C bindings plan.

**Phase to address:** Bindings — Group C (Depth/Outliers/Interval Inference) — audit first, extend second.

---

### Pitfall 13: `ConcurrentRegrResult` and `FunctionalGlmResult` are `#[non_exhaustive]` — no struct-literal construction in tests

**What goes wrong:**
Both result types carry `#[non_exhaustive]`. Rust code outside the crate cannot construct them with struct-literal syntax. If any test helper tries to construct a mock result to test PyDict conversion in isolation, it will fail to compile with "cannot create non-exhaustive struct with struct expression."

**How to avoid:**
All pyfda result tests go through a real call path (call → inspect PyDict). Never construct `ConcurrentRegrResult` or `FunctionalGlmResult` literals in test code. This is already the project convention; document it for these new types.

**Warning signs:**
Compiler error: "cannot create non-exhaustive struct with struct expression." Caught at compile time, not runtime — but can waste debugging time if attempted.

**Phase to address:** Bindings — Group A (Regression). Caught at compile time.

---

## Advisor Pitfalls

### Pitfall 14: ITP `adjusted_pvalues` aggregated as numpy scalar in advisor diagnostics — grounding invariant broken

**What goes wrong:**
ITP results carry `adjusted_pvalues` and `raw_pvalues` as numpy arrays (length = n_basis). Extending `_build_inference_diagnostics` naively by writing `diag["min_adjusted_pval"] = result["adjusted_pvalues"].min()` produces a `np.float64` scalar — not a Python `float`. The grounding guard (`json.dumps` roundtrip) fails because `numpy.float64` is not JSON-serialisable. This is the same numpy-scalar class that WR-02 (v5.0 Phase 31) guarded against for `TestResult` scalars.

**Why it happens:**
The existing `_resolve_float` helper in `inference.py` handles the `TestResult` scalar case. ITP results require aggregating a vector — the natural idiom is `.min()` / `.mean()` which return numpy scalars. Adding a new code path that bypasses `_resolve_float` reintroduces the bug.

**How to avoid:**
Always wrap numpy-array aggregates with `float(...)`: `diag["min_adjusted_pval"] = float(result["adjusted_pvalues"].min())`. For means, use a plain-Python loop: `vals = [float(v) for v in result["adjusted_pvalues"]]; diag["mean_adjusted_pval"] = float(sum(vals) / len(vals)) if vals else None`. Add a `json.dumps(build_diagnostics(result, method="itp"), sort_keys=True)` assertion to the ITP advisor test.

**Warning signs:**
`json.dumps(diagnostics)` raises `TypeError: Object of type float64 is not JSON serialisable`.

**Phase to address:** Advisor extension phase.

---

### Pitfall 15: New outlier detector diagnostics must store scalar counts, not raw index lists

**What goes wrong:**
`TvdMssOutliers`, `MuodResult`, and `DepthgramResult` return multiple `Vec<usize>` outlier index sets. If the new `_build_outliers_diagnostics` extension stores raw index lists (`"shape_outliers": [2, 7, 14]`) in the diagnostics dict, the LLM cannot cite a single grounded number — it would have to fabricate a summary. The grounding invariant requires a fdars-computed scalar that the LLM cites directly.

**How to avoid:**
For each outlier set, store scalar counts: `diag["n_shape_outliers"] = len(result.get("shape_outliers", []))`, `diag["shape_outlier_fraction"] = float(len(...)) / float(n_obs)`. The LLM can then cite "3 shape outliers detected (15% of sample)." Also store the scalar range of continuous score arrays (min/max of `shape_index`, `magnitude_index`, `amplitude_index`) as plain `float` values for grounded interpretation.

**Warning signs:**
Advisor output that says "several outliers were detected" without citing a specific count is a fabrication. The grounding guard should catch this if the test prompt requires evidence citation.

**Phase to address:** Advisor extension phase.

---

### Pitfall 16: MCP `_DIAGNOSTICS_METHODS` guard-sync — new aspects require a single atomic commit with the diagnostics builder

**What goes wrong:**
`python/fdars/mcp/server.py:_DIAGNOSTICS_METHODS` is a frozenset that must exactly match the set of aspects `build_diagnostics` supports. If a new aspect (e.g., `"itp"` for interval testing) is added to `build_diagnostics` without simultaneously updating `_DIAGNOSTICS_METHODS`, the MCP tool rejects valid calls with "unsupported method." The reverse — updating the guard before the builder exists — causes a `KeyError` at runtime.

**Why it happens:**
The single-atomic-commit discipline was established in v4.0 Phase 28 and reinforced in v5.0 Phase 34. Advisor work spanning multiple commits (builder in one, guard update in a follow-up) leaves CI broken between commits.

**How to avoid:**
Update `_DIAGNOSTICS_METHODS` and the aspect builder in the same commit. The existing guard-sync test (asserting the two sets are equal) must pass in CI. Never split these into two commits.

**Warning signs:**
Any commit touching `advisor/aspects/` without also touching `mcp/server.py:_DIAGNOSTICS_METHODS`, or vice versa.

**Phase to address:** Advisor extension phase.

---

## Docs Pitfalls

### Pitfall 17: Depth-fence diagram drawn as symmetric pointwise bands — method-accuracy trap

**What goes wrong:**
The functional boxplot / depth-fence concept diagram shows the central region and whisker envelopes. A common mistake is drawing symmetric bands (mean ± k·SD), which is both statistically wrong for the depth-fence method and visually misleading. The functional boxplot central region is the band swept by the deepest 50% of curves (by modified band depth ordering) — it is asymmetric and tracks actual data variation, not a confidence interval.

**How to avoid:**
Draw the central region as the band swept by the deepest 50% curves. Include at least one example curve that is clearly non-central (lower depth) and lies partially outside the central region. The `functional_boxplot` result provides the `central_region` matrix — use those values to set the diagram's band boundaries. Verify via `rsvg-convert` PNG before sign-off (the v4.0 retrospective established this as the method-accuracy gate).

**Warning signs:**
A diagram where the upper and lower whisker envelopes are symmetric about the center line over the full domain.

**Phase to address:** Docs phase.

---

### Pitfall 18: PACE FPCA concept diagram showing curves on a regular shared grid — misrepresents sparse/irregular FPCA

**What goes wrong:**
The PACE FPCA concept diagram must show that each curve is observed at different, sparse time points. If the diagram shows equally spaced observations or the same grid for all curves, it misrepresents PACE — the whole point of PACE is handling the sparse/irregular case. This will be caught at the per-section review gate, but fixing a diagram late is more expensive than getting it right.

**How to avoid:**
Draw each curve's observations as dots at distinct, staggered, irregular time positions (e.g., curve 1 has 3 dots at t=0.1, 0.4, 0.8; curve 2 has 5 dots at t=0.0, 0.2, 0.5, 0.7, 0.9). The fitted trajectory (from BLUP scores) is a smooth line on the work grid with pointwise confidence bands. Mark observed points as open circles or crosses, clearly separate from the smooth fitted line.

**Warning signs:**
Any PACE diagram where all curves have the same number of observations at the same x-positions.

**Phase to address:** Docs phase.

---

### Pitfall 19: ITP adjusted p-value diagram shows adjusted values below raw values — violates closure adjustment direction

**What goes wrong:**
The ITP closure adjustment makes `adjusted_pvalues[k]` the maximum over all contiguous intervals containing component `k` — so the adjusted p-value is always at least as large as the raw p-value. A diagram showing adjusted p-values below raw p-values is methodologically wrong. This is a method-accuracy error.

**Why it happens:**
"Closure" sounds like tightening (smaller p-values), but ITP closure conservatively inflates p-values to control the family-wise error rate. This is the opposite of what a non-specialist expects.

**How to avoid:**
In the ITP concept diagram, show both `raw_pvalues` (lower curve, less conservative) and `adjusted_pvalues` (upper curve, conservative) over the basis-component index. Label them clearly. Caption: "Adjusted p-values are at or above raw p-values — the interval-wise closure adjustment inflates, not deflates, significance thresholds."

**Warning signs:**
Any diagram where the adjusted_pvalues curve dips below the raw_pvalues curve at any basis component.

**Phase to address:** Docs phase.

---

### Pitfall 20: PACE and ITP executed fence datasets too large — ~19-minute docs build will grow to 30+ minutes

**What goes wrong:**
PACE FPCA runs a 6-step pipeline (covariance surface smoothing, Simpson-weighted eigendecomposition, per-curve Cholesky solves). ITP runs `n_perm` permutation sign-flips over `n_basis` components. Docs fences using real datasets (Canadian Weather n=35, Growth n=93) with default parameters will add 5–10 minutes per fence to the already ~19-minute build.

**How to avoid:**
PACE fences: n=10 synthetic curves with 3–5 points each, `ncomp=2`, `bandwidth=0.2`, 21-point work grid. ITP fences: n=20 synthetic curves, `nbasis=10`, `n_perm=199`. Assert `FDARS_FENCE_OK` sentinel at the end. Document the small-data choice in the fence comment. Never use Canadian Weather, Growth, or Tecator datasets for PACE/ITP executed fences.

**Warning signs:**
A fence that takes more than 30 seconds on a laptop CPU. Time the build locally before merging: `mkdocs build` must finish in under 25 minutes.

**Phase to address:** Docs phase.

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Expose `pace_fpca` with a plain 2-D numpy array instead of `IrregFdata` builder | No new Python type needed | Silently wrong PACE on regular data; cannot represent truly sparse curves | Never |
| Resolve ITP seed from `time.time_ns()` | No need to document default | Non-deterministic advisor diagnostics; broken docs fences | Never |
| Skip `json.dumps` determinism test for ITP/outlier advisor extensions | Faster to write tests | numpy-scalar leak undetected until CI fails on another Python version | Never |
| Use `nbasis` (input) instead of `result["n_basis"]` to size ITP p-value arrays | One fewer dict lookup | Index-out-of-bounds or zero-padding on B-spline knot clamping | Never |
| Combine `_DIAGNOSTICS_METHODS` update and aspect builder in separate commits | Smaller diffs | MCP tool broken for one CI window; guard-sync test fails between commits | Never |
| Use real datasets (Canadian Weather, Growth) for PACE/ITP executed fences | Real-data examples | ~19-minute build grows to 30+ minutes | Never for executed fences; OK for illustrative (non-executed) fences |

---

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| `IrregFdata` in Python | Pass a 2-D numpy array to `pace_fpca` | Expose `irreg_fdata_from_lists(argvals_list, values_list)` and require it as the sole input |
| `GlmFamily::Gamma` | Document as "log link" (statsmodels default) | Document as "inverse canonical link g(μ)=1/μ"; include a link-function table in the docs page |
| `DepthMethod` string dispatch | Only map the original 4 v5.0 variants | Map all 13 variants; include a `ValueError` wildcard for unknown strings |
| `ElasticMultinomialResult.train_probabilities` | Return as FdMatrix without noting it is row-normalised | Document "each row sums to 1.0"; add a test: `np.allclose(probs.sum(axis=1), 1.0)` |
| `ConcurrentRegrResult.beta_curve` row indexing | Access as `beta_curve[i, :]` thinking `i` is observation | Predictor k's β(t) is `beta_curve[k, :]` — rows are predictors, not observations |

---

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| Dense curves in `IrregFdata` (n_i >> 100) | Per-curve Cholesky solve is O(n_i³) | Document "expected regime: sparse data, n_i ≤ ~50 per curve"; warn if `total_points / n_obs > 50` | n_i > 200 per curve |
| `n_perm=999` in ITP docs fences | Docs build time exceeds 30 min | Use `n_perm=199` for fences; note full `n_perm=999` as production default in docstring | Any executed fence with default params |
| `ncomp` too large for sparse PACE data | `actual_ncomp=0` → `FdarError::ComputationFailed` | Document "ncomp should be ≤ min n_i − 1"; add a pre-call check | `ncomp >= min(n_i)` |

---

## "Looks Done But Isn't" Checklist

- [ ] **`pace_fpca` binding:** `IrregFdata` Python type is exposed (not a numpy array shim) — verify `fdars.irreg_fdata_from_lists([...], [...])` works as the entry point
- [ ] **`elastic_multinomial` binding:** negative-label guard applied (not relying on core error alone) — verify `pytest.raises(ValueError)` for `y=[-1, 0, 1]`
- [ ] **`DepthMethod` dispatcher:** all 9 new variants mapped — verify `functional_depth(data, method="extreme_rank_length")` returns without `ValueError`
- [ ] **ITP determinism:** seed defaults to 0 — verify two calls with identical args produce bit-identical `adjusted_pvalues`
- [ ] **ITP p-value array length:** `len(result["adjusted_pvalues"]) == result["n_basis"]` — verify with a B-spline call where knot clamping may reduce the actual count
- [ ] **Outlier index dtype:** `result["shape_outliers"].dtype == np.int64` (not bool) — verify for all four new detectors
- [ ] **Advisor grounding:** `json.dumps(build_diagnostics(result, method="itp"), sort_keys=True)` succeeds without `TypeError` — verify in CI
- [ ] **MCP guard-sync commit:** `_DIAGNOSTICS_METHODS` updated in same commit as new aspect builder — verify no green→red→green in CI
- [ ] **PACE diagram:** observations shown as irregular per-curve dots, not shared grid — verify visually via `rsvg-convert` PNG
- [ ] **ITP diagram:** adjusted p-values shown at or above raw p-values everywhere — verify visually

---

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| `beta_curve` transposition (p vs n_obs) | Bindings — Group A (Regression) | Multi-predictor test: `result["beta_curve"].shape == (p, m)` with `p=3` |
| `IrregFdata` missing as Python type | Bindings — Group B (FPCA) | `fdars.irreg_fdata_from_lists` exists; `pace_fpca` accepts its result |
| `eigenfunctions` shape (m, ncomp) vs (ncomp, m) | Bindings — Group B (FPCA) | `result["eigenfunctions"].shape == (m, ncomp)`; column orthonormality |
| `actual_ncomp < requested ncomp` | Bindings — Group B (FPCA) | Test with tiny data producing `actual_ncomp < config.ncomp` |
| `elastic_multinomial` negative/noncontiguous labels | Bindings — Group B (Classification) | `pytest.raises(ValueError)` for `[-1,0,1]` and `[0,2,4]` |
| `DepthMethod` 9 new variants not mapped | Bindings — Group C (Depth/Outliers/ITP) | Smoke test for each of 9 new variant strings |
| `SeqTransform` wildcard arm + all 5 variants | Bindings — Group C | Compile check + 5-variant smoke tests |
| `GlmFamily` wildcard + Gamma inverse link | Bindings — Group A (Regression) + Docs | Compile check; Gamma worked example documents inverse link explicitly |
| ITP seed non-determinism | Bindings — Group C | Determinism test: two calls → equal `adjusted_pvalues` |
| `ItpResult.n_basis` vs `nbasis` mismatch | Bindings — Group C | `len(result["adjusted_pvalues"]) == result["n_basis"]` with B-spline call |
| Outlier index dtype (usize not bool) | Bindings — Group C | `result["shape_outliers"].dtype == np.int64` for all four detectors |
| `outliers_threshold_lrt` seed not exposed | Bindings — Group C | Audit `outliers_mod.rs` before extending; add seed if missing |
| Non-exhaustive struct literals in tests | Bindings — all groups | Compiler catches at build time; never attempt struct-literal construction |
| numpy scalar in ITP advisor diagnostics | Advisor extension | `json.dumps(build_diagnostics(..., method="itp"), sort_keys=True)` in CI |
| Outlier advisor stores index lists not scalars | Advisor extension | Each diagnostic value is `float` or `int`; grounding guard passes |
| `_DIAGNOSTICS_METHODS` guard-sync | Advisor extension | Single-atomic-commit check; guard-sync CI assertion test |
| Depth-fence diagram symmetric bands | Docs | `rsvg-convert` PNG review: asymmetric bands following depth order |
| PACE diagram showing regular shared grid | Docs | `rsvg-convert` PNG review: per-curve irregular observation dots visible |
| ITP closure direction — adjusted below raw | Docs | Visual check: adjusted ≥ raw at every basis component index |
| PACE/ITP fence datasets too large | Docs | `mkdocs build` completes in < 25 min; time the build locally |

---

## Sources

- `fdars-core` v0.23.0 source: `concurrent_regression.rs`, `pace_fpca.rs`, `outliers.rs`, `inference/itp.rs`, `elastic_regression/logistic.rs`, `scalar_on_function/glm.rs`, `depth/dispatch.rs` — HIGH confidence (authoritative source)
- pyfda `.planning/milestones/v5.0-phases/31-REVIEW-FIX.md` — CR-01 negative-label guard, WR-01 seed-default doc fix, WR-02 `json.dumps` determinism test pattern — HIGH confidence
- pyfda `.planning/milestones/v4.0-phases/27-CONTEXT.md` — multi-curve transposition guard, banded distance-matrix test pattern — HIGH confidence
- pyfda `.planning/RETROSPECTIVE.md` — v4.0 tracer-first + transposition test discipline, v5.0 `CvCriterion` wildcard-arm lesson — HIGH confidence
- pyfda `src/convert.rs` — layout conversion functions; confirmed transposition mechanism — HIGH confidence
- pyfda `.planning/codebase/CONCERNS.md` — existing `unwrap` risks, fragile result-dict patterns, `numpy1d_to_usize_vec` unchecked cast — MEDIUM confidence (dated 2026-08-07, pre-v5.0; underlying structural concerns remain valid)
- pyfda `python/fdars/mcp/server.py:_DIAGNOSTICS_METHODS` and `advisor/aspects/` — grounding pattern, `json.dumps` guard, `_resolve_float` helper — HIGH confidence

---
*Pitfalls research for: pyfda v6.0 — fdars-core 0.23 bindings (Regression, PACE-FPCA/Classification, Depth/Outliers/ITP)*
*Researched: 2026-08-20*
