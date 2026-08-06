"""Pure-Python orchestration helpers injected into native submodule namespaces.

These mirror R functions that are orchestration over primitives (not fdars-core
functions): e.g. ``cluster.optim`` / ``cluster.init``. ``install()`` attaches them
onto the relevant native module so they are reachable at the expected path
(``fdars.clustering.cluster_optim``), matching the R layout.
"""

from __future__ import annotations

import numpy as np

__all__ = ["install"]


def _cluster_optim(data, argvals, k_range, criterion="silhouette", max_iter=100,
                   tol=1e-6, seed=42):
    """Select the number of clusters over ``k_range`` (R ``cluster.optim``).

    Fits k-means for each k and scores it with the chosen ``criterion``
    (``silhouette`` or ``calinski``), returning the best model.

    Returns a dict: ``best_k``, ``cluster``, ``centers``, ``scores`` (per k),
    ``k_values``, ``criterion``.
    """
    from fdars import clustering as _cl

    data = np.ascontiguousarray(np.asarray(data, dtype=float))
    argvals = np.asarray(argvals, dtype=float).ravel()
    ks = [int(k) for k in k_range]
    if any(k < 2 for k in ks):
        raise ValueError("cluster_optim requires k >= 2 for every candidate")

    scores, fits = [], {}
    for k in ks:
        fit = _cl.kmeans_fd(data, argvals, k, max_iter=max_iter, tol=tol, seed=seed)
        labels = np.asarray(fit["cluster"], dtype=np.int64)
        if criterion in ("silhouette", "sil"):
            score = float(np.mean(_cl.silhouette_score_data(data, argvals, labels)))
        elif criterion in ("calinski", "calinski_harabasz", "ch"):
            score = float(_cl.calinski_harabasz_data(data, argvals, labels))
        else:
            raise ValueError("criterion must be 'silhouette' or 'calinski'")
        scores.append(score)
        fits[k] = fit
    best_i = int(np.argmax(scores))
    best_k = ks[best_i]
    best = fits[best_k]
    return {
        "best_k": best_k,
        "cluster": best["cluster"],
        "centers": best["centers"],
        "scores": np.asarray(scores, dtype=float),
        "k_values": np.asarray(ks, dtype=np.int64),
        "criterion": criterion,
    }


def _cluster_init(data, argvals=None, k=2, seed=42):
    """k-means++ seeding: pick ``k`` initial centers (R ``cluster.init``).

    Returns a dict: ``centers`` (k, m), ``indices`` (k,) rows chosen as centers.
    """
    X = np.ascontiguousarray(np.asarray(data, dtype=float))
    n = X.shape[0]
    if k < 1 or k > n:
        raise ValueError("require 1 <= k <= n")
    rng = np.random.default_rng(seed)
    idx = [int(rng.integers(n))]
    # squared distances to the nearest chosen center
    d2 = np.sum((X - X[idx[0]]) ** 2, axis=1)
    for _ in range(1, k):
        total = d2.sum()
        probs = d2 / total if total > 0 else np.full(n, 1.0 / n)
        j = int(rng.choice(n, p=probs))
        idx.append(j)
        d2 = np.minimum(d2, np.sum((X - X[j]) ** 2, axis=1))
    indices = np.asarray(idx, dtype=np.int64)
    return {"centers": X[indices].copy(), "indices": indices}


def install():
    """Attach the pure-Python helpers onto their native submodules."""
    from fdars import clustering as _cl

    _cl.cluster_optim = _cluster_optim
    _cl.cluster_init = _cluster_init
