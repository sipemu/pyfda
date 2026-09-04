"""fdars.advisor.aspects.regression — Regression diagnostics builder.

Contains ``_build_regression_diagnostics``.  Accepts any fdars regression
result dict produced by ``fregre_lm``, ``fregre_pls``, ``fregre_l1``,
``fregre_huber``, ``fregre_np``, ``fosr``, ``fosr_fpc``,
``fof_regression``, ``fof_re_regression``, ``fam``, ``fregre_gkam``,
``fregre_gsam``.

Key corrections applied here (see 21-RESEARCH §2):
- Correction #3: ``r_squared`` is NOT always present.  ``fregre_l1`` and
  ``fregre_huber`` do not return it.  Guarded with ``if "r_squared" in raw``.
- Correction #4: ``fosr``/``fosr_fpc`` return 2-D residuals of shape (n, m).
  Residual summary statistics (mean/std/max_abs/skew) are only computed when
  ``np.ndim(residuals) == 1``.
- Correction #5: ``fosr``/``fosr_fpc`` use the key ``"fitted"`` (not
  ``"fitted_values"``).  ``has_fosr`` detects this by checking for the
  ``"fitted"`` key AND verifying the array is 2-D.

All values in the returned dict are native Python types (float, int, bool,
list, None).  No NumPy scalars.  Two calls on the same input always return
an equal, JSON-serialisable dict.
"""

from __future__ import annotations

import numpy as np


def _build_regression_diagnostics(raw, **kwargs) -> dict:
    """Compute regression diagnostics from an fdars regression result dict.

    Parameters
    ----------
    raw : dict
        Native fdars output dict from any of: ``fregre_lm``, ``fregre_pls``,
        ``fregre_l1``, ``fregre_huber``, ``fregre_np``, ``fosr``,
        ``fosr_fpc``, ``functional_glm``, ``concurrent_regression``.
        Keys vary by function — all accesses are guarded.
    **kwargs
        Reserved for future per-method options (ignored).

    Returns
    -------
    dict
        Plain-Python dict with JSON-serialisable values (``float``, ``int``,
        ``bool``, ``list``, ``None``).  No NumPy scalars.  Fields:

        - method (str): always ``"regression"``
        - n_obs (int): number of observations, inferred from the fitted array
        - r_squared (float or None): None when key absent (fregre_l1/huber)
        - residual_mean (float or None): mean of residuals when 1-D only
        - residual_std (float or None): std of residuals when 1-D only
        - residual_max_abs (float or None): max absolute residual when 1-D only
        - residual_skew (float or None): pure-NumPy skewness when 1-D only
        - beta_t_range (list[float] or None): [min, max] when ``"beta_t"`` present
        - has_fosr (bool): True only when ``"fitted"`` key is present AND
          the array is 2-D (ndim==2); 1-D ``"fitted"`` arrays yield False
        - has_functional_glm (bool): True when ``"deviance"`` key is present
          (unique to ``functional_glm``)
        - deviance (float or None): model fit measure (lower = better)
        - aic (float or None): Akaike information criterion
        - bic (float or None): Bayesian information criterion
        - log_likelihood (float or None): log-likelihood at convergence
        - iterations (int or None): IRLS iteration count to convergence
        - glm_ncomp (int or None): number of FPC components used
        - family (str or None): exponential-family distribution name
        - has_concurrent_regression (bool): True when ``"beta_curve"`` key is
          present (unique to ``concurrent_regression``)
        - concurrent_residual_rms (float or None): root-mean-squared residual
          over the full n x m grid; ``None`` when residuals are absent
        - concurrent_residual_max_abs (float or None): max absolute residual
          over the full grid; ``None`` when residuals are absent
        - n_predictors (int or None): number of functional predictor curves
    """
    diag: dict = {"method": "regression"}

    # ------------------------------------------------------------------
    # n_obs — infer from fitted_values (scalar-response variants) or
    # fitted (fosr/fosr_fpc function-on-scalar/function-on-function).
    # ------------------------------------------------------------------
    if "fitted_values" in raw:
        diag["n_obs"] = int(np.asarray(raw["fitted_values"]).shape[0])
    elif "fitted" in raw:
        diag["n_obs"] = int(np.asarray(raw["fitted"]).shape[0])
    else:
        diag["n_obs"] = None

    # ------------------------------------------------------------------
    # r_squared — guarded (correction #3).
    # fregre_l1 and fregre_huber do NOT return this key.
    # ------------------------------------------------------------------
    diag["r_squared"] = (
        float(raw["r_squared"]) if "r_squared" in raw else None
    )

    # ------------------------------------------------------------------
    # Residual summary statistics — only when residuals are 1-D
    # (correction #4).
    #
    # fosr/fosr_fpc return residuals of shape (n, m) — computing
    # np.mean over a 2-D array would silently produce a wrong scalar.
    # The ndim==1 guard prevents that.
    # ------------------------------------------------------------------
    res = np.asarray(raw.get("residuals", []))
    if res.ndim == 1 and res.size > 0:
        r = res  # alias for readability
        diag["residual_mean"] = float(np.mean(r))
        diag["residual_std"] = float(np.std(r))
        diag["residual_max_abs"] = float(np.max(np.abs(r)))
        # Pure-NumPy skewness (no scipy): m3 / m2^1.5
        # m3 = third central moment; m2 = variance
        m3 = float(np.mean((r - r.mean()) ** 3))
        m2 = float(np.var(r))
        diag["residual_skew"] = float(m3 / m2 ** 1.5) if m2 > 0.0 else 0.0
    else:
        diag["residual_mean"] = None
        diag["residual_std"] = None
        diag["residual_max_abs"] = None
        diag["residual_skew"] = None

    # ------------------------------------------------------------------
    # beta_t_range — only when "beta_t" key is present.
    # fregre_np does not return beta_t; fosr/fosr_fpc use "beta" instead.
    # ------------------------------------------------------------------
    if "beta_t" in raw:
        bt = np.asarray(raw["beta_t"], dtype=float)
        diag["beta_t_range"] = [float(np.min(bt)), float(np.max(bt))]
    else:
        diag["beta_t_range"] = None

    # ------------------------------------------------------------------
    # has_fosr — True ONLY when "fitted" key is present AND the array
    # is 2-D (correction #5).
    #
    # fosr/fosr_fpc are the ONLY regression variants that return a 2-D
    # "fitted" array (function-on-scalar / function-on-function regression
    # where the response is itself a function of shape (n, m)).
    # Scalar-response variants (fregre_lm/pls/l1/huber/np) return a 1-D
    # "fitted_values" array and NO 2-D "fitted" key — hence the ndim==2
    # test on the "fitted" key is what distinguishes fosr, and a 1-D
    # "fitted" value yields has_fosr=False.
    # Note: concurrent_regression also has a 2-D "fitted" array so
    # has_fosr is True for concurrent_regression too — a known documented
    # overlap.  has_concurrent_regression is the specific discriminator.
    # ------------------------------------------------------------------
    has_fosr = (
        "fitted" in raw
        and np.asarray(raw["fitted"]).ndim == 2
    )
    diag["has_fosr"] = bool(has_fosr)

    # ------------------------------------------------------------------
    # functional_glm branch (ADV-05)
    # Trigger: "deviance" in raw — unique to functional_glm among all
    # existing regression result shapes.  None of fregre_lm/pls/l1/
    # huber/np/fosr/fosr_fpc expose a "deviance" key.
    #
    # CRITICAL: The key is "iterations" (int), NOT "n_iter"; there is
    # NO "converged" key in the shipped dict (regression_mod.rs:1112).
    # ------------------------------------------------------------------
    has_functional_glm = "deviance" in raw
    diag["has_functional_glm"] = bool(has_functional_glm)
    if has_functional_glm:
        diag["deviance"] = float(raw["deviance"])
        diag["aic"] = float(raw["aic"]) if "aic" in raw else None
        diag["bic"] = float(raw["bic"]) if "bic" in raw else None
        diag["log_likelihood"] = (
            float(raw["log_likelihood"]) if "log_likelihood" in raw else None
        )
        diag["iterations"] = int(raw["iterations"]) if "iterations" in raw else None
        diag["glm_ncomp"] = int(raw["ncomp"]) if "ncomp" in raw else None
        diag["family"] = str(raw["family"]) if "family" in raw else None
    else:
        diag["deviance"] = None
        diag["aic"] = None
        diag["bic"] = None
        diag["log_likelihood"] = None
        diag["iterations"] = None
        diag["glm_ncomp"] = None
        diag["family"] = None

    # ------------------------------------------------------------------
    # concurrent_regression branch (ADV-05)
    # Trigger: "beta_curve" in raw — unique to concurrent_regression;
    # fosr/fosr_fpc use "beta" not "beta_curve".
    # residuals are 2-D (n, m) — the existing ndim==1 guard correctly
    # leaves residual_mean/std/skew as None.  This branch adds a 2-D
    # summary: residual_rms (overall fit quality) and n_predictors.
    # has_fosr is also True for concurrent_regression (2-D "fitted") —
    # has_concurrent_regression is the specific discriminator.
    # ------------------------------------------------------------------
    has_concurrent_regression = "beta_curve" in raw
    diag["has_concurrent_regression"] = bool(has_concurrent_regression)
    if has_concurrent_regression:
        res_2d = np.asarray(raw.get("residuals", np.zeros((0, 0))))
        if res_2d.ndim == 2 and res_2d.size > 0:
            diag["concurrent_residual_rms"] = float(
                np.sqrt(np.mean(res_2d ** 2))
            )
            diag["concurrent_residual_max_abs"] = float(np.max(np.abs(res_2d)))
        else:
            diag["concurrent_residual_rms"] = None
            diag["concurrent_residual_max_abs"] = None
        beta_curve = np.asarray(raw["beta_curve"])
        diag["n_predictors"] = int(beta_curve.shape[0])
    else:
        diag["concurrent_residual_rms"] = None
        diag["concurrent_residual_max_abs"] = None
        diag["n_predictors"] = None

    # ------------------------------------------------------------------
    # fof_regression branch (ADV-01 Phase 72)
    # Trigger: "beta_surface" in raw — unique to fof/fof_re_regression.
    # Existing regression variants use "beta_t" or "beta", never "beta_surface".
    # CONFIRMED keys from src/regression_mod.rs:1295-1304.
    # ------------------------------------------------------------------
    has_fof_regression = "beta_surface" in raw
    diag["has_fof_regression"] = bool(has_fof_regression)
    if has_fof_regression:
        bs = np.asarray(raw["beta_surface"])
        diag["beta_surface_shape"] = [int(bs.shape[0]), int(bs.shape[1])]
        diag["beta_surface_max_abs"] = float(np.max(np.abs(bs)))
        diag["fof_r_squared"] = (
            float(raw["r_squared"]) if "r_squared" in raw else None
        )
        if "ncomp_x" in raw and "ncomp_y" in raw:
            diag["fof_ncomp"] = [int(raw["ncomp_x"]), int(raw["ncomp_y"])]
        else:
            diag["fof_ncomp"] = None
    else:
        diag["beta_surface_shape"] = None
        diag["beta_surface_max_abs"] = None
        diag["fof_r_squared"] = None
        diag["fof_ncomp"] = None

    # ------------------------------------------------------------------
    # fof_re_regression branch (ADV-01 Phase 72)
    # Trigger: "random_effects" in raw AND "n_subjects" in raw — unique to
    # fof_re_regression. CONFIRMED keys from src/regression_mod.rs:1561-1564.
    # has_fof_regression is also True for fof_re (both share beta_surface).
    # has_fof_re_regression is the specific discriminator.
    # ------------------------------------------------------------------
    has_fof_re_regression = "random_effects" in raw and "n_subjects" in raw
    diag["has_fof_re_regression"] = bool(has_fof_re_regression)
    if has_fof_re_regression:
        diag["n_subjects"] = int(raw["n_subjects"])
        if "sigma2_u" in raw:
            diag["sigma2_u_max"] = float(np.max(np.asarray(raw["sigma2_u"])))
        else:
            diag["sigma2_u_max"] = None
        diag["sigma2_eps"] = (
            float(raw["sigma2_eps"]) if "sigma2_eps" in raw else None
        )
        if "random_effects" in raw:
            re = np.asarray(raw["random_effects"])
            diag["re_dims"] = [int(re.shape[0]), int(re.shape[1])]
        else:
            diag["re_dims"] = None
    else:
        diag["n_subjects"] = None
        diag["sigma2_u_max"] = None
        diag["sigma2_eps"] = None
        diag["re_dims"] = None

    # ------------------------------------------------------------------
    # fam / fregre_gsam branch (ADV-01 Phase 72)
    # Trigger: "component_fits" in raw AND "fitted_values" in raw — shared
    # by fam and fregre_gsam (same 7-key dict). CONFIRMED keys from
    # src/scalar_on_function_mod.rs:107-117 and :188-200.
    # NOTE: fregre_gkam also has these keys — has_fregre_gkam is the more
    # specific discriminator for gkam. has_fam will also be True for gkam.
    # ------------------------------------------------------------------
    has_fam = "component_fits" in raw and "fitted_values" in raw
    diag["has_fam"] = bool(has_fam)
    if has_fam:
        fv = np.asarray(raw["fitted_values"])
        diag["fam_n_obs"] = int(fv.shape[0])
        diag["fam_n_components"] = int(len(raw["component_fits"]))
        diag["fam_r_squared"] = (
            float(raw["r_squared"]) if "r_squared" in raw else None
        )
        diag["fam_ncomp"] = (
            int(raw["ncomp"]) if "ncomp" in raw else None
        )
    else:
        diag["fam_n_obs"] = None
        diag["fam_n_components"] = None
        diag["fam_r_squared"] = None
        diag["fam_ncomp"] = None

    # ------------------------------------------------------------------
    # fregre_gkam branch (ADV-01 Phase 72)
    # Trigger: "converged" in raw AND "bandwidths" in raw — unique to
    # fregre_gkam (the multi-predictor kernel additive model).
    # CONFIRMED keys from src/scalar_on_function_mod.rs:289-291.
    # Note: gkam also triggers has_fam above (shares component_fits +
    # fitted_values). has_fregre_gkam is the specific discriminator.
    # ------------------------------------------------------------------
    has_fregre_gkam = "converged" in raw and "bandwidths" in raw
    diag["has_fregre_gkam"] = bool(has_fregre_gkam)
    if has_fregre_gkam:
        diag["gkam_converged"] = bool(raw["converged"])
        bw_arr = np.asarray(raw["bandwidths"])
        diag["gkam_bandwidths"] = [float(v) for v in bw_arr]
        diag["gkam_n_predictors"] = int(len(bw_arr))
    else:
        diag["gkam_converged"] = None
        diag["gkam_bandwidths"] = None
        diag["gkam_n_predictors"] = None

    return diag
