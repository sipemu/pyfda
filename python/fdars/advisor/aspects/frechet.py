"""fdars.advisor.aspects.frechet — Fréchet diagnostics builder.

Contains ``_build_frechet_diagnostics``.  Accepts frechet submodule results:
  - ``frechet_mean`` — returns a numpy array (NOT a dict)
  - ``frechet_anova`` — returns a dict
  - ``frechet_global_reg`` / ``frechet_local_reg`` — return dicts

Phase 72-01: The frechet_mean array path and a None-safe dict path are
implemented here so ``fts`` and ``frechet`` can be registered atomically
across all guard-sync locations (ADV-02).  The full ``anova``/``reg`` field
logic ships in Phase 72-02.

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
        - has_anova (bool): always False in Phase 72-01 (full logic in 72-02)
        - anova_p_value (None): placeholder for 72-02
        - has_global_reg (bool): always False in Phase 72-01
        - has_local_reg (bool): always False in Phase 72-01
        - predicted_n_obs (None): placeholder for 72-02
        - bandwidth (None): placeholder for 72-02
    """
    diag: dict = {"method": "frechet"}

    # ------------------------------------------------------------------
    # frechet_mean — result is a numpy array (not a dict)
    # Discriminator: isinstance check BEFORE dict key lookups.
    # ------------------------------------------------------------------
    has_frechet_mean = not isinstance(raw, dict) and hasattr(raw, "__array__")
    diag["has_frechet_mean"] = bool(has_frechet_mean)
    if has_frechet_mean:
        arr = np.asarray(raw)
        diag["frechet_mean_ndim"] = int(arr.ndim)
        diag["frechet_mean_dim"] = int(arr.shape[-1]) if arr.ndim >= 1 else None
        diag["frechet_mean_trace"] = (
            float(np.trace(arr)) if arr.ndim == 2 else None
        )
    else:
        diag["frechet_mean_ndim"] = None
        diag["frechet_mean_dim"] = None
        diag["frechet_mean_trace"] = None

    # ------------------------------------------------------------------
    # frechet_anova — Phase 72-02 will fill these branches.
    # For now register the keys with None/False so the dict is always
    # fully-shaped and JSON-serialisable.
    # ------------------------------------------------------------------
    diag["has_anova"] = False
    diag["anova_p_value"] = None

    # ------------------------------------------------------------------
    # frechet_global_reg / frechet_local_reg — Phase 72-02.
    # ------------------------------------------------------------------
    diag["has_global_reg"] = False
    diag["has_local_reg"] = False
    diag["predicted_n_obs"] = None
    diag["bandwidth"] = None

    return diag
