---
phase: 72-advisor-extension
plan: 02
subsystem: advisor
tags: [python, advisor, frechet, diagnostics, grounding, json-serialization]

requires:
  - phase: 72-advisor-extension/72-01
    provides: frechet.py stub + guard-sync registrations (fts+frechet in all 4 guard-sync locations)

provides:
  - Real frechet builder branches: anova/global_reg/local_reg/frechet_mean array path
  - Per-aspect serialization + grounding + determinism tests for all four frechet result shapes
  - Stable dict shape (all keys always present, None fallbacks) for the frechet advisor aspect

affects: [advisor, mcp, frechet, test_advisor_frechet]

actuals:
  tokens: 8600
  tasks: 2
  commits: 2

tech-stack:
  added: []
  patterns:
    - "isinstance(raw, dict) guard FIRST before dict key lookups — mandatory for ndarray-returning functions (frechet_mean)"
    - "Discriminator hierarchy using CONFIRMED PyDict keys from frechet_mod.rs; no guessed key names"
    - "Stable dict shape: every key always present in every branch; None fallbacks on inactive branches"
    - "float()/int() cast on every numpy scalar (np.max/np.trace/np.unique return numpy scalars)"

key-files:
  created:
    - tests/test_advisor_frechet.py
  modified:
    - python/fdars/advisor/aspects/frechet.py

key-decisions:
  - "isinstance(raw, dict) first guard (not hasattr check): cleaner discriminator for the array vs dict split"
  - "n_groups derived from len(np.unique(group_labels)) rather than trusting a 'n_groups' key that does not exist in the 9-key frechet_anova dict"
  - "anova_p_value_permutation as the primary anova field name (not anova_p_value) to match the exact source key p_value_permutation"
  - "Stable None fallbacks for all keys across all branches: every branch sets all keys so json.dumps always succeeds regardless of result shape"

patterns-established:
  - "Array-return discriminator: check isinstance(raw, dict) first; if False, treat as numpy array (e.g. frechet_mean)"
  - "Confirmed-key discriminator: read frechet_mod.rs before writing has_* conditions; never guess key names"
  - "Shared fixture reuse: test_advisor_frechet.py reuses the exact fixture construction from test_frechet.py (same RNG seeds, shapes)"

requirements-completed: [ADV-01, ADV-02]

coverage:
  - id: D1
    description: "frechet_mean array path: has_frechet_mean True, ndim/dim/trace correct, no numpy scalars"
    requirement: ADV-01
    verification:
      - kind: unit
        ref: "tests/test_advisor_frechet.py::TestFrechetMeanAspect"
        status: pass

  - id: D2
    description: "frechet_anova dict path: has_anova True, anova_p_value_permutation in [0,1], n_groups==3"
    requirement: ADV-01
    verification:
      - kind: unit
        ref: "tests/test_advisor_frechet.py::TestFrechetAnovaAspect"
        status: pass

  - id: D3
    description: "frechet_global_reg dict path: has_global_reg True, has_local_reg False, bandwidth None"
    requirement: ADV-01
    verification:
      - kind: unit
        ref: "tests/test_advisor_frechet.py::TestFrechetGlobalRegAspect"
        status: pass

  - id: D4
    description: "frechet_local_reg dict path: has_local_reg True, bandwidth float, predicted_n_obs int"
    requirement: ADV-01
    verification:
      - kind: unit
        ref: "tests/test_advisor_frechet.py::TestFrechetLocalRegAspect"
        status: pass

  - id: D5
    description: "All four frechet shapes: json.dumps succeeds, check_no_numpy passes, deterministic"
    requirement: ADV-02
    verification:
      - kind: unit
        ref: "tests/test_advisor_frechet.py (json_serializable+no_numpy_scalars+deterministic tests)"
        status: pass

  - id: D6
    description: "Key-drift verify: p_value_permutation/group_labels/bandwidth/predicted/x_bar confirmed in frechet_mod.rs"
    requirement: ADV-01
    verification:
      - kind: automated_ui
        ref: "for k in p_value_permutation group_labels bandwidth predicted x_bar; do grep -q \"$k\" src/frechet_mod.rs || exit 1; done"
        status: pass

  - id: D7
    description: "frechet correctly absent from _RUNNABLE_METHODS in both server.py and _runner.py (SC3)"
    requirement: ADV-02
    verification:
      - kind: unit
        ref: "tests/test_guard_sync_version_independent.py"
        status: pass

status: complete
---

# Phase 72 Plan 02: Frechet Advisor Builder — Full Field Logic Summary

**One-liner:** Real frechet diagnostics builder with anova/global_reg/local_reg/frechet_mean branches using CONFIRMED PyDict keys from frechet_mod.rs; grounded native-Python scalars; JSON-serialisable; deterministic.

## Accomplishments

- Replaced the 72-01 stub body of `_build_frechet_diagnostics` with real grounded branches for all four frechet result shapes
- frechet_mean array path: `isinstance(raw, dict)` guard applied FIRST; `np.asarray(raw)` extracts ndim/dim/trace; has_frechet_mean True
- frechet_anova dict path: discriminated by `"p_value_permutation" in raw and "group_labels" in raw` (CONFIRMED keys from frechet_mod.rs:97,107); n_groups derived from `len(np.unique(group_labels))`
- frechet_global_reg path: `"predicted" in raw and "x_bar" in raw and not has_local_reg`; predicted_n_obs int; bandwidth None
- frechet_local_reg path: `"bandwidth" in raw`; bandwidth float; predicted_n_obs int
- Stable dict shape: every key always present in every branch regardless of result shape; None fallbacks on inactive branches
- Created `tests/test_advisor_frechet.py` (37 tests) covering json.dumps serialization, check_no_numpy, determinism, method-field, and branch-flag/range assertions for all four shapes
- frechet remains diagnostics-only (not in _RUNNABLE_METHODS) — SC3 constraint upheld

## Commits

- `de244c4` — test(72-02): add failing tests for frechet advisor aspect branches (RED)
- `a0473ef` — feat(72-02): implement frechet builder — anova/global_reg/local_reg/mean branches (GREEN)

## Verification

```
tests/test_advisor_frechet.py             37 passed
tests/test_guard_sync_version_independent.py  2 passed
tests/test_advisor_grounding.py           40 passed
Total: 79 passed
```

Key-drift verify: all 5 discriminator key literals (`p_value_permutation`, `group_labels`, `bandwidth`, `predicted`, `x_bar`) confirmed present in `src/frechet_mod.rs`.

Inline smoke: `build_diagnostics(frechet_mean(spd_objs), method='frechet')` returns `has_frechet_mean=True, frechet_mean_ndim=2`; `json.dumps` succeeds; `check_no_numpy` passes.

## Deviations from Plan

None — plan executed exactly as written.

The stub in 72-01 used `"anova_p_value"` as a placeholder key; the real implementation uses `"anova_p_value_permutation"` matching the confirmed source key. This is correct behavior (the stub was explicitly a placeholder for 72-02).

## Known Stubs

None.

## Threat Flags

None — no new security surface introduced. All file changes are pure Python in the advisor layer (no network endpoints, no auth paths, no schema changes).

## Self-Check: PASSED

- `python/fdars/advisor/aspects/frechet.py`: FOUND (modified)
- `tests/test_advisor_frechet.py`: FOUND (created)
- Commit `de244c4`: FOUND
- Commit `a0473ef`: FOUND
