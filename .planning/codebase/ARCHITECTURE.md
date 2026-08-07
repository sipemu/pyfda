<!-- refreshed: 2026-08-07 -->
# Architecture

**Analysis Date:** 2026-08-07

## System Overview

fdars is a Python library for Functional Data Analysis built on a Rust backend. The architecture follows a **hybrid language binding pattern** where computationally intensive operations run in Rust via the `fdars-core` crate, while Python provides the high-level API and convenience wrappers.

```text
┌────────────────────────────────────────────────────────────────┐
│                    Python API Layer                             │
│            `python/fdars/` – High-level interfaces             │
│                                                                 │
│  ┌─────────────────────────┐  ┌──────────────────────────┐    │
│  │  Pure-Python Helpers    │  │   Fdata Container        │    │
│  │  `_augment.py`          │  │   `fdata_class.py`       │    │
│  │  (orchestration)        │  │   (functional data OOP)  │    │
│  └─────────────────────────┘  └──────────────────────────┘    │
│                                                                 │
│  ┌────────────────────────────────────────────────────────┐   │
│  │  High-level Modules: datasets, results, metrics,       │   │
│  │  covariance, plot (Python utilities over native)       │   │
│  └────────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────────┘
                              │
                              │ PyO3 bindings
                              ▼
┌────────────────────────────────────────────────────────────────┐
│              Rust FFI Layer (PyO3 Extension)                    │
│                  `src/` — Module system                         │
│                                                                 │
│  ┌──────────────────────────────────────────────────────┐     │
│  │  Conversion Layer: `convert.rs`                      │     │
│  │  - numpy ↔ FdMatrix/Vec conversions                  │     │
│  │  - Row-major (numpy) ↔ column-major (Rust) layout   │     │
│  │  - Error marshalling (FdarError → PyValueError)     │     │
│  └──────────────────────────────────────────────────────┘     │
│                                                                 │
│  ┌──────────────────────────────────────────────────────┐     │
│  │  Submodule Registration Layer (lib.rs)               │     │
│  │  - 16 submodules + register_submodule! macro         │     │
│  │  - Each module exposes PyO3 @#[pyfunction] wrappers  │     │
│  └──────────────────────────────────────────────────────┘     │
│                                                                 │
│  ┌──────────────────────────────────────────────────────┐     │
│  │  Functional Modules (1:1 with fdars-core)             │     │
│  │  fdata_mod, depth_mod, metric_mod, basis_mod,       │     │
│  │  smoothing_mod, clustering_mod, regression_mod, etc  │     │
│  │  Each: thin PyO3 wrapper around fdars_core::*       │     │
│  └──────────────────────────────────────────────────────┘     │
└────────────────────────────────────────────────────────────────┘
                              │
                              │ Cargo dependency
                              ▼
┌────────────────────────────────────────────────────────────────┐
│              fdars-core (External Crate)                        │
│         github.com/sipemu/fdars (Rust-only compute)            │
│                                                                 │
│  FdMatrix, depth::*, metric::*, basis::*,                      │
│  clustering::*, regression::*, alignment::*, etc.              │
│  + Linear algebra (LAPACK via nalgebra)                        │
│  + Parallel computation (rayon, with "parallel" feature)       │
└────────────────────────────────────────────────────────────────┘
```

## Component Responsibilities

| Component | Responsibility | File |
|-----------|----------------|------|
| **Fdata (OOP container)** | Bundles observation matrix, evaluation grid, IDs, and metadata; provides method wrappers (`mean()`, `depth()`, `distance()`, etc) | `python/fdars/fdata_class.py` |
| **Conversion layer** | Marshals numpy arrays ↔ Rust types; row-major ↔ column-major layout conversion; error handling | `src/convert.rs` |
| **Functional modules** | PyO3-wrapped thin bindings to fdars-core functions (16 modules: fdata, depth, metric, basis, smoothing, clustering, regression, alignment, outliers, seasonal, spm, classification, tolerance, conformal, simulation, explain) | `src/*_mod.rs` (18 files) |
| **Pure-Python helpers** | Orchestration (k-means parameter search), plotting, dataset loading, metrics, covariance | `python/fdars/{_augment,plot,metrics,covariance,datasets}.py` |
| **Module registry** | PyModule initialization and submodule registration via `register_submodule!` macro | `src/lib.rs` |

## Pattern Overview

**Overall:** Two-layer binding model

**Key Characteristics:**
- **Zero-copy data transfer:** NumPy arrays passed directly to Rust (PyReadonly wrappers avoid GIL contention)
- **Thin wrappers, not rearchitecture:** Each Rust module exports PyO3 functions that map directly to fdars-core primitives
- **Python convenience layer:** Fdata OOP class, high-level functions, and orchestration helpers built in pure Python on top of low-level native functions
- **Submodule namespacing:** Both `from fdars.depth import fraiman_muniz_1d` and `fdars.depth.fraiman_muniz_1d()` work via sys.modules injection in `__init__.py`
- **Feature gating:** fdars-core's "parallel" feature enabled at build time; MSRV is Rust 1.83

## Layers

**Python API Layer** (`python/fdars/`):
- Purpose: High-level, idiomatic Python interface; convenience wrappers
- Location: `python/fdars/`
- Contains: Fdata class, orchestration functions, plotting, dataset utilities
- Depends on: `fdars._native` (compiled PyO3 extension), numpy, pandas, matplotlib
- Used by: End users; called from tests and examples

**PyO3 FFI Layer** (`src/`):
- Purpose: Bridge Python ↔ Rust; type marshalling; function registration
- Location: `src/`
- Contains: 18 Rust modules with @#[pyfunction] decorators; conversion utilities
- Depends on: fdars-core, pyo3, numpy (PyO3 bindings)
- Used by: Python API layer (all native calls go through here)

**Rust Compute Layer** (fdars-core crate):
- Purpose: High-performance numerical computation
- Location: External (Cargo.toml dependency: fdars-core 0.14.0)
- Contains: Linear algebra (FdMatrix), algorithms (clustering, depth, regression, etc)
- Depends on: nalgebra, rayon (for parallel flag), specialized numerical libraries
- Used by: PyO3 wrapper layer (every native function calls into fdars-core)

## Data Flow

### Primary Request Path: Functional Data Operation

1. User calls Python API method (e.g., `fd.mean()`) — **entry:** `python/fdars/fdata_class.py:127` (Fdata.mean)
2. Fdata method extracts data matrix and calls native submodule function (e.g., `fdars.fdata.mean_1d()`) — **call:** `python/fdars/fdata_class.py:127`
3. PyO3 function receives numpy array, converts to FdMatrix via `convert::numpy2d_to_fdmatrix()` — **entry:** `src/fdata_mod.rs:19` (pyfunction mean_1d)
4. Call fdars-core primitive (e.g., `fdars_core::fdata::mean_1d(&mat)`) — **delegate:** `src/fdata_mod.rs:24`
5. Rust compute returns Vec<f64>; convert back to numpy via `convert::vec_to_numpy1d()` — **return:** `src/fdata_mod.rs:25`
6. Python wraps result in Fdata (if applicable) or returns raw array

**Code trace example (Fdata.mean):**
```
fd.mean()  [fdata_class.py:127]
  → fdars.fdata.mean_1d(self.data)  [fdata_class.py:128]
    → numpy2d_to_fdmatrix(data) [convert.rs:29]
    → fdars_core::fdata::mean_1d(&mat) [fdata_mod.rs:24]
    → vec_to_numpy1d(py, result) [convert.rs:66]
  ← return numpy 1D array
```

### Secondary Flow: Parameter Search (Pure Python)

**K-means cluster optimization** — orchestration in Python:
1. User calls `fdars.clustering.cluster_optim(data, argvals, k_range)` — **entry:** `python/fdars/_augment.py:16` (_cluster_optim)
2. Loop over k values, call `fdars.clustering.kmeans_fd()` for each k — **call:** `python/fdars/_augment.py:36`
3. Score each fit using silhouette or Calinski-Harabasz (both Rust) — **call:** `python/fdars/_augment.py:39` (silhouette_score_data)
4. Return best k and all scores

**State Management:**
- No persistent state across calls (each call is independent)
- Fdata object holds metadata/IDs but does not cache computed results
- fdars-core returns results; no caching in Rust layer
- Python layer may cache (e.g., `_augment` stores fitted models in return dict)

## Key Abstractions

**FdMatrix (Column-Major 2D Array):**
- Purpose: Unified representation of functional data samples (rows=observations, cols=function evaluations)
- Examples: `src/convert.rs:29` (numpy2d_to_fdmatrix), `src/fdata_mod.rs:23` (receives FdMatrix)
- Pattern: All core algorithms operate on FdMatrix; Python layer converts numpy (row-major) to FdMatrix on entry, back to numpy on exit

**Fdata (Python OOP Container):**
- Purpose: Bundles data, evaluation grid, IDs, and metadata; provides method interface
- Examples: `python/fdars/fdata_class.py:1` (class definition)
- Pattern: `Fdata.__init__` validates and stores; methods delegate to native functions and wrap results

**PyFunction Wrapping (PyO3):**
- Purpose: Expose Rust functions as Python callables with automatic type conversion
- Examples: `src/fdata_mod.rs:18` (#[pyfunction] mean_1d), `src/depth_mod.rs:22` (fraiman_muniz_1d)
- Pattern: 1:1 mapping to fdars-core; parameter validation in wrapper; return PyResult<T>

**Module Registration Macro:**
- Purpose: Reduce boilerplate for submodule creation and registration
- Examples: `src/lib.rs:28` (register_submodule! macro), `src/lib.rs:39-54` (usage)
- Pattern: Each module exposes a `register(m: &Bound<PyModule>) -> PyResult<()>` function that calls `add_function` for each wrapped function

## Entry Points

**Python Entry Point:**
- Location: `python/fdars/__init__.py`
- Triggers: `import fdars` or `from fdars import ...`
- Responsibilities: Load _native (compiled module), register 16 submodules in sys.modules, import pure-Python helpers, inject orchestration functions

**Rust Entry Point (PyO3 Module):**
- Location: `src/lib.rs:37` (#[pymodule] _native)
- Triggers: When Python loads the compiled extension
- Responsibilities: Register all 16 submodules via register_submodule! macro; return PyResult

**User-Facing Entry Points:**
- `Fdata` class constructor: `python/fdars/fdata_class.py:1`
- Direct function calls: `fdars.fdata.mean_1d(X)`, `fdars.depth.fraiman_muniz_1d(data, ref)`, etc.
- High-level orchestration: `fdars.clustering.cluster_optim()`, `fdars.plot.plot_fdata()`, `fdars.datasets.load_canadian_weather()`

## Architectural Constraints

- **Threading:** Rust layer uses rayon for parallelism (fdars-core with "parallel" feature); Python GIL is released in PyO3 PyReadonly wrappers
- **Global state:** None; all functions are pure (no module-level singletons or mutable state)
- **Circular imports:** Python layer avoids circular imports via lazy imports in some modules (e.g., matplotlib in `plot.py` imported only on use)
- **Binary compatibility:** ABI3 stable (Python 3.9+; Cargo.toml specifies abi3-py39)
- **Data layout mismatch:** Conversion required between numpy (row-major C order) and FdMatrix (column-major Fortran order) on every boundary crossing — see `convert.rs:25-42`

## Anti-Patterns

### Mutable fdars-core State Not Cached in Python

**What happens:** fdars-core is a pure-function library (no internal caches). Python must re-call native functions for each operation, even if called with identical inputs.

**Why it's wrong:** Repeated calls (e.g., depth computed twice) run twice in Rust. High-dimensional operations with many calls may be inefficient.

**Do this instead:** Cache results in Python `Fdata` object or user code: `mean = fd.mean()  # computed once, reuse` rather than calling `fd.mean()` repeatedly.

### NumPy Layout Conversion Overhead

**What happens:** Every call to a native function converts between row-major (numpy) and column-major (FdMatrix) layouts (see `convert.rs:25-42`). Large datasets incur allocation/copy cost.

**Why it's wrong:** Repeated small operations on large matrices may spend more time on conversion than computation.

**Do this instead:** Batch operations; call low-level functions directly with raw NumPy arrays where possible (avoids Fdata wrapper overhead).

### Missing Input Validation in Native Wrappers

**What happens:** Some PyO3 wrappers delegate validation to fdars-core (returning Err). Error messages may be terse or unhelpful.

**Why it's wrong:** Users see low-level errors ("check that data columns == m1*m2") without context.

**Do this instead:** Add Python-side validation in Fdata methods or high-level wrappers (e.g., `fdars.clustering.cluster_optim` validates k_range before looping).

## Error Handling

**Strategy:** Exception-based (PyErr → Python exceptions)

**Patterns:**
- fdars-core returns `Result<T, FdarError>`
- PyO3 wrappers convert to `PyResult<T>` via `convert::to_pyresult()` — **location:** `src/convert.rs:91`
- FdarError message becomes PyValueError message — **location:** `src/convert.rs:86`
- Example: `fdars_core::fdata::deriv_2d()` returns `Ok(result)` or `None`; wrapper checks and raises PyValueError — **location:** `src/fdata_mod.rs:130-134`

## Cross-Cutting Concerns

**Logging:** 
- Rust layer: No logging (fdars-core is silent)
- Python layer: No centralized logging framework; users may print() or configure logging themselves

**Validation:** 
- Rust layer: Basic shape checks in fdars-core (e.g., number of data points must match grid size)
- Python layer: Fdata constructor validates matrix shape, grid length, metadata rows — **location:** `python/fdars/fdata_class.py:100-150`

**Authentication:** 
- Not applicable (library, not networked service)

---

*Architecture analysis: 2026-08-07*
