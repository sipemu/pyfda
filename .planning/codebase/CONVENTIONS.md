# Coding Conventions

**Analysis Date:** 2026-08-07

## Naming Patterns

**Files:**
- Rust module files: snake_case with `_mod.rs` suffix (e.g., `fdata_mod.rs`, `depth_mod.rs`, `regression_mod.rs`)
- Python module files: snake_case (e.g., `fdata_class.py`, `metrics.py`, `_augment.py`)
- Conversion utilities: `convert.rs` for type conversions between numpy and fdars-core types
- Private Python modules: prefix with underscore (e.g., `_augment.py`)

**Functions:**
- Rust: snake_case (e.g., `mean_1d`, `fraiman_muniz_1d`, `fdata_to_basis_1d`)
- Python: snake_case (e.g., `pred_mae`, `kernel_gaussian`, `cluster_optim`)
- Helper functions (private): prefix with underscore (e.g., `_pair()`, `_grids()`, `_default_ids()`)
- Dimension suffix pattern: Rust functions include dimension suffix for variants (`_1d`, `_2d`) to differentiate 1D vs 2D data (e.g., `mean_1d`, `mean_2d`, `fraiman_muniz_1d`, `fraiman_muniz_2d`)

**Variables:**
- Rust: lowercase with underscores, common abbreviations: `data`, `argvals`, `mat`, `av`, `py`, `result`, `n_*` for counts
- Python: lowercase with underscores, use full words in public APIs
- Single-letter variables acceptable for: loop indices (`i`, `j`, `k`), Python context (`py`), temporary results (`r`, `d`)
- Abbreviated conventions in Rust bindings: `col_major`, `nrows`, `ncols` for matrix dimensions

**Types:**
- Rust: PascalCase (e.g., `PyReadonlyArray1<'py, f64>`, `Bound<'py, PyArray2<f64>>`)
- Python: PascalCase (e.g., `Fdata`, `DataFrame`)
- Type hints in Python: use `from __future__ import annotations` and describe with type hints in docstrings

**Constants:**
- None defined at module level; all parameters passed via function arguments

## Code Style

**Formatting:**
- Rust: Follows Rust standard edition 2021; formatted with `rustfmt` (evident from codebase history: "docs+style: simplify home hero ... + rustfmt")
- Python: No explicit linter/formatter detected; follows PEP 8 conventions
  - No `.flake8`, `.black`, or `pylintrc` in repository
  - Code appears to follow 4-space indentation and PEP 8 line-length conventions

**Linting:**
- Rust: `#![allow(clippy::too_many_arguments)]` and `#![allow(clippy::type_complexity)]` at crate root (`src/lib.rs`) to suppress common warnings when binding many fdars-core functions
- Python: No formal linting configuration found

**Comment Style:**
- Rust: `//!` for module-level doc comments at file head, `///` for function documentation
  - Doc comments follow numpy docstring format (Parameters, Returns, Examples)
- Python: `"""` for module and class docstrings; inline `#` for regular comments
  - Docstrings follow NumPy docstring format (Parameters, Returns, Examples)

## Import Organization

**Order (Rust):**
1. Standard library imports (`use std::...`)
2. External crate imports (`use pyo3::...`, `use numpy::...`, `use fdars_core::...`)
3. Local crate imports (`use crate::convert::...`, `mod alignment_mod`, etc.)

**Pattern (`src/lib.rs`):**
```rust
use pyo3::prelude::*;

mod convert;  // Conversion utilities

mod alignment_mod;  // Functional modules
mod basis_mod;
// ... more modules
```

**Order (Python):**
1. `from __future__ import annotations` (if using forward references)
2. Standard library imports (`import sys`, `import numpy as np`)
3. Third-party imports (`import pandas as pd`)
4. Local imports (`from fdars import _native`)

**Path Aliases:**
- Rust: All fdars-core functions accessed via `fdars_core::<module>::<function>` (e.g., `fdars_core::fdata::mean_1d`)
- Python: Import submodules via dynamic registration (e.g., `from fdars import depth; depth.fraiman_muniz_1d(...)`)

**Try-Except Imports:**
```python
try:
    import pandas as pd
    _HAS_PANDAS = True
except ImportError:
    _HAS_PANDAS = False
```
Used in `fdata_class.py` to make pandas optional; check flag before using pandas-dependent features.

## Error Handling

**Patterns:**

**Rust:**
- Convert fdars-core `FdarError` to Python `PyValueError` via `to_pyerr()` in `convert.rs`
- Pattern: `to_pyresult()` wraps `Result<T, FdarError>` into `PyResult<T>`
```rust
let result = to_pyresult(fdars_core::regression::fdata_to_pc_1d(&mat, n_comp, &av))?;
```
- Use `?` operator to propagate errors; PyO3 automatically converts to Python exceptions
- Validation errors: return descriptive `PyValueError::new_err()` messages
```rust
return Err(pyo3::exceptions::PyValueError::new_err(
    "basis_type must be 'bspline' or 'fourier'",
))
```

**Python:**
- Raise `ValueError` for validation errors
```python
if yt.shape != yp.shape:
    raise ValueError(f"shape mismatch: y_true {yt.shape} vs y_pred {yp.shape}")
```
- Check feature availability and raise `ImportError` with installation instructions
```python
if not _HAS_PANDAS:
    raise ImportError(
        "pandas is required for metadata support. "
        "Install it with: pip install pandas"
    )
```
- Use `pytest.raises()` in tests to verify error messages

## Logging

**Framework:** None defined. Codebase uses no logging library; errors are raised as exceptions or printed to stdout via doctest (in docs).

**Patterns:**
- No debug/info logging
- Errors communicated via exceptions
- Documentation examples use direct output to stdout (e.g., `print(repr(fd))`)

## Comments

**When to Comment:**
- Module-level doc comments (`//!` or `"""`) describe purpose and high-level behavior
- Function doc comments (`///` or `"""`) required for all public functions
- NumPy docstring format: Parameters, Returns, Examples; no inline implementation comments unless logic is non-obvious
- No inline comments observed; code is self-documenting via clear naming

**JSDoc/TSDoc:**
- Not applicable (Rust/Python project)
- NumPy/Sphinx docstring format used instead

## Function Design

**Size:** 
- Rust: Short wrapper functions, typically 5-15 lines, calling fdars-core and converting types
- Python: Similar; most functions in `metrics.py`, `covariance.py` are 5-20 lines
- Larger functions (e.g., `_simpson()` in `fdata_class.py`): ~40 lines for numerical integration logic

**Parameters:**
- Rust: Use `#[pyo3(signature = (...))]` to define default parameters (e.g., `scale=true`, `n_comp=3`)
- Python: Use Python function defaults in signature (e.g., `def _cluster_optim(..., criterion="silhouette", max_iter=100, ...)`)
- Array parameters: `PyReadonlyArray1`/`PyReadonlyArray2` for input (read-only), `PyArray1`/`PyArray2` for output
- Dimension variants: separate functions for 1D vs 2D (e.g., `mean_1d()`, `mean_2d()`)

**Return Values:**
- Rust: Single return type or tuple for multiple outputs (e.g., `(Bound<'py, PyArray2<f64>>, usize)`)
- Dictionary returns for structured output (e.g., regression functions return dict with `scores`, `rotation`, `singular_values`)
- Python: Return numpy arrays for numeric data, dicts for structured results, or custom classes (e.g., `Fdata`)

## Module Design

**Exports:**
- Rust: All public functions are `#[pyfunction]` macros; no private functions visible to Python
- Python: Use `__all__` list to define public API (e.g., in `metrics.py`, `_augment.py`)
- Private functions/modules prefixed with underscore; imported but not listed in `__all__`

**Barrel Files:**
- `python/fdars/__init__.py`: Central export point; dynamically registers native submodules and pure-Python layers
- Registration pattern: loop over `_submodule_names` and attach to `sys.modules` and class attributes
- Pure-Python helpers injected via `_augment.install()` into native submodule namespaces

**Module Organization:**
- Rust: One functional category per module (`fdata_mod.rs`, `depth_mod.rs`, etc.); registered as submodules in `lib.rs`
- Python: Classes and utilities split across files (e.g., `Fdata` class in `fdata_class.py`, metrics helpers in `metrics.py`)
- Lazy imports: `import pandas as pd` only in `fdata_class.py` where used; matplotlib imported lazily in `plot.py` module

## Python Class Design

**Fdata Class (`python/fdars/fdata_class.py`):**
- Constructor accepts `data`, `argvals`, `rangeval`, `names`, `id`, `metadata`
- Properties: `n_obs`, `n_points`, `fdata2d`, `dims`, `rangeval`, `data`, `argvals`, `id`, `metadata`
- Operators: `__add__`, `__sub__`, `__mul__`, `__rmul__`, `__truediv__`, `__getitem__`, `__len__`, `__repr__`
- Methods: `mean()`, `center()`, `deriv()`, `norm()`, `normalize()`, `geometric_median()`, `depth()`, `distance()`, `copy()`
- Private helpers: `_default_ids()`, `_argvals_equal()`, `_simpson()`, `_to_dataframe()`
- Metadata handling: auto-convert dict to DataFrame; validate row count

---

*Convention analysis: 2026-08-07*
