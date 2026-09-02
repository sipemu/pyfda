# Phase 59: Documentation & Docs Gate - Context

**Gathered:** 2026-09-01
**Status:** Ready for planning
**Mode:** Auto-generated (smart-discuss) — docs phase; content is the shipped `fdars.sklearn` layer + established v7.0 docs/STYLE_SPEC patterns.

<domain>
## Phase Boundary

Publish a method-accurate "scikit-learn API" docs section documenting the `fdars.sklearn` estimator layer built in Phases 55–58, gated by a green whole-site `mkdocs build --strict` and a blocking human diagram review, then bump the package version at close. Delivers DOCS-01, DOCS-02, DOCS-03, REL-01.

MUST run sequentially on `main`, NOT in worktrees (standing rule: doc-build fences hardcode the main-tree `.venv/bin/mkdocs`; `use_worktrees: false`). Docs build is ~19–25 min with executed fences — keep new fence data small, offline only (no network).

Out of scope: any code change to `python/fdars/sklearn/` beyond doc-driven fixes; fdars-core bump; advisor changes.
</domain>

<decisions>
## Implementation Decisions

### DOCS-01 — new "scikit-learn API" nav section (in `mkdocs.yml`)
- A new top-level nav section "scikit-learn API" with:
  - `docs/sklearn/index.md` — concept/overview: what the layer is, the plain-`(n_obs, n_points)`-ndarray + `argvals`-constructor-param contract, `[sklearn]` install, the full-`check_estimator`-compliance guarantee, and how it fits into `Pipeline`/`GridSearchCV`.
  - Per-family reference pages: transformers, regressors, classifiers, clusterers, outlier-detectors (list the wrapped estimators + their fdars source + key params).
  - A **coverage / EXCLUDE page** — the published list: all 28 wrapped estimators (family, sklearn mixin, fdars source) + the genuinely-structural EXCLUDED_METHODS (pace_fpca, cluster_optim, concurrent_regression, registration, inference tests, SPM, non-Gaussian GLM, fosr, elastic-multinomial-native) with their reason + "still available in the functional API". Derive from `python/fdars/sklearn/_coverage.py` (TRIAGE_VERDICTS + EXCLUDED_METHODS) so it stays truthful.
- Follow the existing `docs/advisor/` section shape (index + per-topic pages) and nav idiom.

### DOCS-02 — offline worked examples + `--strict` gate
- Offline `FDARS_FENCE_OK`-emitting worked examples via markdown-exec (`PYTHONPATH=scripts`, `from docs_fig import ...`), including:
  - a **Pipeline example** (e.g. `Pipeline([Imputer(), BSplineSmoother(), FPCATransformer(), FPC classifier])`), and
  - a **GridSearchCV example** (param_grid over pipeline-stage hyperparameters).
- Keep fence datasets SMALL (build time). No network / no LLM in any fence (the sklearn layer is pure compute — fine offline; `.venv` has scikit-learn 1.8).
- Whole-site `mkdocs build --strict` must be GREEN offline (run via `.venv/bin/mkdocs build --strict`).

### DOCS-03 — hand-authored SVG(s) + blocking human review
- At least one method-accurate hand-authored inline SVG (layer architecture / data flow: `(n_obs, n_points)` ndarray → transformer(s) → FPC scores → predictor, within a sklearn Pipeline). Meet the v7.0 STYLE_SPEC (`docs/assets/diagrams/STYLE_SPEC.md`: viewBox, the five canonical CSS classes, `role="img"` + `aria-label`) and SVGO-idempotence.
- **Blocking human diagram method-accuracy review before close** (the standing hypograph/epigraph lesson) — this is an `autonomous: false` task: the phase halts for human validation of the rendered diagram(s) on the built site.

### Method-accuracy honesty (important)
- The outlier-detector docs MUST be honest about scoring: `MagnitudeShapeDetector` uses a method-faithful MS-plot score (magnitude/shape outlyingness); the other five detectors (LRT, outliergram, TVDMSS, MUOD, depthgram) rank by a subset-invariant modified-band-depth **surrogate** in the sklearn layer, with their true batch-relative methods remaining in `fdars.outliers`. Do not overclaim.
- Note the classifier/regressor reconstructions where relevant (LDA/QDA/KNN/DD/ElasticMultinomial predict via stored FPC scores; GLM = Gaussian FPC-OLS).

### REL-01 — version bump at close
- Bump package version 0.8.0 → 0.9.0 (`Cargo.toml` + `pyproject.toml`); document the `[sklearn]` extra in packaging/README as appropriate. (A semver `vX.Y.Z` tag triggers PyPI publish — tagging is the user's call at ship, not this phase.)

### Claude's Discretion
Exact page split (one combined reference page vs five), which estimators get worked examples, and the diagram's precise composition are at Claude's discretion, guided by STYLE_SPEC, the `docs/advisor/` precedent, and the shipped code.
</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `docs/advisor/` — closest structural precedent (index + per-topic pages, concept + reference + examples).
- `docs/assets/diagrams/STYLE_SPEC.md` — the SVG style contract; `docs/assets/diagrams/*.svg` — existing hand-authored diagrams to match.
- `scripts/docs_fig.py` + markdown-exec (`mkdocs.yml`) — the offline live-fence mechanism (`PYTHONPATH=scripts`); `docs/learn/smoothing.md` + `docs/represent/interpolation.md` show the `FDARS_FENCE_OK` fence idiom.
- `python/fdars/sklearn/_coverage.py` — source of truth for the coverage/EXCLUDE page (TRIAGE_VERDICTS 28×PASS + EXCLUDED_METHODS).
- `.venv/bin/mkdocs` — the build tool (sklearn 1.8 installed, so sklearn fences execute).
- `mkdocs.yml` nav — add the new section.

### Established Patterns
- Docs phases run sequentially on `main`, no worktrees; ~20-min whole-site build; offline fences only.
- v7.0 SVG standard + SVGO idempotence + blocking human diagram review.
- `FDARS_FENCE_OK` sentinel proves a fence executed offline.

### Integration Points
- `docs/sklearn/` (new pages), `mkdocs.yml` (nav), `docs/assets/diagrams/` (new SVG), `Cargo.toml` + `pyproject.toml` (version bump). No change to `python/fdars/sklearn/` source (unless a doc-example reveals a bug).
</code_context>

<specifics>
## Specific Ideas
- Coverage/EXCLUDE page derives from `_coverage.py` so it can't drift from reality.
- Worked examples reuse the small synthetic datasets from `tests/sklearn/test_predictive_pipeline.py` / `test_interop.py` patterns to keep the build fast.
- Hard constraints: offline build (no network/LLM in fences); method-accurate diagrams; `--strict` green; blocking human review before close.
</specifics>

<deferred>
## Deferred Ideas
- `set_output(transform="pandas")` docs (FUT-01); sklearn 1.7+ once Python 3.9 dropped (FUT-03).
- PyPI publish tag (user's action at ship, post-milestone).
</deferred>
