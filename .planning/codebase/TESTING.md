# Testing Patterns

**Analysis Date:** 2026-08-07

## Test Framework

**Runner:**
- pytest (specified in `pyproject.toml` under `[project.optional-dependencies] dev`)
- Config: No `pytest.ini`, `setup.cfg`, or `pyproject.toml` pytest section; uses pytest defaults
- Python version: 3.9+

**Assertion Library:**
- `numpy.testing` for array assertions (e.g., `np.testing.assert_allclose()`, `np.testing.assert_array_equal()`)
- `pytest` assertion style for scalar values and exceptions

**Run Commands:**
```bash
pytest tests/                           # Run all tests
pytest tests/test_basic.py -v          # Run specific test file with verbose output
pytest tests/test_fdata_class.py::TestFdataConstruction::test_1d_basic -v  # Run single test
pytest -xvs                            # Stop on first failure, verbose
```

## Test File Organization

**Location:**
- Tests are co-located in `/home/simonm/projects/rust/pyfda/tests/` directory (separate from source, not inside `src/` or `python/`)
- Three test files: `test_basic.py`, `test_fdata_class.py`, `test_r_parity.py`

**Naming:**
- Test files: `test_*.py` prefix
- Test classes: `Test*` prefix (e.g., `TestFdata`, `TestDepth`, `TestBatchA`)
- Test methods: `test_*` prefix (e.g., `test_import()`, `test_mean_1d()`)

**Structure:**
```
tests/
├── test_basic.py              # Core module smoke tests, depth, metric, clustering, etc.
├── test_fdata_class.py        # Fdata class construction, metadata, operations, subsetting
└── test_r_parity.py           # R-parity validation (ground-truth numerical properties)
```

## Test Structure

**Suite Organization (from `test_basic.py`):**
```python
class TestFdata:
    def test_mean_1d(self):
        from fdars.fdata import mean_1d
        data = np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])
        result = mean_1d(data)
        np.testing.assert_allclose(result, [2.5, 3.5, 4.5])

class TestDepth:
    def setup_method(self):
        np.random.seed(42)
        self.data = np.random.randn(20, 50)
    
    def test_fraiman_muniz(self):
        from fdars.depth import fraiman_muniz_1d
        depths = fraiman_muniz_1d(self.data, self.data)
        assert depths.shape == (20,)
        assert all(0 <= d <= 1 for d in depths)
```

**Patterns:**
- Test classes group related tests by module/functionality
- `setup_method()`: Run before each test method to initialize fixtures (np.random.seed, data arrays)
- One test method per function/behavior
- Import functions inside test methods (lazy import pattern)

## Mocking

**Framework:** pytest built-in (no external mock library detected)

**Patterns:**
- Minimal mocking; most tests use real numpy arrays and actual fdars functions
- Determinism via seeding: `np.random.seed(42)` in `setup_method()` or `np.random.default_rng(seed)` in test data
- Example from `test_r_parity.py`:
```python
def test_rpd_depth(self):
    rng = np.random.default_rng(0)
    X = rng.standard_normal((20, 40))
    R = rng.standard_normal((30, 40))
    av = np.linspace(0, 1, 40)
    d = depth.random_projection_deriv_1d(X, R, av, n_proj=30, n_deriv=1, seed=1)
    assert d.shape == (20,)
    assert np.isfinite(d).all()
    # determinism given a seed
    d2 = depth.random_projection_deriv_1d(X, R, av, n_proj=30, n_deriv=1, seed=1)
    np.testing.assert_allclose(d, d2)
```

**What to Mock:**
- Do not mock fdars functions; test against real implementation
- No external services mocked (no API calls, no database)

**What NOT to Mock:**
- fdars-core functions (test against real behavior)
- NumPy operations (always use real NumPy)

## Fixtures and Factories

**Test Data:**
- Simple inline construction: `np.random.randn(n, m)` for random data
- Deterministic via seed: `np.random.seed(42)` or `np.random.default_rng(seed)`
- Example simple data (`test_basic.py`):
```python
def test_mean_1d(self):
    data = np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])
    result = mean_1d(data)
    np.testing.assert_allclose(result, [2.5, 3.5, 4.5])
```
- Example with shared setup (`test_basic.py`):
```python
class TestMetric:
    def setup_method(self):
        np.random.seed(42)
        self.data = np.random.randn(10, 30)
        self.argvals = np.linspace(0, 1, 30)
```

**Location:**
- No separate fixtures directory
- Fixtures defined inline in `setup_method()` per test class
- No pytest `conftest.py` file

**Factories:**
- No factory pattern; data generation is ad-hoc in setup_method or test method
- Example from `test_r_parity.py`:
```python
def _seasonal_data(self, period_frac=1.0):
    t = np.linspace(0, 10, 200)
    rng = np.random.default_rng(3)
    X = np.vstack([...])
    return X, t
```
Reusable data-generation methods defined on test class itself

## Coverage

**Requirements:** No coverage requirement enforced; no `pytest-cov`, `.coveragerc`, or coverage CI/CD

**View Coverage:**
```bash
pytest --cov=fdars tests/           # If pytest-cov installed
pytest --cov=fdars --cov-report=html tests/
```

## Test Types

**Unit Tests:**
- Scope: Individual fdars functions (e.g., `mean_1d`, `fraiman_muniz_1d`)
- Approach: Call function, assert output shape, dtype, value range, or numerical accuracy
- Example (`test_basic.py`):
```python
def test_mean_1d(self):
    from fdars.fdata import mean_1d
    data = np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])
    result = mean_1d(data)
    np.testing.assert_allclose(result, [2.5, 3.5, 4.5])
```

**Integration Tests:**
- Scope: Multiple functions working together; Fdata class methods; cross-module workflows
- Example (`test_fdata_class.py`):
```python
def test_center_preserves_metadata(self):
    from fdars import Fdata
    meta = pd.DataFrame({"group": ["A", "B", "C"]})
    fd = Fdata(np.random.randn(3, 10), metadata=meta)
    centered = fd.center()
    assert isinstance(centered.metadata, pd.DataFrame)
    assert centered.id == fd.id
```
Tests that operations preserve state (metadata, ids)

**E2E Tests:**
- Not present in codebase
- Closest: `test_r_parity.py` tests ground-truth numerical properties against reference implementations

**Validation Tests:**
- Input validation: shape mismatches, type errors, boundary conditions
- Example (`test_fdata_class.py`):
```python
def test_1d_id_length_mismatch(self):
    from fdars import Fdata
    with pytest.raises(ValueError, match="id must have length"):
        Fdata(np.random.randn(3, 10), id=["a", "b"])
```

## Common Patterns

**Async Testing:**
- Not applicable (synchronous execution; no async code in codebase)

**Error Testing:**
```python
def test_id_length_mismatch(self):
    from fdars import Fdata
    with pytest.raises(ValueError, match="id must have length"):
        Fdata(np.random.randn(3, 10), id=["a", "b"])
```
Use `pytest.raises(ExceptionType, match="regex")` to verify exception type and message

**Shape Assertion Pattern:**
```python
def test_fraiman_muniz(self):
    depths = fraiman_muniz_1d(self.data, self.data)
    assert depths.shape == (20,)
```
Verify output shape and dtype match expectation

**Value Range Assertion:**
```python
def test_fraiman_muniz(self):
    depths = fraiman_muniz_1d(self.data, self.data)
    assert all(0 <= d <= 1 for d in depths)
```
Check depth values are in [0, 1] range

**Numerical Accuracy:**
```python
def test_norm_lp_1d(self):
    data = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
    argvals = np.linspace(0, 1, 3)
    result = norm_lp_1d(data, argvals)
    assert len(result) == 2
    assert all(r >= 0 for r in result)
```
Use `np.testing.assert_allclose(result, expected)` for floating-point comparisons

**Determinism Testing:**
From `test_r_parity.py`:
```python
d = depth.random_projection_deriv_1d(X, R, av, n_proj=30, n_deriv=1, seed=1)
d2 = depth.random_projection_deriv_1d(X, R, av, n_proj=30, n_deriv=1, seed=1)
np.testing.assert_allclose(d, d2)
```
Verify seeded randomness produces identical results

## Test Data Files

- No external test data files
- All test data generated inline via NumPy (arrays, grids)
- Datasets: `fdars.datasets` module provides vendored CSV files (`python/fdars/data/*.csv`) for examples, not used in unit tests

---

*Testing analysis: 2026-08-07*
