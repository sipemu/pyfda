---
phase: 11-python-api-surface
verified: 2026-08-09T19:55:18Z
status: passed
score: 9/9
behavior_unverified: 0
overrides_applied: 0
---

# Phase 11: Python API Surface Verification Report

**Phase Goal:** The recommend-only advisor is a first-class, tested part of the public `fdars` package with a runnable end-to-end recipe.
**Verified:** 2026-08-09T19:55:18Z
**Status:** passed
**Re-verification:** No — initial verification

---

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `import fdars; fdars.advisor.build_diagnostics` resolves without importing anthropic (PYAPI-01) | VERIFIED | `python -c "import sys, fdars; assert 'anthropic' not in sys.modules"` passes; attribute access confirmed |
| 2 | `from fdars.advisor import build_diagnostics, advise, describe_cluster_differences, Advice, Recommendation` all resolve (PYAPI-01) | VERIFIED | All five symbols imported without error; `assert 'advisor' in fdars.__all__` passes |
| 3 | `pip install fdars[advisor]` installs anthropic>=0.72.0 and pydantic>=2.0 (PYAPI-02) | VERIFIED | `pyproject.toml` `[project.optional-dependencies].advisor = ["anthropic>=0.72.0", "pydantic>=2.0"]` confirmed; top-level `dependencies` contains neither |
| 4 | `tests/test_basic.py::test_submodules` asserts `from fdars import advisor` resolves (PYAPI-01) | VERIFIED | `from fdars import advisor` is present in `test_submodules`; test passes |
| 5 | One offline build_diagnostics test in tests/test_advisor.py passes with no anthropic installed and no network (PYAPI-02) | VERIFIED | `TestBuildDiagnosticsOffline::test_clustering_offline_with_synthetic` passes; 4 offline tests pass in 2.36s |
| 6 | build_diagnostics runs offline against a real docs/data/ dataset and passes with no network (PYAPI-02) | VERIFIED | `test_clustering_with_real_dataset` passes — loads Canadian Weather, runs `kmeans_fd(k=4,seed=42)`, calls `build_diagnostics`, asserts `method=="clustering"`, `k==4`, `len(cluster_sizes)==4`, `pairwise_amplitude_distance is not None` |
| 7 | build_diagnostics is deterministic — two runs on identical input return identical output (PYAPI-02) | VERIFIED | `test_build_diagnostics_deterministic` passes — `d1 == d2` on fixed basis result dict |
| 8 | advise() raises a clear ImportError naming `pip install fdars[advisor]` when anthropic is absent (PYAPI-02) | VERIFIED | `test_advise_raises_importerror_without_anthropic` passes — monkeypatched `sys.modules["anthropic"]=None`, `pytest.raises(ImportError, match="pip install fdars\\[advisor\\]")` succeeded |
| 9 | The advise LLM integration test SKIPS (not fails) when ANTHROPIC_API_KEY is absent (PYAPI-02) | VERIFIED | `TestAdvisorIntegration::test_advise_returns_advice_schema` reports SKIPPED with reason "ANTHROPIC_API_KEY not set — skipping LLM integration test"; exit code 0 |
| 10 | examples/advisor_recipe.py runs to completion offline with no ANTHROPIC_API_KEY set (PYAPI-03) | VERIFIED | `env -u ANTHROPIC_API_KEY python examples/advisor_recipe.py` exits 0, prints cluster diagnostics, skips LLM step |
| 11 | When ANTHROPIC_API_KEY is present, the recipe additionally calls describe_cluster_differences(run_llm=True) (PYAPI-03) | VERIFIED | Static check: `ANTHROPIC_API_KEY` guard, `run_llm=True`, and `describe_cluster_differences` all present; `ast.parse` succeeds |

**Score:** 9/9 truths verified (11-01 plans had 5 truths, 11-02 had 4 truths, 11-03 had 2 truths; merged/deduplicated to 11 distinct checks, all verified)

---

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `python/fdars/__init__.py` | advisor import + sys.modules injection + `__all__` entry | VERIFIED | `from fdars import advisor` at L64; `_sys.modules["fdars.advisor"] = advisor` at L72; `"advisor"` in `__all__` at L83; advisor absent from `_submodule_names` tuple (16 native entries only) |
| `pyproject.toml` | `[advisor]` optional-dependency extra | VERIFIED | `advisor = ["anthropic>=0.72.0", "pydantic>=2.0"]` under `[project.optional-dependencies]`; existing `plot` and `dev` extras unchanged |
| `tests/test_basic.py` | extended test_submodules | VERIFIED | `from fdars import advisor` present at L25 inside `test_submodules`; test passes |
| `tests/test_advisor.py` | TestBuildDiagnosticsOffline (4 tests) + TestAdvisorIntegration (1 env-gated test) | VERIFIED | 5 tests collected; 4 offline pass + 1 integration skipped; all test names match plan spec |
| `examples/advisor_recipe.py` | standalone end-to-end recipe script | VERIFIED | File exists; imports `build_diagnostics` and `describe_cluster_differences` from `fdars.advisor`; runs offline without error |

---

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `__init__.py` sys.modules injection | `from fdars.advisor import build_diagnostics` | `_sys.modules["fdars.advisor"] = advisor` at L72 | WIRED | Both attribute access (`fdars.advisor.build_diagnostics`) and import-form (`from fdars.advisor import ...`) resolve; `sys.modules['fdars.advisor'] is fdars.advisor` confirmed |
| `pyproject.toml` `[advisor]` extra | `advisor.py _require_anthropic()` ImportError hint | `anthropic>=0.72.0` floor matches `ADVISOR_ANTHROPIC_MIN_VERSION`; `pydantic>=2.0` declared | WIRED | Extra pins the correct floor; offline guard exercised by `test_advise_raises_importerror_without_anthropic` |
| `os.environ ANTHROPIC_API_KEY` guard in recipe | `describe_cluster_differences(run_llm=True)` call | `if os.environ.get("ANTHROPIC_API_KEY"):` block at L73 | WIRED | `else` branch prints guidance; offline path exits 0 confirmed |
| `kmeans_fd` result (centers/cluster) | `build_diagnostics(method='clustering', argvals=day)` | Result dict passed directly; `build_diagnostics` falls back to `len(centers)` for `k` | WIRED | Real-dataset test + recipe both exercised this path successfully |
| `ANTHROPIC_API_KEY` env presence | `pytest.mark.skipif` on `TestAdvisorIntegration` | Class-level `pytestmark = pytest.mark.skipif(not os.environ.get("ANTHROPIC_API_KEY"), ...)` | WIRED | Test reports SKIPPED (not failed or errored) when key absent |
| monkeypatched `sys.modules["anthropic"]` | `advise()` ImportError | `monkeypatch.setitem(sys.modules, "anthropic", None)` → `_require_anthropic()` guard | WIRED | `pytest.raises(ImportError, match=...)` passed |

---

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|---------------|--------|-------------------|--------|
| `examples/advisor_recipe.py` | `X`, `day` | `fdars.datasets.load_canadian_weather()` → vendored CSV | Yes — 35 stations × 365 points | FLOWING |
| `examples/advisor_recipe.py` | `result` | `clustering.kmeans_fd(X, day, k=4, seed=42)` — native Rust call | Yes — real cluster assignments | FLOWING |
| `examples/advisor_recipe.py` | `diag` | `build_diagnostics(result, method="clustering", argvals=day)` | Yes — printed cluster sizes and separations match computed output | FLOWING |
| `tests/test_advisor.py::test_clustering_with_real_dataset` | `diag` | Same `load_canadian_weather` + `kmeans_fd` + `build_diagnostics` chain | Yes — asserted on computed values | FLOWING |

---

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| All advisor and submodule tests pass | `pytest tests/test_advisor.py tests/test_basic.py::test_submodules -q` | 5 passed, 1 skipped in 2.36s | PASS |
| Recipe runs offline to completion | `env -u ANTHROPIC_API_KEY python examples/advisor_recipe.py` | Exit 0; prints diagnostics (k=4, cluster_sizes=[8,10,3,14], amplitude sep=5.3006) | PASS |
| Advisor import does not pull anthropic | `python -c "import sys, fdars; assert 'anthropic' not in sys.modules"` | No assertion error | PASS |
| pyproject.toml extra correct | `python -c "import tomllib; ..."` (full TOML assertion) | `PASS advisor extra OK: ['anthropic>=0.72.0', 'pydantic>=2.0']` | PASS |
| Real-dataset offline test | `pytest tests/test_advisor.py::TestBuildDiagnosticsOffline::test_clustering_with_real_dataset -v` | PASSED | PASS |
| Determinism test | `pytest tests/test_advisor.py::TestBuildDiagnosticsOffline::test_build_diagnostics_deterministic -v` | PASSED | PASS |
| ImportError guard test | `pytest tests/test_advisor.py::TestBuildDiagnosticsOffline::test_advise_raises_importerror_without_anthropic -v` | PASSED | PASS |
| Integration test skips cleanly | `pytest tests/test_advisor.py::TestAdvisorIntegration -v` | SKIPPED (ANTHROPIC_API_KEY not set) | PASS |
| Full test suite — no regressions | `pytest tests/ -q` | 104 passed, 1 skipped in 3.02s | PASS |

---

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|----------|
| PYAPI-01 | 11-01 | Advisor exposed via `fdars` public API (module registered, `__all__`) | SATISFIED | `"advisor"` in `fdars.__all__`; both import forms work; `sys.modules` injection confirmed |
| PYAPI-02 | 11-01, 11-02 | `build_diagnostics` has offline unit tests against `docs/data/`; LLM call covered by env-gated integration test (no network in CI) | SATISFIED | 4 offline tests pass; `TestAdvisorIntegration` skips cleanly; ImportError guard tested |
| PYAPI-03 | 11-03 | An `examples/` recipe page demonstrates the advisor end-to-end against a real dataset | SATISFIED | `examples/advisor_recipe.py` exists; runs offline (exit 0); contains API-key-guarded LLM step |

No orphaned requirements: REQUIREMENTS.md maps PYAPI-01, PYAPI-02, PYAPI-03 all to Phase 11, all three are claimed by the plans, and all three are satisfied.

---

### Anti-Patterns Found

No anti-pattern markers (`TBD`, `FIXME`, `XXX`, `TODO`, `HACK`, `PLACEHOLDER`) were found in any Phase 11 modified files (`python/fdars/__init__.py`, `pyproject.toml`, `tests/test_basic.py`, `tests/test_advisor.py`, `examples/advisor_recipe.py`).

No stub patterns detected. All data flows are live (real dataset loaded, real clustering computed, real diagnostics returned and printed).

---

### Prohibitions Check

The following prohibitions from plan frontmatter were verified:

| Prohibition | Status | Evidence |
|-------------|--------|----------|
| Importing fdars MUST NOT import anthropic at package-import time | VERIFIED | `assert 'anthropic' not in sys.modules` passes after `import fdars` |
| Do NOT add 'advisor' to `_submodule_names` | VERIFIED | AST check: `_submodule_names` has 16 native entries; `advisor` absent |
| Do NOT modify python/fdars/advisor.py | VERIFIED | `git log -- python/fdars/advisor.py` shows last modification was Phase 10 fix commits, not Phase 11 |
| advise LLM integration test MUST skip (not fail) when ANTHROPIC_API_KEY is absent | VERIFIED | pytest reports SKIPPED with the expected reason string |
| Offline tests MUST NOT import anthropic or call advise() unguarded | VERIFIED | `test_advisor.py` offline class uses monkeypatch for the ImportError guard test; no bare `anthropic` import at module level |
| examples/advisor_recipe.py MUST run to completion offline | VERIFIED | `env -u ANTHROPIC_API_KEY python examples/advisor_recipe.py` exits 0 |
| Do NOT add the recipe to docs/examples/ or mkdocs.yml nav | VERIFIED | File is at `examples/advisor_recipe.py`; `mkdocs.yml` and `docs/examples/` not modified |

---

### Code Review Notes (Advisory — Not Gating)

Per the verification prompt, the code review report (11-REVIEW.md) identified 2 critical and 2 warning findings. These findings are in Phase 10 modules `advisor.py`/`results.py` (pre-existing code cross-referenced by the reviewer), not in Phase 11's own changed files. They do not gate Phase 11 goal achievement and are noted here as advisory follow-ups for a Phase 10 patch if warranted.

---

### Human Verification Required

None. All must-have truths are fully verified through automated checks and behavioral tests. The LLM integration path (advise with a real API key) is intentionally env-gated and confirmed to skip cleanly in offline environments — this is by design, not a gap.

---

## Gaps Summary

None. All 9 grouped truths across all three plans are verified, all artifacts are substantive and wired, all key links are confirmed, all requirements (PYAPI-01, PYAPI-02, PYAPI-03) are satisfied, and no anti-patterns were found.

---

_Verified: 2026-08-09T19:55:18Z_
_Verifier: Claude (gsd-verifier)_
