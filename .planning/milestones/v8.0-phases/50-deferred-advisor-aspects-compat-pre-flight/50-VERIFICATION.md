---
phase: 50-deferred-advisor-aspects-compat-pre-flight
verified: 2026-08-23T21:37:47Z
status: passed
score: 10/10 must-haves verified
behavior_unverified: 0
overrides_applied: 0
---

# Phase 50: Deferred Advisor Aspects (+ Compat Pre-flight) Verification Report

**Phase Goal:** The three deferred advisor aspects (PACE-FPCA, elastic-multinomial, ITP interval-inference) emit grounded, fdars-computed scalars with extended primers; blocking compat fixes (anthropic<1.0 pin, mcp v2 import verify, version-independent guard-sync test) land first as an isolated pre-flight.
**Verified:** 2026-08-23T21:37:47Z
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | The advisor extra pins anthropic below 1.0 so the advisor imports on Python 3.9 (COMPAT-01) | ✓ VERIFIED | `pyproject.toml:42` — `advisor = ["anthropic>=0.72.0,<1.0", "pydantic>=2.0"]`; grep count returns 1 |
| 2 | The MCP server and its 3 existing tools import and load over stdio via the mcp v2 MCPServer path (COMPAT-02) | ✓ VERIFIED | `tests/test_mcp_import_smoke.py` exists, module-level skip on <3.10, 3 passed; `MCPServer` from `mcp.server` asserted; all 3 tool handlers (`fdars_build_diagnostics`, `fdars_run_method`, `fdars_compare_run`) asserted callable |
| 3 | The guard-sync assertion (_DIAGNOSTICS_METHODS mirrors build_diagnostics._supported) runs on Python 3.9 — a pure dict-key comparison that does NOT import mcp (COMPAT-03) | ✓ VERIFIED | `tests/test_guard_sync_version_independent.py` — no `pytestmark`, no top-level `import mcp`; primary test recovers `_supported` by parsing ValueError via `ast.literal_eval`; companion test internally guarded to 3.10+; 3 passed |
| 4 | The ITP aspect reduces the vector-valued adjusted-p-curve to grounded DETECTION scalars (min adjusted p-value; detected-at-0.05) AND LOCALISATION scalars (count + proportion of significant intervals; first significant basis) together — never a lone global scalar (ASPECT-03) | ✓ VERIFIED | `python/fdars/advisor/aspects/inference.py` ITP branch confirmed; `adjusted_pvalues` key read and reduced — never stored; detection scalars `itp_min_adjusted_pvalue=0.02`, `itp_detected_at_0.05=True`; localisation scalars `itp_n_significant_0.05=1`, `itp_fraction_significant_0.05=0.2`, `itp_first_significant_basis=0` confirmed in live Python run; 29 tests pass |
| 5 | The PACE-FPCA aspect emits grounded sigma2 noise/signal scalar, a truncated-rank flag, and a mean prediction-band width, all native float/int (ASPECT-01) | ✓ VERIFIED | `python/fdars/advisor/aspects/fpca.py` has_pace_fpca branch extended; `pace_noise_signal_ratio=0.01` (float), `pace_truncated_rank_flagged=True` (bool), `pace_mean_prediction_band_width=0.5` (float) confirmed; native types confirmed via `type().__name__` checks; 45 PACE/FPCA tests pass |
| 6 | The elastic-multinomial aspect emits a grounded overfitting gap (train minus caller-supplied holdout/CV accuracy) and a class-count flag, native float/int (ASPECT-02) | ✓ VERIFIED | `python/fdars/advisor/aspects/classification.py` has_elastic_multinomial branch extended; `overfitting_gap=0.23` (float, train 0.95 - holdout 0.72) confirmed; `overfitting_gap=None` when no holdout supplied confirmed; `n_classes_flagged=True` (bool) for n_classes=3 confirmed |
| 7 | Every emitted scalar is a native Python float/int (no numpy scalars) and the diagnostics dict is json.dumps-serialisable | ✓ VERIFIED | Live Python: `type(itp_min_adjusted_pvalue)=float`, `type(itp_n_significant_0.05)=int`, `type(itp_fraction_significant_0.05)=float`; `type(pace_noise_signal_ratio)=float`, `type(pace_truncated_rank_flagged)=bool`, `type(pace_mean_prediction_band_width)=float`; `type(overfitting_gap)=float`, `type(n_classes_flagged)=bool`; `json.dumps()` succeeds on all three; `_check_grounding` exercised in test_advisor_itp.py::TestItpGrounding::test_check_grounding_survives (29 tests pass) |
| 8 | `_ASPECT_PRIMERS` is EXTENDED (not replaced) for fpca/classification/inference; the ITP primer explicitly teaches the whether-vs-where (detection vs localisation) distinction (ASPECT-04) | ✓ VERIFIED | `_ASPECT_PRIMERS` has 11 keys (was 10 — new `fpca` key added, note: PLAN stated fpca already existed but it did not; SUMMARY documents this Rule 1 deviation; `len <= 14` gate passes); `'localis' in p['inference']` True; `'itp_n_significant_0.05' in p['inference']` True; `'overfitting_gap' in p['classification']` True; `'pace_noise_signal_ratio' in p['fpca']` True |
| 9 | No new `_DIAGNOSTICS_METHODS` key and no new `build_diagnostics._supported` key are added — guard-sync stays a no-op (ASPECT-04) | ✓ VERIFIED | Pre-phase git state: 14-element `_supported` set; post-phase: identical 14-element set (confirmed via git show + live parse); `_supported == _DIAGNOSTICS_METHODS` True; `git diff 913007f~1 -- python/fdars/mcp/server.py` empty for that set; `holdout_accuracy` kwarg addition to `build_diagnostics` signature is the only change to `__init__.py` |
| 10 | `advise()` returns grounded interpretation for each new aspect (PACE-FPCA, elastic-multinomial, ITP), verified offline across the native and fallback provider machinery via the aspect x provider grounding matrix (ASPECT-05) | ✓ VERIFIED | `tests/test_aspect_provider_matrix.py -k "pace or elastic or itp"` — 6 passed (3 aspects × 2 provider kinds); full matrix 32 passed; env-gated live tests: `tests/test_advisor_live_integration.py -q` — 6 skipped (no API key in CI), no FAILED |

**Score:** 10/10 truths verified (0 present, behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `pyproject.toml` | anthropic>=0.72.0,<1.0 in [advisor] extra | ✓ VERIFIED | Line 42 confirmed |
| `tests/test_mcp_import_smoke.py` | MCP v2 import smoke test, version-gated to 3.10+ | ✓ VERIFIED | Exists, 3102 bytes, module-level pytestmark skip, 3 passed |
| `tests/test_guard_sync_version_independent.py` | Version-independent guard-sync, runs on 3.9 | ✓ VERIFIED | Exists, 6364 bytes, no pytestmark, no top-level mcp import, 3 passed |
| `python/fdars/advisor/aspects/inference.py` | ITP branch in `_build_inference_diagnostics` | ✓ VERIFIED | ITP shape detection by `adjusted_pvalues` key; detection+localisation scalars; raw array not stored |
| `python/fdars/advisor/aspects/fpca.py` | PACE extra scalars in has_pace_fpca branch | ✓ VERIFIED | `pace_noise_signal_ratio`, `pace_truncated_rank_flagged`, `pace_mean_prediction_band_width` added; stable None in else branch |
| `python/fdars/advisor/aspects/classification.py` | overfitting gap + class-count flag; holdout_accuracy kwarg | ✓ VERIFIED | `holdout_accuracy` parameter threaded through; `overfitting_gap`, `n_classes_flagged` emitted; None when no holdout |
| `python/fdars/advisor/_prompts.py` | Extended fpca/classification/inference primers | ✓ VERIFIED | 11 keys total; all three aspects contain the required scalar names; `localis` present in inference entry |
| `tests/test_advisor_itp.py` | ITP detection+localisation scalar tests + primer tests | ✓ VERIFIED | Exists, 16409 bytes, 29 tests pass |
| `tests/test_advisor_group_b.py` | Extended PACE (10 new) + elastic (13 new) tests | ✓ VERIFIED | 45 PACE/elastic tests pass |
| `tests/test_aspect_provider_matrix.py` | 3 new aspect fixtures (fpca_pace, classification_elastic, inference_itp) | ✓ VERIFIED | `grep -c` returns >=12 matches; 6 new cases pass; full matrix 32 passed |
| `tests/test_advisor_live_integration.py` | Env-gated live coverage for 3 new aspects | ✓ VERIFIED | `_ANTHROPIC_GATE`, 3 `test_aspect_live_*` tests; 6 skipped without API key |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| ITP `adjusted_pvalues` array | `inference.py` ITP branch scalar reduction | `has_itp_keys` detection by key presence | ✓ WIRED | `[float(v) for v in raw["adjusted_pvalues"]]` iterates array; never stored |
| PACE `fitted_lower`/`fitted_upper` arrays | `fpca.py` mean prediction-band width scalar | `np.asarray(...).mean()` cast to `float()` | ✓ WIRED | `float((fu_arr - fl_arr).mean())` confirmed in source |
| Every new scalar | `_check_grounding` / `_flatten_diagnostics_numbers` | `test_check_grounding_survives` in TestItpGrounding | ✓ WIRED | Test builds valid Advice citing ITP scalars and calls `_check_grounding(advice, diag)` — passes |
| New aspect diagnostics (50-02) | Matrix fixtures | `_ASPECT_ID_TO_METHOD` routing + `_ASPECT_FIXTURES` tuples | ✓ WIRED | 6 new matrix cases pass `_check_grounding` across native+fallback providers |
| `build_diagnostics` signature | `holdout_accuracy` kwarg | Threaded into `_build_classification_diagnostics` | ✓ WIRED | `holdout_accuracy` parameter in both `build_diagnostics` and `_build_classification_diagnostics`; confirmed in source |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|---------------|--------|--------------------|--------|
| `inference.py` ITP path | `itp_min_adjusted_pvalue` | `min([float(v) for v in raw["adjusted_pvalues"]])` — caller-supplied fdars result | Yes — native float computed from fdars result array | ✓ FLOWING |
| `fpca.py` PACE path | `pace_noise_signal_ratio` | `float(pace_sigma2 / total_signal_variance)` — fdars-computed sigma2 and eigenvalue sum | Yes — native float computed from fdars result | ✓ FLOWING |
| `classification.py` elastic path | `overfitting_gap` | `float(train_acc - float(holdout_accuracy))` — fdars train_accuracy minus caller holdout | Yes — native float; None when no holdout (grounding invariant preserved) | ✓ FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| ITP detection+localisation scalars correct for 1-of-5 significant fixture | Python: `build_diagnostics({adjusted_pvalues:[0.02,0.80,...]},'inference')` | `min=0.02, detected=True, n_sig=1, frac=0.2, first=0` | ✓ PASS |
| ITP no-significant fixture yields None first_basis | Python: all p > 0.05 fixture | `n_sig=0, detected=False, first_significant_basis=None` | ✓ PASS |
| ITP `adjusted_pvalues` not stored in diag | Python: `'adjusted_pvalues' not in diag` | True | ✓ PASS |
| PACE noise/signal ratio numerically correct | Python: `sigma2=0.05 / sum([3.0,1.5,0.5])=5.0 = 0.01` | `pace_noise_signal_ratio=0.01` | ✓ PASS |
| PACE truncated-rank flag correct for ncomp=2 < 3 eigenvalues | Python: `pace_truncated_rank_flagged` | True | ✓ PASS |
| Elastic overfitting_gap is None when no holdout | Python: `build_diagnostics(...,'classification')['overfitting_gap']` | None | ✓ PASS |
| All three diagnostics survive json.dumps | Python: `json.dumps(diag)` | Succeeds for all three | ✓ PASS |
| _check_grounding survives ITP | `test_advisor_itp.py::TestItpGrounding::test_check_grounding_survives` | 29 tests pass | ✓ PASS |
| Aspect×provider matrix 6 new cases | `pytest tests/test_aspect_provider_matrix.py -k "pace or elastic or itp" -q` | 6 passed | ✓ PASS |
| Full matrix 32 cases (QUAL-02 contract intact) | `pytest tests/test_aspect_provider_matrix.py -q` | 32 passed | ✓ PASS |
| Live integration tests skip cleanly | `pytest tests/test_advisor_live_integration.py -q` | 6 skipped, 0 failed | ✓ PASS |
| Compat pre-flight tests | `pytest tests/test_mcp_import_smoke.py tests/test_guard_sync_version_independent.py -q` | 3 passed | ✓ PASS |
| Guard-sync no-op: _supported == _DIAGNOSTICS_METHODS | Python: `supported == _DIAGNOSTICS_METHODS` | True, 14 elements each | ✓ PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|----------|
| COMPAT-01 | 50-01 | anthropic pinned >=0.72.0,<1.0 in [advisor] extra | ✓ SATISFIED | `pyproject.toml:42` confirmed |
| COMPAT-02 | 50-01 | MCP v2 MCPServer + 3 tools import via regression test | ✓ SATISFIED | `test_mcp_import_smoke.py` — 3 passed (skips on 3.9) |
| COMPAT-03 | 50-01 | Guard-sync assertion runs on Python 3.9 without importing mcp | ✓ SATISFIED | `test_guard_sync_version_independent.py` — primary test no pytestmark, no top-level mcp import |
| ASPECT-01 | 50-02 | PACE-FPCA emits grounded sigma2 ratio, truncated-rank flag, mean band width | ✓ SATISFIED | `fpca.py` has_pace_fpca branch; 45 tests pass |
| ASPECT-02 | 50-02 | elastic-multinomial emits grounded overfitting gap + class-count flag | ✓ SATISFIED | `classification.py` has_elastic_multinomial branch; 45 tests pass |
| ASPECT-03 | 50-02 | ITP reduces p-curve to detection AND localisation scalars — never lone scalar | ✓ SATISFIED | `inference.py` ITP branch; all 5 localisation scalars + 2 detection scalars present; 29 tests pass |
| ASPECT-04 | 50-02 | _ASPECT_PRIMERS extended; grounding invariant + guard-sync preserved | ✓ SATISFIED | 11 keys (was 10; note: `fpca` key was absent pre-phase and added); guard-sync no-op confirmed; all primer extensions contain required scalar names and 'localis' |
| ASPECT-05 | 50-03 | advise() grounded interpretation for 3 new aspects, verified offline and env-gated live | ✓ SATISFIED | Matrix: 6 new cases pass (3×2); live: 6 skip cleanly without API key |

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| — | — | — | — | No debt markers, stubs, or placeholder patterns found in any phase-modified file |

### Human Verification Required

None — all must-haves are mechanically verifiable. The live-LLM path (ASPECT-05 live) is env-gated by design and skips cleanly in CI; this is the intended behavior, not a gap.

### Gaps Summary

No gaps. All 10 must-haves are verified against the actual codebase. Phase goal is achieved.

**Notable deviation from PLAN accepted:** Plan 50-02 stated the `"fpca"` key already existed in `_ASPECT_PRIMERS`. The actual pre-phase dict had 10 keys with no `"fpca"` entry. The executor added it as a new key (10 → 11), which is within the plan's `len <= 14` acceptance criterion. This is a correct fix to an incorrect PLAN assumption, not a grounding issue — the guard-sync constraints cover `_DIAGNOSTICS_METHODS` and `build_diagnostics._supported` (both unchanged), not `_ASPECT_PRIMERS` keys.

---

_Verified: 2026-08-23T21:37:47Z_
_Verifier: Claude (gsd-verifier)_
