---
phase: 11-python-api-surface
plan: "02"
subsystem: python-package
tags: [testing, advisor, offline, env-gated, tdd]
status: complete

dependency_graph:
  requires: [11-01-PLAN.md]
  provides: [full TestBuildDiagnosticsOffline suite, TestAdvisorIntegration env-gated class]
  affects: [tests/test_advisor.py]

tech_stack:
  added: []
  patterns: [pytest monkeypatch, pytest.mark.skipif, pytest.importorskip, env-gated integration test]

key_files:
  created: []
  modified:
    - tests/test_advisor.py

decisions:
  - "test_clustering_with_real_dataset uses kmeans_fd directly (not cluster_optim) per Pitfall 6 — k derived from centers.shape[0] since kmeans_fd does not return k key"
  - "test_advise_raises_importerror_without_anthropic placed in TestBuildDiagnosticsOffline (not integration class) because monkeypatch guarantees offline behavior regardless of installed packages"
  - "TestAdvisorIntegration uses class-level pytestmark + per-method importorskip(anthropic)+importorskip(pydantic) belt-and-suspenders per RESEARCH.md Pitfall 2"

metrics:
  duration: "2 minutes"
  completed: "2026-08-09"
  tasks_completed: 3
  commits: 1

actuals:
  tokens: 6200
  tasks: 3
  commits: 1
---

# Phase 11 Plan 02: Expand offline + integration tests for advisor — Summary

**One-liner:** Full `TestBuildDiagnosticsOffline` suite (real dataset, determinism, ImportError guard) plus env-gated `TestAdvisorIntegration` class; all offline tests pass network-free, integration test skips cleanly without `ANTHROPIC_API_KEY`.

## What Was Built

One file expanded: `tests/test_advisor.py` grew from 1 test to 5 tests across 2 classes:

**`TestBuildDiagnosticsOffline` — 4 tests (all offline, no network, no anthropic):**

1. `test_clustering_offline_with_synthetic` — (11-01 tracer, kept intact) synthetic dict with known cluster structure
2. `test_clustering_with_real_dataset` — loads Canadian weather via `fdars.datasets`, runs `clustering.kmeans_fd(X, day, k=4, seed=42)`, passes result to `build_diagnostics(method="clustering", argvals=day)`, asserts `method=="clustering"`, `k==4`, `len(cluster_sizes)==4`, `pairwise_amplitude_distance is not None`
3. `test_build_diagnostics_deterministic` — builds diagnostics twice on a fixed `method="basis"` result dict, asserts `d1 == d2`
4. `test_advise_raises_importerror_without_anthropic` — monkeypatches `sys.modules["anthropic"] = None`, verifies `build_diagnostics(method="alignment")` succeeds offline, then asserts `advise()` raises `ImportError` matching `pip install fdars\[advisor\]`

**`TestAdvisorIntegration` — 1 test (skipped without key):**

5. `test_advise_returns_advice_schema` — class-level `pytestmark = pytest.mark.skipif(not os.environ.get("ANTHROPIC_API_KEY"), ...)` plus `pytest.importorskip("anthropic")` and `pytest.importorskip("pydantic")` belt-and-suspenders; calls `advise(diag, task="parameter", ...)` and asserts `isinstance(advice, Advice)`, `isinstance(advice.interpretation, str)`, `isinstance(advice.recommendations, list)`

## Verification Evidence

All plan-level verifications passed:

```
pytest tests/test_advisor.py::TestBuildDiagnosticsOffline -q
....
4 passed in 2.39s

pytest tests/test_advisor.py::TestAdvisorIntegration -v
SKIPPED [100%] (ANTHROPIC_API_KEY not set — skipping LLM integration test)
1 skipped in 0.06s

pytest tests/ -q
104 passed, 1 skipped in 3.05s
```

Full suite: **104 tests passed, 1 skipped** (no regressions; +3 tests from 11-01's 101).

## Commits

| Task | Commit | Message |
|------|--------|---------|
| 1+2+3 | 9936a70 | test(11-02): expand TestBuildDiagnosticsOffline + add TestAdvisorIntegration |

## Deviations from Plan

**[Rule 1 - Auto-investigate] kmeans_fd does not return `k` key**

- **Found during:** Task 1 pre-implementation check
- **Issue:** `kmeans_fd` returns `{"cluster", "centers", "tot_withinss", "iter", "converged"}` — no `k` key. The plan's `test_clustering_with_real_dataset` assertion `assert diag["k"] == 4` would fail if `_build_clustering_diagnostics` required an explicit `k` key.
- **Fix:** None needed — confirmed that `advisor.py:625` already handles missing `k` via `int(centers.shape[0])` fallback. Test passes correctly (diag["k"] == 4 derived from centers.shape[0]).
- **Files modified:** None — documentation only (confirmed existing behavior).
- **Commit:** N/A (no code change required)

All three plan-level tasks were committed in one commit since they all expand the same file atomically. No architecture changes or new dependencies.

## Known Stubs

None. All deliverables are fully wired:
- `TestBuildDiagnosticsOffline` has 4 passing offline tests
- `TestAdvisorIntegration` skips cleanly without `ANTHROPIC_API_KEY`
- No anthropic import in any offline test path

## Threat Surface Scan

No new security-relevant surface introduced:
- T-11-04 (CI network access): mitigated — integration test gated by `pytest.mark.skipif` + `importorskip`
- T-11-05 (API key in tests): mitigated — no key hardcoded; all key handling delegated to `advisor.py` via env
- T-11-01 (user data → Anthropic): accepted — only occurs when user explicitly sets key and runs integration test

## Self-Check

- [x] `tests/test_advisor.py` modified: 4 offline tests + 1 env-gated integration test
- [x] Commit 9936a70 exists
- [x] `pytest tests/test_advisor.py::TestBuildDiagnosticsOffline -q` → 4 passed
- [x] `pytest tests/test_advisor.py::TestAdvisorIntegration -v` → 1 skipped (ANTHROPIC_API_KEY not set)
- [x] `pytest tests/ -q` → 104 passed, 1 skipped

## Self-Check: PASSED
