"""Tests for Phase 27-02: shift registration, quality scores, banded elastic alignment."""

from __future__ import annotations

import numpy as np
import pytest

import fdars


# ─── Fixtures ─────────────────────────────────────────────────────────────────

def uniform_grid(n: int) -> np.ndarray:
    """Uniform grid on [0, 1] with n points."""
    return np.linspace(0.0, 1.0, n)


def gaussian_bump(argvals: np.ndarray, mu: float, sigma: float) -> np.ndarray:
    """Gaussian bump centred at mu with standard deviation sigma."""
    return np.exp(-((argvals - mu) ** 2) / (2.0 * sigma ** 2))


def make_distinct_curves(n: int = 3, m: int = 50) -> tuple[np.ndarray, np.ndarray]:
    """Build n DISTINCT-shaped curves (sin(k*pi*t) for k=1..n) on a uniform grid."""
    av = uniform_grid(m)
    data = np.array([np.sin((k + 1) * np.pi * av) for k in range(n)])
    return data, av


def make_registered_bumps(n: int = 5, m: int = 101) -> tuple[np.ndarray, np.ndarray]:
    """Build n shifted Gaussian bumps and return the registered version + argvals."""
    av = uniform_grid(m)
    centres = np.linspace(0.35, 0.65, n)
    data = np.array([gaussian_bump(av, mu, 0.08) for mu in centres])
    result = fdars.alignment.least_squares_shift_registration(data, av, max_shift=0.25)
    return result["registered_data"], av


# ─── Task 1: least_squares_shift_registration ─────────────────────────────────

class TestLeastSquaresShiftRegistration:
    """Dict-shape tests and identity-shift assertion for least_squares_shift_registration."""

    def test_dict_keys(self):
        """Result dict has exactly 'registered_data' and 'shifts' keys."""
        n, m = 3, 20
        data = np.ones((n, m))
        av = uniform_grid(m)
        result = fdars.alignment.least_squares_shift_registration(data, av, max_shift=0.2)
        assert sorted(result.keys()) == ["registered_data", "shifts"]

    def test_registered_data_shape(self):
        """registered_data has shape (n, m)."""
        n, m = 4, 30
        data = np.random.default_rng(42).standard_normal((n, m))
        av = uniform_grid(m)
        result = fdars.alignment.least_squares_shift_registration(data, av, max_shift=0.25)
        assert result["registered_data"].shape == (n, m)

    def test_shifts_shape_and_dtype(self):
        """shifts has shape (n,) and dtype float64."""
        n, m = 5, 25
        data = np.ones((n, m))
        av = uniform_grid(m)
        result = fdars.alignment.least_squares_shift_registration(data, av, max_shift=0.2)
        assert result["shifts"].shape == (n,)
        assert result["shifts"].dtype == np.float64

    def test_identity_shift_identical_curves(self):
        """Already-aligned identical curves produce shifts ≈ 0."""
        m = 51
        av = uniform_grid(m)
        bump = gaussian_bump(av, 0.5, 0.08)
        data = np.tile(bump, (4, 1))  # 4 identical rows
        result = fdars.alignment.least_squares_shift_registration(data, av, max_shift=0.25)
        np.testing.assert_allclose(result["shifts"], 0.0, atol=1e-6,
                                   err_msg="identical curves should have shifts ≈ 0")

    def test_identity_shift_single_curve(self):
        """A single curve repeated gives shifts ≈ 0 (unimodal convergence)."""
        m = 40
        av = uniform_grid(m)
        curve = np.sin(2 * np.pi * av)
        data = np.tile(curve, (3, 1))
        result = fdars.alignment.least_squares_shift_registration(data, av, max_shift=0.2)
        np.testing.assert_allclose(result["shifts"], 0.0, atol=1e-5)

    def test_error_on_zero_max_shift(self):
        """max_shift = 0 raises ValueError."""
        data = np.ones((3, 20))
        av = uniform_grid(20)
        with pytest.raises(ValueError):
            fdars.alignment.least_squares_shift_registration(data, av, max_shift=0.0)

    def test_error_on_negative_max_shift(self):
        """Negative max_shift raises ValueError."""
        data = np.ones((3, 20))
        av = uniform_grid(20)
        with pytest.raises(ValueError):
            fdars.alignment.least_squares_shift_registration(data, av, max_shift=-0.1)

    def test_error_on_argvals_mismatch(self):
        """Argvals length != m raises ValueError."""
        data = np.ones((3, 20))
        av_wrong = uniform_grid(15)
        with pytest.raises(ValueError):
            fdars.alignment.least_squares_shift_registration(data, av_wrong, max_shift=0.2)


# ─── Task 2: Quality scores + fd.shift_register() ────────────────────────────

class TestRegistrationQualityScores:
    """Tests for least_squares_score, pairwise_correlation_score, sobolev_least_squares_score."""

    @pytest.fixture(autouse=True)
    def _setup(self):
        """Registered bumps shared across all quality score tests."""
        self.reg, self.av = make_registered_bumps(n=5, m=101)

    def test_least_squares_score_returns_finite_nonneg(self):
        """least_squares_score returns a finite non-negative float."""
        score = fdars.alignment.least_squares_score(self.reg, self.av)
        assert np.isfinite(score), f"expected finite score, got {score}"
        assert score >= 0.0, f"expected non-negative score, got {score}"

    def test_pairwise_correlation_score_returns_finite_in_range(self):
        """pairwise_correlation_score returns a finite float in [-1, 1]."""
        score = fdars.alignment.pairwise_correlation_score(self.reg, self.av)
        assert np.isfinite(score), f"expected finite score, got {score}"
        assert -1.0 <= score <= 1.0 + 1e-10, f"expected score in [-1, 1], got {score}"

    def test_pairwise_correlation_high_for_similar_curves(self):
        """pairwise_correlation_score ≈ 1 for near-identical registered curves."""
        m = 51
        av = uniform_grid(m)
        # All curves nearly identical (tiny noise)
        base = np.sin(2 * np.pi * av)
        data = np.array([base + 1e-10 * i for i in range(5)])
        score = fdars.alignment.pairwise_correlation_score(data, av)
        assert score > 0.999, f"near-identical curves should have high pairwise correlation, got {score}"

    def test_sobolev_score_returns_finite_nonneg(self):
        """sobolev_least_squares_score returns a finite non-negative float."""
        score = fdars.alignment.sobolev_least_squares_score(self.reg, self.av, lambda_=1.0)
        assert np.isfinite(score), f"expected finite score, got {score}"
        assert score >= 0.0, f"expected non-negative score, got {score}"

    def test_sobolev_lambda_zero_equals_least_squares(self):
        """sobolev_least_squares_score(lambda=0) equals least_squares_score."""
        ls = fdars.alignment.least_squares_score(self.reg, self.av)
        sobol = fdars.alignment.sobolev_least_squares_score(self.reg, self.av, lambda_=0.0)
        np.testing.assert_allclose(sobol, ls, rtol=1e-10,
                                   err_msg="sobolev(lambda=0) must equal least_squares_score")

    def test_sobolev_nonuniform_grid_raises_value_error(self):
        """sobolev_least_squares_score with lambda>0 on non-uniform grid raises ValueError."""
        m = 30
        # Construct a deliberately non-uniform grid (quadratic spacing)
        t = np.linspace(0, 1, m) ** 2
        data = np.array([np.sin(2 * np.pi * t) for _ in range(4)])
        with pytest.raises(ValueError, match="(?i)uniform"):
            fdars.alignment.sobolev_least_squares_score(data, t, lambda_=1.0)

    def test_least_squares_score_drops_after_registration(self):
        """LS score decreases after shift registration."""
        m = 101
        av = uniform_grid(m)
        centres = np.linspace(0.3, 0.7, 5)
        data = np.array([gaussian_bump(av, mu, 0.08) for mu in centres])
        result = fdars.alignment.least_squares_shift_registration(data, av, max_shift=0.25)
        score_before = fdars.alignment.least_squares_score(data, av)
        score_after = fdars.alignment.least_squares_score(result["registered_data"], av)
        assert score_after < score_before, (
            f"LS score should drop after registration: before={score_before:.6f}, after={score_after:.6f}"
        )

    def test_pairwise_correlation_error_n1(self):
        """pairwise_correlation_score raises ValueError for n=1."""
        m = 30
        av = uniform_grid(m)
        data = np.ones((1, m))
        with pytest.raises(ValueError):
            fdars.alignment.pairwise_correlation_score(data, av)


class TestShiftRegisterFdataMethod:
    """Tests for fd.shift_register() Fdata method."""

    def _make_fd(self, n: int = 5, m: int = 51) -> "fdars.Fdata":
        """Build an Fdata object with n shifted Gaussian bumps."""
        av = uniform_grid(m)
        centres = np.linspace(0.35, 0.65, n)
        data = np.array([gaussian_bump(av, mu, 0.08) for mu in centres])
        return fdars.Fdata(
            data=data,
            argvals=av,
            rangeval=(0.0, 1.0),
        )

    def test_returns_two_tuple(self):
        """fd.shift_register() returns a 2-tuple."""
        fd = self._make_fd()
        result = fd.shift_register(max_shift=0.25)
        assert isinstance(result, tuple) and len(result) == 2

    def test_registered_is_fdata(self):
        """First element of the tuple is an Fdata object."""
        fd = self._make_fd()
        registered, shifts = fd.shift_register(max_shift=0.25)
        assert isinstance(registered, fdars.Fdata)

    def test_registered_n_obs_preserved(self):
        """Registered Fdata has same n_obs as self."""
        n = 5
        fd = self._make_fd(n=n)
        registered, shifts = fd.shift_register(max_shift=0.25)
        assert registered.n_obs == n

    def test_registered_argvals_unchanged(self):
        """Registered Fdata has the same argvals as self."""
        fd = self._make_fd()
        registered, shifts = fd.shift_register(max_shift=0.25)
        np.testing.assert_array_equal(registered.argvals, fd.argvals)

    def test_shifts_shape(self):
        """Shifts array has shape (n_obs,)."""
        n = 5
        fd = self._make_fd(n=n)
        registered, shifts = fd.shift_register(max_shift=0.25)
        assert shifts.shape == (n,), f"expected shifts shape ({n},), got {shifts.shape}"

    def test_shifts_dtype_float64(self):
        """Shifts array has dtype float64."""
        fd = self._make_fd()
        registered, shifts = fd.shift_register(max_shift=0.25)
        assert shifts.dtype == np.float64


# ─── Task 3: Banded *_with_band functions ────────────────────────────────────

class TestKarcherMeanWithBand:
    """Tests for karcher_mean_with_band."""

    def test_returns_dict_with_correct_keys(self):
        """karcher_mean_with_band returns a dict with the same 6 keys as karcher_mean."""
        data, av = make_distinct_curves(n=3, m=30)
        result = fdars.alignment.karcher_mean_with_band(data, av)
        expected_keys = {"mean", "mean_srsf", "aligned_data", "gammas", "n_iter", "converged"}
        assert set(result.keys()) == expected_keys

    def test_band_frac_none_matches_unbanded(self):
        """karcher_mean_with_band(band_frac=None) mean ≈ karcher_mean mean."""
        data, av = make_distinct_curves(n=3, m=30)
        r_banded = fdars.alignment.karcher_mean_with_band(data, av, band_frac=None)
        r_unbanded = fdars.alignment.karcher_mean(data, av)
        np.testing.assert_allclose(
            r_banded["mean"], r_unbanded["mean"], rtol=1e-6, atol=1e-8,
            err_msg="band_frac=None should match unbanded karcher_mean"
        )

    def test_aligned_data_shape(self):
        """aligned_data has shape (n, m)."""
        n, m = 4, 25
        data, av = make_distinct_curves(n=n, m=m)
        result = fdars.alignment.karcher_mean_with_band(data, av)
        assert result["aligned_data"].shape == (n, m)

    def test_with_band_frac_returns_valid_result(self):
        """karcher_mean_with_band with a real band_frac returns valid mean."""
        data, av = make_distinct_curves(n=3, m=30)
        result = fdars.alignment.karcher_mean_with_band(data, av, band_frac=0.3)
        assert result["mean"].shape == (30,)
        assert np.all(np.isfinite(result["mean"]))


class TestElasticSelfDistanceMatrixWithBand:
    """Tests for elastic_self_distance_matrix_with_band."""

    def test_shape_n_n(self):
        """Returns (n, n) matrix."""
        n, m = 4, 30
        data, av = make_distinct_curves(n=n, m=m)
        D = fdars.alignment.elastic_self_distance_matrix_with_band(data, av)
        assert D.shape == (n, n)

    def test_zero_diagonal(self):
        """Diagonal entries are zero (or very close to zero)."""
        data, av = make_distinct_curves(n=4, m=30)
        D = fdars.alignment.elastic_self_distance_matrix_with_band(data, av)
        np.testing.assert_allclose(np.diag(D), 0.0, atol=1e-8,
                                   err_msg="self-distance matrix diagonal must be ~0")

    def test_symmetric(self):
        """Distance matrix is symmetric."""
        data, av = make_distinct_curves(n=4, m=30)
        D = fdars.alignment.elastic_self_distance_matrix_with_band(data, av)
        np.testing.assert_allclose(D, D.T, atol=1e-10,
                                   err_msg="self-distance matrix must be symmetric")

    def test_band_frac_none_matches_unbanded(self):
        """elastic_self_distance_matrix_with_band(band_frac=None) ≈ elastic_self_distance_matrix."""
        data, av = make_distinct_curves(n=3, m=25)
        D_banded = fdars.alignment.elastic_self_distance_matrix_with_band(data, av, band_frac=None)
        D_unbanded = fdars.alignment.elastic_self_distance_matrix(data, av)
        np.testing.assert_allclose(D_banded, D_unbanded, rtol=1e-6, atol=1e-8,
                                   err_msg="band_frac=None should match unbanded distance matrix")

    def test_multicurve_transposition_round_trip(self):
        """Multi-curve transposition guard: off-diagonal d[0,2] matches independent pairwise computation.

        This test detects transposition bugs (#33 class): if the row/column ordering
        is scrambled, at least one off-diagonal entry will differ from the
        independently computed pairwise distance.
        """
        n, m = 3, 40
        av = uniform_grid(m)
        # 3 DISTINCT curves: sin(k*pi*t) for k=1,2,3 — very different shapes
        curves = np.array([np.sin((k + 1) * np.pi * av) for k in range(n)])

        D = fdars.alignment.elastic_self_distance_matrix_with_band(curves, av)

        # Compute d(curve_0, curve_2) independently using the unbanded function
        two_curves = curves[[0, 2], :]
        D_pair = fdars.alignment.elastic_self_distance_matrix(two_curves, av)
        # D_pair[0,1] == d(curve_0, curve_2)
        expected_d02 = D_pair[0, 1]

        np.testing.assert_allclose(
            D[0, 2], expected_d02, rtol=1e-6, atol=1e-8,
            err_msg=(
                f"D[0,2]={D[0,2]:.6f} should equal independently computed "
                f"d(curve_0, curve_2)={expected_d02:.6f} — transposition bug detected?"
            ),
        )
        # Also check D[2,0] == D[0,2] (symmetry check for completeness)
        np.testing.assert_allclose(D[2, 0], D[0, 2], atol=1e-10)

    def test_all_nonneg(self):
        """All distance matrix entries are non-negative."""
        data, av = make_distinct_curves(n=4, m=30)
        D = fdars.alignment.elastic_self_distance_matrix_with_band(data, av)
        assert np.all(D >= -1e-10), "all distances must be non-negative"


class TestElasticCrossDistanceMatrixWithBand:
    """Tests for elastic_cross_distance_matrix_with_band."""

    def test_shape_n1_n2(self):
        """Returns (n1, n2) matrix."""
        n1, n2, m = 3, 4, 30
        data1, av = make_distinct_curves(n=n1, m=m)
        data2, _ = make_distinct_curves(n=n2, m=m)
        # Make data2 distinct from data1 by shifting
        data2 = data2 * 0.8 + 0.1
        D = fdars.alignment.elastic_cross_distance_matrix_with_band(data1, data2, av)
        assert D.shape == (n1, n2)

    def test_band_frac_none_matches_unbanded(self):
        """elastic_cross_distance_matrix_with_band(band_frac=None) ≈ elastic_cross_distance_matrix."""
        n1, n2, m = 3, 4, 25
        data1, av = make_distinct_curves(n=n1, m=m)
        data2 = np.array([np.cos((k + 1) * np.pi * av) for k in range(n2)])
        D_banded = fdars.alignment.elastic_cross_distance_matrix_with_band(
            data1, data2, av, band_frac=None
        )
        D_unbanded = fdars.alignment.elastic_cross_distance_matrix(data1, data2, av)
        np.testing.assert_allclose(D_banded, D_unbanded, rtol=1e-6, atol=1e-8,
                                   err_msg="band_frac=None should match unbanded cross-distance matrix")

    def test_all_nonneg(self):
        """All cross-distance entries are non-negative."""
        n1, n2, m = 3, 4, 30
        data1, av = make_distinct_curves(n=n1, m=m)
        data2 = np.array([np.cos((k + 1) * np.pi * av) for k in range(n2)])
        D = fdars.alignment.elastic_cross_distance_matrix_with_band(data1, data2, av)
        assert np.all(D >= -1e-10), "all cross-distances must be non-negative"

    def test_with_band_frac(self):
        """Cross-distance matrix with band_frac is valid shape and non-negative."""
        n1, n2, m = 3, 4, 30
        data1, av = make_distinct_curves(n=n1, m=m)
        data2 = np.array([np.cos((k + 1) * np.pi * av) for k in range(n2)])
        D = fdars.alignment.elastic_cross_distance_matrix_with_band(
            data1, data2, av, band_frac=0.3
        )
        assert D.shape == (n1, n2)
        assert np.all(D >= -1e-10)


# ─── Grep-gate: no _banded variants bound ────────────────────────────────────

def test_no_banded_variants_in_module():
    """Verify that the deprecated *_banded (not *_with_band) variants are NOT exposed."""
    import fdars.alignment as almod
    # These should NOT exist in the module namespace
    banded_names = [
        "karcher_mean_banded",
        "elastic_self_distance_matrix_banded",
        "elastic_cross_distance_matrix_banded",
    ]
    for name in banded_names:
        assert not hasattr(almod, name), (
            f"'{name}' should NOT be bound — bind _with_band variants, not _banded"
        )
