# Codebase Concerns

**Analysis Date:** 2026-08-07

## Tech Debt

**Unstable error handling in convert.rs**
- Issue: `.unwrap()` calls on `PyArray2::from_vec2()` in `src/convert.rs:57` and multiple places in `src/basis_mod.rs` (lines 295, 325, 526, 560) and `src/alignment_mod.rs` (lines 941, 969). These will panic if memory allocation fails or if the matrix cannot be converted, leaving no path for graceful degradation.
- Files: `src/convert.rs:57`, `src/basis_mod.rs:290-560`, `src/alignment_mod.rs:941,969`
- Impact: Silent panics in production code during high-dimensional data operations (e.g., large basis projections). Users get Python `RuntimeError` with no context instead of a proper `ValueError` with details.
- Fix approach: Replace `.unwrap()` with `.ok_or_else(|| PyValueError::new_err("..."))` and propagate `PyResult<T>` through all conversion functions. Add integration tests for edge cases (empty matrices, very large matrices).

**Excessive cloning in bindings**
- Issue: 307 instances of `.clone()`, `.to_vec()`, `.to_owned()` across binding modules. Many occur unnecessarily: e.g., converting from numpy to `Vec<f64>` when fdars-core accepts references, or cloning matrix data during intermediate conversions.
- Files: All `src/*_mod.rs` files; most prevalent in `src/explain_mod.rs`, `src/alignment_mod.rs`, `src/regression_mod.rs`
- Impact: Unnecessary memory allocations and copies slow down high-dimensional operations. With large functional data (n_obs=1000, n_points=10000), this becomes measurable overhead.
- Fix approach: Profile hot paths with flamegraph; identify where references could replace clones (esp. in array→Vec conversions). Consider a zero-copy conversion wrapper using numpy's `readonly` mode where feasible. Target 30-40% reduction in clones in critical paths.

**Suppressed clippy warnings at crate root**
- Issue: `src/lib.rs` uses `#![allow(clippy::too_many_arguments)]` and `#![allow(clippy::type_complexity)]` globally. This masks legitimate design issues: functions with >7 arguments are often a sign of poor API design; deep type nesting suggests missing abstractions.
- Files: `src/lib.rs:3-4`
- Impact: Makes it harder to identify functions that should be refactored. New contributors may add more overloaded functions without questioning the pattern.
- Fix approach: Move suppression to individual `#[allow(...)]` attributes on specific functions (those inherently needing many args to wrap fdars-core). Add a design review: any function with >8 params should have a comment explaining why it can't be grouped into a struct.

## Known Bugs

**2D plotting not yet implemented**
- Symptoms: Calling `plot.plot_fdata(fd)` on 2-D surface data raises `NotImplementedError: fdars.plot currently supports 1-D functional data only`.
- Files: `src/python/fdars/plot.py:83-88`
- Trigger: Any call to `plot.plot_fdata()` with `fdata2d=True` Fdata object.
- Workaround: Extract 1-D slices manually and plot individually; or use matplotlib directly on raw arrays.

**NotImplementedError in Fdata 2-D methods**
- Symptoms: `to_basis()` and `to_pc()` methods on 2-D Fdata objects raise `NotImplementedError`.
- Files: `src/python/fdars/fdata_class.py:777, 823`
- Trigger: Calling `fd.to_basis()` or `fd.to_pc()` where `fd.fdata2d == True`.
- Workaround: Reshape 2-D data to 1-D or unfold manually; use low-level functions directly.

**fdars-core dependency version lock**
- Symptoms: If a bug is discovered in fdars-core 0.14.0 (e.g., issue #37 basis_nbasis_cv lambda_ default), users of pyfda stay affected until pyfda itself is rebuilt and released with the new core version.
- Files: `Cargo.toml:18` (currently pinned to `0.14.0` with `features = ["parallel"]`)
- Trigger: Any upstream fix in fdars-core that requires a version bump.
- Workaround: Manual rebuild with `maturin develop` pointing to a patched fdars-core; or wait for next pyfda release.

## Security Considerations

**No input validation on numpy arrays**
- Risk: Many functions accept numpy arrays with no shape or dtype validation. Passing wrong shapes (e.g., 1-D where 2-D is expected) silently fails with cryptic errors deep in Rust code instead of raising a clear ValueError at the entry point.
- Files: All `src/*_mod.rs` files; particularly `src/metric_mod.rs`, `src/depth_mod.rs` (high-volume functions)
- Current mitigation: NumPy's `.readonly` mode prevents in-place corruption; fdars-core error messages propagate (but are not user-friendly).
- Recommendations: Add a validation helper in `convert.rs` that checks shape, dtype, and contiguity; call it at the top of every public function. Example: `fn validate_1d_array(arr: &PyReadonlyArray1, expected_len: Option<usize>) -> PyResult<()>`.

**Unwrap on conversion in fdmatrix_to_numpy2d**
- Risk: `PyArray2::from_vec2()` can fail silently if the row structure is invalid. The `.unwrap()` at line 57 of `convert.rs` will panic, potentially corrupting the Python interpreter state or causing undefined behavior if called from a multithreaded context.
- Files: `src/convert.rs:57`, called by all functions returning 2-D numpy arrays
- Current mitigation: Internal use only; fdars-core guarantees valid matrices, so failure is theoretically impossible.
- Recommendations: Replace with `map_err()` and return `PyResult`. Add a comment explaining the invariant: "FdMatrix shape is always valid; this unwrap is safe because...". Consider a `#[cfg(debug_assertions)]` panic with a helpful message.

## Performance Bottlenecks

**Unavoidable copies in numpy ↔ Rust conversion**
- Problem: Every numpy array passed to a binding must be copied into fdars-core's column-major format (or vice versa). For large data (10,000+ observations), this is measurable (~10-50ms per call).
- Files: `src/convert.rs:29-42` (numpy2d_to_fdmatrix), line 47-58 (fdmatrix_to_numpy2d)
- Cause: NumPy uses row-major (C) order; fdars-core uses column-major (Fortran) order. No way around the transpose.
- Improvement path: 
  1. Document the copy in docstrings so users know to batch operations.
  2. Consider a `fdata_to_native()` function that returns a low-level handle to avoid repeated conversions in loops.
  3. Profile: if a user does 1000 tiny calls in a loop, offer a batched version that loops in Rust.

**Inefficient basis projection with cloning**
- Problem: `fdata_to_basis_1d()` and variants clone entire coefficient matrices and basis data during intermediate steps. For n=500, m=200, n_basis=50, this involves multiple 500×50 matrix copies.
- Files: `src/basis_mod.rs:26-50`, `basis_mod.rs:283-327`, `basis_mod.rs:308-330`
- Cause: Safe Rust forces explicit ownership; fdars-core returns owned data; no direct way to reuse allocations across bindings.
- Improvement path: 
  1. Profile real-world use (growth/tecator datasets).
  2. If bottleneck is confirmed, add a low-level "batch basis projection" binding that accepts a list of datasets.
  3. Consider caching basis functions if the same basis (n_basis, basis_type, argvals) is used repeatedly.

**Alignment functions are O(n²) for large samples**
- Problem: `landmark_detect_and_register()`, elastic changepoint detection, and landmark-based registration scale quadratically in the number of curves due to pairwise similarity/distance computations.
- Files: `src/alignment_mod.rs:1900-2050` (landmark registration), `elastic_changepoint` (line ~235-260)
- Cause: Core fdars-core algorithms; not a binding-level issue.
- Improvement path: Document the quadratic complexity in docstrings. For n>500, recommend downsampling or clustering before full alignment. Explore approximate algorithms (hierarchical, landmark subset).

## Fragile Areas

**Fdata class with optional dependencies**
- Files: `src/python/fdars/fdata_class.py:12-17`
- Why fragile: Optional pandas dependency. If pandas is not installed, `Fdata.metadata` raises `ImportError` at runtime. Many examples assume metadata works; users will hit this unexpectedly.
- Safe modification: 
  1. Either make pandas required (add to `pyproject.toml` dependencies, not optional), or
  2. Add a factory function `fdata_with_metadata()` that checks for pandas and returns an error early.
  3. Test in CI without pandas installed to catch breakage.
- Test coverage: `tests/test_fdata_class.py` tests metadata, but only if pandas is available. Add a `pytest.mark.skipif(not _HAS_PANDAS)` and a separate test for the ImportError case.

**Plot module is a stub for 2-D**
- Files: `src/python/fdars/plot.py`
- Why fragile: Entire 2-D functionality is blocked. Users who read the docs and see `plot.plot_fdata()` will assume it works for 2-D surfaces; it will fail silently at runtime.
- Safe modification: Add a pre-check in `Fdata.__repr__()` or `Fdata.__init__()` that warns users: `"2-D functional data plotting not yet supported; use matplotlib directly."` Add this to CHANGELOG or docs front-and-center.
- Test coverage: Current tests only cover 1-D. Add a test that verifies 2-D raises the expected `NotImplementedError`.

**Results wrapper objects assume fixed dict structure**
- Files: `src/python/fdars/results.py:1-100` (FregreResult, AlignmentResult, etc.)
- Why fragile: Result objects wrap dicts returned by native bindings. If a binding is updated upstream and returns a new key or removes an old one, the result object breaks silently (missing attributes) or breaks noisily (KeyError on access).
- Safe modification: Add a validation step in each result class `__init__()` that checks for required keys before storing. Use `.get()` with defaults for optional keys. Add a test that diffs the dict against an expected schema.
- Test coverage: `tests/test_r_parity.py::TestResults` only tests `.predict()` method; doesn't test all attributes. Add a comprehensive check of `.summary()` output and all expected fields.

**Regression modules with inconsistent parameter names**
- Files: `src/regression_mod.rs:fregre_np_cv` (line 152-173), `fregre_np_mixed` (line 174-205)
- Why fragile: Mix of parameter naming: `n_folds` vs `max_iter`, `h_func` vs `h_response`. No consistent prefix or convention. If new functions are added, the pattern is unclear.
- Safe modification: Add a naming guide to docs: all cross-validation uses `n_folds`, all optimization uses `max_iter` or `tol`, all bandwidth uses `h_*`. Add linting to catch new violations (or just document the legacy inconsistency).
- Test coverage: Tests pass; but no test for parameter alias handling or defaults.

## Scaling Limits

**Python bindings limited to 1D and 2D functional data**
- Current capacity: 1-D curves (n_obs, n_points) and 2-D surfaces (n_obs, dim1, dim2). No 3-D or higher-dimensional support.
- Limit: Architectural assumption in `Fdata` class and all plotting/conversion logic assumes ≤2 dimensions.
- Scaling path: 
  1. Generalize `Fdata` to `.fdata_shape` tuple; store data as (n_obs, *fdata_shape).
  2. Extend all functions to accept variable-dimensional argvals tuple.
  3. Update bindings incrementally (depth, metric, alignment).
  4. Note: fdars-core likely already supports this; just needs Python wrappers.

**NumPy memory limits on large coefficient matrices**
- Current capacity: Basis projection on n=1000, m=500 with n_basis=100 → 100KB coefficient matrix (manageable).
- Limit: n=100,000, m=5000, n_basis=500 → 250MB matrix. Beyond this, memory pressure on a laptop.
- Scaling path: Add batching: `fdata_to_basis_batch(data_list)` that projects each Fdata separately and returns a list, avoiding a single giant matrix. Or add a generator mode that yields coefficients in chunks.

**Parallel feature only in fdars-core; no control from Python**
- Current capacity: fdars-core compiled with `features = ["parallel"]` uses rayon for parallelism. No way to control thread count or disable it from Python.
- Limit: In multithreaded Python environments (e.g., Jupyter with asyncio), oversubscription is possible (e.g., 4 Python threads × 4 rayon threads = 16 OS threads fighting for 8 cores).
- Scaling path: 
  1. Expose `rayon::ThreadPoolBuilder` config to Python (e.g., `fdars.set_num_threads(n)`).
  2. Or add a `parallel=True/False` argument to compute-heavy functions.
  3. Document the default behavior and trade-offs.

## Dependencies at Risk

**fdars-core 0.14.0 – fixed version, no patch stream**
- Risk: Core library is pinned to 0.14.0. If a security issue or correctness bug is found (e.g., issue #37 lambda_ default), pyfda users are stuck until a new version is released and used.
- Impact: Breaking bugs like #33 (recon) and #34 (gauss_model) forced immediate pyfda rebuild and re-release.
- Migration plan: 
  1. Consider `fdars-core = "0.14"` to allow patch updates (0.14.1, 0.14.2) automatically.
  2. Or: Set up a policy to release pyfda updates within 48 hours of fdars-core patches.
  3. Monitor fdars-core changelog and GH issues; create alerts for "Breaking" or "Security" tags.

**PyO3 0.28 – will age out**
- Risk: PyO3 0.28 released in early 2024; new versions will deprecate old APIs. Upgrading to 0.29+ may require code changes in all bindings.
- Impact: Security fixes in PyO3 (e.g., GIL handling) may not backport to 0.28 indefinitely.
- Migration plan: 
  1. Add a note to Cargo.toml: "Monitor PyO3 releases; plan upgrade to 0.29 every 12 months."
  2. Run CI against latest PyO3 on a separate branch to detect breakage early.
  3. Test cross-version compatibility (0.28 to 0.29) on a sample of bindings before full upgrade.

**NumPy 0.28 binding version pinned**
- Risk: NumPy 0.28 (numpy crate) bindings may not support NumPy 2.0+ arrays without code changes.
- Impact: Users with NumPy 2.x installed may see import errors or segfaults.
- Migration plan: Test pyfda with `numpy>=2.0` in CI. If breakage occurs, either update the binding version or add a constraint `numpy<2.0` to `pyproject.toml`.

## Missing Critical Features

**2-D functional data (surfaces) support is incomplete**
- Problem: `Fdata` supports 2-D storage and basic operations (mean, norm, deriv), but plotting, basis projection, and method-style access (`.to_basis()`, `.to_pc()`) are not implemented.
- Blocks: Users cannot perform FPCA or basis regression on 2-D surfaces via the high-level API. Must use low-level functions with raw numpy arrays.
- Priority: Medium (Phase 2 of R-parity plan includes this; not yet completed).

**Irregular functional data (sparsely observed curves)**
- Problem: No support for Fdata with missing or irregular observation points (e.g., growth measurements at different ages per child).
- Blocks: Users with real-world longitudinal data (medical, ecological) cannot use the library.
- Priority: High (Phase 2 of R-parity plan; blocked by need for `IrregFdata` container and interpolation logic).

**Functional mixed models**
- Problem: No bindings for `fdars_core::famm` (functional mixed models with random effects).
- Blocks: Users cannot model hierarchical functional data (e.g., curves nested in groups).
- Priority: High (Phase 2 of R-parity plan).

**Statistical testing module (fdars.tests)**
- Problem: R has `flm.test`, `fmean.test`, `group.test`, `fmm.test_fixed` for hypothesis testing. Python has none.
- Blocks: Users cannot perform formal statistical inference on functional parameters.
- Priority: Medium (Phase 3 of R-parity plan; mostly bindings + pure-Python wrappers).

## Test Coverage Gaps

**Untested edge cases in conversions**
- What's not tested: 
  - Empty matrices (0 observations, 0 points)
  - Single-row or single-column matrices
  - Very large matrices (memory limits)
  - Non-contiguous numpy arrays (C vs F order)
- Files: `src/convert.rs` functions called from all bindings
- Risk: Silent corruption or panics in production on edge cases.
- Priority: High

**2-D functionality untested beyond basic creation**
- What's not tested: 2-D derivatives, 2-D depth, 2-D alignment, 2-D clustering.
- Files: `tests/test_fdata_class.py` and `tests/test_r_parity.py` only test 1-D or basic 2-D construction.
- Risk: 2-D features may be completely broken and no one knows.
- Priority: Medium (lower because 2-D is not heavily used yet)

**No stress tests for large-scale data**
- What's not tested: 
  - n=10,000 curves (typical for medical studies)
  - n_points=100,000 (high-resolution time series)
  - Memory pressure and OOM behavior
- Files: All test files assume small data (n<500, m<500)
- Risk: Performance issues discovered in production; OOM crashes instead of graceful degradation.
- Priority: Medium

**Multithread safety not tested**
- What's not tested: Calling fdars functions concurrently from multiple Python threads (release GIL).
- Files: All bindings; relies on fdars-core being thread-safe.
- Risk: Race conditions or data corruption if fdars-core is not truly thread-safe.
- Priority: Low (low probability, but high impact)

**Optional dependency behavior untested**
- What's not tested: matplotlib not installed (plot should skip gracefully); pandas not installed (metadata should raise clear error).
- Files: `src/python/fdars/plot.py`, `fdata_class.py`
- Risk: Users hit `ImportError` with cryptic traceback instead of clear message.
- Priority: Medium

---

*Concerns audit: 2026-08-07*
