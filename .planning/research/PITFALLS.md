# Pitfalls Research

**Domain:** PyO3/maturin Rust-Python bindings — fdars-core 0.14.0 → 0.17.0 crate bump + new function bindings (interpolation/imputation, functional stats/scoring, shift registration/alignment quality, banded elastic alignment), advisor extension, and docs
**Researched:** 2026-08-13
**Confidence:** HIGH for layout/transposition and grounding-invariant pitfalls (confirmed against convert.rs source and live docs.rs API); HIGH for banded-naming resolution (both `_banded` and `_with_band` variants confirmed to coexist in 0.17.0); MEDIUM for numeric-behavior change pitfalls (faer FPCA SVD path — confirmed additive/non-breaking but numeric equivalence tolerance unverified against real test suite); HIGH for docs/offline-determinism pitfalls (established from v2.1 retrospective and SVGO gate patterns)

---

## Critical Pitfalls

### Pitfall 1: Multi-Curve Transposition Scrambling in Matrix-Returning New Bindings

**What goes wrong:**
Any new binding that receives a 2-D result from fdars-core (`functional_covariance` → m×m FdMatrix, `spline_interpolate` / `spline_interpolate_with_policy` on n curves at new query points → n×q FdMatrix, `karcher_mean_with_band` aligned_data → n×m FdMatrix) must route through `fdmatrix_to_numpy2d`. If a developer forgets this and calls `PyArray2::from_vec2` directly on `mat.to_column_major()` (or on the raw flat Vec without transposing), numpy receives a column-major layout interpreted as row-major. The result looks plausible on a single curve (shape is right, values are numeric) but every multi-curve result is scrambled — observations and time-points are swapped. This is exactly the bug class that upstream shipped a fix for in 0.14.0 (#33: the B-spline basis recon path was reading column-major data as row-major).

For `functional_covariance` the stakes are higher: the output is an m×m symmetric matrix. A transposition bug produces a matrix that is still symmetric and still has the right shape, so no shape assertion catches it — the values are silently wrong at every off-diagonal entry. Only a numerical round-trip test against a known covariance (e.g., covariance of constant curves = 0, covariance of two known curves computed by hand) will catch it.

**Why it happens:**
The pattern is invisible: `mat.to_row_major()` exists and is used by `fdmatrix_to_numpy2d`, but `mat.to_column_major()` also exists and is tempting when the developer is looking at the raw flat Vec. Every existing binding uses `fdmatrix_to_numpy2d` correctly, but each new binding is a fresh opportunity to forget.

**How to avoid:**
Enforce a single conversion rule: **never call `PyArray2::from_vec2` directly on FdMatrix data; always call `fdmatrix_to_numpy2d(py, &result)`**. For `functional_covariance` specifically, add a dedicated round-trip test: construct data with known covariance (two orthogonal step functions → off-diagonal covariance = 0; two identical curves → covariance = variance); assert element-wise that cov[i, j] == cov[j, i] AND that the diagonal equals the pointwise variance. For interpolation bindings, construct a dataset where every curve is a known function (e.g., `f(t) = sin(t)`), interpolate at query points you can compute analytically, then assert `np.testing.assert_allclose(result[i], expected[i])` per-curve — a scramble test that no shape-only check catches.

**Warning signs:**
- A new `*_mod.rs` function that builds a `PyArray2` without calling `fdmatrix_to_numpy2d`
- A test that only checks `result.shape == (n, m)` without checking per-curve values
- A covariance test that only checks symmetry without checking known off-diagonal values

**Phase to address:**
Interpolation/imputation binding phase (earliest matrix-returning new bindings). Add the multi-curve round-trip transposition test as a first-wave deliverable before any other function in that phase goes green.

---

### Pitfall 2: Banded Alignment Naming Ambiguity — Two Parallel APIs in 0.17.0

**What goes wrong:**
fdars-core 0.17.0 exports **both** `karcher_mean_banded` (takes `band_frac: f64`) **and** `karcher_mean_with_band` (takes `band_frac: Option<f64>`), and similarly for `elastic_self_distance_matrix_banded` / `elastic_self_distance_matrix_with_band` and the cross variants. These are **not aliases** — they have different call signatures:

```
karcher_mean_banded(data, argvals, max_iter, tol, lambda, band_frac: f64) -> KarcherMeanResult
karcher_mean_with_band(data, argvals, max_iter, tol, lambda, band_frac: Option<f64>) -> KarcherMeanResult
```

The `_banded` variant always applies the band (a `band_frac ≤ 0 || ≥ 1` reproduces unbanded); the `_with_band` variant treats `None` as "skip the band entirely, identical to `karcher_mean`." Binding the wrong one, or binding both as if they are the same, causes either silent wrong behavior (band_frac=0.0 does not disable the band in `_banded`, it effectively sets zero-width band — likely panics or gives degenerate results) or unnecessary API surface duplication visible to Python users.

The PROJECT.md target says "banded elastic alignment (`karcher_mean_with_band`, `*_distance_matrix_with_band`, `band_frac`)" — this names the `_with_band` family explicitly. Bind the `_with_band` variants; expose `band_frac` as `Optional[float] = None` in the Python signature. Do not also bind the `_banded` variants unless a separate use case is scoped.

**Why it happens:**
The naming coexists because 0.16.0 added the `_with_band` opt-in family and 0.17.0 kept both for backwards compatibility with any direct fdars-core Rust consumers. A developer scanning `fdars_core::alignment::` will see both names and reasonably wonder which to use.

**How to avoid:**
When writing `alignment_mod.rs`, import `fdars_core::alignment::karcher_mean_with_band` (not `karcher_mean_banded`) and map `band_frac: Option<f64>` directly. Write a Python-level test that calls `karcher_mean_with_band(data, argvals, band_frac=None)` and asserts the output equals `karcher_mean(data, argvals)` to numerical tolerance — this is the spec stated in the 0.17.0 docs. Add a docstring in `alignment_mod.rs` and the Python stub explaining: "pass `band_frac=None` for the unbanded elastic Karcher mean (equivalent to `karcher_mean`); pass a float in (0, 1) to restrict alignment to a Sakoe-Chiba band of that width."

**Warning signs:**
- Cargo.toml uses `fdars_core::alignment::karcher_mean_banded` in any new binding
- A Python test that passes `band_frac=0.0` expecting unbanded behavior
- A `register()` call that adds both `karcher_mean_banded` and `karcher_mean_with_band` as separate Python functions

**Phase to address:**
Alignment/registration binding phase. Flag the naming choice explicitly in the plan before writing the binding.

---

### Pitfall 3: Grounding-Invariant Regression When Extending build_diagnostics

**What goes wrong:**
The `_DIAGNOSTICS_METHODS` / `_RUNNABLE_METHODS` guard-sync test (`test_diagnostics_methods_match_advisor_supported`) enforces a set-equality invariant: every method in `build_diagnostics` must be in `_DIAGNOSTICS_METHODS`; every method in `_RUNNABLE_METHODS` must be runnable via `fdars_run_method`. When new diagnostic branches are added for v4.0 capabilities (scoring metrics, imputation quality, registration quality), a developer may add the branch in `build_diagnostics` but forget to:

1. Add the method name to `_DIAGNOSTICS_METHODS` in `advisor.py` → test fails (set is a strict superset)
2. Add a grounded-evidence key: if the new branch returns a scalar computed by Python code rather than by fdars (e.g., the developer calls `np.mean(shifts)` instead of `fdars.alignment.least_squares_score(registered, argvals)`), the grounding invariant is violated — LLM advice will cite a number not computed by fdars. The schema validator does not catch this because the number is still a number.
3. Forget to add the new method to the offline CI offline-diagnostics matrix test — the branch gets no test coverage.

The second failure is the most dangerous because it is silent: tests pass, schema validates, but the advisor is now hallucinating-adjacent (citing a Python-computed mean as if it were a fdars metric).

**Why it happens:**
The grounding invariant is enforced by discipline (schema + system prompt) and by the guard-sync set-equality test, but not by the type system. A developer who does not know the invariant will naturally write `np.mean(result.shifts)` for the shifts diagnostic because it is the shortest path.

**How to avoid:**
For every new diagnostic branch: (a) identify the fdars function that computes the evidence value — for registration quality, use `fdars.alignment.least_squares_score`, `pairwise_correlation_score`, or `sobolev_least_squares_score`; for scoring metrics, use `fdars.scoring.functional_mae` / `functional_mse` etc.; (b) write the diagnostic so it calls the bound fdars function, not Python math; (c) add the method key to `_DIAGNOSTICS_METHODS` in the same commit as the branch; (d) add a test that exercises the new branch with an offline fixture and asserts the evidence dict contains at least one key with a finite float.

Before merging the advisor extension phase, run the guard-sync test explicitly: `pytest tests/test_advisor.py -k test_diagnostics_methods_match_advisor_supported -v`. Its failure message names the mismatched keys.

**Warning signs:**
- A new `build_diagnostics` branch that calls `np.mean`, `np.std`, or `statistics.*` on fdars output instead of a bound fdars function
- A commit that adds a branch in `build_diagnostics` but does not touch `_DIAGNOSTICS_METHODS`
- A new advisor test that mocks the fdars call rather than using the real bound function

**Phase to address:**
Advisor extension phase (after new bindings are green). The guard-sync test must be in the verify checklist for that phase.

---

### Pitfall 4: Result-Error Propagation Gaps in New Bindings

**What goes wrong:**
The new fdars-core functions return `Result<T, FdarError>` far more consistently than the 0.14.0 surface:

- `spline_interpolate` → `Result<FdMatrix, FdarError>` (rejects OOD query points)
- `spline_interpolate_with_policy` → `Result<FdMatrix, FdarError>`
- `impute_missing_values` → `Result<FdMatrix, FdarError>` (rejects all-NaN rows, dimension mismatch)
- `functional_variance` → `Result<Vec<f64>, FdarError>` (rejects n < 2)
- `functional_covariance` → `Result<FdMatrix, FdarError>`
- `trim_mean` → `Result<Vec<f64>, FdarError>` (rejects alpha outside [0,1))
- `depth_based_median` → `Result<usize, FdarError>` (rejects empty data)
- `least_squares_shift_registration` → `Result<ShiftRegistrationResult, FdarError>`
- `least_squares_score` / `pairwise_correlation_score` / `sobolev_least_squares_score` → all `Result<f64, FdarError>`
- `functional_mae` / `functional_mse` / `functional_mape` / `functional_msle` / `functional_explained_variance` → all `Result<f64, FdarError>`

A binding that uses `.unwrap()` instead of `to_pyresult()` will panic on the Python side with a Rust backtrace rather than raising a clean `ValueError`. This matches the known tech debt in `convert.rs:57` and `basis_mod.rs` documented in CONCERNS.md — do not replicate it in new bindings.

Additionally, `depth_based_median` returns `Result<usize, FdarError>` — the caller must use the index to retrieve the actual curve. A binding that only returns the index (a Python `int`) forces users to index back into the input data themselves; the ergonomic pattern is to return the curve as a 1-D numpy array (i.e., call `fdmatrix_to_numpy2d` on the full matrix, then slice row `idx`).

**Why it happens:**
Developers copy the pattern from 0.14.0 bindings that called infallible fdars-core functions and used `.unwrap()` casually. The new functions are explicitly fallible, but the old code pattern is right there to copy.

**How to avoid:**
Every new `*_mod.rs` function must end with `to_pyresult(...)?.into()` or equivalent — no `.unwrap()` on any fdars-core return value. For `depth_based_median`, return the actual curve row, not the index: `let idx = to_pyresult(fdars_core::fdata::depth_based_median(&mat))?; Ok(vec_to_numpy1d(py, mat.row(idx).to_vec()))`. Add an explicit error-propagation test for each fallible function: pass an empty matrix and assert `pytest.raises(ValueError, match="...")`; pass mismatched dimensions and assert the same. These tests cost nothing and prevent the panic-in-production class.

**Warning signs:**
- Any `.unwrap()` in new `*_mod.rs` files
- A `depth_based_median` binding that returns `usize` / Python `int` to the caller
- A test suite for a new binding that has no `pytest.raises(ValueError)` test

**Phase to address:**
All three binding phases (interpolation/imputation, functional stats/scoring, alignment/registration). Add `.unwrap()` to the CI clippy deny list for new files: `#![deny(clippy::unwrap_used)]` in new modules, or enforce via code review checklist.

---

### Pitfall 5: NaN / Off-Grid / Boundary Edge Cases in Interpolation and Imputation

**What goes wrong:**

**spline_interpolate strict domain rejection:** `spline_interpolate` returns `FdarError::InvalidParameter` when any query point lies outside `[argvals[0], argvals[m-1]]`. If the Python binding does not expose `spline_interpolate_with_policy`, users who accidentally pass a query point 1e-10 outside the domain (floating-point rounding near the boundary) get a cryptic `ValueError` instead of useful behavior. The binding should expose `spline_interpolate_with_policy` with `ExtrapolationPolicy` mapped to a Python string enum:

```
"boundary" → ExtrapolationPolicy::Boundary  (clamp to nearest endpoint)
"exception" → ExtrapolationPolicy::Exception (raise ValueError — the default)
"fill"      → ExtrapolationPolicy::Fill(v)   (constant v for OOD points)
"periodic"  → ExtrapolationPolicy::Periodic  (wrap modulo domain length)
```

The `Fill(v)` variant carries a payload value — map this to a Python `fill_value: float = 0.0` parameter that is only used when `policy="fill"`.

**impute_missing_values all-NaN row rejection:** `impute_missing_values` raises `FdarError::InvalidParameter` when an entire curve row is NaN. A Python user who passes a matrix with even one all-NaN row gets an error. The binding must surface this with a descriptive message (fdars-core's message becomes the `ValueError` string via `to_pyerr`). Pre-binding validation that counts NaN rows and raises early with "row i is entirely NaN — cannot impute" is friendlier, though not required.

**ExtrapolationPolicy::Periodic domain length requirement:** Periodic wrapping requires domain length > 0 (i.e., `argvals[-1] - argvals[0] > 0`). Passing a constant grid (all same value) with `policy="periodic"` will produce `FdarError::InvalidParameter` from the core. The Python binding should not add its own check (let the error propagate cleanly) but the docs example must not use a zero-length domain with Periodic.

**Why it happens:**
Off-grid edge cases are easy to miss when writing tests with clean linspace grids. The distinction between `spline_interpolate` (strict) and `spline_interpolate_with_policy` (flexible) is invisible if only the strict version is bound.

**How to avoid:**
Bind `spline_interpolate_with_policy` (not `spline_interpolate`) as the primary Python-facing function. Expose `policy: str = "exception"` and `fill_value: float = 0.0`. Add tests: (a) query point exactly at boundary — must succeed; (b) query point 1e-10 outside boundary with `policy="boundary"` — must return boundary value; (c) all-NaN row to `impute_missing_values` — must raise `ValueError` with a message containing "NaN" or "entirely" or similar; (d) `policy="fill"` with query outside domain — must return `fill_value`.

**Warning signs:**
- Only `spline_interpolate` (strict) is bound, with no `policy` parameter
- No test for query points at or near domain boundaries
- No test for all-NaN rows passed to `impute_missing_values`
- `policy="periodic"` used in a docs example without verifying domain length > 0

**Phase to address:**
Interpolation/imputation binding phase. Edge-case tests must be in the phase verify checklist before the phase closes.

---

### Pitfall 6: Offline / Deterministic Docs Build Broken by New Executed Fences

**What goes wrong:**
New worked-example fences for interpolation, scoring metrics, shift registration, and registration quality will run against the real compiled `fdars` during `mkdocs build`. Three distinct failure modes:

1. **Network or API key required:** a fence that calls `advise()` (LLM path) or imports an optional extra not in the base docs build environment will cause the build to fail in CI. Every new fence must either be illustrative (not executed) or provably offline (calls only `fdars.*` functions, no `[mcp]`/`[advisor]` extras, no API key).

2. **Non-deterministic numeric output in fences:** if a new fence calls any function with internal randomness (e.g., `cluster_optim`, any seeded depth projection) without a fixed seed, the fence output will differ between builds, breaking the byte-identical determinism gate. For registration/alignment, `karcher_mean_with_band` is iterative — its output is deterministic given the same data and seed, but only if the data is constructed from a deterministic source (fixed `np.random.seed` or literal array). Any fence using `np.random` without a seed will fail the determinism gate.

3. **Fence output hard-codes numbers that break with the 0.17.0 bump:** if a fence was written against 0.14.0 with exact numeric output (e.g., `depth_based_median returns curve 3`), and the 0.17.0 faer SVD path (enabled by the `linalg` feature) or parallel fold reordering changes the numeric result, the fence will print different numbers and the doc-test sentinel will fail.

**Why it happens:**
The fast-path during phase execution is to write a fence that "runs and looks right," which is easy to verify locally. The determinism gate only catches it during the SVGO/build CI run, which is slow (~400s). Pattern established in v2.1: only the Python-API advisor page carries an executed fence; MCP/Skill pages are illustrative.

**How to avoid:**
For every new executed fence: (a) fix all random seeds (`np.random.seed(42)` at the top of the block); (b) use only base-extras functions (`fdars.fdata`, `fdars.alignment`, `fdars.scoring`, `fdars.helpers` — not `fdars.advisor` or `fdars.mcp`); (c) print a `FDARS_FENCE_OK` sentinel at the end and grep the built HTML for it during verify; (d) if a fence must cite advisor output, make it illustrative (comment out the `advise()` call, show the expected output as a literal string). For scoring metrics fences specifically, construct data from literal numpy arrays, not from `np.random`, so the integrated error is analytically known and can be asserted in a comment.

**Warning signs:**
- A new ```` ```python exec="1" ``` ```` fence that imports from `fdars.advisor` or uses `advise()`
- A fence with `np.random.randn(...)` but no `np.random.seed(...)` call
- A fence with literal numeric output that was generated against a local build (not verified against CI)

**Phase to address:**
Docs phase (diagram/example authoring). Add "run `mkdocs build --strict` and grep HTML for `FDARS_FENCE_OK`" to the phase verify checklist. The SVGO idempotence gate covers diagram determinism; the `FDARS_FENCE_OK` pattern covers fence execution.

---

### Pitfall 7: faer FPCA SVD Path — Silent Numeric-Behavior Change Breaking Exact-Equality Tests

**What goes wrong:**
fdars-core 0.15.0 introduced a faer-backed FPCA SVD path (1.8–4.1× speedup) under the `parallel` feature (which pyfda already enables). The upstream release notes say results are "equivalent within 1e-8·σ₁" — meaning the leading singular value magnitude sets the absolute tolerance. For a typical functional dataset with `σ₁ ≈ 10`, the tolerance is `1e-7`. Any existing test or doc fence that asserts FPCA results to `1e-9` absolute tolerance or tighter will start failing after the bump.

The failure mode is insidious: the test suite is green on the 0.14.0 wheel but fails immediately on the first `maturin develop` after bumping `Cargo.toml`. The engineer sees a CI failure in `test_r_parity.py` on a line like `np.testing.assert_allclose(scores, expected_scores, atol=1e-10)` and does not immediately connect it to the SVD backend change.

**Why it happens:**
The 0.14.0 test suite was written against the nalgebra SVD. The faer SVD is numerically equivalent but not bit-identical. Tests written with `atol=0` (the default for `assert_array_equal`) or very tight `atol` will fail.

**How to avoid:**
Immediately after the crate bump (first phase of v4.0), run the full test suite and compare FPCA-related failures. For any failing assertion, relax the tolerance to `atol=1e-6, rtol=1e-5` (generous but scientifically correct). Update any fence that hard-codes FPCA scores to use `assert abs(result - expected) < 1e-6` in the comment. Document the tolerance level in a new comment: `# tolerance: faer SVD path, equivalent within 1e-8*sigma_1 per 0.15.0 release notes`. The doc fence determinism is unaffected as long as: (a) the same fdars wheel is used across both build runs (CI rebuilds from the same Cargo.lock), and (b) no fence hard-codes numeric output from FPCA — if it does, regenerate the expected output after the bump.

**Warning signs:**
- `np.testing.assert_allclose(fpca_result, expected, atol=1e-10)` in any test touching `to_pc()` or `fpca_*` functions
- `np.testing.assert_array_equal` on floating-point FPCA outputs (no tolerance at all)
- Doc fences with literal FPCA variance-explained values copied from a local 0.14.0 run

**Phase to address:**
Crate bump phase (first phase of v4.0, before any new bindings). Run `pytest tests/ -x` immediately after `maturin develop --release` with the bumped `Cargo.toml`. Address all FPCA tolerance failures in that phase before proceeding.

---

### Pitfall 8: Cargo.toml Caret Pin Not Covering 0.17.0

**What goes wrong:**
The current `Cargo.toml` pins `fdars-core = "0.14.0"` (exact, no caret). A bump to `"0.17.0"` is also exact. The risk is not the bump itself (it is intentional) but what happens after: `"0.17.0"` will not automatically pick up 0.17.1 patch fixes. Given that bugs #33 and #34 both required a rapid rebuild+re-release of pyfda, locking to an exact patch version creates the same operational burden: every upstream patch requires a manual bump and re-release.

The alternative, `fdars-core = "0.17"` (caret, equivalent to `>=0.17.0, <0.18.0`), accepts patch releases automatically via `cargo update` without a Cargo.toml change. The risk is that a 0.17.x patch introduces a numeric change that breaks tests — but this is caught by the existing test suite on the next CI run.

**Why it happens:**
The original CONCERNS.md documents this as a known issue ("fdars-core dependency version lock"). The exact-pin was a deliberate choice for maximum reproducibility, but it creates a manual re-release burden for every upstream patch.

**How to avoid:**
At the crate bump, set `fdars-core = "0.17"` (caret) in `Cargo.toml`, not `"0.17.0"`. This allows `cargo update` to pick up patches. If the team wants stricter reproducibility, use `fdars-core = "=0.17.0"` (the `=` prefix is the Cargo exact-version syntax) but document the operational cost. Do not silently leave the version as `"0.14.0"` in `Cargo.toml` and expect the bump to happen automatically — it will not.

**Warning signs:**
- `Cargo.toml` still reads `fdars-core = "0.14.0"` after the bump phase closes
- `cargo tree | grep fdars-core` shows 0.14.0 after `maturin develop`

**Phase to address:**
Crate bump phase (first). Verify with `cargo tree | grep fdars-core` that the resolved version is 0.17.x before any new binding work begins.

---

### Pitfall 9: Python 3.9–3.14 Extra Gating for New Optional Bindings

**What goes wrong:**
The v3.0 CI matrix covers Python 3.9–3.14 with version-gated extras (`[mcp]` requires Python 3.10+). If any new v4.0 binding or advisor extension introduces a new dependency that does not support all of 3.9–3.14, the CI matrix will fail on the lower bound. Concrete risks:

- If the scoring metrics Python wrapper imports `scipy.integrate` (for cross-checking), scipy 1.10 is the minimum — but `scipy` is already listed as a docs dependency, so it is not new.
- If a new advisor task family uses `tomllib` (stdlib in 3.11+) or `typing.Self` (3.11+) or `match` syntax (3.10+), the 3.9 CI runner will fail with a syntax error.
- If `ImputationMethod` or `ExtrapolationPolicy` are exposed as Python `StrEnum` (Python 3.11+), the 3.9/3.10 CI will fail.

**Why it happens:**
The bindings layer is ABI3 (stable ABI, `abi3-py39`) so the compiled wheel itself is fine. The Python wrapper code in `python/fdars/` is where version-gating is needed. A developer on Python 3.12 who writes `method: ImputationMethod = ImputationMethod.LINEAR` as a `StrEnum` will not see the 3.9 failure locally.

**How to avoid:**
For enums exposed to Python from new bindings (`ExtrapolationPolicy`, `ImputationMethod`, `ShiftRegistrationResult`), implement them as plain string constants or as a class with string class attributes (compatible with 3.9+), not as `StrEnum`. Use `Literal["boundary", "exception", "fill", "periodic"]` in type hints (not `StrEnum` subclasses). Add a bare-venv smoke test on the 3.9 CI runner that imports the new modules and calls at least one function — the same pattern used in v3.0 for the provider-agnostic advisor.

**Warning signs:**
- `from enum import StrEnum` in any new `python/fdars/*.py` file (3.11+ only)
- `match ... case ...` syntax in new Python wrapper code (3.10+ only)
- `tomllib` or `typing.Self` in new Python wrapper code (3.11+ only)
- A new extra (`[scoring]` or similar) that is not guarded with a version check in `pyproject.toml`

**Phase to address:**
All three binding phases (new Python wrapper code written per phase). Run `python3.9 -c "import fdars.fdata; import fdars.helpers"` on a 3.9 venv immediately after each phase's maturin build.

---

### Pitfall 10: ShiftRegistrationResult Field Access Pattern

**What goes wrong:**
`least_squares_shift_registration` returns `ShiftRegistrationResult` with fields `registered_data` (FdMatrix) and `shifts` (Vec<f64>). The binding must expose both fields to Python. A developer who only exposes `registered_data` (because that is the primary output) leaves the `shifts` vector inaccessible, forcing users to re-run the function or compute shifts themselves. The correct pattern is to return a Python dict with both keys — consistent with the existing pattern in `alignment_mod.rs` (see `elastic_align_pair` returning `{"f_aligned", "gamma", "distance"}`).

A second pitfall: `registered_data` is an FdMatrix (column-major) and must go through `fdmatrix_to_numpy2d`, not be returned as-is. `shifts` is a Vec<f64> and goes through `vec_to_numpy1d`. If the developer swaps the two (returns `shifts` through `fdmatrix_to_numpy2d` or `registered_data` through `vec_to_numpy1d`), the error is type-level and will be caught by PyO3 at runtime — but only if a test actually exercises both fields.

**Why it happens:**
Dict-returning bindings require explicitly mapping every struct field. It is easy to ship with only the "interesting" field and leave the rest.

**How to avoid:**
Test both fields: `result["registered_data"].shape == (n, m)` and `result["shifts"].shape == (n,)` and `result["shifts"].dtype == np.float64`. Add a numerical test: for data that is already aligned (identity shift), assert `np.allclose(result["shifts"], 0.0, atol=1e-6)`.

**Warning signs:**
- `least_squares_shift_registration` binding returns only a single numpy array
- No test that accesses `result["shifts"]`

**Phase to address:**
Alignment/registration binding phase.

---

### Pitfall 11: Method-Accuracy Errors in New SVG Diagrams

**What goes wrong:**
The v3.0 retrospective identified that diagram label-overlaps and stale cross-refs slipped past automated gates and were only caught by visual review. For v4.0, three diagram domains are new: shift registration (horizontal shift concept), ExtrapolationPolicy (boundary/fill/periodic clamp behavior), and registration quality scores (spread-around-mean concept). Each has a specific failure mode:

- **Shift registration:** diagram shows curves shifted in the vertical direction (value shift) instead of horizontal direction (time shift). This is the most common confusion in the domain — "shift registration" in FDA means rigid horizontal (time-axis) translation, not vertical offset.
- **ExtrapolationPolicy:** diagram omits the `Fill(v)` variant or shows it as extrapolation (continuing the spline trend) instead of constant fill.
- **Registration quality:** diagram shows `least_squares_score` as the mean L2 distance between curve pairs, but the correct definition is the Simpson-weighted L2 spread of registered curves around their cross-sectional mean (not pairwise distance). These are different quantities.

**Why it happens:**
Hand-authored diagrams require the author to know the precise mathematical definition. "Shift registration" sounds like it could be vertical; "pairwise score" and "mean spread" look similar in a cartoon.

**How to avoid:**
Write the mathematical definition in a comment at the top of each new SVG file before drawing any path elements. For shift registration: "each curve f_i is replaced by f_i(t + δ_i) where δ_i is the optimal horizontal shift — the time axis, not the value axis, moves." Review each diagram against the fdars-core docs.rs function documentation before SVGO gate. Run `rsvg-convert -w 1440 -h 600 <svg> -o out.png` and Read the PNG to confirm labels match arrows, axes are labeled correctly, and the visual story matches the definition.

**Warning signs:**
- A shift registration diagram where arrows point vertically (up/down) instead of horizontally (left/right)
- An ExtrapolationPolicy diagram with only 2-3 variants shown (all 4 must be shown or the omission must be documented)
- A registration quality diagram that shows pairwise arrows between curves instead of curves clustered around a mean

**Phase to address:**
Docs phase. SVGO idempotence gate catches SVG formatting issues but not method-accuracy errors; a human review of the rendered PNG is the only method-accuracy gate.

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| `.unwrap()` on new fdars-core `Result` returns | Saves 2 lines per binding | Panics in production on degenerate input instead of clean `ValueError`; replicates CONCERNS.md known tech debt | Never — use `to_pyresult()` |
| Returning `depth_based_median` result as Python `int` (index only) | Simpler binding | Forces users to index back into data manually; inconsistent with other median-returning functions that return the curve | Never — return the curve row |
| Binding `karcher_mean_banded` instead of `karcher_mean_with_band` | Already exists in module search | Wrong semantics: `band_frac=0.0` does not mean unbanded in `_banded`; API inconsistency with the `_with_band` family | Never for the primary binding |
| Executed fence with `np.random` and no seed | Easier to write | Breaks the build-determinism CI gate; causes random test flake | Never in executed fences |
| Exact version pin `fdars-core = "=0.17.0"` instead of caret | Maximum reproducibility | Manual re-release burden for every upstream patch (repeated v2/v3 experience) | Acceptable if team has a defined patch SLA |
| Caret pin `fdars-core = "0.17"` | Automatic patch uptake | A 0.17.x patch may silently change numeric output and break tests | Acceptable — CI catches it |
| StrEnum for ExtrapolationPolicy / ImputationMethod | Idiomatic Python 3.11+ | Breaks Python 3.9/3.10 CI runners | Never — use string literals / Literal type hints |

---

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| `fdars_core::helpers::spline_interpolate` | Binding only the strict form, no policy parameter | Bind `spline_interpolate_with_policy` as the primary function with `policy: str = "exception"` |
| `fdars_core::fdata::functional_covariance` | Returning FdMatrix directly without `fdmatrix_to_numpy2d` | Always route through `fdmatrix_to_numpy2d(py, &result)` — m×m output is still a matrix |
| `fdars_core::fdata::depth_based_median` | Returning the `usize` index to Python | Use the index to retrieve the curve row: `mat.row(idx)` → `vec_to_numpy1d` |
| `fdars_core::alignment::karcher_mean_with_band` | Passing `band_frac: f64` as a required parameter | Expose as `Optional[float] = None` in the Python signature; pass `Some(v)` only when not None |
| `fdars_core::scoring::functional_mae` (and siblings) | Assuming inputs are (y_pred, y_true) order | The order is `(y_true, y_pred, argvals)` — document explicitly, test with asymmetric inputs |
| `_DIAGNOSTICS_METHODS` guard-sync test | Adding a `build_diagnostics` branch without updating the set | Always update `_DIAGNOSTICS_METHODS` in the same commit as the branch |
| MCP boundary | Calling any fdars scoring or registration function inside the MCP server beyond the existing dispatch table | New methods belong in `fdars_run_method` dispatch only, with fdars doing the computation — not in the LLM request path |

---

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| Calling `spline_interpolate_with_policy` per-curve in a Python loop | O(n) maturin boundary crossings; each crossing pays the row-major→column-major transpose cost | Pass the full `(n, m)` matrix; let fdars loop internally | n > 100 curves |
| Calling `functional_covariance` on a high-m dataset | m×m output matrix: at m=1000, that is 1M floats (8MB) copied through the boundary | Document in docstring; recommend downsampling `argvals` before covariance if m > 500 | m > 500 evaluation points |
| `karcher_mean_with_band` with `band_frac=None` (unbanded) on large n | Same cost as `karcher_mean` — O(n × max_iter × m²) without the band speedup | Use `band_frac ≈ 0.3` for exploratory work; reserve unbanded for final publication runs | n > 200 curves, m > 200 points |
| Running `mkdocs build` in full mode (no `DOCS_FAST=1`) to verify a single new fence | Full build is ~400s because all fences execute | Use `DOCS_FAST=1` for fence iteration; run full build only for final verify | Every phase — will repeatedly time out the 2-min shell limit |

---

## "Looks Done But Isn't" Checklist

- [ ] **Crate bump:** `cargo tree | grep fdars-core` confirms 0.17.x, not 0.14.0 — verify before any new binding work
- [ ] **Layout correctness:** every new matrix-returning binding has a multi-curve round-trip test (not just a shape assertion)
- [ ] **Banded naming:** `karcher_mean_with_band` (not `karcher_mean_banded`) is registered in `alignment_mod.rs`; `band_frac=None` test passes
- [ ] **Error propagation:** every new binding has at least one `pytest.raises(ValueError)` test for a degenerate/invalid input
- [ ] **Guard-sync test green:** `test_diagnostics_methods_match_advisor_supported` passes after the advisor extension phase
- [ ] **Grounding invariant:** every new `build_diagnostics` branch calls a bound fdars function for its evidence value, not Python math
- [ ] **Offline docs build:** every new executed fence prints `FDARS_FENCE_OK` and the built HTML contains that string
- [ ] **FPCA tolerance:** no `assert_array_equal` or `atol < 1e-6` on any FPCA output in tests or doc fences
- [ ] **Python 3.9 clean:** `python3.9 -c "import fdars.fdata; import fdars.helpers; import fdars.scoring"` succeeds on a bare 3.9 venv
- [ ] **ShiftRegistrationResult:** binding returns `{"registered_data": ndarray(n,m), "shifts": ndarray(n,)}`; both fields tested
- [ ] **SVG diagram method-accuracy:** shift registration diagram shows horizontal shift; ExtrapolationPolicy shows all 4 variants; quality score diagram shows spread-around-mean, not pairwise distance

---

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Multi-curve transposition bug found after bindings merged | MEDIUM | Write the round-trip test first to confirm the bug; swap `from_vec2(mat.to_column_major())` for `fdmatrix_to_numpy2d(py, &mat)`; re-run tests |
| Guard-sync test fails after advisor extension | LOW | Add the missing method key(s) to `_DIAGNOSTICS_METHODS` and/or `_RUNNABLE_METHODS`; the failure message names the mismatched keys |
| FPCA tolerance failures after crate bump | LOW | Relax `atol` to `1e-6` on affected assertions; update doc fence expected outputs by running `maturin develop` and re-executing the fence locally |
| Banded alignment bound to `_banded` variant | LOW | Replace `karcher_mean_banded` with `karcher_mean_with_band` in `alignment_mod.rs`; change `band_frac: f64` to `band_frac: Option<f64>`; update register() call |
| Docs fence breaks build determinism (missing seed) | LOW | Add `np.random.seed(42)` at top of fence; regenerate expected outputs; re-run `mkdocs build --strict` |
| Python 3.9 CI failure from StrEnum | LOW | Replace `StrEnum` with a plain class or `Literal` type hint; no functional change needed |
| `impute_missing_values` panics on all-NaN row | LOW | Ensure `to_pyresult()` wraps the call; the FdarError message ("entirely NaN") becomes the ValueError message |

---

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| Multi-curve transposition scrambling | Interpolation/imputation binding phase (earliest matrix-returning new bindings) | Multi-curve round-trip test: known function, assert per-curve values not just shape |
| Banded alignment naming ambiguity | Alignment/registration binding phase | `band_frac=None` produces same output as `karcher_mean`; clippy: no `karcher_mean_banded` in new bindings |
| Grounding-invariant regression | Advisor extension phase | `test_diagnostics_methods_match_advisor_supported` green; offline fixture test for each new branch |
| Result-error propagation gaps | All three binding phases | `pytest.raises(ValueError)` tests for every new fallible function; no `.unwrap()` in new `*_mod.rs` files |
| NaN / off-grid / boundary edge cases | Interpolation/imputation binding phase | Tests: OOD query with `policy="boundary"`, all-NaN row, Periodic with valid domain |
| Offline / deterministic docs build | Docs phase | `FDARS_FENCE_OK` in built HTML; `mkdocs build --strict` green in CI; byte-identical repeat build |
| faer FPCA SVD numeric change | Crate bump phase (first) | Run full test suite immediately after bump; relax FPCA atol before proceeding |
| Cargo.toml pin not covering 0.17.0 | Crate bump phase (first) | `cargo tree \| grep fdars-core` shows 0.17.x |
| Python 3.9–3.14 extra gating | All three binding phases | Bare 3.9 venv smoke import; CI matrix all-green |
| ShiftRegistrationResult field access | Alignment/registration binding phase | Test both `result["registered_data"]` shape and `result["shifts"]` shape and values |
| SVG diagram method-accuracy | Docs phase | `rsvg-convert` visual review of each new diagram PNG before SVGO gate |

---

## Sources

- `src/convert.rs` (pyfda) — live source of `numpy2d_to_fdmatrix` / `fdmatrix_to_numpy2d`; confirmed row-major ↔ column-major transpose pattern
- `.planning/codebase/CONCERNS.md` (pyfda) — documents `.unwrap()` tech debt in convert.rs:57, basis_mod.rs, alignment_mod.rs; input validation gaps
- `.planning/RETROSPECTIVE.md` (pyfda) — v2.1 retrospective: diagram label-overlap, stale cross-refs, execution-sentinel pattern, illustrative-vs-executed fence split
- `docs.rs/fdars-core/0.17.0` — confirmed `karcher_mean_with_band` and `karcher_mean_banded` coexist with different `band_frac` types; confirmed all new function signatures and `Result` return types; confirmed `depth_based_median` returns `usize` not a curve; confirmed `functional_covariance` returns m×m FdMatrix
- `github.com/sipemu/fdars` releases page — confirmed 0.15.0 added faer FPCA SVD ("equivalent within 1e-8·σ₁"), 0.16.0 added `_with_band` family + imputation + scoring metrics
- pyfda memory: `fdars-core-basis-bug.md` — #33 transposition bug in B-spline basis path fixed in 0.14.0; confirms the exact class of layout bug that must be prevented in new bindings
- pyfda memory: `pyfda-release-versioning.md` — versioning and publish trigger patterns

---
*Pitfalls research for: pyfda v4.0 — fdars-core 0.17 binding upgrade*
*Researched: 2026-08-13*
