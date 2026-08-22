---
phase: 38
slug: group-b-fpca-classification-bindings
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-08-20
---

# Phase 38 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (in `.venv`) |
| **Config file** | `conftest.py` / `pyproject.toml` |
| **Quick run command** | `.venv/bin/python -m pytest tests/test_pace_fpca.py tests/test_classification.py -q` |
| **Full suite command** | `.venv/bin/python -m pytest tests/ -q` |
| **Build command** | `.venv/bin/python -m maturin develop` |
| **Estimated runtime** | quick ~20s; full ~130s |

---

## Sampling Rate

- **After every task commit:** quick command above.
- **Before `/gsd-verify-work`:** full suite green (0 failed) + `cargo fmt --check` + `cargo clippy -- -D warnings`.
- **Max feedback latency:** ~130s

---

## Per-Task Verification Map

| Req ID | Behavior | Automated Command |
|--------|----------|-------------------|
| PACE-01 | `fdars.irreg_fdata_from_lists` builds an IrregFdata handle from two ragged lists; round-trips through pace_fpca | `pytest tests/test_pace_fpca.py -k irreg_round_trip` |
| PACE-01 | dense 2-D numpy array → `ValueError` (not silently accepted) | `pytest tests/test_pace_fpca.py -k dense_array_rejection` |
| PACE-01 | ragged length mismatch (len(argvals[i]) ≠ len(values[i])) → `ValueError` (guard BEFORE from_lists panic) | `pytest tests/test_pace_fpca.py -k ragged_mismatch` |
| PACE-02 | `fdars.pace_fpca(data, ncomp,...)` → 10-key dict; `eigenfunctions (m,ncomp)` + `scores (n,ncomp)` transposition-guarded at n≠m≠ncomp | `pytest tests/test_pace_fpca.py -k "pace_smoke or pace_shapes"` |
| PACE-02 | pace_fpca determinism + result.ncomp ≤ config.ncomp handled | `pytest tests/test_pace_fpca.py -k "pace_determinism or pace_ncomp"` |
| CLASS-01 | `fdars.classification.elastic_multinomial(data, labels, argvals,...)` → dict; `train_probabilities (n,K)` guarded at K=3 (K≠n); `class_models` NOT exposed | `pytest tests/test_classification.py -k "multinomial_smoke or multinomial_proba_shape"` |
| CLASS-01 | negative / non-contiguous labels → `ValueError` (CR-01 guard, no usize::MAX wrap) | `pytest tests/test_classification.py -k multinomial_bad_labels` |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_pace_fpca.py` — new (IrregFdata + pace_fpca)
- [ ] `tests/test_classification.py` — new or extended (elastic_multinomial)
- Small inline synthetic sparse data (no existing irregular dataset); multi-class from synthetic or subsampled phoneme.csv.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| `#[pyclass] PyIrregFdata` compiles & passes by-ref into `pace_fpca` | PACE-01/02 | PyO3 0.28 `#[pyclass]` + `&PyIrregFdata`/`PyRef` param form is compile-time; 3 idioms flagged ASSUMED in research | `maturin develop` must build; the round-trip test passing proves the handle path. Fallback: `pace_fpca` accepts the two lists directly. |

*Otherwise: all phase behaviors have automated verification.*

---

## Validation Sign-Off

- [ ] All tasks have automated verify or Wave 0 deps
- [ ] Transposition guards present (eigenfunctions/scores at n≠m≠ncomp; train_probabilities at K≥3,K≠n)
- [ ] Dense-array + ragged-mismatch + negative-label ValueError guards present
- [ ] Feedback latency < 130s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
