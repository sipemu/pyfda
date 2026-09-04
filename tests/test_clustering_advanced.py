"""Tests for advanced functional clustering: dbscan_fd, kcfc_cluster, funfem_cluster, align_cluster_fd.

All tests use a NON-SQUARE fixture (n_obs=20, n_points=30) to guard against transposition bugs.
"""

import numpy as np
import pytest
import fdars.clustering as clustering


# ---------------------------------------------------------------------------
# Shared non-square fixture (n_obs ≠ n_points — transposition guard)
# ---------------------------------------------------------------------------

@pytest.fixture
def data_and_argvals():
    rng = np.random.default_rng(42)
    n_obs, n_points = 20, 30
    data = rng.standard_normal((n_obs, n_points))
    argvals = np.linspace(0.0, 1.0, n_points)
    return data, argvals


# ---------------------------------------------------------------------------
# dbscan_fd
# ---------------------------------------------------------------------------

def test_dbscan_fd(data_and_argvals):
    data, argvals = data_and_argvals
    result = clustering.dbscan_fd(data, argvals, eps=0.5, min_points=3)

    # Keys
    assert set(result.keys()) == {"cluster", "n_clusters", "n_noise", "distances"}

    # cluster dtype must be int64 with -1 encoding noise
    labels = result["cluster"]
    assert labels.dtype == np.int64
    assert labels.shape == (20,)
    # All values are either -1 (noise) or a non-negative cluster id
    assert np.all(labels >= -1)

    # distances is the pairwise n×n matrix
    assert result["distances"].shape == (20, 20)

    # n_noise == count of -1 labels
    assert result["n_noise"] == int(np.sum(labels == -1))

    # Explicitly assert the None→-1 encoding path fires for this fixture.
    # With eps=0.5 on 30-dimensional standard-normal data (L2 distance ≈ 7–10 >> 0.5)
    # every point is noise, so this is a coded contract — not just statistical luck.
    assert result["n_noise"] > 0, (
        "Expected at least one noise point with eps=0.5 on 30-dimensional random data"
    )


# ---------------------------------------------------------------------------
# kcfc_cluster
# ---------------------------------------------------------------------------

def test_kcfc_cluster(data_and_argvals):
    data, argvals = data_and_argvals
    result = clustering.kcfc_cluster(data, argvals, k=3)

    # fpca_models must NOT be present (internal Rust state)
    assert "fpca_models" not in result

    # Required keys
    assert "reconstruction_errors" in result
    assert "cluster" in result
    assert "iterations" in result
    assert "converged" in result

    # Shapes
    assert result["cluster"].shape == (20,)
    assert result["reconstruction_errors"].shape == (20, 3)

    # cluster labels are ints in [0, k)
    assert result["cluster"].dtype == np.int64


# ---------------------------------------------------------------------------
# funfem_cluster
# ---------------------------------------------------------------------------

def test_funfem_cluster(data_and_argvals):
    data, argvals = data_and_argvals
    result = clustering.funfem_cluster(data, argvals, k=2)

    # Required keys
    for key in ("cluster", "membership", "disc_subspace", "log_likelihood", "iterations", "converged"):
        assert key in result, f"missing key: {key}"

    # membership shape: (n, k) = (20, 2)
    assert result["membership"].shape == (20, 2)

    # cluster shape
    assert result["cluster"].shape == (20,)
    assert result["cluster"].dtype == np.int64

    # log_likelihood is a finite float
    assert np.isfinite(result["log_likelihood"])


# ---------------------------------------------------------------------------
# align_cluster_fd
# ---------------------------------------------------------------------------

def test_align_cluster_fd(data_and_argvals):
    data, argvals = data_and_argvals
    result = clustering.align_cluster_fd(data, argvals, k=3)

    # Required keys
    for key in ("cluster", "templates", "distances", "iterations", "converged"):
        assert key in result, f"missing key: {key}"

    # templates: list of length k=3, each shape (n_points,) = (30,)
    templates = result["templates"]
    assert len(templates) == 3
    for tmpl in templates:
        assert isinstance(tmpl, np.ndarray)
        assert tmpl.shape == (30,)

    # distances shape: (n_obs, k) = (20, 3)
    assert result["distances"].shape == (20, 3)

    # cluster labels
    assert result["cluster"].shape == (20,)
    assert result["cluster"].dtype == np.int64
