"""fdars.advisor.aspects.frechet — Fréchet diagnostics builder.

Contains ``_build_frechet_diagnostics``.  Accepts frechet submodule results:
  - ``frechet_mean`` — returns a numpy array (NOT a dict)
  - ``frechet_anova`` — returns a 9-key dict
  - ``frechet_global_reg`` — returns a 3-key dict: predicted, xout, x_bar
  - ``frechet_local_reg`` — returns a 3-key dict: predicted, xout, bandwidth

Phase 72-01: frechet_mean array path and stub dict path registered atomically
across all guard-sync locations (ADV-02).

Phase 72-02: Real anova/global_reg/local_reg field logic with grounded native
scalars, using CONFIRMED keys from src/frechet_mod.rs.

Discriminator keys (CONFIRMED from src/frechet_mod.rs):
  - anova:       "p_value_permutation" in raw AND "group_labels" in raw
  - local_reg:   "bandwidth" in raw  (unique to local_reg)
  - global_reg:  "predicted" in raw AND "x_bar" in raw AND NOT local_reg

frechet_mean returns a naked numpy array (not a dict) — the isinstance(raw, dict)
guard is applied FIRST before any dict key access (Pitfall 4 from RESEARCH §6).

All values in the returned dict are native Python types (float, int, bool,
list, None).  No NumPy scalars.  Two calls on the same input always return
an equal, JSON-serialisable dict.
"""

from __future__ import annotations

import numpy as np


def _build_frechet_diagnostics(raw, **kwargs) -> dict:
    """Compute Fréchet diagnostics from an fdars frechet submodule result.

    Parameters
    ----------
    raw : dict or numpy.ndarray
        Native fdars output from ``frechet_mean`` (numpy array) or from
        ``frechet_anova`` / ``frechet_global_reg`` / ``frechet_local_reg``
        (dict).
    **kwargs
        Reserved for future per-method options (ignored).

    Returns
    -------
    dict
        Plain-Python dict with JSON-serialisable values (``float``, ``int``,
        ``bool``, ``list``, ``None``).  No NumPy scalars.  Fields:

        - method (str): always ``"frechet"``
        - has_frechet_mean (bool): True when raw is a numpy array
        - frechet_mean_ndim (int or None): 1 for spherical, 2 for spd/corr
        - frechet_mean_dim (int or None): last dimension (size d)
        - frechet_mean_trace (float or None): trace when ndim==2, else None
        - has_anova (bool): True when result is a frechet_anova dict
        - anova_p_value_permutation (float or None): permutation p-value in [0,1]
        - anova_p_value_asymptotic (float or None): asymptotic p-value in [0,1]
        - n_perm (int or None): number of permutations used
        - n_groups (int or None): number of distinct groups
        - pooled_frechet_variance (float or None): pooled within-group variance
        - group_frechet_variance_max (float or None): maximum group variance
        - has_global_reg (bool): True when result is frechet_global_reg dict
        - has_local_reg (bool): True when result is frechet_local_reg dict
        - predicted_n_obs (int or None): n_out from predicted array shape[0]
        - bandwidth (float or None): kernel bandwidth (local_reg only)
    """
    diag: dict = {"method": "frechet"}

    # ------------------------------------------------------------------
    # frechet_mean — result is a numpy array (not a dict)
    # MUST be checked FIRST before any dict key access (Pitfall 4).
    # Discriminator: isinstance check before dict lookups.
    # ------------------------------------------------------------------
    if not isinstance(raw, dict):
        # frechet_mean returns a naked numpy array
        arr = np.asarray(raw)
        diag["has_frechet_mean"] = True
        diag["frechet_mean_ndim"] = int(arr.ndim)
        diag["frechet_mean_dim"] = int(arr.shape[-1]) if arr.ndim >= 1 else None
        diag["frechet_mean_trace"] = float(np.trace(arr)) if arr.ndim == 2 else None

        # Set all dict-path fields to None/False
        diag["has_anova"] = False
        diag["anova_p_value_permutation"] = None
        diag["anova_p_value_asymptotic"] = None
        diag["n_perm"] = None
        diag["n_groups"] = None
        diag["pooled_frechet_variance"] = None
        diag["group_frechet_variance_max"] = None
        diag["has_global_reg"] = False
        diag["has_local_reg"] = False
        diag["predicted_n_obs"] = None
        diag["bandwidth"] = None
        return diag

    # ------------------------------------------------------------------
    # Dict path: anova / global_reg / local_reg
    # frechet_mean array case is handled above.
    # ------------------------------------------------------------------
    diag["has_frechet_mean"] = False
    diag["frechet_mean_ndim"] = None
    diag["frechet_mean_dim"] = None
    diag["frechet_mean_trace"] = None

    # Discriminators using CONFIRMED keys from src/frechet_mod.rs:
    #   frechet_anova:      "p_value_permutation" (line 97) AND "group_labels" (line 107)
    #   frechet_local_reg:  "bandwidth" (line 226) — unique to local_reg
    #   frechet_global_reg: "predicted" (line 164) AND "x_bar" (line 166) AND NOT local_reg
    has_anova = "p_value_permutation" in raw and "group_labels" in raw
    has_local_reg = "bandwidth" in raw
    has_global_reg = "predicted" in raw and "x_bar" in raw and not has_local_reg

    # ------------------------------------------------------------------
    # frechet_anova branch
    # Keys confirmed from src/frechet_mod.rs lines 95-110:
    #   statistic, p_value_asymptotic, p_value_permutation, n_perm,
    #   group_frechet_variances, pooled_frechet_variance,
    #   fn_statistic, un_statistic, group_labels
    # ------------------------------------------------------------------
    diag["has_anova"] = bool(has_anova)
    if has_anova:
        # p_value_permutation — always present when has_anova (discriminator key)
        diag["anova_p_value_permutation"] = float(raw["p_value_permutation"])
        # p_value_asymptotic — present in 9-key dict, guard defensively
        diag["anova_p_value_asymptotic"] = (
            float(raw["p_value_asymptotic"]) if "p_value_asymptotic" in raw else None
        )
        # n_perm — echoed from input (frechet_mod.rs:98)
        diag["n_perm"] = int(raw["n_perm"]) if "n_perm" in raw else None
        # n_groups — derived from unique values in the echoed group_labels array
        if "group_labels" in raw:
            diag["n_groups"] = int(len(np.unique(np.asarray(raw["group_labels"]))))
        else:
            diag["n_groups"] = None
        # pooled_frechet_variance — float (frechet_mod.rs:103)
        diag["pooled_frechet_variance"] = (
            float(raw["pooled_frechet_variance"])
            if "pooled_frechet_variance" in raw
            else None
        )
        # group_frechet_variance_max — max of the per-group variance array
        # np.max returns a numpy scalar → cast with float() (Pitfall 2)
        if "group_frechet_variances" in raw:
            diag["group_frechet_variance_max"] = float(
                np.max(np.asarray(raw["group_frechet_variances"]))
            )
        else:
            diag["group_frechet_variance_max"] = None
    else:
        diag["anova_p_value_permutation"] = None
        diag["anova_p_value_asymptotic"] = None
        diag["n_perm"] = None
        diag["n_groups"] = None
        diag["pooled_frechet_variance"] = None
        diag["group_frechet_variance_max"] = None

    # ------------------------------------------------------------------
    # frechet_global_reg / frechet_local_reg branch
    # global_reg keys (frechet_mod.rs lines 164-166): predicted, xout, x_bar
    # local_reg keys  (frechet_mod.rs lines 224-226): predicted, xout, bandwidth
    #
    # predicted_n_obs: int(array.shape[0]) — n_out (number of prediction points)
    # bandwidth: float only for local_reg; None for global_reg
    # ------------------------------------------------------------------
    diag["has_global_reg"] = bool(has_global_reg)
    diag["has_local_reg"] = bool(has_local_reg)

    if has_global_reg or has_local_reg:
        diag["predicted_n_obs"] = (
            int(np.asarray(raw["predicted"]).shape[0])
            if "predicted" in raw
            else None
        )
        # bandwidth: present only in local_reg; guarded for global_reg
        # float() cast: result.bandwidth is already a Rust f64 → Python float,
        # but cast defensively in case of unexpected numpy scalar (Pitfall 2)
        diag["bandwidth"] = (
            float(raw["bandwidth"]) if "bandwidth" in raw else None
        )
    else:
        diag["predicted_n_obs"] = None
        diag["bandwidth"] = None

    return diag
