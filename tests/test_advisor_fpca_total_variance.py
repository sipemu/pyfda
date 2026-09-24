"""FPCA diagnostics must report shares of TOTAL variance, not of retained variance.

Regression test: the cumulative share used to be normalised by the retained
eigenvalues only, so its last element was always 1.0 regardless of n_comp.
"""
import numpy as np

from fdars import Fdata, datasets
from fdars.advisor import build_diagnostics


def _diag(k):
    ds = datasets.load_growth()
    fd = Fdata(np.asarray(ds.data.data), argvals=np.asarray(ds.data.argvals))
    return build_diagnostics(fd.to_pc(n_comp=k), "fpca")


def test_cumulative_share_is_below_one_and_grows_with_components():
    small, large = _diag(2), _diag(4)
    assert small["variance_denominator"] == "total"
    assert small["cumulative_variance_explained"][-1] < large["cumulative_variance_explained"][-1] < 1.0


def test_shares_are_consistent_across_n_comp():
    small, large = _diag(2), _diag(4)
    np.testing.assert_allclose(small["explained_variance_ratio"],
                               large["explained_variance_ratio"][:2], rtol=1e-8)


def test_fallback_without_centered_data_is_labelled():
    d = build_diagnostics({"singular_values": [3.0, 2.0], "scores": np.zeros((10, 2))}, "fpca")
    assert d["variance_denominator"] == "retained_components"
    assert abs(d["cumulative_variance_explained"][-1] - 1.0) < 1e-12
