# Codebase Structure

**Analysis Date:** 2026-08-07

## Directory Layout

```
pyfda/
├── Cargo.toml                      # Rust package manifest (PyO3 cdylib)
├── Cargo.lock                      # Rust dependency lock file
├── pyproject.toml                  # Python build config (maturin backend)
├── mkdocs.yml                      # Documentation site config
├── Makefile                        # Development tasks (build, test, format)
├── README.md                       # Project overview
├── PARITY_PLAN.md                  # R-parity implementation roadmap
│
├── src/                            # Rust FFI layer (PyO3 wrappers)
│   ├── lib.rs                      # Module entry point; submodule registration
│   ├── convert.rs                  # NumPy ↔ Rust type conversion utilities
│   ├── fdata_mod.rs                # Functional data operations (mean, deriv, norm, etc)
│   ├── depth_mod.rs                # Depth functions (Fraiman-Muniz, modal, band, etc)
│   ├── metric_mod.rs               # Distance metrics (Lp, Hausdorff, DTW, elastic, etc)
│   ├── basis_mod.rs                # Basis representations (B-splines, P-splines, Fourier)
│   ├── smoothing_mod.rs            # Nonparametric smoothing (NW, local poly, k-NN)
│   ├── clustering_mod.rs           # Clustering (k-means, fuzzy c-means, GMM)
│   ├── regression_mod.rs           # Regression (FPCA, PLS, nonparametric, robust, FOSR, FANOVA)
│   ├── alignment_mod.rs            # Elastic alignment (SRSF, Karcher mean, elastic FPCA)
│   ├── outliers_mod.rs             # Outlier detection (LRT, outliergram, magnitude-shape)
│   ├── seasonal_mod.rs             # Seasonal analysis (SAZED, autoperiod, STL, peak detection)
│   ├── spm_mod.rs                  # Statistical process monitoring (Phase I/II, EWMA, CUSUM)
│   ├── classification_mod.rs       # Classification (LDA, QDA, k-NN, kernel)
│   ├── tolerance_mod.rs            # Tolerance bands (FPCA, conformal, Degras SCB)
│   ├── conformal_mod.rs            # Conformal prediction (split, jackknife+)
│   ├── simulation_mod.rs           # Simulation (Karhunen-Loève, Gaussian processes)
│   └── explain_mod.rs              # Explainability (SHAP, PDP, permutation, regions)
│
├── python/                         # Python package source
│   └── fdars/                      # Main package
│       ├── __init__.py             # Package initialization; submodule registration
│       ├── fdata_class.py          # Fdata OOP container (bundles data, grid, metadata)
│       ├── _augment.py             # Pure-Python orchestration helpers (cluster_optim, cluster_init)
│       ├── plot.py                 # Visualization wrappers (matplotlib-based plotting)
│       ├── metrics.py              # High-level metric wrappers (distance matrix, pairwise)
│       ├── covariance.py           # Covariance estimation and utilities
│       ├── datasets.py             # Dataset loading (CSV files in data/)
│       ├── results.py              # Result container classes (Results, CrossValidation, etc)
│       └── data/                   # Bundled CSV datasets
│           ├── canadian_weather.csv
│           ├── canadian_weather_precip.csv
│           ├── canadian_weather_meta.csv
│           ├── growth.csv
│           ├── phoneme.csv
│           ├── sonar.csv
│           ├── tecator.csv
│           └── wine.csv
│
├── tests/                          # Test suite
│   ├── test_basic.py               # Smoke tests: basic module functionality
│   ├── test_fdata_class.py         # Fdata container functionality
│   └── test_r_parity.py            # R-parity verification tests
│
├── examples/                       # Example scripts (not yet included in repo)
│   └── [example scripts]
│
├── docs/                           # Documentation source (MkDocs with Material)
│   ├── index.md
│   ├── reference/                  # API reference (auto-generated stubs)
│   │   ├── fdata/
│   │   ├── depth/
│   │   ├── metric/
│   │   ├── basis/
│   │   ├── [16 subdirs, one per module]
│   │   └── explain/
│   ├── learn/                      # Tutorials
│   │   ├── introduction.md
│   │   ├── derivatives.md
│   │   ├── smoothing.md
│   │   ├── simulation.md
│   │   ├── irregular-sampling.md
│   │   └── custom-plotting.md
│   ├── examples/                   # Tutorial examples (markdown + embedded Python)
│   ├── analyze/                    # Analysis category docs
│   ├── represent/                  # Representation category docs
│   ├── align/                      # Alignment category docs
│   ├── regression/                 # Regression category docs
│   ├── monitoring/                 # SPM category docs
│   ├── data/                       # Data files for tutorials
│   ├── assets/                     # Images, diagrams, icons
│   └── javascripts/                # Custom JS (search, math)
│
├── site/                           # Built documentation (generated, not committed)
│   ├── index.html
│   ├── reference/                  # Compiled API docs
│   ├── [mirrors of docs/ structure]
│   └── search/                     # Search index
│
├── scripts/                        # Build and utility scripts
│   └── [build/release scripts]
│
├── .github/                        # GitHub metadata
│   └── workflows/                  # CI/CD pipelines
│       └── ci.yml                  # PyPI build + test
│
├── .planning/                      # GSD planning artifacts
│   └── codebase/                   # Codebase analysis (this directory)
│       ├── ARCHITECTURE.md
│       └── STRUCTURE.md
│
└── target/                         # Rust build artifacts (not committed)
    └── release/                    # Compiled extension
```

## Directory Purposes

**`src/`** — Rust PyO3 wrappers
- Purpose: Bridge Python ↔ Rust; thin wrapping of fdars-core functions
- Contains: 18 Rust modules (.rs files), each wrapping one functional domain (fdata, depth, clustering, etc)
- Key files: `lib.rs` (entry point, submodule registration), `convert.rs` (type marshalling)
- Build output: Compiled to `_native.so` (or `.pyd` on Windows) and installed into Python package

**`python/fdars/`** — Python package
- Purpose: High-level Python API; convenience wrappers; dataset loading
- Contains: Pure Python modules (class, functions, utilities) and bundled CSV datasets
- Key files: `__init__.py` (initialization, sys.modules registration), `fdata_class.py` (OOP container), `_augment.py` (orchestration)
- Imports: `_native` (compiled Rust extension), numpy, pandas, matplotlib (optional)

**`python/fdars/data/`** — Bundled datasets
- Purpose: Example datasets packaged with the wheel for tutorials
- Contains: CSV files (8 datasets: canadian_weather, growth, phoneme, sonar, tecator, wine, etc)
- Shipped with: wheel via maturin `include` glob

**`tests/`** — Test suite
- Purpose: Validation of API and R-parity
- Contains: pytest test files (3 modules; ~200 tests total based on coverage)
- Key files: `test_basic.py` (module smoke tests), `test_fdata_class.py` (Fdata container), `test_r_parity.py` (R package alignment)

**`docs/`** — Documentation source
- Purpose: MkDocs Material site (user guide, tutorials, API reference)
- Contains: Markdown files (learn, reference, examples, tutorials)
- Build: `mkdocs build` outputs to `site/` (not committed)
- Deployment: GitHub Pages (https://sipemu.github.io/pyfda/)

**`examples/`** — Example scripts
- Purpose: Standalone executable examples
- Contains: (Currently sparse; examples integrated into docs/ instead)
- Status: Planned expansion under PARITY_PLAN.md

## Key File Locations

**Entry Points:**

| File | Purpose |
|------|---------|
| `src/lib.rs` | Rust FFI entry point (#[pymodule] _native); registers 16 submodules |
| `python/fdars/__init__.py` | Python package entry point; loads _native, injects submodules into sys.modules |
| `Cargo.toml` | Rust build config; specifies fdars-core 0.14.0 dependency, PyO3 0.28 |
| `pyproject.toml` | Python/maturin build config; specifies wheel metadata, maturin backend |

**Configuration:**

| File | Purpose |
|------|---------|
| `mkdocs.yml` | Documentation site structure and theme (Material) |
| `Makefile` | Development task shortcuts (maturin develop, pytest, mkdocs serve, fmt, lint) |
| `Cargo.lock` | Rust dependency pinning |

**Core Logic:**

| File | Purpose |
|------|---------|
| `src/convert.rs` | Type conversion (numpy arrays ↔ FdMatrix); error marshalling |
| `src/fdata_mod.rs` | Functional data operations (mean, center, deriv, norm, normalize) |
| `src/depth_mod.rs` | Depth functions (Fraiman-Muniz, modal, band, random projection, etc) |
| `src/metric_mod.rs` | Distance metrics (Lp, Hausdorff, DTW, soft-DTW, Fourier, h-shift) |
| `src/regression_mod.rs` | Regression (FPCA, PLS, nonparametric, robust, FOSR, FANOVA) |
| `src/clustering_mod.rs` | Clustering (k-means, fuzzy c-means, GMM, silhouette, Calinski-Harabasz) |
| `python/fdars/fdata_class.py` | Fdata container (OOP interface wrapping low-level functions) |
| `python/fdars/_augment.py` | Orchestration (cluster_optim, cluster_init for hyperparameter search) |

**Testing:**

| File | Purpose |
|------|---------|
| `tests/test_basic.py` | Smoke tests for all 16 modules |
| `tests/test_fdata_class.py` | Fdata container construction, slicing, metadata handling |
| `tests/test_r_parity.py` | Numerical parity with R fdars package (resolves issues #33, #37) |

## Naming Conventions

**Files:**

| Pattern | Example | Usage |
|---------|---------|-------|
| `*_mod.rs` | `fdata_mod.rs`, `depth_mod.rs` | Rust functional modules (1 per domain) |
| `test_*.py` | `test_basic.py`, `test_fdata_class.py` | pytest test modules |
| `*_meta.csv` | `canadian_weather_meta.csv` | Metadata files accompanying data |

**Directories:**

| Pattern | Example | Usage |
|---------|---------|-------|
| `{domain}/` | `docs/reference/fdata/`, `docs/analyze/` | Documentation organized by functional area |
| `{domain}/` | `site/reference/depth/`, `site/examples/` | Built documentation mirrors source |

**Functions/Methods:**

- Python: `snake_case` (e.g., `fraiman_muniz_1d`, `cluster_optim`, `load_canadian_weather`)
- Rust: `snake_case` (e.g., `numpy2d_to_fdmatrix`, `to_pyerr`, `register`)

**Types/Classes:**

- Python: `PascalCase` (e.g., `Fdata`, `CrossValidation`, `Results`)
- Rust: `PascalCase` (e.g., `PyModule`, `PyArray2`)

**Module Naming:**

- Python submodules: lowercase (e.g., `fdars.fdata`, `fdars.depth`, `fdars.clustering`)
- Rust submodules: `snake_case` module names (e.g., `mod alignment_mod`, `mod basis_mod`)

## Where to Add New Code

**New Functional Module (e.g., new statistical test):**

1. **Add Rust wrapper:**
   - Create `src/new_feature_mod.rs`
   - Expose `pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()>` function
   - Implement `#[pyfunction]` wrappers for each fdars-core function
   - Use `convert.rs` utilities for type marshalling
   
   Example structure:
   ```rust
   // src/new_feature_mod.rs
   use crate::convert::*;
   use numpy::{PyArray1, PyReadonlyArray2};
   use pyo3::prelude::*;
   
   #[pyfunction]
   pub fn my_new_function<'py>(
       py: Python<'py>,
       data: PyReadonlyArray2<'py, f64>,
   ) -> PyResult<Bound<'py, PyArray1<f64>>> {
       let mat = numpy2d_to_fdmatrix(data)?;
       let result = fdars_core::new_feature::my_function(&mat);
       Ok(vec_to_numpy1d(py, result))
   }
   
   pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
       m.add_function(wrap_pyfunction!(my_new_function, m)?)?;
       Ok(())
   }
   ```

2. **Register in `src/lib.rs`:**
   ```rust
   mod new_feature_mod;
   
   #[pymodule]
   fn _native(m: &Bound<'_, PyModule>) -> PyResult<()> {
       // ... existing modules ...
       register_submodule!(m, "new_feature", new_feature_mod::register);
       Ok(())
   }
   ```

3. **Add Python convenience layer (optional):**
   - Create `python/fdars/new_feature_helpers.py`
   - Import in `python/fdars/__init__.py`
   - Include in `__all__`

4. **Add tests:**
   - Add test function to `tests/test_basic.py` or create `tests/test_new_feature.py`
   - Use pytest; fixtures available in test files

5. **Add documentation:**
   - Create `docs/reference/new_feature/` with markdown files
   - Create `docs/examples/` tutorial if applicable

**New Utility Function (pure Python, e.g., metric wrappers):**

1. Create or extend file in `python/fdars/` (e.g., `metrics.py`, `covariance.py`)
2. Import `_native` submodule as needed
3. Wrap low-level functions with validation, batching, or caching
4. Import in `python/fdars/__init__.py` if top-level exposure needed
5. Add tests in `tests/` with pytest

**New Dataset:**

1. Add CSV file to `python/fdars/data/`
2. Add loader function to `python/fdars/datasets.py` (pattern: `load_my_dataset()`)
3. Update `pyproject.toml` maturin.include glob to cover new file (already `python/fdars/data/*.csv`)

**Plotting/Visualization:**

- Add to `python/fdars/plot.py` (matplotlib-based)
- Import matplotlib inside functions (lazy loading) to avoid hard dependency

## Special Directories

**`target/`** — Build artifacts
- Purpose: Compiled Rust library and intermediate objects
- Generated: Yes (via `cargo build` / `maturin develop`)
- Committed: No (.gitignore)

**`site/`** — Built documentation
- Purpose: HTML output from `mkdocs build`
- Generated: Yes (via `mkdocs build`)
- Committed: No (.gitignore)

**`.pytest_cache/`** — pytest metadata
- Purpose: Test run cache (speedup)
- Generated: Yes (via pytest)
- Committed: No (.gitignore)

**`.venv/` / `.venv-puncc/`** — Python virtual environments
- Purpose: Development isolation (dependencies installed here)
- Generated: Yes (manual setup via `python -m venv .venv`)
- Committed: No (.gitignore)

**`.planning/codebase/`** — GSD codebase analysis
- Purpose: Architecture and structure documentation for orchestrator
- Generated: No (hand-written or AI-generated via GSD)
- Committed: Yes (reference for future phases)

---

*Structure analysis: 2026-08-07*
