# Pitfalls Research

**Domain:** Agentic auto-tuning advisor + comparative/aggregated grounded advice on top of a
grounded, provider-agnostic, LLM-free-compute FDA advisor (fdars v8.0)
**Researched:** 2026-08-23
**Confidence:** HIGH — all pitfalls derived directly from the shipped codebase
(`python/fdars/advisor/`, `python/fdars/mcp/`, `src/inference_mod.rs`) and from the
documented failure history in `.planning/` and `MEMORY.md`.

---

## Critical Pitfalls

### Pitfall 1: Auto-Tuning Loop Non-Termination — Budget Enforcement at the Wrong Layer

**What goes wrong:**
The loop runs `build_diagnostics` → `advise` → `apply_change` → `re-run` repeatedly. If the
budget cap is checked only inside `advise()` (the LLM call), a slow-converging target
diagnostic can exhaust the LLM token budget or wall-clock time before the Python-layer step
counter fires. Conversely, if the budget is checked only at the Python layer but not also at
the MCP tool level, an agentic LLM driving `fdars_compare_run` in a tool-call loop has no
hard stop and can issue unbounded calls.

**Why it happens:**
The existing `fdars_compare_run` tool is designed for one-shot before/after comparisons, not
multi-step loops. There is no step counter in the current MCP layer. Developers add a Python
`max_steps` guard but forget to surface it as a MCP tool return field, so the orchestrating
agent cannot observe that the budget is near and keeps issuing calls.

**How to avoid:**
- Define `max_steps: int` as a mandatory parameter of the auto-tune loop (both Python API and
  MCP tool). Enforce it in the Python orchestrator BEFORE each LLM call, not inside `advise`.
- Return `{"steps_used": int, "budget_remaining": int, "stopped_by": "budget"|"target"|"no_improvement"}` in every loop response, even partial ones. The MCP tool must include
  this in its return dict so the LLM agent can observe loop termination state.
- The LLM is shown the budget-remaining value in its context at each step, making it
  observable. The Python orchestrator is the authority on whether to continue; the LLM only
  proposes.
- Never allow the LLM to extend its own budget (no "I need more steps" instruction following).

**Warning signs:**
- Auto-tune Python API has `max_steps` only as a keyword-only default, not a required param.
- MCP tool return dict omits `steps_used` or `stopped_by`.
- Unit tests for the loop use `max_steps=100` (permissive) rather than `max_steps=2` (tight).

**Phase to address:**
Closed-loop auto-tuning implementation phase (capstone). Define the termination contract
in the spec/plan before any code is written.

---

### Pitfall 2: LLM Silently Re-Entering the Numeric Path Inside the Loop

**What goes wrong:**
The grounding invariant requires that fdars computes every number. In a multi-step loop, the
LLM proposes the NEXT parameter value (e.g. `n_basis=18`). If the system prompt or the loop
scaffolding asks the LLM to "estimate the expected new diagnostic value" or "predict the
improvement", the LLM is now fabricating a diagnostic, not proposing a parameter. This
fabricated number then gets cited in the next step's evidence and passes `_check_grounding`
because it looks like a parameter integer rather than a diagnostic scalar.

**Why it happens:**
Loop prompts are written to elicit forward-looking rationale ("what improvement do you expect?")
which is good for recommendations but dangerous for numeric prediction. The LLM conflates "I
expect X to improve" with "the new value will be Y". The existing `_check_grounding` guard
extracts numbers from evidence strings but does not distinguish between cited-diagnostic values
and predicted-future values.

**How to avoid:**
- The loop system prompt must be explicit: "Propose one parameter change. Do NOT predict the
  numeric outcome — you will observe the actual diagnostic in the next step." Structure the
  Advice schema so `expected_effect` is free-text qualitative ("should decrease", "should
  increase") and `evidence` cites only the CURRENT step's diagnostics, not a predicted future
  value.
- After each fdars re-run, the new diagnostics dict is the authoritative source. The LLM
  never computes a diagnostic value — it only reads the dict that the orchestrator supplies.
- In tests: assert that `advice.recommendations[*].expected_effect` contains no numeric
  literals that are absent from the current step's diagnostics dict.

**Warning signs:**
- Loop prompts contain phrases like "predict the new GCV value" or "estimate the improvement".
- `expected_effect` strings in loop advice cite specific numbers like "GCV will drop to 0.12".
- `_check_grounding` passes because the LLM-fabricated future value happens to round to a
  real diagnostic in the current dict.

**Phase to address:**
Closed-loop auto-tuning — specifically the system prompt design. Write a dedicated
`_loop_system_prompt()` distinct from the existing `_system_prompt()` to enforce this.

---

### Pitfall 3: Goodhart's Law — Optimising One Diagnostic Degrades Others

**What goes wrong:**
The loop targets a single scalar diagnostic (e.g. minimise `gcv_min` for smoothing or
maximise `accuracy` for classification). At each step, `advise` correctly proposes a change
that improves the target. After several iterations, the target improves but a structurally
important diagnostic degrades silently — e.g. `n_basis` is tuned so aggressively that
`edf` grows to near `n_obs` (overfitting the basis), or `lambda_` is driven so low that
`phase_leakage_indicator` spikes but the convergence target never checks it.

**Why it happens:**
`build_diagnostics` returns a rich dict but the loop only checks one scalar for its stopping
criterion. The LLM advisor does not see a "guard rails" set of secondary diagnostics to
respect, and the system prompt for the loop task does not explicitly forbid degrading them.

**How to avoid:**
- Define a `target_diagnostic: str` (primary) AND an optional `guard_diagnostics: dict[str, tuple[float, float]]` (secondary — name to acceptable range). The loop terminates or refuses the
  proposed step if any guard diagnostic moves outside its range.
- Surface both the target and all guard values in the per-step context that `advise` sees.
- The loop's stop-or-continue decision is made by the Python orchestrator (deterministic range
  check), not by the LLM.
- Default guard diagnostics per method: smoothing — `edf` <= 0.9 x n_obs; fpca — `n_components`
  <= n_obs // 2; clustering — `min_cluster_size` >= 2.

**Warning signs:**
- Loop spec defines only `target_diagnostic` with no guard concept.
- Test assertions only check that the target improved, not that guards held.
- After the loop, `edf` or `n_components` or `fold_error_std` is at a physically implausible
  extreme.

**Phase to address:**
Closed-loop auto-tuning — the loop contract design (spec phase) and the guard-check unit tests.

---

### Pitfall 4: Divergent / Oscillating Auto-Tuning Loop

**What goes wrong:**
The loop proposes `n_basis=20` (up from 15) at step 1. GCV improves. At step 2, `advise` sees
higher EDF and proposes `n_basis=12` (down). At step 3, GCV is worse again and it proposes
`n_basis=22`. The loop oscillates between overshooting and undershooting without converging.
This can also happen with `lambda_` in alignment/smoothing where the diagnostic surface is
nearly flat and small perturbations cause the advisor to flip direction repeatedly.

**Why it happens:**
The LLM's parameter proposal is based only on the current step's diagnostics, not the full
history of (parameter, diagnostic) pairs. Without seeing that `n_basis=20->12->22` is an
oscillation, it makes the same directional inference each time.

**How to avoid:**
- Pass the full loop history (all previous steps: parameter value and diagnostic value) in the
  per-step context so `advise` can observe the trajectory. Include a `history: list[dict]`
  in the user content, one entry per step.
- Add a convergence check in the Python orchestrator: if the last two proposed parameter values
  bracket the current value AND the diagnostic improvement is below a threshold (e.g. 0.1%),
  stop the loop with `stopped_by="converged"`.
- Keep the history compact — store only the target diagnostic and the changed parameter, not
  the full diagnostics dict, to avoid bloating the LLM context.

**Warning signs:**
- Loop implementation passes only the latest diagnostics to `advise`, not the history.
- Integration tests do not include an oscillation test case.
- No monotonicity check in the convergence criterion.

**Phase to address:**
Closed-loop auto-tuning — orchestrator design. Write an oscillation test with a mock advisor
that alternates direction.

---

### Pitfall 5: Non-Deterministic Loop — Untestable Offline

**What goes wrong:**
The auto-tuning loop calls `advise()` at each step, which calls the LLM. In CI without an API
key, the entire loop test is skipped. When the loop IS run manually, the LLM may propose
different parameter changes each run, making the loop non-reproducible for debugging. This
means bugs in the orchestrator (wrong termination, wrong guard check) only surface during
expensive real-LLM runs.

**Why it happens:**
The existing advisor test pattern (env-gated `FDARS_INTEGRATION=1` + `ANTHROPIC_API_KEY`) is
correct for single-shot `advise()` tests. But a multi-step loop has more orchestration
surface (step counter, history accumulation, guard checks, termination logic) than a single
call. If all of this is only testable with a live LLM, the orchestrator bugs go untested in CI.

**How to avoid:**
- Design the loop to accept an injectable `advisor_fn: Callable[[dict, ...], Advice]` parameter
  (default: `advise`). In tests, inject a deterministic mock advisor that always proposes
  `n_basis += 2` or returns a hardcoded `Advice`. This makes the orchestrator testable with
  `pytest -q` and no API key.
- Unit-test ALL of: step counter increment, history accumulation, guard-check firing, target
  improvement detection, budget exhaustion, oscillation detection — all using the mock advisor.
- Keep the live-LLM integration test to one end-to-end smoke test (env-gated) that exercises
  a real `advise()` call inside the loop.

**Warning signs:**
- Loop function signature has no `advisor_fn` injection point.
- The only loop tests are `skipif(not ANTHROPIC_API_KEY)`.
- Orchestrator logic (step counter, guard check) is inside `advise()` rather than outside it.

**Phase to address:**
Closed-loop auto-tuning — the loop must be designed for testability from day one. The injectable
advisor pattern should be in the plan before implementation starts.

---

### Pitfall 6: Comparing Incommensurable Diagnostics Across Method Changes

**What goes wrong:**
The auto-tuning loop compares diagnostics from run N (method: `basis`, `n_basis=15`) with run
N+1 (method: `smoothing`, `n_basis=20`). The `gcv_min` key exists in both result dicts but
means different things for the two methods (one is basis selection, the other is a GCV curve
minimum). The loop's before/after delta computation subtracts them and reports an apparent
improvement that is actually a comparison of different quantities.

This also applies to comparative method-selection: comparing FPCA's `explained_variance_ratio`
with PLS's regression CV error is comparing an unsupervised decomposition quality with a
supervised prediction quality — they are on incompatible scales.

**Why it happens:**
`fdars_compare_run` in the current MCP layer validates that the METHOD is the same across
before/after (it requires `method` to be unchanged). But the auto-tuning loop may propose a
method CHANGE, not just a parameter change. If the loop does not distinguish between
"tune this method" and "switch to a different method", it will try to compare incommensurable
diagnostic dicts.

**How to avoid:**
- The auto-tuning loop must enforce: within a single loop run, the method is FIXED. Parameter
  changes only. Method changes require a new comparative-selection call, not a loop iteration.
- For comparative method-selection: define a `MethodComparison` schema with
  `method_a`, `method_b`, `common_diagnostic`, `a_value`, `b_value`, `recommendation`.
  Never subtract diagnostics that are not semantically equivalent across methods.
- The comparison function must verify that both diagnostic dicts carry the same `method` field
  before computing any delta. If they differ, raise `ValueError` rather than silently
  subtracting incommensurable quantities.
- For the `comparative_select` entry point, use a purpose-built comparison diagnostic (e.g.
  a shared scoring metric from `fdars.scoring`) rather than per-method internal diagnostics.

**Warning signs:**
- Loop or comparison code uses `after[key] - before[key]` without first asserting
  `after["method"] == before["method"]`.
- Comparative selection advice cites FPCA `explained_variance_ratio` alongside PLS CV error
  in the same recommendation.

**Phase to address:**
Comparative method-selection (its own phase) and closed-loop auto-tuning. Both need explicit
incommensurability guards in their contracts.

---

### Pitfall 7: Grounding Violation in Aggregated Pipeline Reports — Wrong-Run Citation

**What goes wrong:**
The pipeline diagnostic report aggregates diagnostics across multiple stages:
`represent -> smooth -> cluster -> monitor`. Each stage has its own diagnostics dict. The
aggregated report is passed to `advise()` as a flat merged dict. The LLM cites a value
(e.g. `gcv_min=0.23`) in a recommendation about the smoothing stage. But `_check_grounding`
looks up `0.23` in the merged dict and finds it — even though it actually came from the
clustering stage's `mean_amplitude_separation=0.23`. The citation is technically grounded
(the value exists in the diagnostics) but its provenance is wrong.

**Why it happens:**
`_check_grounding` does a flat numeric-equality scan across all diagnostic values. It cannot
distinguish "value X came from stage A" from "value X appears in the merged dict because it
happened to equal a value from stage B". Merging dicts from multiple stages collapses
provenance.

**How to avoid:**
- Never pass a flat-merged multi-stage dict to `advise()`. Instead, structure the pipeline
  report as `{"stages": {"represent": {...}, "smooth": {...}, "cluster": {...}}}` and send
  each stage's diagnostics to `advise()` independently, producing per-stage advice objects.
- The pipeline report is then an aggregation of per-stage `Advice` objects, not a single
  `advise()` call on a merged dict.
- If a single unified narrative is needed, assemble it from the per-stage `Advice.interpretation`
  strings — which are themselves grounded — rather than by calling `advise()` on the merged dict.
- Alternative for a true "single call" design: namespace keys (`"smooth.gcv_min"`,
  `"cluster.mean_amplitude_separation"`) so the LLM can cite provenance, and update
  `_check_grounding` to strip the namespace prefix before numeric lookup.

**Warning signs:**
- Pipeline report code contains `merged = {**stage1_diag, **stage2_diag, **stage3_diag}` and
  then calls `advise(merged, ...)`.
- Two pipeline stages coincidentally share a numeric value that appears in both dicts.
- `_check_grounding` passes on a pipeline report that contains provenance-incorrect citations.

**Phase to address:**
Pipeline diagnostic report phase. Design the aggregation architecture (per-stage advice vs.
namespaced merged dict) before implementing.

---

### Pitfall 8: ITP Grounded-Scalar Reduction Loses Localisation — Misleading Summary

**What goes wrong:**
`itp_one_pop` / `itp_two_pop` / `itp_flm` return `{"adjusted_pvalues": ndarray(n_basis,),
"raw_pvalues": ndarray(n_basis,), "n_basis": int, "n_perm": int}`. The p-values are a
VECTOR — one per basis function. To ground the advisor, the vector must be reduced to scalars.
The obvious reduction is `min(adjusted_pvalues)` (the most significant interval). But
`min(adjusted_pvalues)` loses localisation: if 1 of 5 intervals is significant and the other 4
are not, reporting only the minimum creates a misleading impression that "the test is
significant" when it is significant only locally.

A second trap: using `mean(adjusted_pvalues)` as the grounded scalar. If 4/5 intervals are
p=0.80 and 1 interval is p=0.02, the mean (approx 0.66) gives a non-significant summary for a
locally significant result — the opposite of the min trap, equally misleading.

**Why it happens:**
The existing `_build_inference_diagnostics` was designed for scalar-valued `TestResult` dicts
(`statistic`, `p_value`, `n_perm`). When extending to ITP, developers reach for the same
grounded-scalar pattern and pick either `min` or `mean` without considering what the
interpretation means.

**How to avoid:**
Expose MULTIPLE grounded scalars from `ItpResult`, each with a clear semantic:
- `itp_n_significant_0.05` (int): number of basis intervals significant at 0.05 after
  adjustment. This is a count, grounded, and captures localisation.
- `itp_min_adjusted_pvalue` (float): the most significant adjusted p-value. Useful as a
  "is there ANY significant interval?" flag but must be accompanied by `itp_n_significant_0.05`
  to avoid the misleading impression.
- `itp_fraction_significant_0.05` (float): fraction of intervals significant. Ranges 0-1.
  When this is 0.2 (1/5), the LLM can cite "only 1 of 5 intervals significant at 0.05" rather
  than inferring broad significance from `min_p` alone.
- `itp_n_basis` (int): total number of intervals tested (denominator for the above).
- Do NOT store the full p-value vector in the diagnostics dict — only the four scalars above.
- Update `_ASPECT_PRIMERS["inference"]` to explain these ITP-specific fields separately from
  the existing global-test fields.

**Warning signs:**
- `_build_inference_diagnostics` stores only `itp_min_adjusted_pvalue` with no count.
- LLM evidence strings cite `itp_min_adjusted_pvalue = 0.02` without also citing
  `itp_n_significant_0.05`.
- The inference aspect primer does not explain ITP scalars separately from global-test scalars.

**Phase to address:**
Deferred advisor aspects phase (fill ITP). The scalar reduction design must be agreed in the
plan before implementing the diagnostics builder update.

---

### Pitfall 9: MCP LLM-Free Boundary Violated by Auto-Tune Tool

**What goes wrong:**
A new MCP tool `fdars_auto_tune` is added that internally calls `advise()`. Because `advise()`
imports the provider, makes an LLM call, and may consume an API key, the MCP server — which is
supposed to be provably LLM-free — now has a tool that imports and calls the LLM layer. The
`test_mcp_does_not_import_advise` test catches this for existing tools, but a new tool in a
new commit bypasses this test if the test only checks existing tool names.

**Why it happens:**
The auto-tuning loop is conceptually agentic and developers think of it as naturally living in
the MCP layer. But the existing MCP design intentionally keeps the server LLM-free: the agent
(LLM) drives the tools, the tools run fdars, the agent synthesises. Adding an `fdars_auto_tune`
tool that calls `advise()` collapses this separation — the MCP tool becomes an LLM caller.

**How to avoid:**
- Keep the MCP tool layer LLM-free. The auto-tuning loop at the MCP level is implemented as:
  the LLM agent calls `fdars_run_method` then `fdars_build_diagnostics` then `fdars_run_method`
  repeatedly, observing diagnostics at each step. The LLM IS the orchestrator; the tools only
  run fdars and return diagnostics. No new `fdars_auto_tune` MCP tool that calls `advise()`.
- If a convenience auto-tune tool is needed at the MCP level, it must call `run_method` and
  `build_diagnostics` only (no `advise`), returning a history of (params, diagnostics) pairs.
  The LLM interprets the history.
- Extend `test_mcp_does_not_import_advise` to also assert that no module under `fdars.mcp`
  imports `fdars.advisor.advise` — make the test import-graph-aware, not just
  `inspect.getmembers`-based.

**Warning signs:**
- A new MCP tool imports `from fdars.advisor import advise` anywhere in its body.
- `fdars.mcp.server` imports `advise` at module level.
- The `test_mcp_does_not_import_advise` test only checks the existing tool names but not new ones.

**Phase to address:**
Closed-loop auto-tuning capstone. Define the MCP auto-tune surface as "the LLM is the
orchestrator via existing tools" BEFORE writing code — this prevents the anti-pattern from
being implemented and then having to be refactored.

---

### Pitfall 10: Guard-Sync Drift — `_DIAGNOSTICS_METHODS` Diverges from `build_diagnostics._supported`

**What goes wrong:**
When adding PACE-FPCA, elastic-multinomial, and ITP deferred aspects, the developer adds the
new aspect string to `build_diagnostics._supported` in `advisor/__init__.py` (so the Python
API works) but forgets to add it to `_DIAGNOSTICS_METHODS` in `mcp/server.py`. The MCP tool
then rejects the aspect with "unsupported method". Or the reverse: the developer adds it to
`_DIAGNOSTICS_METHODS` first (so MCP works) but the `build_diagnostics` branch handler is
not yet written, causing a `ValueError` from `build_diagnostics` after the MCP guard passes.

**Why it happens:**
The guard-sync has been identified as a recurring risk (the v4.0 Phase 28 note "guard-sync
a no-op" and v5.0/v6.0 equivalents describe it each time). The two sets are defined in
different files and the test that checks their equivalence
(`test_diagnostics_methods_match_advisor_supported`) only runs if the mcp extra is installed.
On Python 3.9 CI (where mcp is unavailable), this test is skipped and the drift goes undetected
until a human runs the full suite on Python 3.10+.

**How to avoid:**
- The atomic-commit rule: `_supported` and `_DIAGNOSTICS_METHODS` must be updated in the SAME
  commit. Add a CI check (not just a test) that imports both sets on Python 3.10+ and asserts
  equality. This check must also run in the pre-commit lint step.
- For deferred aspects, if the Python API support is added before MCP support (or vice versa),
  use a placeholder comment, not a silent omission.
- The existing `test_diagnostics_methods_match_advisor_supported` test is the correct
  verification — make it not-skippable by extracting the `_supported` set to a module-level
  constant that can be imported without the mcp extra.

**Warning signs:**
- A commit message says "add X to build_diagnostics" without mentioning `_DIAGNOSTICS_METHODS`.
- The test `test_diagnostics_methods_match_advisor_supported` is skipped on Python 3.9 (the
  primary CI runner in this project's matrix).
- `build_diagnostics._supported` and `_DIAGNOSTICS_METHODS` differ by more than zero elements
  after any commit that touches either file.

**Phase to address:**
Deferred advisor aspects phase (foundational). This is the first phase in v8.0 and the
guard-sync must be part of each deferred-aspect acceptance criterion.

---

### Pitfall 11: `_ASPECT_PRIMERS` Extension Without Grounding-Aware Wording

**What goes wrong:**
When adding `_ASPECT_PRIMERS` entries for PACE-FPCA or elastic-multinomial, or updating the
`inference` entry for ITP, the primer clause describes the semantics of the new diagnostic
fields. If the primer uses vague wording like "higher pace_ncomp is better" without tying it
to a specific fdars-computed value, the LLM may invent a threshold ("typically >= 5") and cite
that invented threshold in `evidence`. This passes `_check_grounding` only if the invented
value happens to numerically equal something in the diagnostics dict.

**Why it happens:**
Primer authors write natural-language explanations without realising that every claim the
primer enables the LLM to make must be backed by a cited diagnostic value. The primer is not
itself a cited value — it is framing. Framing that implies a threshold ("a high sigma2 indicates
noise") causes the LLM to generate evidence like "sigma2=0.05 indicates high noise" — which
is grounded (0.05 is in the dict) — but also "noise level exceeds the typical 0.02 threshold"
— which is fabricated (no 0.02 in the diagnostics dict).

**How to avoid:**
- Primer clauses must describe WHAT the diagnostic measures and WHAT DIRECTION is better,
  without numeric thresholds. The existing `inference` primer ends with: "Interpret these values
  in the context of the study design and sample size — do not claim significance or non-significance
  beyond the p_value and alpha levels already provided." This explicit prohibition is the
  correct pattern.
- Add a similar prohibition to all new primers: "Only cite values from the diagnostics dict.
  Do not supply thresholds or reference values not present in the diagnostics."
- Test by running the primer through `advise()` with a mock diagnostics dict and asserting that
  `_check_grounding` passes and no invented numbers appear.

**Warning signs:**
- New primer clause contains phrases like "typically", "usually >= N", "standard threshold".
- `_check_grounding` starts raising `GroundingViolationError` on advice that was previously
  clean, after a primer extension.
- Evidence strings cite numeric values that are not in the diagnostics dict but look like
  domain thresholds (0.05 for p-values, 0.9 for variance explained).

**Phase to address:**
Deferred advisor aspects phase and any phase that extends `_ASPECT_PRIMERS`. Include a
primer-wording review in each phase's acceptance criteria.

---

### Pitfall 12: Evaluating "Good Advice" with LLM-as-Judge — Non-Determinism and CI Cost

**What goes wrong:**
The eval strategy uses a second LLM call to judge whether the advice from `advise()` is "good"
— e.g. a rubric-graded judge that scores the advice on a 1-5 scale. This creates: (a) a second
LLM call in the eval path, doubling cost; (b) non-determinism (the judge itself may score
differently each run, making eval results unreproducible); (c) network dependency in what
should be a deterministic test suite; and (d) the judge's own hallucination risk (it may score
a grounded-but-wrong recommendation as "good" because the prose sounds confident).

**Why it happens:**
LLM-as-judge is a common pattern in LLM system evaluation. Developers import it without
considering that this project has a clean offline/online split enforced by env-gating, and that
the grounding invariant already provides a deterministic quality signal.

**How to avoid:**
The primary eval signal for this system should be deterministic and LLM-free:

1. Grounding pass rate: `_check_grounding` already enforces that every cited value is in the
   diagnostics. A recommendation that passes `_check_grounding` is "groundedly correct".
   Track the pass rate across the aspect x provider matrix (already in `test_aspect_provider_matrix.py`).

2. Auto-tuning improvement rate: In the loop, the target diagnostic either improves or it does
   not. This is a deterministic fdars-computed comparison. For a fixed (dataset, starting
   params, target) triple with a mock advisor that proposes a known-good change, the correct
   outcome is deterministic. Assert it in CI without any LLM call.

3. Comparative selection accuracy: When both methods are run on a synthetic dataset where the
   ground truth is known (e.g. one method fits the data-generating process perfectly), assert
   that `comparative_select` returns the correct method. Entirely deterministic.

4. Aspect coverage: Assert that `build_diagnostics` emits all expected scalar keys for each
   aspect. If a key is missing or None when it should be populated, that is a measurable failure.

Use LLM-as-judge only as an optional, offline, manually-run quality audit — never in CI and
never as an acceptance criterion.

**Warning signs:**
- Eval test file imports a `judge` that calls `advise()` or any LLM provider.
- Eval tests are env-gated on `FDARS_INTEGRATION=1` AND listed as required for CI green.
- The eval acceptance criterion is "judge scores >= 4/5" rather than "grounding pass rate = 100%".

**Phase to address:**
Eval strategy phase. Define the eval approach before any implementation so it does not
retroactively constrain the system design.

---

### Pitfall 13: Comparative Method-Selection — Advice Cites the Wrong Run's Diagnostics

**What goes wrong:**
Comparative selection calls `build_diagnostics` twice (once per candidate method) and passes
both dicts to `advise()`. The merged dict contains `{"method_a": {...}, "method_b": {...}}`.
The LLM cites "method_b's r_squared=0.89" in evidence. But in the merged dict, 0.89 also
appears in method_a's diagnostics (as, say, `cumulative_variance_explained[-1]`). The
`_check_grounding` guard finds 0.89 in the flat-merged numbers and passes — but the
citation is provenance-incorrect.

**Why it happens:**
The same root cause as Pitfall 7 (aggregated provenance), but in the specific context of
comparative selection where two diagnostic dicts for DIFFERENT methods are combined. The guard
scans all numeric values in the merged dict without tracking which sub-dict they came from.

**How to avoid:**
- Structure the comparative selection input to `advise()` with namespaced keys:
  `{"fpca.explained_variance_ratio": [...], "pls.cv_error_rate": 0.12}` — never a flat merge
  of two different-method dicts.
- Alternatively, call `advise()` once per method to get per-method interpretation, then call
  a separate `compare_methods(advice_a, advice_b)` function that takes the two `Advice` objects
  and returns a `MethodComparison` object. This avoids combining raw numeric dicts entirely.
- If a single `advise()` call is used, add a `provenance_check` step after `_check_grounding`:
  for each evidence citation, verify that the cited value came from the diagnostics sub-dict
  labeled with the method the citation names.

**Warning signs:**
- Comparative selection passes `{**diag_a, **diag_b}` to `advise()`.
- Two method dicts have coincidentally equal values (very likely in FDA where 0.9, 0.95, 0.05
  appear frequently as explained-variance and p-value thresholds).
- After comparative selection, the LLM cites method A's value in a recommendation about method B.

**Phase to address:**
Comparative method-selection phase. The architecture decision (namespaced vs. per-method calls)
must be made in the plan, not during implementation.

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Single system prompt for all loop steps | Simpler to implement | LLM forward-predicts numeric outcomes; grounding violations accumulate over steps | Never — write a dedicated `_loop_system_prompt()` |
| Flat-merged multi-stage diagnostics dict | One `advise()` call for the whole pipeline | Provenance collapse; `_check_grounding` passes on wrong-run citations (Pitfall 7) | Never — use per-stage advice or namespaced keys |
| Auto-tune loop budget checked inside `advise()` | No new orchestrator code | LLM cost and time can exhaust before Python-layer enforcement | Never — enforce budget in the Python orchestrator |
| Skip guard-sync test on Python 3.9 | Faster CI on 3.9 | Drift between `_DIAGNOSTICS_METHODS` and `_supported` undetected until 3.10+ run | Acceptable only if a non-skippable lint check covers it |
| `min(adjusted_pvalues)` as the sole ITP scalar | Simple single-value reduction | Misleads the LLM into treating local significance as global (Pitfall 8) | Never — emit at minimum `n_significant` and `fraction_significant` alongside `min_p` |

---

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| `_check_grounding` + loop history | Passing the full history as part of the diagnostics dict; `_check_grounding` then accepts any historical value as "grounded" for the current step | Pass history in a separate `history:` section of the user content, outside the diagnostics block that `_check_grounding` reads |
| `fdars_compare_run` + auto-tune | Calling `fdars_compare_run` with different methods in `method` field across before/after | The before/after method must be identical; method change requires a new comparative-selection call, not a compare_run call |
| Provider-agnostic loop | Different providers format `expected_effect` differently (Ollama may be brief, Anthropic verbose) | Loop convergence must not parse `expected_effect` text; use only the fdars-computed diagnostic delta for convergence |
| Pipeline report + docs build | Pipeline report's worked example must not call `advise()` (network dependency); only the `build_diagnostics` stage of each pipeline step can execute in the docs fence | Keep all pipeline-report fences in `FDARS_FENCE_OK` mode using `run_llm=False` equivalents; the LLM step is illustrative only |
| ITP `adjusted_pvalues` array + grounding | `adjusted_pvalues` is a numpy array; putting it directly into the diagnostics dict breaks `_check_grounding` (which iterates `_flatten_diagnostics_numbers` on dict values) | Reduce to scalar diagnostics in `_build_inference_diagnostics` before the dict is returned; never put the raw array in the grounding-checked dict |

---

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| Re-running fdars at every loop step without caching the dataset | Loop re-reads and re-validates the same dataset arrays from the registry at every step | Cache the resolved `(data, argvals)` tuple at loop start; pass it directly to each step's `run_method` call | At > 10 steps on a dataset with n > 500 curves |
| Accumulating full diagnostics dicts in the loop history | Context window bloats after 5+ steps; LLM context truncation causes the advisor to lose early history | Store only `{step: int, param_changed: str, param_value: scalar, target_diagnostic: float}` per history entry | At > 7 steps or if diagnostics dicts are large (outliers or regression with many keys) |
| Building the full pipeline report by calling `build_diagnostics` on all stages sequentially | Each call re-imports the aspect module | All imports are lazy (existing pattern); no action needed unless profiling shows otherwise | Effectively never at typical pipeline depth (3-6 stages) |

---

## "Looks Done But Isn't" Checklist

- [ ] **ITP grounded-scalar reduction:** `adjusted_pvalues` array is stored as scalar count+fraction+min, not as a numpy array — verify `json.dumps(build_diagnostics(itp_result, "inference"))` succeeds without TypeError.
- [ ] **MCP LLM-free boundary:** No import of `fdars.advisor.advise` anywhere under `fdars.mcp` — verify with `grep -r "from fdars.advisor import advise" python/fdars/mcp/`.
- [ ] **Guard-sync atomic commit:** After any change to `build_diagnostics._supported`, the corresponding `_DIAGNOSTICS_METHODS` change is in the same commit — verify with `git diff HEAD --stat | grep -E "advisor.*__init__|mcp.*server"`.
- [ ] **Loop non-determinism:** The loop orchestrator unit tests run with a mock advisor and pass without `ANTHROPIC_API_KEY` — verify by running `pytest tests/test_advisor_loop.py -q` in a bare venv.
- [ ] **Comparative diagnostics provenance:** The comparative-selection advice has no evidence item that cites a value shared between method_a and method_b dicts — verify by constructing a synthetic case where the two dicts have no overlapping numeric values and asserting `_check_grounding` passes.
- [ ] **Pipeline report per-stage isolation:** The pipeline report never calls `advise()` on a flat-merged dict — verify by grepping for `{**` followed by `advise(` in the pipeline report implementation.
- [ ] **Goodhart guard diagnostics:** The auto-tune loop's acceptance test verifies that `edf` does not exceed 0.9 x n_obs even when `gcv_min` is successfully minimised.
- [ ] **Primer wording:** All new `_ASPECT_PRIMERS` entries end with a prohibition on inventing thresholds — verify by reading the new primer clause before merging.

---

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Loop non-termination discovered in production | HIGH | Kill the loop process; add `max_steps` enforcement; add the injectable-advisor test pattern; re-release |
| Grounding violation from wrong-run citation in pipeline report | MEDIUM | Refactor to per-stage `advise()` calls; existing `_check_grounding` continues to work correctly |
| Guard-sync drift discovered after release | LOW | Add the missing aspect to the lagging set in a patch commit; add the atomic-commit CI check so it cannot recur |
| LLM fabricates forward-looking numeric values in loop | MEDIUM | Add "do not predict numeric outcomes" to `_loop_system_prompt`; add the `expected_effect` numeric-literal assertion to tests |
| ITP min-only scalar misleads LLM | LOW | Add `n_significant` and `fraction_significant` fields to `_build_inference_diagnostics`; update the inference primer |

---

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| P1: Loop non-termination | Auto-tuning capstone — contract spec | Assert `stopped_by` field present in all loop return dicts; unit test with `max_steps=2` |
| P2: LLM re-enters numeric path | Auto-tuning capstone — `_loop_system_prompt` | Assert `expected_effect` in loop advice contains no numerics absent from current diagnostics |
| P3: Goodhart degradation | Auto-tuning capstone — guard-diagnostic contract | Assert guard diagnostics hold at every step in the acceptance test |
| P4: Oscillating loop | Auto-tuning capstone — history and convergence check | Unit test with mock advisor that alternates direction; assert loop terminates with `stopped_by="converged"` |
| P5: Non-deterministic loop (untestable) | Auto-tuning capstone — injectable advisor | All orchestrator tests pass with `pytest -q` in bare venv; no `ANTHROPIC_API_KEY` needed |
| P6: Incommensurable comparison | Comparative method-selection and auto-tuning capstone | Assert `ValueError` raised when `before["method"] != after["method"]` in compare |
| P7: Pipeline wrong-run citation | Pipeline diagnostic report phase | Assert `advise()` is never called on a flat-merged dict; per-stage isolation enforced |
| P8: ITP misleading scalar | Deferred advisor aspects phase (ITP) | Assert `n_significant`, `fraction_significant`, `min_adjusted_pvalue` all present; `json.dumps` succeeds |
| P9: MCP LLM-free boundary violated | Auto-tuning capstone — MCP surface design | `test_mcp_does_not_import_advise` passes; grep for `import advise` under `fdars.mcp` returns nothing |
| P10: Guard-sync drift | Deferred advisor aspects phase (foundational) | `test_diagnostics_methods_match_advisor_supported` passes without mcp extra; CI script enforces |
| P11: Primer wording enables fabrication | Deferred aspects + every `_ASPECT_PRIMERS` extension | `_check_grounding` passes on mock diagnostics after primer is added; no invented thresholds in evidence |
| P12: LLM-as-judge eval | Eval strategy phase | Eval acceptance criteria are grounding pass rate + deterministic improvement rate; no LLM judge in CI |
| P13: Comparative wrong-run citation | Comparative method-selection phase | Construct synthetic case with no overlapping values; assert `_check_grounding` correctly rejects wrong-run citations |

---

## Sources

- Codebase: `python/fdars/advisor/__init__.py`, `_prompts.py`, `_schema.py`, `providers/_validate.py`
- Codebase: `python/fdars/mcp/server.py`, `_runner.py`, `_compare.py`
- Codebase: `python/fdars/advisor/aspects/inference.py`, `fpca.py`, `classification.py`
- Codebase: `src/inference_mod.rs` — `itp_result_to_pydict` and the vector-valued `adjusted_pvalues`/`raw_pvalues` fields confirming the ITP vector-valued problem
- Project history: `.planning/PROJECT.md` — v6.0 Phase 40 ITP deferral ("ITP deferred as vector-valued")
- Project history: `.planning/PROJECT.md` — v4.0 Phase 28 "guard-synced atomic commit" pattern
- Project history: `MEMORY.md` — `advisor-grounding-guard-false-positives` (resolved false-positive classes inform the limits of the current guard)
- Project history: `MEMORY.md` — `v6-autonomous-run-state` (loop isolation lessons from doc-phase sequential execution)
- Design: `.planning/design/llm-cluster-narration.md` — recommend-only vs. agentic tuning split decision

---
*Pitfalls research for: fdars v8.0 Advisor — New Capabilities (agentic auto-tuning, comparative selection, pipeline reports, deferred aspects)*
*Researched: 2026-08-23*
