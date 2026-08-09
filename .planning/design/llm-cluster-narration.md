# Design: Grounded AI analysis advisor for `fdars`

**Status:** Approved (design), 2026-08-09 — pending implementation via GSD (milestone v2.0).
**Scope:** New milestone. Net-new library + LLM-integration capability across three surfaces.
Broadened from the original "describe cluster differences" idea to a general **analysis
advisor**; cluster-difference description is one supported task.

## Guiding principle

**One deterministic core, computed by `fdars`; the LLM interprets and reasons over the
computed numbers — it never fabricates them.** Every interpretation and recommendation cites
computed diagnostics and states an expected effect. This grounding invariant holds on every
surface.

## What the advisor does

Given a computed `fdars` result, the advisor:
1. **Interprets** it in domain terms (what the result means).
2. **Recommends** concrete next actions — parameter adjustments or alternative methods.
3. **Explains why** — rationale tied to the computed diagnostics, plus the expected effect.

Three task families:
- **Interpretation** — explain a result (e.g. amplitude vs phase split, FPCA modes, control-limit exceedances).
- **Parameter guidance** — recommend adjustments to `lambda_`, `n_basis`, bandwidth, `n_comp`,
  cluster `k`, depth method, etc., grounded in diagnostics (GCV curve, variance explained,
  warp penalty, cluster separation) with rationale + expected effect.
- **Method guidance** — suggest alternative methods when diagnostics indicate a poor fit
  (linear FPCA + phase variation → elastic FPCA; sparse/irregular sampling → pre-smooth to a
  common grid; density/constrained data → transform to an unconstrained space). Ties directly
  to the **Scope & limitations** boundaries documented on the align/ and represent/ pages.

**Cluster-difference description** is one interpretation task: fdars computes a feature report
(Karcher means, `amplitude_distance`/`phase_distance`, `vert`/`horiz`/`joint_fpca`,
`elastic_logistic` discriminative regions); the advisor verbalizes and interprets it.

## Recommend-only vs. agentic tuning (split by surface)

- **Python API — recommend-only.** Returns structured advice (recommendation + rationale +
  expected effect) that the user inspects and applies. Deterministic to audit; no autonomous loop.
- **Tool/MCP and Agent Skill — agentic.** The model can actually **re-run fdars** with the
  suggested parameters via tools and **compare before/after** diagnostics, iterating until a
  stopping criterion. The compute stays deterministic (fdars); the model orchestrates.

## Core primitive (shared by all surfaces)

New pure-Python module `python/fdars/advisor.py` (separate from the native `explain` module).

### Stage 1 — `build_diagnostics(result, method, ...) -> dict`
*No LLM, offline, deterministic.* A per-method diagnostics report built only from fdars +
numpy. Examples by method:
- **Alignment:** Karcher mean, warp penalty, amplitude/phase distances, alignment convergence.
- **FPCA:** eigenvalues / cumulative variance explained, phase-leakage indicators.
- **Basis/smoothing:** GCV curve, edf, AIC/BIC vs `n_basis`/`lambda_`.
- **Clustering:** per-cluster Karcher means, pairwise amplitude/phase separation, discriminative regions.
The **cluster-difference feature report** is one specialization of this builder.

### Stage 2 — `advise(diagnostics, *, task, domain_context, model="claude-opus-4-8") -> Advice`
Grounded Claude call. Structured output; the model interprets + recommends + explains, citing
diagnostics.

### Schema (Pydantic, structured outputs)
```python
class Recommendation(BaseModel):
    action: str                     # e.g. "increase n_basis to ~15"
    kind: Literal["parameter", "method", "none"]
    rationale: str                  # why — tied to a diagnostic
    expected_effect: str            # what should change if applied
    evidence: list[str]             # each cites a diagnostic value

class Advice(BaseModel):
    interpretation: str
    recommendations: list[Recommendation]
    caveats: list[str]
```

### Grounding mechanics (current Claude API)
- `client.messages.parse(model="claude-opus-4-8", output_format=Advice, ...)` — schema-validated,
  retries on mismatch.
- System prompt: reason only from the provided diagnostics; every `evidence` item cites a value;
  omit unsupported claims; primer on FDA concepts (amplitude vs phase, GCV, variance explained)
  so the model interprets correctly.
- Adaptive thinking on; default effort.
- Optional vision: attach a rendered diagnostic plot (Opus 4.8 high-res) as a complement —
  numbers remain source of truth.

### Dependency hygiene
- `anthropic` gated behind optional extra `pip install fdars[advisor]`; `ImportError` with install
  hint if missing. API key from `ANTHROPIC_API_KEY`. `build_diagnostics` has no LLM/network dep.

## Surfaces

1. **Python API** — `python/fdars/advisor.py`, `__all__ = ["build_diagnostics", "advise",
   "describe_cluster_differences"]`; registered via existing pure-Python injection. Recommend-only.
   `[advisor]` extra in `pyproject.toml`. `build_diagnostics` fully unit-testable offline; LLM
   call stubbed / gated integration test (no network in CI).
2. **Tool / MCP** — coarse-grained tools (`fdars_build_diagnostics`, `fdars_run_method`) so the
   model can re-run and compare; MCP server (stdio local / HTTP-SSE hosted). Data passed by reference.
3. **Anthropic Agent Skill** — `SKILL.md` + script teaching the interpret→recommend→re-run→compare
   loop. Execution env TBD (recommend Managed Agents with `allow_package_managers`, or bundle wheel;
   basic Messages-API code-execution sandbox has no internet).

## Cross-cutting
- `build_diagnostics` is the single deterministic implementation used by all surfaces.
- Grounding invariant everywhere: recommendations cite diagnostics + state expected effect; the
  LLM never invents numbers.
- Method-accuracy (project value): interpretations/recommendations validated against known
  datasets in `docs/data/`.

## Proposed phase order (continues numbering from v1.0 → starts at Phase 10)
1. **Core** — `build_diagnostics` (offline, tested) + `advise` (grounded, schema) + the
   cluster-difference specialization.
2. **Python API surface** — module registration, `[advisor]` extra, tests, `examples/` recipe page.
3. **Tool/MCP surface** — tools + MCP server + agentic re-run/compare loop.
4. **Agent Skill** — SKILL.md + script + packaging.

## Open decisions (recommended defaults)
1. **Skill execution target:** Managed Agents env with package managers (recommended) vs bundled
   wheel vs Messages-API container.
2. **MCP transport:** stdio (local) vs HTTP/SSE (hosted) — or both.
3. **`anthropic` SDK version floor** — a current one supporting `messages.parse` + `claude-opus-4-8`.

## Verified fdars API (from source sweep)
`karcher_mean`, `karcher_median`, `robust_karcher_mean`, `amplitude_distance`, `phase_distance`,
`elastic_distance`, `vert_fpca`, `horiz_fpca`, `joint_fpca`, `elastic_logistic`,
`pspline_fit_gcv`, `smooth_basis_gcv`, `basis_nbasis_cv`, `select_basis_auto_1d` — in
`src/alignment_mod.rs` and `src/basis_mod.rs`. Single shared `argvals` grid required.
