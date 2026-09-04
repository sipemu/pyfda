# Phase 73: Documentation & Release - Context

**Gathered:** 2026-09-04
**Status:** Ready for planning
**Mode:** Smart discuss (autonomous)

<domain>
## Phase Boundary

The milestone-closing phase: document every new v11.0 capability family to the project's
method-accurate standard, update the advisor docs, pass the whole-site strict build, obtain
the blocking human diagram review, and release the package.

In scope:
- **DOCS-01:** one dedicated method-accurate page per new capability family, each with a
  RUNNABLE OFFLINE worked example emitting `FDARS_FENCE_OK`, wired into `mkdocs.yml` nav:
  - **Regression section:** Function-on-Function (fof + fof_re), Additive/Generalized SoF
    (fam/gkam/gsam + selection), Fréchet Regression (frechet).
  - **Analyze section:** Functional Time Series (fts), Density FDA (density_fda), Advanced
    Clustering (dbscan/kcfc/funfem/align), Multi-Domain/FAMM (multi_fdata + famm + mfpca),
    Shapelets (shapelet + GAK metric folds in here or on Distance Metrics).
- **DOCS-02:** one hand-authored, STYLE_SPEC-conformant, SVGO-idempotent inline SVG concept
  diagram per new family, method-accurate against the shipped binding.
- **DOCS-03:** advisor `aspects.md` updated for the new/extended aspects (fts, frechet,
  regression/classification/spm); whole-site `mkdocs build --strict` green OFFLINE; the
  BLOCKING human diagram method-accuracy review approved before close.
- **REL-01:** version bump `0.9.0 → 0.10.0` in `Cargo.toml` + `pyproject.toml`; semver tag
  `v0.10.0` (triggers PyPI publish) — applied at close.

Out of scope: any new bindings/advisor logic (all landed in Phases 66-72).

</domain>

<decisions>
## Implementation Decisions

### Nav organization (user decision)
- **Slot into existing sections** — NO new top-level nav groups. Regression gets
  Function-on-Function, Additive/Generalized SoF, Fréchet Regression; Analyze gets Functional
  Time Series, Density FDA, Advanced Clustering, Multi-Domain/FAMM, Shapelets. GAK folds into
  the Shapelets page (or Distance Metrics). Keeps the method-organized structure stable.

### Hard human gates (NOT autonomous — stop and wait)
- **Blocking human diagram method-accuracy review (DOCS-03, standing v6.0 decision — the
  hypograph/epigraph lesson):** after authoring the 7 diagrams + running `--strict`, PAUSE for
  the user to review each diagram's method-accuracy against the shipped binding. Verification is
  `human_needed` until approved. Do NOT self-approve.
- **Release (REL-01):** the `v0.10.0` tag triggers a PyPI publish — an outward-facing,
  irreversible action. Prep the version bump (0.9.0 → 0.10.0 in both files) but DO NOT create
  the tag / publish autonomously; present it as a checkpoint for the user to trigger after the
  diagram review passes.

### Claude's Discretion (convention-driven)
- **Worked examples:** offline-runnable markdown-exec fences using small datasets (STATE build-
  time note: keep fence datasets small — 5 new submodules add ~10 min to `--strict`), each
  emitting `FDARS_FENCE_OK` per the existing page convention (see docs/represent/depth-functions.md).
- **Diagrams:** hand-authored inline SVG per `docs/assets/diagrams/STYLE_SPEC.md`; SVGO-idempotent
  (run svgo, re-run = no change); method-accurate concept per family. Follow the v7/v10 diagram
  authoring workflow (venv + PYTHONPATH + rsvg-convert visual check).
- **Build:** sequential on `main` (use_worktrees:false); doc-build fences hardcode the main-tree
  `.venv/bin/mkdocs` path; use `DOCS_FAST` for iteration, `mkdocs build --strict` for the final
  offline gate. Advisor fences need `pydantic` in the docs env (STATE CI gotcha).

</decisions>

<code_context>
## Existing Code Insights

### Structure
- `docs/` sections: learn, represent, align, regression, monitoring, inference, analyze, advisor, sklearn, reference.
- `mkdocs.yml` nav (method-organized); add the 7 pages under Regression + Analyze.
- `docs/assets/diagrams/STYLE_SPEC.md` — the diagram authoring standard.
- `docs/advisor/aspects.md` — the per-aspect coverage page (update for fts/frechet + extended regression/classification/spm).
- `FDARS_FENCE_OK` fence convention: docs/represent/depth-functions.md, docs/learn/smoothing.md, docs/represent/interpolation.md (worked-example templates).
- `docs/hooks.py` / `docs/includes` — mkdocs hooks/snippets.

### Worked-example API (from the shipped bindings — Phases 67-71)
- fts: `fdars.fts.{ftsm,ftsm_forecast,functional_acf,stationarity_test,fplsr,dpca,...}`
- fof/sof: `fdars.regression.{fof_regression,predict_fof,fof_cv,fof_re_regression}`, `fdars.scalar_on_function.{fam,fregre_gkam,fregre_gsam,variable_selection,model_selection_ncomp}`
- frechet: `fdars.frechet.{frechet_mean,frechet_global_reg,frechet_local_reg,frechet_anova}`
- density: `fdars.density_fda.{normalize_density,lqd_transform,inverse_lqd,wasserstein_barycenter,lqd_fpca}`
- multi-domain/FAMM: `fdars.multi_fdata.multi_fdata_from_components`, `fdars.famm.{dense_flmm,fast_fmm,multi_famm}`, `fdars.spm.{mfpca,spe_multivariate}`
- clustering: `fdars.clustering.{dbscan_fd,kcfc_cluster,funfem_cluster,align_cluster_fd}`
- shapelet + GAK: `fdars.shapelet.{discover_shapelets,shapelet_transform_fit,shapelet_transform,shapelet_classifier_fit,shapelet_distance}`, `fdars.metric.{gak,gak_gram_matrix,gak_gram_train,gak_gram_predict,sigma_gak}`

### Integration Points
- 7 new `docs/<section>/*.md` pages; `mkdocs.yml` nav edits; 7 inline SVGs (in the pages or docs/assets/diagrams); `docs/advisor/aspects.md` update; `Cargo.toml` + `pyproject.toml` version bump.

</code_context>

<specifics>
## Specific Ideas

- Each worked example must import the shipped binding and produce a small, deterministic result that emits `FDARS_FENCE_OK` — use tiny fixtures so `--strict` stays within budget.
- Diagrams must be method-accurate: depict what each method actually does (e.g. fts forecast = FTSM mean + basis extrapolation; frechet = metric-space barycenter; shapelet = discriminative subsequence). The human review gate exists specifically to catch method-inaccuracy.
- Confirm the exact `FDARS_FENCE_OK` mechanism + the mkdocs-exec setup by reading an existing worked-example page before authoring.
- `mkdocs build --strict` is ~19-25+ min with executed fences — run it ONCE at the close, not per-page (use DOCS_FAST during iteration).

</specifics>

<deferred>
## Deferred Ideas

- (None — this is the closing phase; all deferred items were logged in earlier phases and remain in STATE Deferred Items.)

</deferred>
