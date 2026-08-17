---
phase: 34-advisor-extension
plan: "01"
subsystem: advisor
tags: [advisor, inference, diagnostics, guard-sync, adv-03]
status: complete

dependency_graph:
  requires:
    - 31-01  # fdars.inference bindings (TestResult/ToleranceBand shapes)
  provides:
    - build_diagnostics(method="inference") — grounded offline diagnostics builder
    - "_ASPECT_PRIMERS['inference']" — LLM prompt primer for inference aspect
  affects:
    - fdars.advisor (new dispatch branch + _supported expansion)
    - fdars.mcp.server (_DIAGNOSTICS_METHODS guard set)
    - tests/test_advisor_inference.py (new offline test suite)

tech_stack:
  added: []
  patterns:
    - diagnostics-only aspect (no _RUNNABLE_METHODS entry)
    - atomic guard-sync commit (advisor + MCP in one commit)
    - caller-supplied-dict grounding invariant

key_files:
  created:
    - python/fdars/advisor/aspects/inference.py
    - tests/test_advisor_inference.py
  modified:
    - python/fdars/advisor/aspects/__init__.py
    - python/fdars/advisor/__init__.py
    - python/fdars/advisor/_prompts.py
    - python/fdars/mcp/server.py

decisions:
  - "ToleranceBand / SCB detection: p_value absent AND half_width present — sets band_present=True, all significance fields None, echoes half_width as mean of sequence or scalar cast"
  - "half_width summary in ToleranceBand path: mean over the half_width array using plain-Python loop (no numpy dep in builder) to avoid scalar leakage"
  - "n_perm==0 contract: legitimate asymptotic-test value (Hotelling T²); is_permutation_test=False, NOT an error or None"
  - "_resolve_float helper: single-key lookup returning float or None, mirrors scoring._resolve_metric without dual key aliases"
  - "strongest_significance_level: native float 0.01/0.05/0.10 or None — stored as float(0.01) etc. to ensure json-serialisability"

metrics:
  duration: "~8 minutes"
  completed: "2026-08-17"
  tasks_completed: 2
  commits: 2
  files_created: 2
  files_modified: 4

actuals:
  tokens: 18000
  tasks: 2
  commits: 2
---

# Phase 34 Plan 01: Inference Diagnostics Aspect (ADV-03) Summary

Grounded offline `build_diagnostics(method="inference")` builder summarising fdars-computed `TestResult` dicts with significance flags at alpha 0.01/0.05/0.10 and asymptotic vs permutation discrimination; guard-sync atomic commit keeps drift-lock test green.

## What Was Built

### New: `python/fdars/advisor/aspects/inference.py`

The 14th advisor aspect (after 12 in v3.0 and `scoring` #13 in v4.0). Implements `_build_inference_diagnostics(raw, **kwargs)` — an offline, deterministic builder that:

- Accepts a TestResult-shaped dict `{statistic, p_value, n_perm}` or a ToleranceBand/SCB-shaped dict `{lower, upper, center, half_width}`
- Detects the ToleranceBand shape when `p_value` is absent and `half_width` is present; in that branch, echoes a `half_width` summary scalar and sets all significance fields to `None`
- For the TestResult path: echoes `statistic` (float), `p_value` (float), `n_perm` (int — 0 is legitimate for asymptotic tests)
- Derives three significance flags: `significant_at_0.01`, `significant_at_0.05`, `significant_at_0.10` (each `bool(p_value < alpha)`)
- Derives `strongest_significance_level`: smallest alpha at which significant, or `None`
- Derives `is_permutation_test`: `True` when `n_perm > 0`, `False` when `n_perm == 0` (asymptotic path), `None` when `n_perm` absent
- Raises `ValueError` naming expected keys when input is malformed
- All output values are native Python (no numpy scalars); `json.dumps(sort_keys=True)` is byte-identical across calls

**Grounding invariant intact:** the builder never imports `fdars.inference` and never recomputes any statistic — it only summarises and derives boolean flags from caller-supplied values.

### New: `tests/test_advisor_inference.py`

20 offline tests across 8 case groups mirroring `test_advisor_scoring.py` structure:

1. Basic correctness: method, types, json.dumps
2. Significance flags: correct boolean derivation at each alpha level
3. Asymptotic vs permutation: `n_perm == 0` is legitimate, `is_permutation_test is False`
4. ToleranceBand tolerance: SCB-shaped input returns `method="inference"`, all significance flags `None`, band_present=True
5. Determinism: byte-identical `json.dumps(sort_keys=True)` + `check_no_numpy` recursive walker
6. Grounding: `_extract_numbers` confirms each input value is present in serialised output
7. Offline: no `anthropic`/`openai` imported as side effect
8. Robustness: malformed input raises `ValueError`; non-dict input coerced

### Guard-Sync Edits (all five files in ONE atomic commit — T-34-03)

- `advisor/__init__.py`: `"inference"` added to `_supported` set + lazy dispatch branch after `scoring`
- `mcp/server.py`: `"inference"` added to `_DIAGNOSTICS_METHODS` only (NOT `_RUNNABLE_METHODS`)
- `_prompts.py`: `"inference"` entry added to `_ASPECT_PRIMERS` covering statistic/p_value semantics, asymptotic vs permutation distinction, significance flag derivation
- `aspects/__init__.py`: Submodules docstring updated with inference entry

## Verification

All three Task 1 verify checks passed before commit:
- `build_diagnostics({'statistic':2.5,'p_value':0.03,'n_perm':999}, method='inference')` returned correct dict; `json.dumps` succeeded
- `test_diagnostics_methods_match_advisor_supported` exited 0
- `"inference" in _DIAGNOSTICS_METHODS` and `"inference" not in _RUNNABLE_METHODS` confirmed

Full suite: **556 passed / 4 skipped** (zero regressions; 20 new inference tests; prior baseline was 536).

## Deviations from Plan

None — plan executed exactly as written.

The ToleranceBand `half_width` summary implementation detail (computing the mean of the array using a plain-Python loop) is a minor implementation choice within the plan's "Claude's discretion" latitude; it avoids any numpy dependency in the builder while still providing a meaningful scalar summary.

## Commits

| Task | Commit | Message |
|------|--------|---------|
| Task 1: aspect + all guard edits | `5699ccf` | feat(34-01): add inference diagnostics aspect (ADV-03) — atomic guard-sync |
| Task 2: offline test suite | `8699194` | test(34-01): offline test suite for inference diagnostics aspect (ADV-03) |

## Threat Mitigations Applied

| Threat | Status |
|--------|--------|
| T-34-01: Grounding invariant | Mitigated — no `fdars.inference` import; no recompute; grounding test (case 6) enforces it |
| T-34-02: Malformed raw input | Mitigated — `ValueError` raised with key names when neither TestResult nor ToleranceBand keys present (case 8) |
| T-34-03: Advisor/MCP guard drift | Mitigated — single atomic commit for all five files; `test_diagnostics_methods_match_advisor_supported` stays green |
| T-34-04: Numpy scalar / non-serialisable leak | Mitigated — all values cast to native Python; `check_no_numpy` walker test (case 5) |

## Self-Check: PASSED

- `/home/simonm/projects/rust/pyfda/python/fdars/advisor/aspects/inference.py` — FOUND
- `/home/simonm/projects/rust/pyfda/tests/test_advisor_inference.py` — FOUND
- Commit `5699ccf` — FOUND (`git log --oneline -3`)
- Commit `8699194` — FOUND
