<!-- GSD:project-start source:PROJECT.md -->

## Project

**pyfda — Documentation Overhaul**

pyfda is the PyO3 binding layer that exposes the Rust `fdars-core` functional-data-analysis library to Python as the `fdars` package (represent, smooth, align, analyze, regress, monitor). This milestone is a **documentation overhaul**: reworking the MkDocs site's hand-authored SVG diagrams and its worked example pages to a consistently high, method-accurate standard.

**Core Value:** The documentation — diagrams first, examples second — must make functional data analysis in `fdars` visually clear and provably correct: every diagram faithfully depicts what the method actually does, and every example runs against the current API.

### Constraints

- **Authoring**: Diagrams stay hand-authored inline SVG — max conceptual control, edited by hand against a shared style spec.
- **Accuracy**: Diagrams and example outputs must be method-accurate; correctness is validated by section review on the built site, not assumed.
- **Compatibility**: Examples must run against the *current* `fdars` API and existing datasets in `docs/data/`.
- **Process**: Work proceeds section-by-section (learn/, align/, analyze/, regression/, monitoring/, represent/, examples/) with a review gate per section before moving on.

<!-- GSD:project-end -->

<!-- GSD:stack-start source:codebase/STACK.md -->

## Technology Stack

## Languages

- **Rust** 1.83+ - Core computation engine and bindings via PyO3
- **Python** 3.9 - 3.14 - High-level API wrapper and documentation
- **YAML** - Configuration for CI/CD and MkDocs

## Runtime

- **CPython** 3.9, 3.10, 3.11, 3.12, 3.13 (tested via CI)
- **Maturin** 1.x - Build backend for Rust-to-Python compilation
- **pip** - Python package installation
- **Cargo** - Rust package manager
- Lockfiles: `Cargo.lock` (Rust), `pyproject.toml` (Python)

## Frameworks

- **PyO3** 0.28 - Rust-Python bindings with extension module support (`abi3-py39`)
- **NumPy** 0.28 - Array bindings for zero-copy data exchange
- **Maturin** 1.0-2.0 - Build backend for compiled Python extensions
- **MkDocs** with Material theme 9.5+ - Static documentation site
- **markdown-exec** 1.8+ - Live code execution in documentation blocks
- **Material Extensions** - MkDocs Material theme plugins
- **pytest** - Python test runner
- **NumPy testing** - Array comparison utilities
- **GitHub Actions** - CI/CD automation
- **rust-cache** 2.x - Cargo build artifact caching
- **ghp-import** - GitHub Pages deployment (via mkdocs)

## Key Dependencies

- `fdars-core` 0.14.0 - Core Rust functional data analysis library with `parallel` feature enabled
- `pyo3` 0.28 - Enables Rust functions to be called from Python via ABI3 stable interface
- `numpy` 0.28 - Enables zero-copy NumPy array conversions between Python and Rust
- `matplotlib` 3.6+ - Plotting (optional dependency for `plot` extra)
- `scipy` 1.10+ - Numerical algorithms (scipy.signal, scipy.stats for docs)
- `scikit-learn` 1.3+ - Machine learning utilities (for docs examples)
- `pandas` - Metadata handling and optional dependency
- `nalgebra` - Linear algebra
- `rayon` - Data parallelism
- `rand`, `rand_distr` - Random number generation
- `rustfft` - Fast Fourier Transform
- `approx` - Floating-point comparisons

## Configuration

- No `.env` files detected
- No external service credentials required
- `Cargo.toml` - Rust package metadata and dependencies
- `pyproject.toml` - Python package metadata via PEP 517 build system
- `mkdocs.yml` - Documentation site configuration (`site/`)
- `.github/workflows/` - CI/CD configurations
- `rustfmt` - Rust code formatting (enforced via CI)
- `clippy` - Rust linting (enforced via CI, `-D warnings`)
- No Python linter detected in CI (no `ruff`, `black`, `pylint`)

## Platform Requirements

- Rust 1.83+ (MSRV)
- Python 3.9+ (runtime)
- C/C++ compiler (for Rust compilation)
- Virtual environment recommended (`.venv`, `.venv-puncc`)
- `maturin` for building extension in dev mode (`maturin develop`)
- Deployment: PyPI via wheels (published via GitHub Actions)
- Wheel distribution: Linux (x86_64, aarch64), macOS (x86_64, aarch64), Windows (x86_64)
- Source distribution: sdist included
- Python 3.9-3.13 wheels available
- Build environment: Ubuntu (CI)
- Live code execution during docs build requires compiled `fdars` package
- Matplotlib 3.7+ for figure rendering

<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->

## Conventions

## Naming Patterns

- Rust module files: snake_case with `_mod.rs` suffix (e.g., `fdata_mod.rs`, `depth_mod.rs`, `regression_mod.rs`)
- Python module files: snake_case (e.g., `fdata_class.py`, `metrics.py`, `_augment.py`)
- Conversion utilities: `convert.rs` for type conversions between numpy and fdars-core types
- Private Python modules: prefix with underscore (e.g., `_augment.py`)
- Rust: snake_case (e.g., `mean_1d`, `fraiman_muniz_1d`, `fdata_to_basis_1d`)
- Python: snake_case (e.g., `pred_mae`, `kernel_gaussian`, `cluster_optim`)
- Helper functions (private): prefix with underscore (e.g., `_pair()`, `_grids()`, `_default_ids()`)
- Dimension suffix pattern: Rust functions include dimension suffix for variants (`_1d`, `_2d`) to differentiate 1D vs 2D data (e.g., `mean_1d`, `mean_2d`, `fraiman_muniz_1d`, `fraiman_muniz_2d`)
- Rust: lowercase with underscores, common abbreviations: `data`, `argvals`, `mat`, `av`, `py`, `result`, `n_*` for counts
- Python: lowercase with underscores, use full words in public APIs
- Single-letter variables acceptable for: loop indices (`i`, `j`, `k`), Python context (`py`), temporary results (`r`, `d`)
- Abbreviated conventions in Rust bindings: `col_major`, `nrows`, `ncols` for matrix dimensions
- Rust: PascalCase (e.g., `PyReadonlyArray1<'py, f64>`, `Bound<'py, PyArray2<f64>>`)
- Python: PascalCase (e.g., `Fdata`, `DataFrame`)
- Type hints in Python: use `from __future__ import annotations` and describe with type hints in docstrings
- None defined at module level; all parameters passed via function arguments

## Code Style

- Rust: Follows Rust standard edition 2021; formatted with `rustfmt` (evident from codebase history: "docs+style: simplify home hero ... + rustfmt")
- Python: No explicit linter/formatter detected; follows PEP 8 conventions
- Rust: `#![allow(clippy::too_many_arguments)]` and `#![allow(clippy::type_complexity)]` at crate root (`src/lib.rs`) to suppress common warnings when binding many fdars-core functions
- Python: No formal linting configuration found
- Rust: `//!` for module-level doc comments at file head, `///` for function documentation
- Python: `"""` for module and class docstrings; inline `#` for regular comments

## Import Organization

- Rust: All fdars-core functions accessed via `fdars_core::<module>::<function>` (e.g., `fdars_core::fdata::mean_1d`)
- Python: Import submodules via dynamic registration (e.g., `from fdars import depth; depth.fraiman_muniz_1d(...)`)

## Error Handling

- Convert fdars-core `FdarError` to Python `PyValueError` via `to_pyerr()` in `convert.rs`
- Pattern: `to_pyresult()` wraps `Result<T, FdarError>` into `PyResult<T>`
- Use `?` operator to propagate errors; PyO3 automatically converts to Python exceptions
- Validation errors: return descriptive `PyValueError::new_err()` messages
- Raise `ValueError` for validation errors
- Check feature availability and raise `ImportError` with installation instructions
- Use `pytest.raises()` in tests to verify error messages

## Logging

- No debug/info logging
- Errors communicated via exceptions
- Documentation examples use direct output to stdout (e.g., `print(repr(fd))`)

## Comments

- Module-level doc comments (`//!` or `"""`) describe purpose and high-level behavior
- Function doc comments (`///` or `"""`) required for all public functions
- NumPy docstring format: Parameters, Returns, Examples; no inline implementation comments unless logic is non-obvious
- No inline comments observed; code is self-documenting via clear naming
- Not applicable (Rust/Python project)
- NumPy/Sphinx docstring format used instead

## Function Design

- Rust: Short wrapper functions, typically 5-15 lines, calling fdars-core and converting types
- Python: Similar; most functions in `metrics.py`, `covariance.py` are 5-20 lines
- Larger functions (e.g., `_simpson()` in `fdata_class.py`): ~40 lines for numerical integration logic
- Rust: Use `#[pyo3(signature = (...))]` to define default parameters (e.g., `scale=true`, `n_comp=3`)
- Python: Use Python function defaults in signature (e.g., `def _cluster_optim(..., criterion="silhouette", max_iter=100, ...)`)
- Array parameters: `PyReadonlyArray1`/`PyReadonlyArray2` for input (read-only), `PyArray1`/`PyArray2` for output
- Dimension variants: separate functions for 1D vs 2D (e.g., `mean_1d()`, `mean_2d()`)
- Rust: Single return type or tuple for multiple outputs (e.g., `(Bound<'py, PyArray2<f64>>, usize)`)
- Dictionary returns for structured output (e.g., regression functions return dict with `scores`, `rotation`, `singular_values`)
- Python: Return numpy arrays for numeric data, dicts for structured results, or custom classes (e.g., `Fdata`)

## Module Design

- Rust: All public functions are `#[pyfunction]` macros; no private functions visible to Python
- Python: Use `__all__` list to define public API (e.g., in `metrics.py`, `_augment.py`)
- Private functions/modules prefixed with underscore; imported but not listed in `__all__`
- `python/fdars/__init__.py`: Central export point; dynamically registers native submodules and pure-Python layers
- Registration pattern: loop over `_submodule_names` and attach to `sys.modules` and class attributes
- Pure-Python helpers injected via `_augment.install()` into native submodule namespaces
- Rust: One functional category per module (`fdata_mod.rs`, `depth_mod.rs`, etc.); registered as submodules in `lib.rs`
- Python: Classes and utilities split across files (e.g., `Fdata` class in `fdata_class.py`, metrics helpers in `metrics.py`)
- Lazy imports: `import pandas as pd` only in `fdata_class.py` where used; matplotlib imported lazily in `plot.py` module

## Python Class Design

- Constructor accepts `data`, `argvals`, `rangeval`, `names`, `id`, `metadata`
- Properties: `n_obs`, `n_points`, `fdata2d`, `dims`, `rangeval`, `data`, `argvals`, `id`, `metadata`
- Operators: `__add__`, `__sub__`, `__mul__`, `__rmul__`, `__truediv__`, `__getitem__`, `__len__`, `__repr__`
- Methods: `mean()`, `center()`, `deriv()`, `norm()`, `normalize()`, `geometric_median()`, `depth()`, `distance()`, `copy()`
- Private helpers: `_default_ids()`, `_argvals_equal()`, `_simpson()`, `_to_dataframe()`
- Metadata handling: auto-convert dict to DataFrame; validate row count

<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->

## Architecture

## System Overview

```text

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

- **Zero-copy data transfer:** NumPy arrays passed directly to Rust (PyReadonly wrappers avoid GIL contention)
- **Thin wrappers, not rearchitecture:** Each Rust module exports PyO3 functions that map directly to fdars-core primitives
- **Python convenience layer:** Fdata OOP class, high-level functions, and orchestration helpers built in pure Python on top of low-level native functions
- **Submodule namespacing:** Both `from fdars.depth import fraiman_muniz_1d` and `fdars.depth.fraiman_muniz_1d()` work via sys.modules injection in `__init__.py`
- **Feature gating:** fdars-core's "parallel" feature enabled at build time; MSRV is Rust 1.83

## Layers

- Purpose: High-level, idiomatic Python interface; convenience wrappers
- Location: `python/fdars/`
- Contains: Fdata class, orchestration functions, plotting, dataset utilities
- Depends on: `fdars._native` (compiled PyO3 extension), numpy, pandas, matplotlib
- Used by: End users; called from tests and examples
- Purpose: Bridge Python ↔ Rust; type marshalling; function registration
- Location: `src/`
- Contains: 18 Rust modules with @#[pyfunction] decorators; conversion utilities
- Depends on: fdars-core, pyo3, numpy (PyO3 bindings)
- Used by: Python API layer (all native calls go through here)
- Purpose: High-performance numerical computation
- Location: External (Cargo.toml dependency: fdars-core 0.14.0)
- Contains: Linear algebra (FdMatrix), algorithms (clustering, depth, regression, etc)
- Depends on: nalgebra, rayon (for parallel flag), specialized numerical libraries
- Used by: PyO3 wrapper layer (every native function calls into fdars-core)

## Data Flow

### Primary Request Path: Functional Data Operation

```

```

### Secondary Flow: Parameter Search (Pure Python)

- No persistent state across calls (each call is independent)
- Fdata object holds metadata/IDs but does not cache computed results
- fdars-core returns results; no caching in Rust layer
- Python layer may cache (e.g., `_augment` stores fitted models in return dict)

## Key Abstractions

- Purpose: Unified representation of functional data samples (rows=observations, cols=function evaluations)
- Examples: `src/convert.rs:29` (numpy2d_to_fdmatrix), `src/fdata_mod.rs:23` (receives FdMatrix)
- Pattern: All core algorithms operate on FdMatrix; Python layer converts numpy (row-major) to FdMatrix on entry, back to numpy on exit
- Purpose: Bundles data, evaluation grid, IDs, and metadata; provides method interface
- Examples: `python/fdars/fdata_class.py:1` (class definition)
- Pattern: `Fdata.__init__` validates and stores; methods delegate to native functions and wrap results
- Purpose: Expose Rust functions as Python callables with automatic type conversion
- Examples: `src/fdata_mod.rs:18` (#[pyfunction] mean_1d), `src/depth_mod.rs:22` (fraiman_muniz_1d)
- Pattern: 1:1 mapping to fdars-core; parameter validation in wrapper; return PyResult<T>
- Purpose: Reduce boilerplate for submodule creation and registration
- Examples: `src/lib.rs:28` (register_submodule! macro), `src/lib.rs:39-54` (usage)
- Pattern: Each module exposes a `register(m: &Bound<PyModule>) -> PyResult<()>` function that calls `add_function` for each wrapped function

## Entry Points

- Location: `python/fdars/__init__.py`
- Triggers: `import fdars` or `from fdars import ...`
- Responsibilities: Load _native (compiled module), register 16 submodules in sys.modules, import pure-Python helpers, inject orchestration functions
- Location: `src/lib.rs:37` (#[pymodule] _native)
- Triggers: When Python loads the compiled extension
- Responsibilities: Register all 16 submodules via register_submodule! macro; return PyResult
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

### NumPy Layout Conversion Overhead

### Missing Input Validation in Native Wrappers

## Error Handling

- fdars-core returns `Result<T, FdarError>`
- PyO3 wrappers convert to `PyResult<T>` via `convert::to_pyresult()` — **location:** `src/convert.rs:91`
- FdarError message becomes PyValueError message — **location:** `src/convert.rs:86`
- Example: `fdars_core::fdata::deriv_2d()` returns `Ok(result)` or `None`; wrapper checks and raises PyValueError — **location:** `src/fdata_mod.rs:130-134`

## Cross-Cutting Concerns

- Rust layer: No logging (fdars-core is silent)
- Python layer: No centralized logging framework; users may print() or configure logging themselves
- Rust layer: Basic shape checks in fdars-core (e.g., number of data points must match grid size)
- Python layer: Fdata constructor validates matrix shape, grid length, metadata rows — **location:** `python/fdars/fdata_class.py:100-150`
- Not applicable (library, not networked service)

<!-- GSD:architecture-end -->

<!-- GSD:skills-start source:skills/ -->

## Project Skills

No project skills found. Add skills to any of: `.claude/skills/`, `.agents/skills/`, `.cursor/skills/`, `.github/skills/`, or `.codex/skills/` with a `SKILL.md` index file.
<!-- GSD:skills-end -->

<!-- GSD:workflow-start source:GSD defaults -->

## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:

- `/gsd-quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd-debug` for investigation and bug fixing
- `/gsd-execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->

<!-- GSD:profile-start -->

## Developer Profile

> Profile not yet configured. Run `/gsd-profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.
<!-- GSD:profile-end -->
