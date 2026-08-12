# Phase 21: Per-Aspect Advisor Coverage - Context

**Gathered:** 2026-08-12
**Status:** Ready for planning
**Mode:** Auto-generated (autonomous smart-discuss — diagnostics grounded in `.planning/research/FEATURES.md`, which validated each aspect's output keys against the fdars Rust source)

<domain>
## Phase Boundary

Every fdars analysis aspect — not just clustering — has deterministic offline diagnostics and grounded advice task families, driven by the SAME schema, prompt, and grounding machinery with no per-aspect duplication.

In scope (REQ-IDs): ASPECT-01, ASPECT-02, ASPECT-03, ASPECT-04, ASPECT-05, ASPECT-06, ASPECT-07.

Out of scope: MCP/Skill surface exposure of the new aspects (Phase 22); CI matrix / packaging (Phase 23); docs (Phase 24). This phase is the compute + prompt layer only, driven through the existing Python `advise()`/`build_diagnostics()`.
</domain>

<decisions>
## Implementation Decisions

### Grounded in research (FEATURES.md — per-aspect diagnostics verified against fdars Rust output keys; ARCHITECTURE.md aspects/ layout)

- **New `build_diagnostics` branches**, each a new file under `advisor/aspects/` (mirroring the existing 5), added to the dispatcher `_supported` set in `advisor/__init__.py`. Each is PURE NumPy over the fdars result dict — deterministic, offline, network-free, JSON-serialisable (no numpy scalars leak):
  - **depth** (ASPECT-02) — LOW: summary stats over the returned depth vector (min/median/max, ranking spread, most/least central).
  - **outliers** (ASPECT-02) — LOW: outlier flags/counts, magnitude-vs-shape split, threshold used.
  - **classification** (ASPECT-03) — LOW: class balance, accuracy/confusion summary if present, per-class support.
  - **represent** (ASPECT-01) — LOW: basis/FPCA representation quality (variance captured, n components/nbasis, reconstruction error). Reuse the existing FPCA eigenvalue→variance logic; reconcile with the existing `basis`/`fpca` aspects (extend or add `represent` as its own method string — Claude's discretion, but do not duplicate the eigenvalue→variance code).
  - **regression** + **regression_cv** (ASPECT-04) — MEDIUM: `fregre_lm`/`fregre_pls` fit quality (r², residual skew/spread), and cross-validation summary (`fregre_cv`: chosen hyperparam, CV error curve summary).
  - **spm** (ASPECT-05) — HIGH (the only high-complexity branch): Phase-1 monitoring — T² and SPE exceedance rates, `spe_moment_match_diagnostic` (a real fdars function), eigenvalue→variance conversion (reuse FPCA branch logic). **Exclude** stochastic ARL (`arl0_t2`) — it would break the offline determinism guarantee.
- **ASPECT-06 (task families, no duplication):** the three task families (interpretation, parameter guidance, method guidance) already flow through the shared `_system_prompt(task, aspect)` + `Advice` schema built in Phases 19. Extend the per-aspect clause coverage so every aspect (old + new) has an appropriate FDA-primer clause — do NOT add a new function/schema per aspect. One shared prompt builder, one schema.
- **ASPECT-07 (caller-specified aspect):** `build_diagnostics(result, method, …)` already takes an explicit `method`; keep it caller-specified and NEVER auto-detect the aspect from result keys (key collisions like `r_squared`/`edf` make auto-detection unsafe). Preserve/verify this and add a test asserting no auto-detection path exists.
- **Determinism gate (per success criterion 4):** each new aspect gets an offline determinism test — same input → byte-identical JSON-serialisable output, no numpy scalar types.

### Claude's Discretion

Exact diagnostic field names per aspect, whether `represent` is a new method string vs an extension of `basis`/`fpca`, and the precise SPM exceedance-rate formulation — at Claude's discretion, guided by FEATURES.md's per-aspect reference table and the actual fdars result keys. Verify SPM's `spe_moment_match_diagnostic` signature against the code at plan/execute time.
</decisions>

<code_context>
## Existing Code Insights

- `python/fdars/advisor/__init__.py:115` — `_supported = {"alignment", "fpca", "basis", "smoothing", "clustering"}`; `build_diagnostics()` dispatches lazily to `advisor/aspects/<name>.py`. Extend this set + add the new aspect files.
- `python/fdars/advisor/aspects/` — existing builders: alignment.py, basis.py, clustering.py, fpca.py, smoothing.py (the pattern to mirror; fpca.py has the eigenvalue→variance logic to reuse for represent + spm).
- `python/fdars/advisor/_prompts.py` — `_system_prompt(task, aspect)` + `_GROUNDING_INVARIANT`; extend aspect clauses only.
- `python/fdars/advisor/_schema.py` — `Advice`/`Recommendation` (shared; do NOT duplicate per aspect).
- The grounding invariant + provider layer (Phases 19–20) are unchanged by this phase — new diagnostics feed the same `advise()`.
- fdars result keys per aspect are documented in `.planning/research/FEATURES.md` "Per-Aspect Diagnostics Reference"; the underlying Rust modules are `depth_mod.rs`, `outliers_mod.rs`, `classification_mod.rs`, `regression_mod.rs`, `spm_mod.rs`, `basis_mod.rs`.
</code_context>

<specifics>
## Specific Ideas

- Offline determinism tests per new aspect: run `build_diagnostics` twice on a fixed real dataset (e.g. Canadian Weather) or synthetic input, assert byte-identical `json.dumps(..., sort_keys=True)` and that all values are native Python types (no `np.float64`).
- Reuse a shared eigenvalue→variance helper for fpca/represent/spm rather than copying it into three files.
- Verify SPM against the real fdars API (`spm_phase1`, `spe_moment_match_diagnostic`) before finalizing that builder — flagged HIGH complexity.
- Add a test asserting the aspect is caller-specified (a wrong `method` for a given result dict raises/produces that method's diagnostics, never silently re-routes).
</specifics>

<deferred>
## Deferred Ideas

- Exposing the new aspects through MCP tools + the Agent Skill → Phase 22.
- Stochastic ARL SPM diagnostics → out of scope entirely (FUT-02, breaks determinism).
- Cross-aspect compound diagnostics → out of scope (FUT-03).
</deferred>
