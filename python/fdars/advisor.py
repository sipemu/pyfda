"""fdars.advisor — Grounded AI analysis advisor for fdars results.

Provides two complementary primitives:

* :func:`build_diagnostics` — **offline, deterministic** diagnostics builder.
  Takes an fdars result dict (or wrapper object) and computes a plain-Python,
  JSON-serialisable diagnostics dict from fdars + NumPy only. No LLM, no
  network, no RNG, no wall-clock dependency.  Two calls on the same input
  always return an equal dict.

* :func:`advise` — **grounded Claude call** that interprets the diagnostics
  and returns a schema-validated :class:`Advice` object.  Requires the
  ``anthropic`` package (``pip install fdars[advisor]``).  The LLM reasons
  only over numbers present in the diagnostics; it never fabricates values.

Pydantic models (:class:`Advice`, :class:`Recommendation`) follow the schema
from ``.planning/design/llm-cluster-narration.md``.  When ``pydantic`` is not
installed the classes still exist (as plain dataclass-style objects) so that
importing this module and calling ``build_diagnostics`` both succeed without
any optional dependency installed.  The Pydantic-backed definitions are
required only when ``advise`` is called (they are used as the
``output_format`` for ``client.messages.parse``).

Anthropic SDK version floor
---------------------------
The minimum ``anthropic`` version that supports
``client.messages.parse(output_format=<PydanticModel>)`` and the
``claude-opus-4-8`` model is **0.72.0**.  This decision is RESOLVED here in
Phase 10.  The ``[advisor]`` optional extra (declaring
``anthropic>=0.72.0`` in ``pyproject.toml``) is DECLARED and TESTED in
Phase 11 per the phase split — do not add the extra to pyproject.toml in this
phase.

Grounding invariant
-------------------
Every ``Recommendation`` carries an ``evidence`` list whose entries each cite
a specific value that appears in the diagnostics dict.  The system prompt
reinforces this at the LLM level.  The schema makes ``evidence`` a required
field so the model cannot omit it.
"""

from __future__ import annotations

import json
from typing import List, Literal

import numpy as np

# ---------------------------------------------------------------------------
# SDK version floor (Phase 10 open decision — RESOLVED)
# ---------------------------------------------------------------------------

ADVISOR_ANTHROPIC_MIN_VERSION = "0.72.0"

# ---------------------------------------------------------------------------
# Schema — Pydantic models (with graceful fallback when pydantic is absent)
# ---------------------------------------------------------------------------

# We attempt to import from pydantic.  When pydantic is not installed we
# synthesise equivalent plain-Python classes so that the module is importable
# offline without the [advisor] extra.  The Pydantic-backed classes are
# required for advise() because anthropic.messages.parse uses them as the
# output_format; that code path also needs the anthropic package, which is
# also absent without the extra — so both missing-dependency paths converge at
# the same _require_anthropic() guard inside advise().

try:
    from pydantic import BaseModel as _PydanticBaseModel

    class Recommendation(_PydanticBaseModel):
        """A single actionable recommendation grounded in fdars diagnostics.

        Attributes
        ----------
        action : str
            Concrete step (e.g. ``"increase n_basis to ~15"``).
        kind : {"parameter", "method", "none"}
            Category of the recommendation.
        rationale : str
            Why this action is warranted, tied to a diagnostic.
        expected_effect : str
            What should change in subsequent runs if the action is applied.
        evidence : list[str]
            Each entry cites a specific diagnostic value present in the input.
        """

        action: str
        kind: Literal["parameter", "method", "none"]
        rationale: str
        expected_effect: str
        evidence: List[str]

    class Advice(_PydanticBaseModel):
        """Schema-validated advice returned by :func:`advise`.

        Attributes
        ----------
        interpretation : str
            Plain-language interpretation of the result in domain terms.
        recommendations : list[Recommendation]
            Concrete next actions ordered by priority.
        caveats : list[str]
            Limitations, assumptions, or conditions that qualify the advice.
        """

        interpretation: str
        recommendations: List[Recommendation]
        caveats: List[str]

except ImportError:
    # pydantic is absent — define minimal stand-ins so importing advisor and
    # calling build_diagnostics work fully offline.

    class Recommendation:  # type: ignore[no-redef]
        """Minimal stand-in for the Pydantic Recommendation model.

        Has the same fields; not schema-validated.  advise() requires pydantic
        and will fail with a clear error before this class is used in that path.
        """

        def __init__(
            self,
            action: str,
            kind: str,
            rationale: str,
            expected_effect: str,
            evidence: List[str],
        ):
            self.action = action
            self.kind = kind
            self.rationale = rationale
            self.expected_effect = expected_effect
            self.evidence = evidence

        def __repr__(self) -> str:
            return (
                f"Recommendation(action={self.action!r}, kind={self.kind!r})"
            )

        def __eq__(self, other: object) -> bool:
            if not isinstance(other, Recommendation):
                return NotImplemented
            return self.__dict__ == other.__dict__

    class Advice:  # type: ignore[no-redef]
        """Minimal stand-in for the Pydantic Advice model.

        Has the same fields; not schema-validated.  advise() requires pydantic
        and will fail with a clear error before this class is used in that path.
        """

        def __init__(
            self,
            interpretation: str,
            recommendations: List[Recommendation],
            caveats: List[str],
        ):
            self.interpretation = interpretation
            self.recommendations = recommendations
            self.caveats = caveats

        def __repr__(self) -> str:
            n = len(self.recommendations)
            return (
                f"Advice(interpretation=..., recommendations={n}, "
                f"caveats={len(self.caveats)})"
            )

        def __eq__(self, other: object) -> bool:
            if not isinstance(other, Advice):
                return NotImplemented
            return self.__dict__ == other.__dict__


__all__ = [
    "build_diagnostics",
    "advise",
    "describe_cluster_differences",
    "Advice",
    "Recommendation",
]


# ---------------------------------------------------------------------------
# Offline diagnostics builder
# ---------------------------------------------------------------------------

def build_diagnostics(
    result,
    method: str,
    *,
    argvals=None,
    **kwargs,
) -> dict:
    """Build a deterministic, JSON-serialisable diagnostics dict from an fdars result.

    This function is **offline and deterministic**: it uses only NumPy and
    (optionally) fdars submodules.  It never imports ``anthropic``, opens a
    network connection, uses any RNG, or reads wall-clock time.  Two calls on
    the same input always return an equal dict.

    Parameters
    ----------
    result : dict or AlignmentResult
        Native fdars output dict (or a ``fdars.results`` wrapper whose ``.raw``
        attribute is the underlying dict).
    method : {"alignment", "fpca", "basis", "smoothing", "clustering"}
        The fdars method that produced ``result``.
    argvals : array_like, optional
        Shared evaluation grid, shape ``(m,)``.  Used for amplitude/phase
        distance computations when ``aligned_data`` is present.
    **kwargs
        Reserved for future per-method options.

    Returns
    -------
    dict
        Plain-Python dict with JSON-serialisable values (``float``, ``list``,
        ``str``, ``bool``, ``int``, ``None``).  No NumPy scalars.

    Raises
    ------
    ValueError
        If ``method`` is not in the currently supported set.
    """
    _supported = {"alignment", "fpca", "basis", "smoothing", "clustering"}
    method_lc = method.lower()
    if method_lc not in _supported:
        raise ValueError(
            f"build_diagnostics: unsupported method {method!r}. "
            f"Supported: {sorted(_supported)!r}."
        )

    # Unwrap result wrappers (e.g. fdars.results.AlignmentResult).
    raw: dict = getattr(result, "raw", result)
    if not isinstance(raw, dict):
        raw = dict(raw)

    if method_lc == "alignment":
        return _build_alignment_diagnostics(raw, argvals=argvals)

    if method_lc == "fpca":
        return _build_fpca_diagnostics(raw)

    if method_lc == "basis":
        return _build_basis_diagnostics(raw, **kwargs)

    if method_lc == "smoothing":
        return _build_smoothing_diagnostics(raw, **kwargs)

    if method_lc == "clustering":
        return _build_clustering_diagnostics(raw, argvals=argvals, **kwargs)

    # Unreachable given the check above, but kept for safety.
    raise ValueError(f"Unhandled method: {method!r}")


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


# ---------------------------------------------------------------------------
# FPCA diagnostics branch
# ---------------------------------------------------------------------------

def _build_fpca_diagnostics(raw: dict) -> dict:
    """Compute FPCA-specific diagnostics from an fpca-style result dict.

    Accepts the raw dict from ``fdars.regression.fpca`` (keys ``scores``,
    ``singular_values``, ``rotation``, ``mean``) or from an
    ``fdars.results.FPCAResult`` (already unwrapped by the caller).

    Computes per-component eigenvalues, explained-variance ratio, cumulative
    variance explained, component count, and a deterministic phase-leakage
    indicator.  All values are cast to plain Python types for byte-identical
    repeats across runs.
    """
    diag: dict = {"method": "fpca"}

    sv_raw = raw.get("singular_values")
    scores_raw = raw.get("scores")

    if sv_raw is not None and scores_raw is not None:
        sv = np.asarray(sv_raw, dtype=float)
        scores = np.asarray(scores_raw, dtype=float)
        n_obs = int(scores.shape[0])
        n_comp = int(sv.shape[0])
        denom = max(n_obs - 1, 1)

        # Eigenvalues = singular_values^2 / (n-1), matching FPCAResult.explained_variance
        eigenvalues = (sv ** 2) / denom
        total_var = float(eigenvalues.sum())
        if total_var > 0.0:
            evr = eigenvalues / total_var
        else:
            evr = np.zeros_like(eigenvalues)

        cumulative = float(np.cumsum(evr)[-1]) if n_comp > 0 else 0.0
        cum_list = [float(v) for v in np.cumsum(evr)]

        diag["n_components"] = n_comp
        diag["n_obs"] = n_obs
        diag["eigenvalues"] = [float(v) for v in eigenvalues]
        diag["explained_variance_ratio"] = [float(v) for v in evr]
        diag["cumulative_variance_explained"] = cum_list
        diag["total_variance"] = total_var

        # Phase-leakage indicator: a deterministic scalar that signals when a
        # linear/vertical FPCA is absorbing phase variation.  The indicator is
        # based on the proportion of variance concentrated in higher components
        # relative to the leading component.  A high value (>= 0.5) suggests
        # that later components carry a disproportionate share of variance,
        # which may reflect phase variation leaking into the amplitude
        # decomposition rather than being handled by elastic alignment.
        # Guard: with only one component the indicator is 0.0 (no higher comps).
        if n_comp > 1:
            leading_var = float(evr[0])
            remaining_var = float(evr[1:].sum())
            # Fraction of total variance NOT explained by the first component.
            phase_leakage_indicator = float(remaining_var)
        else:
            phase_leakage_indicator = 0.0
        diag["phase_leakage_indicator"] = phase_leakage_indicator

        # Flag when leakage looks substantial (> 50 % of variance in higher comps).
        diag["phase_leakage_flagged"] = bool(phase_leakage_indicator > 0.5)
    else:
        diag["n_components"] = None
        diag["n_obs"] = None
        diag["eigenvalues"] = None
        diag["explained_variance_ratio"] = None
        diag["cumulative_variance_explained"] = None
        diag["total_variance"] = None
        diag["phase_leakage_indicator"] = None
        diag["phase_leakage_flagged"] = None

    return diag


# ---------------------------------------------------------------------------
# Basis / smoothing diagnostics branches
# ---------------------------------------------------------------------------

def _build_basis_diagnostics(raw: dict, **kwargs) -> dict:
    """Compute basis-selection diagnostics from an n_basis GCV-curve result.

    Accepts either an already-computed result dict with keys
    ``n_basis_values``, ``gcv``, ``edf`` (pass-through, offline) or, when
    raw data + argvals are provided via kwargs, calls
    ``fdars.basis.basis_nbasis_cv`` deterministically.

    All values are cast to plain Python types.
    """
    diag: dict = {"method": "basis"}

    # Branch A: pre-computed GCV curve supplied directly in the result dict.
    if "n_basis_values" in raw and "gcv" in raw:
        n_basis_values = [int(v) for v in raw["n_basis_values"]]
        gcv_values = [float(v) for v in raw["gcv"]]
        edf_values = (
            [float(v) for v in raw["edf"]] if "edf" in raw else None
        )

        # Optimal: index of minimum GCV value.
        if not gcv_values:
            diag["n_basis_values"] = n_basis_values
            diag["gcv_curve"] = gcv_values
            diag["edf"] = edf_values
            diag["gcv_aic_approx"] = None
            diag["gcv_bic_approx"] = None
            diag["optimal_n_basis"] = None
            diag["optimal_gcv"] = None
            diag["optimal_edf"] = None
            return diag
        min_gcv_idx = int(np.argmin(gcv_values))
        optimal_n_basis = n_basis_values[min_gcv_idx]
        optimal_gcv = gcv_values[min_gcv_idx]
        optimal_edf = (
            edf_values[min_gcv_idx] if edf_values is not None else None
        )

        # GCV-based AIC/BIC approximation from GCV + edf when edf is available.
        # These approximate AIC/BIC using log(GCV) rather than log(RSS/n); they
        # are labelled gcv_aic_approx/gcv_bic_approx to make the approximation
        # explicit (standard AIC/BIC use log(RSS/n), which differs from log(GCV)
        # by a (1 - edf/n)^2 denominator factor).
        # AIC_approx  ≈ n * log(GCV) + 2 * edf
        # BIC_approx  ≈ n * log(GCV) + log(n) * edf
        n_obs_raw = raw.get("n_obs")
        aic_values = None
        bic_values = None
        if edf_values is not None and n_obs_raw is not None:
            n_obs = float(n_obs_raw)
            aic_values = [
                float(n_obs * np.log(max(g, 1e-300)) + 2.0 * e)
                for g, e in zip(gcv_values, edf_values)
            ]
            bic_values = [
                float(n_obs * np.log(max(g, 1e-300)) + np.log(n_obs) * e)
                for g, e in zip(gcv_values, edf_values)
            ]

        diag["n_basis_values"] = n_basis_values
        diag["gcv_curve"] = gcv_values
        diag["edf"] = edf_values
        diag["gcv_aic_approx"] = aic_values
        diag["gcv_bic_approx"] = bic_values
        diag["optimal_n_basis"] = optimal_n_basis
        diag["optimal_gcv"] = optimal_gcv
        diag["optimal_edf"] = optimal_edf
        return diag

    # Branch B: raw data provided via kwargs — call fdars.basis.basis_nbasis_cv.
    data_raw = kwargs.get("data")
    argvals_raw = kwargs.get("argvals")
    if data_raw is not None and argvals_raw is not None:
        from fdars import basis as _basis  # noqa: PLC0415

        data_arr = np.asarray(data_raw, dtype=float)
        av_arr = np.asarray(argvals_raw, dtype=float)
        # basis_nbasis_cv returns a dict with gcv, n_basis_values, etc.
        cv_result = _basis.basis_nbasis_cv(data_arr, av_arr)
        return _build_basis_diagnostics(cv_result)

    # Fallback: no usable inputs.
    diag["n_basis_values"] = None
    diag["gcv_curve"] = None
    diag["edf"] = None
    diag["gcv_aic_approx"] = None
    diag["gcv_bic_approx"] = None
    diag["optimal_n_basis"] = None
    diag["optimal_gcv"] = None
    diag["optimal_edf"] = None
    return diag


def _build_smoothing_diagnostics(raw: dict, **kwargs) -> dict:
    """Compute smoothing diagnostics from a lambda_ GCV-curve result.

    Accepts either an already-computed result dict with keys
    ``lambda_values``, ``gcv``, ``edf`` (pass-through, offline) or raw
    data + argvals via kwargs for a live ``fdars.basis.smooth_basis_gcv``
    or ``fdars.basis.pspline_fit_gcv`` call.

    All values are cast to plain Python types.
    """
    diag: dict = {"method": "smoothing"}

    # Branch A: pre-computed smoothing GCV curve supplied in the result dict.
    if "lambda_values" in raw and "gcv" in raw:
        lambda_values = [float(v) for v in raw["lambda_values"]]
        gcv_values = [float(v) for v in raw["gcv"]]
        edf_values = (
            [float(v) for v in raw["edf"]] if "edf" in raw else None
        )

        if not gcv_values:
            diag["lambda_values"] = lambda_values
            diag["gcv_curve"] = gcv_values
            diag["edf"] = edf_values
            diag["gcv_aic_approx"] = None
            diag["gcv_bic_approx"] = None
            diag["optimal_lambda"] = None
            diag["optimal_gcv"] = None
            diag["optimal_edf"] = None
            return diag
        min_gcv_idx = int(np.argmin(gcv_values))
        optimal_lambda = lambda_values[min_gcv_idx]
        optimal_gcv = gcv_values[min_gcv_idx]
        optimal_edf = (
            edf_values[min_gcv_idx] if edf_values is not None else None
        )

        n_obs_raw = raw.get("n_obs")
        aic_values = None
        bic_values = None
        if edf_values is not None and n_obs_raw is not None:
            n_obs = float(n_obs_raw)
            aic_values = [
                float(n_obs * np.log(max(g, 1e-300)) + 2.0 * e)
                for g, e in zip(gcv_values, edf_values)
            ]
            bic_values = [
                float(n_obs * np.log(max(g, 1e-300)) + np.log(n_obs) * e)
                for g, e in zip(gcv_values, edf_values)
            ]

        diag["lambda_values"] = lambda_values
        diag["gcv_curve"] = gcv_values
        diag["edf"] = edf_values
        diag["gcv_aic_approx"] = aic_values
        diag["gcv_bic_approx"] = bic_values
        diag["optimal_lambda"] = optimal_lambda
        diag["optimal_gcv"] = optimal_gcv
        diag["optimal_edf"] = optimal_edf
        return diag

    # Branch B: raw data via kwargs — call fdars.basis.pspline_fit_gcv.
    data_raw = kwargs.get("data")
    argvals_raw = kwargs.get("argvals")
    if data_raw is not None and argvals_raw is not None:
        from fdars import basis as _basis  # noqa: PLC0415

        data_arr = np.asarray(data_raw, dtype=float)
        av_arr = np.asarray(argvals_raw, dtype=float)
        gcv_result = _basis.pspline_fit_gcv(data_arr, av_arr)
        return _build_smoothing_diagnostics(gcv_result)

    # Fallback: no usable inputs.
    diag["lambda_values"] = None
    diag["gcv_curve"] = None
    diag["edf"] = None
    diag["gcv_aic_approx"] = None
    diag["gcv_bic_approx"] = None
    diag["optimal_lambda"] = None
    diag["optimal_gcv"] = None
    diag["optimal_edf"] = None
    return diag


# ---------------------------------------------------------------------------
# Clustering diagnostics branch
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Anthropic import guard
# ---------------------------------------------------------------------------

def _require_anthropic():
    """Import and return the ``anthropic`` module, or raise a clear ImportError.

    Raises
    ------
    ImportError
        When the ``anthropic`` package is not installed.  The error message
        contains ``pip install fdars[advisor]`` (install hint, CORE-04) and
        ``anthropic>={ADVISOR_ANTHROPIC_MIN_VERSION}`` (version floor, Phase 10
        resolved decision).
    """
    try:
        import anthropic  # noqa: PLC0415
    except ImportError as exc:
        raise ImportError(
            "The fdars advisor requires the anthropic SDK. "
            f"Install it with: pip install fdars[advisor]\n"
            f"Requires: anthropic>={ADVISOR_ANTHROPIC_MIN_VERSION}"
        ) from exc

    installed = tuple(
        int(x) for x in anthropic.__version__.split(".")[:3]
    )
    floor = tuple(
        int(x) for x in ADVISOR_ANTHROPIC_MIN_VERSION.split(".")[:3]
    )
    if installed < floor:
        raise ImportError(
            f"fdars advisor requires anthropic>={ADVISOR_ANTHROPIC_MIN_VERSION}; "
            f"found {anthropic.__version__}. "
            f"Run: pip install 'anthropic>={ADVISOR_ANTHROPIC_MIN_VERSION}'"
        )
    return anthropic


# ---------------------------------------------------------------------------
# Pydantic import guard
# ---------------------------------------------------------------------------

def _require_pydantic():
    """Import and return the ``pydantic`` module, or raise a clear ImportError.

    Raises
    ------
    ImportError
        When the ``pydantic`` package is not installed.  The error message
        contains ``pip install fdars[advisor]`` so users know how to fix it.
    """
    try:
        import pydantic  # noqa: PLC0415
        return pydantic
    except ImportError as exc:
        raise ImportError(
            "The fdars advisor requires pydantic for structured output. "
            "Install it with: pip install fdars[advisor]"
        ) from exc


# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------

def _system_prompt(task: str) -> str:
    """Build the grounded-output system prompt for the given task family.

    The base prompt encodes the grounding invariant and an FDA primer.
    A task-family clause is appended based on ``task``.

    Parameters
    ----------
    task : str
        Task family identifier (case-insensitive).  Supported:
        ``"interpretation"``, ``"parameter"``, ``"method"``.

    Returns
    -------
    str
        The complete system prompt to pass to the Claude API.

    Raises
    ------
    ValueError
        If ``task`` is not in the currently supported set.
    """
    task_lc = task.lower().strip()

    # -- Grounding invariant (MUST be present verbatim) ---------------------
    base = (
        "You are a functional data analysis (FDA) advisor. "
        "You reason only from the diagnostics provided in the user message. "
        "Every evidence item in each Recommendation must cite a specific "
        "diagnostic value that appears in the input — do not omit this. "
        "Omit any claim not supported by a provided value. "
        "Never fabricate numbers or invent values not present in the diagnostics. "
        "Never estimate or assume numerical results that are not explicitly given.\n\n"
        # FDA primer so the model interprets results with method-accuracy
        "FDA primer:\n"
        "- Amplitude variation: variability in the height/magnitude of curves "
        "(captured by amplitude_distance; large values indicate shape differences).\n"
        "- Phase variation: variability in the timing/location of features "
        "(captured by phase_distance; large values indicate time-warping is substantial).\n"
        "- Karcher mean (template mean): the elastic Frechet mean of a set of curves, "
        "computed iteratively by warping each curve toward the current mean; "
        "convergence is indicated by the converged flag and n_iter count.\n"
        "- Warp penalty (lambda_): regularisation strength on the warping functions; "
        "higher values penalise large warps and preserve more phase variation in the aligned curves.\n"
        "- GCV (generalised cross-validation): a model-selection criterion for smoothing "
        "and basis representation; lower GCV indicates better generalisation.\n"
        "- Variance explained: cumulative proportion of total functional variation "
        "captured by the leading FPCA components.\n"
    )

    # -- Task-family clause -------------------------------------------------
    _supported_tasks = {"interpretation", "parameter", "method"}
    if task_lc not in _supported_tasks:
        raise ValueError(
            f"_system_prompt: unsupported task {task!r}. "
            f"Supported: {sorted(_supported_tasks)!r}."
        )

    if task_lc == "interpretation":
        task_clause = (
            "Task: interpretation.\n"
            "Explain what the computed result means in domain terms: "
            "describe the amplitude and phase variation balance, "
            "whether the alignment converged and in how many iterations, "
            "and what the mean curve summary implies about the underlying process. "
            "Set recommendation kind to 'none' unless a concrete parameter or "
            "method change is clearly warranted by the diagnostics. "
            "When kind is 'none', set action to a concise interpretation summary "
            "rather than a blank string."
        )

    elif task_lc == "parameter":
        # ADVISE-02: parameter guidance grounded in diagnostics.
        task_clause = (
            "Task: parameter.\n"
            "Recommend concrete parameter adjustments for the fdars method. "
            "The parameters you may recommend adjusting are: "
            "lambda_ (warp penalty / smoothing regularisation), "
            "n_basis (number of basis functions), "
            "bandwidth (kernel smoother bandwidth), "
            "n_comp (number of FPCA components), "
            "cluster k (number of clusters), "
            "depth method (which functional depth measure to use). "
            "For each recommendation: "
            "set kind='parameter'; "
            "state a concrete action with a target value or direction "
            "(e.g. 'increase lambda_ from the current value toward 1.0', "
            "'reduce n_basis to the value at the GCV minimum'); "
            "tie the rationale to a specific diagnostic value "
            "(e.g. the GCV curve minimum, the cumulative variance explained, "
            "the warp penalty, the cluster separation); "
            "state the expected_effect in terms of the next run's diagnostics. "
            "Evidence must cite the specific diagnostic value(s) that motivate "
            "the recommendation — do not cite values absent from the input. "
            "Only recommend changes that are clearly supported by the diagnostics."
        )

    elif task_lc == "method":
        # ADVISE-03: method guidance — flag poor-fit methods, suggest alternatives.
        task_clause = (
            "Task: method.\n"
            "Identify when the chosen fdars method is a poor fit for the data "
            "and recommend an alternative. Use the following mappings:\n"
            "- Linear/vertical FPCA + substantial phase variation "
            "(high phase_leakage_indicator or variance concentrated in higher "
            "components) -> recommend elastic FPCA (amplitude/phase decomposition) "
            "to separate amplitude and phase variation before decomposition.\n"
            "- Sparse or irregularly sampled data (irregular argvals spacing, "
            "few observations per curve) -> recommend pre-smoothing to a common "
            "grid before any group-level analysis.\n"
            "- Density-valued, compositional, or strictly positive/constrained data "
            "-> recommend transforming to an unconstrained space "
            "(e.g. log-ratio, Bayes-Hilbert) before applying standard FDA methods.\n"
            "For each recommendation: "
            "set kind='method'; "
            "name the current method and why it is a poor fit; "
            "name the alternative method and what it addresses; "
            "state the expected_effect (what should improve in subsequent analysis). "
            "Evidence must cite the specific diagnostic value(s) that flag the "
            "poor-fit signal (e.g. phase_leakage_indicator value, "
            "cumulative variance pattern, cluster separation). "
            "Only flag a method mismatch when the diagnostics clearly support it."
        )

    return base + "\n" + task_clause


# ---------------------------------------------------------------------------
# advise — grounded LLM call
# ---------------------------------------------------------------------------

def advise(
    diagnostics: dict,
    *,
    task: str,
    domain_context: str,
    model: str = "claude-opus-4-8",
) -> Advice:
    """Return schema-validated :class:`Advice` for the given diagnostics.

    Calls the Claude API via ``client.messages.parse`` with adaptive thinking
    and the grounding-invariant system prompt.  Returns the validated
    :class:`Advice` object.

    Requires the ``anthropic`` package (``pip install fdars[advisor]``).

    Parameters
    ----------
    diagnostics : dict
        Output from :func:`build_diagnostics`.
    task : str
        Task family (``"interpretation"``; more added in Phase 10-02).
    domain_context : str
        Free-text description of the problem domain, dataset, or analysis goal.
        Helps the model ground its interpretation in the user's context.
    model : str, optional
        Claude model identifier.  Default ``"claude-opus-4-8"``.

    Returns
    -------
    Advice
        Schema-validated advice object with ``interpretation``,
        ``recommendations``, and ``caveats``.

    Raises
    ------
    ImportError
        When the ``anthropic`` package is not installed.
    """
    anthropic = _require_anthropic()
    _require_pydantic()
    client = anthropic.Anthropic()

    system = _system_prompt(task)

    user_content = (
        f"Domain context: {domain_context}\n\n"
        f"Task: {task}\n\n"
        "Diagnostics (reason only from these values):\n"
        + json.dumps(diagnostics, sort_keys=True, indent=2)
    )

    response = client.messages.parse(
        model=model,
        max_tokens=16000,
        thinking={"type": "adaptive"},
        system=system,
        output_format=Advice,
        messages=[{"role": "user", "content": user_content}],
    )

    parsed = response.parsed_output
    if parsed is None:
        raise ValueError(
            "advise: the Anthropic API did not return a parseable Advice object. "
            "The model may have responded with only a thinking block or a refusal. "
            f"Raw response stop_reason: {response.stop_reason!r}"
        )
    return parsed


# ---------------------------------------------------------------------------
# Cluster-difference specialization (CORE-05)
# ---------------------------------------------------------------------------

def describe_cluster_differences(
    result,
    *,
    argvals=None,
    domain_context: str = "",
    model: str = "claude-opus-4-8",
    run_llm: bool = True,
    **kwargs,
):
    """Interpret cluster differences from an fdars clustering result.

    This function is a **specialization** built on top of
    :func:`build_diagnostics` (clustering branch) and :func:`advise`.  It does
    not reimplement the diagnostics; it calls
    ``build_diagnostics(result, method="clustering", argvals=argvals, **kwargs)``
    to produce the deterministic, offline cluster feature report, then
    optionally interprets that report via the Claude API.

    **Stage 1 — offline cluster feature report** (no LLM, no network):

    Calls :func:`build_diagnostics` with ``method="clustering"`` to compute:

    - Per-cluster Karcher means (``cluster_means``)
    - Cluster sizes (``cluster_sizes``)
    - Pairwise amplitude/phase distance between cluster means
      (``pairwise_amplitude_distance``, ``pairwise_phase_distance``) when
      ``argvals`` is provided
    - Scalar separation summaries (``mean_amplitude_separation``,
      ``mean_phase_separation``)

    **Stage 2 — grounded LLM interpretation** (requires anthropic, optional):

    When ``run_llm=True``, passes the cluster feature report to
    :func:`advise` with ``task="interpretation"`` and returns a
    schema-validated :class:`Advice` object.  The LLM reasons only over the
    computed diagnostics and cites specific values in each recommendation.

    Parameters
    ----------
    result : dict or clustering result wrapper
        Native fdars clustering result dict (e.g. from
        ``fdars.clustering.kmeans``) with keys ``centers``, ``cluster``,
        and ``k``.  A wrapper whose ``.raw`` attribute is the underlying
        dict is also accepted (unwrapped by :func:`build_diagnostics`).
    argvals : array_like, optional
        Shared evaluation grid, shape ``(m,)``.  Required for pairwise
        amplitude/phase distance computation between cluster means.  When
        absent, distance keys in the feature report are ``None``.
    domain_context : str, optional
        Free-text description of the problem domain or analysis goal.
        Passed to :func:`advise` to help ground the interpretation.
    model : str, optional
        Claude model identifier.  Default ``"claude-opus-4-8"``.
    run_llm : bool, optional
        When ``True`` (default), call :func:`advise` and return an
        :class:`Advice` object.  When ``False``, return the raw clustering
        diagnostics dict (the Stage 1 feature report) without any LLM or
        network call — fully offline and exercisable in CI without an API key.
    **kwargs
        Forwarded to :func:`build_diagnostics` (reserved for future
        per-method options).

    Returns
    -------
    Advice
        Schema-validated advice when ``run_llm=True``.  Includes a
        plain-language ``interpretation`` of the cluster differences,
        grounded ``recommendations``, and ``caveats``.
    dict
        Raw clustering diagnostics dict (``{"method": "clustering", ...}``)
        when ``run_llm=False``.  Offline path — no anthropic import or
        network call.

    Raises
    ------
    ImportError
        When ``run_llm=True`` and the ``anthropic`` package is not installed.
        The error message names ``pip install fdars[advisor]``.

    Notes
    -----
    This is the design's "cluster-difference feature report" specialization.
    It follows the Stage 1 (deterministic builder) + Stage 2 (grounded LLM
    interpretation) pattern that all later specialization surfaces share.
    The grounding invariant applies: every ``Recommendation`` must cite a
    specific diagnostic value present in the feature report.

    Examples
    --------
    Offline path — inspect the feature report without an API call:

    >>> result = {"centers": [[0.0, 1.0, 0.0], [0.0, -1.0, 0.0]],
    ...           "cluster": [0, 0, 1, 1], "k": 2}
    >>> diag = describe_cluster_differences(
    ...     result, argvals=[0.0, 0.5, 1.0], run_llm=False
    ... )
    >>> diag["method"]
    'clustering'
    >>> diag["k"]
    2
    """
    diagnostics = build_diagnostics(
        result, method="clustering", argvals=argvals, **kwargs
    )
    if not run_llm:
        return diagnostics
    return advise(
        diagnostics,
        task="interpretation",
        domain_context=domain_context,
        model=model,
    )


# ---------------------------------------------------------------------------
# Offline determinism check (importable, side-effect-free)
# ---------------------------------------------------------------------------

def _selfcheck_alignment_diagnostics() -> None:
    """Verify that build_diagnostics(alignment) is deterministic on a fixed input.

    Uses only inline fixed arrays (no RNG). Asserts that two calls on the same
    input return an equal, JSON-serialisable dict.

    Raises
    ------
    AssertionError
        If two calls return different dicts (should never happen).
    """
    synthetic = {
        "mean": [0.0, 1.0, 2.0, 1.0, 0.0],
        "aligned_data": [
            [0.0, 1.0, 2.0, 1.0, 0.0],
            [0.1, 1.1, 2.0, 0.9, 0.0],
        ],
        "converged": True,
        "n_iter": 3,
    }
    av = [0.0, 0.25, 0.5, 0.75, 1.0]
    d1 = build_diagnostics(synthetic, method="alignment", argvals=av)
    d2 = build_diagnostics(synthetic, method="alignment", argvals=av)
    assert d1 == d2, (
        "build_diagnostics(alignment) is not deterministic: "
        f"first call returned {d1}, second call returned {d2}"
    )
    # Verify JSON-serialisability (no numpy scalars, no non-serialisable types).
    json.dumps(d1)
