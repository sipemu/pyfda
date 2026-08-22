---
phase: 37
slug: group-a-regression-bindings
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-08-20
---

# Phase 37 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (in `.venv`) |
| **Config file** | `pyproject.toml` / `conftest.py` |
| **Quick run command** | `.venv/bin/python -m pytest tests/test_regression.py -q` |
| **Full suite command** | `.venv/bin/python -m pytest tests/ -q` |
| **Estimated runtime** | quick ~15s; full ~120s |

---

## Sampling Rate

- **After every task commit:** `.venv/bin/python -m pytest tests/test_regression.py -q`
- **After every plan wave / before `/gsd-verify-work`:** `.venv/bin/python -m pytest tests/ -q` must be green (0 failed), plus `cargo fmt --check` + `cargo clippy -- -D warnings`.
- **Max feedback latency:** ~120s

---

## Per-Task Verification Map

| Req ID | Behavior | Test Type | Automated Command |
|--------|----------|-----------|-------------------|
| REGR-01 | `concurrent_regression` returns dict {beta_curve,intercept,fitted,residuals,argvals}; smoke | unit | `pytest tests/test_regression.py -k concurrent_smoke` |
| REGR-01 | `beta_curve.shape == (p, m)` for p=3 — transposition guard | unit | `pytest tests/test_regression.py -k beta_curve_shape_p3` |
| REGR-01 | determinism + `residuals == response - fitted` | unit | `pytest tests/test_regression.py -k "determinism or residuals_consistency"` |
| REGR-02 | `functional_glm` Gaussian/Binomial/Poisson/Gamma: dict keys + finite/link-appropriate fitted values; family string round-trips | unit | `pytest tests/test_regression.py -k functional_glm` |
| REGR-02 | invalid `family` → `ValueError` (GlmFamily wildcard arm) | unit | `pytest tests/test_regression.py -k glm_bad_family` |
| REGR-03 | registration + `to_pyresult` guards: degenerate inputs (mismatched grids, too few curves, invalid n_comp, ragged predictors) raise `ValueError` | unit | `pytest tests/test_regression.py -k "raises or valueerror"` |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_regression.py` — new test class(es) for `concurrent_regression` + `functional_glm` (may extend existing file if present)
- Existing `conftest.py` fixtures cover dataset loading.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| `Vec<PyReadonlyArray2>`/list-of-arrays binding compiles & extracts | REGR-01 | Rust/PyO3 compile-time + runtime smoke; verified by the transposition/smoke test passing | Build with `maturin develop`; if `FromPyObject` for the predictor list fails, fall back to `Bound<'py, PyList>` manual extraction |

*Otherwise: all phase behaviors have automated verification.*

---

## Validation Sign-Off

- [ ] All tasks have automated verify or Wave 0 dependencies
- [ ] No 3 consecutive tasks without automated verify
- [ ] Transposition guards present for `beta_curve (p,m)` at p≥2
- [ ] Feedback latency < 120s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
