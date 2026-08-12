---
phase: 21-per-aspect-advisor-coverage
plan: "05"
subsystem: advisor/aspects
tags: [spm, monitoring, phase-i, aspect-05, aspect-06, determinism, live-fdars-call]
requirements: [ASPECT-05, ASPECT-06]

dependency_graph:
  requires:
    - "21-03: _utils._eigenvalues_to_variance_cumulative (shared helper, used here)"
    - "21-01 through 21-04: all prior aspect builders and _supported set"
  provides:
    - "advisor/aspects/spm.py: _build_spm_diagnostics (ASPECT-05)"
    - "spm in _supported + dispatch branch (plan 21-05)"
    - "ASPECT-06 finalized: all 7 new aspect primers verified in _ASPECT_PRIMERS"
  affects:
    - "advisor/__init__.py: _supported set + dispatch"
    - "tests/test_advisor.py: +4 spm tests"

tech_stack:
  added: []
  patterns:
    - "Live fdars call guarded by try/except -> None fallback (graceful degradation)"
    - "RESEARCH correction #8: excess_kurtosis renamed to spe_kurtosis_excess in output"
    - "pytest.importorskip('fdars.spm') guards determinism test against missing compiled ext"
    - "Shared _eigenvalues_to_variance_cumulative from _utils.py (no sv^2/(n-1) step for SPM)"

key_files:
  created:
    - python/fdars/advisor/aspects/spm.py
  modified:
    - python/fdars/advisor/__init__.py
    - tests/test_advisor.py

decisions:
  - "spe_kurtosis_excess = float(mmd['excess_kurtosis']): rename per RESEARCH correction #8 for LLM clarity"
  - "arl0_t2 excluded: stochastic (Monte Carlo seed-dependent), breaks offline determinism guarantee (FUT-02)"
  - "spm_phase1 returns eigenvalues directly -> no sv^2/(n-1) step before _eigenvalues_to_variance_cumulative"
  - "Task 2 (spm primer in _prompts.py) was already present from prior wave: only verification needed, no code change"
  - "TDD: RED tests added first (spm not in _supported -> ValueError); GREEN after builder + dispatcher wired"

metrics:
  duration_minutes: 3
  completed: "2026-08-12T08:57:22Z"
  tasks_completed: 3
  tasks_total: 3
  commits: 1

status: complete

actuals:
  tokens: 3500
  tasks: 3
  commits: 1
---

# Phase 21 Plan 05: SPM Aspect Builder Summary

SPM Phase I monitoring diagnostics (ASPECT-05) added as the final HIGH-complexity aspect, making exactly one live deterministic fdars call (`spe_moment_match_diagnostic`), reusing the shared eigenvalue helper, and completing ASPECT-06 primer coverage for all seven new aspects.

## What Was Built

### `python/fdars/advisor/aspects/spm.py` (NEW)

`_build_spm_diagnostics(raw, **kwargs)` computes Phase I SPM diagnostics:

- `n_obs`, `ncomp`: observation count and component count from `t2`/`eigenvalues` arrays
- `t2_limit`, `spe_limit`: direct scalar floats from `spm_phase1` result (NOT dicts)
- `t2_max`, `t2_mean`, `t2_exceedance_rate`: T2 summary stats; exceedance rate = fraction of observations exceeding the control limit
- `spe_max`, `spe_mean`, `spe_exceedance_rate`: SPE analogues
- `eigenvalues`: plain list of floats from `raw["eigenvalues"]`
- `variance_explained_cumulative`: delegated to `_eigenvalues_to_variance_cumulative` from `_utils.py` (no `sv^2/(n-1)` step — SPM returns eigenvalues directly)
- `spe_kurtosis_excess`: float from `mmd["excess_kurtosis"]` (RESEARCH correction #8 rename); `None` on ImportError/any exception
- `spe_moment_match_adequate`: bool from `mmd["is_adequate"]`; `None` on failure

Security mitigations T-21-07 and T-21-08: all key accesses guarded, live call wrapped in bare `except Exception`.

### `python/fdars/advisor/__init__.py` (MODIFIED)

- `"spm"` added to `_supported` set (comment: `# ASPECT-05 (plan 21-05)`)
- Lazy dispatch branch: `if method_lc == "spm": from fdars.advisor.aspects.spm import ...`
- Docstring updated to include `"spm"` in the method union type

### `tests/test_advisor.py` (MODIFIED)

Added `TestSpm` class with 4 tests:

| Test | What It Checks |
|------|----------------|
| `test_spm_basic` | Field presence, exceedance rates, cumulative variance, JSON-serialisability (no fdars required) |
| `test_spm_deterministic` | `pytest.importorskip("fdars.spm")` + two calls byte-identical, no numpy scalars, `spe_kurtosis_excess` is native float |
| `test_spm_prompt_clause` | `t2_exceedance_rate` in `_system_prompt('interpretation', 'spm')`, absent from base |
| `test_all_seven_aspect_primers_present` | ASPECT-06 Nyquist gate: all 7 new aspects in `_ASPECT_PRIMERS` |

## ASPECT-06 Finalization

All seven new aspect primers were already present in `_prompts.py` from prior waves. This plan verified and gated coverage:

| Aspect | Primer Token | Status |
|--------|-------------|--------|
| depth | `depth_q10` | Present (plan 21-01) |
| outliers | `outlier_fraction` | Present (plan 21-02) |
| classification | `error_rate` | Present (plan 21-02) |
| represent | `is_uniform_grid` | Present (plan 21-03) |
| regression | `r_squared` | Present (plan 21-04) |
| regression_cv | `optimal_k` | Present (plan 21-04) |
| spm | `t2_exceedance_rate` | Present (prior wave) |

## Verification

### Plan verify command
```
OK
```
- `d['n_obs']==10`, `d['ncomp']==3`, `t2_exceedance_rate==0.1`, `spe_exceedance_rate==0.1`, `variance_explained_cumulative[-1]≈1.0`, `spe_kurtosis_excess is not None`

### Live call confirmed
`spe_moment_match_diagnostic([...])` returns `{'excess_kurtosis': -0.577..., 'theoretical_kurtosis': 3.345..., 'is_adequate': False}` — all native Python types, deterministic pure moment computation.

### Full test suite result
```
225 passed, 4 skipped in 27.19s
```
Baseline was 221 passed, 4 skipped. The +4 tests are the new SPM tests; all prior tests remain green.

## Deviations from Plan

None — plan executed exactly as written, except:

**[Note] Task 2 spm primer already present:** The `_prompts.py` `_ASPECT_PRIMERS["spm"]` entry was landed in a prior wave (not plan 21-05). Task 2 was verification-only with no code change required. The ASPECT-06 finalization gate is enforced by `test_all_seven_aspect_primers_present` in the commit.

## Known Stubs

None — all diagnostic fields are fully computed from the fixture; no placeholder values.

## Threat Surface Scan

No new network endpoints, auth paths, file access patterns, or schema changes. The one trust boundary crossing (builder -> `fdars.spm` native call) is mitigated by the `try/except` guard (T-21-08).

## Self-Check: PASSED

| Check | Result |
|-------|--------|
| `python/fdars/advisor/aspects/spm.py` exists | FOUND |
| `.planning/phases/21-per-aspect-advisor-coverage/21-05-SUMMARY.md` exists | FOUND |
| Commit `4b41cb7` in git log | FOUND |
| `225 passed, 4 skipped` full suite | PASSED |
