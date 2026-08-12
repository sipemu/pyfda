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
    # Data matrix range
    # -----------------------------------------------------------------------
    if data is not None and data.size > 0:
        diag["data_range_min"] = float(np.min(data))
        diag["data_range_max"] = float(np.max(data))
        diag["data_range_mean"] = float(np.mean(data))
    else:
        diag["data_range_min"] = None
        diag["data_range_max"] = None
        diag["data_range_mean"] = None

    return diag
