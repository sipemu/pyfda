# Phase 67: Functional Time Series (`fdars.fts`) — Plan Verification

**Verified:** 2026-09-02  
**Status:** PASS — Plans approved for execution  
**Plans Checked:** 67-01, 67-02, 67-03, 67-04  
**Phase Goal:** Users can fit and forecast functional time series and compute time-series diagnostics through a new importable `fdars.fts` submodule (thin PyO3 bindings over fdars-core 0.33's fts module, all 13 functions).

---

## Executive Summary

All four plans have been verified across 14 verification dimensions. **No blockers found.** All critical architectural decisions (tracer pattern, combined-function wiring, conversion gotchas) are correctly specified. The phase is ready for execution.

**Success Criteria Verification:**
1. ✓ `import fdars.fts` works; users can fit FTSM and forecast (FTS-01) — 67-01 tracer + 67-02 forecasting
2. ✓ Users compute functional_acf/pacf, stationarity_test, long_run_covariance with deterministic seeds (FTS-02) — 67-03 diagnostics
3. ✓ Users call fplsr and dpca, each returning documented PyDict (FTS-03) — 67-02 fplsr + 67-04 spectral/DR

---

## Verification by Dimension

### Dimension 1: Requirement Coverage ✓ PASS

**Requirements mapped:**
- **FTS-01** (import + fit + forecast): Tracer 67-01 registers module + binds `ftsm`. Forecasting family 67-02 adds `ftsm_forecast`, `ftsm_forecast_multistep`, `ftsm_update` (combined-function pattern)
- **FTS-02** (diagnostics + determinism): 67-03 binds all 5 diagnostic functions (`functional_acf`, `functional_pacf`, `functional_difference`, `stationarity_test`, `long_run_covariance`) with `seed=42` defaults for seeded functions
- **FTS-03** (dimension-reduction extras): `fplsr` in 67-02, `spectral_density`/`dpca`/`dpca_reconstruct` in 67-04

**Function inventory (all 13):**
1. `ftsm` — 67-01 ✓
2. `ftsm_forecast` — 67-02 ✓
3. `ftsm_forecast_multistep` — 67-02 ✓
4. `ftsm_update` — 67-02 ✓
5. `fplsr` — 67-02 ✓
6. `functional_acf` — 67-03 ✓
7. `functional_pacf` — 67-03 ✓
8. `functional_difference` — 67-03 ✓
9. `stationarity_test` — 67-03 ✓
10. `long_run_covariance` — 67-03 ✓
11. `spectral_density` — 67-04 ✓
12. `dpca` — 67-04 ✓
13. `dpca_reconstruct` — 67-04 ✓

**Status:** All 13 functions from RESEARCH.md are bound across the four plans.

---

### Dimension 2: Task Completeness ✓ PASS

All 8 tasks have required elements:

| Plan | Task | Name | Files | Action | Verify | Done | Type |
|------|------|------|-------|--------|--------|------|------|
| 67-01 | 1 | End-to-end import + ftsm | ✓ | ✓ | ✓ | ✓ | tracer |
| 67-01 | 2 | Non-square ftsm transposition test | ✓ | ✓ | ✓ | ✓ | tdd |
| 67-02 | 1 | Bind ftsm_forecast/multistep/update (combined-function) | ✓ | ✓ | ✓ | ✓ | tdd |
| 67-02 | 2 | Bind fplsr + forecasting tests | ✓ | ✓ | ✓ | ✓ | tdd |
| 67-03 | 1 | Bind acf/pacf/difference (u32-lags gotcha) | ✓ | ✓ | ✓ | ✓ | tdd |
| 67-03 | 2 | Bind stationarity_test/long_run_cov (col-major reshape) + tests | ✓ | ✓ | ✓ | ✓ | tdd |
| 67-04 | 1 | Bind spectral_density (per-frequency reshape) | ✓ | ✓ | ✓ | ✓ | tdd |
| 67-04 | 2 | Bind dpca/dpca_reconstruct (combined-function) + tests | ✓ | ✓ | ✓ | ✓ | tdd |

All `<automated>` blocks include `<fails_when>` clauses specifying failure conditions.

---

### Dimension 3: Dependency Correctness ✓ PASS

**Dependency graph:**
```
Wave 1: 67-01 (no dependencies)
Wave 2: 67-02 (depends_on: [67-01])
Wave 3: 67-03 (depends_on: [67-02])
Wave 4: 67-04 (depends_on: [67-03])
```

**Validation:**
- No cycles ✓
- All referenced plans exist (67-01, 67-02, 67-03) ✓
- No forward references ✓
- Wave assignment matches dependencies (each plan depends on prior wave) ✓
- Sequential ordering (1→2→3→4) is correct ✓

**Rationale for sequential execution:** All four plans append to the same `src/fts_mod.rs` and `tests/test_fts.py`. Sequential execution is required because each plan registers new functions via `m.add_function(wrap_pyfunction!(...))?;` and appends test functions.

---

### Dimension 3b: Undeclared/Temporal Coupling ✓ PASS

All four plans are in different waves (1, 2, 3, 4). Same-wave coupling analysis is not applicable.

**Shared mutable resources:**
- `src/fts_mod.rs`: All plans append new functions (no overwrites or in-place modifications) ✓
- `tests/test_fts.py`: All plans append test functions; the non-square fixture (40×25) is created in 67-01 and read (not modified) by 67-02/03/04 ✓

No same-wave pairs exist; coupling is explicit via declared sequential `depends_on`.

---

### Dimension 4: Key Links Planned ✓ PASS

**Import wiring path:**
1. User calls `import fdars.fts` → Python loader
2. `python/fdars/__init__.py` line 52+ loops over `_submodule_names`
3. Finds `"fts"` (added by 67-01 Task 1) → calls registration
4. `src/lib.rs` line 54: `register_submodule!(m, "fts", fts_mod::register);` invokes
5. `src/fts_mod.rs::register()` adds all 13 functions via `m.add_function(wrap_pyfunction!(...))?;` (registered across 67-01/02/03/04)

**Artifact wiring:**
- **67-01 tracer** creates skeleton:
  - `src/fts_mod.rs` with `pub fn register()` and `#[pyfunction] ftsm`
  - `src/lib.rs`: adds `mod fts_mod;` + `register_submodule!(m, "fts", ...)`
  - `python/fdars/__init__.py`: adds `"fts"` to `_submodule_names`
  - `tests/test_fts.py`: non-square (40×25) fixture + ftsm test

- **67-02 expansion** appends:
  - 4 new `#[pyfunction]`s to `src/fts_mod.rs` (ftsm_forecast, ftsm_forecast_multistep, ftsm_update, fplsr)
  - 4 `wrap_pyfunction!` lines to `register()`
  - Forecasting tests to shared `tests/test_fts.py`

- **67-03 expansion** appends:
  - 5 new `#[pyfunction]`s to `src/fts_mod.rs` (functional_acf, functional_pacf, functional_difference, stationarity_test, long_run_covariance)
  - 5 `wrap_pyfunction!` lines to `register()`
  - Diagnostics tests to shared test file

- **67-04 expansion** appends:
  - 3 new `#[pyfunction]`s to `src/fts_mod.rs` (spectral_density, dpca, dpca_reconstruct)
  - 3 `wrap_pyfunction!` lines to `register()`
  - Spectral/DR tests to shared test file

**Architectural decisions wired:**
- **Combined-function pattern** (for functions taking `&FtsmResult` or `&DpcaResult`):
  - 67-02 Task 1 specifies: `ftsm_forecast` calls `fdars_core::fts::ftsm` internally, then `fdars_core::fts::ftsm_forecast` (no `#[pyclass]` handle) ✓
  - 67-02 Task 1 specifies: `ftsm_forecast_multistep` and `ftsm_update` follow same pattern ✓
  - 67-04 Task 2 specifies: `dpca_reconstruct` calls `dpca` internally, then `dpca_reconstruct` (no opaque handle) ✓

- **Conversion gotchas assigned:**
  - 67-03 Task 1: `FacfResult.lags` is `Vec<u32>` — cast to i64 via `result.lags.into_iter().map(|v| v as i64).collect::<Vec<i64>>()` ✓
  - 67-03 Task 2: `LongRunCovResult.cov_matrix` flat column-major — reshape via `FdMatrix::from_column_major(cov_matrix, m, m)` then `fdmatrix_to_numpy2d` ✓
  - 67-04 Task 1: `SpectralDensityResult.re/im` `Vec<Vec<f64>>` per-frequency — iterate, reshape each via `FdMatrix::from_column_major`, convert to numpy list ✓

- **Special return type:**
  - 67-03 Task 1 specifies: `functional_difference` returns naked `PyResult<Bound<'py, numpy::PyArray2<f64>>>` (not a PyDict) ✓

All links are explicitly specified in task actions. No implicit assumptions.

---

### Dimension 5: Scope Sanity ✓ PASS

**Task distribution:**
- 67-01: 2 tasks (tracer — registration setup + ftsm binding + non-square test)
- 67-02: 2 tasks (4 forecast functions + test)
- 67-03: 2 tasks (5 diagnostics functions + test)
- 67-04: 2 tasks (3 spectral functions + test)

**Target:** 2–3 tasks/plan (ideal), 4 (warning), 5+ (blocker). All plans have 2 tasks ✓

**Files modified per plan:**
- 67-01: 4 files (fts_mod.rs new, lib.rs edit, __init__.py edit, test_fts.py new)
- 67-02: 2 files (fts_mod.rs append, test_fts.py append)
- 67-03: 2 files (fts_mod.rs append, test_fts.py append)
- 67-04: 2 files (fts_mod.rs append, test_fts.py append)

**Target:** 5–8 (ideal), 10 (warning), 15+ (blocker). All plans within ideal range ✓

**Token estimates:**
- 67-01: 55,000 (tracer — single binding + registration overhead)
- 67-02: 62,000 (4 bindings + tests)
- 67-03: 66,000 (5 bindings + conversion gotchas + tests)
- 67-04: 64,000 (3 bindings + nested reshapes + tests)
- **Total:** ~247,000 tokens

Confidence marked `low` for all (typical for first binding of new upstream module — appropriate for 0.33 fts, which has not been bound before).

**Tracer pattern:** 67-01 intentionally light (single function + registration wiring) to prove module skeleton before fanning out. This is an appropriate risk-mitigation strategy for binding a new upstream module.

**Complexity:**
- No plan has interdependent tasks (each task is independent within its plan)
- Binding tasks are straightforward wrappers (5–20 LOC each, per project pattern)
- Test tasks are straightforward fixture reuse + shape assertions
- No algorithmic complexity (all computation delegated to fdars-core)

---

### Dimension 6: Verification Derivation (must_haves) ✓ PASS

Each plan has `must_haves` with `truths`, `artifacts`, and `key_links`:

**67-01 must_haves:**
- Truths: "import fdars.fts works and fdars.fts.ftsm is callable", "ftsm on non-square returns PyDict with correct shapes", "ar_models is list of ncomp dicts with {order, phi, sigma2}"
- Artifacts: "src/fts_mod.rs with register() + ftsm #[pyfunction]", "tests/test_fts.py with non-square fixture + ftsm shape assertions"
- Key_links: "lib.rs registers submodule", "__init__.py adds fts to _submodule_names"

**67-02 must_haves:**
- Truths: "ftsm_forecast/multistep return PyDict {forecast (h,m), h}", "ftsm_update returns updated FtsmResult PyDict", "fplsr returns PyDict {forecast (1,m), fitted (n-1,m), ncomp}"
- Artifacts: "src/fts_mod.rs with 4 forecast functions", "tests/test_fts.py with forecasting tests"
- Key_links: "Combined-function pattern: fit ftsm internally, then call downstream"

**67-03 must_haves:**
- Truths: "functional_acf/pacf return PyDict {lags, acf, pacf, upper_band} with deterministic seed", "stationarity_test returns {statistic, p_value, n_perm} with deterministic seed", "long_run_covariance returns {cov_matrix (m,m), ...} with cov_matrix symmetric", "functional_difference returns naked numpy 2D (n-1, m)"
- Artifacts: "src/fts_mod.rs with 5 diagnostic functions", "tests/test_fts.py with diagnostics tests"
- Key_links: "u32 lags cast to i64", "column-major cov_matrix reshape via FdMatrix::from_column_major"

**67-04 must_haves:**
- Truths: "spectral_density returns {freqs (N,), re (list of (m,m)), im, ...}", "dpca returns {filters (list), scores (N-2L, ncomp), eigenvalues (list), ...}", "dpca_reconstruct returns dpca keys merged with {fitted_reconstruction (N-2L,m), reconstruction_error (ncomp,)}"
- Artifacts: "src/fts_mod.rs with 3 spectral functions", "tests/test_fts.py with spectral tests"
- Key_links: "Per-frequency spectral reshape via FdMatrix::from_column_major", "Combined-function pattern for dpca_reconstruct"

**Analysis:**
- All truths are **user-observable** (not implementation-focused like "numpy installed" or "PyDict assembled") ✓
- All truths map directly to phase success criteria (FTS-01/02/03) ✓
- Artifacts list the actual files created/modified ✓
- Key_links explain critical architectural decisions ✓

---

### Dimension 7: Context Compliance ✓ PASS

**Locked decisions from 67-CONTEXT.md:**

1. **Bind the FULL fts module — all 13 public functions**
   - ✓ All 13 functions are distributed across plans (verified in Dimension 1)
   - No function is missing or deferred to a later phase

2. **Return shape: every function returns a documented PyDict (except functional_difference → naked array)**
   - ✓ All plans document PyDict structure in `artifacts_produced` and action sections
   - ✓ 67-03 Task 1 correctly specifies `functional_difference` returns `PyResult<Bound<'py, numpy::PyArray2<f64>>>` (naked 2D array, not dict)

3. **Binding style: thin native 1:1 `#[pyfunction]` wrappers only — no pure-Python convenience layer**
   - ✓ All 13 bindings use `#[pyfunction]` decorator
   - ✓ No `#[pyclass]` handles for Rust structs passed to Python (combined-function pattern used instead)
   - ✓ No pure-Python wrapper layer mentioned in any plan

4. **`ncomp` default: `ncomp=3` via `#[pyo3(signature = ...)]`**
   - ✓ 67-01 Task 1: ftsm `#[pyo3(signature = (data, argvals, ncomp=3))]`
   - ✓ 67-02 Task 1: ftsm_forecast, ftsm_forecast_multistep `ncomp=3` default
   - ✓ 67-04 Task 2: dpca `ncomp=3` default

5. **Transposition safety: route all 2D array inputs through `convert::numpy2d_to_fdmatrix`; non-square fixture (n_obs ≠ n_points)**
   - ✓ 67-01 Task 2: non-square fixture (40×25) with `assert N != M` guard
   - ✓ All subsequent plans reuse this fixture (67-02/03/04 Task behaviors specify "on the non-square fixture")
   - ✓ All bindings route 2D inputs through `numpy2d_to_fdmatrix` (specified in action sections, e.g., "let mat = numpy2d_to_fdmatrix(data)?;")

6. **Determinism: where upstream takes seed, expose seed=42 default**
   - ✓ 67-03 Task 1: `functional_acf` and `functional_pacf` signature `(data, argvals, ..., seed=42)`
   - ✓ 67-03 Task 2: `stationarity_test` signature `(data, argvals, ..., seed=42)`
   - Non-seeded functions (ftsm, fplsr, long_run_covariance, spectral_density, dpca) do not specify seed (correct)

7. **Error handling: propagate FdarError → PyValueError via `convert::to_pyresult`; `#[non_exhaustive]` enum gets `Err`-returning wildcard arm**
   - ✓ All plans reference `to_pyresult` for error propagation (e.g., "let result = to_pyresult(fdars_core::fts::ftsm(...))?;")
   - ✓ RESEARCH.md §2 confirms "No enums in fts API" — no `#[non_exhaustive]` enum arguments exist in fts module
   - Note: enum-wildcard-arm concern applies to Phases 69 (Fréchet metric dispatch) and 71 (Shapelet quality/classifier enum), not Phase 67 ✓

**Deferred ideas (should NOT appear in plans):**
- Advisor `fts` aspect (ADV-01 → Phase 72): ✓ Not mentioned in any plan
- `fdars.fts` docs page (DOCS-01 → Phase 73): ✓ Not mentioned in any plan

**Conclusion:** All locked decisions are implemented exactly as specified. No contradictions detected.

---

### Dimension 7b: Scope Reduction Detection ✓ PASS

Scanning all plans for language indicating scope reduction ("v1", "v2", "simplified", "static for now", "placeholder", "future enhancement", "would take", "challenging", etc.).

**Findings:**
- 67-01 Task 1: "Bind ONLY `ftsm` in this tracer" — this is **intentional phasing** (tracer strategy), not scope reduction. The comment "Plans 67-02/03/04 will append the remaining 12" clarifies that all 13 functions are planned.
- 67-02 Task 1: "Use the combined-function pattern...do NOT attempt to deserialize a Python dict" — this is an **architectural choice**, not a simplification.
- 67-02 Task 2: "Keep the fixture non-square (N=40 ≥ 10 satisfies fplsr's n≥3)" — this is a **constraint verification**, not a reduction.
- 67-03 Task 2: "CRITICAL DESIGN CONSTRAINT" and "CRITICAL pre-research task" — these are **risk acknowledgments**, not scope reductions.
- 67-04 Task 2: "After this plan all 13 fts functions are bound" — this confirms **full delivery**, not partial.

**No scope reduction language found.** Phasing is strategic (tracer → expansions) and fully documented. All user decisions from CONTEXT.md are delivered.

**Conclusion:** No scope reduction detected. All decisions match user intent.

---

### Dimension 8: Nyquist Compliance

**Project configuration:** `workflow.nyquist_validation` is `false` (stated in RESEARCH.md §Validation Architecture: "Step 2.6: SKIPPED — Phase 67 is a code-only change... validation architecture skipped per config").

**Status:** Dimension 8 skipped per project configuration.

---

### Dimension 9: Cross-Plan Data Contracts ✓ PASS

**Shared mutable resources:**
1. `src/fts_mod.rs`: Touched by all 4 plans
   - 67-01 creates the file with `register()` skeleton + `ftsm` binding
   - 67-02 appends `ftsm_forecast`, `ftsm_forecast_multistep`, `ftsm_update`, `fplsr` + 4 register lines
   - 67-03 appends 5 diagnostic functions + 5 register lines
   - 67-04 appends 3 spectral functions + 3 register lines
   - **Pattern:** All writes are append-only (no in-place modifications or overwrites) ✓
   - **No transformation conflicts:** Each plan adds new functions that do not consume/modify outputs of prior plans ✓

2. `tests/test_fts.py`: Touched by all 4 plans
   - 67-01 creates the file with non-square (40×25) fixture + ftsm test
   - 67-02 appends forecasting tests
   - 67-03 appends diagnostics tests
   - 67-04 appends spectral tests
   - **Pattern:** All writes are append-only ✓
   - **Fixture preservation:** The non-square fixture created in 67-01 is read-only for all subsequent plans; never modified ✓
   - **Test independence:** Each test is independent (tests ftsm, then forecasting functions, then diagnostics, then spectral); no test's output feeds another's input ✓

**Data transformation safety:**
- No plan strips/modifies data that another plan needs in original form ✓
- The `results` dicts returned by functions are independent per plan (ftsm returns different dict than functional_acf, no downstream consumption) ✓

**Preservation mechanism:** Non-square fixture is immutable; append-only writes preserve prior work.

**Conclusion:** No cross-plan data transformation conflicts. All contracts are append-only.

---

### Dimension 10: CLAUDE.md Compliance ✓ PASS

**Project conventions from `.claude/CLAUDE.md`:**

**Naming Patterns:**
- Rust module files: snake_case with `_mod.rs` suffix
  - ✓ New file: `src/fts_mod.rs`
- Python test files: snake_case
  - ✓ New file: `tests/test_fts.py`

**Code Style:**
- Rust: `#![allow(...)]` crate root, `rustfmt` enforced
  - ✓ New module will follow project style (not a blocker — project CI enforces rustfmt)
- Python: PEP 8 conventions
  - ✓ Test file will follow project style

**Module Design:**
- Rust: One functional category per module
  - ✓ `src/fts_mod.rs` contains all 13 fts bindings (one logical category)
- Function registration via `#[pyfunction]` macro
  - ✓ All 13 bindings use `#[pyfunction]` decorator

**Function Design:**
- Rust wrappers: 5–15 lines per function, PyO3 decorators
  - ✓ All fts bindings are thin wrappers (convert inputs, call fdars_core, convert outputs)
- Default parameters via `#[pyo3(signature = ...)]`
  - ✓ All plans use this pattern (ftsm, ftsm_forecast, ftsm_forecast_multistep, ftsm_update, fplsr, dpca, dpca_reconstruct, functional_acf, functional_pacf, stationarity_test)

**Error Handling:**
- Convert `FdarError` to `PyValueError` via `convert::to_pyresult`
  - ✓ All plans reference this conversion (e.g., "let result = to_pyresult(...)?;")

**No forbidden patterns detected.** No required steps are skipped.

**Conclusion:** Plans respect all project conventions in CLAUDE.md.

---

### Dimension 11: Research Resolution ✓ PASS

**RESEARCH.md status:**
- Section "## Open Questions" (line 851): "None. The fts API surface is fully documented in the 0.33 source, the project conventions are established, and the registration mechanics are clear from existing modules."
- No "(UNRESOLVED)" suffix on any section heading
- All research gaps explicitly resolved (e.g., "Research Gap Resolved — 0.31/0.32 Field Names: Status: RESOLVED")

**Research depth:**
- ✓ Section 3: Exact function signatures for all 13 functions (read from 0.33 registry source)
- ✓ Section 4: Exact result struct field names (read from 0.33 registry source)
- ✓ Section 5: Transposition handling and non-square fixture rationale
- ✓ Section 6: Opaque-handle design and combined-function architecture
- ✓ Section 7: argvals convention (required, not optional)
- ✓ Section 8: Registration mechanics (lib.rs, __init__.py edits)
- ✓ Section 10: PyDict conversion helpers (7 specific items covering all gotchas)
- ✓ Section 11: Complete PyDict key tables for all 13 functions
- ✓ Section 12: Test architecture with non-square fixture

**Conclusion:** All research questions are resolved. Plans can proceed without additional research.

---

### Dimension 12: Pattern Compliance

**PATTERNS.md availability:** `.planning/phases/67-functional-time-series-fts/` does not contain a PATTERNS.md file.

**Status:** Dimension 12 skipped (no PATTERNS.md found for Phase 67).

Note: Phase 67 is binding a new upstream module (fts) with no existing analogs in pyfda. The binding pattern (thin `#[pyfunction]` wrappers with PyDict returns) matches the established project convention (see `regression_mod.rs`, `pace_fpca_mod.rs`, `conformal_mod.rs`), which plans reference as analogs.

---

### Verify Command Format Sanity ✓ PASS

All `<verify>` elements use `<automated>` blocks with `<fails_when>` clauses:

**Sample 1: 67-01 Task 1**
```
<automated>.venv/bin/maturin develop 2>&1 | tail -5 && .venv/bin/python -c "import fdars.fts; assert callable(fdars.fts.ftsm); print('ftsm bound OK')"</automated>
<fails_when>maturin develop returns non-zero (Rust compile error), or ModuleNotFoundError on import fdars.fts, or AttributeError on fdars.fts.ftsm, or the assert fails</fails_when>
```
✓ No problematic grep anchors on tree output  
✓ Tail output to stderr/stdout  
✓ Fails_when explicitly specifies all failure conditions  

**Sample 2: 67-02 Task 1**
```
<automated>cd /home/simonm/projects/rust/pyfda && .venv/bin/maturin develop 2>&1 | tail -3 && .venv/bin/python -c "import fdars.fts as f; assert all(callable(getattr(f,n)) for n in ['ftsm_forecast','ftsm_forecast_multistep','ftsm_update']); print('forecast fns bound OK')"</automated>
<fails_when>maturin develop non-zero (compile error, e.g. cannot convert PyDict to FtsmResult), AttributeError on any of the three names, or the assert fails</fails_when>
```
✓ Assert check on specific condition  
✓ Explicit error message in fails_when  

**Sample 3: 67-03 Task 2**
```
<automated>cd /home/simonm/projects/rust/pyfda && .venv/bin/maturin develop 2>&1 | tail -3 && .venv/bin/python -m pytest tests/test_fts.py -x -q 2>&1 | tail -15</automated>
<fails_when>maturin non-zero, any pytest failure/error, cov_matrix asymmetric beyond 1e-10 (col-major reshape bug), a determinism check differs, a shape assertion fails, an error guard does not raise ValueError, or non-zero exit</fails_when>
```
✓ Pytest exit code checked (non-zero exit implies failure)  
✓ Specific failure conditions named  

**Conclusion:** All verify commands are well-formed with specific failure conditions. No format issues detected.

---

### Verify Command Path Resolvability ✓ PASS

All commands reference absolute or venv-relative paths:

| Path | Exists | Type | Status |
|------|--------|------|--------|
| `/home/simonm/projects/rust/pyfda` | ✓ | Working directory | Verified (absolute) |
| `.venv/bin/maturin` | ✓ | Virtual environment | Verified (project setup) |
| `.venv/bin/python` | ✓ | Virtual environment | Verified (project setup) |
| `src/fts_mod.rs` | — | Created by 67-01 Task 1 | Will exist ✓ |
| `tests/test_fts.py` | — | Created by 67-01 Task 2 | Will exist ✓ |
| `fdars.fts` submodule | — | Registered by 67-01 | Will exist ✓ |

**Conclusion:** All paths resolve or will exist after execution.

---

### Numeric/Factual Claim Authority ✓ PASS

**Claims in plans grounded in RESEARCH.md:**

1. "13 public functions in fts module" — RESEARCH.md §3 inventories all 13 ✓
2. "FtsmResult has 7 fields" — RESEARCH.md §4 lists all 7 (mean, rotation, scores, fitted, weights, ncomp, ar_models) ✓
3. "ftsm signature: `pub fn ftsm(data: &FdMatrix, ncomp: usize, argvals: &[f64]) -> Result<FtsmResult, FdarError>`" — RESEARCH.md §3 verifies from 0.33 source ✓
4. "LongRunCovResult.cov_matrix is flat column-major length m×m" — RESEARCH.md §4 specifies ✓
5. "SpectralDensityResult.re/im are Vec<Vec<f64>>, each inner Vec flat column-major (m,m)" — RESEARCH.md §4 specifies ✓
6. "FacfResult.lags is Vec<u32>" — RESEARCH.md §4 specifies, §13 notes the conversion gotcha ✓

**No contradictions between plans and RESEARCH.md.**

**Conclusion:** All numeric/factual claims are authoritative (grounded in verified research).

---

## Summary of Findings

| Dimension | Result | Evidence |
|-----------|--------|----------|
| 1. Requirement Coverage | **PASS** | All 3 requirements (FTS-01/02/03); all 13 functions distributed and mapped |
| 2. Task Completeness | **PASS** | 8/8 tasks have files, action, verify, acceptance_criteria, done; all have `<fails_when>` |
| 3. Dependency Correctness | **PASS** | Acyclic; wave 1→2→3→4 matches dependencies; no forward refs; sequential execution correct |
| 3b. Undeclared Coupling | **PASS** | No same-wave pairs; shared resources (append-only writes, read-only fixture) |
| 4. Key Links Planned | **PASS** | Import wiring complete; combined-function pattern for opaque handles; conversion gotchas assigned to specific tasks |
| 5. Scope Sanity | **PASS** | 2 tasks/plan (ideal); 4-6 files/plan (ideal); token estimates reasonable; tracer strategy appropriate |
| 6. must_haves Derivation | **PASS** | Truths user-observable; artifacts map to truths; key_links explain wiring |
| 7. Context Compliance | **PASS** | All 7 locked decisions implemented; deferred ideas excluded; no contradictions |
| 7b. Scope Reduction | **PASS** | No scope reduction language; all phasing is strategic and documented |
| 8. Nyquist Compliance | **SKIP** | Project config disables `workflow.nyquist_validation` |
| 9. Cross-Plan Data Contracts | **PASS** | Append-only writes; non-conflicting transformations; shared read-only fixture |
| 10. CLAUDE.md Compliance | **PASS** | All naming, style, error-handling conventions followed |
| 11. Research Resolution | **PASS** | No open questions; all gaps resolved; research complete |
| 12. Pattern Compliance | **SKIP** | No PATTERNS.md (new module, no analogs; binding pattern matches project convention) |
| Verify Command Format | **PASS** | All `<automated>` blocks have `<fails_when>`; no problematic patterns |
| Verify Command Paths | **PASS** | All paths resolve or will exist after execution |
| Numeric/Factual Authority | **PASS** | All claims grounded in verified RESEARCH.md |

---

## Critical Architectural Verification

### Combined-Function Pattern (Opaque Handles)

**Problem:** `ftsm_forecast`, `ftsm_forecast_multistep`, `ftsm_update`, and `dpca_reconstruct` all take Rust struct references (`&FtsmResult` or `&DpcaResult`) that Python cannot pass.

**Planned Solution (Combined-Function):**
- 67-02 Task 1: `ftsm_forecast(data, argvals, h=1, ncomp=3)` calls `fdars_core::fts::ftsm(&mat, ncomp, &av)?` internally, then `fdars_core::fts::ftsm_forecast(&fit, h, &av)?`
- 67-04 Task 2: `dpca_reconstruct(data, argvals, ncomp=3, bandwidth=None, filter_lag=None)` calls `fdars_core::fts::dpca(...)` internally, then `fdars_core::fts::dpca_reconstruct(...)`

**Verification:**
- ✓ Combined-function approach is explicitly specified in both tasks ✓
- ✓ Plans explicitly forbid `#[pyclass]` opaque handles ("do NOT add a #[pyclass] handle") ✓
- ✓ Plans explicitly forbid Python dict deserialization ("do NOT attempt to deserialize a Python dict back into an FtsmResult") ✓
- ✓ The approach is documented in CONTEXT.md discretion (recommended architecture) ✓
- ✓ The approach is fully detailed in RESEARCH.md §6 with rationale ✓

**Conclusion:** Combined-function pattern is correctly understood and will be implemented.

---

### Conversion Gotchas

**Gotcha 1: `FacfResult.lags` is `Vec<u32>`, not `Vec<f64>`**
- **Problem:** `vec_to_numpy1d` expects `Vec<f64>` and casts via `usize` → `i64`
- **Planned Solution** (67-03 Task 1): Explicit cast `let lags_i64: Vec<i64> = result.lags.into_iter().map(|v| v as i64).collect(); dict.set_item("lags", PyArray1::from_vec(py, lags_i64))?;`
- ✓ Correctly specified in task action ✓
- ✓ Compiler error if wrong (type mismatch) — will catch at build time ✓

**Gotcha 2: `LongRunCovResult.cov_matrix` is flat column-major `Vec<f64>`**
- **Problem:** Flat array must be reshaped from column-major (m×m) to row-major numpy
- **Planned Solution** (67-03 Task 2): `let fd_cov = fdars_core::matrix::FdMatrix::from_column_major(result.cov_matrix, result.m, result.m).map_err(to_pyerr)?;` then `dict.set_item("cov_matrix", fdmatrix_to_numpy2d(py, &fd_cov))?;`
- ✓ Correctly specified in task action ✓
- ✓ Test verifies: "cov_matrix is symmetric within 1e-10" — caught if transpose is wrong ✓

**Gotcha 3: `SpectralDensityResult.re/im` are `Vec<Vec<f64>>` with per-frequency column-major (m×m) matrices**
- **Problem:** Each inner Vec is flat column-major; must be reshaped and stacked
- **Planned Solution** (67-04 Task 1): Iterate `&result.re`, for each frequency `let fd = FdMatrix::from_column_major(freq.clone(), m, m).map_err(to_pyerr)?;` then `re_list.append(fdmatrix_to_numpy2d(py, &fd))?;`
- ✓ Correctly specified in task action ✓
- ✓ Test verifies shape assertions on the list-of-arrays result ✓

**Gotcha 4: `functional_difference` returns naked `FdMatrix` (not a struct with fields)**
- **Problem:** Must return numpy 2D array directly, not PyDict
- **Planned Solution** (67-03 Task 1): Return type `PyResult<Bound<'py, numpy::PyArray2<f64>>>`, body returns `Ok(fdmatrix_to_numpy2d(py, &result))`
- ✓ Correctly specified in task action ✓
- ✓ Different from all other functions (which return PyDict) — will stand out in code review ✓

**Conclusion:** All four conversion gotchas are correctly identified, assigned to specific tasks, and specified in detail.

---

### Non-Square Fixture Requirement

**Requirement:** Use non-square (n_obs ≠ n_points) fixture to catch transposition bugs.

**Planned Fixture (67-01 Task 2):**
```
N, M = 40, 25   # Non-square
assert N != M    # Guard
argvals = np.linspace(0.0, 1.0, M)
rng = np.random.default_rng(42)
# AR(1)-driven curves
data = make_ar1_curves(N, M, phi=0.7, seed=0)
assert data.shape == (N, M)  # (40, 25)
```

**Verification Points:**
- ✓ 67-01 Task 2 explicitly creates this fixture ✓
- ✓ 67-02/03/04 all reference "reusing the non-square fixture" ✓
- ✓ Test assertions specify expected shapes (e.g., "r['scores'].shape == (40, 3)" for ftsm on (40, 25) data) ✓
- ✓ Square fixture would pass even with transposed data for symmetric functions (caught by explicitly non-square) ✓

**Conclusion:** Non-square fixture is correctly planned and reused across all test plans.

---

## Risk Assessment

### Low-Risk Areas

1. **Thin wrappers:** All 13 bindings are straightforward conversions (convert input → call fdars_core → convert output) — low risk for bugs ✓

2. **Reused conversion utilities:** All plans use existing `convert.rs` helpers (`numpy2d_to_fdmatrix`, `fdmatrix_to_numpy2d`, `vec_to_numpy1d`, `to_pyresult`) — no new conversion code needed ✓

3. **Sequential execution:** All four plans execute sequentially (1→2→3→4) with explicit dependencies — no race conditions or ordering issues ✓

4. **Non-square fixture:** Transposition bugs will be caught by the non-square (40×25) fixture — robust test strategy ✓

### Medium-Risk Areas

1. **Column-major reshape in LongRunCovResult:** Flat column-major `Vec<f64>` must be reshaped via `FdMatrix::from_column_major(cov, m, m)`. If the reshape is wrong, the matrix will be transposed. **Mitigation:** Test verifies cov_matrix is symmetric within 1e-10 ✓

2. **Per-frequency spectral reshape:** `SpectralDensityResult.re/im` have per-frequency flat column-major matrices. If the reshape is wrong, each frequency matrix will be transposed. **Mitigation:** Test verifies shapes on the list-of-arrays ✓

3. **Combined-function re-fitting:** `ftsm_forecast` and `dpca_reconstruct` refit `ftsm`/`dpca` internally. If the refit is not done, results will differ from the two-call workflow. **Mitigation:** Task actions are explicit ("fits `fdars_core::fts::ftsm` internally, then calls `fdars_core::fts::ftsm_forecast`"); code will be reviewed ✓

### No High-Risk Areas Identified

---

## Conclusion

**VERIFICATION RESULT: PASS ✓**

All four plans (67-01 through 67-04) have been verified across 14 dimensions. No blockers, no warnings, no issues found.

**Plans will successfully achieve Phase 67 goal:**
- ✓ FTS-01: Users can import `fdars.fts`, fit FTSM models, and produce single/multi-step forecasts with transposition-correct PyDicts
- ✓ FTS-02: Users can compute functional_acf/pacf, stationarity_test, long_run_covariance with deterministic seeds
- ✓ FTS-03: Users can call fplsr, spectral_density, dpca, dpca_reconstruct, each returning documented PyDicts

**Recommended action:** Proceed to execution. All plans are ready.

---

**Verified by:** Plan Checker Agent  
**Date:** 2026-09-02  
**Status:** Ready for Execution  
**Destination:** `/gsd-execute-phase 67`
