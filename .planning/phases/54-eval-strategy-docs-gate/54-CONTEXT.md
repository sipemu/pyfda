# Phase 54: Eval Strategy + Docs Gate - Context

**Gathered:** 2026-08-24
**Status:** Ready for planning
**Mode:** Smart discuss (autonomous) — all three grey areas accepted as recommended

<domain>
## Phase Boundary

Close the milestone on a proven quality bar: a deterministic eval strategy measuring "good advice" for the two agentic capabilities (comparative selection + auto-tuning), plus new/updated docs pages for the four v8.0 capabilities with method-accurate hand-authored SVGs and offline worked examples, gated by a green whole-site `mkdocs build --strict` and a BLOCKING human diagram method-accuracy review. Requirements: EVAL-01, EVAL-02, DOCS-01, DOCS-02, DOCS-03.

Out of boundary: any new advisor capability (all shipped in 50–53); the package semver bump (decided at milestone-close, triggers PyPI publish).

</domain>

<decisions>
## Implementation Decisions

### Eval strategy (EVAL-01/02)
- **Fixtures**: deterministic synthetic fixtures where the correct answer is known from the data — a constructed dataset with a known-best method (comparative) and a known improving convergence direction (auto-tune). New `tests/test_advisor_eval.py`.
- **Signals**: comparative — the fdars-computed ranked winner equals the known-best on the constructed dataset; auto-tune — the loop moves the target metric in the improving direction and terminates boundedly. Assert diagnostic improvement + grounding-pass.
- **CI policy**: offline deterministic checks only; any live-LLM eval is env-gated (skips without a key); CI stays network-free. NO LLM-as-judge in CI.
- **Scope**: eval covers the two "good advice" capabilities (comparative + auto-tune); the deferred aspects + pipeline remain covered by their existing grounding/offline tests.

### Docs pages & diagrams (DOCS-01/02)
- **Pages**: one new page per new capability — comparative method-selection, pipeline diagnostic report, closed-loop auto-tuning — PLUS an update to the existing `docs/advisor/aspects.md` for the 3 deferred aspects (PACE-FPCA, elastic-multinomial, ITP).
- **Diagrams**: 3 new method-accurate hand-authored inline SVGs — comparison ranking flow, pipeline stage-aggregation, auto-tune loop — STYLE_SPEC-conformant (`docs/assets/diagrams/STYLE_SPEC.md`), SVGO-idempotent.
- **Worked examples**: each new page carries a runnable offline `FDARS_FENCE_OK` worked example on small/synthetic data. The auto-tune example uses the OFFLINE/injectable path (mock/heuristic propose_fn) — NO network in the docs build.
- **Nav**: wire the new pages into the "AI Advisor" nav section in `mkdocs.yml` (alongside the existing index/python-api/mcp/providers/aspects/agent-skill pages).

### Gate & human review (DOCS-03)
- **Build gate**: whole-site `mkdocs build --strict` green OFFLINE (docs recipe: venv + `PYTHONPATH=scripts` + `DOCS_FAST` where applicable; build is ~19–25 min with executed fences — keep new fence data small).
- **SVGO**: the 3 new SVGs pass the SVGO idempotence + build-determinism gate.
- **Human review**: a BLOCKING human diagram method-accuracy review before milestone close — the orchestrator renders the new SVGs (PNG via rsvg-convert) and PAUSES for the user's approval (the standing v6.0/v7.0 decision; DOCS-03). This is the one required human pause in the phase.
- **Version bump**: the package semver bump (currently 0.7.0 → next; triggers PyPI publish) is surfaced at milestone-close, NOT in this phase.

### Claude's Discretion
- Exact page prose/structure (follow mature-page template: intro/method/worked example/parameters/caveats), SVG composition within STYLE_SPEC, and eval fixture datasets — at Claude's discretion, method-accurate against the shipped 50–53 code.

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `docs/advisor/` — existing AI Advisor section (index, python-api, mcp, providers, aspects, agent-skill) — the pattern + nav home for the new pages.
- `docs/assets/diagrams/STYLE_SPEC.md` — the SVG style spec (viewBox, 5 CSS classes, role/aria) all new diagrams must follow.
- v7.0 delivered the advisor-surface SVGs + the SVGO/determinism gate — the exact toolchain + review cadence to reuse.
- Shipped 50–53 code is the method-accuracy ground truth: compare_methods (+ fdars_compare_methods), build_pipeline_report/pipeline_report (+ fdars_build_pipeline_report), auto_tune (+ fdars_auto_tune), and the 3 deferred aspects.
- `scripts/docs_fig.py` + `markdown-exec` — the executed-fence mechanism (`PYTHONPATH=scripts`).

### Established Patterns
- Docs run SEQUENTIALLY on main, NOT in worktrees (fences hardcode the main-tree `.venv/bin/mkdocs` path — standing v6.0 decision).
- Offline `FDARS_FENCE_OK` sentinel proves a fence executed without network.
- Grounding invariant holds in doc examples (fdars computes; the advisor only interprets); the auto-tune doc example uses the offline injectable path so the docs build needs no API key.

### Integration Points
- New pages under `docs/advisor/`; new SVGs under `docs/assets/diagrams/`; nav in `mkdocs.yml`.
- New eval tests in `tests/test_advisor_eval.py`.

</code_context>

<specifics>
## Specific Ideas

- Docs phase runs SEQUENTIALLY on main (worktrees disabled) — the whole-site `--strict` fences build against the real tree.
- Keep new executed-fence data small (synthetic n ≤ 20 / subsampled) — the whole-site build is ~19–25 min.
- The blocking human diagram review is REQUIRED before milestone close (v6.0 lesson: a misdepicted method slipped past executors + verifier, caught only by human review).

</specifics>

<deferred>
## Deferred Ideas

- Eval fixtures for aspects/pipeline beyond their existing grounding tests — rejected (scope to the two "good advice" caps).
- One combined advisor page — rejected (3 separate capability pages).
- Package semver bump — deferred to milestone-close.
- A rendered HTML dashboard for the pipeline report — out of scope (narrative + docs diagram only).
</deferred>
