# Phase 73: Documentation & Release — Research

**Researched:** 2026-09-04
**Domain:** MkDocs docs authoring (markdown-exec fences, inline SVG diagrams, STYLE_SPEC), version bump, PyPI publish gate
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **Nav:** slot into existing sections — NO new top-level nav groups. Regression gets Function-on-Function, Additive/Generalized SoF, Fréchet Regression; Analyze gets Functional Time Series, Density FDA, Advanced Clustering, Multi-Domain/FAMM, Shapelets. GAK folds into the Shapelets page (or Distance Metrics).
- **Hard human gates (NOT autonomous — stop and wait):**
  - Blocking human diagram method-accuracy review (DOCS-03, standing v6.0 decision): after authoring 7 diagrams + running `--strict`, PAUSE for the user to review each diagram's method-accuracy against the shipped binding. Do NOT self-approve.
  - Release (REL-01): the `v0.10.0` tag triggers PyPI publish — prep the version bump but DO NOT create the tag/publish autonomously; present as a checkpoint after diagram review passes.

### Claude's Discretion

- **Worked examples:** offline-runnable markdown-exec fences using small datasets (keep fence datasets small — 5 new submodules add ~10 min to `--strict`), each emitting `FDARS_FENCE_OK` per the existing page convention.
- **Diagrams:** hand-authored inline SVG per `docs/assets/diagrams/STYLE_SPEC.md`; SVGO-idempotent; method-accurate concept per family. Follow the v7/v10 diagram authoring workflow (venv + PYTHONPATH + rsvg-convert visual check).
- **Build:** sequential on `main` (use_worktrees:false); doc-build fences hardcode the main-tree `.venv/bin/mkdocs` path; use `DOCS_FAST` for iteration, `mkdocs build --strict` for the final offline gate. Advisor fences need `pydantic` in the docs env (STATE CI gotcha).

### Deferred Ideas (OUT OF SCOPE)

- None — this is the closing phase; all deferred items were logged in earlier phases and remain in STATE Deferred Items.
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| DOCS-01 | One dedicated method-accurate page per new capability family (fts, fof/sof-regression, frechet, density-fda, multi-domain/FAMM, clustering, shapelet) wired into `mkdocs.yml` nav, each with a runnable offline worked example emitting `FDARS_FENCE_OK` | Fence mechanism fully documented; per-family API signatures verified; page skeleton provided |
| DOCS-02 | One hand-authored, STYLE_SPEC-conformant, SVGO-idempotent inline SVG concept diagram per new family, method-accurate against the shipped binding | Full STYLE_SPEC rules extracted; SVGO idempotence protocol documented; concrete SVG template provided |
| DOCS-03 | Advisor `aspects.md` updated for new/extended aspects; whole-site `mkdocs build --strict` green offline; blocking human diagram method-accuracy review approved before close | aspects.md structure fully mapped; offline --strict command documented; human gate sequencing specified |
| REL-01 | Package version bumped `0.9.0 → 0.10.0` in `Cargo.toml` + `pyproject.toml`; semver tag `v0.10.0` (triggers PyPI publish) — decided/applied at milestone close | Exact lines to edit verified; publish trigger workflow documented; HUMAN-GATED checkpoint specified |
</phase_requirements>

---

## Summary

Phase 73 closes the v11.0 milestone by documenting every new capability family to the project's
method-accurate standard and releasing the package. All binding work (Phases 67–72) is already
shipped. This phase is purely authoring: 7 doc pages, 7 SVG diagrams, one aspects.md update,
a final `--strict` build gate, a blocking human diagram review, and a version bump prep.

The docs build pipeline is well-understood from v7.0/v10.0. The core contract is simple:
every new page contains an offline-runnable `python exec="1"` fence (validated by markdown-exec
during `mkdocs build --strict`) that ends with `print("... FDARS_FENCE_OK")`. The SVGO
idempotence gate runs over all 93 + 7 diagrams in CI. The version bump is two file edits
(Cargo.toml line 3, pyproject.toml line 7); the `v0.10.0` semver tag triggers the publish
workflow and is a hard human gate.

**Primary recommendation:** Author pages and diagrams family-by-family using `DOCS_FAST=1`
for iteration, then run ONE `mkdocs build --strict` at the close, then STOP for the blocking
human diagram review before any release actions.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Fence execution (markdown-exec) | Frontend Server (MkDocs build) | — | markdown-exec runs fences at build time in the docs Python process; not a browser or backend concern |
| FDARS_FENCE_OK assertion | MkDocs build / CI gate | — | `check_docs_figures.py` scans the built site for traceback markers; `--strict` fails on markdown warnings |
| SVG diagram storage | CDN / Static (docs/assets/diagrams/) | — | Hand-authored SVG committed to repo; served as static assets |
| SVGO idempotence gate | CI (docs.yml) | local dev | Runs `npx svgo@3.3.4` pass-1/pass-2 diff in the Lint SVG diagrams step |
| Nav wiring | Frontend Server (mkdocs.yml) | — | mkdocs.yml nav section owns page routing |
| Version bump | Build system (Cargo.toml + pyproject.toml) | — | Two files control the published version number |
| PyPI publish | External (GitHub Actions publish.yml) | — | Triggered by semver tag push; entirely external to the local build |

---

## 1. Fence / FDARS_FENCE_OK Mechanism

### Fence Syntax

Every worked-example fence in the fdars docs uses this pattern:

```
```python exec="1" source="above"
import numpy as np
from fdars.<module> import <function>

# ... small deterministic computation ...
result = <function>(data, argvals)

print(f"key: {result['key']}  FDARS_FENCE_OK")
```
```

If the fence also renders a matplotlib figure:

```
```python exec="1" html="1" source="above"
import numpy as np
from docs_fig import fig, render
from fdars.<module> import <function>

f, ax = fig()
# ... plot ...
print(render(f))
```
```

The `html="1"` option tells markdown-exec to treat the block's stdout as raw HTML. Without
it, stdout is treated as text. `source="above"` renders the code block above the output.
[VERIFIED: docs/represent/depth-functions.md:8-29, docs/advisor/aspects.md:195-208]

### Block Options Reference

| Option | Effect |
|--------|--------|
| `exec="1"` | Runs the code at build time |
| `html="1"` | stdout is embedded as raw HTML (needed for matplotlib SVG output via `render(f)`) |
| `source="above"` | Shows the code block above the rendered output |

### How FDARS_FENCE_OK Is Asserted

There is **no hook or grep gate** enforcing `FDARS_FENCE_OK` at build time. It is a
**human-readable convention**, not a machine-enforced contract. Its purpose is to make it
immediately obvious (when reading the rendered page) that the fence completed successfully
with a known-good output value. [VERIFIED: docs/hooks.py:1-17] — hooks.py only adds `scripts/`
to `sys.path`; it performs no FDARS_FENCE_OK check.

The real build-time assertion is twofold:

1. **Fence exception → traceback in HTML:** If the fence raises, markdown-exec embeds a
   Python traceback in the built page instead of failing the build. `check_docs_figures.py`
   scans for `"Traceback (most recent call last)"` and `'class="exec-error"'` in built HTML
   and exits non-zero, which CI treats as a failure.
   [VERIFIED: scripts/check_docs_figures.py:14-19]

2. **`--strict` makes mkdocs warnings into errors:** warnings from unresolvable links etc.
   become build failures under `--strict`.

So: `FDARS_FENCE_OK` is purely a convention. The fence must not raise and must print the
marker at the end. The CI gate (`check_docs_figures.py`) catches silent traceback-in-HTML
failures; `--strict` catches structural doc errors.

### DOCS_FAST vs. --strict

| Mode | Command | Fence behavior | When to use |
|------|---------|---------------|-------------|
| Fast iteration | `DOCS_FAST=1 PYTHONPATH=scripts .venv/bin/mkdocs build` | Fences run but `fast(full, fast_val)` uses low iteration counts | Per-page authoring; keeps build < 3 min |
| Strict gate | `PYTHONPATH=scripts .venv/bin/mkdocs build --strict` | All fences run at full iteration counts; warnings=errors | ONE run at phase close |

`DOCS_FAST=1` activates `docs_fig.fast()` helpers. **Do not use for final gate output.**
[VERIFIED: scripts/docs_fig.py:114-131]

### Copy-Pasteable Page Skeleton

```markdown
---
title: [Family Name]
---

# [Family Name]

[2–3 sentence intro: what the method does and why it matters for FDA]

![Family concept diagram](../assets/diagrams/[family-slug].svg){ .fdars-diagram }

## [Core Concept]

[Method math and description — 1–2 paragraphs]

```python exec="1" source="above"
import numpy as np
from fdars.[module] import [function]

rng = np.random.default_rng(42)
n, m = 15, 40                       # keep small — no fancy fixture
t = np.linspace(0, 1, m)
data = np.array([np.sin(2 * np.pi * t + rng.uniform(0, 0.5)) for _ in range(n)])

result = [function](data, t, ...)
print(f"[key]: {result['[key]']}  FDARS_FENCE_OK")
```

[Interpretation paragraph: what the output means]

## API Reference

```python
from fdars.[module] import [function]

result = [function](data, argvals, ...)
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `data` | `np.ndarray` (n, m) | Functional observations (n curves, m grid points) |
| `argvals` | `np.ndarray` (m,) | Evaluation grid |

| Key | Meaning |
|-----|---------|
| `[key]` | [description] |

## References

- [Author (Year) paper title. Journal.]
```

### Environment for Fence Execution

- `PYTHONPATH=scripts` — exposes `docs_fig.py` and `docs_data.py` to fence code
- `.venv` must have `fdars` installed (via `maturin develop --release`)
- `pydantic>=2.0` and `anthropic>=0.72.0` must be in `.venv` — required by advisor fences
  (docs/requirements.txt already includes both) [VERIFIED: docs/requirements.txt:17-21]
- The canonical local build command: `PYTHONPATH=scripts .venv/bin/mkdocs build --strict`

---

## 2. Per-Family Worked-Example Templates

### How to Read the Tables

`[VERIFIED: src/...]` means the function signature was confirmed by reading the actual
Rust source file this session. The call pattern is the minimal offline example the planner
should template. All fixtures use `seed=42` (or `rng = np.random.default_rng(42)`) for
determinism.

---

### Family A: Functional Time Series (`fdars.fts`)

**Page location:** `docs/analyze/functional-time-series.md`
**Nav slot:** Analyze section (new entry)

**Shipped functions** [VERIFIED: src/fts_mod.rs:46-741]:
- `ftsm(data, argvals, ncomp=3)` → dict with keys: `mean`, `rotation`, `scores`, `fitted`, `weights`, `ncomp`
- `ftsm_forecast(data, argvals, h, ncomp=3)` → dict
- `ftsm_forecast_multistep(data, argvals, h_list, ncomp=3)` → dict
- `ftsm_update(data, argvals, new_obs, ncomp=3)` → dict
- `fplsr(data, argvals, y, ncomp=3)` → dict with `forecast`, `fitted`, `ncomp`
- `functional_acf(data, argvals, lags, seed=42)` → dict
- `functional_pacf(data, argvals, lags, seed=42)` → dict
- `stationarity_test(data, argvals, n_perm=99, seed=42)` → dict with `statistic`, `p_value`
- `long_run_covariance(data, argvals, bandwidth=1.0)` → dict with `cov_matrix`
- `spectral_density(data, argvals, freq)` → dict with `re`, `im`
- `dpca(data, argvals, ncomp=3, order=1)` → dict with `filters`, `scores`, `eigenvalues`, `valid_range`
- `dpca_reconstruct(data, argvals, ncomp=3, order=1)` → dict (merged dpca + `reconstruction_error`)
- `functional_difference(data, lag=1)` → 2D numpy array (naked, not a dict)

**Minimal offline example:**

```python exec="1" source="above"
import numpy as np
from fdars.fts import ftsm, ftsm_forecast, stationarity_test

rng = np.random.default_rng(42)
n, m = 20, 30       # non-square: n != m (transposition guard)
t = np.linspace(0, 1, m)
data = np.array([np.sin(2 * np.pi * t + rng.uniform(0, 0.5)) +
                 0.1 * rng.standard_normal(m) for _ in range(n)])

fit = ftsm(data, t, ncomp=3)
fc  = ftsm_forecast(data, t, h=3, ncomp=3)
st  = stationarity_test(data, t, n_perm=19, seed=42)

print(f"ftsm ncomp:     {fit['ncomp']}")
print(f"forecast shape: {np.asarray(fc['forecast']).shape}")
print(f"stationarity p: {st['p_value']:.3f}  FDARS_FENCE_OK")
```

**Fixture note:** `n=20, m=30` is non-square (required to catch transposition bugs per
phase decision 67-01). Use `n_perm=19` for stationarity_test to keep fence runtime < 2 s.

---

### Family B: Function-on-Function & Scalar-on-Function Regression

**Page location:** `docs/regression/function-on-function.md` (FoF + FoF-RE)
AND `docs/regression/additive-sof.md` (FAM / gkam / gsam / selection)
**Nav slot:** Regression section (two new entries)

**Shipped FoF functions** [VERIFIED: src/regression_mod.rs:1276-1650]:
- `fof_regression(x_data, y_data, x_argvals, y_argvals, ncomp_x, ncomp_y)` → dict:
  `intercept`, `beta_surface`, `fitted`, `residuals`, `r_squared_t`, `r_squared`,
  `ncomp_x`, `ncomp_y`, `coef_matrix` (NOTE: `fpca_x`/`fpca_y` intentionally excluded)
- `predict_fof(x_data, y_data, x_argvals, y_argvals, ncomp_x, ncomp_y, new_x)` → 2D array
- `fof_cv(x_data, y_data, x_argvals, y_argvals, ncomp_x_range)` → dict with `best_ncomp_x`, `cv_scores`
- `fof_re_regression(x_data, y_data, x_argvals, y_argvals, subject_ids, ncomp_x, ncomp_y)` → dict
- `predict_fof_re(...)` → 2D array

**Shipped SoF functions** [VERIFIED: src/scalar_on_function_mod.rs:76-490]:
- `fam(data, y, argvals, scalar_covariates=None, ncomp, bandwidth, kernel, n_grid_bandwidth)` → dict
- `fregre_gsam(...)` — same 7-key dict structure as fam (has_fam discriminator in advisor)
- `fregre_gkam(...)` → dict with different key structure
- `variable_selection(data, y, argvals, ...)` → dict
- `model_selection_ncomp(data, y, argvals, ...)` → dict

**Minimal FoF offline example:**

```python exec="1" source="above"
import numpy as np
from fdars.regression import fof_regression

rng = np.random.default_rng(42)
n, mx, my = 25, 20, 15    # non-square predictor and response grids
tx = np.linspace(0, 1, mx)
ty = np.linspace(0, 1, my)
X  = np.array([np.sin(2 * np.pi * tx + rng.uniform(0, 0.3)) for _ in range(n)])
Y  = np.array([np.cos(np.pi * ty + rng.uniform(0, 0.3))     for _ in range(n)])

fit = fof_regression(X, Y, tx, ty, ncomp_x=3, ncomp_y=3)
print(f"r_squared:       {fit['r_squared']:.4f}")
print(f"beta_surface:    {np.asarray(fit['beta_surface']).shape}  FDARS_FENCE_OK")
```

**Fixture note:** `ncomp_x=3, ncomp_y=3` is safe for n=25. The beta_surface shape is
`(ncomp_x, ncomp_y)` in the coefficient matrix sense (confirm via spot-check). Keep
the grids non-square to expose any transposition bug.

---

### Family C: Fréchet Regression (`fdars.frechet`)

**Page location:** `docs/regression/frechet-regression.md`
**Nav slot:** Regression section (new entry)

**Shipped functions** [VERIFIED: src/frechet_mod.rs:55-489]:
- `frechet_mean(objects, space, d, weights=None)` → returns array (SPD case: (d,d) 2D array) or list — NOT a dict; the return type varies by space
- `frechet_global_reg(predictors, responses, argvals, xout)` → dict: `predicted`, `xout`, `x_bar`
- `frechet_local_reg(predictors, responses, argvals, xout, bandwidth)` → dict
- `frechet_anova(objects, group_labels, space, d, n_perm=99)` → dict with `statistic`, `p_value`

**Minimal offline example — use the SPD (symmetric positive-definite) space:**

```python exec="1" source="above"
import numpy as np
from fdars.frechet import frechet_mean

rng = np.random.default_rng(42)
d = 2
# Build small list of SPD matrices as (d,d) numpy arrays
spds = []
for _ in range(8):
    A = rng.standard_normal((d, d))
    spds.append(A @ A.T + np.eye(d))  # symmetric positive-definite

mean_spd = np.asarray(frechet_mean(spds, space="spd", d=d))
print(f"Fréchet mean (SPD, d=2): shape {mean_spd.shape}")
print(f"positive diagonal: {mean_spd[0,0] > 0} {mean_spd[1,1] > 0}  FDARS_FENCE_OK")
```

**Fixture note:** SPD inputs require the objects to be passed as Python lists of 2D numpy
arrays (not stacked 3D array). The `frechet_mean` function in the `"spd"` space validates
positive diagonal entries and symmetry. [VERIFIED: src/frechet_mod.rs:344-370]. The frechet
return type is NOT a dict for `frechet_mean` — it returns the mean object directly (an
array or list depending on space). This is a non-trivial fixture: SPD matrices must be
genuinely SPD (positive-definite diagonal). The example above constructs them via `A@A.T + I`.

---

### Family D: Density FDA (`fdars.density_fda`)

**Page location:** `docs/analyze/density-fda.md`
**Nav slot:** Analyze section (new entry)

**Shipped functions** [VERIFIED: src/density_fda_mod.rs:40-273]:
- `normalize_density(density, argvals)` → 1D numpy array (naked, not dict)
- `lqd_transform(density, argvals)` → 1D numpy array (naked)
- `inverse_lqd(lqd, argvals)` → 1D numpy array (naked)
- `wasserstein_barycenter(densities, argvals, weights=None)` → 1D numpy array (naked)
- `lqd_fpca(densities, argvals, n_comp=3)` → dict: `scores`, `loadings`, `mean_lqd`, `singular_values`, `explained_variance`, `n_comp`

**Minimal offline example:**

```python exec="1" source="above"
import numpy as np
from fdars.density_fda import normalize_density, lqd_transform, lqd_fpca

rng = np.random.default_rng(42)
m = 50
t = np.linspace(0, 1, m)
# Simulate 10 small density-like functions (non-negative, will be normalized)
densities = np.array([np.abs(np.sin(np.pi * t + rng.uniform(0, 0.5))) + 0.01
                      for _ in range(10)])
norm = np.array([normalize_density(densities[i], t) for i in range(10)])
lqd  = np.array([lqd_transform(norm[i], t) for i in range(10)])
fp   = lqd_fpca(norm, t, n_comp=2)

print(f"normalized density sum (approx 1): {np.trapz(norm[0], t):.4f}")
print(f"lqd_fpca n_comp: {fp['n_comp']}  FDARS_FENCE_OK")
```

**Fixture note:** `normalize_density`, `lqd_transform`, and `inverse_lqd` return naked 1D
arrays (not dicts). Phase 69 decision: "single-vector transform convention." The LQD
transform requires a non-negative density; ensure fixture values are > 0 everywhere.

---

### Family E: Multi-Domain/FAMM (`fdars.multi_fdata` + `fdars.famm` + `fdars.spm`)

**Page location:** `docs/analyze/multi-domain.md`
**Nav slot:** Analyze section (new entry)

**Shipped functions** [VERIFIED: src/multi_fdata_mod.rs:86-159, src/famm_mod.rs:94-305]:
- `multi_fdata_from_components(components)` → `PyMultiFunData` opaque handle (NOT a dict)
- `dense_flmm(y, multi_fdata, ...)` → dict (14-key structure)
- `fast_fmm(y, curves, ...)` → dict
- `multi_famm(y, multi_fdata, ...)` → dict (reuses `dense_flmm_result_to_pydict`)
- `mfpca(variables, ...)` → dict with `components`, `eigenvalues`, `variance_explained` [VERIFIED: src/spm_mod.rs:882-975]
- `spe_multivariate(standardized_vars, reconstructed_vars, argvals_list, ...)` → dict or array

**Minimal offline example (focus on mfpca — most self-contained):**

```python exec="1" source="above"
import numpy as np
from fdars.spm import mfpca

rng = np.random.default_rng(42)
n, m1, m2 = 20, 30, 25   # non-square variable grids
t1 = np.linspace(0, 1, m1)
t2 = np.linspace(0, 1, m2)
V1 = np.array([np.sin(2 * np.pi * t1 + rng.uniform(0, 0.3)) for _ in range(n)])
V2 = np.array([np.cos(np.pi * t2 + rng.uniform(0, 0.3))     for _ in range(n)])

result = mfpca([V1, V2], ncomp=2)
print(f"mfpca scores shape:  {np.asarray(result['scores']).shape}")
print(f"eigenvalues:         {[round(e, 4) for e in np.asarray(result['eigenvalues'])[:2].tolist()]}  FDARS_FENCE_OK")
```

**Fixture note:** `PyMultiFunData` is an opaque handle (Phase 70 decision: "standalone
container — 0 consumers in fdars-core 0.33"). The most useful self-contained example is
`mfpca` (takes a list of 2D numpy arrays directly, no handle needed). For `dense_flmm` /
`multi_famm`, a more complex fixture is needed (longitudinal y-vector + multi_fdata handle).
Use `mfpca` as the primary fence; mention `dense_flmm` in the API table without a live fence.

---

### Family F: Advanced Clustering (`fdars.clustering` — extension)

**Page location:** `docs/analyze/advanced-clustering.md`
**Nav slot:** Analyze section (new entry)

**Shipped functions** [VERIFIED: src/clustering_mod.rs:313-565]:
- `dbscan_fd(data, argvals, eps, min_points)` → dict: `cluster` (1D int array, -1=noise), `n_clusters`, `n_noise`, `distances`
- `kcfc_cluster(data, argvals, k, ...)` → dict with labels + per-cluster FPCA info
- `funfem_cluster(data, argvals, k, ...)` → dict
- `align_cluster_fd(data, argvals, k, ...)` → dict with `templates` as list of 1D arrays

**Minimal offline example:**

```python exec="1" source="above"
import numpy as np
from fdars.clustering import dbscan_fd, kcfc_cluster

rng = np.random.default_rng(42)
n, m = 25, 40     # non-square
t = np.linspace(0, 1, m)
# Two clear clusters: sin-family and cos-family
X = np.vstack([
    np.array([np.sin(2 * np.pi * t + rng.uniform(-0.2, 0.2)) for _ in range(13)]),
    np.array([np.cos(2 * np.pi * t + rng.uniform(-0.2, 0.2)) for _ in range(12)]),
])

db  = dbscan_fd(X, t, eps=0.5, min_points=3)
kfc = kcfc_cluster(X, t, k=2)

print(f"dbscan n_clusters: {db['n_clusters']}")
print(f"kcfc labels shape: {np.asarray(kfc['labels']).shape}  FDARS_FENCE_OK")
```

**Fixture note:** `dbscan_fd` maps noise points to `-1` (not `None`) in the Python output.
[VERIFIED: src/clustering_mod.rs:328-334]. `kcfc_cluster` excludes `fpca_models` from the
PyDict (Phase 70 decision: "holds internal FpcaResult Rust structs not exposed as #[pyclass]").
Use `eps=0.5, min_points=3` for the fixture — tested values from Phase 70.

---

### Family G: Shapelets + GAK (`fdars.shapelet` + `fdars.metric`)

**Page location:** `docs/analyze/shapelets.md` (GAK folds into this page)
**Nav slot:** Analyze section (new entry)

**Shipped shapelet functions** [VERIFIED: src/shapelet_mod.rs:214-481]:
- `discover_shapelets(data, labels, n_shapelets, quality, ...)` → list of shapelet arrays
- `shapelet_transform_fit(data, labels, n_shapelets, quality, ...)` → `PyShapeletFit` opaque handle
- `shapelet_transform(fit, data)` → 2D numpy array (n_test, n_shapelets)
- `shapelet_classifier_fit(data, labels, n_shapelets, quality, classifier, ...)` → `PyShapeletClassifierFit` opaque handle with `.predict(data)` and `.train_accuracy`
- `shapelet_distance(x, y, ...)` → scalar float

**Shipped GAK functions** [VERIFIED: src/metric_mod.rs:4-163]:
- `gak(x, y, sigma)` → scalar float (self-similarity = 1.0)
- `sigma_gak(data)` → float (automatic bandwidth selection)
- `gak_gram_matrix(data, sigma=None)` → (n, n) 2D numpy array
- `gak_gram_train(data, sigma=None)` → `PyGakGramTrain` opaque handle
- `gak_gram_predict(train_handle, new_data)` → (n_test, n_train) 2D numpy array

**Minimal offline example:**

```python exec="1" source="above"
import numpy as np
from fdars.shapelet import (shapelet_transform_fit, shapelet_transform,
                             shapelet_classifier_fit)
from fdars.metric import gak_gram_matrix, sigma_gak

rng = np.random.default_rng(42)
m = 40
t = np.linspace(0, 1, m)
# Two classes: sin (label 0) and cos (label 1)
n_per_class = 8
X_train = np.vstack([
    np.array([np.sin(2*np.pi*t + rng.uniform(-0.1,0.1)) for _ in range(n_per_class)]),
    np.array([np.cos(2*np.pi*t + rng.uniform(-0.1,0.1)) for _ in range(n_per_class)]),
])
y_train = np.array([0]*n_per_class + [1]*n_per_class, dtype=np.int64)
X_test  = X_train[:4]   # 4 test curves (n_test != n_train)

fit     = shapelet_transform_fit(X_train, y_train, n_shapelets=5, quality="info_gain")
X_feat  = shapelet_transform(fit, X_test)

sig     = sigma_gak(X_train)
K_train = gak_gram_matrix(X_train, sigma=sig)

clf     = shapelet_classifier_fit(X_train, y_train, n_shapelets=5,
                                  quality="info_gain", classifier="knn", k=3)
print(f"shapelet features shape: {X_feat.shape}")
print(f"GAK Gram shape:          {K_train.shape}")
print(f"classifier train_acc:    {clf.train_accuracy:.3f}  FDARS_FENCE_OK")
```

**Fixture note:** `shapelet_transform_fit` returns a `PyShapeletFit` opaque handle —
used only as input to `shapelet_transform(fit, data)`. The `shapelet_classifier_fit`
takes raw `data + labels` (not a `PyShapeletFit`) — independent fit path.
[VERIFIED: src/shapelet_mod.rs:389] Quality must be `"info_gain"` or `"f_statistic"`;
classifier must be `"knn"` or `"lda"`. Invalid strings raise `ValueError`.
[VERIFIED: Phase 71 verification]. `sigma_gak` returns a float bandwidth for use as
`sigma=` argument to other GAK functions.

---

## 3. STYLE_SPEC Diagram Rules

### Mandatory SVG Root Pattern

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 300" fill="none"
     role="img" aria-label="[text matching the .ttl text element]"
     aria-labelledby="NAME-title NAME-desc">
  <title id="NAME-title">[concise diagram name]</title>
  <desc id="NAME-desc">[1–2 sentences: what the diagram depicts and the method it illustrates]</desc>
  <style>
    .ttl{font:700 17px system-ui,-apple-system,sans-serif;fill:#1a1a2e}
    .sub{font:400 12px system-ui,sans-serif;fill:#6c757d}
    .lab{font:700 13px system-ui,sans-serif}
    .sm{font:400 11px system-ui,sans-serif;fill:#495057}
    .mono{font:600 12px ui-monospace,monospace}
  </style>
  ...
</svg>
```

[VERIFIED: docs/assets/diagrams/STYLE_SPEC.md:36-147]

### viewBox Rules

| viewBox | Height | Use when |
|---------|--------|---------|
| `0 0 720 300` | 300 | Standard single-row (most common — 64 of 93 diagrams) |
| `0 0 720 480` | 480 | Two-row layouts |
| `0 0 720 520` | 520 | Three-row layouts (1 diagram) |

**Fixed width is always 720.** [VERIFIED: docs/assets/diagrams/STYLE_SPEC.md:107-114]

### Typography (verbatim from STYLE_SPEC)

| Class | Rule |
|-------|------|
| `.ttl` | `font:700 17px system-ui,-apple-system,sans-serif;fill:#1a1a2e` — diagram title centered at y≈26 |
| `.sub` | `font:400 12px system-ui,sans-serif;fill:#6c757d` — subtitle at y≈46 |
| `.lab` | `font:700 13px system-ui,sans-serif` — fill set per element |
| `.sm`  | `font:400 11px system-ui,sans-serif;fill:#495057` |
| `.mono`| `font:600 12px ui-monospace,monospace` |

[VERIFIED: docs/assets/diagrams/STYLE_SPEC.md:40-58]

### Colour Palette (verbatim values)

| Hex | Role |
|-----|------|
| `#1a1a2e` | Title text (`.ttl`) |
| `#6c757d` | Subtitle, secondary (`.sub`) |
| `#495057` | `.sm` text, structural lines |
| `#ced4da` | Panel borders (`stroke`) |
| `#f8f9fa` | Panel fill (neutral panels) |
| `#fd7e14` | Orange accent — method/process panel stroke |
| `#fff4ea` | Fill on orange accent panels |
| `#f8d7b8` | Inner element borders in orange panels |

Data curve palette (FDARS_COLORS order): `#3f51b5` (indigo), `#e8710a` (orange),
`#198754` (green), `#dc3545` (red), `#6f42c1` (purple), `#0dcaf0` (cyan), `#6c757d` (grey)

[VERIFIED: docs/assets/diagrams/STYLE_SPEC.md:63-96]

### Stroke Weights

| Element | `stroke-width` |
|---------|---------------|
| Panel border (outer rect) | `1.5` |
| Axis / reference lines | `1.2` |
| Data curves (primary) | `2.0`–`2.8` |
| Data curves (secondary/faded) | `1.4`–`1.6` |
| Arrows | `2.0` |

[VERIFIED: docs/assets/diagrams/STYLE_SPEC.md:98-104]

### Panel Patterns

Neutral panel (grey background):
```xml
<rect x="24" y="70" width="196" height="188" rx="12"
      fill="#f8f9fa" stroke="#ced4da" stroke-width="1.5"/>
```

Method/process panel (orange accent):
```xml
<rect x="272" y="70" width="176" height="188" rx="12"
      fill="#fff4ea" stroke="#fd7e14" stroke-width="1.5"/>
```

[VERIFIED: docs/assets/diagrams/STYLE_SPEC.md:161-175]

### Diagram Embedding in Pages

Diagrams are stored as separate `.svg` files in `docs/assets/diagrams/` (NOT inline in
the `.md` file). They are referenced from the markdown page using the Material-theme
image syntax with a CSS class:

```markdown
![Family concept diagram](../assets/diagrams/[slug].svg){ .fdars-diagram }
```

[VERIFIED: docs/represent/depth-functions.md:6, docs/learn/smoothing.md:8]

The `.fdars-diagram` class is defined in `docs/stylesheets/extra.css` and controls sizing.

### SVGO-Idempotence Verification Protocol

The SVGO gate uses a **two-pass idempotence check** — never a direct diff against the
hand-authored source (svgo normalises whitespace/attribute ordering regardless of plugins).

**Exact command sequence for one diagram:**

```bash
FIRST=$(npx svgo@3.3.4 --config svgo.config.mjs --quiet \
         --input docs/assets/diagrams/[slug].svg --output -)
SECOND=$(printf '%s' "$FIRST" | \
         npx svgo@3.3.4 --config svgo.config.mjs --quiet \
         --input - --output -)
diff <(printf '%s' "$FIRST") <(printf '%s' "$SECOND")
# zero output = PASS (idempotent)
# non-zero output = FAIL (svgo would still transform on second pass)
```

**Pin: `npx svgo@3.3.4` — not `latest`** (svgo v4 has a different CLI/config API).
**Always pass `--config svgo.config.mjs`** — without it, `inlineStyles` converts CSS
classes to inline `style=` attributes, corrupting the class-based structure.
**Never use `--output <file>`** — always `--output -` (stdout only; D-02: never rewrite
committed hand-authored SVGs).

[VERIFIED: docs/assets/diagrams/STYLE_SPEC.md:16-33, svgo.config.mjs (project root)]

**The CI gate runs this loop** [VERIFIED: .github/workflows/docs.yml:53-63]:

```bash
FAILED=0
for svg in docs/assets/diagrams/*.svg; do
  first=$(npx svgo@3.3.4 --config svgo.config.mjs --quiet --input "$svg" --output -)
  second=$(printf '%s' "$first" | npx svgo@3.3.4 --config svgo.config.mjs --quiet --input - --output -)
  if ! diff <(printf '%s' "$first") <(printf '%s' "$second") >/dev/null; then
    echo "SVGO: $svg is not stable under svgo.config.mjs"
    FAILED=1
  fi
done
[ $FAILED -eq 0 ] || { echo "SVGO lint failed"; exit 1; }
```

### Concrete Existing Diagram as Pattern

`docs/assets/diagrams/clustering.svg` is a representative 720×480 diagram:
[VERIFIED: docs/assets/diagrams/clustering.svg:1-10]
- Root `<svg>` has `viewBox="0 0 720 480"`, `fill="none"`, `role="img"`, `aria-label`, `aria-labelledby`
- `<title id="...">` and `<desc id="...">` wired to `aria-labelledby`
- `<style>` block present with canonical five classes

---

## 4. Offline `--strict` Recipe

### Complete Command

```bash
cd /home/simonm/projects/rust/pyfda
PYTHONPATH=scripts .venv/bin/mkdocs build --strict
python scripts/check_docs_figures.py site
```

**Prerequisites:**
1. `.venv` active with `fdars` installed: `source .venv/bin/activate && maturin develop --release`
2. Docs deps installed: `pip install -r docs/requirements.txt` (includes `pydantic`, `anthropic`)
3. `DOCS_FAST` NOT set (unset for final gate)

**Why `PYTHONPATH=scripts`?** The hooks.py fallback adds `scripts/` to `sys.path` at build
start, but some markdown-exec execution contexts do not retain that insertion. The env var
is the canonical mechanism. [VERIFIED: docs/hooks.py:14-16, .github/workflows/docs.yml:84]

**Why `pydantic` in the docs venv?** Advisor fences execute `build_diagnostics()` at build
time (e.g. `docs/advisor/aspects.md:196-208`). The advisor imports pydantic for schema
validation on every code path. Missing pydantic → `ModuleNotFoundError` → traceback in HTML
→ `check_docs_figures.py` fails. [VERIFIED: docs/requirements.txt:17-21]

### Build Time Budget

- Typical `--strict` with all fences executing: **19–25+ min** on a fast laptop
- With 5 new submodule pages (7 new fences) added in Phase 73: budget **25–35 min**
- Per-page iteration with `DOCS_FAST=1`: **< 3 min** (fast() helpers lower iteration counts)

### How `--strict` Validates Fences

`--strict` does NOT enforce `FDARS_FENCE_OK` directly. What it does:
1. Fails on any MkDocs warning (broken links, missing pages referenced in nav)
2. Runs all `exec="1"` fences via markdown-exec (but a fence exception renders as a traceback, not a build failure)
3. `check_docs_figures.py site` catches the traceback-in-HTML case

So the gate is: `mkdocs build --strict` (nav/link correctness) → `check_docs_figures.py site`
(fence exceptions). Both must pass.

### DOCS_FAST for Per-Page Iteration

Set `DOCS_FAST=1` to activate `docs_fig.fast()` helpers:

```bash
DOCS_FAST=1 PYTHONPATH=scripts .venv/bin/mkdocs build
```

Or use `mkdocs serve` for live-reload (no `--strict`, no `check_docs_figures.py`):

```bash
DOCS_FAST=1 PYTHONPATH=scripts .venv/bin/mkdocs serve
```

Then open `http://127.0.0.1:8000` and navigate to the new page.

---

## 4b. aspects.md Update (DOCS-03)

### Structure Per Aspect

[VERIFIED: docs/advisor/aspects.md:1-702] — every aspect follows this structure:

1. **Coverage table row** (`## Coverage Table`): one row per aspect with columns:
   `| Aspect (method=) | fdars source(s) | Key diagnostics (count) | Offline fence |`

2. **Section heading** (`## aspect-name`): `## fts`, `## frechet`, etc.

3. **fdars source** line: "**fdars source:** `fdars.fts.ftsm`, `fdars.fts.stationarity_test`, ..."

4. **Key table**: one row per diagnostic key with columns `| Key | Meaning |`

5. **Task families** line: the three task strings for this aspect

6. **Optional fence** (if the aspect has one): `python exec="1" html="1" source="above"` ending with `FDARS_FENCE_OK`

### What Needs Adding / Extending

Based on Phase 72 verification [VERIFIED: phases/72-advisor-extension/72-VERIFICATION.md:24-29]:

**New aspects to add (new sections + new coverage table rows):**

- **`fts`** — 6 discriminated branches: stationarity/acf/dpca/fplsr/ftsm/forecast
  - fdars source: `fdars.fts.ftsm`, `fdars.fts.stationarity_test`, `fdars.fts.functional_acf`, `fdars.fts.dpca`, `fdars.fts.fplsr`
  - Add offline fence (small ftsm example ending with FDARS_FENCE_OK)

- **`frechet`** — diagnostics-only (NOT in `_RUNNABLE_METHODS`); 4 result shapes:
  array path + anova + global_reg + local_reg
  - fdars source: `fdars.frechet.frechet_mean`, `fdars.frechet.frechet_anova`, `fdars.frechet.frechet_global_reg`, `fdars.frechet.frechet_local_reg`
  - No online fence (diagnostics-only; offline fence acceptable)

**Existing aspects to extend (add new sub-tables):**

- **`regression`** — add FoF regression keys:
  - `has_fof_regression` — True when `"beta_surface"` key present AND `"fitted"` is 2D
  - `fof_r_squared` — scalar from `fof_regression` result
  - `beta_surface_shape` — list of 2 ints `[ncomp_x, ncomp_y]`
  [VERIFIED: phases/72-advisor-extension/72-VERIFICATION.md:74]

- **`spm`** — add mfpca branch keys:
  - `has_mfpca` — True when mfpca result dict is input (gating sentinel for spm_phase1 fields)
  - `mfpca_ncomp` — number of MFPCA components (from `len(eigenvalues)` in the mfpca result)
  - `mfpca_eigenvalues` — list of floats (from `result['eigenvalues']`)
  (Note: when `has_mfpca=True`, the spm_phase1 `ncomp` and `eigenvalues` keys are None — gated)
  (Note: mfpca result dict keys are `scores`, `eigenfunctions`, `eigenvalues`, `means`, `scales`,
   `grid_sizes` [VERIFIED: src/spm_mod.rs:915-946] — the advisor derives mfpca_ncomp from these)
  [VERIFIED: phases/72-advisor-extension/72-VERIFICATION.md:31,74]

- **`classification`** — shapelet-classifier guard clarification:
  - `elastic_multinomial` branch trigger: `"train_accuracy" in raw AND "n_shapelets" NOT in raw`
  (Phase 72 CR-01 fix — shapelet classifier must not spuriously trigger `has_elastic_multinomial`)
  [VERIFIED: phases/72-advisor-extension/72-VERIFICATION.md:30]

**Coverage table position:** Insert `fts` and `frechet` rows after `fpca` row (alphabetical
within the existing ordering convention). Insert `spe_multivariate` under spm fdars sources.

---

## 5. REL-01 Mechanics

### Exact Files and Lines to Edit

**Cargo.toml line 3** [VERIFIED: Cargo.toml:3]:
```toml
version = "0.9.0"
```
Change to:
```toml
version = "0.10.0"
```

**pyproject.toml line 7** [VERIFIED: pyproject.toml:7]:
```toml
version = "0.9.0"
```
Change to:
```toml
version = "0.10.0"
```

No other files need a version edit — maturin derives the package version from pyproject.toml,
and classifiers are not version-pinned.

### Tag → Publish Trigger

[VERIFIED: .github/workflows/publish.yml:6-9]

The publish workflow fires on:
```yaml
on:
  push:
    tags:
      - "v[0-9]+.[0-9]+.[0-9]+"
```

Tag `v0.10.0` matches this regex. Milestone tag `v11.0` does NOT match (only 2 numeric
segments), so it will not trigger a publish. The correct semver tag is `v0.10.0`.

The publish workflow (publish.yml) builds wheels for linux x86_64/aarch64, macos x86_64/aarch64,
windows x86_64, plus an sdist — then publishes all to PyPI via
`pypa/gh-action-pypi-publish`. This is an **outward-facing, irreversible action**.

### HUMAN-GATED Checkpoint Sequencing

The planner MUST sequence as follows:
1. Author all pages and diagrams (DOCS-01, DOCS-02)
2. Update aspects.md (DOCS-03)
3. Run ONE `mkdocs build --strict` gate — verify green
4. `checkpoint:human-review` — PAUSE for user diagram method-accuracy review
5. After user approves: edit `Cargo.toml` + `pyproject.toml` (version bump)
6. `checkpoint:human-release` — PAUSE; user runs `git tag v0.10.0 && git push origin v0.10.0`
   (the tag triggers the publish workflow autonomously in CI)

**Do NOT create the tag or push it autonomously.** Do NOT run `git tag` or `git push --tags`.

---

## 6. Recommended Plan Shape (Sequencing)

```
Wave 1 (per-family, sequential):
  For each of 7 families:
    T1: Author docs/<section>/<family>.md (page + fence + API table)
    T2: Author docs/assets/diagrams/<family>.svg (hand-authored inline SVG)
    T3: Wire into mkdocs.yml nav (add nav entry, verify DOCS_FAST build passes)

Wave 2 (aspects + gate):
  T8: Update docs/advisor/aspects.md (add fts + frechet sections + coverage rows;
      extend regression/spm/classification sub-tables)
  T9: Run final mkdocs build --strict + check_docs_figures.py — gate must be green

Wave 3 (human gates — PAUSE points, not autonomous):
  CHECKPOINT: human diagram method-accuracy review (DOCS-03 blocking gate)
  After approval:
  T10: Bump version (Cargo.toml:3 + pyproject.toml:7, 0.9.0 → 0.10.0)
  CHECKPOINT: human release (user triggers git tag v0.10.0 + push)
```

**Why sequential for Wave 1?** The 73-CONTEXT.md decision: `use_worktrees: false`. Nav edits
to `mkdocs.yml` would conflict across parallel worktrees.

**DOCS_FAST during authoring:** Use `DOCS_FAST=1 PYTHONPATH=scripts .venv/bin/mkdocs build`
(or `mkdocs serve`) per page. Build only the affected page in isolation if possible by
temporarily removing other nav entries. Only run full `--strict` once at T9.

**Diagram authoring workflow (from memory/v7.0 pattern):**
1. Write SVG by hand in `docs/assets/diagrams/<slug>.svg`
2. Verify SVGO idempotence: run the two-pass diff locally
3. Visual check: `rsvg-convert -w 720 docs/assets/diagrams/<slug>.svg -o /tmp/<slug>.png`
   (requires `rsvg-convert` from `librsvg`; `convert` from ImageMagick also works)
4. Commit only after visual + SVGO checks pass

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead |
|---------|-------------|-------------|
| Inline matplotlib figures | Custom SVG rendering code | `docs_fig.fig()` + `docs_fig.render(f)` with `html="1"` fence option |
| SVGO SVG lint | Custom XML checker | `npx svgo@3.3.4 --config svgo.config.mjs` two-pass idempotence |
| Fence exception detection | Parse stdout manually | `python scripts/check_docs_figures.py site` (already in docs.yml) |
| Fast/full iteration toggle | `os.environ` checks per block | `docs_fig.fast(full_val, fast_val)` helper |

---

## Common Pitfalls

### Pitfall 1: Missing `PYTHONPATH=scripts`
**What goes wrong:** Fences fail with `ModuleNotFoundError: No module named 'docs_fig'`.
**Why it happens:** hooks.py adds `scripts/` to sys.path only for some exec contexts.
**How to avoid:** Always prefix with `PYTHONPATH=scripts` in the build command.
**Warning signs:** Traceback-in-HTML containing `docs_fig` or `docs_data`.

### Pitfall 2: `pydantic` not in docs venv
**What goes wrong:** Advisor-page fences raise `ModuleNotFoundError: No module named 'pydantic'`.
**Why it happens:** `docs/requirements.txt` includes pydantic but a fresh venv may have
been created without installing all requirements. CI catches this; local builds miss it.
**How to avoid:** Always install with `pip install -r docs/requirements.txt` before building.
**Warning signs:** Traceback in `docs/advisor/` pages in the built site.

### Pitfall 3: Square fixture hiding transposition bugs
**What goes wrong:** A fence with `n=30, m=30` runs without error but the output is silently
transposed — the FoF beta_surface is (m,n) instead of (ncomp_x, ncomp_y).
**How to avoid:** Use non-square data (`n != m`) in every fence involving 2D input.
This is a standing project convention. [Phase decisions 67-01, 68-01]

### Pitfall 4: DOCS_FAST=1 left on for the final gate
**What goes wrong:** `--strict` build passes but fences use reduced iteration counts,
producing figures that look rough and may emit incorrect `FDARS_FENCE_OK` markers.
**How to avoid:** Run the final gate with `DOCS_FAST` unset. Use `DOCS_FAST=1` only during
authoring iteration.

### Pitfall 5: SVGO pin forgotten
**What goes wrong:** `npx svgo` (no version pin) uses svgo v4, which has a different CLI
(`--config` flag may be ignored; `inlineStyles` converts CSS classes to inline attributes).
**How to avoid:** Always use `npx svgo@3.3.4 --config svgo.config.mjs`.

### Pitfall 6: Tagging autonomously
**What goes wrong:** `git tag v0.10.0 && git push origin v0.10.0` triggers an irreversible
PyPI publish. A mistake in the version bump or package content cannot be undone.
**How to avoid:** The planner MUST NOT include an autonomous `git tag` task. The release
checkpoint is human-gated.

### Pitfall 7: `frechet_mean` return type
**What goes wrong:** Code tries to access `result['key']` on the frechet_mean return value,
but `frechet_mean` returns a raw array (not a dict) for the SPD space.
**How to avoid:** `frechet_mean` returns the mean object directly (array for SPD, list of
arrays for other spaces). Only `frechet_global_reg`, `frechet_local_reg`, and `frechet_anova`
return dicts. [VERIFIED: src/frechet_mod.rs:344-489]

### Pitfall 8: nav entries before page files exist
**What goes wrong:** Adding a nav entry to `mkdocs.yml` before the `.md` file exists causes
`--strict` to fail (broken nav link is a warning→error under `--strict`).
**How to avoid:** Create the `.md` file first (even a stub), then add to mkdocs.yml nav,
then iterate on the content.

### Pitfall 9: mfpca takes a list, not a stacked array
**What goes wrong:** `mfpca([V1, V2])` works but `mfpca(np.stack([V1, V2]))` fails because
the function signature accepts `Vec<PyReadonlyArray2>` (Python list), not a 3D array.
**How to avoid:** Always pass a Python list of 2D arrays to `mfpca` and `spe_multivariate`.
[VERIFIED: src/spm_mod.rs:882-913]

---

## Validation Architecture

> `workflow.nyquist_validation` not explicitly set to false in config — treated as enabled.
> However, Phase 73 is a documentation + version-bump phase with no new Python/Rust code.
> All fences ARE the tests: each fence executes live fdars code and asserts a result.

### Test Framework
| Property | Value |
|----------|-------|
| Framework | markdown-exec (build-time fence execution) + `check_docs_figures.py` |
| Config file | `mkdocs.yml` (plugins: markdown-exec) |
| Quick run command | `DOCS_FAST=1 PYTHONPATH=scripts .venv/bin/mkdocs build` |
| Full suite command | `PYTHONPATH=scripts .venv/bin/mkdocs build --strict && python scripts/check_docs_figures.py site` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | Notes |
|--------|----------|-----------|-------------------|-------|
| DOCS-01 | Each page fence executes without error, prints FDARS_FENCE_OK | build-time execution | `mkdocs build --strict && check_docs_figures.py site` | No separate pytest; fence IS the test |
| DOCS-02 | Diagrams pass SVGO idempotence | lint | SVGO two-pass loop in docs.yml | Run locally before committing each diagram |
| DOCS-03 | Whole-site `--strict` green | integration | Same as DOCS-01 command | Run once at end |
| REL-01 | Version in Cargo.toml + pyproject.toml is 0.10.0 | manual verify | `grep 'version' Cargo.toml pyproject.toml` | No automated test needed |

### Sampling Rate
- **Per page (authoring):** `DOCS_FAST=1 PYTHONPATH=scripts .venv/bin/mkdocs build`
- **Per wave merge:** n/a (sequential phase, no worktrees)
- **Phase gate:** `PYTHONPATH=scripts .venv/bin/mkdocs build --strict && python scripts/check_docs_figures.py site`

### Wave 0 Gaps

- [ ] 7 new `.md` files (stubs must exist before nav entries)
- [ ] 7 new `.svg` diagram files in `docs/assets/diagrams/`
- [ ] `mkdocs.yml` nav entries (7 new lines)
- [ ] `docs/advisor/aspects.md` updated sections

*(No test framework install needed — markdown-exec and docs deps already in requirements.txt)*

---

## Security Domain

> `security_enforcement` not explicitly set to false — treated as enabled.

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | No | Documentation phase — no auth |
| V3 Session Management | No | Static site |
| V4 Access Control | No | No access control layer |
| V5 Input Validation | Minimal | Fence code inputs are hardcoded fixtures |
| V6 Cryptography | No | Not applicable |

**Only security-relevant concern:** The PyPI publish is an irreversible supply-chain action.
The human gate (checkpoint before `git tag`) is the correct control. No additional security
controls apply to the documentation authoring work.

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | ~~`mfpca` key names unverified~~ — RESOLVED: keys are `scores`, `eigenfunctions`, `eigenvalues`, `means`, `scales`, `grid_sizes` (no `n_comp` key) [VERIFIED: src/spm_mod.rs:915-946] | Family E template | N/A — resolved |
| A2 | `fof_re_regression` and `predict_fof_re` exist as separate Python-callable functions under `fdars.regression` | Family B template | ImportError in fence; verify with `dir(fdars.regression)` |
| A3 | `lqd_fpca` dict key `n_comp` (not `ncomp`) — Phase 69 decision states "6-key PyDict" with `loadings` (not rotation) — confirmed; n_comp key name assumed from Phase 69 context | Family D template | Fence would raise KeyError |
| A4 | The two SoF pages (fof.md and additive-sof.md) vs. one combined page — exact nav entry names are Claude's discretion; no user decision on whether to split | Section 6 sequencing | Minor: planner chooses; both options are consistent with "slot into existing sections" |

**If A1 is wrong:** Read `src/spm_mod.rs:909-975` to find the exact key names before writing
the mfpca fence.

---

## Open Questions

1. **mfpca exact key names** — RESOLVED
   - What we know: `mfpca()` returns keys: `scores`, `eigenfunctions`, `eigenvalues`, `means`, `scales`, `grid_sizes` [VERIFIED: src/spm_mod.rs:915-946]. No `n_comp` key. The `ncomp` parameter controls the number of components requested; the result has `eigenvalues` of that length.
   - No action needed.

2. **One FoF+SoF page vs. two pages**
   - What we know: user said "Regression gets Function-on-Function, Additive/Generalized SoF"
   - What's unclear: whether these are one page or two nav entries
   - Recommendation: two separate pages (FoF methods are conceptually distinct from additive SoF)

3. **GAK on Distance Metrics page vs. Shapelets page**
   - What we know: user said "GAK folds into the Shapelets page (or Distance Metrics)"
   - What's unclear: which page gets it
   - Recommendation: fold GAK into the Shapelets page (they're both time-series similarity methods); add a note to the Distance Metrics page pointing there

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| `.venv` with `fdars` | Fence execution | ✓ | maturin develop (current) | None — must rebuild |
| `PYTHONPATH=scripts` | `docs_fig`, `docs_data` | ✓ | n/a (env var) | hooks.py fallback (unreliable) |
| `pydantic>=2.0` | Advisor fences | ✓ | in docs/requirements.txt | None — install required |
| `npx svgo@3.3.4` | SVGO idempotence gate | Needs npm/npx | 3.3.4 pinned | None for the CI gate; local skippable |
| `rsvg-convert` | Visual SVG check | May not be installed | — | `convert` (ImageMagick) or browser open |
| `mkdocs + markdown-exec` | Build | ✓ | in docs/requirements.txt | — |

---

## Sources

### Primary (HIGH confidence)
- `docs/hooks.py` — fence execution environment; PYTHONPATH behavior [VERIFIED this session]
- `docs/represent/depth-functions.md` — canonical FDARS_FENCE_OK fence template [VERIFIED]
- `docs/advisor/aspects.md` — aspects structure per section [VERIFIED: full file read]
- `docs/assets/diagrams/STYLE_SPEC.md` — all diagram rules [VERIFIED: full file read]
- `docs/assets/diagrams/clustering.svg` — concrete SVG structure [VERIFIED]
- `mkdocs.yml` — nav structure; markdown-exec plugin config [VERIFIED]
- `.github/workflows/docs.yml` — SVGO gate loop; build command [VERIFIED]
- `.github/workflows/publish.yml` — semver tag trigger pattern [VERIFIED]
- `Cargo.toml:1-3` — current version field [VERIFIED]
- `pyproject.toml:1-7` — current version field [VERIFIED]
- `src/fts_mod.rs` — fts function signatures [VERIFIED]
- `src/frechet_mod.rs` — frechet function signatures and return types [VERIFIED]
- `src/density_fda_mod.rs` — density_fda function signatures [VERIFIED]
- `src/clustering_mod.rs` — advanced clustering signatures; dbscan noise-as-minus-1 [VERIFIED]
- `src/shapelet_mod.rs` — shapelet function signatures; enum dispatch [VERIFIED]
- `src/metric_mod.rs` — GAK function signatures [VERIFIED]
- `src/spm_mod.rs:882-975` — mfpca + spe_multivariate functions [VERIFIED]
- `src/scalar_on_function_mod.rs:76-490` — SoF function signatures [VERIFIED]
- `src/regression_mod.rs:1276-1650` — FoF function signatures; PyDict keys [VERIFIED]
- `scripts/check_docs_figures.py` — FDARS_FENCE_OK enforcement mechanism [VERIFIED]
- `scripts/docs_fig.py` — DOCS_FAST mechanism; render() pattern [VERIFIED]
- `docs/requirements.txt` — pydantic/anthropic in docs env [VERIFIED]
- Phase 71 VERIFICATION.md — shapelet enum error messages; PyShapeletFit behavior [VERIFIED]
- Phase 72 VERIFICATION.md — aspects added; advisor key names; Phase 72 decisions [VERIFIED]

### Secondary (MEDIUM confidence)
- STATE.md blockers — build time estimates (19–25 min) [CITED: .planning/STATE.md]
- REQUIREMENTS.md — requirement descriptions [CITED: .planning/REQUIREMENTS.md]
- 73-CONTEXT.md — user decisions and discretion areas [CITED: .planning/phases/73-documentation-release/73-CONTEXT.md]

---

## Metadata

**Confidence breakdown:**
- Fence mechanism: HIGH — hooks.py, depth-functions.md, aspects.md all read this session
- STYLE_SPEC diagram rules: HIGH — STYLE_SPEC.md read in full this session
- Per-family API signatures: HIGH — all Rust source files read this session (except mfpca key names: MEDIUM)
- --strict recipe: HIGH — docs.yml and check_docs_figures.py read this session
- aspects.md structure: HIGH — full file read this session
- REL-01 mechanics: HIGH — publish.yml and exact file lines verified this session

**Research date:** 2026-09-04
**Valid until:** Stable — this is a closing docs phase; no upstream changes expected before execution
