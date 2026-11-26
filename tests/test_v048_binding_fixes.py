"""Binding-level fixes found while documenting the fdars-core 0.48 upgrade."""

import numpy as np
import pytest

from fdars import alignment as A
from fdars import metric as M


def _bumps(n=6, m=101, seed=0):
    rng = np.random.default_rng(seed)
    t = np.linspace(0, 1, m)
    c = 0.5 + 0.08 * rng.standard_normal(n)
    return np.array([np.exp(-((t - ci) / 0.08) ** 2) for ci in c]), t, c


def test_landmark_detect_and_register_default_registers_one_landmark():
    X, t, c = _bumps()
    r = A.landmark_detect_and_register(X, t, min_prominence=0.1)
    assert len(r["target_landmarks"]) == 1
    peaks = t[r["registered"].argmax(1)]
    assert np.ptp(peaks) < np.ptp(c) / 5


def test_landmark_detect_and_register_rejects_zero_count():
    X, t, _ = _bumps()
    with pytest.raises(ValueError, match="expected_count must be >= 1"):
        A.landmark_detect_and_register(X, t, expected_count=0)


def test_landmark_detect_and_register_rejects_too_few_features():
    X, t, _ = _bumps()
    with pytest.raises(ValueError, match="detected landmark"):
        A.landmark_detect_and_register(X, t, min_prominence=0.1, expected_count=2)


@pytest.mark.parametrize("fn", ["shape_mean", "shape_self_distance_matrix"])
def test_shape_quotient_unknown_raises(fn):
    X, t, _ = _bumps(n=4)
    with pytest.raises(ValueError, match="unknown quotient"):
        getattr(A, fn)(X, t, quotient="translation")


@pytest.mark.parametrize(
    "q",
    [
        "reparameterization",
        "reparameterization_translation",
        "reparameterization_translation_scale",
    ],
)
def test_shape_quotient_valid_names_accepted(q):
    X, t, _ = _bumps(n=4)
    D = A.shape_self_distance_matrix(X, t, quotient=q)
    assert D.shape == (4, 4)
    np.testing.assert_allclose(np.diag(D), 0.0, atol=1e-12)


def test_sbd_is_not_exactly_cyclic_shift_invariant():
    x = np.sin(np.linspace(0, 4 * np.pi, 64))
    y = np.roll(x, 5)
    r = M.sbd(x, y)
    assert 0.0 < r["distance"] < 0.05
    assert M.sbd(x, 3.0 * x + 2.0)["distance"] == pytest.approx(0.0, abs=1e-12)
