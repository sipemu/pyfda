---
phase: 39
slug: group-c-depth-outliers-interval-inference-bindings
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-08-21
---

# Phase 39 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (in `.venv`) |
| **Config file** | `pyproject.toml` / `conftest.py` |
| **Quick run command** | `.venv/bin/python -m pytest tests/test_depth.py tests/test_outliers.py tests/test_inference.py -q` |
| **Full suite command** | `.venv/bin/python -m pytest tests/ -q` |
| **Build command** | `.venv/bin/python -m maturin develop` |
| **Estimated runtime** | quick ~25s; full ~135s |

---

## Sampling Rate

- **After every task commit:** quick command above (per-area subset).
- **Before `/gsd-verify-work`:** full suite green (0 failed) + `cargo fmt --check` + `cargo clippy -- -D warnings`.
- **Max feedback latency:** ~135s

---

## Per-Task Verification Map

| Req ID | Behavior | Automated Command |
|--------|----------|-------------------|
| DEPTH-03 | 9 new `functional_depth` methods return finite `(n,)` arrays; `functional_boxplot(method=...)` accepts them; invalid method → `ValueError` listing all 13 | `pytest tests/test_depth.py -k "new_variant or bad_method"` |
| OUTL-01 | `fdars.outliers.tvdmss(data, ...)` → dict; outlier indices `list[int]`; deterministic | `pytest tests/test_outliers.py -k tvdmss` |
| OUTL-02 | `fdars.outliers.muod(data, ...)` → dict (amplitude/magnitude/shape index sets + scores) | `pytest tests/test_outliers.py -k muod` |
| OUTL-03 | `fdars.outliers.sequential_transform_outliers(data, transforms=[...])` → dict incl. `per_transform` list[dict]; SeqTransform string dispatch + invalid transform → `ValueError` | `pytest tests/test_outliers.py -k "seqtransform or bad_transform"` |
| OUTL-04 | `fdars.outliers.depthgram(data, ...)` → dict (two depth indices + flagged outliers) | `pytest tests/test_outliers.py -k depthgram` |
| ITP-01 | `itp_one_pop(data, argvals, mu0,...)` → dict with `adjusted_pvalues`/`raw_pvalues` 1-D arrays, `basis_type`, `n_basis`, `n_perm`; `len(adjusted_pvalues)==n_basis` | `pytest tests/test_inference.py -k itp_one_pop` |
| ITP-02 | `itp_two_pop(a, b, argvals, ..., seed=None)` → dict; seeded determinism | `pytest tests/test_inference.py -k itp_two_pop` |
| ITP-03 | `itp_flm(data, response, argvals, basis_type=...)` → dict; `ProjectionBasisType` bspline/fourier dispatch + invalid basis → `ValueError`; re-fits internally | `pytest tests/test_inference.py -k itp_flm` |
| ITP-04 | 3 ITP fns registered via new `itp_result_to_pydict`; vectors as 1-D arrays; degenerate inputs → `ValueError` (to_pyresult, no .unwrap) | `pytest tests/test_inference.py -k itp` |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_depth.py` — extend (9 new methods)
- [ ] `tests/test_outliers.py` — extend/new (4 detectors)
- [ ] `tests/test_inference.py` — extend (3 ITP fns)
- Small synthetic / existing small datasets; no new dataset files.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| itp module path (`inference::itp::` vs `inference::`) | ITP-01..04 | compile-time; A1 in research | `maturin develop` resolves the correct re-export; build failure points to the path |

*Otherwise: all phase behaviors have automated verification. NB: the 4 outlier detectors are deterministic (no seed field in any config) — no seed-determinism test needed for them; only ITP permutation determinism.*

---

## Validation Sign-Off

- [ ] All tasks have automated verify or Wave 0 deps
- [ ] Depth: all 9 new tokens dispatch + invalid-method ValueError
- [ ] Outliers: index sets as list[int]; SeqTransform per-transform list[dict]; invalid transform ValueError
- [ ] ITP: vector p-values as 1-D arrays; basis dispatch + invalid-basis ValueError; seed determinism
- [ ] Feedback latency < 135s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
