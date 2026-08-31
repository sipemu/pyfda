"""fdars sklearn estimator skeletons.

This module contains production-quality sklearn-compatible estimators that
wrap fdars native functions.  Each estimator:

* Inherits from the appropriate sklearn mixin and ``_BaseFdarsEstimator``.
* Stores all constructor parameters **verbatim** (no mutation in ``__init__``).
* Validates input via ``_validate(self, X, ...)`` (sets ``n_features_in_``).
* Upcasts to float64 explicitly AFTER ``_validate`` (accepts float32 inputs).
* Guards against too-small samples with a Python-layer ``ValueError`` whose
  message contains the substring ``"1 sample"`` before any native call.
* Calls ``fdars._native.*`` directly -- **never constructs an Fdata object**.

Phase plan
----------
* Plan 01 (this file): ``FPCATransformer`` -- tracer estimator, proven PASS
  by ``parametrize_with_checks`` before Plan 02 adds the remaining candidates.
* Plan 02: remaining ~30 candidate skeleton estimators added to this file.
* Plans 56-58: families reorganised into proper submodules.
"""

from __future__ import annotations

import numpy as np
from sklearn.base import TransformerMixin
from sklearn.utils.validation import check_is_fitted

from fdars.sklearn._base import _BaseFdarsEstimator, _validate
from fdars import _native


# ---------------------------------------------------------------------------
# FPCATransformer
# ---------------------------------------------------------------------------

class FPCATransformer(TransformerMixin, _BaseFdarsEstimator):
    """Functional Principal Component Analysis transformer.

    Wraps ``fdars._native.regression.fpca`` as a sklearn ``TransformerMixin``.
    Input: ``(n_obs, n_points)`` float ndarray of functional observations
    (rows = curves, columns = evaluation points).

    ``fit`` computes FPCA on the training data.  ``transform`` projects new
    observations onto the fitted components via mean-centering and dot product.

    This is a **keep-forever** production estimator -- Phase 56 imports it.

    Parameters
    ----------
    argvals : array-like of shape (n_points,) or None, optional
        Evaluation grid for the functional domain.  When None (default),
        ``np.arange(n_points)`` is used at fit time.

        **Stored verbatim** -- resolved to ``self.argvals_`` only in ``fit``.

    n_components : int, optional (default=3)
        Number of principal components to compute.  Automatically capped at
        ``min(n_obs - 1, n_points)`` during fit so it never exceeds the
        rank of the centred data.

        **Stored verbatim** -- never clipped in ``__init__``.

    Attributes
    ----------
    components_ : ndarray of shape (n_components_, n_points)
        FPCA eigenvectors (rows = components), sign-canonicalized so the
        element of largest absolute value in each component is positive.

    mean_ : ndarray of shape (n_points,)
        Per-point mean of the training data used for centering.

    n_components_ : int
        Actual number of components stored (may be less than ``n_components``
        when the training data is rank-deficient).

    argvals_ : ndarray of shape (n_points,)
        Concrete evaluation grid resolved at fit time.

    n_features_in_ : int
        Number of features (evaluation points) seen during fit, set by
        ``validate_data``.

    Notes
    -----
    SVD sign canonicalization: each component is flipped so its largest-abs
    element is positive.  This makes repeated fits on the same data produce
    identical ``components_``, satisfying ``check_fit_idempotent``.

    ``Fdata`` is **never** constructed inside this estimator; input arrays are
    passed directly to ``fdars._native.regression.fpca``.

    Examples
    --------
    >>> import numpy as np
    >>> from fdars.sklearn._skeletons import FPCATransformer
    >>> X = np.random.randn(20, 50)
    >>> est = FPCATransformer(n_components=3)
    >>> est.fit(X)
    FPCATransformer(n_components=3)
    >>> scores = est.transform(X)
    >>> scores.shape
    (20, 3)
    """

    _min_samples: int = 2  # check_fit2d_1sample guard threshold

    def __init__(self, argvals=None, n_components=3):
        super().__init__(argvals=argvals)
        self.n_components = n_components  # verbatim -- same name as param

    def fit(self, X, y=None):
        """Fit FPCA to the training data.

        Parameters
        ----------
        X : array-like of shape (n_obs, n_points)
            Functional observations (rows = curves).
        y : ignored
            Not used; present for sklearn pipeline compatibility.

        Returns
        -------
        self : FPCATransformer
            Fitted estimator.

        Raises
        ------
        ValueError
            If ``n_obs < 2`` (message contains ``"1 sample"`` substring for
            ``check_fit2d_1sample`` compliance).
        """
        X = _validate(self, X, reset=True, dtype="numeric", ensure_2d=True)
        X = X.astype(np.float64)  # upcast float32 -> float64 AFTER validate
        n_obs, n_pts = X.shape

        # Python-layer 1-sample guard -- BEFORE any native call.
        # sklearn's check_fit2d_1sample expects a ValueError whose message
        # contains the substring "1 sample" (or similar; see RESEARCH Pitfall 4).
        if n_obs < self._min_samples:
            raise ValueError(
                f"n_samples={n_obs} is too small; FPCATransformer requires "
                f"at least {self._min_samples} samples."
            )

        # Cap n_components at the maximum feasible rank.
        n_comp = min(self.n_components, n_obs - 1, n_pts)

        self.argvals_ = self._resolve_argvals(n_pts)

        result = _native.regression.fpca(X, self.argvals_, n_comp)

        # rotation: (n_pts, n_comp) from native -> transpose to (n_comp, n_pts)
        components = np.array(result["rotation"]).T
        scores = np.array(result["scores"])  # (n_obs, n_comp)

        # SVD sign canonicalization for check_fit_idempotent.
        components, scores = self._sign_canonicalize(components, scores)

        self.components_ = components           # (n_comp, n_pts)
        self.mean_ = np.array(result["mean"])   # (n_pts,)
        self.n_components_ = n_comp

        return self

    def transform(self, X):
        """Project functional observations onto the fitted FPCA components.

        Parameters
        ----------
        X : array-like of shape (n_obs, n_points)
            Functional observations to project.

        Returns
        -------
        X_transformed : ndarray of shape (n_obs, n_components_)
            FPCA scores (projections onto each component).
        """
        check_is_fitted(self)
        X = _validate(self, X, reset=False, dtype="numeric", ensure_2d=True)
        X = X.astype(np.float64)
        centered = X - self.mean_
        return centered @ self.components_.T  # (n_obs, n_components_)

    def get_feature_names_out(self, input_features=None):
        """Return output feature names for this transformer.

        Parameters
        ----------
        input_features : ignored
            Not used; present for sklearn pipeline compatibility.

        Returns
        -------
        feature_names_out : ndarray of str, shape (n_components_,)
            Strings of the form ``["fpca0", "fpca1", ...]``.
        """
        check_is_fitted(self)
        return np.array([f"fpca{i}" for i in range(self.n_components_)])
