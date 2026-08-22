# Phase 48: Page Depth - Context

**Gathered:** 2026-08-22
**Status:** Ready for planning
**Mode:** Discuss answers captured below (scope = 8 thin + 2 borderline; new fences = selective). Milestone-level decision: "full parity + new worked examples."

<domain>
## Phase Boundary

Extend the thin v4–v6 method pages to the structure of the mature pages — intro/theory, method explanation, worked example, **parameters table**, **caveats/interpretation** — and add new executable worked examples where they materially help (DEPTH-01/02/03). This phase edits `docs/**/*.md` PAGE CONTENT only — NO diagrams (all diagram work finished in Phases 42–47). NO whole-site `mkdocs build --strict` (that is Phase 49); verify new fences execute at the page level (see gate below).

**Target pages (10 — from 42-AUDIT.md §4; user chose 8 thin + 2 borderline):**
- `regression/concurrent-regression.md` (79) — add params table, caveats/interpretation, extended worked example (currently only a code snippet).
- `regression/functional-glm.md` (106) — add params table (GLM-family link functions), caveats/interpretation, a multi-family worked example (currently only binary response). NOTE: Gamma uses inverse canonical link 1/μ (NOT log; ≠ R) — document accurately.
- `represent/pace-fpca.md` (116) — add params/returns for `irreg_fdata_from_lists` + `pace_fpca`, caveats (when PACE fails vs basis-smoothing), a comparison with standard FPCA.
- `inference/interval-inference.md` (145) — add caveats (sample-size requirements, basis sensitivity), a comparison with the permutation test; flesh out the 3 signatures (`itp_one_pop`/`itp_two_pop`/`itp_flm`).
- `represent/interpolation.md` (125) — add params table, caveats (aliasing, oscillation risk with high-degree splines), comparison with smoothing.
- `represent/imputation.md` (126) — add params table for `ImputationMethod`, caveats (MCAR vs MAR assumptions), strengthen recommendations.
- `analyze/scoring-metrics.md` (132) — add caveats for `functional_mape` (y_true≠0), metric-selection-by-use-case guidance, a comparison table of metrics.
- `analyze/functional-statistics.md` (141) — add caveats on covariance-surface estimation (small-n bias), guidance on depth-median vs geometric-median.
- `align/banded-alignment.md` (156, borderline) — add theoretical justification for the Sakoe–Chiba band (why O(m·B) vs O(m²)), caveats on `band_frac` selection for long-range phase shifts.
- `align/shift-registration.md` (169, borderline) — add interpretation thresholds for the quality scores (`sobolev_score`, `alignment_score`), comparison with landmark registration.
</domain>

<decisions>
## Implementation Decisions

### Extension depth (per DEPTH-01/02 + milestone "full parity")
- Bring each of the 10 pages to the mature-page structure: intro/theory → method explanation → worked example → **parameters table** → **caveats/interpretation/comparison**. Match the depth of confirmed-mature peers (e.g. `analyze/outlier-detection.md`, `regression/classification.md`).
- Parameters tables MUST be accurate to the shipped API — read the actual binding signatures (`python/fdars/…`, `src/*_mod.rs`) for parameter names, defaults, and returns. Do NOT invent parameters.

### New worked examples / fences (selective — user choice)
- Add the missing structure (params table, caveats, comparisons) to EVERY target page.
- Add a NEW executable offline worked example (`FDARS_FENCE_OK` sentinel) ONLY where it materially helps — e.g. a multi-family GLM example on functional-glm, a PACE-vs-standard-FPCA comparison on pace-fpca, an ITP-vs-permutation comparison on interval-inference. Reuse each page's EXISTING fence otherwise. Do NOT add a new executable fence to every page (keeps the ~19–25 min build near-flat).
- Every fence (new or reused) runs OFFLINE against the current `fdars` API and emits `FDARS_FENCE_OK`; keep NEW fence data SMALL (synthetic `n ≤ 20`, subsampled datasets) to hold build time down.

### Method-accuracy
- Prose, params, and examples must be method-accurate against the shipped bindings (the docs' core value). Where a page's claim is uncertain, verify against the code; surface genuine ambiguities in the SUMMARY.

### Per-page verification gate (NOT a whole-site build)
- For each page with a NEW or MODIFIED fence: verify the fence executes and emits `FDARS_FENCE_OK` — either by running the fence's Python directly under the repo `.venv` (`PYTHONPATH=scripts`), or a targeted `DOCS_FAST` build of the affected page(s). The whole-site `mkdocs build --strict` is Phase 49 (GATE-01).
- Pages with only prose/params/caveats additions (no fence change) need no build — just method-accuracy review.

### Commit granularity
- Batched by section/theme (e.g. regression pages, represent pages, analyze pages, align pages, inference page) — planner's judgment; one commit per batch.

### Claude's Discretion
- Exact section wording, table columns, and which pages get a new fence vs reuse, at the executor's discretion within "full parity + selective fences + method-accurate + small fence data."

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `.planning/phases/42-diagram-audit/42-AUDIT.md` §4 — the thin-page list + per-page missing sections (authoritative worklist).
- Mature peer pages for the structure bar: `analyze/outlier-detection.md` (681), `regression/classification.md` (680), `inference/functional-inference.md` (317).
- The `FDARS_FENCE_OK` fence pattern (markdown-exec) — see existing fences in `docs/regression/concurrent-regression.md:72`, `docs/represent/imputation.md:95`, etc.
- Build recipe (memory: docs-diagram-verify-workflow): repo `.venv` + `PYTHONPATH=scripts` + `DOCS_FAST`.
- Shipped bindings for params/method-accuracy: `python/fdars/` + `src/*_mod.rs` for each page's methods.

### Established Patterns
- Executed fences emit `FDARS_FENCE_OK`; data kept small; offline (no network/key).
- Pages already in nav — no mkdocs.yml/nav change needed.

### Integration Points
- Only the 10 `.md` pages change (+ possibly new small fence code within them). No diagrams touched (Phases 42–47 done). Whole-site `--strict` build + blocking human review at Phase 49.

</code_context>

<specifics>
## Specific Ideas

- `functional-glm.md` Gamma link + AIC caveat is method-sensitive: fdars Gamma uses inverse canonical link 1/μ (NOT log), and its AIC is NOT comparable to R `glm()` — the caveats section must state this (matches the shipped code + the v6.0 research finding, and the just-verified functional-glm.svg).
- Advisor pages are NOT in Phase 48's depth scope (this milestone's DEPTH targets the v4–v6 method pages).
- Two code-vs-prose discrepancies surfaced in Phase 47 (mcp.md "5 methods" vs code 6; aspects.md "12+" vs code 14) are ADVISOR pages, out of Phase 48 scope — leave for a possible Phase 49 note, do NOT edit here.

</specifics>

<deferred>
## Deferred Ideas

- Whole-site `mkdocs build --strict` (GATE-01) + blocking human review (GATE-02) → Phase 49.
- Advisor-page prose depth + the mcp/aspects prose-vs-code count updates → out of this milestone's DEPTH scope (Phase 49 note at most).

</deferred>
