# Phase 15: Python API Page - Context

**Gathered:** 2026-08-11
**Status:** Ready for planning

<domain>
## Phase Boundary

Author a new `docs/advisor/python-api.md` page documenting the recommend-only Python advisor surface — `build_diagnostics`, `advise`, `describe_cluster_differences`, and the `Advice`/`Recommendation` schema — with a worked example whose offline fence executes during the docs build against a `docs/data/` dataset (no API key). Covers PYDOC-01, PYDOC-02, PYDOC-03. The `mkdocs.yml` nav entry is added in Phase 18 (NAVDOC-01); this phase authors the page and may add it to the `advisor/` section content, but full nav wiring + build gate is Phase 18.

</domain>

<decisions>
## Implementation Decisions

### Page & Runnable Example
- Page path: `docs/advisor/python-api.md` (under the `advisor/` section created in Phase 14).
- Dataset for the worked example: Canadian Weather (`docs/data/canadian_weather*.csv`), consistent with `examples/advisor_recipe.py`.
- The EXECUTED fence is offline and needs no API key: load the dataset → cluster with `kmeans_fd` → `build_diagnostics(method="clustering", ...)` → print a couple of diagnostic values.
- `advise()` is shown as an ILLUSTRATIVE (non-executed) fence: the call plus a representative `Advice`, explicitly marked "requires `ANTHROPIC_API_KEY`, not run in the docs build." Never run a live LLM call in the docs build.

### Execution Mechanism & Depth
- Use the repo's established offline doc-exec mechanism (markdown-exec with `PYTHONPATH=scripts`) so the offline fence's output renders inline on the page — match how existing pages run offline code; the executor must read an existing exec-fence page to copy the exact directive.
- Document `describe_cluster_differences`, including its `run_llm=False` offline escape hatch (returns the raw diagnostics dict — usable without a key).
- Present the schema as small tables: `Recommendation` (fields `action` / `kind` / `rationale` / `expected_effect` / `evidence`) and `Advice` (`interpretation` / `recommendations` / `caveats`). Field names/types must match `python/fdars/advisor.py`.
- Cross-link back to the advisor overview (`docs/advisor/index.md`) and forward to the MCP/Skill pages (authored in Phases 16–17 — use section-relative links that will resolve once those pages exist).

### Claude's Discretion
- Exact prose, table wording, and section order, subject to method-accuracy against the source.
- Exact `kmeans_fd` parameters for the example, as long as the fence runs offline and deterministically in the build.

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `python/fdars/advisor.py` — `__all__ = ["build_diagnostics", "advise", "describe_cluster_differences", "Advice", "Recommendation"]`. `advise(diagnostics, task, ...)` returns `Advice`; `describe_cluster_differences(..., run_llm=True)` wraps `build_diagnostics(method="clustering")` + advise, with `run_llm=False` returning the raw diagnostics dict.
- `examples/advisor_recipe.py` — the canonical offline Canadian Weather → kmeans_fd → build_diagnostics recipe to mirror.
- `docs/advisor/index.md` — the Phase 14 overview page to cross-link from/to.
- Existing docs pages that run offline code fences via markdown-exec (`PYTHONPATH=scripts`, `scripts/docs_fig.py`) — copy the exact fence directive from one of them.

### Established Patterns
- Docs build runs executable fences; the doc-test harness is `pytest-markdown-docs` (one-page CI gate) and inline execution is markdown-exec.
- Grounding invariant: the executed example computes real diagnostics offline; the LLM `advise()` step is never run in the build.
- `Advice` schema: `Recommendation` requires `evidence: list[str]` citing diagnostic values (enforced by Pydantic + system prompt).

### Integration Points
- New file `docs/advisor/python-api.md`.
- `mkdocs.yml` nav wiring deferred to Phase 18.
- Datasets in `docs/data/` (canadian_weather*.csv) drive the example.

</code_context>

<specifics>
## Specific Ideas

- The executed fence MUST run offline in the build with no `ANTHROPIC_API_KEY` — a build that tries a live LLM call is a defect.
- Signatures, argument names, return types, and schema field names must be verified against `python/fdars/advisor.py` before writing — do not invent parameters.

</specifics>

<deferred>
## Deferred Ideas

- MCP server page (Phase 16) and Agent Skill page (Phase 17) — only cross-linked here.
- `mkdocs.yml` nav wiring + full-build gate (Phase 18).

</deferred>
