# fdars (Python) → R Parity Plan

**Finding:** `fdars-core` (Rust) is already at ~full R parity. Python exposes 264 of
~315 R capabilities. The remaining gap is **~100 missing bindings over existing core**
plus a small set of pure-Python layers and — most importantly — an **ergonomics layer**
(result objects + plotting) that R has and Python lacks. This is mostly mechanical
binding work, not algorithm implementation.

Baseline: Python 264 fns / 16 modules · R 315 exports / 36 source files · core has the algorithms.

---

## PROGRESS (branch feat/r-parity-phase1)

**Phase 4 — ergonomics: DONE.** fdars.datasets (6 datasets in wheel), fdars.plot
(8 matplotlib plotters, optional extra), fdars.results (result objects with
.predict/.summary), Fdata methods (concat/int_simpson/2-D norm/scale_minmax/to_pc/to_basis),
submodules exposed as attributes.

**Phase 1 — bindings landed (batches A–G):**
- A: depth.random_projection_deriv_1d, metric.int_simpson, metric.inprod,
  explain.andrews_transform/andrews_loadings
- B: seasonal.estimate_period_acf, seasonal.detect_multiple_periods
- C: alignment.detect_landmarks / landmark_register / landmark_detect_and_register
- D: regression.fregre_np_cv, regression.fregre_np_mixed
- E: spm.spm_cusum, spm.spm_ewma, spm.t2_limit_robust, spm.spe_limit_robust
- F: alignment.elastic_changepoint (amplitude/phase/fpca)
- G (pure-Python): fdars.metrics (pred.*), fdars.covariance (8 kernels + compose +
  make_gaussian_process + r_brownian/r_bridge/r_ou), clustering.cluster_optim/cluster_init
Each batch numerically validated; all 61 existing tests still pass.

**Remaining (Phase 2 subsystems + Phase 3 — not yet done):**
- irregular functional data (fdars.irreg over irreg_fdata/) — L
- functional mixed models (famm.rs) — L
- 2D FOSR (function_on_scalar_2d.rs) — L
- SPM: MEWMA, AMEWMA, iterative Phase-I, partial/FRCC/profile/elastic monitoring,
  mfpca (need multi-matrix / chart-state design) — L
- scalar_on_shape (config struct + chained predict) — M
- fdars.tests module (flm.test, fmean.test, group.test/distance, fmm.test.fixed) — M
- generic/CV conformal wrappers (jackknife+, cv-conformal, generic) — M
- misc: fregre.pc/basis variants, elastic.attribution, fdata.bootstrap, depth-outlier
  pond/trim/boxplot (pure-Python) — S/M

---

---

## Phase 1 — Quick-win bindings (core exists, thin PyO3 wrappers) — effort S

Bind functions whose Rust core already exists; each is a `#[pyfunction]` + re-export.

- **depth:** `random_projection_deriv` (RPD, `rpd_depth_1d_seeded`), streaming depth batch/vs-ref/one (`streaming_depth/`).
- **outliers:** `depth_pond`, `depth_trim`, `boxplot`, `outlier_summary`.
- **fdata/metric:** `int_simpson`, `inprod`, `fdata_gradient`, `localavg`, `register` (shift), `pred_mae/mse/rmse/r2`.
- **simulation:** `r_ou`, `r_brownian`, `r_bridge`, `sim_multi_fun_data` (multivariate).
- **smoothing:** `cv_s`, `gcv_s`, `local_constant_regression`, weighting-kernel primitives (`Ker.*`).
- **alignment:** `andrews_transform`, `andrews_loadings` (core `andrews.rs`), `tsrvf_from_alignment`, `tsrvf_inverse`, `shape_representative`, `diagnose_alignment_pairwise`.
- **clustering:** `cluster_optim`, `cluster_init` (k-means++).
- **spm:** `spm_rules`, `spm_limit_robust`, `spm_contributions`.
- **seasonal:** `estimate_period` (ACF path), `detect_period` dispatcher.

Deliverable: ~35 new bindings. Target Python 264 → ~300.

## Phase 2 — Missing subsystems with core backing (bind + Python wrapper) — effort M/L

Each maps to an existing core module; needs a binding set + a Python-facing wrapper/object.

- **Irregular functional data** (`irreg_fdata/`): `IrregFdata` container + construct/`is_irregular`/`as_fdata`/`sparsify`/int/norm/mean/lp/standardize. **New `fdars.irreg` module.** (L)
- **Functional mixed models** (`famm.rs`): `fmm`, `fmm_predict`, `fmm_test_fixed`. (L)
- **2D function-on-scalar** (`function_on_scalar_2d.rs`): `fosr_2d`. (L)
- **SPM monitoring** (`spm/{cusum,ewma,mewma,amewma,partial,frcc,profile,elastic_spm}.rs`):
  `spm_cusum/ewma/mewma/amewma`, `spm_arl`, `spm_phase1_iterative`, `spm_monitor_partial[_batch]`,
  `frcc_phase1/monitor`, `spm_profile_phase1/monitor`, `spm_elastic_phase1/monitor`, `mfpca`. (L)
- **Landmark registration** (`landmark.rs`): `landmark_register`, `detect_landmarks`. (M)
- **Elastic suite** (`elastic_changepoint.rs`, `alignment/clustering.rs`, `elastic_regression`, `scalar_on_shape`):
  `elastic_changepoint`, `elastic_kmeans/hclust/cutree`, `elastic_pcr`, `scalar_on_shape` (+predict). (M)
- **Regression variants** (`scalar_on_function/`): `fregre_pc`, `fregre_basis[_cv]`, `fregre_pc_cv`,
  `fregre_np_cv/multi/mixed`, `fregre_lm_cv`, `rp_stat`, generic `cv_fdata` driver. (M)
- **Seasonal:** `detrend` (detrend/*), `decompose`, `detect_periods`, `detect_amplitude_modulation`. (M)
- **explain:** `elastic_attribution` (amp vs phase importance). (M)

## Phase 3 — Pure-Python layers (little/no core) — effort M

- **`fdars.covariance` module:** kernel constructors (`kernel_gaussian/exponential/matern/brownian/
  linear/polynomial/whitenoise/periodic`), `kernel_add/mult`, `make_gaussian_process` (1D/2D, function mean).
  Thin over core `CovKernel` where present; compose in Python.
- **`fdars.tests` module:** `flm_test` (needs `compute_adot`/`pcvm_statistic` bindings), `fmean_test`,
  `group_test`, `group_distance`, `fmm_test_fixed`.
- **conformal:** `jackknife_plus`, `cv_conformal_regression/classification`,
  `conformal_generic_regression/classification`.
- **fdata:** `bootstrap`, `bootstrap_ci`.

## Phase 4 — Ergonomics parity (the biggest UX gap) — effort L

R ships 184 S3 methods; Python returns 163 plain dicts. Close this to make the API idiomatic.

- **Result objects:** wrap fitted-model dicts in lightweight Python classes (`FregreLM`, `FPCA`,
  `AlignmentResult`, `SPMChart`, …) with `.predict(newdata)`, `.summary()`, `__repr__`, `.coef()`.
  Prediction becomes `fit.predict(x)` instead of `predict_fregre_lm(fit_dict, x)`.
- **Plotting layer:** `fdars.plot` (matplotlib) — `plot(Fdata)`, FPCA components, alignment before/after,
  SPM charts, outliergram, tolerance bands, STL. Optional extra `fdars[plot]`.
- **`Fdata` gaps:** `concat`/`c()`/append, 2-D `norm`, `int_simpson` method, `scale_minmax`,
  method-style `to_pc/to_pls/to_basis`.
- **`fdars.datasets`:** promote `scripts/docs_data.py` loaders into the installed package, returning
  `Fdata` objects (ship the vendored CSVs as package data).

---

## Recommended sequencing

1. **Phase 1** first — fast, mechanical, biggest parity jump per hour; raises count to ~300.
2. **Phase 4 result-objects + plotting** early-ish — it's what users actually feel as "not on par."
3. **Phase 2 subsystems** by demand (irregFdata + SPM monitoring likely highest value).
4. **Phase 3** pure-Python modules alongside.

Each phase: add bindings in `src/*_mod.rs`, register in `python/fdars/__init__.py`, add a docs page +
build-time figure, `maturin develop` + smoke-test, then bump the `fdars` release.

Verification harness: extend `scripts/` with an `api_parity.py` that diffs the live Python surface
against `r_exports.txt` and reports the remaining gap count (a moving parity scoreboard).
