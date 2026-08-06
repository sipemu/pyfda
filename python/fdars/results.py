"""fdars.results – lightweight, opt-in result wrappers.

Native fdars functions return plain ``dict`` objects.  This module adds a thin
ergonomic layer *on top of* those dicts without changing the numeric core: a
result object simply wraps an existing dict (plus, where the native ``predict_*``
functions require them, the original training arrays) and forwards to the same
free functions.  Nothing here recomputes or alters the fitted numbers.

Typical use::

    fit = fdars.regression.fregre_lm(X, y, n_comp=3)
    res = fdars.results.wrap_fregre(fit, "lm", data=X, response=y, n_comp=3)
    res                      # rich __repr__
    res.summary()            # printed summary
    res.coef()               # coefficient vector
    yhat = res.predict(X_new)  # == predict_fregre_lm(X, y, X_new, 3)

All wrappers are opt-in: the underlying dict is always available as ``.raw`` and
via attribute / item access, so existing dict-based code keeps working.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import numpy as np

from fdars import _native

__all__ = [
    "DictResult",
    "FregreResult",
    "FPCAResult",
    "AlignmentResult",
    "SPMResult",
    "wrap_fregre",
    "wrap_fpca",
    "wrap_alignment",
    "wrap_spm",
]


# ---------------------------------------------------------------------------
# Generic base
# ---------------------------------------------------------------------------

class DictResult:
    """Attribute/item view over a result ``dict`` with a generic summary.

    Every key of the wrapped dict is exposed both as an attribute
    (``res.r_squared``) and via item access (``res["r_squared"]``).  The
    original dict is preserved untouched as :attr:`raw`.
    """

    #: Human-readable label used in ``__repr__`` / ``summary``.
    _kind = "Result"

    def __init__(self, result: Dict[str, Any]):
        if not isinstance(result, dict):
            raise TypeError(
                f"{type(self).__name__} expects a dict result, got "
                f"{type(result).__name__}"
            )
        # Store on the instance __dict__ under a private name so attribute
        # access does not clash with wrapped keys.
        object.__setattr__(self, "raw", dict(result))

    # -- dict-like access ---------------------------------------------------

    def keys(self) -> List[str]:
        """Return the keys of the wrapped result dict."""
        return list(self.raw.keys())

    def __getitem__(self, key: str) -> Any:
        return self.raw[key]

    def __contains__(self, key: str) -> bool:
        return key in self.raw

    def __getattr__(self, name: str) -> Any:
        # Only reached when normal attribute lookup fails.
        try:
            return object.__getattribute__(self, "raw")[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

    def as_dict(self) -> Dict[str, Any]:
        """Return a shallow copy of the underlying dict."""
        return dict(self.raw)

    # -- display ------------------------------------------------------------

    def _describe(self, value: Any) -> str:
        if isinstance(value, np.ndarray):
            return f"ndarray{value.shape} {value.dtype}"
        if isinstance(value, (list, tuple)):
            return f"{type(value).__name__}(len={len(value)})"
        if isinstance(value, float):
            return f"{value:.6g}"
        return repr(value)

    def __repr__(self) -> str:
        keys = ", ".join(self.keys())
        return f"{self._kind}({keys})"

    def summary(self) -> None:
        """Print a generic per-key summary of the wrapped result."""
        print(f"{self._kind}")
        print("=" * len(self._kind))
        for key, value in self.raw.items():
            print(f"  {key}: {self._describe(value)}")


# ---------------------------------------------------------------------------
# Scalar-on-function regression
# ---------------------------------------------------------------------------

class FregreResult(DictResult):
    """Wrapper for scalar-on-function regression fits.

    Wraps the dict returned by :func:`fdars.regression.fregre_lm`,
    :func:`~fdars.regression.fregre_pls`, :func:`~fdars.regression.fregre_huber`
    or :func:`~fdars.regression.fregre_l1` and exposes ``.predict``, ``.coef``,
    ``.summary`` and a rich ``__repr__``.

    Because the native ``predict_*`` functions refit from the original training
    data, this wrapper stores the training arrays and fit parameters so that
    :meth:`predict` can delegate to the matching free function.

    Parameters
    ----------
    result : dict
        The fit dict (``fitted_values``, ``residuals``, ``beta_t`` …).
    method : str
        One of ``"lm"``, ``"pls"``, ``"huber"``, ``"l1"``.
    data : numpy.ndarray
        Training functional predictors, shape ``(n, m)``.
    response : numpy.ndarray
        Training scalar response, length ``n``.
    argvals : numpy.ndarray, optional
        Evaluation grid (required for ``method="pls"``).
    n_comp : int, optional
        Number of components used for the fit (default 3).
    huber_k : float, optional
        Huber tuning constant (only for ``method="huber"``).
    """

    _kind = "FregreResult"
    _ROBUST = {"huber", "l1"}

    def __init__(
        self,
        result: Dict[str, Any],
        method: str,
        data,
        response,
        argvals=None,
        n_comp: int = 3,
        huber_k: float = 1.345,
    ):
        super().__init__(result)
        method = method.lower()
        if method not in {"lm", "pls", "huber", "l1"}:
            raise ValueError(
                f"unknown method {method!r}; expected one of "
                "'lm', 'pls', 'huber', 'l1'"
            )
        object.__setattr__(self, "method", method)
        object.__setattr__(self, "_data", np.asarray(data, dtype=np.float64))
        object.__setattr__(self, "_response", np.asarray(response, dtype=np.float64))
        object.__setattr__(
            self, "_argvals",
            None if argvals is None else np.asarray(argvals, dtype=np.float64),
        )
        object.__setattr__(self, "n_comp", int(n_comp))
        object.__setattr__(self, "huber_k", float(huber_k))

        if method == "pls" and self._argvals is None:
            raise ValueError("argvals is required for method='pls'")

    # -- predictions --------------------------------------------------------

    def predict(self, newdata) -> np.ndarray:
        """Predict responses for ``newdata`` via the matching ``predict_*``.

        Parameters
        ----------
        newdata : array_like or Fdata
            New functional predictors, shape ``(n_new, m)``.

        Returns
        -------
        numpy.ndarray
            Predicted scalar responses, length ``n_new``.
        """
        new = _as_matrix(newdata)
        reg = _native.regression
        if self.method == "lm":
            return reg.predict_fregre_lm(
                self._data, self._response, new, self.n_comp
            )
        if self.method == "pls":
            return reg.predict_fregre_pls(
                self._data, self._argvals, self._response, new, self.n_comp
            )
        # robust: l1 / huber
        return reg.predict_fregre_robust(
            self._data, self._response, new, self.n_comp,
            self.method, self.huber_k,
        )

    def coef(self) -> np.ndarray:
        """Return the coefficient function ``beta_t`` over the grid."""
        return np.asarray(self.raw["beta_t"])

    @property
    def fitted_values(self) -> np.ndarray:
        return np.asarray(self.raw["fitted_values"])

    @property
    def residuals(self) -> np.ndarray:
        return np.asarray(self.raw["residuals"])

    @property
    def r_squared(self) -> Optional[float]:
        val = self.raw.get("r_squared")
        return None if val is None else float(val)

    def __repr__(self) -> str:
        parts = [f"method={self.method}", f"n_comp={self.n_comp}"]
        if self.r_squared is not None:
            parts.append(f"R2={self.r_squared:.4f}")
        parts.append(f"n={self._data.shape[0]}")
        return f"FregreResult({', '.join(parts)})"

    def summary(self) -> None:
        print("Functional regression result")
        print("============================")
        print(f"Method: fregre_{self.method}")
        print(f"Components: {self.n_comp}")
        print(f"Training obs: {self._data.shape[0]}")
        print(f"Grid points: {self._data.shape[1]}")
        if self.r_squared is not None:
            print(f"R-squared: {self.r_squared:.6g}")
        if "intercept" in self.raw:
            print(f"Intercept: {float(self.raw['intercept']):.6g}")
        res = self.residuals
        print("Residuals:")
        print(f"  min {res.min():.4g}  mean {res.mean():.4g}  max {res.max():.4g}")
        print(f"  RMSE {np.sqrt(np.mean(res ** 2)):.6g}")


# ---------------------------------------------------------------------------
# FPCA / representation
# ---------------------------------------------------------------------------

class FPCAResult(DictResult):
    """Wrapper for FPCA / functional-representation results.

    Wraps the dict from :func:`fdars.regression.fpca` (keys ``scores``,
    ``rotation``, ``singular_values``, ``mean``, ``centered``, ``weights``) and
    provides sklearn-style accessors.
    """

    _kind = "FPCAResult"

    @property
    def components(self) -> np.ndarray:
        """Principal component functions, shape ``(m, n_comp)`` (``rotation``)."""
        return np.asarray(self.raw["rotation"])

    @property
    def scores(self) -> np.ndarray:
        """Component scores, shape ``(n, n_comp)``."""
        return np.asarray(self.raw["scores"])

    @property
    def mean(self) -> np.ndarray:
        """Mean function, length ``m``."""
        return np.asarray(self.raw["mean"])

    @property
    def singular_values(self) -> np.ndarray:
        return np.asarray(self.raw["singular_values"])

    @property
    def explained_variance(self) -> np.ndarray:
        """Per-component variance (singular values squared / (n-1))."""
        sv = self.singular_values
        n = self.scores.shape[0]
        denom = max(n - 1, 1)
        return (sv ** 2) / denom

    @property
    def explained_variance_ratio(self) -> np.ndarray:
        """Fraction of total variance explained by each component."""
        var = self.explained_variance
        total = var.sum()
        if total == 0:
            return np.zeros_like(var)
        return var / total

    @property
    def n_components(self) -> int:
        return int(self.scores.shape[1])

    def transform(self, newdata=None) -> np.ndarray:
        """Project data onto the principal components.

        Parameters
        ----------
        newdata : array_like or Fdata, optional
            New curves, shape ``(n_new, m)``.  If ``None`` the training scores
            are returned unchanged.

        Returns
        -------
        numpy.ndarray
            Scores, shape ``(n_new, n_comp)``.
        """
        if newdata is None:
            return self.scores
        new = _as_matrix(newdata)
        centered = new - self.mean[None, :]
        weights = np.asarray(self.raw.get("weights"))
        if weights is not None and weights.size == centered.shape[1]:
            return (centered * weights[None, :]) @ self.components
        return centered @ self.components

    def __repr__(self) -> str:
        evr = self.explained_variance_ratio
        cum = float(evr.sum())
        return (
            f"FPCAResult(n_components={self.n_components}, "
            f"n_obs={self.scores.shape[0]}, cum_var={cum:.4f})"
        )

    def summary(self) -> None:
        print("Functional PCA result")
        print("=====================")
        print(f"Components: {self.n_components}")
        print(f"Observations: {self.scores.shape[0]}")
        print(f"Grid points: {self.mean.shape[0]}")
        evr = self.explained_variance_ratio
        print("Explained variance ratio:")
        cum = 0.0
        for i, r in enumerate(evr):
            cum += float(r)
            print(f"  PC{i + 1}: {float(r):.4f}  (cumulative {cum:.4f})")


# ---------------------------------------------------------------------------
# Elastic alignment
# ---------------------------------------------------------------------------

class AlignmentResult(DictResult):
    """Wrapper for elastic-alignment output.

    Handles the dicts from :func:`fdars.alignment.karcher_mean`,
    :func:`~fdars.alignment.align_to_target`, and the vertical/horizontal FPCA
    routines, normalising key names via the :attr:`aligned`, :attr:`warps` and
    :attr:`mean` accessors.
    """

    _kind = "AlignmentResult"

    @property
    def aligned(self) -> Optional[np.ndarray]:
        """Aligned curves, shape ``(n, m)`` (``aligned_data``) if present."""
        val = self.raw.get("aligned_data")
        return None if val is None else np.asarray(val)

    @property
    def warps(self) -> Optional[np.ndarray]:
        """Warping functions gamma, shape ``(n, m)`` (``gammas``) if present."""
        val = self.raw.get("gammas")
        return None if val is None else np.asarray(val)

    @property
    def mean(self) -> Optional[np.ndarray]:
        """Karcher / template mean curve if present."""
        val = self.raw.get("mean")
        return None if val is None else np.asarray(val)

    @property
    def converged(self) -> Optional[bool]:
        val = self.raw.get("converged")
        return None if val is None else bool(val)

    def __repr__(self) -> str:
        parts = []
        aligned = self.aligned
        if aligned is not None:
            parts.append(f"aligned={aligned.shape}")
        if self.raw.get("n_iter") is not None:
            parts.append(f"n_iter={int(self.raw['n_iter'])}")
        if self.converged is not None:
            parts.append(f"converged={self.converged}")
        if not parts:
            parts.append(", ".join(self.keys()))
        return f"AlignmentResult({', '.join(parts)})"

    def summary(self) -> None:
        print("Elastic alignment result")
        print("========================")
        aligned = self.aligned
        if aligned is not None:
            print(f"Aligned curves: {aligned.shape[0]} × {aligned.shape[1]}")
        if self.mean is not None:
            print(f"Mean curve length: {self.mean.shape[0]}")
        if self.raw.get("n_iter") is not None:
            print(f"Iterations: {int(self.raw['n_iter'])}")
        if self.converged is not None:
            print(f"Converged: {self.converged}")
        if "distances" in self.raw:
            d = np.asarray(self.raw["distances"])
            print(f"Distances: mean {d.mean():.4g}, max {d.max():.4g}")


# ---------------------------------------------------------------------------
# Statistical process monitoring
# ---------------------------------------------------------------------------

class SPMResult(DictResult):
    """Wrapper for SPM Phase I / Phase II dicts.

    Wraps :func:`fdars.spm.spm_phase1` and :func:`fdars.spm.spm_monitor` output,
    exposing control :attr:`limits`, monitoring :attr:`statistics`, and an
    :attr:`is_ooc` out-of-control mask.
    """

    _kind = "SPMResult"

    @property
    def statistics(self) -> Dict[str, np.ndarray]:
        """Return the ``t2`` and ``spe`` statistic arrays."""
        out: Dict[str, np.ndarray] = {}
        if "t2" in self.raw:
            out["t2"] = np.asarray(self.raw["t2"])
        if "spe" in self.raw:
            out["spe"] = np.asarray(self.raw["spe"])
        return out

    @property
    def limits(self) -> Dict[str, float]:
        """Return the ``t2`` and ``spe`` upper control limits if present."""
        out: Dict[str, float] = {}
        if self.raw.get("t2_limit") is not None:
            out["t2"] = float(self.raw["t2_limit"])
        if self.raw.get("spe_limit") is not None:
            out["spe"] = float(self.raw["spe_limit"])
        return out

    @property
    def is_ooc(self) -> np.ndarray:
        """Boolean per-observation out-of-control mask (T2 OR SPE alarm).

        Uses the Phase-II ``t2_alarm`` / ``spe_alarm`` masks when present,
        otherwise derives them from the Phase-I statistics vs. their limits.
        """
        if "t2_alarm" in self.raw or "spe_alarm" in self.raw:
            n = len(np.asarray(self.raw.get("t2", self.raw.get("spe"))))
            mask = np.zeros(n, dtype=bool)
            if "t2_alarm" in self.raw:
                mask |= np.asarray(self.raw["t2_alarm"], dtype=bool)
            if "spe_alarm" in self.raw:
                mask |= np.asarray(self.raw["spe_alarm"], dtype=bool)
            return mask
        # Phase I: compare statistics to limits.
        limits = self.limits
        stats = self.statistics
        n = len(next(iter(stats.values())))
        mask = np.zeros(n, dtype=bool)
        if "t2" in stats and "t2" in limits:
            mask |= stats["t2"] > limits["t2"]
        if "spe" in stats and "spe" in limits:
            mask |= stats["spe"] > limits["spe"]
        return mask

    def __repr__(self) -> str:
        n = len(next(iter(self.statistics.values()), []))
        n_ooc = int(self.is_ooc.sum())
        phase = "phase2" if "t2_alarm" in self.raw else "phase1"
        return f"SPMResult({phase}, n={n}, out_of_control={n_ooc})"

    def summary(self) -> None:
        print("SPM monitoring result")
        print("=====================")
        phase = "Phase II" if "t2_alarm" in self.raw else "Phase I"
        print(f"Stage: {phase}")
        stats = self.statistics
        n = len(next(iter(stats.values()), []))
        print(f"Observations: {n}")
        for name, limit in self.limits.items():
            print(f"  {name.upper()} limit: {limit:.6g}")
        ooc = self.is_ooc
        print(f"Out-of-control: {int(ooc.sum())} / {n}")
        if ooc.any():
            idx = np.nonzero(ooc)[0].tolist()
            print(f"  indices: {idx}")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _as_matrix(x) -> np.ndarray:
    """Coerce an Fdata or array-like to a float64 2-D matrix."""
    data = getattr(x, "data", x)
    arr = np.asarray(data, dtype=np.float64)
    if arr.ndim == 1:
        arr = arr.reshape(1, -1)
    return arr


def wrap_fregre(
    result: Dict[str, Any],
    method: str,
    data,
    response,
    argvals=None,
    n_comp: int = 3,
    huber_k: float = 1.345,
) -> FregreResult:
    """Wrap a scalar-on-function regression fit dict in a :class:`FregreResult`."""
    return FregreResult(
        result, method, data, response,
        argvals=argvals, n_comp=n_comp, huber_k=huber_k,
    )


def wrap_fpca(result: Dict[str, Any]) -> FPCAResult:
    """Wrap an FPCA / representation dict in a :class:`FPCAResult`."""
    return FPCAResult(result)


def wrap_alignment(result: Dict[str, Any]) -> AlignmentResult:
    """Wrap an alignment dict in an :class:`AlignmentResult`."""
    return AlignmentResult(result)


def wrap_spm(result: Dict[str, Any]) -> SPMResult:
    """Wrap an SPM phase1/monitor dict in an :class:`SPMResult`."""
    return SPMResult(result)
