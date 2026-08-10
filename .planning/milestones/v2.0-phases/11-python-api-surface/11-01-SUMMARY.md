---
phase: 11-python-api-surface
plan: "01"
subsystem: python-package
tags: [packaging, api-surface, testing, advisor]
status: complete

dependency_graph:
  requires: [10-03-PLAN.md]
  provides: [fdars.advisor public API, [advisor] optional extra, offline test coverage]
  affects: [python/fdars/__init__.py, pyproject.toml, tests/]

tech_stack:
  added: []
  patterns: [pure-Python submodule injection, sys.modules registration, optional-dependency extras]

key_files:
  created:
    - tests/test_advisor.py
  modified:
    - python/fdars/__init__.py
    - pyproject.toml
    - tests/test_basic.py

decisions:
  - "advisor wired via plain 'from fdars import advisor' + sys.modules injection (not added to _submodule_names — it is pure-Python, not a native Rust submodule)"
  - "pydantic>=2.0 included in [advisor] extra alongside anthropic>=0.72.0 (Pitfall 4: anthropic SDK does not auto-pull pydantic)"
  - "test_advisor.py TestBuildDiagnosticsOffline uses synthetic clustering result dict (centers/cluster/k) not raw data — matches advisor.py Branch A offline path"

metrics:
  duration: "2 minutes"
  completed: "2026-08-09"
  tasks_completed: 3
  commits: 3

actuals:
  tokens: 3200
  tasks: 3
  commits: 3
---

# Phase 11 Plan 01: Wire advisor into public fdars API — Summary

**One-liner:** JWT-style submodule injection + sys.modules registration makes `fdars.advisor` a first-class public API, with `[advisor]` optional extra pinning `anthropic>=0.72.0` + `pydantic>=2.0`.

## What Was Built

Three changes implement the tracer slice that proves `fdars.advisor` is reachable from the public `fdars` package without breaking network-free CI:

1. **`python/fdars/__init__.py`** — `from fdars import advisor` added after the existing pure-Python imports; `_sys.modules["fdars.advisor"] = advisor` registered so both `fdars.advisor.build_diagnostics` attribute access and `from fdars.advisor import build_diagnostics` import-form resolve; `"advisor"` added to `__all__`. The advisor module is kept out of `_submodule_names` (that tuple is for native Rust submodules only).

2. **`pyproject.toml`** — `advisor = ["anthropic>=0.72.0", "pydantic>=2.0"]` added to `[project.optional-dependencies]`. Floor matches `ADVISOR_ANTHROPIC_MIN_VERSION` in `advisor.py`. `pydantic>=2.0` included because `anthropic>=0.72.0` does not auto-install pydantic (Pitfall 4). Top-level `dependencies` list unchanged.

3. **`tests/test_basic.py`** + **`tests/test_advisor.py`** — `test_submodules` extended to import `advisor`; new `TestBuildDiagnosticsOffline::test_clustering_offline_with_synthetic` passes a synthetic `{"centers": ..., "cluster": ..., "k": 2}` dict to `build_diagnostics(method="clustering")` and asserts `method`, `k`, `cluster_sizes`. Runs with no `anthropic` installed and no network.

## Verification Evidence

All four plan-level verifications passed:

```
PASS: anthropic not in sys.modules  (after import fdars)
PASS: all symbols resolve  (build_diagnostics, advise, describe_cluster_differences, Advice, Recommendation)
PASS: advisor extra OK: ['anthropic>=0.72.0', 'pydantic>=2.0']  (pyproject.toml)
2 passed in 0.19s  (pytest test_submodules + test_clustering_offline_with_synthetic)
```

Full suite: **101 tests passed** (no regressions).

## Commits

| Task | Commit | Message |
|------|--------|---------|
| 1 (tracer) | 497b5a0 | feat(11-01): wire fdars.advisor into public package API |
| 2 | 06c2f2a | chore(11-01): add [advisor] optional-dependency extra to pyproject.toml |
| 3 | 29f2908 | test(11-01): extend test_submodules + create TestBuildDiagnosticsOffline |

## Deviations from Plan

None — plan executed exactly as written.

The `autonomous: true` frontmatter and fully-automated tracer `<verify>` (Python one-liner) meant the tracer feedback gate resolved without human input. All acceptance criteria were met on first attempt.

## Known Stubs

None. All three deliverables are fully wired:
- `fdars.advisor` module is reachable via both import forms
- `[advisor]` extra is declared with correct floors
- One offline `build_diagnostics` reachability test passes

## Threat Surface Scan

No new security-relevant surface introduced beyond what was already in the plan's threat model:
- T-11-01 (anthropic import at package-load): mitigated — verified `anthropic` not in `sys.modules` after `import fdars`
- T-11-02 (dependency floor tampering): mitigated — `anthropic>=0.72.0` and `pydantic>=2.0` declared
- T-11-03 (base install pulling heavy deps): mitigated — advisor deps kept out of top-level `dependencies`

## Self-Check

- [x] `python/fdars/__init__.py` modified with advisor import + sys.modules injection
- [x] `pyproject.toml` modified with advisor extra
- [x] `tests/test_basic.py` modified with advisor import in test_submodules
- [x] `tests/test_advisor.py` created with TestBuildDiagnosticsOffline
- [x] Commit 497b5a0 exists
- [x] Commit 06c2f2a exists
- [x] Commit 29f2908 exists

## Self-Check: PASSED
