"""Tests for fdars.shapelet submodule (SHAPE-01).

Tests cover:
- PyShapeletFit opaque handle (shapelet_transform_fit → accessor properties)
- shapelet_transform: shape (n_test, K) with n_test ≠ n_train (transposition check)
- discover_shapelets: summary dict with n_shapelets > 0 and quality str
- shapelet_distance: (float, int) tuple; exact-window distance near zero
- shapelet_classifier_fit → PyShapeletClassifierFit handle
  - n_shapelets, train_accuracy, classes (int64), n_classes, predict
  - classifier="lda" fits without error
- Enum Err arms: invalid quality / classifier → ValueError listing valid names
"""
import numpy as np
import pytest

# ---------------------------------------------------------------------------
# Shared fixture data (created once at module load)
# ---------------------------------------------------------------------------

RNG = np.random.default_rng(42)

# Labeled 2-class dataset: n_obs=20, n_points=30 (non-square, catches transpose)
N_OBS, N_PTS = 20, 30
DATA = np.zeros((N_OBS, N_PTS))
LABELS = np.zeros(N_OBS, dtype=np.int64)
for i in range(N_OBS):
    is_class1 = i % 2 == 1
    LABELS[i] = int(is_class1)
    DATA[i] = 0.01 * i + np.arange(N_PTS) * 0.001 + RNG.standard_normal(N_PTS) * 0.05
    if is_class1:
        mid = N_PTS // 2
        DATA[i, mid : mid + 6] += np.array([1, 2, 3, 3, 2, 1])  # triangular motif

# Train/test split with different row counts — catches transpose bug
TRAIN, TRAIN_Y = DATA[:16], LABELS[:16]
TEST, TEST_Y = DATA[16:], LABELS[16:]  # n_test=4 ≠ n_train=16


# ---------------------------------------------------------------------------
# Task 1 tracer tests: shapelet_transform_fit + PyShapeletFit + shapelet_transform
# ---------------------------------------------------------------------------


def test_fit_handle_accessors():
    """shapelet_transform_fit returns PyShapeletFit with correct n_shapelets and n_train."""
    import fdars.shapelet as sh

    fit = sh.shapelet_transform_fit(TRAIN, TRAIN_Y)

    # n_shapelets > 0 — at least one shapelet discovered
    assert fit.n_shapelets > 0, f"Expected n_shapelets > 0, got {fit.n_shapelets}"
    # n_train == 16 — number of training observations
    assert fit.n_train == 16, f"Expected n_train == 16, got {fit.n_train}"


def test_transform_shape():
    """shapelet_transform returns float64 array of shape (n_test, n_shapelets)."""
    import fdars.shapelet as sh

    fit = sh.shapelet_transform_fit(TRAIN, TRAIN_Y)
    out = sh.shapelet_transform(fit, TEST)

    assert out.ndim == 2, f"Expected 2D output, got ndim={out.ndim}"
    n_test = TEST.shape[0]  # 4
    K = fit.n_shapelets
    assert out.shape == (n_test, K), (
        f"Expected shape ({n_test}, {K}), got {out.shape}"
    )
    assert out.dtype == np.float64, f"Expected float64, got {out.dtype}"


# ---------------------------------------------------------------------------
# Task 2 tests: discover_shapelets + shapelet_distance + quality Err arm
# ---------------------------------------------------------------------------


def test_discover():
    """discover_shapelets returns dict with n_shapelets > 0 and quality == 'info_gain'."""
    import fdars.shapelet as sh

    result = sh.discover_shapelets(TRAIN, TRAIN_Y)

    assert isinstance(result, dict), f"Expected dict, got {type(result)}"
    assert "n_shapelets" in result, f"Missing key 'n_shapelets': {result.keys()}"
    assert "quality" in result, f"Missing key 'quality': {result.keys()}"
    assert result["n_shapelets"] > 0, (
        f"Expected n_shapelets > 0, got {result['n_shapelets']}"
    )
    assert result["quality"] == "info_gain", (
        f"Expected quality == 'info_gain', got {result['quality']!r}"
    )


def test_distance():
    """shapelet_distance returns (float, int); exact z-normalized window distance ≈ 0.

    Uses a spike motif that appears only at one location so the best offset is unambiguous.
    """
    import fdars.shapelet as sh

    # Series with a unique spike motif starting at index 5 (not at 0 to be unambiguous)
    # Background is constant 0.0 so z-normalized windows elsewhere have sd≈0 (handled by core)
    # The spike [1,4,1] at index 5 is z-normalized uniquely
    series = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 4.0, 1.0, 0.0, 0.0, 0.0, 0.0], dtype=np.float64)
    window_start = 5  # spike window [1, 4, 1]
    window = series[window_start : window_start + 3].copy()
    # z-normalize the window
    mu = window.mean()
    sd = window.std()
    if sd < 1e-10:
        sd = 1.0
    window_z = (window - mu) / sd

    dist, offset = sh.shapelet_distance(window_z, series)

    assert isinstance(dist, float), f"Expected float distance, got {type(dist)}"
    assert isinstance(offset, int), f"Expected int offset, got {type(offset)}"
    # Exact-window match should yield near-zero distance
    assert dist < 1e-6, f"Expected dist < 1e-6 for exact match, got {dist}"
    assert offset == window_start, f"Expected offset={window_start}, got {offset}"


def test_quality_err_arm():
    """An invalid quality string raises ValueError listing valid variants."""
    import fdars.shapelet as sh

    with pytest.raises(ValueError, match="info_gain") as exc_info:
        sh.discover_shapelets(TRAIN, TRAIN_Y, quality="bogus")
    assert "f_statistic" in str(exc_info.value), (
        f"Error message must list 'f_statistic': {exc_info.value}"
    )


# ---------------------------------------------------------------------------
# Task 3 tests: shapelet_classifier_fit → PyShapeletClassifierFit handle
# ---------------------------------------------------------------------------


def test_classifier_handle_accessors():
    """shapelet_classifier_fit returns handle with correct n_shapelets, train_accuracy, classes."""
    import fdars.shapelet as sh

    handle = sh.shapelet_classifier_fit(TRAIN, TRAIN_Y)

    assert handle.n_shapelets > 0, f"Expected n_shapelets > 0, got {handle.n_shapelets}"
    assert 0.0 <= handle.train_accuracy <= 1.0, (
        f"Expected train_accuracy in [0,1], got {handle.train_accuracy}"
    )
    assert handle.classes.dtype == np.int64, (
        f"Expected classes dtype int64, got {handle.classes.dtype}"
    )
    assert handle.n_classes == 2, f"Expected n_classes == 2, got {handle.n_classes}"


def test_classifier_predict_shape():
    """handle.predict(TEST) returns a 1D int64 array of length n_test (=4)."""
    import fdars.shapelet as sh

    handle = sh.shapelet_classifier_fit(TRAIN, TRAIN_Y)
    preds = handle.predict(TEST)

    assert preds.ndim == 1, f"Expected 1D predictions, got ndim={preds.ndim}"
    assert preds.shape[0] == TEST.shape[0], (
        f"Expected {TEST.shape[0]} predictions, got {preds.shape[0]}"
    )
    assert preds.dtype == np.int64, f"Expected int64 predictions, got {preds.dtype}"


def test_classifier_lda():
    """classifier='lda' fits and predicts without error."""
    import fdars.shapelet as sh

    handle = sh.shapelet_classifier_fit(TRAIN, TRAIN_Y, classifier="lda")
    preds = handle.predict(TEST)

    assert preds.ndim == 1
    assert preds.shape[0] == TEST.shape[0]
    assert preds.dtype == np.int64


def test_classifier_err_arm():
    """An invalid classifier string raises ValueError listing valid classifiers."""
    import fdars.shapelet as sh

    with pytest.raises(ValueError, match="knn") as exc_info:
        sh.shapelet_classifier_fit(TRAIN, TRAIN_Y, classifier="bogus")
    assert "lda" in str(exc_info.value), (
        f"Error message must list 'lda': {exc_info.value}"
    )


def test_negative_label_rejected():
    """Negative labels raise ValueError from labels_i64_to_usize guard."""
    import fdars.shapelet as sh

    bad_labels = TRAIN_Y.copy()
    bad_labels[0] = -1
    with pytest.raises(ValueError, match="negative"):
        sh.shapelet_transform_fit(TRAIN, bad_labels)
    with pytest.raises(ValueError, match="negative"):
        sh.discover_shapelets(TRAIN, bad_labels)
    with pytest.raises(ValueError, match="negative"):
        sh.shapelet_classifier_fit(TRAIN, bad_labels)


def test_knn_k_zero_rejected():
    """classifier='knn', k=0 raises ValueError from binding-level guard."""
    import fdars.shapelet as sh

    with pytest.raises(ValueError, match="k must be >= 1"):
        sh.shapelet_classifier_fit(TRAIN, TRAIN_Y, classifier="knn", k=0)
