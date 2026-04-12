"""Tests for the Fdata class."""

import numpy as np
import pandas as pd
import pytest


class TestFdataConstruction:
    def test_1d_basic(self):
        from pyfda import Fdata

        t = np.linspace(0, 1, 50)
        X = np.random.randn(10, 50)
        fd = Fdata(X, argvals=t)

        assert fd.n_obs == 10
        assert fd.n_points == 50
        assert fd.fdata2d is False
        assert fd.rangeval == (0.0, 1.0)
        assert len(fd.id) == 10
        assert fd.id[0] == "obs_1"
        assert fd.metadata is None

    def test_1d_default_argvals(self):
        from pyfda import Fdata

        fd = Fdata(np.random.randn(5, 20))
        np.testing.assert_array_equal(fd.argvals, np.arange(20, dtype=np.float64))

    def test_1d_single_curve(self):
        from pyfda import Fdata

        fd = Fdata(np.array([1.0, 2.0, 3.0]))
        assert fd.n_obs == 1
        assert fd.n_points == 3

    def test_1d_with_ids(self):
        from pyfda import Fdata

        fd = Fdata(np.random.randn(3, 10), id=["a", "b", "c"])
        assert fd.id == ["a", "b", "c"]

    def test_1d_id_length_mismatch(self):
        from pyfda import Fdata

        with pytest.raises(ValueError, match="id must have length"):
            Fdata(np.random.randn(3, 10), id=["a", "b"])

    def test_1d_argvals_length_mismatch(self):
        from pyfda import Fdata

        with pytest.raises(ValueError, match="Length of argvals"):
            Fdata(np.random.randn(3, 10), argvals=np.linspace(0, 1, 5))

    def test_2d_from_3d_array(self):
        from pyfda import Fdata

        surfaces = np.random.randn(5, 8, 10)
        fd = Fdata(surfaces)

        assert fd.fdata2d is True
        assert fd.n_obs == 5
        assert fd.n_points == 80
        assert fd.dims == (8, 10)

    def test_2d_from_tuple_argvals(self):
        from pyfda import Fdata

        s = np.linspace(0, 1, 8)
        t = np.linspace(0, 2, 10)
        fd = Fdata(np.random.randn(5, 80), argvals=(s, t))

        assert fd.fdata2d is True
        assert fd.dims == (8, 10)
        assert fd.rangeval == ((0.0, 1.0), (0.0, 2.0))

    def test_2d_grid_mismatch(self):
        from pyfda import Fdata

        s = np.linspace(0, 1, 5)
        t = np.linspace(0, 1, 5)
        with pytest.raises(ValueError, match="does not match"):
            Fdata(np.random.randn(3, 30), argvals=(s, t))


class TestFdataMetadata:
    def test_dict_metadata_converted_to_dataframe(self):
        from pyfda import Fdata

        meta = {"group": ["A", "B", "A"], "value": [1.0, 2.0, 3.0]}
        fd = Fdata(np.random.randn(3, 10), metadata=meta)
        assert isinstance(fd.metadata, pd.DataFrame)
        assert list(fd.metadata.columns) == ["group", "value"]
        assert len(fd.metadata) == 3

    def test_dataframe_metadata(self):
        from pyfda import Fdata

        meta = pd.DataFrame({"group": ["A", "B", "C"], "value": [1, 2, 3]})
        fd = Fdata(np.random.randn(3, 10), metadata=meta)
        assert isinstance(fd.metadata, pd.DataFrame)
        assert list(fd.metadata.columns) == ["group", "value"]

    def test_metadata_row_mismatch(self):
        from pyfda import Fdata

        meta = pd.DataFrame({"x": [1, 2]})
        with pytest.raises(ValueError, match="must have 3 rows"):
            Fdata(np.random.randn(3, 10), metadata=meta)

    def test_metadata_column_access(self):
        from pyfda import Fdata

        meta = pd.DataFrame({"group": ["A", "B"], "score": [1.5, 2.5]})
        fd = Fdata(np.random.randn(2, 10), metadata=meta)
        assert fd.metadata["score"].sum() == 4.0
        assert list(fd.metadata["group"]) == ["A", "B"]


class TestFdataRepr:
    def test_repr_1d(self):
        from pyfda import Fdata

        fd = Fdata(np.random.randn(10, 50), argvals=np.linspace(0, 1, 50))
        r = repr(fd)
        assert "1D" in r
        assert "10 obs" in r
        assert "50 points" in r

    def test_repr_2d(self):
        from pyfda import Fdata

        fd = Fdata(np.random.randn(5, 8, 10))
        r = repr(fd)
        assert "2D" in r
        assert "5 obs" in r
        assert "8" in r and "10" in r

    def test_repr_with_metadata(self):
        from pyfda import Fdata

        meta = pd.DataFrame({"group": ["A", "B"], "score": [1.0, 2.0]})
        fd = Fdata(np.random.randn(2, 10), metadata=meta)
        r = repr(fd)
        assert "metadata" in r
        assert "group" in r


class TestFdataSubsetting:
    def setup_method(self):
        from pyfda import Fdata

        np.random.seed(42)
        self.t = np.linspace(0, 1, 50)
        meta = pd.DataFrame({
            "group": list("AABBBCCCDD"),
            "val": list(range(10)),
        })
        self.fd = Fdata(
            np.random.randn(10, 50),
            argvals=self.t,
            id=[f"p_{i}" for i in range(10)],
            metadata=meta,
        )

    def test_slice(self):
        sub = self.fd[0:3]
        assert sub.n_obs == 3
        assert sub.id == ["p_0", "p_1", "p_2"]
        assert isinstance(sub.metadata, pd.DataFrame)
        assert list(sub.metadata["group"]) == ["A", "A", "B"]

    def test_list_index(self):
        sub = self.fd[[0, 5, 9]]
        assert sub.n_obs == 3
        assert sub.id == ["p_0", "p_5", "p_9"]
        assert isinstance(sub.metadata, pd.DataFrame)

    def test_column_subset(self):
        sub = self.fd[0:3, 10:20]
        assert sub.n_obs == 3
        assert sub.n_points == 10
        np.testing.assert_array_equal(sub.argvals, self.t[10:20])

    def test_len(self):
        assert len(self.fd) == 10

    def test_subset_metadata_reset_index(self):
        sub = self.fd[5:8]
        assert list(sub.metadata.index) == [0, 1, 2]


class TestFdataArithmetic:
    def setup_method(self):
        from pyfda import Fdata

        self.fd1 = Fdata(np.ones((5, 10)))
        self.fd2 = Fdata(np.full((5, 10), 2.0))

    def test_add_fdata(self):
        result = self.fd1 + self.fd2
        np.testing.assert_allclose(result.data, 3.0)

    def test_sub_fdata(self):
        result = self.fd2 - self.fd1
        np.testing.assert_allclose(result.data, 1.0)

    def test_mul_scalar(self):
        result = self.fd1 * 3.0
        np.testing.assert_allclose(result.data, 3.0)

    def test_rmul_scalar(self):
        result = 2.0 * self.fd1
        np.testing.assert_allclose(result.data, 2.0)

    def test_div_scalar(self):
        result = self.fd2 / 2.0
        np.testing.assert_allclose(result.data, 1.0)

    def test_shape_mismatch(self):
        from pyfda import Fdata

        other = Fdata(np.ones((5, 20)))
        with pytest.raises(ValueError, match="dimensions must match"):
            self.fd1 + other


class TestFdataOperations:
    def setup_method(self):
        from pyfda import Fdata

        np.random.seed(42)
        self.t = np.linspace(0, 1, 50)
        self.fd = Fdata(np.random.randn(15, 50), argvals=self.t)

    def test_mean(self):
        mu = self.fd.mean()
        assert mu.shape == (50,)

    def test_center(self):
        centered = self.fd.center()
        assert isinstance(centered, type(self.fd))
        assert centered.shape == self.fd.shape
        col_means = centered.data.mean(axis=0)
        np.testing.assert_allclose(col_means, 0.0, atol=1e-10)

    def test_deriv(self):
        d = self.fd.deriv(nderiv=1)
        assert isinstance(d, type(self.fd))
        assert d.shape == self.fd.shape

    def test_norm(self):
        norms = self.fd.norm(p=2.0)
        assert norms.shape == (15,)
        assert all(n >= 0 for n in norms)

    def test_normalize(self):
        normed = self.fd.normalize("center")
        assert normed.shape == self.fd.shape

    def test_geometric_median(self):
        med = self.fd.geometric_median()
        assert med.shape == (50,)

    def test_depth(self):
        depths = self.fd.depth(method="fraiman_muniz")
        assert depths.shape == (15,)

    def test_distance(self):
        D = self.fd.distance(method="lp", p=2.0)
        assert D.shape == (15, 15)
        np.testing.assert_allclose(np.diag(D), 0.0, atol=1e-10)

    def test_copy(self):
        fd2 = self.fd.copy()
        fd2.data[0, 0] = 999.0
        assert self.fd.data[0, 0] != 999.0


class TestFdataMetadataPreserved:
    def test_center_preserves_metadata(self):
        from pyfda import Fdata

        meta = pd.DataFrame({"group": ["A", "B", "C"]})
        fd = Fdata(np.random.randn(3, 10), metadata=meta)
        centered = fd.center()
        assert isinstance(centered.metadata, pd.DataFrame)
        assert centered.id == fd.id

    def test_normalize_preserves_metadata(self):
        from pyfda import Fdata

        meta = pd.DataFrame({"group": ["A", "B", "C"]})
        fd = Fdata(np.random.randn(3, 10), metadata=meta)
        normed = fd.normalize("autoscale")
        assert isinstance(normed.metadata, pd.DataFrame)

    def test_subset_preserves_metadata(self):
        from pyfda import Fdata

        meta = pd.DataFrame({"group": ["A", "B", "C"], "val": [1, 2, 3]})
        fd = Fdata(np.random.randn(3, 10), metadata=meta)
        sub = fd[0:2]
        assert isinstance(sub.metadata, pd.DataFrame)
        assert list(sub.metadata["group"]) == ["A", "B"]
        assert list(sub.metadata["val"]) == [1, 2]
