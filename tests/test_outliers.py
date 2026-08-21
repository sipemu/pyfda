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


class TestSeqTransform:
    """Tests for fdars.outliers.sequential_transform_outliers (OUTL-03)."""

    def test_seqtransform_smoke(self):
        """sequential_transform_outliers returns correct dict structure."""
        rng = np.random.default_rng(3)
        data = rng.standard_normal((15, 30))
        data[0, :] += 10

        result = outl.sequential_transform_outliers(data, transforms=["t0", "t1", "d1"])

        assert set(result.keys()) == {"per_transform_outliers", "union_outliers"}

        per_tf = result["per_transform_outliers"]
        assert isinstance(per_tf, list)
        assert len(per_tf) == 3

        valid_tokens = {"t0", "t1", "t2", "d1", "d2"}
        for entry in per_tf:
            assert isinstance(entry, dict)
            assert set(entry.keys()) == {"transform", "outliers"}
            assert entry["transform"] in valid_tokens
            outliers = entry["outliers"]
            assert isinstance(outliers, list)
            assert all(isinstance(i, int) for i in outliers)

        union = result["union_outliers"]
        assert isinstance(union, list)
        assert all(isinstance(i, int) for i in union)

    def test_seqtransform_bad_transform(self):
        """Invalid transform token raises ValueError naming the offending token."""
        rng = np.random.default_rng(3)
        data = rng.standard_normal((15, 30))
        with pytest.raises(ValueError, match="nope"):
            outl.sequential_transform_outliers(data, transforms=["t0", "nope"])

    def test_seqtransform_depth_method(self):
        """depth_method reuses the depth dispatcher; default and new token both work."""
        rng = np.random.default_rng(3)
        data = rng.standard_normal((15, 30))
        data[0, :] += 10

        result_default = outl.sequential_transform_outliers(
            data, transforms=["t0"], depth_method="modified_band"
        )
        assert set(result_default.keys()) == {"per_transform_outliers", "union_outliers"}

        result_tv = outl.sequential_transform_outliers(
            data, transforms=["t0"], depth_method="total_variation"
        )
        assert set(result_tv.keys()) == {"per_transform_outliers", "union_outliers"}
