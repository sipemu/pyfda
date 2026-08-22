---
phase: 40
slug: advisor-extension
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-08-21
---

# Phase 40 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (in `.venv`) — Python-only phase, NO maturin rebuild needed |
| **Config file** | `pyproject.toml` / `conftest.py` |
| **Quick run command** | `.venv/bin/python -m pytest tests/ -k advisor -q` |
| **Full suite command** | `.venv/bin/python -m pytest tests/ -q` |
| **Estimated runtime** | quick ~15s; full ~130s |

---

## Sampling Rate

- **After every task commit:** `.venv/bin/python -m pytest tests/ -k advisor -q`
- **Before `/gsd-verify-work`:** full suite green (0 failed). NO cargo build/fmt/clippy needed (no Rust change) — but if any `src/*.rs` is touched, run them.
- **Max feedback latency:** ~130s

---

## Per-Task Verification Map

| Req ID | Behavior | Automated Command |
|--------|----------|-------------------|
| ADV-04 | `outliers` build_diagnostics emits grounded scalars for tvdmss/muod/sequential_transform/depthgram (n_outliers, fraction, score ranges — all float/int); depthgram checked BEFORE outliergram (shared mbd/mei keys) | `pytest tests/ -k "advisor and outlier" -q` |
| ADV-05 | `regression` build_diagnostics emits grounded scalars for functional_glm (deviance/AIC/iterations; trigger `deviance`) + concurrent_regression (2-D residual RMS; trigger `beta_curve`) | `pytest tests/ -k "advisor and regression" -q` |
| ADV-05 | Group B: `classification` emits grounded scalar for elastic_multinomial (train_accuracy; trigger `train_accuracy`); `fpca` emits grounded scalars for pace_fpca (eigenvalues→variance-explained, sigma2, ncomp; trigger `eigenvalues`) | `pytest tests/ -k "advisor and (classification or fpca)" -q` |
| ADV-04/05 | grounding invariant: every emitted diagnostic is float/int (NO numpy scalar), byte-identical `json.dumps(sort_keys=True)` across two runs, `_check_grounding` passes; MCP guard-sync `test_diagnostics_methods_match_advisor_supported` stays green with NO edit (no new aspect key) | `pytest tests/ -k "grounding or diagnostics_methods_match or determinism" -q` |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] New/extended advisor offline tests (mirror `tests/test_advisor_inference.py` pattern): build_diagnostics on a REAL shipped v6.0 result → assert grounded scalars present + all float/int + deterministic + `_check_grounding` passes.
- Existing `test_diagnostics_methods_match_advisor_supported` must remain green unchanged.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| `_ASPECT_PRIMERS` primer wording (LLM-facing) | ADV-04/05 | Primer text affects LLM behavior, not offline determinism — no automated test covers content | Commit primer edits atomically with the builder change; review the diff for accuracy vs the emitted scalars |

*Otherwise: all phase behaviors have automated offline verification.*

---

## Validation Sign-Off

- [ ] Grounded scalars for all 6 new-capability result dicts (4 outliers + functional_glm + concurrent_regression + elastic_multinomial + pace_fpca)
- [ ] Every diagnostic float/int (no numpy), deterministic json.dumps, `_check_grounding` passes
- [ ] No new aspect key; `test_diagnostics_methods_match_advisor_supported` green with no guard edit
- [ ] Full suite 0 failed
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
