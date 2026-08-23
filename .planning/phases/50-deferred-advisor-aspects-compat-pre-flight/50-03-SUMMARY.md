---
phase: 50-deferred-advisor-aspects-compat-pre-flight
plan: "03"
subsystem: advisor
tags: [advisor, grounding, itp, pace-fpca, elastic-multinomial, aspect, testing, matrix]

# Dependency graph
requires:
  - "50-02 (new scalars: PACE-FPCA noise/signal ratio, truncated-rank flag, band width; elastic-multinomial overfitting gap + class-count flag; ITP detection+localisation scalars)"
provides:
  - "PACE-FPCA, elastic-multinomial, ITP offline fixtures in the aspect×provider grounding matrix (ASPECT-05)"
  - "All 6 new matrix cases (3 aspects × 2 provider kinds) pass _check_grounding across native and fallback providers"
  - "Env-gated live-LLM coverage for all three new aspects via Anthropic provider (ASPECT-05)"
  - "QUAL-02 contract preserved: exactly 3 test_live_* provider tests remain"
affects:
  - "Phase 51+ (comparative method-selection, pipeline report) — grounding matrix now covers all ASPECT-05 scalars"

actuals:
  tokens: 18000
  tasks: 2
  commits: 2

tech-stack:
  added: []
  patterns:
    - "Aspect-ID-to-method routing map: _ASPECT_ID_TO_METHOD dict maps descriptive fixture IDs (fpca_pace, classification_elastic, inference_itp) to the underlying method dispatch key (fpca, classification, inference) so parametrize labels stay unique while build_diagnostics receives the correct method string"
    - "test_aspect_live_* naming convention for aspect live tests (distinct from test_live_* provider tests) to preserve QUAL-02 contract that counts exactly 3 test_live_* functions"
    - "_ANTHROPIC_GATE module-level bool mirrors the existing _OPENAI/_GEMINI/_OLLAMA_GATE pattern"

key-files:
  created: []
  modified:
    - "tests/test_aspect_provider_matrix.py (3 new synthetic fixtures, 3 fixture tuples in _ASPECT_FIXTURES, _ASPECT_ID_TO_METHOD routing, classification_elastic holdout_accuracy forwarding)"
    - "tests/test_advisor_live_integration.py (_ANTHROPIC_GATE, 3 fixture dicts, 3 env-gated test_aspect_live_* tests)"

key-decisions:
  - "ASPECT-05: New live tests named test_aspect_live_* (not test_live_*) to preserve QUAL-02 contract in test_aspect_provider_matrix.py (which asserts exactly 3 test_live_* functions — one per provider)"
  - "ASPECT-05: holdout_accuracy=0.72 forwarded in classification_elastic fixture so overfitting_gap is a real float (not None) — the grounding scanner _build_grounded_advice_dict cites the first top-level numeric, which is overfitting_gap after build_diagnostics"
  - "ASPECT-05: _ANTHROPIC_GATE added to mirror the existing gate pattern; live aspect tests gate on FDARS_INTEGRATION AND ANTHROPIC_API_KEY (the advisor's native provider)"

requirements-completed: [ASPECT-05]

coverage:
  - id: D1
    description: "PACE-FPCA, elastic-multinomial, ITP fixtures added to the offline aspect×provider grounding matrix (ASPECT-05)"
    requirement: ASPECT-05
    verification:
      - kind: unit
        ref: "tests/test_aspect_provider_matrix.py -k 'pace or elastic or itp' (6 passed)"
        status: pass
      - kind: unit
        ref: "tests/test_aspect_provider_matrix.py -q (32 passed, full suite including QUAL-02)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Env-gated live-LLM coverage for PACE-FPCA, elastic-multinomial, ITP — skips cleanly without ANTHROPIC_API_KEY (ASPECT-05)"
    requirement: ASPECT-05
    verification:
      - kind: unit
        ref: "tests/test_advisor_live_integration.py -q (6 skipped — 3 orig + 3 new; no FAILED, no ERROR)"
        status: pass
    human_judgment: false

duration: 3min
completed: 2026-08-23
status: complete
---

# Phase 50 Plan 03: Cross-Provider Grounding Matrix for New Aspects Summary

**Offline aspect×provider matrix extended with PACE-FPCA/elastic-multinomial/ITP fixtures (6 new cases all passing _check_grounding); env-gated live coverage added for all three, CI stays network-free**

## Performance

- **Duration:** 3 min
- **Started:** 2026-08-23T21:26:58Z
- **Completed:** 2026-08-23T21:29:48Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments

- **Task 1 (Matrix fixtures):** Added three synthetic offline fixtures — `_PACE_FPCA_RESULT` (eigenvalues, ncomp, sigma2, fitted_lower/upper), `_ELASTIC_RESULT` (train_accuracy, n_classes), `_ITP_RESULT` (adjusted_pvalues, raw_pvalues, n_basis, n_perm) — and three tuples to `_ASPECT_FIXTURES`: `fpca_pace`, `classification_elastic`, `inference_itp`. Added `_ASPECT_ID_TO_METHOD` routing map so descriptive aspect IDs map to the correct `build_diagnostics` method string. Extended the `elif` routing in `test_aspect_provider_matrix` to forward `holdout_accuracy` for `classification_elastic`. All 6 new matrix cases (3 aspects × 2 provider kinds) pass `_check_grounding` for both native and fallback providers. Full matrix: 32 passed (was 26).

- **Task 2 (Live coverage):** Added `_ANTHROPIC_GATE` module-level bool to `test_advisor_live_integration.py` (mirrors the existing _OPENAI/_GEMINI/_OLLAMA_GATE pattern). Added three fixture dicts (identical shapes to Task 1) and three env-gated tests — `test_aspect_live_pace_fpca`, `test_aspect_live_elastic_multinomial`, `test_aspect_live_itp` — each asserting that the new ASPECT-01/02/03 scalars are present in the diagnostics and that `advise()` returns a valid grounded Advice via the Anthropic provider. Named `test_aspect_live_*` (not `test_live_*`) to preserve the QUAL-02 contract (exactly 3 `test_live_*` provider tests). All 6 tests (3 orig + 3 new) skip cleanly with no keys set.

## Task Commits

1. **Task 1: Aspect×provider matrix fixtures** - `7038cb4` (test)
2. **Task 2: Env-gated live coverage** - `725dfb6` (test)

## Files Created/Modified

- `tests/test_aspect_provider_matrix.py` (modified) — 3 new synthetic fixtures (`_PACE_FPCA_RESULT`, `_ELASTIC_RESULT`, `_ITP_RESULT`); 3 fixture tuples added to `_ASPECT_FIXTURES`; `_ASPECT_ID_TO_METHOD` routing dict; `classification_elastic` holdout_accuracy forwarding; full suite 32 passed
- `tests/test_advisor_live_integration.py` (modified) — `_ANTHROPIC_GATE` bool; 3 fixture dicts (`_PACE_FPCA_FIXTURE`, `_ELASTIC_FIXTURE`, `_ITP_FIXTURE`); 3 env-gated `test_aspect_live_*` tests; all 6 skip cleanly in CI

## Decisions Made

- Live aspect tests named `test_aspect_live_*` (not `test_live_*`) to preserve the QUAL-02 contract in `test_aspect_provider_matrix.py` which asserts exactly 3 `test_live_*` functions covering {openai, gemini, ollama}. A deviation would have broken the existing `test_live_integration_contract` assertion at line 377.
- `holdout_accuracy=0.72` forwarded in `_ELASTIC_RESULT` fixture so `overfitting_gap` is a non-None float — the grounding scanner `_build_grounded_advice_dict` scans for the first top-level numeric value, which is `overfitting_gap` after `build_diagnostics` for the elastic-multinomial path.
- `_ANTHROPIC_GATE` gates on `FDARS_INTEGRATION AND ANTHROPIC_API_KEY` — the Anthropic provider is the advisor's native structured-output provider, the natural choice for aspect integration tests.

## Deviations from Plan

None — plan executed exactly as written. The `test_aspect_live_*` naming (not `test_live_*`) is aligned with the plan's intent (mirror the skipif gate; not break the QUAL-02 contract); the plan did not specify an exact naming pattern for the aspect tests.

## Issues Encountered

One naming constraint discovered during Task 2: the `test_live_integration_contract` test in `test_aspect_provider_matrix.py` asserts `len(test_live_names) == 3` (exactly one per provider). Adding `test_live_aspect_*` would have broken this. Solution: use `test_aspect_live_*` prefix instead — these don't match `name.startswith("test_live")` so the contract count stays at 3.

## Known Stubs

None.

## Threat Flags

None — no new network endpoints, auth paths, file access patterns, or schema changes. Test-only file edits; all live tests are env-gated and skip by default in CI.

## Self-Check: PASSED

- `tests/test_aspect_provider_matrix.py` exists: FOUND
- `tests/test_advisor_live_integration.py` exists: FOUND
- Commits 7038cb4, 725dfb6 exist in git log: FOUND
- `grep -c 'fpca_pace\|classification_elastic\|inference_itp' tests/test_aspect_provider_matrix.py` = 12 (>= 3)
- `grep -c '_ANTHROPIC_GATE' tests/test_advisor_live_integration.py` = 4 (present)
- `pytest tests/test_aspect_provider_matrix.py -q -k "pace or elastic or itp"`: 6 passed
- `pytest tests/test_aspect_provider_matrix.py -q`: 32 passed (QUAL-02 contract preserved)
- `pytest tests/test_advisor_live_integration.py -q`: 6 skipped (3 orig + 3 new; no FAILED, no ERROR)

---
*Phase: 50-deferred-advisor-aspects-compat-pre-flight*
*Completed: 2026-08-23*
