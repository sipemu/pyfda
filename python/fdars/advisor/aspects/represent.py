"""fdars.advisor.aspects.represent — Represent diagnostics builder.

Contains ``_build_represent_diagnostics``, a pre-analysis data-quality check
over the raw functional data matrix and evaluation grid.

Unlike ``basis`` (which operates on a GCV curve result dict) or ``fpca``
(which operates on FPCA decomposition scores/singular values), ``represent``
operates on the **input data** — the observation matrix and argvals grid.
It is a NEW method string, not an extension of ``basis`` or ``fpca``.

Accepts EITHER:

* Form A: a dict with ``"data"`` (n×m array) and ``"argvals"`` (m,) keys.
* Form B: an Fdata-like object exposing ``.data`` and ``.argvals`` attributes
  (e.g. ``fdars.Fdata``).  No ``__array__`` method required, no ``keys()``
  method required.

The dispatcher in ``advisor/__init__.py`` ensures both forms reach this builder
intact — a dict is never coerced to an ndarray, and an Fdata-like object is
never coerced via ``dict(raw)`` (guarded by ``hasattr(raw, "data")``).

All returned values are native Python types (float, int, bool, None).
No NumPy scalars.  Two calls on the same input always return an equal,
JSON-serialisable dict.  No fdars call, no eigenvalue computation.
"""

from __future__ import annotations

import numpy as np


def _build_represent_diagnostics(raw, **kwargs) -> dict:
    """Compute represent diagnostics from a data matrix and evaluation grid.

    Parameters
    ----------
    raw : dict or Fdata-like
        Form A — dict with keys ``"data"`` (n×m array) and ``"argvals"`` (m,
        array).  ``"rangeval"`` (tuple of 2 floats) is accepted but not used.
        Form B — an object with ``.data`` and ``.argvals`` attributes (e.g.
        ``fdars.Fdata``).  Attribute-first lookup is always tried first; the
        dict fallback is used only when the attribute is absent.
    **kwargs
        Reserved for future per-method options (ignored).

    Returns
    -------
    dict
        Plain-Python dict with JSON-serialisable values.  Fields:

        - method (str): always ``"represent"``
        - n_obs (int): number of functional observations (rows of data)
        - n_points (int): number of evaluation grid points (columns of data)
        - argvals_min (float): minimum argval (first grid point)
        - argvals_max (float): maximum argval (last grid point)
        - argvals_spacing_mean (float or None): mean spacing between adjacent
          argvals; ``None`` when fewer than 2 argvals
        - argvals_spacing_std (float or None): std of spacing; ``None`` when
          fewer than 2 argvals
        - is_uniform_grid (bool): ``True`` when ``spacing_std / spacing_mean
          < 0.01`` or when ``spacing_mean == 0``;  ``True`` by default when
          fewer than 2 argvals (trivially uniform)
        - data_range_min (float): minimum value in the data matrix
        - data_range_max (float): maximum value in the data matrix
        - data_range_mean (float): mean value in the data matrix

        All values are ``None`` when the corresponding array is missing or
        cannot be resolved from ``raw``.
    """
    diag: dict = {"method": "represent"}

    # -----------------------------------------------------------------------
    # Resolve data and argvals — attribute-first, dict-fallback.
    # This pattern handles both Fdata objects (.data/.argvals) and plain dicts
    # without risking a KeyError or dict() coercion on Fdata.
    # -----------------------------------------------------------------------
    data_raw = getattr(raw, "data", None)
    if data_raw is None and isinstance(raw, dict):
        data_raw = raw.get("data")

    argvals_raw = getattr(raw, "argvals", None)
    if argvals_raw is None and isinstance(raw, dict):
        argvals_raw = raw.get("argvals")

    # -----------------------------------------------------------------------
    # Coerce to NumPy float arrays (only after None-guard).
    # -----------------------------------------------------------------------
    data = np.asarray(data_raw, dtype=float) if data_raw is not None else None
    argvals = np.asarray(argvals_raw, dtype=float) if argvals_raw is not None else None

    # -----------------------------------------------------------------------
    # Grid dimensions
    # -----------------------------------------------------------------------
    if data is not None and data.ndim == 2:
        diag["n_obs"] = int(data.shape[0])
        diag["n_points"] = int(data.shape[1])
    else:
        diag["n_obs"] = None
        diag["n_points"] = None

    # -----------------------------------------------------------------------
    # Argvals statistics
    # -----------------------------------------------------------------------
    if argvals is not None and len(argvals) > 0:
        diag["argvals_min"] = float(np.min(argvals))
        diag["argvals_max"] = float(np.max(argvals))

        if len(argvals) >= 2:
            diffs = np.diff(argvals)
            spacing_mean = float(np.mean(diffs))
            spacing_std = float(np.std(diffs))
            diag["argvals_spacing_mean"] = spacing_mean
            diag["argvals_spacing_std"] = spacing_std
            if spacing_mean > 0:
                diag["is_uniform_grid"] = bool(spacing_std / spacing_mean < 0.01)
            else:
                # All spacings are zero — trivially uniform (degenerate grid)
                diag["is_uniform_grid"] = True
        else:
            diag["argvals_spacing_mean"] = None
            diag["argvals_spacing_std"] = None
            diag["is_uniform_grid"] = True  # single point = trivially uniform
    else:
        diag["argvals_min"] = None
        diag["argvals_max"] = None
        diag["argvals_spacing_mean"] = None
        diag["argvals_spacing_std"] = None
        diag["is_uniform_grid"] = None

    # -----------------------------------------------------------------------
    # Data matrix range (use nan-aware reductions so NaN cells in the original
    # data matrix — which may be present when imputation context is supplied —
    # do not propagate to the output as float('nan'), which would break
    # determinism (nan != nan in Python equality comparisons).
    # -----------------------------------------------------------------------
    if data is not None and data.size > 0:
        non_nan = data[~np.isnan(data)]
        if non_nan.size > 0:
            diag["data_range_min"] = float(np.min(non_nan))
            diag["data_range_max"] = float(np.max(non_nan))
            diag["data_range_mean"] = float(np.mean(non_nan))
        else:
            # All cells are NaN — nothing to summarise
            diag["data_range_min"] = None
            diag["data_range_max"] = None
            diag["data_range_mean"] = None
    else:
        diag["data_range_min"] = None
        diag["data_range_max"] = None
        diag["data_range_mean"] = None

    # -----------------------------------------------------------------------
    # Imputation quality (ADV-02, plan 28-02) — optional extension.
    #
    # Activated when the caller supplies an 'imputed' matrix alongside the
    # original 'data' (which may contain NaN cells).  Follows the same
    # attribute-first / dict-fallback resolution as data/argvals above so
    # Fdata-like objects with an 'imputed' attribute are also supported.
    #
    # Two new keys are added:
    #   imputed_fraction — structural count: fraction of data cells that were
    #       NaN/imputed.  This is a plain count, NOT a scientific metric, so
    #       it is computed from the data matrix directly (acceptable).
    #   imputation_mae — fdars-computed consistency residual: the functional
    #       MAE between the original matrix (with NaN replaced by the imputed
    #       values) and the imputed matrix, computed by the BOUND fdars function
    #       fdars.scoring.functional_mae.  NEVER numpy arithmetic for this value
    #       (grounding invariant, per ADV-02 plan decisions).
    #
    # When no imputed matrix is present, both keys are None and ALL pre-existing
    # represent behavior is byte-for-byte unchanged (backward-compatible).
    # -----------------------------------------------------------------------
    imputed_raw = getattr(raw, "imputed", None)
    if imputed_raw is None and isinstance(raw, dict):
        imputed_raw = raw.get("imputed")

    if imputed_raw is not None and data is not None and argvals is not None:
        try:
            imputed_arr = np.asarray(imputed_raw, dtype=float)
            data_arr = np.asarray(data_raw, dtype=float)

            if (
                data_arr.ndim == 2
                and imputed_arr.ndim == 2
                and data_arr.shape == imputed_arr.shape
                and data_arr.size > 0
            ):
                # imputed_fraction: count NaN cells in the original data divided
                # by the total cell count — a structural count, not a cited metric.
                nan_mask = np.isnan(data_arr)
                total_cells = int(data_arr.size)
                nan_count = int(np.sum(nan_mask))
                diag["imputed_fraction"] = float(nan_count) / float(total_cells)

                # imputation_mae: fdars-computed consistency residual.
                # We compare the imputed matrix against the original matrix with
                # NaN cells replaced by their imputed values (i.e. imputed_arr)
                # so the MAE measures how much the imputation changed the
                # observed cells.  When the imputed matrix matches the original
                # everywhere the observed cells agree (NaN → imputed), the
                # residual reflects only the NaN-filled cells.
                # For a clean consistency measure: compare imputed_arr against
                # itself but replace the NON-NaN cells in data_arr as y_true —
                # equivalently, functional_mae(imputed_arr, imputed_arr, argvals)
                # would be zero.  Instead we use y_true = data_arr with NaN
                # cells filled from imputed_arr, and y_pred = imputed_arr, so
                # the MAE captures the difference at the *observed* (non-NaN)
                # cells only.  This requires a non-NaN y_true array:
                y_true_clean = data_arr.copy()
                y_true_clean[nan_mask] = imputed_arr[nan_mask]
                # y_true_clean has NO NaNs; y_pred = imputed_arr.
                # functional_mae(y_true_clean, imputed_arr, argvals) == 0 only
                # when the original data and the imputed data agree at every
                # observed (non-NaN) cell.  Non-zero values indicate the imputer
                # modified observed cells, which measures consistency.
                av_arr = np.asarray(argvals, dtype=float)

                # Lazy import — matching alignment.py's lazy-import idiom so
                # importing advisor never forces the full fdars.scoring chain.
                from fdars import scoring as _scoring  # noqa: PLC0415

                diag["imputation_mae"] = float(
                    _scoring.functional_mae(y_true_clean, imputed_arr, av_arr)
                )
            else:
                diag["imputed_fraction"] = None
                diag["imputation_mae"] = None
        except Exception:
            diag["imputed_fraction"] = None
            diag["imputation_mae"] = None
    else:
        diag["imputed_fraction"] = None
        diag["imputation_mae"] = None

    return diag
