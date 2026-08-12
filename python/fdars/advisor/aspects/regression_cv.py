"""fdars.advisor.aspects.regression_cv — Regression CV diagnostics builder.

Contains ``_build_regression_cv_diagnostics``.  Handles BOTH fdars CV
functions:

* ``fregre_cv`` — returns ``optimal_k``, ``min_cv_error``, ``k_values``
  (numpy array), ``cv_errors`` (numpy array), ``fold_errors`` (numpy array).
* ``model_selection_ncomp`` — returns ``best_ncomp`` and ``criteria`` (list
  of (ncomp, aic, bic, gcv) tuples).

Key corrections applied here (see 21-RESEARCH §2):
- Correction #7: ``cv_errors`` and ``k_values`` from ``fregre_cv`` are
  returned as numpy arrays, NOT Python lists.  Cast via list comprehension:
  ``[float(v) for v in raw["cv_errors"]]``.
- ``model_selection_ncomp`` has NO top-level ``cv_errors``/``k_values``.
  Extract them from the ``criteria`` list of tuples (index 0 = ncomp,
  index 3 = GCV).

All values in the returned dict are native Python types (float, int, bool,
list, None).  No NumPy scalars.  Two calls on the same input always return
an equal, JSON-serialisable dict.
"""

from __future__ import annotations

import numpy as np


def _build_regression_cv_diagnostics(raw, **kwargs) -> dict:
    """Compute regression CV diagnostics from an fdars CV result dict.

    Parameters
    ----------
    raw : dict
        Native fdars output dict from either ``fregre_cv`` or
        ``model_selection_ncomp``.  Keys vary by source — all accesses
        are guarded.
    **kwargs
        Reserved for future per-method options (ignored).

    Returns
    -------
    dict
        Plain-Python dict with JSON-serialisable values (``float``, ``int``,
        ``bool``, ``list``, ``None``).  No NumPy scalars.  Fields:

        - method (str): always ``"regression_cv"``
        - optimal_k (int): chosen number of components / nearest-neighbours
        - min_cv_error (float or None): minimum CV error (absent for
          ``model_selection_ncomp``)
        - cv_curve (list[float]): CV error values per k (GCV for
          ``model_selection_ncomp``)
        - k_values (list[int]): component counts matching ``cv_curve``
        - cv_curve_range (list[float] or None): [min, max] when non-empty
        - elbow_present (bool): True when the curve has a local minimum NOT
          at index 0 or -1 (i.e. the optimal is interior, not boundary)
    """
    diag: dict = {"method": "regression_cv"}

    # ------------------------------------------------------------------
    # Detect source function by key presence.
    # fregre_cv always has "optimal_k" and "cv_errors".
    # model_selection_ncomp always has "best_ncomp" and "criteria".
    # ------------------------------------------------------------------
    if "optimal_k" in raw:
        # --- fregre_cv path ---
        diag["optimal_k"] = int(raw["optimal_k"])
        diag["min_cv_error"] = (
            float(raw["min_cv_error"]) if "min_cv_error" in raw else None
        )
        # Cast numpy arrays to Python lists (correction #7)
        diag["cv_curve"] = [float(v) for v in raw.get("cv_errors", [])]
        diag["k_values"] = [int(v) for v in raw.get("k_values", [])]

    elif "best_ncomp" in raw:
        # --- model_selection_ncomp path ---
        diag["optimal_k"] = int(raw["best_ncomp"])
        diag["min_cv_error"] = None  # not a direct top-level key
        criteria = raw.get("criteria", [])
        # Each entry is a (ncomp, aic, bic, gcv) tuple; index 3 = GCV
        diag["k_values"] = [int(c[0]) for c in criteria]
        diag["cv_curve"] = [float(c[3]) for c in criteria]

    else:
        # Unknown source — emit safe defaults
        diag["optimal_k"] = None
        diag["min_cv_error"] = None
        diag["cv_curve"] = []
        diag["k_values"] = []

    # ------------------------------------------------------------------
    # cv_curve_range — [min, max] when non-empty
    # ------------------------------------------------------------------
    if diag["cv_curve"]:
        diag["cv_curve_range"] = [
            float(min(diag["cv_curve"])),
            float(max(diag["cv_curve"])),
        ]
    else:
        diag["cv_curve_range"] = None

    # ------------------------------------------------------------------
    # elbow_present — True when the CV curve has a strict local minimum
    # at an interior index (NOT at index 0 or index -1).
    #
    # "Don't hand-roll": identify any index i in [1, n-2] where
    # cv_curve[i] < cv_curve[i-1] AND cv_curve[i] < cv_curve[i+1].
    # This is 4 lines of NumPy; no signal-processing library needed.
    # ------------------------------------------------------------------
    cv = diag["cv_curve"]
    if len(cv) >= 3:
        arr = np.asarray(cv, dtype=float)
        # Interior indices: 1 to n-2 inclusive
        interior = arr[1:-1]
        left = arr[:-2]
        right = arr[2:]
        has_interior_min = bool(np.any((interior < left) & (interior < right)))
        diag["elbow_present"] = has_interior_min
    else:
        # Fewer than 3 points — cannot have an interior minimum
        diag["elbow_present"] = False

    return diag
