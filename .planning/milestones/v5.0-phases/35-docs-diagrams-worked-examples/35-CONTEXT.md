# Phase 35: Docs — Diagrams & Worked Examples - Context

**Gathered:** 2026-08-18
**Status:** Ready for planning
**Mode:** Smart discuss (autonomous) — docs structure grey area accepted by user

<domain>
## Phase Boundary

Document the v5.0 capabilities on the MkDocs site to the project's method-accurate standard: functional inference (two-sample tests, SCB bands, functional ANOVA), the functional boxplot, and the basis/smoothing quick wins — each with hand-authored inline SVG diagram(s) + runnable offline `FDARS_FENCE_OK` worked examples, wired into nav, whole-site `mkdocs build --strict` green offline, SVGs SVGO-idempotent, and a BLOCKING human diagram method-accuracy review. Covers DOCS-04, DOCS-05, DOCS-06, DOCS-07. Depends on Phases 31/32/33/34 (docs run against the real shipped bindings + advisor aspect). Final phase of v5.0.

</domain>

<decisions>
## Implementation Decisions (accepted grey area)

### Page structure & nav (DOCS-07)
- **New top-level "Inference" nav section** with ONE combined page ("Functional Inference") containing sections for (a) two-sample tests (`t_perm_test`/`f_perm_test`/`two_sample_mean_test`), (b) simultaneous confidence bands (`mean_scb`/`scb_two_sample_test`), and (c) one-way functional ANOVA (`oneway_anova_vstat`). Each section carries a method-accurate hand-authored inline SVG + a small executed fence. (DOCS-04)
- **Functional-boxplot page under `analyze/`** (beside the existing depth/outliers docs) with its own SVG (median / 50% central region / whiskers / flagged outliers) + executed fence. (DOCS-05)
- **Basis/smoothing additions fold into existing pages** — `constant_basis` documented in the existing basis/represent docs area; AIC selection (`smooth_basis_aic` + `optim_bandwidth(criterion="aic")` + `basis_nbasis_cv(criterion="aic")`) in the existing smoothing docs; the advisor `aspects.md` page updated to list the new `inference` aspect. No new standalone basis/smoothing page. (DOCS-06)
- All new pages wired into `mkdocs.yml` nav. (DOCS-07)

### Worked examples & build discipline (the ~18-min build is real)
- Every worked example is a runnable offline `markdown-exec` fence that emits the `FDARS_FENCE_OK` sentinel. Use SMALL params to protect the build: permutation tests `n_perm=19`, SCB `nb=50`, small/subset or synthetic data. NO network, NO API key (advisor examples that need a key stay illustrative/offline like the v2.1/v3.0 precedent).
- Datasets (per research): Growth (boys/girls) for two-sample tests; Canadian Weather (single group / by region) for SCB + ANOVA + functional boxplot; Tecator (NIR → fat%) for FLM inference. Load via the existing `docs/data/` datasets.
- Build recipe (from prior-milestone workflow): `PYTHONPATH=scripts DOCS_FAST=1 mkdocs build --strict` for fast iteration; the FINAL gate is a full (non-DOCS_FAST) `mkdocs build --strict` offline, exit 0, with `FDARS_FENCE_OK` present in every new executed page.

### Diagrams (DOCS-04/05/07)
- Hand-authored inline SVG only (no programmatic generation) — the locked project constraint. Conform to `docs/assets/diagrams/STYLE_SPEC.md` (viewBox, `.ttl/.sub/.lab/.sm/.mono` classes, system-ui fonts, muted palette, `role="img"` + `aria-label`).
- Every new SVG must pass the SVGO idempotence + determinism gate (the CI check over all diagrams). Method-accurate: each diagram faithfully depicts what the method actually does (permutation null distribution + observed statistic; SCB band around the mean; ANOVA between/within decomposition; boxplot central region + fence + outliers).
- Diagram designs are Claude's discretion against the STYLE_SPEC; correctness is validated at the blocking human review.

### Human review gate (DOCS-07, success criterion 4)
- A BLOCKING human diagram method-accuracy review is required before the milestone closes. In this autonomous run, the executor/verifier takes the phase as far as it can (all pages built, fences green, SVGs SVGO-idempotent, strict build green) and then HALTS at the human-verify checkpoint — the run surfaces the built pages/diagrams for the user to review (use `rsvg-convert` to render SVGs to PNG for visual inspection, per the prior-milestone recipe). The phase is not marked verified until the human confirms diagram accuracy.

### Claude's Discretion
- Exact prose, section ordering within the inference page, number of SVGs per section (min one per method family), and whether the basis/smoothing additions land in `learn/` vs `represent/` — decided at plan/execute time following the existing docs organization and the closest existing page.

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `docs/assets/diagrams/STYLE_SPEC.md` — the SVG style spec all new diagrams must conform to.
- `mkdocs.yml` — nav config; add the new "Inference" section + the analyze/ boxplot page + confirm existing basis/smoothing pages.
- `docs/` sections: `learn/`, `represent/`, `align/`, `analyze/`, `regression/`, `monitoring/`, `advisor/`, `reference/`, `examples/`. The v4.0 Phase 29 added 6 pages across represent/analyze/align with the same recipe — use those as structural templates.
- `docs/advisor/aspects.md` (or equivalent) — the per-aspect coverage page to update for the new `inference` aspect (14 aspects now).
- `scripts/` (`docs_fig.py`, `PYTHONPATH=scripts`) — the markdown-exec figure/execution mechanism; `docs/hooks.py` fallback.
- `docs/data/` — Growth, Canadian Weather, Tecator, phoneme, sonar, wine datasets for the fences.
- The v5.0 bindings/advisor are already shipped (Phases 31–34): `fdars.inference.*`, `fdars.depth.functional_depth/functional_boxplot`, `fdars.basis.constant_basis/smooth_basis_aic`, `fdars.smoothing`/`optim_bandwidth(criterion="aic")`, advisor `inference` aspect.

### Established Patterns (v1.0 + v4.0 docs)
- Diagram referenced as `![...](../assets/diagrams/NAME.svg){ .fdars-diagram }`; inline figures via markdown-exec importing `docs_fig` from `scripts/`.
- Executed offline fences emit `FDARS_FENCE_OK`; whole-site `mkdocs build --strict` must be exit 0 offline; new SVGs SVGO-idempotent; per-page human method-accuracy review.

### Integration Points
- New/edited files under `docs/`, new SVGs under `docs/assets/diagrams/`, `mkdocs.yml` nav. No Rust/Python source changes (bindings already shipped). Build/test = the docs toolchain, not pytest (though the pytest suite must remain green — no source changes expected).

</code_context>

<specifics>
## Specific Ideas

- Inference page diagrams: (a) permutation test — observed statistic vs. the permutation null histogram with the p-value tail shaded; (b) SCB — mean curve with a simultaneous band, contrasted with pointwise CIs; (c) ANOVA — between-group vs. within-group variation decomposition. Functional boxplot: the canonical López-Pintado–Romo picture (deepest median curve, shaded 50% central region, whiskers/fence, flagged outlier curves).
- Keep executed fences tiny (subset rows/cols, `n_perm=19`, `nb=50`) — the full strict build already runs ~18 min; do not add heavy compute.

</specifics>

<deferred>
## Deferred Ideas

- Functional-boxplot advisor outlier diagnostics — deferred (Phase 34 decision); docs may mention the numeric result but no advisor aspect for it.
- A11Y-01 (long-form `<title>`/`<desc>` + aria-labelledby) — still deferred to a future milestone.
- `fdars.plot.plot_functional_boxplot()` helper (PLOT-01) — future; docs show the numeric dict, not a plotting helper.

</deferred>
