---
phase: 11
slug: python-api-surface
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-08-09
---

# Phase 11 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (9.x local; installed via `pip install pytest` in CI) |
| **Config file** | none — no `pytest.ini` / `setup.cfg` / `[tool.pytest]`; Wave 0 adds `tests/test_advisor.py` |
| **Quick run command** | `pytest tests/test_advisor.py -v` |
| **Full suite command** | `pytest tests/ -v` |
| **Estimated runtime** | ~30 seconds (offline; LLM integration test skips without `ANTHROPIC_API_KEY`) |

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/test_advisor.py -v`
- **After every plan wave:** Run `pytest tests/ -v`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** ~30 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 11-01-* | 01 | 1 | PYAPI-01 | — | `advisor` importable via public API, no key needed | smoke | `pytest tests/test_basic.py::test_submodules -x` (extended for advisor) | ❌ W0 | ⬜ pending |
| 11-02-* | 02 | 1 | PYAPI-01 | — | `anthropic` never imported at package import time | unit | `pytest tests/test_advisor.py::TestBuildDiagnosticsOffline -x` | ❌ W0 | ⬜ pending |
| 11-02-* | 02 | 1 | PYAPI-02 | T-10-01 | LLM test SKIPS (not fails) when key absent | integration | `pytest tests/test_advisor.py::TestAdvisorIntegration -v` | ❌ W0 | ⬜ pending |
| 11-03-* | 03 | 2 | PYAPI-03 | — | recipe runs offline through `build_diagnostics`; `advise` guarded | smoke | `python examples/advisor_recipe.py` (no key set) | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*
*Exact task IDs are assigned by the planner; rows map by requirement.*

---

## Wave 0 Requirements

- [ ] `tests/test_advisor.py` — offline `build_diagnostics` tests against `docs/data/` (PYAPI-01, PYAPI-02) + env-gated `advise` integration test that skips without `ANTHROPIC_API_KEY` (uses `pytest.importorskip("anthropic")` + `pytest.mark.skipif`)
- [ ] `examples/advisor_recipe.py` — end-to-end recipe covering PYAPI-03 (runs offline; `advise` step guarded so the script does not fail without a key)
- [ ] Extend `tests/test_basic.py::test_submodules` to assert `from fdars import advisor` resolves

*Framework already present (pytest); no install task needed beyond CI's existing `pip install pytest`.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| `advise()` returns coherent, diagnostics-grounded advice from a live model | PYAPI-02 | Requires a real `ANTHROPIC_API_KEY` and network; not run in CI | Set `ANTHROPIC_API_KEY`, run `python examples/advisor_recipe.py`, inspect that recommendations cite the numeric diagnostics |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references (`tests/test_advisor.py`, `examples/advisor_recipe.py`)
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
