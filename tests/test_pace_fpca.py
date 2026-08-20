"""Tests for fdars.pace_fpca: PyIrregFdata #[pyclass] handle, irreg_fdata_from_lists,
and pace_fpca bindings (PACE-01 + PACE-02).

Task 1: end-to-end tracer (TestIrregFdataRoundTrip)
Task 2: validation guards (TestIrregFdataValidation)
Task 3: full 10-key converter + transposition guards + determinism (TestPaceFpcaResult)
Task 5: import-path coverage (TestPaceImportPaths)
"""

import numpy as np
import pytest

import fdars.pace_fpca as pf


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

def _make_ragged_data(n=6, seed=42):
    """Return (argvals_list, values_list) with n ragged curves on [0,1]."""
    rng = np.random.default_rng(seed)
    argvals_list = []
    values_list = []
    for i in range(n):
        # Each curve has between 3 and 5 observation points
        n_pts = 3 + (i % 3)
        t = np.sort(rng.uniform(0.0, 1.0, n_pts))
        v = (i + 1) * np.sin(t * np.pi) + rng.normal(0, 0.05, n_pts)
        argvals_list.append(t)
        values_list.append(v)
    return argvals_list, values_list


# ---------------------------------------------------------------------------
# Task 1: End-to-end tracer — prove the #[pyclass] handle round-trip
# ---------------------------------------------------------------------------

class TestIrregFdataRoundTrip:
    """Prove the IrregFdata #[pyclass] handle + pace_fpca round-trip works."""

    def test_irreg_round_trip(self):
        """Build a PyIrregFdata handle from ragged lists and run pace_fpca end-to-end."""
        argvals_list, values_list = _make_ragged_data(n=6)

        # Build the opaque handle
        fd = pf.irreg_fdata_from_lists(argvals_list, values_list)

        # Handle is the correct type
        assert isinstance(fd, pf.PyIrregFdata), (
            f"Expected pf.PyIrregFdata, got {type(fd)}"
        )

        # Call pace_fpca — bandwidth >= 0.15 (Pitfall 6: too-narrow bandwidth -> NaN mean)
        result = pf.pace_fpca(fd, ncomp=2, bandwidth=0.2, sigma2=0.01, alpha=0.05)

        # Returns a dict
        assert isinstance(result, dict), f"Expected dict, got {type(result)}"

        # eigenfunctions and scores are 2-D numpy arrays
        ef = result["eigenfunctions"]
        sc = result["scores"]
        assert ef.ndim == 2, f"eigenfunctions should be 2-D, got shape {ef.shape}"
        assert sc.ndim == 2, f"scores should be 2-D, got shape {sc.shape}"


# ---------------------------------------------------------------------------
# Task 2: Validation guards
# ---------------------------------------------------------------------------

class TestIrregFdataValidation:
    """Validation guards for irreg_fdata_from_lists (PACE-01 guards)."""

    def test_dense_array_rejection(self):
        """A dense 2-D numpy array must be rejected with ValueError, not silently accepted."""
        data_2d = np.zeros((5, 10))
        with pytest.raises(ValueError, match="2-D"):
            pf.irreg_fdata_from_lists(data_2d, data_2d)

    def test_ragged_mismatch(self):
        """Per-curve length mismatch raises ValueError BEFORE IrregFdata::from_lists (no PanicException)."""
        argvals_list = [np.array([0.1, 0.5, 0.9]), np.array([0.2, 0.8])]
        # Curve 0: argvals has 3 points, values has 4 — mismatch
        values_list = [np.array([1.0, 2.0, 3.0, 4.0]), np.array([5.0, 6.0])]
        with pytest.raises(ValueError):
            pf.irreg_fdata_from_lists(argvals_list, values_list)

    def test_outer_length_mismatch(self):
        """Outer-length mismatch (3 argvals curves vs 2 values curves) raises ValueError."""
        argvals_list = [np.array([0.1, 0.5]), np.array([0.2, 0.8]), np.array([0.3, 0.7])]
        values_list = [np.array([1.0, 2.0]), np.array([3.0, 4.0])]
        with pytest.raises(ValueError):
            pf.irreg_fdata_from_lists(argvals_list, values_list)


# ---------------------------------------------------------------------------
# Task 3: Full 10-key converter + transposition guards + truncation + determinism
# ---------------------------------------------------------------------------

# Use n=6, m=21 (via work_grid), ncomp=2 so n != m != ncomp → transposition-guarded
_N = 6
_M = 21
_NCOMP_REQUEST = 2
_WORK_GRID = np.linspace(0.0, 1.0, _M)
_BW = 0.2  # bandwidth >= 0.15 to avoid NaN-mean (Pitfall 6)


class TestPaceFpcaResult:
    """Full 10-key dict, transposition guards, ncomp truncation, determinism."""

    @pytest.fixture(scope="class")
    def result(self):
        av, vl = _make_ragged_data(n=_N, seed=7)
        fd = pf.irreg_fdata_from_lists(av, vl)
        return pf.pace_fpca(
            fd,
            ncomp=_NCOMP_REQUEST,
            bandwidth=_BW,
            sigma2=0.01,
            work_grid=_WORK_GRID.tolist(),
            alpha=0.05,
        )

    def test_pace_result_keys(self, result):
        """Dict must have exactly the 10 expected keys."""
        expected = {
            "mean", "eigenvalues", "eigenfunctions", "scores",
            "fitted", "fitted_lower", "fitted_upper",
            "argvals", "sigma2", "ncomp",
        }
        assert set(result.keys()) == expected, (
            f"Key mismatch: got {set(result.keys())}"
        )

    def test_eigenfunctions_transposition_guard(self, result):
        """eigenfunctions.shape must be (m, ncomp), NOT (ncomp, m)."""
        k = result["ncomp"]
        ef = result["eigenfunctions"]
        assert ef.shape == (_M, k), (
            f"eigenfunctions shape: expected ({_M}, {k}), got {ef.shape}"
        )
        # Eigenfunctions must be 2-D float arrays (shape is the critical guard)
        assert ef.dtype.kind == "f", f"eigenfunctions must be float, got {ef.dtype}"

    def test_scores_transposition_guard(self, result):
        """scores.shape must be (n, ncomp), with n != m != ncomp."""
        k = result["ncomp"]
        sc = result["scores"]
        assert sc.shape == (_N, k), (
            f"scores shape: expected ({_N}, {k}), got {sc.shape}"
        )
        # Confirm n != m != ncomp so a transpose cannot accidentally pass
        assert _N != _M and _M != k, (
            f"Fixture must have n != m != ncomp but got n={_N}, m={_M}, k={k}"
        )

    def test_fitted_shapes(self, result):
        """fitted, fitted_lower, fitted_upper must each be (n, m); mean/argvals length m."""
        for key in ("fitted", "fitted_lower", "fitted_upper"):
            arr = result[key]
            assert arr.shape == (_N, _M), (
                f"{key} shape: expected ({_N}, {_M}), got {arr.shape}"
            )
        assert result["mean"].shape == (_M,), f"mean shape: {result['mean'].shape}"
        assert result["argvals"].shape == (_M,), f"argvals shape: {result['argvals'].shape}"

    def test_ncomp_truncation(self):
        """Requesting more components than available should not raise; ncomp echoes actual count."""
        av, vl = _make_ragged_data(n=_N, seed=7)
        fd = pf.irreg_fdata_from_lists(av, vl)
        r = pf.pace_fpca(
            fd, ncomp=10, bandwidth=_BW, sigma2=0.01,
            work_grid=_WORK_GRID.tolist(), alpha=0.05
        )
        actual = r["ncomp"]
        assert actual <= 10, f"ncomp should be <= 10, got {actual}"
        # Shapes must agree with actual ncomp, not requested 10
        assert r["eigenvalues"].shape == (actual,)
        assert r["eigenfunctions"].shape == (_M, actual)
        assert r["scores"].shape == (_N, actual)

    def test_pace_determinism(self):
        """Two identical calls must return byte-identical eigenfunctions, scores, fitted."""
        av, vl = _make_ragged_data(n=_N, seed=7)
        fd = pf.irreg_fdata_from_lists(av, vl)
        kwargs = dict(ncomp=_NCOMP_REQUEST, bandwidth=_BW, sigma2=0.01,
                      work_grid=_WORK_GRID.tolist(), alpha=0.05)
        r1 = pf.pace_fpca(fd, **kwargs)
        r2 = pf.pace_fpca(fd, **kwargs)
        for key in ("eigenfunctions", "scores", "fitted"):
            assert np.array_equal(r1[key], r2[key]), (
                f"Determinism failed for key '{key}'"
            )

    def test_sigma2_echo(self):
        """sigma2 in the result dict must equal the value passed in."""
        av, vl = _make_ragged_data(n=_N, seed=7)
        fd = pf.irreg_fdata_from_lists(av, vl)
        r = pf.pace_fpca(
            fd, ncomp=_NCOMP_REQUEST, bandwidth=_BW, sigma2=0.02,
            work_grid=_WORK_GRID.tolist(), alpha=0.05
        )
        assert isinstance(r["sigma2"], float), f"sigma2 must be a Python float, got {type(r['sigma2'])}"
        assert r["sigma2"] == 0.02, f"sigma2 echo failed: expected 0.02, got {r['sigma2']}"


# ---------------------------------------------------------------------------
# Task 5: Import-path coverage
# ---------------------------------------------------------------------------

class TestPaceImportPaths:
    """Both import path patterns must resolve for pace_fpca submodule symbols."""

    def test_submodule_attribute_access(self):
        """Attribute access via fdars.pace_fpca resolves to callables / the class."""
        import fdars
        assert callable(fdars.pace_fpca.irreg_fdata_from_lists)
        assert callable(fdars.pace_fpca.pace_fpca)
        assert isinstance(fdars.pace_fpca.PyIrregFdata, type)

    def test_from_import(self):
        """from fdars.pace_fpca import ... resolves all three symbols."""
        from fdars.pace_fpca import (  # noqa: F401
            irreg_fdata_from_lists,
            pace_fpca,
            PyIrregFdata,
        )
        assert callable(irreg_fdata_from_lists)
        assert callable(pace_fpca)
        assert isinstance(PyIrregFdata, type)
