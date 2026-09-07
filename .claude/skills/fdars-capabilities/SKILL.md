---
name: fdars-capabilities
description: >
  Discover the full fdars functional data analysis capability surface:
  list every public submodule and callable, get the call signature and
  one-line purpose, and find the right method for a task.
  Use this skill to answer: "what can fdars do?", "which method for X?",
  "how do I call Y?", "list the fdars clustering/depth/regression/...
  methods", or "browse the fdars API".
  Trigger: whenever the user asks what fdars can do, wants to find a
  method by task description, needs a method's signature or purpose, or
  wants to explore any part of the fdars capability surface.
  Do NOT use this skill for parameter tuning, diagnostics, or before/after
  comparison — use fdars-advisor for those tasks.
compatibility: >
  Requires fdars installed (Python 3.9+).  No API key required.
  pip install fdars
  The capability map is available as docs/llms.txt at
  https://sipemu.github.io/pyfda/llms.txt or via the fdars_list_capabilities
  MCP tool (Python 3.10+, mcp>=2.0.0).
allowed-tools: Bash Read WebFetch
---

## Capability Map

The full fdars API digest is at:

- **Agent URL:** https://sipemu.github.io/pyfda/llms.txt
- **MCP tool (Python 3.10+):** `fdars_list_capabilities(module="depth")`
- **Offline:** `python -c "import json, importlib.resources as r; print(r.files('fdars').joinpath('_capability_map.json').read_text())"`

## Module Overview

| Module | Callables | Purpose | Example |
|--------|-----------|---------|---------|
| `Fdata` (class) | 28 | OOP container: bundle data matrix, grid, IDs, metadata; method wrappers for all core ops | `fd = fdars.Fdata(data, argvals)` |
| `fdars.fdata` | 15 | Low-level functional data ops: center, mean, deriv, norm, integrate (1-D and 2-D variants) | `fdars.fdata.mean_1d(data)` |
| `fdars.depth` | 18 | Depth measures: Fraiman-Muniz, band, modal, random-projection (1-D and 2-D) | `fdars.depth.fraiman_muniz_1d(data, ref)` |
| `fdars.alignment` | 68 | Elastic alignment: SRSF, Karcher mean, elastic FPCA, pairwise/group registration | `fdars.alignment.align_to_target(data, target)` |
| `fdars.basis` | 16 | Basis representations: B-spline, Fourier, FPCA; CV for nbasis selection | `fdars.basis.basis_nbasis_cv(data, argvals)` |
| `fdars.smoothing` | 10 | Kernel and P-spline smoothing; LOO-CV bandwidth/lambda selection | `fdars.smoothing.cv_smoother(data, argvals, bandwidth)` |
| `fdars.clustering` | 11 | Functional clustering: k-means, k-medoids, elastic-alignment clustering, DBSCAN, FunFEM | `fdars.clustering.align_cluster_fd(data, argvals, k)` |
| `fdars.regression` | 29 | Functional regression: scalar-on-function LM, bootstrap CI, cross-validation, concurrent | `fdars.regression.fregre_lm(data, y, argvals)` |
| `fdars.classification` | 9 | Functional classifiers: elastic multinomial, centroid-based (1-D and 2-D) | `fdars.classification.elastic_multinomial(data, labels)` |
| `fdars.outliers` | 8 | Functional outlier detection: depthgram, magnitude-shape plot, bagplot | `fdars.outliers.depthgram(data, argvals)` |
| `fdars.inference` | 11 | Functional hypothesis tests: permutation F-test, ANOVA, two-sample, pointwise | `fdars.inference.f_perm_test(data1, data2, argvals)` |
| `fdars.spm` | 23 | Statistical process monitoring: Hotelling T², EWMA, MEWMA, ARL, phase-I/II charts | `fdars.spm.arl0_ewma_t2(lambda_, ucl, p)` |
| `fdars.seasonal` | 18 | Seasonal/periodic FDA: peak timing, amplitude, phase variability analysis | `fdars.seasonal.analyze_peak_timing(data, argvals)` |
| `fdars.metric` | 26 | Distance and kernel matrices: DTW, elastic, GAK, Lp; cross and gram matrices | `fdars.metric.dtw_cross_1d(data, ref)` |
| `fdars.represent` | 4 | Re-grid and interpolate functional data (linear/cubic/policy-aware) | `fdars.represent.fdata_interpolate_with_policy(data, argvals, new_argvals)` |
| `fdars.smoothing` | 10 | (see above) | |
| `fdars.scalar_on_function` | 5 | Scalar-on-function regression: FAM, GSAM, GKAM, model selection, GSAM-CV | `fdars.scalar_on_function.fam(data, y, argvals)` |
| `fdars.frechet` | 4 | Fréchet regression and ANOVA for metric-space responses (Wasserstein, spherical) | `fdars.frechet.frechet_anova(data_list, groups)` |
| `fdars.density_fda` | 5 | Density FDA via LQD transform: forward/inverse transform, Wasserstein barycenter | `fdars.density_fda.inverse_lqd(psi, t_grid, target_argvals)` |
| `fdars.fts` | 13 | Functional time series: DPCA, DPCA forecast, long-run covariance, ACF/PACF, AR models | `fdars.fts.dpca(data, argvals, n_comp)` |
| `fdars.multi_fdata` | 2 | Multi-domain functional data: container and from-components builder | `fdars.multi_fdata.multi_fdata_from_components(data_list, argvals_list)` |
| `fdars.pace_fpca` | 3 | PACE FPCA for irregularly observed functional data | `fdars.pace_fpca.irreg_fdata_from_lists(obs_list, argvals_list)` |
| `fdars.famm` | 3 | Functional Linear Mixed Models (FLMM) via REML-EM | `fdars.famm.dense_flmm(data, argvals, group)` |
| `fdars.shapelet` | 7 | Shapelet discovery and distance for functional data classification | `fdars.shapelet.discover_shapelets(data, labels)` |
| `fdars.conformal` | 7 | Conformal prediction: classification sets and tolerance/prediction bands | `fdars.conformal.conformal_classif(data, labels, alpha)` |
| `fdars.tolerance` | 9 | Tolerance and prediction bands: conformal, depth-based, simultaneous | `fdars.tolerance.conformal_prediction_band(data, argvals, alpha)` |
| `fdars.simulation` | 8 | Simulation utilities: add noise, generate curves, random functional data | `fdars.simulation.add_error_curve(data, sigma)` |
| `fdars.explain` | 46 | Explainability: anchor explanations, LIME, functional feature importance | `fdars.explain.anchor_explanation(model, data, instance)` |
| `fdars.scoring` | 5 | Functional regression scoring: RMSE, MAE, R², functional explained variance | `fdars.scoring.functional_explained_variance(y_true, y_pred, argvals)` |
| `fdars.covariance` | 14 | Covariance kernels: Gaussian, Matern, Brownian, additive; kernel matrix builders | `fdars.covariance.kernel_gaussian(sigma, length_scale)` |
| `fdars.metrics` | 5 | Prediction metrics (MAE, MSE, RMSE, R², MedAE) for scalar regression targets | `fdars.metrics.pred_mae(y_true, y_pred)` |
| `fdars.datasets` | 7 | Example datasets: Canadian weather, phoneme, Berkeley growth, and more | `fdars.datasets.load_canadian_weather()` |

## How to Find a Method

```bash
# List all methods in a module
python -c "import fdars; print([n for n in dir(fdars.depth) if not n.startswith('_')])"

# Or via MCP tool (requires mcp>=2.0.0, Python 3.10+):
# fdars_list_capabilities(module="depth")

# Browse the full API digest (409 public module callables + 28 Fdata class methods = 437 total):
# https://sipemu.github.io/pyfda/llms.txt
```

## Skill Boundary

This skill covers **capability discovery only**: what fdars can do, which method
to use for a task, and how to call it.

For **parameter tuning, grounded diagnostics, and before/after comparisons**
(e.g., smoothing basis selection, cluster k guidance, FPCA component count,
alignment lambda, depth ranking thresholds), use the `fdars-advisor` skill instead.

## Scientific Provenance Protocol

When asked about the paper origins, citations, or cross-language implementations
of an fdars method, use this protocol.

### Step 1: Look up via `fdars_method_references`

Three equivalent surfaces (use whichever is available):

```bash
# MCP tool (requires fdars[mcp] installed, Python 3.10+):
# fdars_method_references("depth.fraiman_muniz_1d")

# Offline (any Python 3.9+, no compiled install required):
# python -c "
# import json, importlib.resources as r
# ref = json.loads(r.files('fdars').joinpath('_references_map.json').read_text())
# idx = ref['callable_index'].get('depth.fraiman_muniz_1d', [])
# papers = [ref['papers'][k] for k in idx]
# import pprint; pprint.pprint(papers)
# "

# Published docs surfaces (no install):
# https://sipemu.github.io/pyfda/references/   (full references page)
# https://sipemu.github.io/pyfda/llms.txt      (llms.txt provenance section)
```

### Step 2: Route by return value

**Path A — `curated: true` hit**
The return payload includes `"curated": True` and at least one paper with
`"curated": True`.

- Use the paper data **verbatim**: authors, year, DOI, cross-language implementations.
- Present as: `"According to fdars curated provenance: [Authors] ([Year]), [Title]. doi:[DOI]"`
- Do **not** paraphrase, embellish, or add citations absent from the payload.

**Path B — `curated: false` hit (all backing papers have `curated: false`)**
The callable is indexed in `callable_index` but all backing papers are pending
DOI-landing-page verification.

- State the candidate paper(s) from the payload WITH an explicit caveat that
  they are pending Phase-84 human verification.
- Attach `grounded: false` to **each citation** in any structured output you produce:
  `{ "grounded": false, "source": "pending_verification" }`
- Do **not** present as confirmed curated provenance.

**Path C — `NO_CURATED_ENTRY` sentinel**
The callable exists in fdars but has no entry in `callable_index`.

- You MAY synthesize a candidate reference from training knowledge.
- You **MUST** flag every synthesized citation structurally:
  `{ "grounded": false, "source": "synthesis", "review_required": true }`
- State explicitly: `"No curated entry exists for [callable]. The following is
  synthesized and ungrounded — treat as a starting point for manual verification only."`
- **Never omit the `grounded: false` flag** in structured output.
- **Never present synthesized provenance as matching the curated surface.**

### Non-duplication with `fdars-advisor`

This provenance protocol covers **citation lookup and cross-language implementation
pointers only**.

For **parameter tuning, method-selection diagnostics, and before/after comparisons**
(e.g., smoothing basis selection, cluster k guidance, FPCA component count,
alignment lambda, depth ranking thresholds), use the `fdars-advisor` skill —
do **not** route those queries here.

### Walkthrough

**Walkthrough A — Curated Hit: `depth.fraiman_muniz_1d` (Path A)**

```
User: What paper is depth.fraiman_muniz_1d based on?

Step 1: call fdars_method_references("depth.fraiman_muniz_1d")

Return:
{
  "method": "depth.fraiman_muniz_1d",
  "curated": True,
  "papers": [
    {
      "paper_key": "fraiman_muniz_2001",
      "title": "Trimmed means for functional data",
      "authors": ["Fraiman, R.", "Muniz, G."],
      "year": 2001,
      "doi": "10.1007/BF02595706",
      "url": "https://link.springer.com/article/10.1007/BF02595706",
      "type": "journal",
      "cross_language": {
        "R": {"package": "fda.usc", "function": "depth.FM", "confidence": "high"},
        "Python": {"package": "scikit-fda", "function": "fraiman_muniz_depth", "confidence": "high"}
      },
      "curated": True
    }
  ],
  "coverage": "28/437",
  "version": "..."
}

Step 2: curated: True → Path A
Response: "According to fdars curated provenance: Fraiman, R. and Muniz, G. (2001),
'Trimmed means for functional data'. doi:10.1007/BF02595706.
Cross-language: R fda.usc::depth.FM (high confidence),
Python scikit-fda.fraiman_muniz_depth (high confidence)."
```

**Walkthrough B — NO_CURATED_ENTRY Sentinel: `explain.shap_values` (Path C)**

`explain.shap_values` is absent from `callable_index` — confirmed by the Phase-82
guard test `test_references_tool_llm_free_boundary` in
`tests/test_guard_sync_version_independent.py`.

```
User: What paper is explain.shap_values based on?

Step 1: call fdars_method_references("explain.shap_values")

Return:
{
  "method": "explain.shap_values",
  "curated": False,
  "sentinel": "NO_CURATED_ENTRY",
  "message": "No curated reference entry for 'explain.shap_values'. ...",
  "version": "..."
}

Step 2: NO_CURATED_ENTRY sentinel → Path C
Response: "No curated entry exists for explain.shap_values in the fdars provenance
surface. The following is synthesized from training knowledge and ungrounded:

  { "grounded": false, "source": "synthesis", "review_required": true,
    "candidate": "Lundberg & Lee (2017), A Unified Approach to Interpreting
    Model Predictions, NeurIPS 2017." }

Treat this as a starting point for manual verification only — it has NOT been
confirmed against fdars-core source code or DOI landing pages."
```

**Walkthrough C — `curated: false` Hit (Pending): `clustering.align_cluster_fd` (Path B)**

`clustering.align_cluster_fd` is indexed in `callable_index` but its sole backing
paper is `_uncurated_align_cluster_fd_2026-09` with `curated: false`.

```
User: What paper backs clustering.align_cluster_fd?

Step 1: call fdars_method_references("clustering.align_cluster_fd")

Return:
{
  "method": "clustering.align_cluster_fd",
  "curated": False,
  "papers": [
    {
      "paper_key": "_uncurated_align_cluster_fd_2026-09",
      "title": "",
      "authors": [],
      "year": null,
      "curated": False
    }
  ],
  "coverage": "28/437",
  "version": "..."
}

Step 2: curated: False (all papers curated:false) → Path B
Response: "clustering.align_cluster_fd has a candidate attribution pending
Phase-84 human DOI-landing-page verification. Attribution is contested —
no single curated primary paper confirmed.

  { "grounded": false, "source": "pending_verification" }

Do not treat this as confirmed curated provenance."
```

## Optional Extras

- **`plot` module** — matplotlib-based plotting helpers (`plot_fdata`, `plot_depth`, etc.);
  install with `pip install "fdars[plot]"` (matplotlib optional dependency).
  Not included in the capability map (optional dependency).
- **`advisor` module** — LLM-powered advisor loop; not included in the capability map
  (see the `fdars-advisor` skill for tuning and diagnostics workflows).
