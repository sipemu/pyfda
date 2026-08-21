"""Tests for fdars.outliers — tvdmss, muod, sequential_transform_outliers, depthgram."""

import numpy as np
import pytest
from fdars import outliers as outl


class TestTvdMss:
    """Tests for fdars.outliers.tvdmss (OUTL-01)."""

    def test_tvdmss_smoke(self):
        """tvdmss returns a 4-key dict with correct types and shapes."""
        rng = np.random.default_rng(1)
        data = rng.standard_normal((15, 30))
        data[0, :] += 10  # plant a magnitude outlier

        result = outl.tvdmss(data)

        assert set(result.keys()) == {"magnitude_outliers", "shape_outliers", "tvd", "mss"}

        for key in ("magnitude_outliers", "shape_outliers"):
            v = result[key]
            assert isinstance(v, list), f"{key} must be a list, got {type(v)}"
            assert all(isinstance(i, int) for i in v), f"{key} elements must be int"

        for key in ("tvd", "mss"):
            arr = result[key]
            assert isinstance(arr, np.ndarray), f"{key} must be ndarray"
            assert arr.shape == (15,), f"{key} shape must be (15,), got {arr.shape}"


class TestMuod:
    """Tests for fdars.outliers.muod (OUTL-02)."""

    def test_muod_smoke(self):
        """muod returns a 6-key dict with 3 list[int] index sets + 3 (n,) arrays."""
        rng = np.random.default_rng(2)
        data = rng.standard_normal((15, 30))
        data[0, :] += 10  # plant an outlier

        result = outl.muod(data)

        expected_keys = {
            "shape_outliers",
            "magnitude_outliers",
            "amplitude_outliers",
            "shape_index",
            "magnitude_index",
            "amplitude_index",
        }
        assert set(result.keys()) == expected_keys

        for key in ("shape_outliers", "magnitude_outliers", "amplitude_outliers"):
            v = result[key]
            assert isinstance(v, list), f"{key} must be a list, got {type(v)}"
            assert all(isinstance(i, int) for i in v), f"{key} elements must be int"

        for key in ("shape_index", "magnitude_index", "amplitude_index"):
            arr = result[key]
            assert isinstance(arr, np.ndarray), f"{key} must be ndarray"
            assert arr.shape == (15,), f"{key} shape must be (15,), got {arr.shape}"

    def test_muod_degenerate(self):
        """muod raises ValueError when n < 3 (below core minimum)."""
        data = np.zeros((2, 30))
        with pytest.raises(ValueError):
            outl.muod(data)
