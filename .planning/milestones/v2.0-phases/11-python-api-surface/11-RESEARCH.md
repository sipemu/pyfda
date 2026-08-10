# Phase 11: Python API Surface - Research

**Researched:** 2026-08-09
**Domain:** Python packaging, submodule injection, pytest, fdars API integration
**Confidence:** HIGH

## Summary

Phase 11 is a pure integration-and-packaging phase. All computation primitives exist in `python/fdars/advisor.py` (531+ lines, grown through Phase 10). The work is: (1) wire the module into the public `fdars` package namespace; (2) declare the `[advisor]` optional-dependency extra in `pyproject.toml`; (3) write offline unit tests and an env-gated LLM integration test; (4) add an `examples/` recipe script demonstrating the advisor end-to-end.

No new algorithms need to be invented. Every design pattern to follow (submodule injection, lazy-import guards, env-gated test skips) is already present in the codebase and is documented here with exact file:line citations.

**Primary recommendation:** Follow the pure-Python-module-direct-import pattern — `advisor` is NOT a native Rust submodule, so it must be wired into `__init__.py` differently from the 16 native submodules in `_submodule_names`. It should be imported as a plain Python module and listed in `__all__`, with `sys.modules` injection added so `from fdars import advisor` and `fdars.advisor.build_diagnostics(...)` both work.

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| PYAPI-01 | `build_diagnostics`, `advise`, `describe_cluster_differences` reachable from public `fdars` API (module registered, `__all__`) | Submodule injection pattern documented in section "Pure-Python Submodule Injection Pattern" |
| PYAPI-02 | Offline unit tests for `build_diagnostics` against `docs/data/` datasets; LLM call covered by env-gated integration test skipped without `ANTHROPIC_API_KEY` | Test conventions documented in section "Test Conventions & CI Constraints" |
| PYAPI-03 | `examples/` recipe page demonstrating advisor end-to-end against a real dataset | Format and dataset choice documented in section "Recipe Page Format" |
</phase_requirements>

## Project Constraints (from CLAUDE.md)

- Diagrams stay hand-authored inline SVG — not relevant to this phase
- Examples must run against the current `fdars` API — advisor module must be wired before examples are written
- No `.env` files; no external service credentials hardcoded — API key comes from `ANTHROPIC_API_KEY` env var (already implemented in `advisor.py:955`)
- No Python linter detected in CI — no formatter gate to worry about
- Error handling: convert errors to `ImportError`/`ValueError` with clear messages; `_require_anthropic()` already follows this pattern

---

## 1. Where the Advisor Code Lives Today

### File

`python/fdars/advisor.py` [VERIFIED: python/fdars/advisor.py:1-1136]

Created in Phase 10; never imported by `__init__.py` (deferred to Phase 11 by design).

### Current `__all__` (verbatim)

```python
__all__ = [
    "build_diagnostics",
    "advise",
    "describe_cluster_differences",
    "Advice",
    "Recommendation",
]
```
[VERIFIED: python/fdars/advisor.py:175-181]

### Function Signatures (verbatim from source)

**`build_diagnostics`** [VERIFIED: python/fdars/advisor.py:188-255]
```python
def build_diagnostics(
    result,
    method: str,
    *,
    argvals=None,
    **kwargs,
) -> dict:
```
- `method` must be one of `{"alignment", "fpca", "basis", "smoothing", "clustering"}` (case-insensitive)
- Returns a plain-Python dict with JSON-serialisable values only
- Fully offline and deterministic; no network, no RNG, no wall-clock
- Unwraps `.raw` from wrapper objects automatically

**`advise`** [VERIFIED: python/fdars/advisor.py:915-982]
```python
def advise(
    diagnostics: dict,
    *,
    task: str,
    domain_context: str,
    model: str = "claude-opus-4-8",
) -> Advice:
```
- Calls `_require_anthropic()` first — raises `ImportError` with `pip install fdars[advisor]` hint if absent
- Reads API key from environment via `anthropic.Anthropic()` (never hardcoded) [VERIFIED: python/fdars/advisor.py:955]
- `task` must be one of `{"interpretation", "parameter", "method"}` (case-insensitive)

**`describe_cluster_differences`** [VERIFIED: python/fdars/advisor.py:989-1100]
```python
def describe_cluster_differences(
    result,
    *,
    argvals=None,
    domain_context: str = "",
    model: str = "claude-opus-4-8",
    run_llm: bool = True,
    **kwargs,
):
```
- `run_llm=False` returns raw clustering diagnostics dict (fully offline, no import of `anthropic`)
- `run_llm=True` calls `advise(task="interpretation", ...)` and returns schema-validated `Advice`

**`ADVISOR_ANTHROPIC_MIN_VERSION`** [VERIFIED: python/fdars/advisor.py:53]
```python
ADVISOR_ANTHROPIC_MIN_VERSION = "0.72.0"
```

### Current Import Status

`advisor.py` is NOT imported in `__init__.py` as of Phase 10 completion. The module comment at line 1 of `advisor.py` explicitly notes "pyproject.toml, `__init__.py`, and tests untouched — deferred to Phase 11 per plan." [VERIFIED: python/fdars/advisor.py:1-40 (module docstring)]

---

## 2. Pure-Python Submodule Injection Pattern

### How Native Submodules Are Registered

`python/fdars/__init__.py` [VERIFIED: python/fdars/__init__.py:1-80]

The 16 native (Rust/PyO3) submodules are registered via a loop:

```python
_submodule_names = (
    "fdata", "depth", "metric", "basis", "smoothing",
    "clustering", "regression", "alignment", "outliers",
    "seasonal", "spm", "classification", "tolerance",
    "conformal", "simulation", "explain",
)

for _name in _submodule_names:
    _submod = getattr(_native, _name)
    _sys.modules[f"{__name__}.{_name}"] = _submod
    setattr(_sys.modules[__name__], _name, _submod)
```
[VERIFIED: python/fdars/__init__.py:34-58]

This pattern works because these are attributes of `_native` (the compiled extension module). `advisor` is NOT an attribute of `_native` — it is a pure-Python file.

### How Pure-Python Modules Are Currently Registered

```python
from fdars import datasets, results, metrics, covariance  # noqa: E402
from fdars import plot  # noqa: E402
from fdars import _augment as _augment  # noqa: E402
```
[VERIFIED: python/fdars/__init__.py:61-63]

These are plain imports. They are listed in `__all__` directly:

```python
__all__ = [
    "Fdata",
    *(_submodule_names),
    "datasets",
    "results",
    "plot",
    "metrics",
    "covariance",
]
```
[VERIFIED: python/fdars/__init__.py:69-77]

**Note:** `_augment` is imported but deliberately NOT listed in `__all__` (it is private).

### Exact Pattern for `advisor` Module (what Phase 11 must do)

`advisor` must follow the pure-Python module pattern:

1. Add `from fdars import advisor  # noqa: E402` after the existing pure-Python imports
2. Add `_sys.modules["fdars.advisor"] = advisor` so `from fdars import advisor` and `import fdars; fdars.advisor.build_diagnostics(...)` both resolve via the package namespace
3. Add `"advisor"` to `__all__`

The `sys.modules` injection is needed (unlike `datasets` etc.) because users may do `from fdars.advisor import build_diagnostics` — without it, `fdars.advisor` would not be findable as `sys.modules["fdars.advisor"]`. Compare with how the native loop does `_sys.modules[f"{__name__}.{_name}"] = _submod` for the same reason.

### `_augment.install()` Pattern (NOT needed for advisor)

`_augment.install()` injects helpers into native submodule namespaces by direct attribute assignment:
```python
def install():
    from fdars import clustering as _cl
    _cl.cluster_optim = _cluster_optim
    _cl.cluster_init = _cluster_init
```
[VERIFIED: python/fdars/_augment.py:82-87]

`advisor` does NOT need this treatment — it is a standalone module, not an extension to an existing native submodule.

---

## 3. `pyproject.toml` Optional-Dependency Extras

### Current Layout (verbatim)

```toml
[project.optional-dependencies]
plot = ["matplotlib>=3.6"]
dev = ["pytest", "matplotlib>=3.6"]
```
[VERIFIED: pyproject.toml:38-40]

### Stanza to Add

```toml
[project.optional-dependencies]
plot = ["matplotlib>=3.6"]
dev = ["pytest", "matplotlib>=3.6"]
advisor = ["anthropic>=0.72.0", "pydantic>=2.0"]
```

**Rationale for `pydantic>=2.0`:** `advisor.py` imports `pydantic.BaseModel` and uses `Literal`, `List` from pydantic. Pydantic v2 is required because v1 has a different `BaseModel` API and `messages.parse(output_format=...)` with Anthropic SDK 0.72+ requires pydantic v2 model instances. [ASSUMED — the exact floor may be pydantic v1-compatible; verify against `anthropic` SDK 0.72.0 release notes before pinning. The pydantic v2 requirement is standard for modern Anthropic structured output use.]

**`anthropic>=0.72.0` rationale:** Explicitly resolved in Phase 10: `ADVISOR_ANTHROPIC_MIN_VERSION = "0.72.0"` [VERIFIED: python/fdars/advisor.py:53]. This is the floor supporting `client.messages.parse(output_format=<PydanticModel>)` and `claude-opus-4-8`.

### Lazy Import + ImportError Guard Convention

The existing pattern from `advisor.py` (CORE-04 compliant) is:

```python
def _require_anthropic():
    try:
        import anthropic
    except ImportError as exc:
        raise ImportError(
            "The fdars advisor requires the anthropic SDK. "
            f"Install it with: pip install fdars[advisor]\n"
            f"Requires: anthropic>={ADVISOR_ANTHROPIC_MIN_VERSION}"
        ) from exc
    ...
    return anthropic
```
[VERIFIED: python/fdars/advisor.py:722-754]

This is already implemented and complete. Phase 11 does NOT change `advisor.py`'s internal guard — it only adds the extra to `pyproject.toml` so users can satisfy it with `pip install fdars[advisor]`.

---

## 4. Test Conventions & CI Network-Free Constraint

### Test Directory and Layout

```
tests/
  test_basic.py        — import/submodule smoke tests, function-level unit tests
  test_fdata_class.py  — Fdata class tests
  test_r_parity.py     — numerical parity tests against R reference values
```
[VERIFIED: Bash ls /home/simonm/projects/rust/pyfda/tests/]

No `conftest.py` inside `tests/`; the root-level `conftest.py` handles markdown-doc testing only. Unit tests in `tests/` are plain pytest classes/functions.

### CI Workflow: How Tests Run

`.github/workflows/ci.yml` runs Python tests: [VERIFIED: .github/workflows/ci.yml:50-77]

```yaml
- name: Create virtualenv and install dependencies
  run: |
    python -m venv .venv
    source .venv/bin/activate
    pip install maturin numpy pandas pytest

- name: Build and install
  run: |
    source .venv/bin/activate
    maturin develop --release

- name: Run tests
  run: |
    source .venv/bin/activate
    pytest tests/ -v
```

**Key observation:** CI installs ONLY `maturin numpy pandas pytest` — no `anthropic`, no `pydantic`. The `[advisor]` extra is NOT installed in CI. Therefore:
- Any test that imports `anthropic` directly must be guarded
- Any test that calls `advise()` without a key/package must skip or be guarded
- `build_diagnostics` and `describe_cluster_differences(run_llm=False)` are safe because they do not import `anthropic`

### Offline Unit Test Pattern

Existing idiom from `tests/test_r_parity.py` and `tests/test_basic.py`:
- Plain `class TestX: / def test_y(self):` structure, no fixtures
- `np.random.default_rng(seed)` for reproducibility
- `assert "key" in result` for dict structure checks
- `np.testing.assert_allclose(...)` for numerical assertions

No `conftest.py` fixtures are needed for the advisor tests; datasets are loaded via `fdars.datasets`.

### Dataset Loader API for Offline Tests

`python/fdars/datasets.py` provides loaders that read vendored CSVs from inside the installed package (via `importlib.resources`). [VERIFIED: python/fdars/datasets.py:1-102]

Available loaders and shapes:
- `load_canadian_weather()` → `Dataset` with `.data` (Fdata, 35×365), `.argvals` (days, 365), `.meta` (station, province, region, lat, lon)
- `load_growth()` → `Dataset` with `.data` (Fdata, 93×31), `.argvals` (ages, 31), `.meta` (id, sex)
- `load_tecator()` → `Dataset` with `.data` (Fdata, 240×100), `.argvals` (wavelengths, 100), `.meta` (moisture, fat, protein)
- `load_sonar()` → `Dataset` with `.data` (Fdata, 208×60)

The `Dataset.data` attribute is an `Fdata` object. To get the raw matrix: `dataset.data.data` (numpy array, shape rows=obs, cols=points).

**Recommended dataset for clustering test:** `load_canadian_weather()` — natural groupings by region, 35 observations, 365 time points. The `fdars.clustering.kmeans_fd` result dict has `centers`, `cluster`, `k` keys that `build_diagnostics(method="clustering")` consumes directly. [VERIFIED: tests/test_basic.py:97-107 — kmeans_fd returns `{"cluster": ..., "centers": ...}`]

### Env-Gated Integration Test Idiom

The existing project uses `pytest.importorskip("matplotlib")` [VERIFIED: tests/test_r_parity.py:445]. The exact idiom for `ANTHROPIC_API_KEY`-gated tests is:

```python
import os
import pytest

# At class or function level:
pytestmark = pytest.mark.skipif(
    not os.environ.get("ANTHROPIC_API_KEY"),
    reason="ANTHROPIC_API_KEY not set — skipping LLM integration test"
)
```

Or alternatively, for finer-grained control:

```python
def test_advise_integration():
    if not os.environ.get("ANTHROPIC_API_KEY"):
        pytest.skip("ANTHROPIC_API_KEY not set")
    pytest.importorskip("anthropic")
    pytest.importorskip("pydantic")
    ...
```

The `pytest.importorskip("anthropic")` form additionally verifies the package is installed (useful if someone sets the key but forgot to install the extra). Use BOTH guards: env-key check AND `importorskip`. This matches the matplotlib pattern already in the codebase.

**The test MUST NOT fail when `ANTHROPIC_API_KEY` is absent — it must SKIP.**

### Recommended Test File

Add `tests/test_advisor.py` with two test classes:

1. `TestAdvisorOffline` — exercises `build_diagnostics` for all 5 method branches using synthetic dicts and/or real datasets; tests `describe_cluster_differences(run_llm=False)`; tests `ImportError` guard when anthropic absent (monkeypatch `sys.modules`); fully offline, no skip conditions.

2. `TestAdvisorIntegration` — exercises `advise()` with `pytestmark = pytest.mark.skipif(not os.environ.get("ANTHROPIC_API_KEY"), ...)` — skipped in CI, runnable locally with a real key.

---

## 5. Recipe Page Format

### `examples/` Directory (Untracked)

The untracked `examples/` directory at the repo root contains standalone Python scripts (not markdown pages): [VERIFIED: Bash ls /home/simonm/projects/rust/pyfda/examples/]

```
examples/
  diagnostics.py          — standalone Python script with if __name__ == "__main__": block
  outlier_detection.py    — same pattern
  partial_predictor.py
  ...
```

These are standalone `.py` scripts, not MkDocs markdown pages. They are development-time notebooks/scripts, NOT part of the MkDocs `docs/examples/` documentation. [VERIFIED: examples/diagnostics.py:1-35 — standalone script with local imports, not markdown-exec]

The PYAPI-03 requirement says "An `examples/` recipe page demonstrates the advisor end-to-end against a real dataset." Given that `examples/` contains plain `.py` files and not `.md` files, and given that the docs examples at `docs/examples/` are MkDocs pages using `markdown-exec`, the most appropriate deliverable is a **standalone `.py` script** at `examples/advisor_recipe.py`, matching the pattern of the existing files.

**The MkDocs `docs/examples/` route would require:** adding a nav entry to `mkdocs.yml`, creating a new `.md` file in `docs/examples/`, and having markdown-exec run the code at docs-build time (which would require `ANTHROPIC_API_KEY` to be available during the build — a CI blocker). The standalone script avoids this entirely.

**Recommendation: `examples/advisor_recipe.py`** — runnable standalone Python script with:
- Dataset load via `fdars.datasets.load_canadian_weather()`
- Clustering via `fdars.clustering.kmeans_fd` or `cluster_optim`
- `build_diagnostics(result, method="clustering", argvals=day)` — offline stage
- Optional `describe_cluster_differences(result, argvals=day, domain_context="...", run_llm=True)` gated on `ANTHROPIC_API_KEY` presence (the script should degrade gracefully)
- Structured inspection of the returned `Advice` object

### Existing Script Pattern (verbatim from `examples/outlier_detection.py`)

```python
"""One-line description.

Multi-line prose about what the script demonstrates.

Dependencies: numpy, scipy, scikit-learn.
"""
# ... imports ...

if __name__ == "__main__":
    # ... demo code ...
```
[VERIFIED: examples/outlier_detection.py:1-15, 243-250]

**Chosen dataset for recipe:** `load_canadian_weather()` — natural groupings (Arctic/Atlantic/Continental/Pacific regions), 35 curves, 365 daily temperature points. The clustering result naturally demonstrates `build_diagnostics(method="clustering")` with interpretable cluster differences (temperature level, seasonal amplitude).

---

## 6. Architecture Patterns

### Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| `build_diagnostics` (offline) | Python package layer | — | Pure-Python computation; no native/Rust involvement |
| `advise` (LLM) | Python package layer | Anthropic API (external) | LLM call is a library call, not a service boundary in the package |
| Public API registration | Python package layer (`__init__.py`) | — | Submodule injection is a Python package concern |
| Optional dependency gating | pyproject.toml + `_require_anthropic()` | — | Standard Python extras pattern |
| Unit tests | `tests/` directory | CI via `.github/workflows/ci.yml` | Existing pytest infrastructure |

### Recommended Project Structure (additions only)

```
python/fdars/
  advisor.py           # EXISTS (Phase 10) — no changes needed
  __init__.py          # MODIFY: import advisor, sys.modules injection, __all__

pyproject.toml         # MODIFY: add [advisor] extra

tests/
  test_advisor.py      # CREATE: offline + env-gated integration tests

examples/
  advisor_recipe.py    # CREATE: standalone end-to-end recipe
```

---

## 7. Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Optional import guard with version check | Custom version-check logic | `_require_anthropic()` already in `advisor.py` | Already implemented correctly at lines 722-754 |
| Env-var based test skip | `os.environ` check + sys.exit | `pytest.mark.skipif` + `pytest.importorskip` | Integrates with pytest output; marks test as SKIP not ERROR |
| Package extras declaration | Custom install script | `pyproject.toml [project.optional-dependencies]` | Standard PEP 517 mechanism, works with pip and maturin |
| Dataset loading in tests | Reading CSV directly | `fdars.datasets.load_canadian_weather()` etc. | Vendored datasets load via `importlib.resources` from installed package |

---

## 8. Common Pitfalls

### Pitfall 1: Adding `advisor` to `_submodule_names`
**What goes wrong:** Planner adds `"advisor"` to the `_submodule_names` tuple, causing the loop to do `getattr(_native, "advisor")` — which raises `AttributeError` because `advisor` is not a Rust native submodule.
**Why it happens:** The native loop pattern looks identical to what's needed, and it's tempting to just add to the tuple.
**How to avoid:** `advisor` must be imported with a plain `from fdars import advisor` followed by manual `sys.modules` injection. See section 2 above.
**Warning signs:** `AttributeError: module '_native' has no attribute 'advisor'` on `import fdars`.

### Pitfall 2: Calling `advise` in an offline unit test
**What goes wrong:** A test that calls `advise()` (not `build_diagnostics`) runs in CI, which has no `anthropic` installed and no `ANTHROPIC_API_KEY`, causing the test to fail (not skip).
**Why it happens:** The developer expects the `ImportError` to surface as a test failure they can catch, but pytest treats unguarded `ImportError` during test collection as an error.
**How to avoid:** Guard any test calling `advise()` with BOTH `pytest.importorskip("anthropic")` AND `pytest.mark.skipif(not os.environ.get("ANTHROPIC_API_KEY"), ...)`.

### Pitfall 3: `describe_cluster_differences` requires clustering result structure
**What goes wrong:** Test passes a plain `{"data": ..., "argvals": ...}` dict expecting `build_diagnostics` to call `fdars.clustering.kmeans_fd` automatically — it does not.
**Why it happens:** `_build_clustering_diagnostics` Branch B only triggers when `data` and `argvals` kwargs are provided. The offline path (Branch A) expects `centers`, `cluster`, `k` in the result dict.
**How to avoid:** Offline tests must provide a dict with `centers` (k×m array), `cluster` (n labels), `k` keys. Run `fdars.clustering.kmeans_fd(data, argvals, k=4)` first, then pass its output to `build_diagnostics`. [VERIFIED: python/fdars/advisor.py:619-626]

### Pitfall 4: `pydantic` not listed as optional dependency
**What goes wrong:** User runs `pip install fdars[advisor]` which installs `anthropic` but not `pydantic`. Calling `advise()` fails with `ImportError` from `_require_pydantic()`.
**Why it happens:** `anthropic>=0.72.0` does not automatically pull in `pydantic` as a hard dependency.
**How to avoid:** List both `anthropic>=0.72.0` AND `pydantic>=2.0` in the `[advisor]` extra stanza in `pyproject.toml`.

### Pitfall 5: `advisor` recipe in `docs/examples/` requires network during build
**What goes wrong:** Adding an advisor page to `docs/examples/` as a markdown-exec page means `mkdocs build` would call `advise()` at build time, which requires `ANTHROPIC_API_KEY` in CI.
**Why it happens:** `markdown-exec` runs Python fences at build time; the docs CI job does not have API keys.
**How to avoid:** Keep the recipe as a standalone `examples/advisor_recipe.py` script, not a markdown-exec docs page. If a docs page is desired later, it must use `run_llm=False` for the inline example and show pre-computed output.

### Pitfall 6: Clustering `argvals` kwarg vs result dict format
**What goes wrong:** `describe_cluster_differences` receives a clustering result from `cluster_optim` (which returns `best_k`, `cluster`, `centers`, `scores`, etc.) and the `argvals` grid is passed as a kwarg, but it is not forwarded correctly.
**Why it happens:** `cluster_optim` returns a superset dict; `_build_clustering_diagnostics` reads `centers`, `cluster`, `k` keys. `k` is present as `best_k` in `cluster_optim` output — not as `k`. This means passing `cluster_optim` output directly will silently produce `diag["k"] = len(centers)` (fallback) rather than an error.
**How to avoid:** Either (a) use `kmeans_fd` directly (which returns `{"centers": ..., "cluster": ..., "k": ...}`) or (b) normalize the `cluster_optim` output before passing to `build_diagnostics`. The recipe should use `kmeans_fd(data, argvals, k=4)` directly for clarity. [VERIFIED: python/fdars/advisor.py:619-625 — `k_raw = raw.get("k")`]

---

## 9. Code Examples

### PYAPI-01: Wire `advisor` into `__init__.py`

```python
# In python/fdars/__init__.py, after the existing pure-Python imports:
from fdars import advisor  # noqa: E402

# sys.modules injection so `from fdars.advisor import build_diagnostics` works:
_sys.modules["fdars.advisor"] = advisor

# In __all__:
__all__ = [
    "Fdata",
    *(_submodule_names),
    "datasets",
    "results",
    "plot",
    "metrics",
    "covariance",
    "advisor",          # ADD THIS
]
```

### PYAPI-02: Offline unit test structure

```python
# tests/test_advisor.py
import numpy as np
import pytest
import os


class TestBuildDiagnosticsOffline:
    """Offline tests — no LLM, no network, no anthropic required."""

    def test_clustering_offline_with_synthetic(self):
        from fdars.advisor import build_diagnostics
        result = {
            "centers": [[0.0, 1.0, 0.0], [0.0, -1.0, 0.0]],
            "cluster": [0, 0, 1, 1],
            "k": 2,
        }
        diag = build_diagnostics(result, method="clustering")
        assert diag["method"] == "clustering"
        assert diag["k"] == 2
        assert diag["cluster_sizes"] == [2, 2]

    def test_clustering_with_real_dataset(self):
        from fdars import datasets, clustering
        from fdars.advisor import build_diagnostics
        ds = datasets.load_canadian_weather()
        X = np.asarray(ds.data.data, dtype=float)
        day = np.asarray(ds.argvals, dtype=float)
        result = clustering.kmeans_fd(X, day, k=4, seed=42)
        diag = build_diagnostics(result, method="clustering", argvals=day)
        assert diag["method"] == "clustering"
        assert diag["k"] == 4
        assert len(diag["cluster_sizes"]) == 4
        assert diag["pairwise_amplitude_distance"] is not None

    def test_describe_cluster_differences_offline(self):
        from fdars.advisor import describe_cluster_differences
        result = {"centers": [[0.0, 1.0, 0.0], [0.0, -1.0, 0.0]],
                  "cluster": [0, 0, 1, 1], "k": 2}
        diag = describe_cluster_differences(
            result, argvals=[0.0, 0.5, 1.0], run_llm=False
        )
        assert diag["method"] == "clustering"

    def test_advise_raises_importerror_without_anthropic(self, monkeypatch):
        import sys
        monkeypatch.setitem(sys.modules, "anthropic", None)
        from fdars.advisor import advise, build_diagnostics
        diag = build_diagnostics(
            {"mean": [0.0, 1.0, 0.0], "converged": True, "n_iter": 3},
            method="alignment",
        )
        with pytest.raises(ImportError, match="pip install fdars\\[advisor\\]"):
            advise(diag, task="interpretation", domain_context="test")

    def test_build_diagnostics_deterministic(self):
        from fdars.advisor import build_diagnostics
        result = {"n_basis_values": [5, 8, 10], "gcv": [0.5, 0.3, 0.4], "edf": [3.0, 5.0, 7.0]}
        d1 = build_diagnostics(result, method="basis")
        d2 = build_diagnostics(result, method="basis")
        assert d1 == d2


class TestAdvisorIntegration:
    """LLM integration tests — skipped in CI without ANTHROPIC_API_KEY."""

    pytestmark = pytest.mark.skipif(
        not os.environ.get("ANTHROPIC_API_KEY"),
        reason="ANTHROPIC_API_KEY not set — skipping LLM integration test"
    )

    def test_advise_returns_advice_schema(self):
        pytest.importorskip("anthropic")
        pytest.importorskip("pydantic")
        from fdars.advisor import build_diagnostics, advise, Advice
        result = {"n_basis_values": [5, 8, 10], "gcv": [0.5, 0.3, 0.4]}
        diag = build_diagnostics(result, method="basis")
        advice = advise(diag, task="parameter", domain_context="NIR spectroscopy")
        assert isinstance(advice, Advice)
        assert isinstance(advice.interpretation, str)
        assert isinstance(advice.recommendations, list)
```

### PYAPI-03: Recipe script skeleton

```python
# examples/advisor_recipe.py
"""fdars AI advisor — end-to-end recipe.

Demonstrates the advisor workflow:
  1. Load a real dataset (Canadian Weather).
  2. Cluster the temperature curves with kmeans_fd.
  3. Build offline diagnostics with build_diagnostics.
  4. Optionally get grounded LLM interpretation (requires ANTHROPIC_API_KEY).

Run:
    pip install fdars[advisor]
    ANTHROPIC_API_KEY=sk-... python examples/advisor_recipe.py
"""
import os
import numpy as np
import fdars
from fdars import datasets, clustering
from fdars.advisor import build_diagnostics, describe_cluster_differences

# Step 1: Load data
ds = datasets.load_canadian_weather()
X = np.asarray(ds.data.data, dtype=float)   # (35, 365)
day = np.asarray(ds.argvals, dtype=float)    # (365,)

# Step 2: Cluster
result = clustering.kmeans_fd(X, day, k=4, seed=42)
print(f"Cluster assignments: {result['cluster']}")

# Step 3: Build offline diagnostics
diag = build_diagnostics(result, method="clustering", argvals=day)
print(f"Cluster sizes: {diag['cluster_sizes']}")
print(f"Mean amplitude separation: {diag['mean_amplitude_separation']:.4f}")

# Step 4: Optional LLM interpretation
if os.environ.get("ANTHROPIC_API_KEY"):
    advice = describe_cluster_differences(
        result,
        argvals=day,
        domain_context=(
            "35 Canadian weather stations clustered by daily temperature curve. "
            "4 climate regions: Arctic, Atlantic, Continental, Pacific."
        ),
        run_llm=True,
    )
    print("\n--- Advisor interpretation ---")
    print(advice.interpretation)
    for rec in advice.recommendations:
        print(f"[{rec.kind}] {rec.action}")
else:
    print("\nSet ANTHROPIC_API_KEY to get LLM interpretation.")
    print("Offline diagnostics available in `diag` dict above.")
```

---

## 10. State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Optional deps not declared | `[project.optional-dependencies]` extras in pyproject.toml | PEP 517/518 standard | `pip install fdars[advisor]` works |
| Submodule injection via `getattr(_native, name)` | Plain `from fdars import module` for pure-Python modules | Existing pattern in `__init__.py` | `advisor` must follow the pure-Python path |

---

## 11. Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3.9+ | All | ✓ | 3.14 (local), 3.10/3.12/3.13 (CI) | — |
| `fdars` (compiled) | All tests | ✓ | 0.2.0 | — |
| `pytest` | Tests | ✓ | 9.0.3 (local) | — |
| `numpy` | `build_diagnostics` | ✓ | Installed | — |
| `anthropic>=0.72.0` | `advise()` only | Not in CI | Not installed in CI | Skip test via `pytestmark` |
| `pydantic>=2.0` | `advise()` only | Not in CI | Not installed in CI | Skip test; offline path uses stand-ins |

**Missing dependencies with no fallback:** None that block offline functionality.
**Missing dependencies with fallback:** `anthropic` and `pydantic` — integration tests skip cleanly.

---

## 12. Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest 9.0.3 (local), installed via `pip install pytest` in CI |
| Config file | None — no `pytest.ini`, `setup.cfg [tool:pytest]`, or `pyproject.toml [tool.pytest]` detected |
| Quick run command | `pytest tests/test_advisor.py -v` |
| Full suite command | `pytest tests/ -v` |

### Phase Requirements to Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| PYAPI-01 | `fdars.advisor.build_diagnostics` reachable | smoke | `pytest tests/test_advisor.py::TestBuildDiagnosticsOffline::test_clustering_offline_with_synthetic -x` | No — Wave 0 |
| PYAPI-01 | `from fdars.advisor import advise` reachable | smoke | `pytest tests/test_basic.py::test_submodules -x` (extend to include advisor) | Partial — extend existing |
| PYAPI-02 | `build_diagnostics` works offline with real dataset | unit | `pytest tests/test_advisor.py::TestBuildDiagnosticsOffline -x` | No — Wave 0 |
| PYAPI-02 | LLM test skips without key (not fails) | integration | `pytest tests/test_advisor.py::TestAdvisorIntegration -v` | No — Wave 0 |
| PYAPI-03 | Recipe script runs without key | smoke | `python examples/advisor_recipe.py` (without key set) | No — Wave 0 |

### Sampling Rate

- **Per task commit:** `pytest tests/test_advisor.py -v`
- **Per wave merge:** `pytest tests/ -v`
- **Phase gate:** Full suite green before `/gsd-verify-work`

### Wave 0 Gaps

- [ ] `tests/test_advisor.py` — covers PYAPI-01 (API reachability), PYAPI-02 (offline + env-gated)
- [ ] `examples/advisor_recipe.py` — covers PYAPI-03 (end-to-end recipe)

---

## 13. Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | No | — |
| V3 Session Management | No | — |
| V4 Access Control | No | — |
| V5 Input Validation | Yes | `build_diagnostics` validates `method` arg; raises `ValueError` for unknown methods [VERIFIED: python/fdars/advisor.py:226-232] |
| V6 Cryptography | No | — |

### Known Threat Patterns

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| API key in source code | Information Disclosure | Key read from env via `anthropic.Anthropic()` — never hardcoded [VERIFIED: python/fdars/advisor.py:955] |
| User data sent to Anthropic API | Information Disclosure | Accepted risk — user explicitly calls `advise()`; documented in Phase 10 threat model (T-10-01) |
| Prompt injection via `domain_context` | Tampering | Mitigated by system prompt structure; LLM only reasons over numeric diagnostics; no tool execution |

---

## 14. Package Legitimacy Audit

No new packages are introduced by this phase. The phase only declares existing packages as optional dependencies in `pyproject.toml`. The `anthropic` SDK was already evaluated in Phase 10 (ADVISOR_ANTHROPIC_MIN_VERSION = "0.72.0" resolved). [VERIFIED: python/fdars/advisor.py:53]

**Packages removed due to SLOP verdict:** None
**Packages flagged as suspicious:** None (no new packages)

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `pydantic>=2.0` is the correct floor for the `[advisor]` extra (v1 may also work with the fallback classes) | Section 3 | If pydantic v1 is sufficient, the version floor is unnecessarily strict — low risk since v2 is now universally standard |
| A2 | The `examples/` directory at repo root is the intended location for PYAPI-03 recipe (not a new `docs/examples/advisor-*.md` page) | Section 5 | If docs page is required, the markdown-exec at build time would require ANTHROPIC_API_KEY in CI — a CI blocker that would need architecture changes |

---

## Open Questions

1. **`pydantic` version floor**
   - What we know: `advisor.py` uses `pydantic.BaseModel`, `Literal`, `List`; these work in both v1 and v2 syntax
   - What's unclear: Whether `anthropic>=0.72.0`'s `messages.parse(output_format=...)` requires pydantic v2 specifically
   - Recommendation: Use `pydantic>=2.0` to match modern ecosystem; it's a safe default for new extras

2. **Recipe as docs page vs standalone script**
   - What we know: `examples/` contains `.py` scripts; `docs/examples/` contains markdown-exec `.md` pages; the docs build requires fdars but not the `[advisor]` extra
   - What's unclear: Whether the team wants an advisor page in the MkDocs nav eventually
   - Recommendation: Ship as `examples/advisor_recipe.py` now; a docs page can be added in a follow-up when a strategy for pre-computed output is established

3. **`test_basic.py::test_submodules` extension**
   - What we know: `test_submodules` currently imports all 16 native submodules; it does not import `advisor`
   - What's unclear: Whether to extend this test or leave it to `test_advisor.py`
   - Recommendation: Add `from fdars import advisor` to `test_submodules` to catch regressions in `__init__.py` wiring

---

## Sources

### Primary (HIGH confidence)
- `python/fdars/advisor.py` (full file read this session) — all function signatures, `__all__`, `ADVISOR_ANTHROPIC_MIN_VERSION`
- `python/fdars/__init__.py` (full file read this session) — injection pattern, `_submodule_names`, `__all__`
- `python/fdars/_augment.py` (full file read this session) — `install()` pattern
- `pyproject.toml` (full file read this session) — existing extras layout
- `tests/test_basic.py`, `tests/test_r_parity.py` (read this session) — test conventions
- `.github/workflows/ci.yml` (read this session) — CI install commands and network constraints
- `conftest.py` (read this session) — root conftest scope and conventions
- `examples/diagnostics.py`, `examples/outlier_detection.py` (read this session) — recipe script pattern
- `.planning/phases/10-advisor-core-primitive/10-01-SUMMARY.md` through `10-03-SUMMARY.md` (read this session) — Phase 10 decisions and deliverables

### Secondary (MEDIUM confidence)
- `docs/data/README.md` (read this session) — dataset descriptions and shapes
- `python/fdars/datasets.py` (partial read this session) — loader API

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — all patterns verified from source files read this session
- Architecture: HIGH — injection pattern and test idioms directly cited with file:line
- Pitfalls: HIGH — derived from reading actual source code and test structure

**Research date:** 2026-08-09
**Valid until:** 2026-09-09 (stable internal patterns; only stale if `__init__.py` or `advisor.py` change significantly)
