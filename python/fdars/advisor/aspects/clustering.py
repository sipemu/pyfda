"""fdars.advisor.aspects.clustering — Clustering diagnostics builder.

Contains ``_build_clustering_diagnostics``, moved verbatim from
``advisor/__init__.py``.  Logic is unchanged; this is a pure file move.
"""

from __future__ import annotations

import numpy as np


def _build_clustering_diagnostics(raw: dict, *, argvals=None, **kwargs) -> dict:
    """Compute clustering diagnostics from a clustering result dict.

    Accepts a result dict with keys ``centers`` (cluster mean curves, shape
    ``(k, m)``), ``cluster`` (per-observation cluster labels), and ``k``.
    Optionally computes pairwise amplitude/phase distance between cluster
    means when ``argvals`` is provided.

    All values are cast to plain Python types.
    """
    diag: dict = {"method": "clustering"}

    centers_raw = raw.get("centers")
    labels_raw = raw.get("cluster")
    k_raw = raw.get("k")

    if centers_raw is not None:
        centers = np.asarray(centers_raw, dtype=float)
        k = int(k_raw) if k_raw is not None else int(centers.shape[0])
        diag["k"] = k

        # Per-cluster means as plain lists.
        diag["cluster_means"] = [[float(v) for v in row] for row in centers]

        # Cluster sizes from label array (when present).
        if labels_raw is not None:
            labels = np.asarray(labels_raw, dtype=int)
            cluster_sizes = []
            for ki in range(k):
                cluster_sizes.append(int(np.sum(labels == ki)))
            diag["cluster_sizes"] = cluster_sizes
        else:
            diag["cluster_sizes"] = None

        # Pairwise amplitude/phase separation between cluster means.
        # Requires argvals for distance computations.
        if argvals is not None and k > 1:
            av_arr = np.asarray(argvals, dtype=float)

            from fdars import alignment as _alignment  # noqa: PLC0415

            amp_matrix: list = []
            phase_matrix: list = []
            for i in range(k):
                amp_row: list = []
                phase_row: list = []
                for j in range(k):
                    if i == j:
                        amp_row.append(0.0)
                        phase_row.append(0.0)
                    else:
                        try:
                            amp = float(
                                _alignment.amplitude_distance(
                                    centers[i], centers[j], av_arr, 0.0
                                )
                            )
                            phase = float(
                                _alignment.phase_distance(
                                    centers[i], centers[j], av_arr, 0.0
                                )
                            )
                        except Exception:
                            amp = None
                            phase = None
                        amp_row.append(amp)
                        phase_row.append(phase)
                amp_matrix.append(amp_row)
                phase_matrix.append(phase_row)

            diag["pairwise_amplitude_distance"] = amp_matrix
            diag["pairwise_phase_distance"] = phase_matrix

            # Scalar summaries: mean off-diagonal distance.
            off_diag_amp = [
                amp_matrix[i][j]
                for i in range(k)
                for j in range(k)
                if i != j
            ]
            off_diag_phase = [
                phase_matrix[i][j]
                for i in range(k)
                for j in range(k)
                if i != j
            ]
            off_diag_amp_finite = [v for v in off_diag_amp if v is not None]
            off_diag_phase_finite = [v for v in off_diag_phase if v is not None]
            diag["mean_amplitude_separation"] = (
                float(np.mean(off_diag_amp_finite)) if off_diag_amp_finite else None
            )
            diag["mean_phase_separation"] = (
                float(np.mean(off_diag_phase_finite)) if off_diag_phase_finite else None
            )
        else:
            diag["pairwise_amplitude_distance"] = None
            diag["pairwise_phase_distance"] = None
            diag["mean_amplitude_separation"] = None
            diag["mean_phase_separation"] = None
    else:
        diag["k"] = None
        diag["cluster_means"] = None
        diag["cluster_sizes"] = None
        diag["pairwise_amplitude_distance"] = None
        diag["pairwise_phase_distance"] = None
        diag["mean_amplitude_separation"] = None
        diag["mean_phase_separation"] = None

    return diag
