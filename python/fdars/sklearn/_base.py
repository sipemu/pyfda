"""Shared base class and compat shims for fdars sklearn estimators.

This module provides:

* ``_validate`` -- hand-rolled shim bridging sklearn 1.3-1.5 (private
  ``estimator._validate_data``) and sklearn 1.6+ (public
  ``sklearn.utils.validation.validate_data``). In sklearn 1.8 the private
  ``_validate_data`` method is removed; the public function is the only path.

* ``_HAS_TAGS_DATACLASS`` -- bool flag; True when sklearn exposes the
  ``Tags`` dataclass (1.6+). In sklearn 1.8 ``_more_tags()`` / ``_get_tags()``
  are removed; only ``__sklearn_tags__`` is supported.

* ``_sign_canonicalize`` -- static helper for SVD sign canonicalization
  (largest-abs element positive per component), required for
  ``check_fit_idempotent`` on FPCA-family estimators.

* ``_BaseFdarsEstimator`` -- concrete base class for all fdars sklearn
  estimators. Centralises: verbatim constructor storage; ``argvals_``
  resolution at fit time; ``n_features_in_`` via ``validate_data``; float32
  to float64 upcast pattern; and 1-sample guard helpers.

Compatibility span: sklearn 1.3 through 1.8 (and beyond, as long as the
public ``validate_data`` function and ``__sklearn_tags__`` are stable).
Feature detection uses ``hasattr``/``try-import`` rather than version
comparisons so it degrades gracefully as the API evolves.
"""

from __future__ import annotations

import numpy as np

# ---------------------------------------------------------------------------
# validate_data shim
# ---------------------------------------------------------------------------
# sklearn 1.6 made validate_data a public module-level function.
# sklearn 1.8 REMOVED the private estimator._validate_data method.
# We try the public function first so the 1.8 path is the primary branch.

try:
    from sklearn.utils.validation import validate_data as _sklearn_validate_data  # 1.6+

    def _validate(estimator, X, y=None, *, reset=True, dtype="numeric", **kw):
        """Validate input data via the sklearn 1.6+ public validate_data function.

        Parameters
        ----------
        estimator : BaseEstimator
            The estimator instance (sets n_features_in_ as a side effect).
        X : array-like
            Input feature matrix.
        y : array-like or None
            Target array. When None, only X is validated.
        reset : bool
            True on the first call (fit); False on subsequent calls (transform/predict).
        dtype : str or type
            Use ``"numeric"`` to accept any numeric dtype; do NOT use
            ``np.float64`` here (that rejects float32 non-compliantly).
            Upcast to float64 explicitly after this call.
        **kw
            Forwarded to validate_data (e.g. ensure_2d=True).

        Returns
        -------
        np.ndarray or tuple
            Validated X (and y if provided).
        """
        if y is not None:
            return _sklearn_validate_data(estimator, X, y, reset=reset, dtype=dtype, **kw)
        return _sklearn_validate_data(estimator, X, reset=reset, dtype=dtype, **kw)

except ImportError:
    # sklearn 1.3-1.5 fallback — _validate_data is a private estimator method.
    def _validate(estimator, X, y=None, *, reset=True, dtype="numeric", **kw):  # type: ignore[misc]
        """Validate input data via the sklearn 1.3-1.5 private _validate_data method.

        Parameters
        ----------
        estimator : BaseEstimator
            The estimator instance.
        X : array-like
            Input feature matrix.
        y : array-like or None
            Target array.
        reset : bool
            True on the first call (fit); False on subsequent calls.
        dtype : str or type
            Use ``"numeric"`` to accept any numeric dtype.
        **kw
            Forwarded to _validate_data.

        Returns
        -------
        np.ndarray or tuple
        """
        if y is not None:
            return estimator._validate_data(X, y, reset=reset, dtype=dtype, **kw)
        return estimator._validate_data(X, reset=reset, dtype=dtype, **kw)


# ---------------------------------------------------------------------------
# Tags API detection
# ---------------------------------------------------------------------------
# sklearn 1.6 introduced the Tags dataclass and __sklearn_tags__().
# sklearn 1.8 removed _more_tags() / _get_tags() entirely.
# We detect which API is present and set _HAS_TAGS_DATACLASS accordingly.

_HAS_TAGS_DATACLASS: bool = False
try:
    from sklearn.utils import Tags as _SklearnTags  # noqa: F401 -- 1.6+
    _HAS_TAGS_DATACLASS = True
except ImportError:
    pass

from sklearn.base import BaseEstimator  # noqa: E402


# ---------------------------------------------------------------------------
# Base class
# ---------------------------------------------------------------------------

class _BaseFdarsEstimator(BaseEstimator):
    """Shared contract enforcement base for all fdars sklearn estimators.

    Centralises the sklearn API contract so subclass ``fit``/``transform``/
    ``predict`` methods only need to implement the functional logic.

    Constructor Parameters
    ----------------------
    argvals : array-like or None, optional
        Evaluation grid for the functional observations (the time/domain points).
        When None, ``_resolve_argvals(n_features)`` returns ``np.arange(n_features)``.

        **Stored verbatim** -- no conversion in ``__init__``. This is required
        for ``clone()`` / ``get_params()`` / ``set_params()`` round-trips (the
        sklearn clone contract requires that constructor args equal the stored
        attribute values exactly, so BaseEstimator.get_params() introspects
        ``__init__`` and returns them unchanged).

    Notes
    -----
    Subclasses MUST:

    * Call ``super().__init__(argvals=argvals)`` in their own ``__init__``.
    * Store all additional constructor params verbatim (no mutation).
    * Call ``_validate(self, X, reset=True, dtype="numeric", ensure_2d=True)``
      at the top of ``fit`` to set ``n_features_in_``.
    * Call ``X = X.astype(np.float64)`` AFTER ``_validate`` to upcast float32.
    * Call ``self.argvals_ = self._resolve_argvals(n_pts)`` in ``fit`` -- ONLY
      in fit, never in ``__init__``.
    * Define a class-level ``_min_samples`` attribute and raise a ``ValueError``
      whose message contains the substring ``"1 sample"`` before any native call
      when ``n_obs < self._min_samples``. This satisfies ``check_fit2d_1sample``.

    Subclasses MUST NOT:
    * Convert ``self.argvals`` in ``__init__`` (breaks clone round-trip).
    * Construct ``Fdata`` objects internally (dtype side-effects break
      ``check_estimators_dtypes``).
    * Call fdars native functions with float32 input (upcast first).
    """

    def __init__(self, argvals=None):
        # VERBATIM storage -- no conversion, no None-to-arange, no np.asarray.
        # BaseEstimator.get_params() introspects the __init__ signature and
        # returns stored attributes by name; clone() calls set_params() with
        # the returned values.  If argvals=None is passed we must store None --
        # converting it to np.arange(n) here would make get_params() return an
        # array, and clone() would then try to set_params(argvals=<array>).
        self.argvals = argvals

    def _resolve_argvals(self, n_features: int) -> np.ndarray:
        """Resolve the ``argvals`` constructor parameter at fit time.

        Parameters
        ----------
        n_features : int
            Number of evaluation points (columns of the input X after validation).

        Returns
        -------
        np.ndarray, shape (n_features,), dtype float64
            Concrete evaluation grid.  Defaults to ``np.arange(n_features)``
            when ``self.argvals is None``.
        """
        if self.argvals is None:
            return np.arange(n_features, dtype=np.float64)
        return np.asarray(self.argvals, dtype=np.float64)

    @staticmethod
    def _sign_canonicalize(
        components: np.ndarray, scores: np.ndarray
    ) -> tuple[np.ndarray, np.ndarray]:
        """Flip SVD components so each component's largest-abs element is positive.

        This makes FPCA decomposition deterministic across restarts, satisfying
        ``check_fit_idempotent``.  The same sign flip is applied to the
        corresponding score columns so the projection remains consistent.

        Parameters
        ----------
        components : np.ndarray, shape (n_components, n_pts)
            Component matrix (rows = components).
        scores : np.ndarray, shape (n_obs, n_components)
            Score matrix (columns = scores for each component).

        Returns
        -------
        components : np.ndarray
            Sign-canonicalized components (same shape).
        scores : np.ndarray
            Consistently sign-flipped scores (same shape).
        """
        max_abs_idx = np.argmax(np.abs(components), axis=1)  # (n_components,)
        signs = np.sign(components[np.arange(len(components)), max_abs_idx])
        signs = np.where(signs == 0, 1.0, signs)  # keep unflipped if all-zero component
        components = components * signs[:, np.newaxis]
        scores = scores * signs[np.newaxis, :]
        return components, scores

    # Tags API override -- defined based on which sklearn version is present.
    # sklearn 1.8+: only __sklearn_tags__() exists; _more_tags() is gone.
    # sklearn 1.6-1.7: __sklearn_tags__() exists; _more_tags() deprecated.
    # sklearn 1.3-1.5: only _more_tags() dict exists.
    if _HAS_TAGS_DATACLASS:
        def __sklearn_tags__(self):
            """Return the Tags dataclass for this estimator (sklearn 1.6+)."""
            tags = super().__sklearn_tags__()
            # Subclasses may override to set non_deterministic=True etc.
            return tags
    else:
        def _more_tags(self):  # type: ignore[override]
            """Return the tags dict for this estimator (sklearn 1.3-1.5)."""
            # Return empty dict -- BaseEstimator merges with its own defaults.
            return {}
