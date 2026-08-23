---
phase: 50-deferred-advisor-aspects-compat-pre-flight
plan: "02"
subsystem: advisor
tags: [advisor, grounding, itp, pace-fpca, elastic-multinomial, aspect, primer]

# Dependency graph
requires:
  - "50-01 (compat pre-flight — stable advisor/MCP surface)"
provides:
  - "ITP branch in inference.py: detection+localisation scalars end-to-end through _check_grounding (ASPECT-03)"
  - "PACE-FPCA extra scalars: noise/signal ratio, truncated-rank flag, mean band width (ASPECT-01)"
  - "elastic-multinomial scalars: overfitting gap + class-count flag, holdout_accuracy kwarg (ASPECT-02)"
  - "Extended _ASPECT_PRIMERS for fpca/classification/inference (ASPECT-04)"
affects:
  - "50-03 (grounding matrix — new scalars to verify)"
  - "Phase 51+ (comparative method-selection, pipeline report — feed on accurate diagnostics)"

actuals:
  tokens: 42000
  tasks: 4
  commits: 4

tech-stack:
  added: []
  patterns:
    - "ITP vector-to-scalar reduction: detect shape by 'adjusted_pvalues' key; cast array elements via float() loop; emit detection+localisation scalars; never store the raw array"
    - "Stable-key-set pattern: add itp_*/pace_*/overfitting_* fields set to None in all other paths so the key set is identical across result shapes"
    - "PACE band-width scalar: (fitted_upper - fitted_lower).mean() via numpy, cast to native float"
    - "holdout_accuracy caller-supplied kwarg threaded from build_diagnostics into _build_classification_diagnostics (mirrors n_classes pattern)"
    - "Primer extension pattern: append clause to existing entry string; end clause with 'only cite values present' prohibition (PITFALLS #11)"

key-files:
  created:
    - "tests/test_advisor_itp.py (29 tests: detection, localisation, grounding, _check_grounding end-to-end, primer whether-vs-where)"
  modified:
    - "python/fdars/advisor/aspects/inference.py (ITP branch in _build_inference_diagnostics)"
    - "python/fdars/advisor/aspects/fpca.py (PACE extra scalars in has_pace_fpca branch)"
    - "python/fdars/advisor/aspects/classification.py (overfitting_gap + n_classes_flagged; holdout_accuracy kwarg)"
    - "python/fdars/advisor/__init__.py (holdout_accuracy kwarg in build_diagnostics signature)"
    - "python/fdars/advisor/_prompts.py (new 'fpca' primer entry; extended 'classification' and 'inference' entries)"
    - "tests/test_advisor_group_b.py (10 new PACE tests + 13 new elastic tests)"

key-decisions:
  - "ASPECT-03: ITP detection AND localisation emitted together — lone itp_min_adjusted_pvalue would mislead LLM into treating local significance as global (PITFALLS #8)"
  - "ASPECT-02: overfitting_gap is None (not fabricated) when holdout_accuracy not supplied — the elastic_multinomial result has no holdout accuracy of its own (grounding invariant, T-50B-03)"
  - "ASPECT-01: pace_noise_signal_ratio emits None (not 0.0) when total signal variance is zero — preserves sentinel-value distinction from a low-but-real ratio"
  - "ASPECT-04: 'fpca' added as new _ASPECT_PRIMERS key (was absent, count 10 -> 11, well within len <= 14 gate); no new _DIAGNOSTICS_METHODS or _supported key — guard-sync no-op"
  - "ITP primer contains 'localis' as verifiable whether-vs-where teaching signal; both test_primer_contains_localisation and test_primer_names_n_significant pass"

requirements-completed: [ASPECT-01, ASPECT-02, ASPECT-03, ASPECT-04]

coverage:
  - id: D1
    description: "ITP vector-to-scalar reduction with detection+localisation scalars"
    requirement: ASPECT-03
    verification:
      - kind: unit
        ref: "tests/test_advisor_itp.py (29 tests)"
        status: pass
    human_judgment: false
  - id: D2
    description: "PACE-FPCA noise/signal ratio, truncated-rank flag, mean band width"
    requirement: ASPECT-01
    verification:
      - kind: unit
        ref: "tests/test_advisor_group_b.py::TestPaceFpca (new 10 tests)"
        status: pass
    human_judgment: false
  - id: D3
    description: "elastic-multinomial overfitting gap + class-count flag"
    requirement: ASPECT-02
    verification:
      - kind: unit
        ref: "tests/test_advisor_group_b.py::TestElasticMultinomial (new 13 tests)"
        status: pass
    human_judgment: false
  - id: D4
    description: "Extended _ASPECT_PRIMERS for fpca/classification/inference; ITP whether-vs-where teaching"
    requirement: ASPECT-04
    verification:
      - kind: unit
        ref: "tests/test_advisor_itp.py::TestItpPrimer (2 tests)"
        status: pass
    human_judgment: false
  - id: D5
    description: "Guard-sync no-op: _supported and _DIAGNOSTICS_METHODS unchanged"
    requirement: ASPECT-04
    verification:
      - kind: other
        ref: "git diff HEAD python/fdars/advisor/__init__.py python/fdars/mcp/server.py (empty)"
        status: pass
    human_judgment: false

duration: 10min
completed: 2026-08-23
status: complete
---

# Phase 50 Plan 02: Deferred Advisor Aspects Summary

**ITP vector-to-scalar reduction (detection+localisation), PACE-FPCA noise/signal and band-width scalars, elastic-multinomial overfitting gap, and extended primers for all three — all grounded native float/int, json.dumps clean, guard-sync unchanged.**

## Performance

- **Duration:** 10 min
- **Started:** 2026-08-23T21:12:18Z
- **Completed:** 2026-08-23T21:22:00Z
- **Tasks:** 4
- **Files modified:** 6

## Accomplishments

- **Task 1 (TRACER — ITP):** Added an ITP branch to `_build_inference_diagnostics` in `inference.py`. Detected by the unique `adjusted_pvalues` key. Reduces the numpy p-value array to DETECTION scalars (`itp_min_adjusted_pvalue`, `itp_detected_at_0.05`) and LOCALISATION scalars (`itp_n_significant_0.05`, `itp_fraction_significant_0.05`, `itp_first_significant_basis`) at fixed alpha=0.05. Raw array never stored (grounding + JSON invariant). Stable `itp_*` None fields added to TestResult and ToleranceBand paths. 27 tests (all but 2 primer tests) pass before Task 4; all 29 pass after.

- **Task 2 (PACE-FPCA):** Extended the existing `has_pace_fpca` branch in `fpca.py` with three new ASPECT-01 scalars: `pace_noise_signal_ratio` (sigma2 / sum(eigenvalues), None when total variance is zero), `pace_truncated_rank_flagged` (bool, True when ncomp < len(eigenvalues)), and `pace_mean_prediction_band_width` (mean of `fitted_upper - fitted_lower` over the full (n, m) grid). Stable None fields in the else branch. 10 new tests added to `TestPaceFpca`.

- **Task 3 (elastic-multinomial):** Extended the `has_elastic_multinomial` branch in `classification.py` with `overfitting_gap` (train_accuracy minus caller-supplied holdout_accuracy, or None when absent — grounding invariant: gap not fabricated) and `n_classes_flagged` (bool, True when n_classes > 2). Added `holdout_accuracy: float | None = None` kwarg threaded from `build_diagnostics` through `_build_classification_diagnostics`. Stable None fields in non-elastic paths. 13 new tests added to `TestElasticMultinomial`.

- **Task 4 (primers + guard-sync gate):** Extended three `_ASPECT_PRIMERS` entries: added a new `"fpca"` entry (the key was absent; len 10 -> 11, within the len <= 14 gate); extended `"classification"` with `overfitting_gap` and `n_classes_flagged` language; extended `"inference"` with an ITP whether-vs-where clause explicitly teaching that detection (itp_min_adjusted_pvalue + itp_detected_at_0.05) and localisation (itp_n_significant_0.05, itp_fraction_significant_0.05, itp_first_significant_basis) answer different questions and must be cited together. Each new clause ends with the "only cite values present" prohibition. Contains "localis" as verifiable whether-vs-where signal. Guard-sync no-op confirmed: `git diff HEAD python/fdars/advisor/__init__.py python/fdars/mcp/server.py` is empty.

## Task Commits

1. **Task 1: ITP tracer** - `b64caea` (feat)
2. **Task 2: PACE-FPCA scalars** - `ab26ed5` (feat)
3. **Task 3: elastic-multinomial scalars** - `6b54967` (feat)
4. **Task 4: primer extensions** - `8a0166f` (feat)

## Files Created/Modified

- `tests/test_advisor_itp.py` (created) — 29 tests: ITP detection+localisation scalar tests, _check_grounding end-to-end survival, primer whether-vs-where assertions
- `python/fdars/advisor/aspects/inference.py` (modified) — ITP branch added to `_build_inference_diagnostics`; stable itp_* None fields in TestResult and ToleranceBand paths
- `python/fdars/advisor/aspects/fpca.py` (modified) — 3 new PACE scalars in has_pace_fpca branch; None fields in else branch
- `python/fdars/advisor/aspects/classification.py` (modified) — holdout_accuracy kwarg; overfitting_gap + n_classes_flagged in elastic branch; None fields in non-elastic path
- `python/fdars/advisor/__init__.py` (modified) — holdout_accuracy kwarg threaded into build_diagnostics
- `python/fdars/advisor/_prompts.py` (modified) — new fpca primer; extended classification and inference entries
- `tests/test_advisor_group_b.py` (modified) — 10 new PACE tests + 13 new elastic tests

## New Scalar Keys Emitted

**ITP (inference aspect):**
- `itp_result_present` (bool)
- `itp_min_adjusted_pvalue` (float) — DETECTION
- `itp_detected_at_0.05` (bool) — DETECTION
- `itp_n_significant_0.05` (int) — LOCALISATION
- `itp_fraction_significant_0.05` (float) — LOCALISATION
- `itp_first_significant_basis` (int or None) — LOCALISATION
- `itp_n_basis` (int)
- `itp_n_perm` (int)

**PACE-FPCA (fpca aspect):**
- `pace_noise_signal_ratio` (float or None)
- `pace_truncated_rank_flagged` (bool or None)
- `pace_mean_prediction_band_width` (float or None)

**elastic-multinomial (classification aspect):**
- `overfitting_gap` (float or None)
- `overfitting_gap_holdout_source` (str "holdout_accuracy" or None)
- `n_classes_flagged` (bool or None)

## Decisions Made

- ITP: detection AND localisation emitted together (PITFALLS #8) — lone min_p misleads LLM
- overfitting_gap is None (not fabricated) when holdout_accuracy not supplied (T-50B-03)
- pace_noise_signal_ratio is None when total signal variance is 0 (degenerate case guard)
- n_classes_flagged uses the binary/multiclass structural split (n_classes > 2) — no invented threshold
- "fpca" added as new _ASPECT_PRIMERS key (was absent in 10-key dict; 11 <= 14 gate passes)
- Guard-sync: no new _DIAGNOSTICS_METHODS or _supported key — confirmed by empty git diff

## Deviations from Plan

**1. [Rule 1 - Investigation] _ASPECT_PRIMERS had no "fpca" key**
- **Found during:** Task 4
- **Issue:** Plan stated "fpca/classification/inference already exist" in _ASPECT_PRIMERS, but the actual dict had 10 keys with no "fpca" entry
- **Fix:** Added "fpca" as a new _ASPECT_PRIMERS key (len 10 -> 11). The plan's len <= 14 acceptance criterion still passes. This adds only a primer entry — it is NOT a new _DIAGNOSTICS_METHODS or _supported key (those are the guard-sync constraints). No behavioral change to build_diagnostics.
- **Commit:** 8a0166f

## Issues Encountered

None beyond the "fpca" key absence (handled as Rule 1 — plan's own acceptance criteria accommodate len <= 14).

## Known Stubs

None.

## Threat Flags

None — no new network endpoints, auth paths, file access patterns, or schema changes. The `holdout_accuracy` kwarg is a caller-supplied native float, not a trust boundary crossing.

## Self-Check: PASSED

- `python/fdars/advisor/aspects/inference.py` exists: FOUND
- `python/fdars/advisor/aspects/fpca.py` exists: FOUND
- `python/fdars/advisor/aspects/classification.py` exists: FOUND
- `python/fdars/advisor/_prompts.py` exists: FOUND
- `tests/test_advisor_itp.py` exists: FOUND
- `tests/test_advisor_group_b.py` exists: FOUND
- Commits b64caea, ab26ed5, 6b54967, 8a0166f exist in git log: FOUND
- `pytest tests/test_advisor_itp.py tests/test_advisor_group_b.py -q`: 74 passed
- `json.dumps(build_diagnostics(itp_result, "inference"))`: succeeds
- `json.dumps(build_diagnostics(pace_result, "fpca"))`: succeeds
- ITP diag carries both detection and localisation scalars: VERIFIED
- `git diff HEAD python/fdars/advisor/__init__.py python/fdars/mcp/server.py`: empty (guard-sync no-op)
- `_ASPECT_PRIMERS` contains "localis" in "inference" entry and "itp_n_significant_0.05": VERIFIED
- `len(_ASPECT_PRIMERS) <= 14`: 11 <= 14 PASSED

---
*Phase: 50-deferred-advisor-aspects-compat-pre-flight*
*Completed: 2026-08-23*
