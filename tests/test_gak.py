"""Tests for GAK (Global Alignment Kernel) metric bindings in fdars.metric.

SHAPE-02: gak, sigma_gak, gak_gram_matrix, gak_gram_train, gak_gram_predict,
and the PyGakGramTrain opaque handle.
"""
import numpy as np
import pytest
import fdars.metric as m

# ---------------------------------------------------------------------------
# Fixtures (RESEARCH §6.2)
# ---------------------------------------------------------------------------

RNG = np.random.default_rng(7)

# Non-square Gram fixture: n_train=8, n_points=25 (8 ≠ 25)
N_TRAIN, N_PTS = 8, 25
TRAIN_MAT = RNG.standard_normal((N_TRAIN, N_PTS))

# Test set: n_test=3 ≠ n_train=8 (non-square Gram proves orientation)
N_TEST = 3
TEST_MAT = RNG.standard_normal((N_TEST, N_PTS))

# Two 1D series for pairwise gak()
X = np.array([0.0, 1.0, 2.0, 3.0])
Y = np.array([0.0, 1.0, 2.0, 3.0])  # identical → gak should be ≈ 1.0
Z = np.array([3.0, 2.0, 1.0, 0.0])  # reversed → distinct from X

# Shared sigma for scalar tests
SIGMA = m.sigma_gak(TRAIN_MAT)


# ---------------------------------------------------------------------------
# Task 1: gak + sigma_gak + gak_gram_matrix (tracer)
# ---------------------------------------------------------------------------

def test_gak_self_similarity():
    """gak(X, X, sigma) == 1.0; gak(X, Z, sigma) in [0, 1]."""
    assert callable(m.gak), "gak must be callable on fdars.metric"
    val_self = m.gak(X, X, SIGMA)   # same variable — true self-similarity
    assert abs(val_self - 1.0) < 1e-9, f"gak(X, X, sigma) should be exactly 1.0, got {val_self}"
    val_cross = m.gak(X, Z, SIGMA)
    assert 0.0 <= val_cross <= 1.0, f"gak(X, Z, sigma) must be in [0, 1], got {val_cross}"


def test_sigma_gak():
    """sigma_gak(data) returns a positive float."""
    assert callable(m.sigma_gak), "sigma_gak must be callable on fdars.metric"
    s = m.sigma_gak(TRAIN_MAT)
    assert isinstance(s, float), f"sigma_gak must return float, got {type(s)}"
    assert s > 0, f"sigma_gak must return > 0, got {s}"


def test_gram_matrix_shape():
    """gak_gram_matrix: (8, 8), unit diagonal, symmetric."""
    assert callable(m.gak_gram_matrix), "gak_gram_matrix must be callable on fdars.metric"
    G = m.gak_gram_matrix(TRAIN_MAT)
    assert G.shape == (N_TRAIN, N_TRAIN), f"gram must be ({N_TRAIN},{N_TRAIN}), got {G.shape}"
    np.testing.assert_allclose(np.diag(G), np.ones(N_TRAIN), atol=1e-9,
                               err_msg="gram diagonal must be all ~1.0")
    assert np.allclose(G, G.T, atol=1e-12), "gram must be symmetric"


# ---------------------------------------------------------------------------
# Task 2: PyGakGramTrain handle + gak_gram_train
# ---------------------------------------------------------------------------

def test_gram_train_handle():
    """gak_gram_train returns a PyGakGramTrain with gram (8,8), sigma>0, n_train==8."""
    assert callable(m.gak_gram_train), "gak_gram_train must be callable on fdars.metric"
    handle = m.gak_gram_train(TRAIN_MAT)
    assert hasattr(handle, "gram"), "handle must expose .gram"
    assert hasattr(handle, "sigma"), "handle must expose .sigma"
    assert hasattr(handle, "n_train"), "handle must expose .n_train"
    assert handle.gram.shape == (N_TRAIN, N_TRAIN), \
        f"handle.gram must be ({N_TRAIN},{N_TRAIN}), got {handle.gram.shape}"
    assert handle.sigma > 0, f"handle.sigma must be > 0, got {handle.sigma}"
    assert handle.n_train == N_TRAIN, f"handle.n_train must be {N_TRAIN}, got {handle.n_train}"


def test_gram_train_matches_matrix():
    """handle.gram matches gak_gram_matrix(TRAIN_MAT) within 1e-12."""
    handle = m.gak_gram_train(TRAIN_MAT)
    G_matrix = m.gak_gram_matrix(TRAIN_MAT)
    np.testing.assert_allclose(handle.gram, G_matrix, atol=1e-12,
                               err_msg="handle.gram must match gak_gram_matrix")


# ---------------------------------------------------------------------------
# Task 3: gak_gram_predict — (n_test, n_train) precomputed-kernel contract
# ---------------------------------------------------------------------------

def test_gram_predict_shape():
    """gak_gram_predict(handle, TEST_MAT) is shape (3, 8): n_test ≠ n_train."""
    assert callable(m.gak_gram_predict), "gak_gram_predict must be callable on fdars.metric"
    handle = m.gak_gram_train(TRAIN_MAT)
    K = m.gak_gram_predict(handle, TEST_MAT)
    assert K.shape == (N_TEST, N_TRAIN), \
        f"predict must be ({N_TEST},{N_TRAIN}) — (n_test, n_train) contract; got {K.shape}"


def test_gram_predict_reproduces_train():
    """gak_gram_predict(handle, TRAIN_MAT) reproduces handle.gram within 1e-12."""
    handle = m.gak_gram_train(TRAIN_MAT)
    K = m.gak_gram_predict(handle, TRAIN_MAT)
    np.testing.assert_allclose(K, handle.gram, atol=1e-12,
                               err_msg="predict on train data must reproduce handle.gram")
