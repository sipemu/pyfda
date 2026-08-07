# Technology Stack

**Analysis Date:** 2026-08-07

## Languages

**Primary:**
- **Rust** 1.83+ - Core computation engine and bindings via PyO3
- **Python** 3.9 - 3.14 - High-level API wrapper and documentation

**Secondary:**
- **YAML** - Configuration for CI/CD and MkDocs

## Runtime

**Environment:**
- **CPython** 3.9, 3.10, 3.11, 3.12, 3.13 (tested via CI)
- **Maturin** 1.x - Build backend for Rust-to-Python compilation

**Package Manager:**
- **pip** - Python package installation
- **Cargo** - Rust package manager
- Lockfiles: `Cargo.lock` (Rust), `pyproject.toml` (Python)

## Frameworks

**Core:**
- **PyO3** 0.28 - Rust-Python bindings with extension module support (`abi3-py39`)
- **NumPy** 0.28 - Array bindings for zero-copy data exchange
- **Maturin** 1.0-2.0 - Build backend for compiled Python extensions

**Documentation:**
- **MkDocs** with Material theme 9.5+ - Static documentation site
- **markdown-exec** 1.8+ - Live code execution in documentation blocks
- **Material Extensions** - MkDocs Material theme plugins

**Testing:**
- **pytest** - Python test runner
- **NumPy testing** - Array comparison utilities

**Build/Dev:**
- **GitHub Actions** - CI/CD automation
- **rust-cache** 2.x - Cargo build artifact caching
- **ghp-import** - GitHub Pages deployment (via mkdocs)

## Key Dependencies

**Critical:**
- `fdars-core` 0.14.0 - Core Rust functional data analysis library with `parallel` feature enabled
  - Provides 100+ functional data analysis algorithms
  - Enables parallel computation via Rayon
- `pyo3` 0.28 - Enables Rust functions to be called from Python via ABI3 stable interface
- `numpy` 0.28 - Enables zero-copy NumPy array conversions between Python and Rust

**Scientific Computing (Optional/Development):**
- `matplotlib` 3.6+ - Plotting (optional dependency for `plot` extra)
- `scipy` 1.10+ - Numerical algorithms (scipy.signal, scipy.stats for docs)
- `scikit-learn` 1.3+ - Machine learning utilities (for docs examples)
- `pandas` - Metadata handling and optional dependency

**Rust Transitive Dependencies:**
- `nalgebra` - Linear algebra
- `rayon` - Data parallelism
- `rand`, `rand_distr` - Random number generation
- `rustfft` - Fast Fourier Transform
- `approx` - Floating-point comparisons

## Configuration

**Environment:**
- No `.env` files detected
- No external service credentials required

**Build:**
- `Cargo.toml` - Rust package metadata and dependencies
  - Lib name: `_native` (compiled as `cdylib`)
  - Edition: 2021
  - MSRV: 1.83
- `pyproject.toml` - Python package metadata via PEP 517 build system
  - Build system: `maturin`
  - Python requirement: `>=3.9`
  - Includes CSV dataset vendoring via `include` glob
- `mkdocs.yml` - Documentation site configuration (`site/`)
- `.github/workflows/` - CI/CD configurations

**Code Quality:**
- `rustfmt` - Rust code formatting (enforced via CI)
- `clippy` - Rust linting (enforced via CI, `-D warnings`)
- No Python linter detected in CI (no `ruff`, `black`, `pylint`)

## Platform Requirements

**Development:**
- Rust 1.83+ (MSRV)
- Python 3.9+ (runtime)
- C/C++ compiler (for Rust compilation)
- Virtual environment recommended (`.venv`, `.venv-puncc`)
- `maturin` for building extension in dev mode (`maturin develop`)

**Production:**
- Deployment: PyPI via wheels (published via GitHub Actions)
- Wheel distribution: Linux (x86_64, aarch64), macOS (x86_64, aarch64), Windows (x86_64)
- Source distribution: sdist included
- Python 3.9-3.13 wheels available

**Documentation:**
- Build environment: Ubuntu (CI)
- Live code execution during docs build requires compiled `fdars` package
- Matplotlib 3.7+ for figure rendering

---

*Stack analysis: 2026-08-07*
