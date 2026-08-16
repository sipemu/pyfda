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

    # -- Registration quality scores (ADV-02, plan 28-02) ------------------
    # Three fdars-computed registration-quality scores are added when the
    # registered matrix and argvals are present.  Each score is cast to a
    # native float; a score that raises (e.g. n < 2 for pairwise correlation,
    # or any fdars ValueError) maps to None without failing the builder.
    # When aligned_raw or argvals is absent, all three keys are None and
    # ALL pre-existing behavior is byte-for-byte unchanged (backward-compatible).
    if aligned_raw is not None and argvals is not None:
        aligned_arr_reg = np.asarray(aligned_raw, dtype=float)
        av_arr_reg = np.asarray(argvals, dtype=float)
        # Reuse the lazy import already established above (alignment branch).
        from fdars import alignment as _alignment  # noqa: PLC0415

        # least_squares_score — lower is better; mean L2 spread around mean
        try:
            diag["least_squares_score"] = float(
                _alignment.least_squares_score(aligned_arr_reg, av_arr_reg)
            )
        except Exception:
            diag["least_squares_score"] = None

        # pairwise_correlation_score — higher is better; guard n >= 2
        n_reg = int(aligned_arr_reg.shape[0])
        if n_reg >= 2:
            try:
                diag["pairwise_correlation_score"] = float(
                    _alignment.pairwise_correlation_score(aligned_arr_reg, av_arr_reg)
                )
            except Exception:
                diag["pairwise_correlation_score"] = None
        else:
            diag["pairwise_correlation_score"] = None

        # sobolev_least_squares_score — lambda_=0.0 is safe on any grid
        try:
            diag["sobolev_score"] = float(
                _alignment.sobolev_least_squares_score(
                    aligned_arr_reg, av_arr_reg, lambda_=0.0
                )
            )
        except Exception:
            diag["sobolev_score"] = None
    else:
        diag["least_squares_score"] = None
        diag["pairwise_correlation_score"] = None
        diag["sobolev_score"] = None

    # -- Convergence --------------------------------------------------------
    converged_raw = raw.get("converged")
    diag["converged"] = bool(converged_raw) if converged_raw is not None else None

    n_iter_raw = raw.get("n_iter")
    diag["n_iter"] = int(n_iter_raw) if n_iter_raw is not None else None

    return diag
