# Feature Research

**Domain:** FDA AI advisor — new capabilities (v8.0)
**Researched:** 2026-08-23
**Confidence:** MEDIUM (web sources cross-checked against existing codebase)

---

## Context: What Already Exists (Do Not Rebuild)

The advisor surface shipped in v2.0-v6.0:
- `build_diagnostics(result, method)` — offline, deterministic, 14 aspects
- `advise(diagnostics, task, ...)` — grounded LLM call, 3 task families + `describe_cluster_differences`
- 4 providers (Anthropic / OpenAI / Gemini / Ollama), provider-agnostic
- MCP: 3 tools — `fdars_build_diagnostics`, `fdars_run_method` (6 methods), `fdars_compare_run` (before/after delta); provably LLM-free compute path
- `_ASPECT_PRIMERS` dict + `_system_prompt(task, aspect)` for per-aspect FDA context
- `HandleRegistry` with opaque result/dataset handles (by-reference invariant)

All four v8.0 capabilities build on this surface. Nothing below requires rebuilding it.

---

## Capability A — Fill Deferred Advisor Aspects

Three methods were deliberately deferred in v6.0 with minimal or no advisor coverage:
- **PACE-FPCA** (`fpca.py` has stubs: `has_pace_fpca`, `pace_ncomp`, `pace_sigma2`, `pace_variance_explained_cumulative` — but no quality flags, no band-width diagnostics, no noise-ratio signal, no aspect primer)
- **elastic-multinomial** (`classification.py` has stubs: `has_elastic_multinomial`, `train_accuracy`, `train_error_rate` — but no aspect primer extension, no OvR-class-balance signal)
- **ITP interval-inference** (the inference aspect uses a scalar `p_value` path — but ITP returns vector `adjusted_pvalues`/`raw_pvalues`; the vector is unreachable through the current inference builder, which only handles `TestResult`-scalar and `ToleranceBand` shapes)

### Table Stakes

Features that must exist for each deferred aspect to be usable:

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| PACE-FPCA: `sigma2_ratio` scalar | Noise-to-signal ratio is the primary PACE quality signal — sigma2/eigenvalues[0] > 0.5 means noise dominates; LLM cannot interpret PACE result without it | LOW | Computed from existing `pace_sigma2` and `eigenvalues[0]` already present in result dict |
| PACE-FPCA: `ncomp_truncated` flag | When actual `ncomp` < requested, rank deficiency occurred; advisor must flag this | LOW | `ncomp_actual != ncomp_requested`; needs `ncomp_requested` passed via kwargs to `build_diagnostics` |
| PACE-FPCA: `mean_band_width` scalar | Average (fitted_upper - fitted_lower) width across all n curves on work grid; measures prediction uncertainty | LOW | Computable from `fitted_upper` and `fitted_lower` arrays already in result dict; `np.mean(fitted_upper - fitted_lower)` |
| PACE-FPCA: aspect primer in `_ASPECT_PRIMERS` | LLM needs FDA context for PACE-specific scalars (sigma2_ratio, BLUP, band width) | LOW | Add "pace_fpca" key to `_ASPECT_PRIMERS` in `_prompts.py` |
| elastic-multinomial: `n_classes_flag` | OvR schemes scale quadratically; flag when n_classes > 3 as "many-class OvR" | LOW | `n_classes` already emitted; boolean flag |
| elastic-multinomial: `overfitting_gap` | Gap between train_accuracy and CV accuracy; indicates generalization quality | LOW | `overfitting_gap = train_accuracy - (1 - cv_error_rate)` when both present; else None |
| elastic-multinomial: aspect primer extension | Current "classification" primer covers elastic_multinomial briefly but lacks OvR-specific context | LOW | Extend existing "classification" entry in `_ASPECT_PRIMERS` |
| ITP: vector-to-scalar reduction builder | New builder branch in `_build_inference_diagnostics` that handles ITP result shape (keys: `adjusted_pvalues`, `raw_pvalues`, `basis_type`, `n_basis`, `n_perm`) | MEDIUM | Detect ITP shape by presence of `adjusted_pvalues` array key; process as numpy, emit plain Python types |
| ITP: `min_adjusted_pvalue` scalar | Global detection signal — minimum of adjusted p-value curve; answers "is there any difference?" | LOW | `float(np.min(adjusted_pvalues))` |
| ITP: `n_significant_intervals` at alpha=0.05 | Localisation count — how many basis intervals are significant; answers "how widespread?" | LOW | `int(np.sum(adjusted_pvalues < 0.05))` |
| ITP: `proportion_significant` scalar | Fractional localisation — n_significant / n_basis; scale-free across different nbasis choices | LOW | `n_significant_intervals / n_basis` |
| ITP: `first_significant_basis` index | Onset localisation — index of first significant basis component; answers "where does it start?" | LOW | Index of first element where `adjusted_pvalues < 0.05`; None when none significant |
| ITP: `detected_at_0.05` boolean | Primary detection flag; answers whether ANY basis interval is significant at alpha=0.05 | LOW | `bool(min_adjusted_pvalue < 0.05)` |
| ITP: aspect primer for ITP path | Current "inference" primer is calibrated to scalar TestResult, not vector ITP p-curves | LOW | Extend "inference" primer or add "itp" key; explain detection vs localisation distinction |

### Differentiators

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| PACE-FPCA: bandwidth sensitivity signal | If sigma2_ratio is high AND mean_band_width is large, both signals jointly indicate poor bandwidth calibration — compound flag | LOW | Derived from two already-computed scalars; no additional fdars call |
| PACE-FPCA: reconstruction quality via fitted vs raw | Mean L2 norm of (fitted - observed) on work grid as a reconstruction diagnostic | MEDIUM | Requires matching sparse observed points to work-grid positions — non-trivial alignment; low priority for v8.0 |
| ITP: `max_consecutive_significant` | Length of longest run of consecutive significant basis intervals — distinguishes localised spike from broad region | LOW | Single pass over bool array; high interpretive value for FDA narratives |
| elastic-multinomial: `class_confidence_gap` | Mean(max per-row probability) - second-highest; measures decision confidence | HIGH | Requires `class_models` which is excluded from binding (Phase 38 CR-01); defer |

### Anti-Features

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| PACE: reconstruct FVE via numerical integration | Users want same FVE metric as standard FPCA for direct comparison | pace_fpca eigenvalues are pre-scaled; re-deriving FVE via numerical integration in Python would drift from Rust implementation | Use `pace_variance_explained_cumulative` from existing `_eigenvalues_to_variance_cumulative` helper already wired in fpca.py stubs |
| ITP: report raw_pvalues as primary signal | Raw (pre-closure-adjustment) p-values look more significant | Reporting unadjusted p-values violates the ITP's designed interval-wise error control | Emit `raw_pvalues_min` as a secondary scalar with a clearly labelled "unadjusted" caveat; never present as primary detection signal |
| ITP: LLM decides which intervals are significant | LLM narrative about specific intervals sounds richer | LLM fabricating specific interval locations violates the grounding invariant | Emit `first_significant_basis` and `n_significant_intervals` as grounded integers; LLM cites these |
| elastic-multinomial: per-class accuracy breakdown | Detailed per-class report is more informative | Requires `class_models` excluded from binding (Phase 38 CR-01); rebuilding would need a binding change | Use `train_accuracy` + `n_classes` to derive expected per-class accuracy under uniform distribution as a baseline comparison |

### Feature Dependencies (Capability A)

```
ITP vector shape detection (inference.py new branch)
    +-enables-> min_adjusted_pvalue, n_significant_intervals, proportion_significant
                    +-enables-> detected_at_0.05, first_significant_basis
                                    +-enables-> ITP aspect primer (meaningful text)

PACE stubs already present (fpca.py)
    +-augmented-by-> sigma2_ratio, ncomp_truncated, mean_band_width
                         +-enables-> PACE aspect primer (meaningful text)

elastic_multinomial stubs already present (classification.py)
    +-augmented-by-> overfitting_gap, n_classes_flag
                         +-enables-> extended classification primer
```

**Existing advisor components used:**
- `_build_inference_diagnostics` in `inference.py` — add ITP branch; detected by `adjusted_pvalues` key
- `_build_fpca_diagnostics` in `fpca.py` — augment `has_pace_fpca` branch with new scalars
- `_build_classification_diagnostics` in `classification.py` — augment `has_elastic_multinomial` branch
- `_ASPECT_PRIMERS` in `_prompts.py` — extend "inference", "fpca" (PACE), "classification" entries
- `_DIAGNOSTICS_METHODS` guard in `server.py` — no change needed (ITP uses existing "inference" method)

**Grounding constraint:** all new scalars computed from arrays already returned by fdars (adjusted_pvalues, eigenvalues, fitted_upper/fitted_lower); no LLM inference about specific values.

---

## Capability B — Comparative Method-Selection

A recommender that runs multiple candidate fdars methods on the same data, builds diagnostics for each, then ranks and picks among them with grounded justification.

**How comparable tools work:** ML leaderboards and champion/candidate frameworks share: (1) run all candidates on same data, record per-metric scores; (2) rank per metric; (3) pick winner on primary metric; (4) justify by citing the winning value and the margin over the runner-up; (5) flag ties and near-ties; (6) note when no single method dominates.

**LLM role:** narrate WHY the winner is better, citing fdars-computed margins. Winner selection is deterministic (sort on primary metric); the LLM only provides explanation.

### Table Stakes

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| `compare_methods(dataset_id, methods, primary_metric, ...)` entry point | Single call orchestrating multi-run comparison; reuses `_runner.run_method` + `build_diagnostics` per candidate | MEDIUM | Returns `{"candidates": [...], "ranking": [...], "winner": str, "margin": float}` |
| Per-candidate diagnostics dict in result | Each candidate's full diagnostics available for LLM citation and user inspection | LOW | List of `{"method": str, "diagnostics": dict, "primary_metric_value": float, "rank": int}` |
| Deterministic winner selection on primary_metric | Winner chosen by sort on primary_metric; LLM does NOT choose the winner | LOW | `sorted(candidates, key=lambda c: c["diagnostics"][primary_metric])` with direction flag (lower/higher better) |
| `margin_to_next` scalar | Margin between each candidate and the next-ranked on primary_metric | LOW | `candidates[i+1][metric] - candidates[i][metric]` after sorting; enables "FPC-LM beats PLS by X" |
| `advise_comparison(comparison_result, domain_context, ...)` LLM call | Grounded LLM narration of the comparison; passes full comparison result as diagnostics | MEDIUM | Wraps `advise()` with `task="comparison"`; new task family in `_prompts.py` |
| "comparison" task family in `_system_prompt` | Task clause instructing LLM to cite winner, margin, runner-up; never invent rankings | LOW | Add to `_supported_tasks`; instruct LLM to cite the `winner` field and `margin_to_next` scalar |
| MCP tool `fdars_compare_methods` | Agentic surface; takes method list + primary_metric; returns comparison result dict; LLM-free compute path | MEDIUM | New tool in `server.py`; restricted to `_RUNNABLE_METHODS`; orchestrates run+diagnostics per candidate |

### Differentiators

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Multi-metric ranking | Shows per-metric rankings so users see trade-offs (best cv_error may have worse explained_variance) | LOW | Already possible once comparison result includes all diagnostics; just surface per-metric rank |
| Tie detection threshold | Flag when margin < user-defined threshold as "effectively tied" — prevents overconfident picks | LOW | One comparison against threshold param; emit `is_tie: bool` |
| No-winner flag | When no single method wins on primary AND all secondary metrics simultaneously | LOW | Check if same method ranks 1st across all; emit `has_clear_winner: bool` |

### Anti-Features

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| LLM-chosen winner | "Let the AI pick the best method" | Violates grounding invariant; LLM can hallucinate rankings | Winner always determined by deterministic sort on fdars-computed primary_metric scalar; LLM cites the rank |
| Multi-objective weighted aggregation into single score | Reduces comparison to one number for simplicity | Weights are user-domain choices; hides trade-offs; creates false confidence | Present per-metric rankings and flag the primary-metric winner; no aggregated score |
| Comparing diagnostics-only methods | Those methods produce richer diagnostics | Diagnostics-only methods (regression, classification) need caller-supplied inputs (labels, y, reference) that the coordinator cannot supply at run-time | Restrict comparison to `_RUNNABLE_METHODS` (6 methods); diagnostics-only methods can be added by caller as pre-computed diagnostics |

### Feature Dependencies (Capability B)

```
_runner.run_method (6 runnable methods, existing)
    +-used-by-> compare_methods() orchestrator (new)
                    +-uses-> build_diagnostics() per candidate (existing)
                                 +-aggregates-into-> comparison_result dict (new)
                                                         +-passed-to-> advise_comparison() (new)
                                                                            +-uses-> advise() (existing)
                                                                                     +-uses-> "comparison" task (new)
```

```
HandleRegistry (existing)
    +-used-by-> fdars_compare_methods MCP tool (new)
                    +-restricted-to-> _RUNNABLE_METHODS
```

---

## Capability C — Pipeline Diagnostic Report

A multi-aspect narrative report for an end-to-end FDA analysis, aggregating diagnostics across N pipeline stages into one Advice object.

**How comparable tools work:** ML pipeline report patterns include: (1) per-stage diagnostics blocks, ordered by pipeline sequence; (2) inter-stage transition signals (upstream quality affects downstream); (3) aggregated summary with overall health flag and flagged issues; (4) traceability — each cited value traceable to fdars-computed origin.

**Key structural insight:** A pipeline report is N `build_diagnostics` calls (one per stage) plus one `advise` call receiving a dict-of-dicts. The LLM synthesises across stages, not just summarises each independently.

### Table Stakes

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| `build_pipeline_diagnostics(stages)` offline aggregator | Deterministic aggregation of N stage diagnostics; no LLM | LOW | `stages: list[tuple[str, dict]]` — (stage_name, diagnostics_dict); validates and assembles; preserves input order |
| Stage ordering preserved | Report must reflect actual pipeline order (represent -> smooth -> fpca -> cluster) | LOW | Preserve input list order; do not sort alphabetically |
| Per-stage `has_warnings` flag rollup | Boolean derived from stage-level flag scalars (e.g. `phase_leakage_flagged`, `significant_at_0.05`) | LOW | Apply per-aspect flag rules already encoded in each aspect builder |
| `n_flagged_stages` scalar | How many stages have at least one warning flag; top-level summary scalar | LOW | `sum(s.get("has_warnings", False) for s in assembled)` |
| `report_pipeline(stages, domain_context, ...)` LLM call | Grounded LLM narration across all stages | MEDIUM | Wraps `advise()` with `task="pipeline"` |
| "pipeline" task family in `_system_prompt` | Task clause instructing LLM to synthesise cross-stage signals, not repeat per-stage detail | LOW | Add to `_supported_tasks` |
| Flattened diagnostics schema for LLM context | Pipeline report sends N * 15+ keys; must be flat (not nested) to avoid LLM confusion and context size issues | MEDIUM | Flatten with stage prefixes: `represent_n_points`, `fpca_cumulative_variance_explained`, etc. |

### Differentiators

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Cross-stage signal detection (offline) | Flag when stage A quality issue likely affects stage B (e.g. high `imputed_fraction` in represent -> caveats for downstream FPCA) | MEDIUM | Hardcoded cross-stage rules; no LLM needed; adds `cross_stage_warnings: list[str]` to pipeline report |
| Pipeline health score | Integer 0-N counting stages without warnings; quick overview | LOW | `n_stages - n_flagged_stages`; include in pipeline report |
| MCP tool `fdars_build_pipeline_diagnostics` | Agentic surface; takes list of result_ids with stage names; LLM-free compute | MEDIUM | New tool; orchestrates `build_diagnostics` per stage; parameter schema for list of handles requires care |

### Anti-Features

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| LLM runs intermediate fdars steps | "Let the AI drive the whole pipeline" | Pipeline steps require user data and domain choice (which method, which parameters) that cannot be automated without human judgment | Advisor takes pre-computed stage results; user runs fdars; closed-loop auto-tuning (Capability D) handles the automation layer |
| Single aggregated "pipeline score" | Summarises everything in one number | Hides which stages are problematic; false confidence | Provide per-stage flags + `n_flagged_stages`; let narrative synthesise |
| Cross-stage parameter propagation | Automatically adjust downstream parameters based on upstream results | Requires domain judgment; violates LLM-free-compute constraint if applied automatically | Surface the cross-stage signal as a diagnostic; let the LLM recommend and the human apply |

### Feature Dependencies (Capability C)

```
build_diagnostics (existing, per-method)
    +-called N times-> build_pipeline_diagnostics() (new aggregator)
                           +-passed-to-> report_pipeline() LLM call (new)
                                             +-uses-> advise() (existing)
                                                      +-uses-> "pipeline" task family (new)
```

**Requires Capability A first:** If deferred aspects (PACE-FPCA, elastic-multinomial, ITP) appear as pipeline stages, their grounded diagnostics must exist. Do Capability A before Capability C.

---

## Capability D — Closed-Loop Auto-Tuning (Capstone)

Turns the existing manual recommend -> re-run -> compare loop into an autonomous, bounded loop: the advisor proposes a parameter/method change, applies it, re-runs fdars, compares diagnostics, and iterates until a target diagnostic improves or a step budget is hit. The compute path stays LLM-free; the LLM only proposes and interprets.

**What applies from AutoML/HPO pattern (Optuna, Ray Tune, SMAC cross-check):**
- Max steps hard budget (analogous to max_trials)
- No-improvement window / patience (analogous to early stopping)
- Oscillation guard (not present in standard HPO — specific to sequential LLM-guided loop)
- Explicit target threshold (stop when diagnostic crosses goal value)

**What does NOT apply:**
- Bayesian surrogate model (LLM is the proposal mechanism; no surrogate)
- Parallel trial pruning (loop is sequential)
- Multi-fidelity resource allocation (ASHA/HyperBand)
- Surrogate expected improvement / acquisition functions

### Table Stakes

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| `autotune(dataset_id, method, target_metric, *, max_steps, direction, ...)` Python API | Single call running the bounded loop; returns `AutotuneResult` | HIGH | Orchestrates: propose (LLM) -> apply (run_method) -> measure (build_diagnostics) -> compare -> repeat |
| `max_steps` hard budget (required param) | Loop must terminate unconditionally | LOW | `step >= max_steps` check at top of each iteration; emit `stop_reason="budget_exhausted"` |
| `target_metric` + `direction` params | User specifies which diagnostic to optimise and whether lower or higher is better | LOW | e.g. `target_metric="cv_error_rate", direction="minimize"` |
| `target_value` optional threshold | Loop stops when target_metric reaches/crosses threshold | LOW | e.g. `target_value=0.05` — stop when cv_error_rate <= 0.05 |
| No-improvement patience stop | Stop when target_metric does not improve by >= `min_delta` for `patience` consecutive steps | LOW | Track per-step delta history; `stop_reason="no_improvement"` |
| Oscillation guard | Detect alternating-sign consecutive per-step deltas; halt | LOW | Track sign of last K deltas; if alternates for K >= 3 steps, halt; `stop_reason="oscillation_detected"` |
| LLM-proposed parameter change per step | Each step: send current diagnostics to `advise(task="parameter")`; extract Recommendation with `kind="parameter"`; parse to parameter dict | HIGH | Parameter parsing from Recommendation.action is the fragile component — see pitfalls below |
| Structured parameter delta in Recommendation schema | To avoid fragile free-text parsing, add `parameter_delta: dict[str, float | int] | None` field to `Recommendation` Pydantic model | MEDIUM | Schema change to `_schema.py`; field is optional (None for kind="none"/"method"); LLM emits structured dict |
| Apply proposed parameter via existing runner | `run_method(dataset_id, method, **parsed_params)` using `_runner.run_method` | LOW | Reuses existing code exactly; no new compute |
| Compare before/after via existing delta logic | `build_diagnostics` + delta from `_compare.compare_run` | LOW | Reuses `_compare.compare_run` exactly |
| `AutotuneResult` schema | `{"history": [...], "best_params": dict, "final_diagnostics": dict, "stop_reason": str, "n_steps": int, "improved": bool}` | LOW | Pydantic or dataclass |
| Grounding invariant preserved throughout | Every LLM call uses existing `advise()` + `_check_grounding` path; loop only adds orchestration | LOW | Coordinator calls existing code; no new LLM paths outside standard grounding guard |

### Differentiators

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| `callback` / `yield_on_each_step` | Human-in-the-loop inspection at each step without stopping the loop | MEDIUM | Generator pattern or `callback(step, diagnostics, proposed_params) -> bool` to continue |
| History replay in `AutotuneResult` | Full step-by-step trajectory; user can see each parameter tried and its diagnostic outcome | LOW | `history: list[{"step": int, "params": dict, "diagnostics": dict, "delta": float, "stop_signals": list}]` |
| Best-of-history tracking | Track the best diagnostics across all steps, not just the final; useful when loop oscillates | LOW | `best_params = argmax over history on target_metric`; always returned in `AutotuneResult` |
| Warm-start from prior result | If user has an existing result_id, skip step 0 compute | LOW | Optional `initial_result_id` param; use as step 0 without re-running |

### Anti-Features

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| LLM computes the comparison delta | "Let the AI decide if the run improved" | Violates LLM-free-compute constraint; LLM fabricating improvement deltas is exactly what grounding invariant prevents | `compare_run` (existing, deterministic) computes the delta; LLM receives the numeric delta in diagnostics |
| Unbounded loop (no max_steps) | "Keep going until it converges" | A stuck LLM or oscillating parameter loops forever, consuming API credits | `max_steps` is a required parameter; hard-coded upper cap at 20 |
| Bayesian surrogate model for proposals | Smarter search than asking the LLM | Mixes two proposal mechanisms; requires separate HPO infra (Optuna/SMAC) | LLM-as-proposer is the design; if richer search needed, that is a separate HPO integration milestone |
| MCP tool `fdars_autotune` with `advise()` inside | Natural implementation puts LLM call inside the tool | Breaks MCP's LLM-free-compute contract; creates unobservable inner loop | The agentic loop over MCP is orchestrated by the LLM client calling existing tools (`fdars_run_method`, `fdars_compare_run`) in sequence; `fdars_autotune` as a single monolithic MCP tool is an anti-feature |

**Critical MCP boundary clarification:** MCP tools must stay LLM-free. This means a monolithic `fdars_autotune` MCP tool cannot internally call `advise()`. The agentic loop over MCP must be orchestrated by the LLM client (the Claude agent), using the existing tools per step. The Python API `autotune()` CAN call `advise()` internally.

### Feature Dependencies (Capability D)

```
autotune() Python API (new)
    +-requires-> advise() (existing, for proposals)
    +-requires-> _runner.run_method() (existing, for applying params)
    +-requires-> compare_run() (existing, for delta computation)
    +-requires-> build_diagnostics() (existing, for measuring state)
    +-requires-> Recommendation.parameter_delta (new schema field)
    +-produces-> AutotuneResult (new)

MCP agentic loop pattern (documentation only):
    +-orchestrated-by-> LLM client (external)
    +-uses-> fdars_run_method (existing tool)
    +-uses-> fdars_compare_run (existing tool)
    +-uses-> fdars_build_diagnostics (existing tool)
```

**Sequencing:** Capability D requires Capabilities A (richer diagnostics to target) and B (awareness of method alternatives). Implement D last.

---

## Eval Strategy (Cross-Cutting)

### Table Stakes

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Deterministic improvement test for auto-tuning | Given synthetic data with known optimum, verify loop terminates with better-than-initial params | LOW | Offline; no LLM key; fixed seed + known-optimum synthetic data |
| Grounding pass rate for comparison | Given comparison result, verify winning method in Advice.recommendations matches deterministic rank winner | LOW | Offline check: `advice.recommendations[0].action` must reference the highest-ranked method name |
| Step-count regression test | Verify auto-tuning loop terminates in <= max_steps for a standard input | LOW | Smoke test; verifies budget hard stop |
| Oscillation detection unit test | Verify oscillation guard triggers on synthetically alternating delta sequence | LOW | Unit test; no fdars call needed |

### Differentiators

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Aspect x proposal match rate (env-gated) | For each aspect, measure how often LLM's proposed parameter matches expected direction; requires LLM API key | MEDIUM | Env-gated; CI only when ANTHROPIC_API_KEY present; follows `test_aspect_provider_matrix.py` pattern |

---

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| ITP vector-to-scalar reduction builder | HIGH | MEDIUM | P1 — foundation for ITP advise |
| ITP grounded scalars (min_p, n_significant, proportion, first_basis, detected_at_0.05) | HIGH | LOW | P1 — all from same vector pass |
| PACE-FPCA sigma2_ratio + ncomp_truncated + mean_band_width | HIGH | LOW | P1 — fills the most-requested gap |
| Aspect primer extensions (PACE, ITP, elastic-multinomial) | HIGH | LOW | P1 — required for LLM to interpret new diagnostics |
| elastic-multinomial overfitting_gap + n_classes_flag | MEDIUM | LOW | P1 — completes the OvR picture |
| Eval: deterministic improvement + grounding tests | HIGH | LOW | P1 — must ship with capabilities |
| `compare_methods()` Python API | HIGH | MEDIUM | P2 — core of capability B |
| Deterministic winner selection + rank table | HIGH | LOW | P2 — grounding constraint |
| "comparison" task family in system prompt | HIGH | LOW | P2 — LLM narration |
| `build_pipeline_diagnostics()` aggregator | HIGH | LOW | P2 — straightforward aggregation |
| "pipeline" task family in system prompt | HIGH | LOW | P2 — multi-stage narration |
| MCP `fdars_compare_methods` tool | MEDIUM | MEDIUM | P2 — extends MCP surface |
| `autotune()` Python API core loop | HIGH | HIGH | P3 — capstone; implement last |
| max_steps + patience + oscillation guard stops | HIGH | LOW | P3 — safety rails for autotune |
| Recommendation.parameter_delta schema field | HIGH | MEDIUM | P3 — required for autotune param parsing |
| Cross-stage signal detection (offline) | MEDIUM | MEDIUM | P3 — valuable but not blocking |
| History replay in AutotuneResult | LOW | LOW | P3 — add once core loop works |
| MCP autotune agentic orchestration pattern | MEDIUM | HIGH | P3 — complex boundary; document pattern |
| Tie detection / no-winner flag in comparison | LOW | LOW | P3 — polish |

---

## Phase-Specific Warnings

| Phase Topic | Likely Pitfall | Mitigation |
|-------------|---------------|------------|
| ITP vector reduction | `adjusted_pvalues` is a numpy array in raw dict; existing inference builder casts to float for scalar paths; new branch must guard against the array and keep it as numpy for scalar computations | Detect ITP shape by presence of `adjusted_pvalues` key (not by `p_value` absence alone); compute scalars with numpy, emit plain Python floats and ints |
| PACE-FPCA ncomp_truncated | `ncomp_requested` is a call-time parameter, not in the result dict; the advisor builder only sees the result dict | Pass via `build_diagnostics(result, "fpca", ncomp_requested=N)` kwargs; emit `ncomp_truncated = bool(diag["pace_ncomp"] < ncomp_requested)` when `ncomp_requested` is present |
| PACE-FPCA mean_band_width | `fitted_upper` and `fitted_lower` are 2D arrays shape (n, m); mean over all cells is a reasonable scalar but hides per-curve variation | Use `float(np.mean(np.asarray(fitted_upper) - np.asarray(fitted_lower)))` — document as "average pointwise band width across all observations" |
| compare_methods parameter parsing | Only needed for autotune, not comparison; do not confuse the two | In comparison, the LLM only narrates; it does NOT propose parameters; parameter parsing is autotune-only |
| autotune parameter parsing from LLM output | Free-text `Recommendation.action` parsing ("increase n_comp to 5") is fragile | Add `parameter_delta: dict[str, float | int] | None` field to `Recommendation` Pydantic model; LLM emits structured dict, not free text |
| MCP autotune LLM-free boundary | Natural implementation puts `advise()` inside `fdars_autotune` MCP tool — violates LLM-free-compute contract | Do NOT put `advise()` inside a MCP tool; document the agentic pattern: LLM client orchestrates existing tools per step |
| Pipeline report LLM context size | Full pipeline (6 stages x 15+ diagnostics) = 90+ key-value pairs; approaches context limits for smaller models | Flatten with stage prefixes (`represent_n_points`, `fpca_cumulative_variance_explained`) so LLM sees a flat dict; test with smallest supported model |
| `_DIAGNOSTICS_METHODS` guard sync | New advisor entry points (compare_methods, report_pipeline, autotune) must stay in sync with MCP server guard | Follow the atomic-commit pattern from v4.0 Phase 28 / v5.0 Phase 34: advisor code + MCP guard update in one commit |

---

## Sources

- Existing codebase: `/python/fdars/advisor/`, `/src/inference_mod.rs`, `/src/pace_fpca_mod.rs`, `/tests/test_pace_fpca.py`
- PROJECT.md — v6.0 Phase 38/39/40 deferral context and binding output shapes
- [Pini & Vantini (2016) ITP — Biometrics abstract](https://onlinelibrary.wiley.com/doi/abs/10.1111/biom.12476)
- [fdapace FPCA documentation — BLUP scores, xiVar, sigma2](https://rdrr.io/cran/fdapace/man/FPCA.html)
- [IWT fdatest R package — interval-wise testing reference](https://cran.r-project.org/web/packages/fdatest/fdatest.pdf)
- [Galaxy IWTomics tutorial — localisation vs detection](https://training.galaxyproject.org/archive/2022-04-01/topics/statistics/tutorials/iwtomics/tutorial.html)
- [Milvus AutoML stopping criteria](https://milvus.io/ai-quick-reference/how-does-automl-determine-stopping-criteria-for-training)
- [Ray Tune key concepts — HPO stopping patterns](https://docs.ray.io/en/latest/tune/key-concepts.html)
- [AutoML benchmark with early stopping (2025)](https://arxiv.org/abs/2504.01222)
- [Medium: The Agent Loop Problem — agentic stopping](https://medium.com/@Modexa/the-agent-loop-problem-when-smart-wont-stop-ccbf8489180f)

---

*Feature research for: fdars AI advisor — v8.0 new capabilities*
*Researched: 2026-08-23*
