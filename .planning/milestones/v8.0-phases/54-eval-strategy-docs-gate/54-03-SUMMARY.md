---
phase: 54-eval-strategy-docs-gate
plan: "03"
subsystem: docs
tags: [advisor, documentation, comparative-selection, pipeline-report, auto-tuning, aspects, nav, FDARS_FENCE_OK, offline-fence, DOCS-01, DOCS-02]

requires:
  - phase: 54-02
    provides: "advisor-comparative-selection.svg, advisor-pipeline-report.svg, advisor-auto-tuning.svg"
  - phase: 51-comparative-method-selection
    provides: "compare_methods() fdars-authoritative winner, _normalize_candidates, _rank"
  - phase: 52-pipeline-diagnostic-report
    provides: "build_pipeline_report(), _compute_cross_stage_caveats R1/R2/R3, per-stage labeled blocks"
  - phase: 53-closed-loop-auto-tuning-capstone
    provides: "auto_tune(), FakeProvider offline testing pattern, TuneResult, 5 stop reasons"
  - phase: 50-deferred-advisor-aspects-compat-pre-flight
    provides: "PACE-FPCA scalars, ITP detection+localisation scalars, elastic-multinomial overfitting_gap"

provides:
  - "docs/advisor/comparative-selection.md — mature-page with embedded SVG + offline FDARS_FENCE_OK worked example"
  - "docs/advisor/pipeline-report.md — mature-page with embedded SVG + offline FDARS_FENCE_OK worked example"
  - "docs/advisor/auto-tuning.md — mature-page with embedded SVG + offline FakeProvider FDARS_FENCE_OK worked example (no API key)"
  - "docs/advisor/aspects.md — updated with PACE-FPCA, ITP detection+localisation, elastic-multinomial deferred scalars"
  - "mkdocs.yml — AI Advisor nav extended with three new page entries"

affects:
  - 54-04 (DOCS-03 human review gate: reviews these three pages and their diagrams)

actuals:
  tokens: 18500
  tasks: 3
  commits: 3

tech-stack:
  added: []
  patterns:
    - "FakeProvider offline pattern: injectable Provider satisfying protocol (name, model, supports_native_structured_output, complete_structured); FakeProvider used in docs fence without API key"
    - "mature-page structure: intro/method/worked-example/parameters/caveats applied to three new advisor capability pages"
    - "pre-built diagnostics dict pattern in fences: build pre-built dicts with 'method' key to bypass fdars calls in offline fences"

key-files:
  created:
    - docs/advisor/comparative-selection.md
    - docs/advisor/pipeline-report.md
    - docs/advisor/auto-tuning.md
  modified:
    - docs/advisor/aspects.md
    - mkdocs.yml

key-decisions:
  - "comparative-selection fence uses pre-built diagnostics dicts (not raw fdars calls) to stay offline — the compare_methods() offline path accepts pre-built dicts without needing actual fdars data"
  - "pipeline-report fence uses pre-built diagnostics dicts for represent+fpca raw results via build_diagnostics() and direct dict for represent — this avoids any potential fdars call issues"
  - "auto-tuning fence uses FakeProvider + injectable _run_method/_build_diagnostics seams per the 53-02 offline test pattern — maps directly to the proven offline approach"
  - "aspects.md appended PACE/ITP/elastic scalars to existing sections without rewriting existing rows — preserving backward compatibility"
  - "overfitting_gap documented with explicit warning that None when holdout_accuracy absent — grounding invariant preserved in prose"
  - "ITP scalars documented in two named families (detection vs localisation) with tip block explaining the whether-vs-where distinction"

requirements-completed: [DOCS-01, DOCS-02]

coverage:
  - id: D1
    description: "comparative-selection.md — mature-page with Plan-02 SVG embed, offline compare_methods(run_llm=False) fence emitting FDARS_FENCE_OK"
    requirement: DOCS-01
    verification:
      - kind: other
        ref: "test -f docs/advisor/comparative-selection.md && grep -q FDARS_FENCE_OK docs/advisor/comparative-selection.md (PASS)"
        status: pass
    human_judgment: true
    rationale: "Method-accuracy of the page prose (does it faithfully describe COMPARE-01/02/03 semantics) requires human review — Plan 04 DOCS-03 gate"
  - id: D2
    description: "pipeline-report.md — mature-page with Plan-02 SVG embed, offline build_pipeline_report(run_llm=False) fence emitting FDARS_FENCE_OK"
    requirement: DOCS-01
    verification:
      - kind: other
        ref: "test -f docs/advisor/pipeline-report.md && grep -q FDARS_FENCE_OK docs/advisor/pipeline-report.md (PASS)"
        status: pass
    human_judgment: true
    rationale: "Method-accuracy of the page prose (does it faithfully describe PIPE-01/02/03 semantics) requires human review — Plan 04 DOCS-03 gate"
  - id: D3
    description: "auto-tuning.md — mature-page with Plan-02 SVG embed, offline FakeProvider fence emitting FDARS_FENCE_OK (no API key, no network)"
    requirement: DOCS-01
    verification:
      - kind: other
        ref: "test -f docs/advisor/auto-tuning.md && grep -q FDARS_FENCE_OK docs/advisor/auto-tuning.md && ! grep -q ANTHROPIC_API_KEY docs/advisor/auto-tuning.md (all PASS)"
        status: pass
    human_judgment: true
    rationale: "Method-accuracy of the page prose (does it faithfully describe TUNE-02/03/05 semantics) requires human review — Plan 04 DOCS-03 gate"
  - id: D4
    description: "aspects.md updated with three Phase-50 deferred-aspect scalar families (PACE-FPCA, ITP, elastic-multinomial); existing rows preserved"
    requirement: DOCS-01
    verification:
      - kind: other
        ref: "grep -q pace_noise_signal_ratio docs/advisor/aspects.md && grep -q itp_min_adjusted_pvalue docs/advisor/aspects.md && grep -q overfitting_gap docs/advisor/aspects.md (all PASS)"
        status: pass
    human_judgment: false
  - id: D5
    description: "mkdocs.yml AI Advisor nav lists comparative-selection, pipeline-report, auto-tuning"
    requirement: DOCS-02
    verification:
      - kind: other
        ref: "grep -q advisor/comparative-selection.md mkdocs.yml && grep -q advisor/pipeline-report.md mkdocs.yml && grep -q advisor/auto-tuning.md mkdocs.yml (all PASS)"
        status: pass
    human_judgment: false
  - id: D6
    description: "All three fences execute offline and emit FDARS_FENCE_OK (verified by running fence code via python)"
    requirement: DOCS-02
    verification:
      - kind: other
        ref: "PYTHONPATH=scripts .venv/bin/python -c '<fence code>' → FDARS_FENCE_OK for all three fences"
        status: pass
    human_judgment: false

duration: 5min
completed: "2026-08-30"
status: complete
---

# Phase 54 Plan 03: Three Advisor Docs Pages + Aspects Update Summary

**Three mature-structure pages (comparative-selection, pipeline-report, auto-tuning) with embedded Plan-02 SVGs and offline FDARS_FENCE_OK worked examples; aspects.md updated with PACE-FPCA noise/signal, ITP detection+localisation, and elastic-multinomial overfitting scalars; AI Advisor nav wired in mkdocs.yml.**

## Performance

- **Duration:** 5 min
- **Started:** 2026-08-30T21:38:14Z
- **Completed:** 2026-08-30T21:43:56Z
- **Tasks:** 3
- **Files modified:** 5

## Accomplishments

- `docs/advisor/comparative-selection.md` — mature-page (intro/method/worked-example/parameters/caveats) embedding `advisor-comparative-selection.svg`; offline fence uses pre-built smoothing diagnostics dicts + `compare_methods(run_llm=False)` returning fdars-authoritative winner; documents fdars-computed winner invariant (COMPARE-01), incommensurability guard (COMPARE-03), per-candidate labeled blocks (COMPARE-02), union grounding
- `docs/advisor/pipeline-report.md` — mature-page embedding `advisor-pipeline-report.svg`; offline fence builds synthetic three-stage pipeline (represent→fpca→cluster) using `build_pipeline_report(run_llm=False)`; documents per-stage labeled blocks (never flat-merged), Python cross-stage R1/R2/R3 caveats before LLM, union grounding
- `docs/advisor/auto-tuning.md` — mature-page embedding `advisor-auto-tuning.svg`; offline fence uses `FakeProvider` + injectable `_run_method`/`_build_diagnostics` seams (proven 53-02 pattern) — no API key, no network; documents bounded termination (5 stop reasons), schema-validated `parameter_delta` numeric boundary, Goodhart guard after fdars re-run
- `docs/advisor/aspects.md` — appended three Phase-50 deferred-aspect scalar families: PACE-FPCA (`pace_noise_signal_ratio`, `pace_truncated_rank_flagged`, `pace_mean_prediction_band_width`); ITP detection (`itp_min_adjusted_pvalue`, `itp_detected_at_0.05`) + localisation (`itp_n_significant_0.05`, `itp_fraction_significant_0.05`, `itp_first_significant_basis`); elastic-multinomial (`overfitting_gap` + `n_classes_flagged`); existing rows preserved
- `mkdocs.yml` — AI Advisor nav extended with `Comparative Selection`, `Pipeline Report`, `Auto-Tuning` entries placed after `Python API` and before `Provider Setup`; indentation matches existing entries

## Task Commits

1. **Task 1: comparative-selection.md + pipeline-report.md** - `28f7941` (feat)
2. **Task 2: auto-tuning.md + aspects.md update** - `921120e` (feat)
3. **Task 3: nav wiring in mkdocs.yml** - `4651674` (feat)

## Files Created/Modified

- `docs/advisor/comparative-selection.md` (created) — Comparative method-selection page; embeds advisor-comparative-selection.svg; offline fence with pre-built smoothing diagnostics + compare_methods(run_llm=False)
- `docs/advisor/pipeline-report.md` (created) — Pipeline diagnostic report page; embeds advisor-pipeline-report.svg; offline fence with three-stage pipeline + build_pipeline_report(run_llm=False)
- `docs/advisor/auto-tuning.md` (created) — Closed-loop auto-tuning page; embeds advisor-auto-tuning.svg; offline fence using FakeProvider + injectable seams
- `docs/advisor/aspects.md` (modified) — Added PACE-FPCA, ITP detection+localisation, elastic-multinomial deferred scalars to fpca/classification/inference sections
- `mkdocs.yml` (modified) — AI Advisor nav extended with three new pages

## Decisions Made

- **comparative-selection fence uses pre-built diagnostics dicts:** The `compare_methods()` offline path accepts pre-built diagnostics dicts (has `"method"` key — passed through unchanged). This avoids needing actual fdars smoothing calls in the fence while still exercising the real compare_methods code path.
- **pipeline-report fence calls real build_diagnostics for fpca/clustering stages:** The fpca and clustering stages use real fdars calls (`regression.fpca`, `kmeans_fd`) on synthetic n=12 data — this exercises the full pipeline path through the real diagnostics builders while staying small enough for the docs build.
- **auto-tuning fence uses FakeProvider pattern from 53-02:** The injectable `_run_method`/`_build_diagnostics`/`provider` seams are the proven offline testing infrastructure from 53-02. The fence directly mirrors the test pattern, ensuring the docs example is grounded in the actual API seams.
- **ITP documented as two named families (detection vs localisation):** ASPECT-03 from Phase 50 established that detection and localisation scalars must be cited together. The aspects.md update names both families explicitly with a tip block explaining the "whether vs where" distinction.
- **overfitting_gap warning added:** The aspects.md `overfitting_gap` row includes a warning admonition explaining that the gap is `None` when `holdout_accuracy` is not supplied — matching the grounding invariant from Phase 50.

## Deviations from Plan

**1. [Rule 1 - Bug] Removed ANTHROPIC_API_KEY literal from auto-tuning.md prose**

- **Found during:** Task 2 acceptance criteria verification
- **Issue:** The auto-tuning page prose referenced `ANTHROPIC_API_KEY` in two places in explanatory text ("no ANTHROPIC_API_KEY is needed"). The plan's verify command `! grep -q 'ANTHROPIC_API_KEY' docs/advisor/auto-tuning.md` fails when the literal string appears anywhere in the file, even in a "not needed" context.
- **Fix:** Replaced "no `ANTHROPIC_API_KEY` is needed" with "no API key or network connection is needed" — semantically identical, but avoids the literal key name that the acceptance criterion forbids.
- **Files modified:** `docs/advisor/auto-tuning.md`
- **Verification:** `! grep -q 'ANTHROPIC_API_KEY' docs/advisor/auto-tuning.md` → PASS
- **Committed in:** 921120e (Task 2 commit)

## Issues Encountered

None beyond the API key literal deviation above (handled inline as Rule 1).

## Threat Mitigations Verified

| Threat | Status |
|--------|--------|
| T-54C-01: auto-tune fence reaching network | Mitigated — FakeProvider + injectable seams; `! grep -q ANTHROPIC_API_KEY` assertion passes |
| T-54C-02: fence data too large for DOCS_FAST build | Mitigated — all fences use n ≤ 20 synthetic data (n=12 for pipeline/clustering, synthetic dicts for comparative, synthetic call chain for auto-tune) |
| T-54C-03: aspects.md tampering (existing rows) | Mitigated — append-only; existing rows verified preserved via section-level Edit calls |
| T-54C-SC: pip/npm installs | Not applicable — no package installs in this plan |

## Known Stubs

None — all three pages carry complete content. Method-accuracy human review is intentionally deferred to Plan 04 (DOCS-03).

## Threat Flags

None — no new network endpoints, auth paths, file access patterns, or schema changes. Pure documentation authoring.

## Self-Check

| Check | Result |
|-------|--------|
| `docs/advisor/comparative-selection.md` exists | FOUND |
| `docs/advisor/pipeline-report.md` exists | FOUND |
| `docs/advisor/auto-tuning.md` exists | FOUND |
| FDARS_FENCE_OK in comparative-selection.md | PASS |
| FDARS_FENCE_OK in pipeline-report.md | PASS |
| FDARS_FENCE_OK in auto-tuning.md | PASS |
| advisor-comparative-selection.svg embedded | PASS |
| advisor-pipeline-report.svg embedded | PASS |
| advisor-auto-tuning.svg embedded | PASS |
| No ANTHROPIC_API_KEY string in auto-tuning.md | PASS |
| pace_noise_signal_ratio in aspects.md | PASS |
| itp_min_adjusted_pvalue in aspects.md | PASS |
| overfitting_gap in aspects.md | PASS |
| comparative-selection.md in mkdocs.yml nav | PASS |
| pipeline-report.md in mkdocs.yml nav | PASS |
| auto-tuning.md in mkdocs.yml nav | PASS |
| Commit 28f7941 (Task 1) | FOUND |
| Commit 921120e (Task 2) | FOUND |
| Commit 4651674 (Task 3) | FOUND |
| comparative-selection fence executes offline → FDARS_FENCE_OK | VERIFIED (python run) |
| pipeline-report fence executes offline → FDARS_FENCE_OK | VERIFIED (python run) |
| auto-tune fence executes offline → FDARS_FENCE_OK | VERIFIED (python run) |

## Self-Check: PASSED

---
*Phase: 54-eval-strategy-docs-gate*
*Completed: 2026-08-30*
