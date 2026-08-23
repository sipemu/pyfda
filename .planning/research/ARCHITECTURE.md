# Architecture Research

**Domain:** fdars AI advisor — new capabilities integration (v8.0)
**Researched:** 2026-08-23
**Confidence:** HIGH — based on direct source reading of all advisor/MCP modules

---

## Existing System: What Is Already Shipped

The shipped advisor surface has five discrete layers. All four new capabilities
integrate into this existing structure; nothing is replaced.

```
┌──────────────────────────────────────────────────────────────────────────┐
│  User-facing entry points                                                 │
│  Python API:  build_diagnostics() / advise() / describe_cluster_differences()│
│  MCP tools:   fdars_build_diagnostics / fdars_run_method / fdars_compare_run │
│  Agent Skill: .claude/skills/fdars-advisor/ (SKILL.md)                   │
└──────────────────────────────────────────────────────────────────────────┘
              │ calls                │ calls
              ▼                      ▼
┌──────────────────┐    ┌────────────────────────────────────────────────┐
│  advisor/        │    │  mcp/                                          │
│  __init__.py     │    │  server.py   (MCPServer + 3 @mcp.tool handlers)│
│  build_diagnostics│    │  _runner.py  (run_method dispatch, 6 methods) │
│  advise()        │    │  _compare.py (compare_run, before/after delta) │
│  describe_*()    │    │  _registry.py (HandleRegistry singleton)       │
└────────┬─────────┘    └────────────────────────────────────────────────┘
         │ dispatches to
         ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  advisor/aspects/    (one file per aspect — 14 aspects today)            │
│  alignment.py  fpca.py  basis.py  smoothing.py  clustering.py            │
│  depth.py  outliers.py  classification.py  represent.py                  │
│  regression.py  regression_cv.py  spm.py  scoring.py  inference.py       │
│  _utils.py  (shared helpers: _eigenvalues_to_variance_cumulative)        │
└──────────────────────────────────────────────────────────────────────────┘
         │ LLM call via
         ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  advisor/providers/   (Provider protocol + 4 adapters)                   │
│  _protocol.py         (Provider ABC: complete_structured, name, model,   │
│                        supports_native_structured_output)                 │
│  _factory.py          (resolve_provider — picks adapter by name/instance)│
│  anthropic.py  openai.py  gemini.py  ollama.py                           │
│  _validate.py         (ValidateAndRetry wrapper + _check_grounding)      │
└──────────────────────────────────────────────────────────────────────────┘
         │ formats prompt via
         ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  advisor/_prompts.py  (GROUNDING_INVARIANT + _ASPECT_PRIMERS dict        │
│                        + _system_prompt() builder)                        │
│  advisor/_schema.py   (Advice + Recommendation Pydantic models)          │
└──────────────────────────────────────────────────────────────────────────┘
```

### Guard-sync invariant (T-22-05 / T-22-07)

Two frozensets in `mcp/server.py` must always mirror the advisor's `_supported`
set in `advisor/__init__.py:build_diagnostics`:

- `_RUNNABLE_METHODS` — aspects that `fdars_run_method` / `fdars_compare_run`
  can re-run (currently 6: alignment/fpca/basis/smoothing/clustering/depth)
- `_DIAGNOSTICS_METHODS` — every aspect that `fdars_build_diagnostics` accepts
  (currently 14: the 6 runnable + 8 diagnostics-only)

Every time `build_diagnostics` grows a new aspect, `_DIAGNOSTICS_METHODS` must
be updated in the same commit. This is the atomic guard-sync rule followed
verbatim in v4.0 Phase 28, v5.0 Phase 34, v6.0 Phase 40.

---

## New Capability 1: Deferred Aspects (FOUNDATIONAL)

### What is deferred

Three aspects left undone at v6.0 Phase 40:
1. **PACE-FPCA** — `fpca.py` already carries `has_pace_fpca` detection and a
   partial branch that reads `eigenvalues`/`ncomp`/`sigma2` from the raw dict.
   The `_ASPECT_PRIMERS["fpca"]` entry contains no PACE-specific language yet.
2. **Elastic-multinomial** — `classification.py` already has `has_elastic_multinomial`
   detection and reads `train_accuracy`/`train_error_rate`/`n_classes`. The
   `_ASPECT_PRIMERS["classification"]` entry carries elastic_multinomial primer text.
   The advisor already handles this one at the diagnostics level; the gap is whether
   the primer text is complete enough and whether test coverage exists.
3. **ITP interval inference** — `inference.py` handles `TestResult` scalars
   (`statistic`, `p_value`, `n_perm`). ITP functions (`itp_one_pop`, `itp_two_pop`,
   `itp_flm`) return vector-valued p-curves (`p_values: array(m,)`), not a single
   scalar `p_value`. The current builder does not handle the ITP result shape.

### Integration points: deferred aspects

**`advisor/aspects/fpca.py`** — EXTEND the `has_pace_fpca` branch:
- Add `pace_blup_scores_n_obs`, `pace_blup_scores_ncomp` (from `scores` shape if
  present in the pace_fpca result)
- Add `pace_prediction_variance_mean` if `prediction_variance` is in raw
- Keep all new diagnostics as native floats/ints — no numpy scalars

**`advisor/_prompts.py` — `_ASPECT_PRIMERS`** — EXTEND `"fpca"` entry to cover
PACE-specific diagnostic keys (sigma2, pace_sigma2, pace_ncomp,
pace_variance_explained_first). The existing `"classification"` entry already
has elastic_multinomial text; verify completeness, add if needed.

**`advisor/aspects/inference.py`** — ADD an ITP branch:
- Trigger: `"p_values"` key in raw (array-valued p-curve) — unique to ITP results
- Grounded-scalar reduction: compute `min_p_value`, `max_p_value`,
  `significant_points_frac` (fraction of grid points where p_value < 0.05),
  `n_significant_points` (integer count), `interval_length_frac` (fraction of
  domain where significant). All derived from fdars-computed array; no LLM in
  the reduction path.
- Add `itp_result_present: bool` flag to distinguish from standard TestResult path

**`advisor/_prompts.py` — `_ASPECT_PRIMERS`** — EXTEND `"inference"` entry with
an ITP-specific clause describing the grounded-scalar reduction fields.

**`mcp/server.py` — `_DIAGNOSTICS_METHODS`** — No change needed: `"inference"`
and `"fpca"` and `"classification"` are already in the frozenset. The deferred
aspects land in existing aspect slots; the guard-sync is a no-op for this
feature (exactly as Phase 40 noted for the ITP deferral).

**`advisor/__init__.py` — `build_diagnostics._supported`** — No change needed
for same reason (same existing method keys handle the extended builders).

**Tests** — Add offline unit tests for each new diagnostic field in each
extended builder. All offline (no LLM). Pattern: existing `tests/test_advisor_*`
or equivalent in `tests/`.

### Data flow: deferred aspects

```
caller: build_diagnostics(pace_fpca_result, "fpca")
  → advisor/__init__.py: dispatches to fpca.py (unchanged routing)
  → fpca.py: detects "eigenvalues" in raw → has_pace_fpca=True
             computes pace_sigma2, pace_ncomp, pace_blup_scores_n_obs,
             pace_prediction_variance_mean (ALL native floats/ints)
  → returns plain-Python diagnostics dict

caller: advise(diag, task="parameter", aspect="fpca")
  → _prompts.py: _system_prompt() fetches _ASPECT_PRIMERS["fpca"]
                 (now includes PACE language)
  → provider: LLM interprets, cites grounded PACE scalar values
  → _validate.py: _check_grounding verifies cited values in diag dict
```

```
caller: build_diagnostics(itp_result, "inference")
  → advisor/__init__.py: dispatches to inference.py (unchanged routing)
  → inference.py: detects "p_values" array → ITP branch
                  computes min_p_value, significant_points_frac, etc.
                  (NO numpy scalars; all plain float/int)
  → returns plain-Python diagnostics dict
```

---

## New Capability 2: Comparative Method-Selection

### Design decision: new entry point over N build_diagnostics calls

Comparative selection is NOT a new task family passed to `advise()` with a
single diagnostics dict. The LLM cannot compare methods it has not seen
diagnostics for. The pattern is:

1. Run `build_diagnostics` once per candidate method/config — deterministic,
   offline, fdars-computed.
2. Assemble a comparison dict keyed by method name, each value a diagnostics
   dict.
3. Call a single `advise()` (or new `rank_methods()` entry point) with a new
   task family `"comparison"` and a structured multi-diagnostics payload.

This preserves the grounding invariant: the LLM receives only fdars-computed
scalars for every candidate, ranks based only on those numbers, and must cite
specific values from specific candidate keys.

### Integration points: comparative method-selection

**`advisor/__init__.py`** — ADD new public function:

```python
def compare_methods(
    candidates: dict,   # {label: result_or_diagnostics}
    method: str,        # same fdars aspect for all candidates
    *,
    domain_context: str,
    model: str = "claude-opus-4-8",
    provider=None,
    run_llm: bool = True,
) -> "Advice | dict":
    ...
```

Internally: loop `build_diagnostics(v, method)` for each candidate, assemble
`comparison_diagnostics = {label: diag, ...}`, call `advise()` with
`task="comparison"` and the flattened multi-dict.

**`advisor/_prompts.py` — `_system_prompt()`** — ADD `"comparison"` to the
supported task set. The task clause instructs the LLM to rank candidates by
specific diagnostic values and cite the winning/losing values for each
criterion. The grounding invariant applies identically — every cited number must
appear in the comparison_diagnostics payload.

**`advisor/_schema.py`** — Evaluate whether `Advice` is sufficient or needs a
`ComparisonAdvice` subclass. Given the existing schema has `recommendations`
with a `kind` field, adding `kind="comparison"` is sufficient without a new
class. The `action` field carries the ranking decision; `evidence` cites the
delta between candidates.

**`advisor/_prompts.py` — `_ASPECT_PRIMERS`** — No new entries needed: the
existing per-aspect primer applies to each candidate's diagnostics already.

**`mcp/server.py`** — ADD new MCP tool:

```python
@mcp.tool()
def fdars_compare_methods(
    dataset_id: str,
    method: str,
    candidate_params: list[dict],  # each dict: param overrides per candidate
    domain_context: str = "",
) -> dict:
    ...
```

Internally: for each `candidate_params` entry, calls `run_method` + `build_diagnostics`,
assembles comparison dict, stores it in registry, returns a handle plus the
comparison diagnostics. Does NOT call the LLM — fully deterministic. The LLM
call is the Python-API responsibility only.

**Guard-sync**: `_DIAGNOSTICS_METHODS` needs no change; `fdars_compare_methods`
calls existing `run_method` paths. The new MCP tool validates `method` against
`_RUNNABLE_METHODS` (because it needs to run, not just accept a pre-computed
result). If caller passes pre-computed result dicts (not re-running), they use
`fdars_build_diagnostics` per candidate themselves — no new MCP needed.

**Data flow: comparative method-selection**

```
Python API path:
  compare_methods({"k=3": res_a, "k=4": res_b}, method="clustering", ...)
    → build_diagnostics(res_a, "clustering") → diag_a
    → build_diagnostics(res_b, "clustering") → diag_b
    → comparison_diagnostics = {"k=3": diag_a, "k=4": diag_b}
    → advise(comparison_diagnostics, task="comparison", ...)
      → _system_prompt("comparison", aspect="clustering")
      → provider: LLM ranks, cites "k=3 silhouette=0.78 vs k=4 silhouette=0.61"
      → _check_grounding verifies 0.78 and 0.61 exist in comparison_diagnostics

MCP agentic path:
  fdars_compare_methods(ds_id, "clustering", [{"k": 3}, {"k": 4}])
    → run_method(ds_id, "clustering", k=3) → store result_a
    → run_method(ds_id, "clustering", k=4) → store result_b
    → build_diagnostics(result_a, "clustering") → diag_a
    → build_diagnostics(result_b, "clustering") → diag_b
    → return {comparison diagnostics} (no LLM call in MCP layer)
```

---

## New Capability 3: Pipeline Diagnostic Report

### Design decision: new aggregation entry point

A pipeline report aggregates diagnostics across multiple DIFFERENT aspects
(represent → smooth → cluster/regress → monitor) rather than comparing multiple
configs of the same aspect. It is a new concept:

- Multiple `build_diagnostics` calls, each with a different method
- A `PipelineReport` container that holds the ordered stage list
- A single `advise()` call with the full multi-stage payload and task `"pipeline"`

### Integration points: pipeline diagnostic report

**`advisor/__init__.py`** — ADD new public function:

```python
def build_pipeline_report(
    stages: list[tuple[str, object]],   # [(method_name, result), ...]
    *,
    argvals=None,
    **per_stage_kwargs: dict,
) -> dict:
    """Offline, deterministic multi-stage diagnostics aggregation."""
    ...
```

Returns a plain-Python dict:
```python
{
    "method": "pipeline",
    "stages": [
        {"stage": 0, "method": "represent", "diagnostics": {...}},
        {"stage": 1, "method": "smoothing", "diagnostics": {...}},
        {"stage": 2, "method": "clustering", "diagnostics": {...}},
    ],
    "n_stages": 3,
}
```

All values remain fdars-computed scalars within each stage's diagnostics dict.

ADD new public function:

```python
def pipeline_report(
    stages: list[tuple[str, object]],
    *,
    domain_context: str,
    model: str = "claude-opus-4-8",
    provider=None,
    run_llm: bool = True,
) -> "Advice | dict":
    ...
```

Same `run_llm=False` escape hatch as `describe_cluster_differences`.

**`advisor/_prompts.py` — `_system_prompt()`** — ADD `"pipeline"` to the
supported task set. Task clause instructs the LLM to: narrate each stage's
findings in sequence, flag cross-stage issues (e.g. high imputation fraction in
represent stage affecting downstream clustering), and cite specific diagnostic
values by stage name. Grounding invariant unchanged — LLM must cite values
present in the pipeline_report dict.

**`advisor/_schema.py`** — Existing `Advice` schema is sufficient. The
`interpretation` field carries the cross-stage narrative; `recommendations` list
carries per-stage or cross-stage actions.

**`mcp/server.py`** — ADD new MCP tool:

```python
@mcp.tool()
def fdars_build_pipeline_report(
    dataset_id: str,
    stage_methods: list[str],    # ordered method names
    stage_result_ids: list[str], # handles per stage from prior fdars_run_method calls
) -> dict:
    ...
```

Internally: loops `build_diagnostics` per stage using stored result handles,
assembles pipeline report dict, stores it in registry, returns it.
Fully deterministic — no LLM call. Returns the report dict (not a handle, since
the dict is JSON-serialisable).

**Guard-sync**: `_DIAGNOSTICS_METHODS` needs no change — each stage uses an
existing diagnostics method. No new entries to `_DIAGNOSTICS_METHODS`.

**`mcp/server.py` — `_DIAGNOSTICS_METHODS`** — Confirm `fdars_build_pipeline_report`
validates each stage method against `_DIAGNOSTICS_METHODS` before processing.
This is the correct guard for the pipeline tool (it accepts diagnostics-only
methods, not just runnable ones).

**Data flow: pipeline report**

```
Python API path:
  pipeline_report([("represent", fd), ("smoothing", smooth_result), ...], ...)
    → build_pipeline_report([...]) → pipeline_dict
      → build_diagnostics(fd, "represent") → diag_0
      → build_diagnostics(smooth_result, "smoothing") → diag_1
      → ... all offline, fdars-computed
    → advise(pipeline_dict, task="pipeline", ...)
      → _system_prompt("pipeline")
      → provider: LLM narrates stages, cites "stage 0 imputed_fraction=0.18,
                  stage 1 optimal_edf=6.3"
      → _check_grounding verifies 0.18 and 6.3 in pipeline_dict["stages"][*]

MCP agentic path:
  fdars_build_pipeline_report(ds_id, ["represent","smoothing"], [r_id_0, r_id_1])
    → build_diagnostics(result_0, "represent") → diag_0
    → build_diagnostics(result_1, "smoothing") → diag_1
    → return pipeline_dict (no LLM call)
```

---

## New Capability 4: Closed-Loop Auto-Tuning (Capstone)

### Design principle: the loop core must be LLM-free in the compute path

The LLM is called ONCE per iteration for proposal only. fdars runs every
computation. The loop orchestrator checks convergence and budget deterministically.

```
┌─────────────────────────────────────────────────────────────────┐
│                  AUTO-TUNING LOOP CORE (Python)                  │
│                                                                   │
│  iteration 0:                                                     │
│    fdars_run_method(params_0) ──→ result_0                        │
│    build_diagnostics(result_0) ──→ diag_0                         │
│    ┌────────────────────────────────────────────────────────┐    │
│    │ LLM CALL (advise proposal only)                        │    │
│    │  advise(diag_0, task="parameter") → Advice             │    │
│    │  extract proposed param from Advice.recommendations[0] │    │
│    └────────────────────────────────────────────────────────┘    │
│    parse proposal → params_1 (deterministic extraction)           │
│    compare_run(before=result_0, params_after=params_1)            │
│       → diag_1 + delta (ALL fdars-computed)                       │
│    target_check: delta[target_key] improves? budget exhausted?    │
│                  (DETERMINISTIC — no LLM)                         │
│                                                                   │
│  iteration 1 (if not converged):                                  │
│    advise(diag_1, task="parameter") → Advice (proposal only)      │
│    ... repeat ...                                                  │
│                                                                   │
│  exit: target met OR step_budget exhausted OR stagnation detected │
│  return: TuningTrace (all iterations, final params, final diag)   │
└─────────────────────────────────────────────────────────────────┘
```

### Architectural guarantee: LLM-free compute path

The loop orchestrator never passes LLM text into any fdars call. The only
LLM interaction is `advise()` returning an `Advice` object; the orchestrator
then PARSES the `action` field (a string like "increase n_basis to 20") to
extract a scalar parameter. The parse is deterministic: a simple regex or
structured extraction on the `action` string. If parsing fails, the loop exits
with an explicit error — it never retries by asking the LLM again (that would
put the LLM in the numeric path).

A cleaner version (preferred): add a new task `"parameter_proposal"` that
returns a machine-parseable `Advice` where `action` is constrained to a
structured format (e.g. "param=n_basis value=20"). The `_schema.py` can stay
the same — the task clause in the system prompt instructs the format.

### Integration points: auto-tuning

**New file: `advisor/_tuning.py`** — The shared loop core, used by both the
Python API entry point and the MCP tool. Key function:

```python
def _run_tuning_loop(
    dataset_id: str,          # or (data, argvals) for Python-API path
    method: str,
    initial_params: dict,
    target_key: str,          # diagnostic key to optimize
    target_direction: str,    # "maximize" or "minimize"
    step_budget: int,
    *,
    domain_context: str,
    model: str = "claude-opus-4-8",
    provider=None,
    allow_stagnation: bool = True,
    stagnation_window: int = 2,
) -> "TuningTrace":
    ...
```

Uses `run_method` + `build_diagnostics` + `advise` (proposal only) in sequence.
All arithmetic (delta, target check, stagnation) is pure Python/NumPy — no LLM.

**`advisor/__init__.py`** — ADD public Python API entry point:

```python
def auto_tune(
    result,
    method: str,
    *,
    initial_params: dict,
    target_key: str,
    target_direction: str = "minimize",
    step_budget: int = 5,
    domain_context: str = "",
    model: str = "claude-opus-4-8",
    provider=None,
    argvals=None,
) -> "TuningTrace":
    ...
```

Returns a `TuningTrace` dataclass/Pydantic model containing:
- `method: str`
- `iterations: list[TuningStep]` — each step: `params`, `diagnostics`, `delta`, `proposal`
- `final_params: dict`
- `final_diagnostics: dict`
- `converged: bool`
- `n_steps: int`

**`advisor/_schema.py`** — ADD `TuningStep` and `TuningTrace` Pydantic models
(or plain dataclasses with the offline fallback pattern already used for `Advice`).

**`mcp/server.py`** — ADD new MCP tool:

```python
@mcp.tool()
def fdars_auto_tune(
    dataset_id: str,
    method: str,
    target_key: str,
    target_direction: str = "minimize",
    step_budget: int = 5,
    lambda_: float | None = None,
    n_basis: int | None = None,
    n_comp: int | None = None,
    k: int | None = None,
    seed: int | None = None,
) -> dict:
    ...
```

Flat scalar params (same pattern as `fdars_compare_run` — no nested dicts in
MCP schema, Pitfall 6 from existing code). Does NOT accept a provider or model
because the MCP layer is LLM-free. The MCP tool runs the fdars compute loop
only — the LLM proposal path is NOT available from MCP. This is the correct
separation: the MCP tool handles deterministic auto-tuning (propose-via-heuristic
or simply re-run with grid search over the param space within budget), while the
Python API tool uses the LLM for the proposal.

Alternative MCP design (preferred for v8.0): `fdars_auto_tune` over MCP uses a
**heuristic proposal** (e.g. exponential grid search on the param range) rather
than calling an LLM, keeping the MCP layer fully LLM-free. The Python API
`auto_tune()` uses the LLM for intelligent proposal. Both share the same loop
core from `_tuning.py` via a `proposal_fn` argument:

```python
def _run_tuning_loop(
    ...,
    proposal_fn,  # callable(diagnostics, method, params) -> dict (next params)
) -> TuningTrace:
    ...
```

Python API path passes `proposal_fn = lambda d, m, p: _llm_propose(d, m, p, ...)`.
MCP path passes `proposal_fn = _heuristic_propose` (no LLM).

**Guard-sync**: `fdars_auto_tune` validates `method` against `_RUNNABLE_METHODS`
(it re-runs fdars). No new entries to `_DIAGNOSTICS_METHODS` or `_RUNNABLE_METHODS`.

**`mcp/_compare.py` — `_ALLOWED_PARAMS`** — No change; `fdars_auto_tune` builds
`params_after` internally from flat scalar args using the same allowlist pattern.
The loop core in `_tuning.py` calls `run_method` and `compare_run` directly.

**Data flow: auto-tuning**

```
Python API path (LLM-assisted proposal):
  auto_tune(result, "smoothing", target_key="optimal_edf",
            target_direction="minimize", step_budget=3)
    → _run_tuning_loop(proposal_fn=_llm_propose, ...)
      iteration 0:
        run_method(ds_id, "smoothing", n_basis=15) → result_0
        build_diagnostics(result_0, "smoothing") → diag_0
        _llm_propose(diag_0, "smoothing", {n_basis:15})
          → advise(diag_0, task="parameter_proposal")
          → parse action → {n_basis: 20}
        compare_run(ds_id, "smoothing", r_0, {n_basis: 20}) → delta
        target_check: optimal_edf delta < 0? (minimize) → continue
      iteration 1: ...
    → TuningTrace(iterations=[...], final_params={n_basis: 20}, converged=True)

MCP path (heuristic proposal, fully LLM-free):
  fdars_auto_tune(ds_id, "smoothing", target_key="optimal_edf",
                  target_direction="minimize", step_budget=3, n_basis=15)
    → _run_tuning_loop(proposal_fn=_heuristic_propose, ...)
      → same compute loop, heuristic picks next param (e.g. bisection on n_basis)
      → fully deterministic
    → return TuningTrace as JSON-serialisable dict
```

---

## Component Summary: New vs Modified

| Component | File | Status | Notes |
|-----------|------|--------|-------|
| PACE-FPCA diagnostics | `advisor/aspects/fpca.py` | **EXTEND** | Add pace_blup fields to existing has_pace_fpca branch |
| ITP inference diagnostics | `advisor/aspects/inference.py` | **EXTEND** | Add ITP vector→scalar reduction branch |
| Elastic-multinomial review | `advisor/aspects/classification.py` | **VERIFY** | Branch already exists; verify completeness + test coverage |
| PACE-FPCA aspect primer | `advisor/_prompts.py` | **EXTEND** | Extend `_ASPECT_PRIMERS["fpca"]` with PACE language |
| ITP inference primer | `advisor/_prompts.py` | **EXTEND** | Extend `_ASPECT_PRIMERS["inference"]` with ITP scalar reduction language |
| Comparison task | `advisor/_prompts.py` | **EXTEND** | Add `"comparison"` to `_system_prompt()` supported tasks |
| Pipeline task | `advisor/_prompts.py` | **EXTEND** | Add `"pipeline"` to `_system_prompt()` supported tasks |
| Proposal task | `advisor/_prompts.py` | **EXTEND** | Add `"parameter_proposal"` to `_system_prompt()` supported tasks |
| TuningStep + TuningTrace | `advisor/_schema.py` | **EXTEND** | Add new dataclass/Pydantic models |
| Loop core | `advisor/_tuning.py` | **NEW** | Shared by Python API + MCP; accepts proposal_fn |
| compare_methods() | `advisor/__init__.py` | **EXTEND** | New public function |
| build_pipeline_report() | `advisor/__init__.py` | **EXTEND** | New public function |
| pipeline_report() | `advisor/__init__.py` | **EXTEND** | New public function |
| auto_tune() | `advisor/__init__.py` | **EXTEND** | New public function |
| `__all__` export list | `advisor/__init__.py` | **EXTEND** | Add new public symbols |
| fdars_compare_methods | `mcp/server.py` | **NEW TOOL** | Validates against `_RUNNABLE_METHODS` |
| fdars_build_pipeline_report | `mcp/server.py` | **NEW TOOL** | Validates stages against `_DIAGNOSTICS_METHODS` |
| fdars_auto_tune | `mcp/server.py` | **NEW TOOL** | Validates against `_RUNNABLE_METHODS`; heuristic proposal only |
| `_DIAGNOSTICS_METHODS` | `mcp/server.py` | **NO CHANGE** — deferred aspects use existing slots | Verify stays in sync |
| `_RUNNABLE_METHODS` | `mcp/server.py` | **NO CHANGE** | No new runnable methods |
| Advisor Agent Skill | `.claude/skills/fdars-advisor/SKILL.md` | **EXTEND** | Document new entry points in walkthrough |

---

## Guard-Sync Atomicity Rules (per-capability)

| Capability | `build_diagnostics._supported` | `_DIAGNOSTICS_METHODS` | `_RUNNABLE_METHODS` | Same-commit rule |
|---|---|---|---|---|
| Deferred aspects (PACE, ITP, multinomial) | No change | No change | No change | Aspect file + _prompts.py + tests in one commit |
| Comparative method-selection | No change | No change | No change | compare_methods + _prompts.py("comparison") + tests in one commit |
| Pipeline report | No change | No change | No change | build_pipeline_report + pipeline_report + fdars_build_pipeline_report + _prompts.py("pipeline") + tests in one commit |
| Auto-tuning | No change | No change | No change | _tuning.py + auto_tune + fdars_auto_tune + _prompts.py("parameter_proposal") + _schema.py(TuningTrace) + tests in one commit |

**Key insight**: none of the four new capabilities add a new `build_diagnostics`
method slot. They operate above the diagnostics layer (comparison, pipeline,
tuning) or extend existing aspect builders (deferred aspects). This means the
`_DIAGNOSTICS_METHODS` guard-sync commits are no-ops for v8.0. The atomic rule
still applies within each capability: all files touched by that capability must
land together.

---

## Recommended Build Order

### Phase 1 (Foundational): Deferred Aspects

**Rationale**: The deferred aspects extend existing code paths with no new
abstractions. They are the lowest-risk change, exercise the existing
`build_diagnostics` + `advise` + `_check_grounding` pipeline, and unblock
accurate `_ASPECT_PRIMERS` for all subsequent LLM calls (the comparison and
pipeline features benefit from complete primers).

Files touched: `aspects/fpca.py`, `aspects/inference.py`,
`aspects/classification.py` (verify), `_prompts.py` (extend two primer entries),
tests.

### Phase 2: Comparative Method-Selection

**Rationale**: Builds on the existing `build_diagnostics` + `advise` call
pattern. Adds one new task family ("comparison") and one new Python entry point.
The MCP tool (`fdars_compare_methods`) uses only existing `run_method` and
`build_diagnostics` primitives. No new schema types needed.

Files touched: `advisor/__init__.py` (compare_methods), `_prompts.py`
(add "comparison" task), `mcp/server.py` (new tool), tests.

### Phase 3: Pipeline Diagnostic Report

**Rationale**: Introduces the `build_pipeline_report` aggregation pattern and
the "pipeline" task family. More surface area than Phase 2 (MCP tool needs
multi-handle input), but no new loop logic or schema. The multi-stage
aggregation is a new concept and needs careful test coverage before the
capstone builds on it.

Files touched: `advisor/__init__.py` (build_pipeline_report, pipeline_report),
`_prompts.py` (add "pipeline" task), `mcp/server.py` (new tool), tests.

### Phase 4 (Capstone): Closed-Loop Auto-Tuning

**Rationale**: The most complex capability — introduces `_tuning.py`, new schema
types, a new task family ("parameter_proposal"), and a novel MCP tool. Depends
on Phase 1 (accurate diagnostics), Phase 2 (proven multi-run pattern), and the
existing `compare_run` infrastructure. Building last means the loop core can
rely on a thoroughly tested diagnostics/comparison layer.

Files touched: `advisor/_tuning.py` (NEW), `advisor/_schema.py` (TuningStep,
TuningTrace), `advisor/__init__.py` (auto_tune), `_prompts.py` (add
"parameter_proposal" task), `mcp/server.py` (fdars_auto_tune), tests.

---

## Anti-Patterns to Avoid

### Anti-Pattern 1: LLM text feeding back into fdars params

**What:** Passing the raw `action` string from an `Advice` recommendation
directly as a function argument.
**Why bad:** If the LLM fabricates a param value, fdars runs with it. The
grounding invariant covers evidence citations, not action text.
**Instead:** Parse `action` with a strict regex that extracts only a numeric
value and validates it is within a pre-declared param range before passing to
`run_method`. Reject unparseable proposals with an error — do not retry by
asking the LLM again.

### Anti-Pattern 2: New aspects without atomic guard-sync

**What:** Adding a new aspect to `build_diagnostics._supported` in one commit
and updating `_DIAGNOSTICS_METHODS` in a later commit.
**Why bad:** In the window between commits, `fdars_build_diagnostics` will raise
`ValueError` for the new method even though the advisor core supports it.
**Instead:** Use a single atomic commit as done in v4.0 Phase 28, v5.0 Phase 34,
v6.0 Phase 40.

### Anti-Pattern 3: LLM call inside the MCP auto-tune tool

**What:** Adding a provider/model argument to `fdars_auto_tune` and having the
MCP tool call `advise()`.
**Why bad:** The MCP boundary must be provably LLM-free. Allowing an LLM call
inside an MCP tool breaks the documented MCP-LLM-free invariant and introduces
an API-key dependency in the compute path.
**Instead:** MCP auto-tune uses a heuristic proposal function. The LLM-assisted
proposal lives exclusively in the Python API `auto_tune()`.

### Anti-Pattern 4: Arrays crossing MCP boundary in pipeline or comparison tools

**What:** Returning per-stage diagnostics arrays (e.g. cluster centers, FPCA
rotation matrices) in the `fdars_build_pipeline_report` or
`fdars_compare_methods` return value.
**Why bad:** Violates the by-reference handle invariant; large JSON payloads
across the MCP stdio boundary.
**Instead:** Return only scalar summaries from each stage's diagnostics (the
`build_diagnostics` output is already scalar-only — lists are permitted but
large arrays are reduced to summary scalars by each aspect builder). The
pipeline report tool returns the aggregated diagnostics dict, which is
JSON-serialisable by construction.

### Anti-Pattern 5: Duplicating comparison or pipeline logic in MCP tools

**What:** Re-implementing the loop or aggregation inside `fdars_compare_methods`
or `fdars_build_pipeline_report` instead of calling the Python API functions.
**Why bad:** Two implementations diverge. Bugs in one don't get fixed in the other.
**Instead:** MCP tools call the same Python API functions used by direct callers.
`fdars_compare_methods` calls `compare_methods()` (or its internal helpers).
`fdars_build_pipeline_report` calls `build_pipeline_report()`. Single implementation.

---

## Integration Boundaries Summary

| Boundary | Communication | Grounding invariant | LLM-free invariant |
|---|---|---|---|
| Python API → advisor core | Direct function call | Enforced by `_check_grounding` | n/a (LLM allowed here) |
| Python API → MCP tools | Separate entry points sharing `_tuning.py` | Enforced in Python API path | MCP path uses heuristic proposal |
| MCP tools → fdars | Via `run_method` / `build_diagnostics` (unchanged) | fdars computes; MCP never fabricates | MCP layer has zero LLM calls |
| LLM → param extraction | Parse `Advice.recommendations[0].action` string | Grounding guard on evidence; action parsed deterministically | LLM text never directly calls fdars |
| `_check_grounding` | Called in `advise()` after every LLM response | Rejects cited numbers absent from diagnostics | n/a |

---

## Sources

- Direct source reading: `python/fdars/advisor/__init__.py`, `_prompts.py`,
  `_schema.py`, `aspects/*.py`, `providers/_validate.py`
- Direct source reading: `python/fdars/mcp/server.py`, `_runner.py`,
  `_compare.py`, `_registry.py`
- `.planning/PROJECT.md` (v8.0 milestone context, shipped milestone history,
  guard-sync precedents at Phase 28/34/40)
- `.planning/codebase/ARCHITECTURE.md` (system overview)

---

*Architecture research for: fdars v8.0 Advisor — New Capabilities*
*Researched: 2026-08-23*
*Confidence: HIGH — grounded in direct source reading of all advisor and MCP modules*
