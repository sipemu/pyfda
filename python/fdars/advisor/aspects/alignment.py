"""fdars.advisor.aspects.alignment — Alignment diagnostics builder.

Contains ``_build_alignment_diagnostics``, moved verbatim from
``advisor/__init__.py``.  Logic is unchanged; this is a pure file move.
"""

from __future__ import annotations

import numpy as np


def _build_alignment_diagnostics(raw: dict, *, argvals=None) -> dict:
    """Compute alignment-specific diagnostics from a karcher_mean-style result.

    All values are cast to plain Python types (``float``, ``list``, ``bool``,
    ``int``) so repeated runs are byte-identical and the result is
    JSON-serialisable.
    """
    diag: dict = {"method": "alignment"}

    # -- Karcher / template mean summary ------------------------------------
    mean_raw = raw.get("mean")
    if mean_raw is not None:
        mean_arr = np.asarray(mean_raw, dtype=float)
        diag["mean_length"] = int(mean_arr.shape[0])
        diag["mean_min"] = float(np.min(mean_arr))
        diag["mean_max"] = float(np.max(mean_arr))
        diag["mean_avg"] = float(np.mean(mean_arr))
        # Full mean curve as a plain list for downstream reference
        diag["mean_curve"] = [float(v) for v in mean_arr]
    else:
        diag["mean_length"] = None
        diag["mean_min"] = None
        diag["mean_max"] = None
        diag["mean_avg"] = None
        diag["mean_curve"] = None

    # -- Warp / amplitude / phase separation --------------------------------
    aligned_raw = raw.get("aligned_data")
    if aligned_raw is not None and mean_raw is not None and argvals is not None:
        aligned_arr = np.asarray(aligned_raw, dtype=float)
        mean_arr = np.asarray(mean_raw, dtype=float)
        av_arr = np.asarray(argvals, dtype=float)

        # Lazy import inside build_diagnostics — importing advisor never forces
        # a heavy import chain on its own.
        from fdars import alignment as _alignment  # noqa: PLC0415

        amp_dists = []
        phase_dists = []
        for curve in aligned_arr:
            try:
                amp = float(_alignment.amplitude_distance(curve, mean_arr, av_arr, 0.0))
                phase = float(_alignment.phase_distance(curve, mean_arr, av_arr, 0.0))
            except Exception:
                amp = None
                phase = None
            amp_dists.append(amp)
            phase_dists.append(phase)

        amp_finite = [v for v in amp_dists if v is not None]
        phase_finite = [v for v in phase_dists if v is not None]

        diag["n_obs"] = int(aligned_arr.shape[0])
        diag["amplitude_distances"] = amp_dists
        diag["phase_distances"] = phase_dists
        diag["amplitude_mean"] = float(np.mean(amp_finite)) if amp_finite else None
        diag["amplitude_max"] = float(np.max(amp_finite)) if amp_finite else None
        diag["phase_mean"] = float(np.mean(phase_finite)) if phase_finite else None
        diag["phase_max"] = float(np.max(phase_finite)) if phase_finite else None
    elif aligned_raw is not None:
        aligned_arr = np.asarray(aligned_raw, dtype=float)
        diag["n_obs"] = int(aligned_arr.shape[0])
        diag["amplitude_distances"] = None
        diag["phase_distances"] = None
        diag["amplitude_mean"] = None
        diag["amplitude_max"] = None
        diag["phase_mean"] = None
        diag["phase_max"] = None
    else:
        diag["n_obs"] = None
        diag["amplitude_distances"] = None
        diag["phase_distances"] = None
        diag["amplitude_mean"] = None
        diag["amplitude_max"] = None
        diag["phase_mean"] = None
        diag["phase_max"] = None

    # -- Convergence --------------------------------------------------------
    converged_raw = raw.get("converged")
    diag["converged"] = bool(converged_raw) if converged_raw is not None else None

    n_iter_raw = raw.get("n_iter")
    diag["n_iter"] = int(n_iter_raw) if n_iter_raw is not None else None

    return diag
