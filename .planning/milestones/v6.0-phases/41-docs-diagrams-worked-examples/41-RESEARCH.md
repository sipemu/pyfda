# Phase 41: Docs — Diagrams & Worked Examples - Research

**Researched:** 2026-08-21
**Domain:** MkDocs documentation authoring — hand-authored inline SVG, markdown-exec fences, fdars v6.0 API
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**DOCS-08 — Regression**
New/updated Regression page(s) covering `fdars.regression.concurrent_regression` + `functional_glm` — method-accurate hand-authored inline SVG(s) + a runnable offline `FDARS_FENCE_OK` worked example (small/synthetic or subsampled data to protect the build); documents the Gamma inverse-link (1/μ) + non-R-comparable AIC caveats surfaced in Phase 37. Wire into the Regression nav section. Exact page split — new `concurrent-regression.md`/`functional-glm.md` vs folding into existing regression pages — decided at plan time by the established nav pattern.

**DOCS-09 — FPCA & Classification**
PACE-FPCA page (likely `docs/represent/pace-fpca.md`) — method-accurate SVG showing irregular/sparse observations + recovered eigenfunctions; executed fence using SMALL inline synthetic sparse data (n ≤ 20) built via `fdars.pace_fpca.irreg_fdata_from_lists` → `fdars.pace_fpca.pace_fpca`. elastic-multinomial coverage (fold into `docs/regression/classification.md` or a page) — worked example on phoneme.csv subsampled to 3 classes, m ≤ 64 for fence speed.

**DOCS-10 — Depth / Outliers / Interval Inference**
Fold the 9 new `functional_depth` methods into the existing depth page (`docs/represent/depth-functions.md`) with a short method table + a representative fence. Functional-outliers coverage (extend `docs/analyze/outlier-detection.md` or a new page) for the 4 detectors — method-accurate SVG + fence. Interval-wise-inference page (likely `docs/inference/interval-inference.md`) for `itp_one_pop`/`itp_two_pop`/`itp_flm` — SVG showing closure-adjusted p-value intervals (CORRECT closure direction) + fence.

**DOCS-11 — Advisor + nav + build + review**
Update the advisor `aspects.md` for the extended `outliers`/`regression` diagnostics (Phase 40). All new pages wired into `mkdocs.yml` nav; whole-site `mkdocs build --strict` passes offline (exit 0); every new SVG is SVGO-idempotent and determinism-clean. BLOCKING human diagram method-accuracy review (rsvg-convert PNG check: depth asymmetry, PACE irregular observations, ITP closure direction) before the milestone closes — the orchestrator PAUSES here for the user.

**Method-accuracy + build constraints (locked)**
Diagrams stay HAND-AUTHORED inline SVG conforming to `STYLE_SPEC.md` (viewBox, inline `<style>` classes, system-ui, role="img"+aria-label); no programmatic generation. Fences execute REAL fdars compute offline and MUST emit `FDARS_FENCE_OK`; keep fence data tiny (PACE/ITP synthetic n ≤ 20) so the ~19-min build doesn't blow out (target < ~25 min). Build recipe: venv + `PYTHONPATH=scripts` + `DOCS_FAST` for iteration; the full `mkdocs build --strict` (DOCS_FAST unset) is the source-of-truth gate. Use `rsvg-convert` to render new SVGs to PNG for the human review.

### Claude's Discretion
Exact page split / filenames, diagram compositions (within STYLE_SPEC), and fence datasets are at Claude's discretion, grounded in the existing docs pages and the shipped v6.0 API. The human diagram review is NOT at Claude's discretion — it is a blocking user gate.

### Deferred Ideas (OUT OF SCOPE)
- `fdars.plot.plot_functional_boxplot()` helper (PLOT-01) — future milestone, not docs.
- Dedicated PACE/multinomial advisor aspects (PACE-ADV/MULTINOM-ADV) — deferred at Phase 40.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| DOCS-08 | Regression docs for `concurrent_regression` + `functional_glm`, Gamma inverse-link + AIC caveats, SVG + fence | API signatures verified from `src/regression_mod.rs`; page structure from v5.0 precedents |
| DOCS-09 | PACE-FPCA page + elastic-multinomial extension to classification.md, method-accurate SVGs, fences on synthetic/phoneme data | API signatures verified from `src/pace_fpca_mod.rs` and `src/classification_mod.rs` |
| DOCS-10 | 9 new depth methods folded into depth-functions.md, 4 outlier detectors extended in outlier-detection.md, ITP interval-inference new page | API signatures verified from `src/depth_mod.rs`, `src/outliers_mod.rs`, `src/inference_mod.rs` |
| DOCS-11 | `advisor/aspects.md` update for extended outliers/regression diagnostics; nav wiring; `mkdocs build --strict` gate; SVGO idempotence; blocking human review | `advisor/aspects.md` read; `mkdocs.yml` nav structure verified; `STYLE_SPEC.md` and `svgo.config.mjs` confirmed present |
</phase_requirements>

---

## Summary

Phase 41 documents the v6.0 bindings (Phases 37–40) to the project's method-accurate standard. The work is purely documentation: no source changes. Four requirements map to five file-change groups:

1. **DOCS-08**: Two new pages under `docs/regression/` for `concurrent_regression` and `functional_glm`, each with a hand-authored SVG and an executed fence.
2. **DOCS-09**: One new page `docs/represent/pace-fpca.md` and an extension to `docs/regression/classification.md` for `elastic_multinomial`.
3. **DOCS-10**: Extensions to `docs/represent/depth-functions.md` (9 new depth methods), `docs/analyze/outlier-detection.md` (4 new outlier detectors), and a new `docs/inference/interval-inference.md` page.
4. **DOCS-11**: One update to `docs/advisor/aspects.md`, all nav wiring in `mkdocs.yml`, the `mkdocs build --strict` gate, SVGO idempotence on every new SVG, and a blocking human diagram review.

The direct pattern precedent is v5.0 Phase 35 (plans 35-01 through 35-04): TRACER-FIRST task 1 proves the toolchain end-to-end, subsequent tasks expand. Every new page follows the exact outlier-detection/functional-inference page template: H1, KaTeX theory, `![title](../assets/diagrams/NAME.svg){ .fdars-diagram }`, `python exec="1" html="1" source="above"` fence ending with `print("FDARS_FENCE_OK")`, parameter table, Returns table, References section.

**Primary recommendation:** Split into 4 plans matching the 4 requirements (DOCS-08, DOCS-09, DOCS-10, DOCS-11). Each plan is a self-contained wave with its own per-page strict build verification gate. DOCS-11 is the final plan and must run last (nav + global build + advisor update).

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| SVG diagrams | Static authored assets | — | Hand-authored markup; no server-side rendering |
| Executed fences | Build-time Python compute | `fdars` compiled extension | `markdown-exec` runs fences during `mkdocs build` |
| Nav wiring | `mkdocs.yml` config | — | YAML-driven; planner edits this file |
| Advisor aspects.md | Pure Python docs | `fdars.advisor` module | Update text + fence only; no src changes |

---

## Page Plan (per requirement)

### DOCS-08: Regression (2 new pages)

**Recommendation: 2 separate new pages** — the nav pattern in `mkdocs.yml` already has 12 entries under Regression, and both `concurrent_regression` and `functional_glm` are conceptually distinct (varying-coefficient model vs exponential-family GLM). Folding both into a single page would make it as long as the existing `scalar-on-function.md`.

| Action | File | Nav placement |
|--------|------|---------------|
| CREATE | `docs/regression/concurrent-regression.md` | After `Robust Regression` in Regression nav section |
| CREATE | `docs/regression/functional-glm.md` | After `concurrent-regression.md` in Regression nav section |

**`mkdocs.yml` nav additions (under `- Regression:`):**
```yaml
    - Concurrent Regression: regression/concurrent-regression.md
    - Functional GLM: regression/functional-glm.md
```
Insert after the existing `- Robust Regression: regression/robust-regression.md` entry. [VERIFIED: mkdocs.yml:127]

### DOCS-09: FPCA & Classification (1 new page + 1 extension)

| Action | File | Nav placement |
|--------|------|---------------|
| CREATE | `docs/represent/pace-fpca.md` | After `Elastic FPCA` in Represent nav section |
| EXTEND | `docs/regression/classification.md` | No nav change (entry already exists) |

**`mkdocs.yml` nav addition (under `- Represent:`):**
```yaml
    - PACE FPCA: represent/pace-fpca.md
```
Insert after the existing `- Elastic FPCA: represent/elastic-fpca.md` entry. [VERIFIED: mkdocs.yml:95-96]

The `elastic_multinomial` section is appended to `docs/regression/classification.md` as a new `## Elastic Multinomial Classification` section with its own SVG reference, theory, parameter table, and fence.

### DOCS-10: Depth / Outliers / Interval Inference (2 extensions + 1 new page)

| Action | File | Nav placement |
|--------|------|---------------|
| EXTEND | `docs/represent/depth-functions.md` | No nav change |
| EXTEND | `docs/analyze/outlier-detection.md` | No nav change |
| CREATE | `docs/inference/interval-inference.md` | After `Functional Inference` in Inference nav section |

**`mkdocs.yml` nav change (under `- Inference:`):**
```yaml
  - Inference:
    - Functional Inference: inference/functional-inference.md
    - Interval-wise Inference: inference/interval-inference.md
```
Convert the current single-item Inference section (line 133) to a two-item section with the new page appended. [VERIFIED: mkdocs.yml:132-133]

### DOCS-11: Advisor + build + nav + review (1 file update, no nav change)

| Action | File | Nav change |
|--------|------|------------|
| UPDATE | `docs/advisor/aspects.md` | None |

The `advisor/aspects.md` is already at `advisor/aspects.md` in the nav (`- Per-Aspect Coverage: advisor/aspects.md`). [VERIFIED: mkdocs.yml:151]

---

## Verified API Signatures

All signatures read directly from shipped `src/*.rs` files this session.

### `concurrent_regression` [VERIFIED: src/regression_mod.rs:1035-1059]

```python
# Module: fdars.regression
concurrent_regression(
    predictors,       # list[np.ndarray] — each shape (n, m); list of p predictor matrices
    response,         # np.ndarray (n, m) — functional response
    argvals=None,     # np.ndarray (m,) or None → uniform [0,1] grid
    bandwidth=0.2,    # float; kernel bandwidth (must be > 0)
    kernel="gaussian" # str: "gaussian", "epanechnikov", or "tricube"
)
# Returns dict: beta_curve (p, m), intercept (m,), fitted (n, m), residuals (n, m), argvals (m,)
# CRITICAL: beta_curve rows index PREDICTORS (p), NOT observations (n)
```

### `functional_glm` [VERIFIED: src/regression_mod.rs:1166-1192]

```python
# Module: fdars.regression
functional_glm(
    data,                    # np.ndarray (n, m)
    response,                # np.ndarray (n,) scalar
    family="gaussian",       # str: "gaussian", "binomial", "poisson", "gamma"
    n_comp=3,                # int
    scalar_covariates=None,  # np.ndarray (n, q) or None
    max_iter=25,             # int
    tol=1e-6                 # float
)
# Returns dict: intercept, beta_t (m,), beta_se (m,), gamma (q,), fitted_values (n,),
#               linear_predictors (n,), ncomp, coefficients, std_errors,
#               log_likelihood, deviance, iterations, aic, bic, family
# DOCS CAVEAT: Gamma uses inverse canonical link g(μ)=1/μ — NOT log-link (unlike R default)
# DOCS CAVEAT: functional_glm AIC magnitude is NOT comparable to R glm() AIC
```

### `irreg_fdata_from_lists` + `pace_fpca` [VERIFIED: src/pace_fpca_mod.rs:91-153, 219-240]

```python
# Module: fdars.pace_fpca
handle = irreg_fdata_from_lists(
    argvals_list,  # list of 1-D arrays — one per curve (ragged grids)
    values_list    # list of 1-D arrays — one per curve, same length as argvals entry
)
# Returns: PyIrregFdata opaque handle
# Raises ValueError: if a 2-D numpy array is passed, lengths mismatch, or per-curve mismatch

pace_fpca(
    data,             # PyIrregFdata handle from irreg_fdata_from_lists
    ncomp=3,          # int
    bandwidth=0.1,    # float; use >= 0.15 for [0,1] data with few points
    sigma2=0.01,      # float; measurement error variance
    work_grid=None,   # list[float] or None → 51 uniform pts on [0, 1]
    alpha=0.05        # float; confidence level for bands
)
# Returns dict (10 keys): mean (m,), eigenvalues (ncomp,), eigenfunctions (m, ncomp),
#   scores (n, ncomp), fitted (n, m), fitted_lower (n, m), fitted_upper (n, m),
#   argvals (m,), sigma2 (float), ncomp (int — ACTUAL count, may be < requested)
# NOTE: eigenfunctions is (m, ncomp) — column k is the k-th eigenfunction
```

### `elastic_multinomial` [VERIFIED: src/classification_mod.rs:330-358]

```python
# Module: fdars.classification
elastic_multinomial(
    data,           # np.ndarray (n, m)
    labels,         # np.ndarray (n,) dtype int64 — 0-indexed contiguous (0..K)
    argvals,        # np.ndarray (m,)
    ncomp_beta=10,  # int; B-spline basis functions per OvR model
    lambda_=0.1,    # float; roughness penalty
    max_iter=100,   # int
    tol=1e-4        # float
)
# Returns dict: n_classes (int), classes (K,), train_probabilities (n, K),
#               predicted_classes (n,), train_accuracy (float)
# GUARD: labels must be non-negative 0-indexed; negative values raise ValueError
```

### `functional_depth` (extended) [VERIFIED: src/depth_mod.rs:518-531]

```python
# Module: fdars.depth
functional_depth(
    data,                    # np.ndarray (n, m)
    method="fraiman_muniz",  # str — 13 accepted values (see below)
    scale=True,              # bool; fraiman_muniz only
    nproj=50,                # int; random_projection only
    seed=None                # int|None; random_projection only (None → 0)
)
# Returns: np.ndarray (n,) of depth scores
# 13 accepted method strings (from src/depth_mod.rs:428-442):
# "fraiman_muniz", "band", "modified_band", "random_projection",
# "total_variation", "hypograph_index", "modified_hypograph_index",
# "epigraph_index", "half_region", "modified_half_region",
# "extremal", "extreme_rank_length", "l_infinity"
```

### Outlier detectors (new v6.0) [VERIFIED: src/outliers_mod.rs:211-495]

```python
# Module: fdars.outliers

tvdmss(data, emp_factor_mss=1.5, emp_factor_tvd=1.5, central_region_tvd=0.5)
# data: (n, m); no argvals param; no seed param
# Returns: magnitude_outliers (list[int]), shape_outliers (list[int]), tvd (n,), mss (n,)

muod(data, factor=1.5)
# data: (n, m); no argvals; no seed; requires n >= 3
# Returns: shape_outliers, magnitude_outliers, amplitude_outliers (all list[int]);
#          shape_index, magnitude_index, amplitude_index (all (n,))

sequential_transform_outliers(data, transforms, depth_method="modified_band", emp_factor=1.5)
# data: (n, m); transforms: list[str] — each must be one of "t0","t1","t2","d1","d2"
# Returns: per_transform_outliers (list[dict] each {transform:str, outliers:list[int]}),
#          union_outliers (list[int])
# NOTE: "depth_method" NOT "method"; accepts all 13 functional_depth method strings

depthgram(data, outliergram_factor=1.5, boxplot_factor=1.5)
# data: (n, m); no argvals; no seed; requires n >= 2
# Returns: mbd_mei_d, mei_mbd_d, mbd_mei_t, mei_mbd_t, mbd_mei_t2, mei_mbd_t2 (all (n,));
#          shape_outliers, magnitude_outliers (list[int]); mbd, mei (both (n,))
```

### ITP interval-inference functions [VERIFIED: src/inference_mod.rs:637-792]

```python
# Module: fdars.inference

itp_one_pop(data, argvals, mu0=None, basis_type="bspline", nbasis=5, n_perm=999, seed=None)
# data: (n, m); n >= 2; mu0: (m,) or None → zero function
# basis_type: "bspline" (default) or "fourier"
# Returns: adjusted_pvalues (n_basis,), raw_pvalues (n_basis,), basis_type (str),
#          n_basis (int — ACTUAL, may be < nbasis for bspline clamping), n_perm (int)

itp_two_pop(data_a, data_b, argvals, basis_type="bspline", nbasis=5, n_perm=999, seed=None)
# data_a: (n_a, m), data_b: (n_b, m); both n >= 2; same column count
# Returns: same 5-key dict as itp_one_pop

itp_flm(data, response, argvals, basis_type="bspline", nbasis=5, n_perm=999, seed=None)
# data: (n, m); response: (n,) scalar
# Returns: same 5-key dict as itp_one_pop
```

---

## Worked-Example Fence Blueprints

### DOCS-08: `concurrent_regression` fence

```python exec="1" html="1" source="above"
import numpy as np
from docs_fig import fig, render, fast
import fdars.regression as reg

rng = np.random.default_rng(0)
n, m = 20, 50
t = np.linspace(0, 1, m)
# Two synthetic predictor curves + a response
x1 = np.array([np.sin(2 * np.pi * t) + rng.normal(0, 0.1, m) for _ in range(n)])
x2 = np.array([np.cos(2 * np.pi * t) + rng.normal(0, 0.1, m) for _ in range(n)])
y  = x1 * np.sin(2 * np.pi * t) + x2 * 0.5 + rng.normal(0, 0.05, (n, m))

res = reg.concurrent_regression([x1, x2], y, t)
beta = np.asarray(res["beta_curve"])  # shape (2, m) — p=2 predictors

f, ax = fig(figsize=(8.0, 3.8))
ax.plot(t, beta[0], color="#3f51b5", lw=2.2, label="β₁(t) — sin predictor")
ax.plot(t, beta[1], color="#e8710a", lw=2.2, label="β₂(t) — cos predictor")
ax.set(title="Concurrent regression — estimated coefficient curves",
       xlabel="t", ylabel="β(t)")
ax.legend(fontsize=9)
print(render(f))
print(f"beta_curve shape: {beta.shape}  (p=2 predictors × m={m} grid points)")
print("FDARS_FENCE_OK")
```

Key points:
- `predictors` is `list[np.ndarray]` where each element is `(n, m)`, not a single 3-D array.
- `beta_curve` shape is `(p, m)` — row k is the k-th predictor's coefficient curve. Confusing `(p, m)` with `(n, m)` is the #1 transposition pitfall.
- `argvals` is positional third arg (optional); it is NOT a keyword-only arg.

### DOCS-08: `functional_glm` fence

```python exec="1" html="1" source="above"
import numpy as np
from docs_fig import fig, render
import fdars.regression as reg

rng = np.random.default_rng(1)
n, m = 30, 60
t = np.linspace(0, 1, m)
X = np.array([np.sin(2 * np.pi * t * (1 + 0.3 * rng.normal())) + rng.normal(0, 0.1, m)
              for _ in range(n)])
# Binary response (Binomial)
logit_true = X @ np.sin(2 * np.pi * t) / m
prob_true = 1 / (1 + np.exp(-3 * logit_true))
y = rng.binomial(1, prob_true).astype(float)

res = reg.functional_glm(X, y, family="binomial", n_comp=3)
beta_t = np.asarray(res["beta_t"])

f, ax = fig(figsize=(8.0, 3.6))
ax.plot(t, beta_t, color="#3f51b5", lw=2.2)
ax.set(title="Functional GLM (binomial) — coefficient function β(t)",
       xlabel="t", ylabel="β(t)")
print(render(f))
print(f"deviance={res['deviance']:.3f}  aic={res['aic']:.3f}  family={res['family']}")
print("FDARS_FENCE_OK")
```

### DOCS-09: `pace_fpca` fence (n ≤ 20, fully synthetic)

```python exec="1" html="1" source="above"
import numpy as np
from docs_fig import fig, render
import fdars.pace_fpca as pf

rng = np.random.default_rng(42)
n = 15  # sparse curves; each has only 5-8 observations
t_full = np.linspace(0, 1, 51)  # dense work grid for result

argvals_list = [np.sort(rng.uniform(0, 1, rng.integers(5, 9))) for _ in range(n)]
values_list  = [np.sin(2 * np.pi * av) + rng.normal(0, 0.15, len(av))
                for av in argvals_list]

handle = pf.irreg_fdata_from_lists(argvals_list, values_list)
res = pf.pace_fpca(handle, ncomp=2, bandwidth=0.2, sigma2=0.05)
ef = np.asarray(res["eigenfunctions"])   # shape (m, ncomp)
argvals_out = np.asarray(res["argvals"]) # work grid

f, (a0, a1) = fig(1, 2, figsize=(11.0, 3.8))
for i, (av, vl) in enumerate(zip(argvals_list, values_list)):
    a0.scatter(av, vl, s=18, color="#3f51b5", alpha=0.5)
a0.plot(argvals_out, np.asarray(res["mean"]), color="#e8710a", lw=2.2, label="PACE mean")
a0.set(title=f"Sparse irregular observations (n={n}, ragged grids)", xlabel="t")
a0.legend(fontsize=9)
a1.plot(argvals_out, ef[:, 0], color="#3f51b5", lw=2.2, label="PC 1")
a1.plot(argvals_out, ef[:, 1], color="#e8710a", lw=2.2, label="PC 2")
a1.set(title="PACE eigenfunctions recovered on work grid", xlabel="t")
a1.legend(fontsize=9)
print(render(f))
print(f"actual ncomp={res['ncomp']}  scores shape={np.asarray(res['scores']).shape}")
print("FDARS_FENCE_OK")
```

### DOCS-09: `elastic_multinomial` fence (phoneme, 3 classes, m ≤ 64)

```python exec="1" html="1" source="above"
import numpy as np
from docs_fig import fig, render
from docs_data import load_phoneme
import fdars.classification as clf

freq, X, meta = load_phoneme()
ph = meta["phoneme"].to_numpy()

# 3-class subset: "aa", "ao", "dcl" — the three most common in phoneme.csv
classes_3 = ["aa", "ao", "dcl"]
mask = np.isin(ph, classes_3)
X3 = X[mask]
y3 = np.array([classes_3.index(p) for p in ph[mask]], dtype=np.int64)
freq3 = freq

# Subsample columns to m ≤ 64 for fence speed
step = max(1, X3.shape[1] // 64)
X3 = X3[:, ::step]
freq3 = freq3[::step]

res = clf.elastic_multinomial(X3, y3, freq3, ncomp_beta=8, lambda_=0.1)
print(f"n_classes={res['n_classes']}  train_accuracy={res['train_accuracy']:.3f}")
print(f"train_probabilities shape: {np.asarray(res['train_probabilities']).shape}")
print("FDARS_FENCE_OK")
```

> **Dataset check**: phoneme.csv is in `docs/data/`. [VERIFIED: docs/data/ listing]. The three classes aa/ao/dcl are the most common in the standard ElemStatLearn phoneme dataset. Labels must be `dtype=int64` and 0-indexed contiguous.

### DOCS-10: `functional_depth` extension fence (new 9 methods)

```python exec="1" source="above"
import numpy as np
from fdars.simulation import simulate
from fdars.depth import functional_depth

rng = np.random.default_rng(7)
t = np.linspace(0, 1, 80)
X = np.asarray(simulate(n=25, argvals=t, n_basis=5, seed=7))
X[0] += 2.5  # magnitude outlier

new_methods = [
    "hypograph_index", "modified_hypograph_index", "epigraph_index",
    "half_region", "modified_half_region", "extremal",
    "extreme_rank_length", "l_infinity", "total_variation",
]
for method in new_methods:
    d = np.asarray(functional_depth(X, method=method))
    print(f"{method:<28s}  outlier_rank={np.argsort(d)[0]}  min={d.min():.3f}")
print("FDARS_FENCE_OK")
```

### DOCS-10: `tvdmss` + `muod` fence (outlier detectors)

```python exec="1" source="above"
import numpy as np
from fdars.simulation import simulate
from fdars.outliers import tvdmss, muod, sequential_transform_outliers, depthgram

rng = np.random.default_rng(3)
t = np.linspace(0, 1, 60)
X = np.asarray(simulate(n=30, argvals=t, n_basis=4, seed=3))
X[0] += 3.0   # magnitude outlier
X[1] = -X[1]  # shape outlier

r_tv = tvdmss(X)
r_mu = muod(X)
r_st = sequential_transform_outliers(X, transforms=["t0", "d1"])
r_dg = depthgram(X)

print(f"tvdmss    magnitude_outliers={r_tv['magnitude_outliers']}")
print(f"muod      magnitude_outliers={r_mu['magnitude_outliers']}")
print(f"seq_trans union_outliers={r_st['union_outliers']}")
print(f"depthgram magnitude_outliers={r_dg['magnitude_outliers']}")
print("FDARS_FENCE_OK")
```

> **Note on `tvdmss` and `muod` signatures**: neither takes `argvals` — the function operates purely on the data matrix. There is no `seed` parameter for either (both are deterministic). [VERIFIED: src/outliers_mod.rs:212-228, 289-298]

### DOCS-10: `itp_one_pop` fence (synthetic, n=20)

```python exec="1" source="above"
import numpy as np
from docs_fig import fig, render, fast
import fdars.inference as fi

rng = np.random.default_rng(5)
n, m = 20, 40
t = np.linspace(0, 1, m)
# Curves with mean shifted from zero in [0.4, 0.7] — ITP should flag those basis coefs
X = np.array([np.sin(2 * np.pi * t) + rng.normal(0, 0.3, m) for _ in range(n)])
X[:, 16:28] += 1.0  # local shift

n_perm = fast(199, 19)
res = fi.itp_one_pop(X, t, mu0=None, basis_type="bspline", nbasis=5,
                     n_perm=n_perm, seed=0)
adj_p = np.asarray(res["adjusted_pvalues"])
raw_p = np.asarray(res["raw_pvalues"])

print(f"n_basis (actual)={res['n_basis']}  n_perm={res['n_perm']}")
print(f"adjusted_pvalues={adj_p.round(3).tolist()}")
print(f"raw_pvalues     ={raw_p.round(3).tolist()}")
print("FDARS_FENCE_OK")
```

> **Critical ITP detail**: `n_basis` in the returned dict is the ACTUAL number of basis functions after bspline clamping — it may be less than the requested `nbasis`. Code must read `res["n_basis"]` to know the array length, not assume `nbasis`. The `adjusted_pvalues` array has `n_basis` elements, not `nbasis`.

---

## Architecture Patterns

### Page Structure Template (from v5.0 precedents)

Every new capability page follows this structure: [VERIFIED: docs/inference/functional-inference.md, docs/analyze/functional-boxplot.md]

```markdown
# Title

Short intro paragraph framing the method and its use case.

![Title matching aria-label](../assets/diagrams/NAME.svg){ .fdars-diagram }

## Theory

KaTeX equations. Parameter table. Returns table.

```python exec="1" html="1" source="above"
import numpy as np
from docs_fig import fig, render, fast
import fdars.MODULE as mod

# tiny data
...
print(render(f))
print("FDARS_FENCE_OK")
```

## References

1. Author (year). ...
```

### Fence execution pattern [VERIFIED: docs/inference/functional-inference.md:48-111]

```python
# Mandatory: exec="1" html="1" source="above" on the code fence
# Mandatory: last print() must be "FDARS_FENCE_OK" (exact string)
# DOCS_FAST pattern for expensive calls:
from docs_fig import fast
n_perm = fast(199, 19)    # 199 in full build, 19 in DOCS_FAST=1 mode
```

### SVG include pattern [VERIFIED: docs/analyze/functional-boxplot.md:9]

```markdown
![Descriptive alt text matching diagram title](../assets/diagrams/NAME.svg){ .fdars-diagram }
```

### SVGO idempotence check pattern [VERIFIED: docs/assets/diagrams/STYLE_SPEC.md]

```bash
# Check: svgo(svgo(svg)) == svgo(svg)
FILE=docs/assets/diagrams/NAME.svg
npx svgo@3.3.4 --config svgo.config.mjs --quiet --input "$FILE" --output /tmp/pass1.svg
npx svgo@3.3.4 --config svgo.config.mjs --quiet --input /tmp/pass1.svg --output /tmp/pass2.svg
diff /tmp/pass1.svg /tmp/pass2.svg && echo "IDEMPOTENT" || echo "FAILS"
```

---

## New SVG Diagrams to Hand-Author

Seven new SVGs are needed. All must conform to STYLE_SPEC.md: [VERIFIED: docs/assets/diagrams/STYLE_SPEC.md]

```
viewBox="0 0 720 300" (standard); 720x480 only if a tall two-row layout is required
fill="none" on root <svg>
role="img" aria-label="[descriptive text matching .ttl text]"
<style> block copied verbatim (5 classes: .ttl .sub .lab .sm .mono)
Structural colours: #1a1a2e (title), #6c757d (subtitle), #495057 (annotations),
                    #ced4da (borders/axes), #f8f9fa (panel fill), #fd7e14 (accent stroke)
Data-curve colours (in order): #3f51b5 #e8710a #198754 #dc3545 #6f42c1 #0dcaf0 #6c757d
```

### 1. `docs/assets/diagrams/concurrent-regression.svg`

**Method-accuracy requirement:** Must faithfully show that `concurrent_regression` estimates **one smooth coefficient curve per predictor** — i.e., p curves `β₁(t), …, β_p(t)` — NOT a single scalar coefficient per predictor. The key visual distinction from ordinary regression is that the coefficient is itself a function of time. Show: (left panel) multiple overlapping predictor curves; (right panel) the corresponding time-varying coefficient curves with the same p-count. A naive drawing that shows a scalar "coefficient" misrepresents the method.

### 2. `docs/assets/diagrams/functional-glm.svg`

**Method-accuracy requirement:** Must show the two-stage pipeline: (1) FPCA projects functional data onto FPC scores; (2) the GLM is fit in score space with the chosen link function. A critical distinction is the link function dispatch: Gaussian=identity, Binomial=logit, Poisson=log, Gamma=**inverse (1/μ)** — not log-link. The diagram must label the Gamma branch with "inverse link 1/μ" to prevent the R-user confusion. Suggested: a flow diagram left-to-right with a fork for family/link dispatch.

### 3. `docs/assets/diagrams/pace-fpca.svg`

**Method-accuracy requirement (flagged by reviewer):** Must show:
- **Left panel:** sparse, irregular observations (dots at different x-positions per curve, NOT on a common grid — this is what "irregular" means).
- **Right panel:** the recovered smooth eigenfunctions on the common work grid, NOT the raw data resampled.
- The visual contrast "ragged irregular dots → smooth eigenfunction curves" is the core message. A diagram that shows regular-grid data with uniform spacing is incorrect.

### 4. `docs/assets/diagrams/elastic-multinomial.svg`

**Method-accuracy requirement:** Must convey K-class one-vs-rest structure: K binary elastic classifiers, each producing a score, combined via softmax into class probabilities. Show 3 classes (for concreteness), 3 OvR binary models, and the softmax aggregation. A diagram that looks like ordinary LDA misrepresents the elastic (SRSF-domain) multinomial model.

### 5. `docs/assets/diagrams/functional-outliers.svg`

**Method-accuracy requirement (flagged by reviewer):** Must faithfully show the asymmetry between hypograph and epigraph depth:
- Hypograph index = proportion of curves BELOW the reference curve.
- Epigraph index = proportion of curves ABOVE the reference curve.
- A curve at the bottom of the bundle has high hypograph index (many curves above it) and LOW epigraph index.
- A curve at the top has the reverse.
- The diagram must show at least two reference curves — one near the top, one near the bottom — with the asymmetric counting correctly labelled. Drawing both indices as symmetric is a method-accuracy error.

### 6. `docs/assets/diagrams/itp-interval-inference.svg`

**Method-accuracy requirement (flagged by reviewer — CRITICAL):** The ITP p-value vector is closure-adjusted. The correct closure direction is:
- For a sequence of p-values `p[0], p[1], …, p[K-1]` (one per basis function), the Bonferroni-Holm closure is applied from the **smallest to largest** index (or in a specific ordering based on the Simes/Romano-Wolf procedure depending on the fdars-core implementation).
- The diagram must show the p-value profile as a **vector** (one value per basis function, plotted against basis-function index or domain interval), NOT as a single scalar. Each bar/line segment represents one basis function's closure-adjusted p-value.
- The closure adjustment REDUCES p-values compared to raw (makes it easier to reject) — the adjusted curve should be at or BELOW the raw p-value curve, not above it.
- A diagram showing closure as inflating p-values would be a method-accuracy error.

Suggested layout (viewBox 720x300):
- Left panel: test statistic curve over the domain (or basis function index).
- Right panel: side-by-side bars of raw p-values (light) and closure-adjusted p-values (darker, at or below the raw), with a horizontal dashed 0.05 threshold line.

### 7. `docs/assets/diagrams/depth-asymmetry.svg` (optional — integrate into functional-outliers.svg if space permits)

If the outliers SVG becomes too dense with 4 detectors, author a dedicated asymmetry diagram showing hypograph vs epigraph counting for functional depth, to be referenced in the `depth-functions.md` extension section.

---

## Advisor `aspects.md` Update (DOCS-11)

The `docs/advisor/aspects.md` file has two aspects requiring updates. [VERIFIED: docs/advisor/aspects.md:270-350]

### `outliers` aspect — current coverage

Current fdars sources documented: `detect_outliers_lrt`, `detect_outliers_lrt_with_dist`, `outliergram`, `magnitude_shape`. [VERIFIED: docs/advisor/aspects.md:271-275]

**Required additions (from ADV-04, Phase 40):**

The `outliers` aspect `build_diagnostics` was extended in Phase 40 to handle the 4 new detector result-dict keys. The `aspects.md` section must add these to the documented fdars sources list and add new rows to the key table:

| New key | Meaning | Source |
|---------|---------|--------|
| `tvdmss_n_magnitude_outliers` | Count of tvdmss magnitude outliers; `None` when tvdmss keys absent | `tvdmss` result |
| `tvdmss_n_shape_outliers` | Count of tvdmss shape outliers; `None` when absent | `tvdmss` result |
| `muod_n_magnitude_outliers` | Count of muod magnitude outliers; `None` when absent | `muod` result |
| `muod_n_shape_outliers` | Count of muod shape outliers; `None` when absent | `muod` result |
| `muod_n_amplitude_outliers` | Count of muod amplitude outliers; `None` when absent | `muod` result |
| `seq_transform_n_union` | Count of union outliers from sequential transform; `None` when absent | `sequential_transform_outliers` |
| `depthgram_n_shape_outliers` | Count of depthgram shape outliers; `None` when absent | `depthgram` |
| `depthgram_n_magnitude_outliers` | Count of depthgram magnitude outliers; `None` when absent | `depthgram` |

> These key names are `[ASSUMED]` — the actual key names in `build_diagnostics` output for the v6.0 detectors must be confirmed by reading `python/fdars/advisor.py` at plan time. The planner must do a `grep` on `advisor.py` for the new diagnostic key names before emitting the table.

### `regression` aspect — current coverage

Current fdars sources: `fregre_lm`, `fregre_pls`, `fregre_l1`, `fregre_huber`, `fregre_np`, `fosr`, `fosr_fpc`. [VERIFIED: docs/advisor/aspects.md:330-332]

**Required additions (from ADV-05, Phase 40):** Add `functional_glm` and `concurrent_regression` to the fdars sources list and document any new diagnostic keys the Phase 40 advisor extension exposed. The planner must read `python/fdars/advisor.py` to confirm exact key names before writing the table rows.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead |
|---------|-------------|-------------|
| SVGO check | Custom diff logic | `npx svgo@3.3.4 --config svgo.config.mjs` idempotence check (pin version) |
| Fence execution | Custom script runner | `markdown-exec` plugin (already configured in `mkdocs.yml`) |
| Deterministic SVG IDs | uuid4 → non-deterministic | `svg.hashsalt = "fdars-docs"` already in `scripts/docs_fig.py` |
| Fast/full build toggle | Per-file env checks | `from docs_fig import fast` helper |
| Dataset loading | Custom CSV reader | `from docs_data import load_phoneme, load_tecator, load_canadian_weather` |

---

## Common Pitfalls

### Pitfall 1: `beta_curve` shape confusion in `concurrent_regression`

**What goes wrong:** Treating `beta_curve` as `(n_obs, m)` — the shape of every other FdMatrix in pyfda. It is actually `(p, m)` where p is the number of predictors.
**Root cause:** The code comment in `regression_mod.rs` line 984: "NOT (n_obs, m) as with every other FdMatrix in pyfda." [VERIFIED: src/regression_mod.rs:984]
**How to avoid:** The fence must assert `beta.shape == (p, m)` where p is `len(predictors)`.

### Pitfall 2: Gamma link function confusion in `functional_glm`

**What goes wrong:** Documenting the Gamma family as using a log-link (as R's `glm()` defaults to). It uses the **inverse canonical link** 1/μ.
**Root cause:** The code comment at line 1091: "Gamma uses inverse canonical link g(μ)=1/μ, NOT log-link (unlike R default)." [VERIFIED: src/regression_mod.rs:1091]
**How to avoid:** The DOCS-08 page must contain an admonition warning box: `!!! warning "Gamma inverse link"` noting the distinction.

### Pitfall 3: `irreg_fdata_from_lists` rejects 2-D numpy arrays

**What goes wrong:** Passing `X` (a dense `(n, m)` numpy array) to `irreg_fdata_from_lists`. It raises `ValueError` with the message "received a 2-D numpy array; pass two Python lists of 1-D arrays".
**Root cause:** The explicit guard at `src/pace_fpca_mod.rs:110-115`. [VERIFIED: src/pace_fpca_mod.rs:110-115]
**How to avoid:** The PACE fence must construct `argvals_list` and `values_list` as Python lists explicitly.

### Pitfall 4: `sequential_transform_outliers` param is `depth_method` not `method`

**What goes wrong:** Calling `sequential_transform_outliers(X, ["t0"], method="modified_band")` — the parameter name is `depth_method`, not `method`.
**Root cause:** `src/outliers_mod.rs:398`: `#[pyo3(signature = (data, transforms, depth_method="modified_band", emp_factor=1.5))]`. [VERIFIED: src/outliers_mod.rs:398]

### Pitfall 5: ITP `n_basis` return vs `nbasis` input

**What goes wrong:** Assuming `len(res["adjusted_pvalues"]) == nbasis`. After bspline clamping, `res["n_basis"]` may be less than the requested `nbasis`.
**Root cause:** `src/inference_mod.rs:618`: "B-spline clamping may reduce the actual count; read `n_basis` from the returned dict for the actual length of the p-value arrays." [VERIFIED: src/inference_mod.rs:617-619]

### Pitfall 6: svgo version — must pin `@3.3.4`

**What goes wrong:** Using `npx svgo` or `npx svgo@latest` — v4 has a different CLI and config API.
**Root cause:** STYLE_SPEC.md: "Pin `svgo@3.3.4` — not `latest`. svgo v4 has a different CLI and config API." [VERIFIED: docs/assets/diagrams/STYLE_SPEC.md:19-20]

### Pitfall 7: `elastic_multinomial` requires `labels` dtype `int64`

**What goes wrong:** Passing `labels` as `np.int32` or a plain Python list of ints. The binding's Rust signature is `PyReadonlyArray1<'py, i64>`.
**Root cause:** `src/classification_mod.rs:334`. [VERIFIED: src/classification_mod.rs:334]
**How to avoid:** The fence must include `labels = np.array([...], dtype=np.int64)`.

---

## Build / Verify Recipe

### Fast iteration (per-page check)

```bash
cd /home/simonm/projects/rust/pyfda
# Activate venv
source .venv/bin/activate

# Fast build (DOCS_FAST=1 lowers n_perm/nb counts via fast() helper)
PYTHONPATH=scripts DOCS_FAST=1 mkdocs build --strict

# Check fence output in built HTML
grep -c "FDARS_FENCE_OK" site/inference/interval-inference/index.html
grep -q "interval-inference.svg" site/inference/interval-inference/index.html && echo SVG_REF_OK
```

### Full site build (source-of-truth gate)

```bash
cd /home/simonm/projects/rust/pyfda
PYTHONPATH=scripts mkdocs build --strict
# Expected: exit 0; ~19-min wall time
```

### SVGO idempotence check per new SVG

```bash
# For each new SVG:
FILE=docs/assets/diagrams/concurrent-regression.svg
npx svgo@3.3.4 --config svgo.config.mjs --quiet --input "$FILE" --output /tmp/pass1.svg
npx svgo@3.3.4 --config svgo.config.mjs --quiet --input /tmp/pass1.svg --output /tmp/pass2.svg
diff /tmp/pass1.svg /tmp/pass2.svg && echo "IDEMPOTENT: $FILE" || echo "FAILS: $FILE"
```

### `rsvg-convert` PNG render for human diagram review

```bash
# Render each new SVG to PNG for visual method-accuracy review
for SVG in \
    docs/assets/diagrams/concurrent-regression.svg \
    docs/assets/diagrams/functional-glm.svg \
    docs/assets/diagrams/pace-fpca.svg \
    docs/assets/diagrams/elastic-multinomial.svg \
    docs/assets/diagrams/functional-outliers.svg \
    docs/assets/diagrams/itp-interval-inference.svg; do
  PNG="/tmp/$(basename ${SVG%.svg}).png"
  rsvg-convert -w 1440 "$SVG" -o "$PNG" && echo "Rendered: $PNG"
done
```

---

## Plan Split Recommendation

**Four plans** (not one), matching the four requirements, ordered by dependency:

| Plan | Requirement | New files | Type | Wave |
|------|-------------|-----------|------|------|
| 41-01 | DOCS-08 | `concurrent-regression.md`, `functional-glm.md`, 2 SVGs | 2 new pages | 1 |
| 41-02 | DOCS-09 | `pace-fpca.md`, 1 SVG; extend `classification.md`, 1 SVG | 1 new + 1 extend | 2 |
| 41-03 | DOCS-10 | extend `depth-functions.md`; extend `outlier-detection.md`, 1 SVG; `interval-inference.md`, 1 SVG | 1 new + 2 extend | 3 |
| 41-04 | DOCS-11 | extend `advisor/aspects.md`; `mkdocs.yml` nav wiring; full build + SVGO gate + human review | Nav + build + gate | 4 |

**Rationale:** The ~19-min build makes iteration expensive. Separating into 4 plans means each plan has its own per-page `DOCS_FAST=1` build verification that runs quickly, with the final full-site build only in plan 41-04. If a fence or SVG causes a build error, the failure is isolated to one plan's scope rather than requiring a full-site retry.

Wave sequencing: Plans 41-01, 41-02, 41-03 can run sequentially (each depends on the prior wave's nav additions being stable). Plan 41-04 must run last. Alternatively, 41-01 and 41-02 could parallelize since they write to different directories, but the sequential approach is safer given the single `mkdocs.yml` file shared by all.

---

## Validation Architecture

> `workflow.nyquist_validation` is not explicitly set to false; treat as enabled.

### Test Framework

| Property | Value |
|----------|-------|
| Framework | `mkdocs build --strict` (build-time execution via `markdown-exec`) |
| Config file | `mkdocs.yml` |
| Quick run command | `PYTHONPATH=scripts DOCS_FAST=1 .venv/bin/mkdocs build --strict` |
| Full suite command | `PYTHONPATH=scripts .venv/bin/mkdocs build --strict` (no DOCS_FAST) |

### Phase Requirements → Validation Map

| Req ID | Behavior | Validation Type | Automated Check |
|--------|----------|-----------------|-----------------|
| DOCS-08 | `concurrent_regression` fence emits FDARS_FENCE_OK | Build-time fence execution | `grep -q FDARS_FENCE_OK site/regression/concurrent-regression/index.html` |
| DOCS-08 | `functional_glm` fence emits FDARS_FENCE_OK | Build-time fence execution | `grep -q FDARS_FENCE_OK site/regression/functional-glm/index.html` |
| DOCS-08 | Gamma inverse-link caveat documented | Manual review | Human reads page |
| DOCS-09 | `pace_fpca` fence emits FDARS_FENCE_OK | Build-time fence execution | `grep -q FDARS_FENCE_OK site/represent/pace-fpca/index.html` |
| DOCS-09 | `elastic_multinomial` fence emits FDARS_FENCE_OK | Build-time fence execution | `grep -c FDARS_FENCE_OK site/regression/classification/index.html` ≥ previous count + 1 |
| DOCS-10 | 9 new depth methods documented in depth-functions.md | Build-time + manual review | `grep -q hypograph_index site/represent/depth-functions/index.html` |
| DOCS-10 | 4 outlier detectors fence emits FDARS_FENCE_OK | Build-time fence execution | `grep -q FDARS_FENCE_OK site/analyze/outlier-detection/index.html` |
| DOCS-10 | `itp_*` fence emits FDARS_FENCE_OK | Build-time fence execution | `grep -q FDARS_FENCE_OK site/inference/interval-inference/index.html` |
| DOCS-11 | `mkdocs build --strict` exits 0 (full build, no DOCS_FAST) | Build gate | `echo "exit=$?"` |
| DOCS-11 | Every new SVG is SVGO-idempotent | SVGO idempotence check | `diff /tmp/pass1.svg /tmp/pass2.svg` |
| DOCS-11 | All new SVGs are determinism-clean | SVG timestamp metadata | `grep -v "<dc:date>" SVG` (no date stamp) |
| DOCS-11 | Human diagram review passes | **BLOCKING human gate** | `rsvg-convert` render + visual inspection |

### Sampling Rate

- **Per task commit:** `PYTHONPATH=scripts DOCS_FAST=1 .venv/bin/mkdocs build --strict` (fast build, exit 0)
- **Per plan completion:** verify FDARS_FENCE_OK count in affected pages
- **Phase gate:** Full `PYTHONPATH=scripts .venv/bin/mkdocs build --strict` green before `/gsd-verify-work`; BLOCKING human diagram review before milestone closes

### Wave 0 Gaps

None — existing test infrastructure (build-time fence execution via `markdown-exec`) covers all phase requirements. No new test files or framework config needed.

---

## Security Domain

No security concerns for a documentation-only phase. No network calls during build (all fences execute offline). No user-supplied input paths. The `PYTHONPATH=scripts` injection is scoped to `docs_fig.py` and `docs_data.py` which are part of the project.

---

## Environment Availability

| Dependency | Required By | Available | Notes |
|------------|------------|-----------|-------|
| `.venv/bin/mkdocs` | All fences | Yes | Verified: file exists |
| `PYTHONPATH=scripts` | All fences | Yes | `scripts/docs_fig.py` confirmed |
| `rsvg-convert` | Human review | Not checked | Install via `librsvg` if missing (`sudo pacman -S librsvg`) |
| `npx svgo@3.3.4` | SVGO gate | Yes (npx available) | Pins to exact version via `@3.3.4` |
| `svgo.config.mjs` | SVGO gate | Yes | Verified: file exists |
| `fdars` compiled extension | All fences | Yes | Built by maturin; venv has the package |

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | phoneme.csv contains classes "aa", "ao", "dcl" as the three most common | Fence Blueprints | Fence errors at build time; fix by reading `docs/data/README.md` and adjusting class names |
| A2 | New `build_diagnostics` key names for v6.0 outlier detectors (`tvdmss_n_magnitude_outliers`, etc.) | Advisor aspects.md update | Wrong key names in aspects.md; planner must grep `python/fdars/advisor.py` to get exact names |
| A3 | New `build_diagnostics` key names for v6.0 regression (`functional_glm`/`concurrent_regression` diagnostics) | Advisor aspects.md update | Same as A2; planner must grep advisor.py |
| A4 | `elastic_multinomial` with phoneme subsampled to 3 classes and m ≤ 64 runs in < 30 seconds | Fence Blueprints | Fence causes build timeout; fallback: use purely synthetic 3-class data instead |
| A5 | ITP closure adjustment direction: adjusted_pvalues ≤ raw_pvalues | SVG diagram, ITP section | Method-accuracy error in diagram; reviewer catches at human review gate |

---

## Open Questions

1. **`advisor.py` exact new key names for v6.0 outlier/regression diagnostics**
   - What we know: Phase 40 extended `build_diagnostics` for `outliers` and `regression` aspects.
   - What's unclear: The exact Python dict keys emitted by the new code paths (e.g., whether the key is `tvdmss_n_magnitude_outliers` or `n_tvdmss_magnitude_outliers` or something else).
   - Recommendation: Planner reads `python/fdars/advisor.py` at plan time with `grep -n "tvdmss\|muod\|sequential\|depthgram\|concurrent_regression\|functional_glm"` before writing the `aspects.md` update task.

2. **Phoneme class distribution for the 3-class elastic_multinomial example**
   - What we know: phoneme.csv has 5 classes; we need 3 for the example.
   - What's unclear: Which 3 classes are most balanced / most representative for docs.
   - Recommendation: Planner reads `docs/data/README.md` (or does `python -c "import pandas; print(pandas.read_csv('docs/data/phoneme.csv')['phoneme'].value_counts())"`) to confirm the three most common classes and their counts.

3. **`tvdmss` takes `data` only — no `argvals` parameter**
   - What we know: The Rust signature `tvdmss<'py>(py, data, ...)` has no `argvals`. [VERIFIED: src/outliers_mod.rs:213]
   - What's unclear: Whether the docs page should explain WHY `argvals` is not needed (depth-based internally uses uniform grid assumption) for user clarity.
   - Recommendation: Add a brief note in the parameter table: "No `argvals` parameter — the method uses the column spacing of the data matrix as the implicit grid."

---

## Sources

### Primary (HIGH confidence)

- `src/regression_mod.rs` (lines 978-1192) — `concurrent_regression` and `functional_glm` exact signatures, return dict keys, Gamma-link DOCS caveat [VERIFIED]
- `src/pace_fpca_mod.rs` (lines 1-251) — `irreg_fdata_from_lists` and `pace_fpca` exact signatures, 10-key return dict, 2-D array rejection guard [VERIFIED]
- `src/classification_mod.rs` (lines 278-372) — `elastic_multinomial` exact signature, return keys, labels-int64 requirement [VERIFIED]
- `src/outliers_mod.rs` (lines 200-507) — `tvdmss`, `muod`, `sequential_transform_outliers`, `depthgram` exact signatures, no-argvals, no-seed facts [VERIFIED]
- `src/inference_mod.rs` (lines 596-811) — `itp_one_pop`, `itp_two_pop`, `itp_flm` exact signatures, n_basis clamping note [VERIFIED]
- `src/depth_mod.rs` (lines 428-532) — 13 accepted `functional_depth` method strings verbatim [VERIFIED]
- `docs/assets/diagrams/STYLE_SPEC.md` — SVG authoring contract: viewBox values, style block, SVGO invocation, idempotence gate [VERIFIED]
- `scripts/docs_fig.py` — `fast()` helper, `render()`, `FDARS_COLORS`, `svg.hashsalt` determinism [VERIFIED]
- `mkdocs.yml` (lines 82-195) — current nav structure, Inference section at line 132-133, Represent section at 93-101 [VERIFIED]
- `docs/advisor/aspects.md` (lines 1-529) — current aspect coverage table, outliers/regression/classification/fpca aspect documentation [VERIFIED]
- `.planning/milestones/v5.0-phases/35-docs-diagrams-worked-examples/35-01-PLAN.md` — v5.0 docs phase plan pattern (TRACER-FIRST, per-page strict build, wave structure) [VERIFIED]
- `docs/inference/functional-inference.md` — v5.0 page template (exec fence, SVG include, FDARS_FENCE_OK sentinel position) [VERIFIED]
- `docs/analyze/functional-boxplot.md` — v5.0 page template (returns table, admonition tips) [VERIFIED]
- `docs/represent/depth-functions.md` — page to EXTEND; current depth API summary table at lines 490-500 [VERIFIED]
- `docs/analyze/outlier-detection.md` — page to EXTEND; current structure verified [VERIFIED]
- `docs/regression/classification.md` — page to EXTEND; current phoneme example at lines 410-438 [VERIFIED]

### Tertiary (LOW confidence)

- `[ASSUMED]` Phoneme 3-class subset uses "aa", "ao", "dcl" — verify with `docs/data/README.md`
- `[ASSUMED]` New advisor diagnostic key names for v6.0 detectors — verify with `python/fdars/advisor.py`

---

## Metadata

**Confidence breakdown:**
- Standard page structure: HIGH — read from v5.0 precedents
- API signatures: HIGH — read from shipped Rust source files
- SVG method-accuracy notes: HIGH for ITP/PACE/concurrent-regression; MEDIUM for depthgram (less common reviewer flag)
- Advisor key names: LOW — must be confirmed at plan time

**Research date:** 2026-08-21
**Valid until:** 2026-09-20 (stable — docs-only phase, no external library churn)
