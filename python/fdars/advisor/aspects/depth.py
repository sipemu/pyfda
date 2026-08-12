"""fdars.advisor.aspects.depth — Depth diagnostics builder.

Contains ``_build_depth_diagnostics``.  Accepts the raw depth SCORE ARRAY
returned by any ``fdars.depth.*`` function (e.g. ``fraiman_muniz_1d``,
``modal_1d``).  All fdars depth functions return an ``ndarray (n,)`` directly,
NOT a result dict — this builder consumes the array.

All values in the returned dict are native Python types (float, int, str,
list).  No NumPy scalars.  Two calls on the same input always return an equal,
JSON-serialisable dict.
"""

from __future__ import annotations

import numpy as np


def _build_depth_diagnostics(raw, *, method_name: str = "unknown", **kwargs) -> dict:
    """Compute depth diagnostics from a depth score array.

    Parameters
    ----------
    raw : array_like
        The depth score array of shape ``(n,)`` returned by any
        ``fdars.depth.*`` function (e.g. ``fraiman_muniz_1d``).  This is the
        raw ndarray, NOT a dict — fdars depth functions return scores directly.
    method_name : str, optional
        Name of the depth method used (e.g. ``"fraiman_muniz"``,
        ``"modal"``, ``"random_projection"``).  Default ``"unknown"``.
    **kwargs
        Reserved for future per-method options (ignored).

    Returns
    -------
    dict
        Plain-Python dict with JSON-serialisable values (``float``, ``int``,
        ``str``, ``list``).  No NumPy scalars.  Fields:

        - method (str): always ``"depth"``
        - method_name (str): caller-supplied depth method name
        - n_obs (int): number of observations
        - depth_min (float): minimum depth score (most peripheral curve)
        - depth_max (float): maximum depth score (most central curve)
        - depth_mean (float): mean depth score
        - depth_median (float): median depth score
        - depth_q10 (float): 10th percentile depth score (flags peripheral curves)
        - depth_q90 (float): 90th percentile depth score
        - depth_histogram (list[int]): 10-bucket histogram of depth scores
    """
    scores = np.asarray(raw, dtype=float)

    diag: dict = {
        "method": "depth",
        "method_name": str(method_name),
        "n_obs": int(len(scores)),
        "depth_min": float(np.min(scores)),
        "depth_max": float(np.max(scores)),
        "depth_mean": float(np.mean(scores)),
        "depth_median": float(np.median(scores)),
        "depth_q10": float(np.percentile(scores, 10)),
        "depth_q90": float(np.percentile(scores, 90)),
        "depth_histogram": [int(v) for v in np.histogram(scores, bins=10)[0]],
    }

    return diag
