"""fdars.advisor.aspects.outliers — Outlier diagnostics builder.

Contains ``_build_outliers_diagnostics``.  Accepts the result dict returned by
any ``fdars.outliers.*`` function.  Eight distinct result shapes are handled by
key-presence guards:

* ``detect_outliers_lrt`` / ``detect_outliers_lrt_with_dist`` ->
  ``{"outliers": bool_arr, "threshold": float, ...}``
* ``outliergram`` ->
  ``{"mei": arr, "mbd": arr, "outliers": bool_arr}``
* ``magnitude_shape`` ->
  ``{"magnitude": arr, "shape": arr}``  (NO "outliers" key!)
* ``depthgram`` ->
  ``{"mbd_mei_d": arr, "mbd": arr, "mei": arr, "shape_outliers": list, ...}``
* ``muod`` ->
  ``{"amplitude_outliers": list, "shape_index": arr, "magnitude_index": arr, ...}``
* ``tvdmss`` ->
  ``{"tvd": arr, "mss": arr, "magnitude_outliers": list, "shape_outliers": list}``
* ``sequential_transform_outliers`` ->
  ``{"union_outliers": list, "per_transform_outliers": list}``

Every key access is guarded (ASVS V5).  Missing keys emit ``None`` rather than
raising ``KeyError``.  All values in the returned dict are native Python types
(``float``, ``int``, ``bool``, ``list``, ``None``).  No NumPy scalars.  Two
calls on the same input always return an equal, JSON-serialisable dict.
"""

from __future__ import annotations

import numpy as np


def _build_outliers_diagnostics(raw: dict, **kwargs) -> dict:
    """Compute outlier diagnostics from an fdars outliers result dict.

    Handles four result shapes (``detect_outliers_lrt``, ``outliergram``,
    ``magnitude_shape``, and ``detect_outliers_lrt_with_dist``) by inferring
    which function was called from key presence.

    Parameters
    ----------
    raw : dict
        Native fdars outliers result dict.  Keys vary by function:

        - ``detect_outliers_lrt``: ``"outliers"`` (bool array n,), ``"threshold"``
        - ``outliergram``: ``"mei"``, ``"mbd"``, ``"outliers"``
        - ``magnitude_shape``: ``"magnitude"``, ``"shape"`` (NO ``"outliers"`` key)

    **kwargs
        Reserved for future per-method options (ignored).

    Returns
    -------
    dict
        Plain-Python dict with JSON-serialisable values (``float``, ``int``,
        ``bool``, ``list``, ``None``).  No NumPy scalars.  Fields:

        - method (str): always ``"outliers"``
        - n_obs (int): number of observations (inferred from whichever array is
          present)
        - n_outliers (int or None): count of flagged outliers when ``"outliers"``
          key is present; ``None`` for ``magnitude_shape`` results
        - outlier_fraction (float or None): fraction flagged; ``None`` when
          ``"outliers"`` key absent
        - threshold (float or None): LRT threshold when present
        - has_magnitude_shape (bool): True when ``"magnitude"`` and ``"shape"``
          keys are both present
        - magnitude_range (list or None): [min, max] of magnitude scores
        - shape_range (list or None): [min, max] of shape scores
        - has_outliergram (bool): True when ``"mei"`` and ``"mbd"`` keys are
          both present
        - mei_range (list or None): [min, max] of MEI scores
        - mbd_range (list or None): [min, max] of MBD scores
    """
    diag: dict = {"method": "outliers"}

    # -- Infer n_obs from whichever array is present first -------------------
    # Priority: "outliers" bool array, then "magnitude", then "shape",
    # then "mei", then "mbd", then "tvd" (tvdmss), then "shape_index" (muod).
    n_obs: int | None = None
    for key in ("outliers", "magnitude", "shape", "mei", "mbd", "tvd", "shape_index"):
        if key in raw:
            arr = np.asarray(raw[key])
            n_obs = int(len(arr))
            break
    diag["n_obs"] = n_obs

    # -- n_outliers / outlier_fraction (only when "outliers" key present) ----
    # CRITICAL: magnitude_shape returns NO "outliers" key; never assume
    # n_outliers is computable from it.
    if "outliers" in raw:
        outliers_arr = np.asarray(raw["outliers"], dtype=bool)
        n_outliers = int(np.sum(outliers_arr))
        diag["n_outliers"] = n_outliers
        diag["outlier_fraction"] = (
            float(n_outliers / n_obs) if n_obs and n_obs > 0 else 0.0
        )
    else:
        diag["n_outliers"] = None
        diag["outlier_fraction"] = None

    # -- threshold (LRT only) ------------------------------------------------
    diag["threshold"] = float(raw["threshold"]) if "threshold" in raw else None

    # -- magnitude_shape shape -----------------------------------------------
    has_magnitude_shape = "magnitude" in raw and "shape" in raw
    diag["has_magnitude_shape"] = bool(has_magnitude_shape)
    if has_magnitude_shape:
        magnitude = np.asarray(raw["magnitude"], dtype=float)
        shape = np.asarray(raw["shape"], dtype=float)
        diag["magnitude_range"] = [float(np.min(magnitude)), float(np.max(magnitude))]
        diag["shape_range"] = [float(np.min(shape)), float(np.max(shape))]
    else:
        diag["magnitude_range"] = None
        diag["shape_range"] = None

    # -- outliergram shape ---------------------------------------------------
    # Guard: depthgram also has "mei"/"mbd" but is detected separately below
    # via its unique "mbd_mei_d" key.  Exclude depthgram from this block.
    has_outliergram = "mei" in raw and "mbd" in raw and "mbd_mei_d" not in raw
    diag["has_outliergram"] = bool(has_outliergram)
    if has_outliergram:
        mei = np.asarray(raw["mei"], dtype=float)
        mbd = np.asarray(raw["mbd"], dtype=float)
        diag["mei_range"] = [float(np.min(mei)), float(np.max(mei))]
        diag["mbd_range"] = [float(np.min(mbd)), float(np.max(mbd))]
    else:
        diag["mei_range"] = None
        diag["mbd_range"] = None

    # -- tvdmss shape --------------------------------------------------------
    # Trigger: "tvd" in raw and "mss" in raw (unique to tvdmss; neither
    # outliergram nor muod carries these keys).
    has_tvdmss = "tvd" in raw and "mss" in raw
    diag["has_tvdmss"] = bool(has_tvdmss)
    if has_tvdmss:
        tvd = np.asarray(raw["tvd"], dtype=float)
        mss = np.asarray(raw["mss"], dtype=float)
        mag_out = raw.get("magnitude_outliers") or []
        shp_out = raw.get("shape_outliers") or []
        n_magnitude_outliers = int(len(mag_out))
        n_shape_outliers = int(len(shp_out))
        diag["n_magnitude_outliers"] = n_magnitude_outliers
        diag["n_shape_outliers"] = n_shape_outliers
        if n_obs and n_obs > 0:
            diag["magnitude_outlier_fraction"] = float(n_magnitude_outliers / n_obs)
            diag["shape_outlier_fraction"] = float(n_shape_outliers / n_obs)
        else:
            diag["magnitude_outlier_fraction"] = 0.0
            diag["shape_outlier_fraction"] = 0.0
        diag["tvd_range"] = [float(np.min(tvd)), float(np.max(tvd))]
        diag["mss_range"] = [float(np.min(mss)), float(np.max(mss))]
    else:
        diag["n_magnitude_outliers"] = None
        diag["n_shape_outliers"] = None
        diag["magnitude_outlier_fraction"] = None
        diag["shape_outlier_fraction"] = None
        diag["tvd_range"] = None
        diag["mss_range"] = None

    # -- muod shape ----------------------------------------------------------
    # Trigger: "amplitude_outliers" in raw (unique to muod).
    # Note: muod also has "shape_outliers"/"magnitude_outliers" like tvdmss, but
    # tvdmss does NOT have "amplitude_outliers"; muod does NOT have "tvd"/"mss".
    has_muod = "amplitude_outliers" in raw
    diag["has_muod"] = bool(has_muod)
    if has_muod:
        mag_out = raw.get("magnitude_outliers") or []
        shp_out = raw.get("shape_outliers") or []
        amp_out = raw.get("amplitude_outliers") or []
        n_mag = int(len(mag_out))
        n_shp = int(len(shp_out))
        n_amp = int(len(amp_out))
        diag["n_muod_magnitude_outliers"] = n_mag
        diag["n_muod_shape_outliers"] = n_shp
        diag["n_amplitude_outliers"] = n_amp
        # n_obs for muod comes from the score arrays (e.g. shape_index)
        muod_n_obs = n_obs if n_obs and n_obs > 0 else None
        if muod_n_obs:
            diag["muod_magnitude_outlier_fraction"] = float(n_mag / muod_n_obs)
            diag["muod_shape_outlier_fraction"] = float(n_shp / muod_n_obs)
            diag["amplitude_outlier_fraction"] = float(n_amp / muod_n_obs)
        else:
            diag["muod_magnitude_outlier_fraction"] = None
            diag["muod_shape_outlier_fraction"] = None
            diag["amplitude_outlier_fraction"] = None
        # Score ranges — [float(min), float(max)] via np.asarray
        for score_key, range_key in (
            ("shape_index", "shape_index_range"),
            ("magnitude_index", "magnitude_index_range"),
            ("amplitude_index", "amplitude_index_range"),
        ):
            if score_key in raw:
                arr = np.asarray(raw[score_key], dtype=float)
                diag[range_key] = [float(np.min(arr)), float(np.max(arr))]
            else:
                diag[range_key] = None
    else:
        diag["n_muod_magnitude_outliers"] = None
        diag["n_muod_shape_outliers"] = None
        diag["n_amplitude_outliers"] = None
        diag["muod_magnitude_outlier_fraction"] = None
        diag["muod_shape_outlier_fraction"] = None
        diag["amplitude_outlier_fraction"] = None
        diag["shape_index_range"] = None
        diag["magnitude_index_range"] = None
        diag["amplitude_index_range"] = None

    # -- sequential_transform_outliers shape ---------------------------------
    # Trigger: "union_outliers" in raw (unique to this detector).
    # CRITICAL: n_obs is NOT recoverable from this result dict — no score array
    # is present.  Do NOT emit an outlier_fraction.
    has_sequential_transform = "union_outliers" in raw
    diag["has_sequential_transform"] = bool(has_sequential_transform)
    if has_sequential_transform:
        diag["n_union_outliers"] = int(len(raw["union_outliers"]))
        per_tf = raw.get("per_transform_outliers") or []
        diag["n_transforms"] = int(len(per_tf))
    else:
        diag["n_union_outliers"] = None
        diag["n_transforms"] = None

    # -- depthgram shape -----------------------------------------------------
    # Trigger: "mbd_mei_d" in raw (unique to depthgram; shared "mei"/"mbd"
    # keys already excluded from the outliergram block above via the
    # "mbd_mei_d" not in raw guard).
    has_depthgram = "mbd_mei_d" in raw
    diag["has_depthgram"] = bool(has_depthgram)
    if has_depthgram:
        # n_obs from "mbd" (length n per depthgram structure)
        dg_mbd = np.asarray(raw["mbd"], dtype=float)
        dg_mei = np.asarray(raw["mei"], dtype=float)
        dg_n_obs = int(len(dg_mbd))
        dg_shp = raw.get("shape_outliers") or []
        dg_mag = raw.get("magnitude_outliers") or []
        dg_n_shp = int(len(dg_shp))
        dg_n_mag = int(len(dg_mag))
        diag["n_depthgram_shape_outliers"] = dg_n_shp
        diag["n_depthgram_magnitude_outliers"] = dg_n_mag
        if dg_n_obs > 0:
            diag["depthgram_shape_outlier_fraction"] = float(dg_n_shp / dg_n_obs)
            diag["depthgram_magnitude_outlier_fraction"] = float(dg_n_mag / dg_n_obs)
        else:
            diag["depthgram_shape_outlier_fraction"] = 0.0
            diag["depthgram_magnitude_outlier_fraction"] = 0.0
        diag["depthgram_mbd_range"] = [float(np.min(dg_mbd)), float(np.max(dg_mbd))]
        diag["depthgram_mei_range"] = [float(np.min(dg_mei)), float(np.max(dg_mei))]
    else:
        diag["n_depthgram_shape_outliers"] = None
        diag["n_depthgram_magnitude_outliers"] = None
        diag["depthgram_shape_outlier_fraction"] = None
        diag["depthgram_magnitude_outlier_fraction"] = None
        diag["depthgram_mbd_range"] = None
        diag["depthgram_mei_range"] = None

    return diag
