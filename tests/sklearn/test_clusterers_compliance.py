"""Per-clusterer compliance tests for fdars sklearn clusterers.

Each test function uses ``parametrize_with_checks`` to run the full
scikit-learn estimator battery for ONE clusterer in isolation.  This
keeps each clusterer's battery independently selectable and fast.

Scope (Plan 03 — Wave 3 / Phase 58)
-------------------------------------
* ``test_functional_kmeans_compliance``  — FunctionalKMeans (CLUS-01)
* ``test_fuzzy_cmeans_compliance``       — FuzzyFunctionalCMeans (CLUS-02)
* ``test_functional_gmm_compliance``     — FunctionalGMM (CLUS-02)

Key design decisions
---------------------
* FunctionalKMeans: ``random_state`` maps to ``check_random_state`` → u64 seed.
  The rayon-parallel ``kmeans_fd`` path is empirically deterministic under a
  fixed seed, so NO ``non_deterministic`` sklearn tag is needed.  A plain
  determinism assertion (``test_functional_kmeans_deterministic``) pins this.
* FuzzyFunctionalCMeans and FunctionalGMM: ``n_iter_ = max_iter`` set in
  ``fit`` (native exposes no iteration count; same convention as
  ``LogisticFPCClassifier``).  This resolves deferred review WR-03 and makes
  ``check_non_transformer_estimators_n_iter`` pass for both estimators.

Usage
-----
Run a single clusterer battery::

    pytest tests/sklearn/test_clusterers_compliance.py::test_functional_kmeans_compliance -v

Run all clusterer compliance tests::

    pytest tests/sklearn/test_clusterers_compliance.py -q
"""

from __future__ import annotations

import numpy as np
from sklearn.utils.estimator_checks import parametrize_with_checks

from fdars.sklearn._skeletons import (
    FunctionalGMM,
    FunctionalKMeans,
    FuzzyFunctionalCMeans,
)


# ---------------------------------------------------------------------------
# CLUS-01 — FunctionalKMeans compliance (Plan 03 / Phase 58)
# ---------------------------------------------------------------------------


@parametrize_with_checks([FunctionalKMeans(n_clusters=2)])
def test_functional_kmeans_compliance(estimator, check):
    """Full parametrize_with_checks battery for FunctionalKMeans (CLUS-01).

    Regression guard confirming FunctionalKMeans remains green after the
    clusterer n_iter_ fix in Plan 03.

    Verifies:
    - ``check_clustering``: labels_ integer dtype, fits with n_clusters=2.
    - ``check_methods_subset_invariance``: stored-cluster predict (L2 centroid).
    - ``check_estimators_dtypes``: float32 input upcast to float64.
    - ``check_non_transformer_estimators_n_iter``: n_iter_ set from result["iter"].
    """
    check(estimator)


# ---------------------------------------------------------------------------
# CLUS-02 — FuzzyFunctionalCMeans compliance (Plan 03 / Phase 58)
# ---------------------------------------------------------------------------


@parametrize_with_checks([FuzzyFunctionalCMeans(n_clusters=2)])
def test_fuzzy_cmeans_compliance(estimator, check):
    """Full parametrize_with_checks battery for FuzzyFunctionalCMeans (CLUS-02).

    Verifies ``check_non_transformer_estimators_n_iter`` is now green:
    ``fit`` sets ``self.n_iter_ = self.max_iter`` because ``fuzzy_cmeans_fd``
    exposes no iteration count (WR-03 resolved).

    Verifies:
    - ``check_clustering``: labels_ integer dtype, fits with n_clusters=2.
    - ``check_methods_subset_invariance``: stored-center predict (L2 distance).
    - ``check_estimators_dtypes``: float32 input upcast to float64.
    - ``check_non_transformer_estimators_n_iter``: n_iter_ == max_iter.
    """
    check(estimator)


# ---------------------------------------------------------------------------
# CLUS-02 — FunctionalGMM compliance (Plan 03 / Phase 58)
# ---------------------------------------------------------------------------


@parametrize_with_checks([FunctionalGMM(n_clusters=2)])
def test_functional_gmm_compliance(estimator, check):
    """Full parametrize_with_checks battery for FunctionalGMM (CLUS-02).

    Verifies ``check_non_transformer_estimators_n_iter`` is now green:
    ``fit`` sets ``self.n_iter_ = self.max_iter`` because ``gmm_cluster``
    exposes bic/icl values but no EM iteration count (WR-03 resolved).

    Verifies:
    - ``check_clustering``: labels_ integer dtype, fits with n_clusters=2.
    - ``check_methods_subset_invariance``: membership-weighted centroid predict.
    - ``check_estimators_dtypes``: float32 input upcast to float64.
    - ``check_non_transformer_estimators_n_iter``: n_iter_ == max_iter.
    """
    check(estimator)


# ---------------------------------------------------------------------------
# CLUS-01 determinism regression test (Plan 03 / Phase 58)
# ---------------------------------------------------------------------------


def test_functional_kmeans_deterministic():
    """FunctionalKMeans is deterministic under a fixed random_state (CLUS-01).

    The rayon-parallel ``kmeans_fd`` path is empirically deterministic when
    given the same seed — two independent fits with ``random_state=7`` must
    produce identical ``labels_`` arrays.  This determinism means NO sklearn
    ``non_deterministic`` tag is required on FunctionalKMeans.

    Design note: ``random_state`` is mapped to a u64 seed via
    ``check_random_state(self.random_state).randint(0, 2**31)``; the same
    Python RandomState seed always yields the same u64, so the native path
    sees identical initialization across calls.
    """
    X = np.random.RandomState(0).rand(40, 15)
    labels_a = FunctionalKMeans(n_clusters=3, random_state=7).fit(X).labels_
    labels_b = FunctionalKMeans(n_clusters=3, random_state=7).fit(X).labels_
    assert np.array_equal(labels_a, labels_b), (
        "FunctionalKMeans produced different labels_ across two fits with the "
        f"same random_state=7. First 10: {labels_a[:10]} vs {labels_b[:10]}"
    )
