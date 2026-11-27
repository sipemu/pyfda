//! Functional-inference tests for `fdars.inference` submodule.
//!
//! Exposes two-sample permutation tests, an asymptotic Hotelling-T² mean
//! test, and simultaneous confidence band (SCB) inference from fdars-core 0.20:
//!
//! - [`t_perm_test`] — integrated L2 permutation test (mirrors R `fda::tperm.fd`).
//! - [`f_perm_test`] — integrated F permutation test (mirrors R `fda::Fperm.fd`).
//! - [`two_sample_mean_test`] — asymptotic Hotelling-T² on shared FPC basis.
//! - [`mean_scb`] — Degras simultaneous confidence band for the mean function.
//! - [`scb_two_sample_test`] — SCB-based two-sample mean-equality test.
//! - [`scb_two_sample_band`] — that band and the regions where it excludes zero.
//! - [`itp_pointwise_pvalues`] / [`itp_two_pop_regions`] — B-spline ITP
//!   p-values on the grid and the directed regions where two means differ.
//!
//! All fallible functions route errors through `to_pyresult()` — no `.unwrap()`
//! appears in this module. Degenerate inputs raise `ValueError` on the Python side.
//! `seed=None` resolves to fixed default `0` for [`t_perm_test`] and [`f_perm_test`],
//! giving byte-identical results across calls with the same inputs.
//! [`mean_scb`] and [`scb_two_sample_test`] accept no `seed` parameter; their
//! bootstrap randomness is internal to fdars-core and not externally seeded.

use crate::convert::*;
use numpy::{AllowTypeChange, PyArray1, PyArrayLike1, PyReadonlyArray1, PyReadonlyArray2};
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};

// ---------------------------------------------------------------------------
// Internal helper: map a fdars_core::inference::TestResult to a Python dict.
//
// The struct is #[non_exhaustive] — never struct-literal it; access each
// field individually.
// ---------------------------------------------------------------------------

fn test_result_to_pydict<'py>(
    py: Python<'py>,
    r: fdars_core::inference::TestResult,
) -> PyResult<Bound<'py, PyDict>> {
    let dict = PyDict::new(py);
    dict.set_item("statistic", r.statistic)?;
    dict.set_item("p_value", r.p_value)?;
    dict.set_item("n_perm", r.n_perm)?;
    Ok(dict)
}

// ---------------------------------------------------------------------------
// t_perm_test
// ---------------------------------------------------------------------------

/// Functional two-sample permutation *t*-test.
///
/// Tests the null hypothesis that ``data_a`` and ``data_b`` are drawn from
/// populations with the same mean curve. The test statistic is the integrated
/// L2 distance between the two sample-mean curves,
/// ``sqrt( ∫ (mean_a − mean_b)² dt )``, integrated with Simpson weights over
/// ``argvals``. The permutation null pools all ``n_a + n_b`` curves, relabels
/// group membership via a seeded Fisher–Yates shuffle, and recomputes the
/// statistic. P-value: ``(#{perm >= observed} + 1) / (n_perm + 1)``.
///
/// Parameters
/// ----------
/// data_a : numpy.ndarray
///     First sample, shape ``(n_a, m)``. Rows are observations.
/// data_b : numpy.ndarray
///     Second sample, shape ``(n_b, m)``. Must have the same column count as
///     ``data_a``.
/// argvals : numpy.ndarray
///     Evaluation points, length ``m``. Must match the column count.
/// n_perm : int, optional
///     Number of permutations (default 999). Must be >= 1.
/// seed : int or None, optional
///     RNG seed for deterministic results. ``None`` resolves to fixed default
///     ``0`` — two calls with ``seed=None`` and identical inputs are
///     byte-identical. Pass an explicit integer to override.
///
/// Returns
/// -------
/// dict
///     ``{"statistic": float, "p_value": float, "n_perm": int}``
///
/// Raises
/// ------
/// ValueError
///     If ``data_a`` and ``data_b`` have mismatched column counts, if
///     ``argvals.len()`` does not match the column count, if either sample
///     has fewer than 2 rows, or if ``n_perm == 0``.
#[pyfunction]
#[pyo3(signature = (data_a, data_b, argvals, n_perm=999, seed=None))]
pub fn t_perm_test<'py>(
    py: Python<'py>,
    data_a: PyReadonlyArray2<'py, f64>,
    data_b: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    n_perm: usize,
    seed: Option<u64>,
) -> PyResult<Bound<'py, PyDict>> {
    let mat_a = numpy2d_to_fdmatrix(data_a)?;
    let mat_b = numpy2d_to_fdmatrix(data_b)?;
    let av = numpy1d_to_vec(argvals);
    let s = seed.unwrap_or(0);
    let result = to_pyresult(fdars_core::inference::t_perm_test(
        &mat_a, &mat_b, &av, n_perm, s,
    ))?;
    test_result_to_pydict(py, result)
}

// ---------------------------------------------------------------------------
// f_perm_test
// ---------------------------------------------------------------------------

/// Functional two-sample permutation *F*-test.
///
/// The k = 2 case of functional ANOVA: assembles a two-group problem from
/// ``data_a`` (label 0) and ``data_b`` (label 1) and computes the integrated
/// F-statistic. More sensitive than :func:`t_perm_test` when group variance
/// also differs (F-statistic captures both mean and variance differences).
/// The permutation null relabels group membership via a seeded Fisher–Yates
/// shuffle. P-value: ``(#{perm >= observed} + 1) / (n_perm + 1)``.
///
/// Parameters
/// ----------
/// data_a : numpy.ndarray
///     First sample, shape ``(n_a, m)``. Rows are observations.
/// data_b : numpy.ndarray
///     Second sample, shape ``(n_b, m)``. Must have the same column count as
///     ``data_a``.
/// argvals : numpy.ndarray
///     Evaluation points, length ``m``. Must match the column count.
/// n_perm : int, optional
///     Number of permutations (default 999). Must be >= 1.
/// seed : int or None, optional
///     RNG seed for deterministic results. ``None`` resolves to fixed default
///     ``0`` — two calls with ``seed=None`` and identical inputs are
///     byte-identical. Pass an explicit integer to override.
///
/// Returns
/// -------
/// dict
///     ``{"statistic": float, "p_value": float, "n_perm": int}``
///
/// Raises
/// ------
/// ValueError
///     If ``data_a`` and ``data_b`` have mismatched column counts, if
///     ``argvals.len()`` does not match the column count, if either sample
///     has fewer than 2 rows, or if ``n_perm == 0``.
#[pyfunction]
#[pyo3(signature = (data_a, data_b, argvals, n_perm=999, seed=None))]
pub fn f_perm_test<'py>(
    py: Python<'py>,
    data_a: PyReadonlyArray2<'py, f64>,
    data_b: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    n_perm: usize,
    seed: Option<u64>,
) -> PyResult<Bound<'py, PyDict>> {
    let mat_a = numpy2d_to_fdmatrix(data_a)?;
    let mat_b = numpy2d_to_fdmatrix(data_b)?;
    let av = numpy1d_to_vec(argvals);
    let s = seed.unwrap_or(0);
    let result = to_pyresult(fdars_core::inference::f_perm_test(
        &mat_a, &mat_b, &av, n_perm, s,
    ))?;
    test_result_to_pydict(py, result)
}

// ---------------------------------------------------------------------------
// two_sample_mean_test
// ---------------------------------------------------------------------------

/// Functional two-sample mean-equality test via Hotelling-T² on a shared FPC
/// basis.
///
/// Both samples are projected onto a common FPC basis fitted on the pooled
/// data. The Hotelling-T² statistic is formed on the difference of the two
/// group score-means and compared against an asymptotic χ²(``ncomp``)
/// distribution. No permutations are performed; ``result["n_perm"]`` is always
/// ``0``.
///
/// Parameters
/// ----------
/// data_a : numpy.ndarray
///     First sample, shape ``(n_a, m)``. Rows are observations.
/// data_b : numpy.ndarray
///     Second sample, shape ``(n_b, m)``. Must have the same column count as
///     ``data_a``.
/// argvals : numpy.ndarray
///     Evaluation points, length ``m``. Must match the column count.
/// ncomp : int, optional
///     Number of FPC components for the shared basis (default 5). Keep small
///     relative to ``min(n_a, n_b)``.
///
/// Returns
/// -------
/// dict
///     ``{"statistic": float, "p_value": float, "n_perm": int}`` with
///     ``n_perm`` always equal to ``0`` (asymptotic, not permutation-based).
///
/// Raises
/// ------
/// ValueError
///     If ``data_a`` and ``data_b`` have mismatched column counts, if
///     ``argvals.len()`` does not match the column count, if either sample
///     has fewer than 2 rows, or if ``ncomp == 0``.
#[pyfunction]
#[pyo3(signature = (data_a, data_b, argvals, ncomp=5))]
pub fn two_sample_mean_test<'py>(
    py: Python<'py>,
    data_a: PyReadonlyArray2<'py, f64>,
    data_b: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    ncomp: usize,
) -> PyResult<Bound<'py, PyDict>> {
    let mat_a = numpy2d_to_fdmatrix(data_a)?;
    let mat_b = numpy2d_to_fdmatrix(data_b)?;
    let av = numpy1d_to_vec(argvals);
    let result = to_pyresult(fdars_core::inference::two_sample_mean_test(
        &mat_a, &mat_b, &av, ncomp,
    ))?;
    test_result_to_pydict(py, result)
}

// ---------------------------------------------------------------------------
// Internal helper: map a multiplier string to MultiplierDistribution.
//
// The enum is #[non_exhaustive] — the wildcard arm is mandatory.  An unknown
// string becomes a Python ValueError listing the accepted values.
// ---------------------------------------------------------------------------

fn multiplier_from_str(s: &str) -> PyResult<fdars_core::tolerance::MultiplierDistribution> {
    match s {
        "gaussian" => Ok(fdars_core::tolerance::MultiplierDistribution::Gaussian),
        "rademacher" => Ok(fdars_core::tolerance::MultiplierDistribution::Rademacher),
        _ => Err(PyValueError::new_err(format!(
            "multiplier must be 'gaussian' or 'rademacher', got '{s}'"
        ))),
    }
}

// ---------------------------------------------------------------------------
// mean_scb
// ---------------------------------------------------------------------------

/// Simultaneous confidence band for the mean function (Degras).
///
/// Wraps ``fdars_core::inference::mean_scb`` (which in turn wraps
/// ``tolerance::scb_mean_degras``). Returns a simultaneous band whose
/// ``lower``/``upper`` interval covers the true mean at approximately
/// ``confidence`` coverage.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Functional data matrix, shape ``(n, m)``. Requires ``n >= 3``.
/// argvals : numpy.ndarray
///     Evaluation grid, length ``m``. Must match the column count of ``data``.
/// bandwidth : float
///     Kernel bandwidth for local-polynomial smoothing. Must be positive.
/// nb : int, optional
///     Number of multiplier bootstrap replicates (default 200). Must be >= 1.
/// confidence : float, optional
///     Confidence level in the open interval ``(0, 1)`` (default 0.95).
/// multiplier : str, optional
///     Multiplier distribution: ``"gaussian"`` (default) or ``"rademacher"``.
///
/// Returns
/// -------
/// dict
///     ``{"lower": ndarray, "upper": ndarray, "center": ndarray,
///     "half_width": ndarray}`` — each a 1-D array of length ``m``.
///
/// Raises
/// ------
/// ValueError
///     If ``multiplier`` is not ``"gaussian"`` or ``"rademacher"``,
///     if ``nb == 0``, if ``confidence`` is outside ``(0, 1)``,
///     if ``bandwidth <= 0``, if ``n < 3``, or if the grid length mismatches.
#[pyfunction]
#[pyo3(signature = (data, argvals, bandwidth, nb=200, confidence=0.95, multiplier="gaussian"))]
pub fn mean_scb<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    bandwidth: f64,
    nb: usize,
    confidence: f64,
    multiplier: &str,
) -> PyResult<Bound<'py, PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let dist = multiplier_from_str(multiplier)?;
    let band = to_pyresult(fdars_core::inference::mean_scb(
        &mat, &av, bandwidth, nb, confidence, dist,
    ))?;
    let dict = PyDict::new(py);
    dict.set_item("lower", vec_to_numpy1d(py, band.lower))?;
    dict.set_item("upper", vec_to_numpy1d(py, band.upper))?;
    dict.set_item("center", vec_to_numpy1d(py, band.center))?;
    dict.set_item("half_width", vec_to_numpy1d(py, band.half_width))?;
    Ok(dict)
}

// ---------------------------------------------------------------------------
// scb_two_sample_test
// ---------------------------------------------------------------------------

/// Two-sample mean-equality test via a simultaneous confidence band for the
/// mean difference (``SCBmeanfd``-style Degras test).
///
/// Forms the paired difference matrix ``d[i] = data_a[i] - data_b[i]`` over the
/// first ``min(n_a, n_b)`` rows and applies the Degras multiplier bootstrap to
/// produce a simultaneous band for the mean difference. The null of equal means
/// is rejected when that band excludes zero at any grid point.
///
/// The returned dict encodes the decision:
///
/// * ``statistic`` — maximum standardised excursion of the difference band from
///   zero, ``max_t (|center(t)| / half_width(t))``; exceeds ``1.0`` when null
///   is rejected.
/// * ``p_value`` — ``0.0`` when the null is rejected, ``1.0`` otherwise
///   (conservative SCB-based encoding; no finer p-value available from a single
///   band).
/// * ``n_perm`` — always ``0`` (asymptotic/bootstrap, not permutation).
///
/// Parameters
/// ----------
/// data_a : numpy.ndarray
///     First sample, shape ``(n_a, m)``.
/// data_b : numpy.ndarray
///     Second sample, shape ``(n_b, m)``. Must have the same column count.
/// argvals : numpy.ndarray
///     Evaluation grid, length ``m``.
/// bandwidth : float
///     Kernel bandwidth for local-polynomial smoothing. Must be positive.
/// nb : int, optional
///     Number of multiplier bootstrap replicates (default 200). Must be >= 1.
/// confidence : float, optional
///     Confidence level in ``(0, 1)`` (default 0.95).
/// multiplier : str, optional
///     Multiplier distribution: ``"gaussian"`` (default) or ``"rademacher"``.
///
/// Returns
/// -------
/// dict
///     ``{"statistic": float, "p_value": float, "n_perm": int}`` with
///     ``n_perm`` always ``0``.
///
/// Raises
/// ------
/// ValueError
///     If ``multiplier`` is not ``"gaussian"`` or ``"rademacher"``,
///     if columns of ``data_a`` and ``data_b`` mismatch, if grid length
///     mismatches, if ``nb == 0``, or if ``confidence`` is outside ``(0, 1)``.
#[pyfunction]
#[pyo3(signature = (data_a, data_b, argvals, bandwidth, nb=200, confidence=0.95, multiplier="gaussian"))]
pub fn scb_two_sample_test<'py>(
    py: Python<'py>,
    data_a: PyReadonlyArray2<'py, f64>,
    data_b: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    bandwidth: f64,
    nb: usize,
    confidence: f64,
    multiplier: &str,
) -> PyResult<Bound<'py, PyDict>> {
    let mat_a = numpy2d_to_fdmatrix(data_a)?;
    let mat_b = numpy2d_to_fdmatrix(data_b)?;
    let av = numpy1d_to_vec(argvals);
    let dist = multiplier_from_str(multiplier)?;
    let result = to_pyresult(fdars_core::inference::scb_two_sample_test(
        &mat_a, &mat_b, &av, bandwidth, nb, confidence, dist,
    ))?;
    test_result_to_pydict(py, result)
}

// ---------------------------------------------------------------------------
// Difference regions (shared with ``alignment.elastic_local_difference_test``)
// ---------------------------------------------------------------------------

/// `DifferenceRegion`s → list of dicts with keys ``start_idx``, ``end_idx``,
/// ``t_start``, ``t_end``, ``direction`` (``"positive"`` / ``"negative"``) and
/// ``min_adjusted_pvalue`` (float, or None for band-based regions). With
/// `timing`, each dict also gets ``timing`` (``"a_later"`` / ``"a_earlier"``).
pub(crate) fn difference_regions_list<'py>(
    py: Python<'py>,
    regions: &[fdars_core::regions::DifferenceRegion],
    timing: bool,
) -> PyResult<Bound<'py, PyList>> {
    use fdars_core::alignment::{LocalDifferenceTest, Timing};
    use fdars_core::regions::SignificanceDirection;
    let list = PyList::empty(py);
    for r in regions {
        let d = PyDict::new(py);
        d.set_item("start_idx", r.start_idx)?;
        d.set_item("end_idx", r.end_idx)?;
        d.set_item("t_start", r.t_start)?;
        d.set_item("t_end", r.t_end)?;
        let direction = match r.direction {
            SignificanceDirection::Positive => "positive",
            SignificanceDirection::Negative => "negative",
            _ => "unknown",
        };
        d.set_item("direction", direction)?;
        d.set_item("min_adjusted_pvalue", r.min_adjusted_pvalue)?;
        if timing {
            let t = match LocalDifferenceTest::timing(r) {
                Timing::ALater => "a_later",
                Timing::AEarlier => "a_earlier",
                _ => "unknown",
            };
            d.set_item("timing", t)?;
        }
        list.append(d)?;
    }
    Ok(list)
}

// ---------------------------------------------------------------------------
// scb_two_sample_band
// ---------------------------------------------------------------------------

/// Two-sample SCB for the mean difference and the regions where it excludes zero.
///
/// Same construction and arguments as ``scb_two_sample_test`` (paired
/// difference of the first ``min(n_a, n_b)`` rows, Degras multiplier
/// bootstrap), which returns only the decision; this function also returns the
/// band and the contiguous grid regions where it excludes zero, i.e. where the
/// two mean functions differ with simultaneous (family-wise over the grid)
/// coverage ``confidence``. ``statistic`` and ``rejected`` reproduce
/// ``scb_two_sample_test`` exactly for the same inputs.
///
/// Parameters
/// ----------
/// data_a : numpy.ndarray
///     First sample, shape ``(n_a, m)``.
/// data_b : numpy.ndarray
///     Second sample, shape ``(n_b, m)``. Must have the same column count.
/// argvals : numpy.ndarray
///     Evaluation grid, length ``m``.
/// bandwidth : float
///     Kernel bandwidth for local-polynomial smoothing. Must be positive.
/// nb : int, optional
///     Number of multiplier bootstrap replicates (default 200). Must be >= 1.
/// confidence : float, optional
///     Confidence level in ``(0, 1)`` (default 0.95).
/// multiplier : str, optional
///     Multiplier distribution: ``"gaussian"`` (default) or ``"rademacher"``.
///
/// Returns
/// -------
/// dict
///     ``estimate`` (m,) smoothed ``mean_a - mean_b`` (band centre), ``lower``
///     (m,), ``upper`` (m,), ``half_width`` (m,) ``= critical_value *
///     sigma(t) / sqrt(n)``, ``critical_value``, ``confidence``,
///     ``statistic`` (``max_t |estimate| / half_width``), ``rejected`` (band
///     excludes zero somewhere) and ``regions``: list of dicts
///     ``{start_idx, end_idx, t_start, t_end, direction,
///     min_adjusted_pvalue}`` with ``direction`` ``"positive"`` (A above B) or
///     ``"negative"`` and ``min_adjusted_pvalue`` always None.
///
/// Raises
/// ------
/// ValueError
///     As ``scb_two_sample_test``.
#[pyfunction]
#[pyo3(signature = (data_a, data_b, argvals, bandwidth, nb=200, confidence=0.95, multiplier="gaussian"))]
pub fn scb_two_sample_band<'py>(
    py: Python<'py>,
    data_a: PyReadonlyArray2<'py, f64>,
    data_b: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    bandwidth: f64,
    nb: usize,
    confidence: f64,
    multiplier: &str,
) -> PyResult<Bound<'py, PyDict>> {
    let mat_a = numpy2d_to_fdmatrix(data_a)?;
    let mat_b = numpy2d_to_fdmatrix(data_b)?;
    let av = numpy1d_to_vec(argvals);
    let dist = multiplier_from_str(multiplier)?;
    let r = to_pyresult(fdars_core::inference::scb_two_sample_band(
        &mat_a, &mat_b, &av, bandwidth, nb, confidence, dist,
    ))?;
    let dict = PyDict::new(py);
    dict.set_item("estimate", vec_to_numpy1d(py, r.estimate))?;
    dict.set_item("lower", vec_to_numpy1d(py, r.lower))?;
    dict.set_item("upper", vec_to_numpy1d(py, r.upper))?;
    dict.set_item("half_width", vec_to_numpy1d(py, r.half_width))?;
    dict.set_item("critical_value", r.critical_value)?;
    dict.set_item("confidence", r.confidence)?;
    dict.set_item("statistic", r.statistic)?;
    dict.set_item("rejected", r.rejected)?;
    dict.set_item("regions", difference_regions_list(py, &r.regions, false)?)?;
    Ok(dict)
}

// ---------------------------------------------------------------------------
// flm_f_test
// ---------------------------------------------------------------------------

/// Functional linear model overall-significance F-test.
///
/// Re-fits a scalar-on-function linear regression (``fregre_lm``) internally
/// from ``data``, ``response``, and ``n_comp``, then applies the
/// ``fdars_core::inference::flm_f_test`` F-test on the fitted object.
/// The ``FregreLmResult`` never crosses the Python boundary.
///
/// A significant result (small ``p_value``) indicates that the functional
/// predictor explains a statistically significant fraction of the variance in
/// the scalar response (i.e. the overall regression is meaningful).
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Functional predictors, shape ``(n, m)``. Rows are observations.
/// response : numpy.ndarray
///     Scalar response, length ``n``.
/// n_comp : int, optional
///     Number of FPC components for the internal fit (default 5). Must be
///     strictly less than ``n - 1``; a degenerate fit (too few observations
///     relative to ``n_comp``) raises ``ValueError``.
///
/// Returns
/// -------
/// dict
///     ``{"statistic": float, "p_value": float, "n_perm": int}`` with
///     ``n_perm`` always equal to ``0`` (asymptotic, not permutation-based).
///
/// Raises
/// ------
/// ValueError
///     If the internal ``fregre_lm`` fit is degenerate (e.g. ``n_comp`` is too
///     large relative to ``n``), or if the F-test denominator degrees of
///     freedom are non-positive, or if ``r_squared`` is non-finite.
#[pyfunction]
#[pyo3(signature = (data, response, n_comp=5))]
pub fn flm_f_test<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    response: PyReadonlyArray1<'py, f64>,
    n_comp: usize,
) -> PyResult<Bound<'py, PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let resp = numpy1d_to_vec(response);
    let fit = to_pyresult(fdars_core::scalar_on_function::fregre_lm(
        &mat, &resp, None, n_comp,
    ))?;
    let result = to_pyresult(fdars_core::inference::flm_f_test(&fit))?;
    test_result_to_pydict(py, result)
}

// ---------------------------------------------------------------------------
// flm_gof_test
// ---------------------------------------------------------------------------

/// Functional linear model goodness-of-fit test (Ramsey-RESET style).
///
/// Re-fits a scalar-on-function linear regression (``fregre_lm``) internally
/// from ``data``, ``response``, and ``n_comp``, then applies the
/// ``fdars_core::inference::flm_gof_test`` lack-of-fit test on the fitted
/// object. The ``FregreLmResult`` never crosses the Python boundary.
///
/// A significant result (small ``p_value``) indicates that the functional
/// linear model misses a nonlinear effect of the functional predictor, i.e.
/// the linear specification is insufficient.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Functional predictors, shape ``(n, m)``. Rows are observations.
/// response : numpy.ndarray
///     Scalar response, length ``n``.
/// n_comp : int, optional
///     Number of FPC components for the internal fit (default 5). Must satisfy
///     ``n > n_comp + Q + 1`` (where Q = 3 auxiliary polynomial powers) for
///     sufficient residual degrees of freedom; a degenerate fit raises
///     ``ValueError``.
///
/// Returns
/// -------
/// dict
///     ``{"statistic": float, "p_value": float, "n_perm": int}`` with
///     ``n_perm`` always equal to ``0`` (asymptotic, not permutation-based).
///
/// Raises
/// ------
/// ValueError
///     If the internal ``fregre_lm`` fit is degenerate, if ``n <= 4``
///     (insufficient auxiliary df), if residuals/fitted values contain
///     non-finite values, or if the auxiliary design is rank-deficient
///     (constant fitted values).
#[pyfunction]
#[pyo3(signature = (data, response, n_comp=5))]
pub fn flm_gof_test<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    response: PyReadonlyArray1<'py, f64>,
    n_comp: usize,
) -> PyResult<Bound<'py, PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let resp = numpy1d_to_vec(response);
    let fit = to_pyresult(fdars_core::scalar_on_function::fregre_lm(
        &mat, &resp, None, n_comp,
    ))?;
    let result = to_pyresult(fdars_core::inference::flm_gof_test(&fit))?;
    test_result_to_pydict(py, result)
}

// ---------------------------------------------------------------------------
// oneway_anova_vstat
// ---------------------------------------------------------------------------

/// One-way functional ANOVA V-statistic (asymptotic scaled-χ² test).
///
/// Computes the Satterthwaite-approximated V-statistic for testing equality of
/// group mean functions in a one-way functional ANOVA design. The test is
/// asymptotic (no permutations); ``result["n_perm"]`` is always ``0``.
///
/// Complements the existing permutation ``fanova`` (from ``fdars.regression``):
/// this function is faster (single computation) but relies on the asymptotic
/// distribution, while ``fanova`` is exact under the permutation null.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Functional data matrix, shape ``(n, m)``. Rows are observations.
/// groups : numpy.ndarray
///     1-D integer array of length ``n`` with non-negative 0-indexed group
///     labels (dtype int64). Negative values raise ``ValueError``. Labels
///     need not be contiguous — any distinct non-negative ``int64`` values
///     define the groups.
/// argvals : numpy.ndarray
///     Evaluation grid, length ``m``. Must match the column count of ``data``.
///
/// Returns
/// -------
/// dict
///     ``{"statistic": float, "p_value": float, "n_perm": int}`` with
///     ``n_perm`` always equal to ``0`` (asymptotic).
///
/// Raises
/// ------
/// ValueError
///     If ``groups.len() != n``, if fewer than 2 distinct groups are present,
///     if ``n < 3``, if ``argvals.len() != m`` (or ``m == 0``), or if any
///     group label is negative.
#[pyfunction]
#[pyo3(signature = (data, groups, argvals))]
pub fn oneway_anova_vstat<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    groups: PyReadonlyArray1<'py, i64>,
    argvals: PyReadonlyArray1<'py, f64>,
) -> PyResult<Bound<'py, PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let raw = groups.as_array();
    if raw.iter().any(|&x| x < 0) {
        return Err(PyValueError::new_err(
            "groups must contain non-negative integer labels; got at least one negative value",
        ));
    }
    let grp = raw.iter().map(|&x| x as usize).collect::<Vec<_>>();
    let av = numpy1d_to_vec(argvals);
    let result = to_pyresult(fdars_core::inference::oneway_anova_vstat(&mat, &grp, &av))?;
    test_result_to_pydict(py, result)
}

// ---------------------------------------------------------------------------
// Internal helper: map a ProjectionBasisType variant to its string token.
//
// The enum is #[non_exhaustive] — the wildcard arm is mandatory.
// ---------------------------------------------------------------------------

fn basis_type_variant_str(b: &fdars_core::ProjectionBasisType) -> &'static str {
    match b {
        fdars_core::ProjectionBasisType::Bspline => "bspline",
        fdars_core::ProjectionBasisType::Fourier => "fourier",
        _ => "unknown",
    }
}

// ---------------------------------------------------------------------------
// Internal helper: map a basis_type string to ProjectionBasisType.
//
// The enum is #[non_exhaustive] — an unknown token raises ValueError.
// ---------------------------------------------------------------------------

fn basis_type_from_str(s: &str) -> PyResult<fdars_core::ProjectionBasisType> {
    match s {
        "bspline" => Ok(fdars_core::ProjectionBasisType::Bspline),
        "fourier" => Ok(fdars_core::ProjectionBasisType::Fourier),
        other => Err(PyValueError::new_err(format!(
            "basis_type must be 'bspline' or 'fourier', got '{other}'"
        ))),
    }
}

// ---------------------------------------------------------------------------
// Internal helper: map a fdars_core::inference::ItpResult to a Python dict.
//
// The struct is #[non_exhaustive] — never struct-literal it; access each
// field individually.  P-values are VECTORS (Vec<f64>) not scalars — exposed
// as 1-D numpy arrays via vec_to_numpy1d.  This is DISTINCT from
// test_result_to_pydict which expects scalar statistic/p_value fields.
// ---------------------------------------------------------------------------

pub(crate) fn itp_result_to_pydict<'py>(
    py: Python<'py>,
    r: fdars_core::inference::ItpResult,
) -> PyResult<Bound<'py, PyDict>> {
    let dict = PyDict::new(py);
    dict.set_item("adjusted_pvalues", vec_to_numpy1d(py, r.adjusted_pvalues))?;
    dict.set_item("raw_pvalues", vec_to_numpy1d(py, r.raw_pvalues))?;
    dict.set_item("basis_type", basis_type_variant_str(&r.basis_type))?;
    dict.set_item("n_basis", r.n_basis)?;
    dict.set_item("n_perm", r.n_perm)?;
    Ok(dict)
}

// ---------------------------------------------------------------------------
// itp_one_pop
// ---------------------------------------------------------------------------

/// Interval-wise testing procedure for a single functional population.
///
/// Tests whether the mean function of ``data`` differs from a null mean
/// ``mu0`` (default: zero function) at each projection-basis coefficient.
/// Returns closure-adjusted and raw p-values (one per basis function).
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Functional data matrix, shape ``(n, m)``. Requires ``n >= 2``.
/// argvals : numpy.ndarray
///     Evaluation grid, length ``m``. Must match the column count of ``data``.
/// mu0 : numpy.ndarray or None, optional
///     Null mean function, length ``m``. ``None`` uses the zero function.
/// basis_type : str, optional
///     Projection basis: ``"bspline"`` (default) or ``"fourier"``.
/// nbasis : int, optional
///     Number of basis functions to request (default 5). Must be >= 2.
///     B-spline clamping may reduce the actual count; read ``n_basis`` from
///     the returned dict for the actual length of the p-value arrays.
/// n_perm : int, optional
///     Number of permutations (default 999). Must be >= 1.
/// seed : int or None, optional
///     RNG seed. ``None`` resolves to fixed default ``0`` — two calls with
///     ``seed=None`` and identical inputs are byte-identical.
///
/// Returns
/// -------
/// dict
///     ``{"adjusted_pvalues": ndarray(n_basis,), "raw_pvalues": ndarray(n_basis,),
///     "basis_type": str, "n_basis": int, "n_perm": int}``
///
/// Raises
/// ------
/// ValueError
///     If ``n < 2``, ``argvals`` length mismatches, ``mu0`` length mismatches,
///     ``nbasis < 2``, ``n_perm == 0``, or basis projection fails.
#[pyfunction]
#[pyo3(signature = (data, argvals, mu0=None, basis_type="bspline", nbasis=5, n_perm=999, seed=None))]
pub fn itp_one_pop<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    mu0: Option<PyReadonlyArray1<'py, f64>>,
    basis_type: &str,
    nbasis: usize,
    n_perm: usize,
    seed: Option<u64>,
) -> PyResult<Bound<'py, PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let mu0_vec = mu0.map(|a| numpy1d_to_vec(a));
    let bt = basis_type_from_str(basis_type)?;
    let s = seed.unwrap_or(0);
    let r = to_pyresult(fdars_core::inference::itp_one_pop(
        &mat,
        &av,
        mu0_vec.as_deref(),
        bt,
        nbasis,
        n_perm,
        s,
    ))?;
    itp_result_to_pydict(py, r)
}

// ---------------------------------------------------------------------------
// itp_two_pop
// ---------------------------------------------------------------------------

/// Interval-wise testing procedure for two functional populations.
///
/// Tests whether the mean functions of ``data_a`` and ``data_b`` differ at
/// each projection-basis coefficient. Returns closure-adjusted and raw
/// p-values (one per basis function).
///
/// Parameters
/// ----------
/// data_a : numpy.ndarray
///     First sample, shape ``(n_a, m)``. Requires ``n_a >= 2``.
/// data_b : numpy.ndarray
///     Second sample, shape ``(n_b, m)``. Requires ``n_b >= 2``. Must have
///     the same column count as ``data_a``.
/// argvals : numpy.ndarray
///     Evaluation grid, length ``m``. Must match the column count.
/// basis_type : str, optional
///     Projection basis: ``"bspline"`` (default) or ``"fourier"``.
/// nbasis : int, optional
///     Number of basis functions to request (default 5). Must be >= 2.
/// n_perm : int, optional
///     Number of permutations (default 999). Must be >= 1.
/// seed : int or None, optional
///     RNG seed. ``None`` resolves to fixed default ``0`` — two calls with
///     ``seed=None`` and identical inputs are byte-identical.
///
/// Returns
/// -------
/// dict
///     ``{"adjusted_pvalues": ndarray(n_basis,), "raw_pvalues": ndarray(n_basis,),
///     "basis_type": str, "n_basis": int, "n_perm": int}``
///
/// Raises
/// ------
/// ValueError
///     If ``n_a < 2`` or ``n_b < 2``, column counts mismatch, ``argvals``
///     length mismatches, ``nbasis < 2``, ``n_perm == 0``, or basis
///     projection fails.
#[pyfunction]
#[pyo3(signature = (data_a, data_b, argvals, basis_type="bspline", nbasis=5, n_perm=999, seed=None))]
pub fn itp_two_pop<'py>(
    py: Python<'py>,
    data_a: PyReadonlyArray2<'py, f64>,
    data_b: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    basis_type: &str,
    nbasis: usize,
    n_perm: usize,
    seed: Option<u64>,
) -> PyResult<Bound<'py, PyDict>> {
    let mat_a = numpy2d_to_fdmatrix(data_a)?;
    let mat_b = numpy2d_to_fdmatrix(data_b)?;
    let av = numpy1d_to_vec(argvals);
    let bt = basis_type_from_str(basis_type)?;
    let s = seed.unwrap_or(0);
    let r = to_pyresult(fdars_core::inference::itp_two_pop(
        &mat_a, &mat_b, &av, bt, nbasis, n_perm, s,
    ))?;
    itp_result_to_pydict(py, r)
}

// ---------------------------------------------------------------------------
// itp_pointwise_pvalues / itp_two_pop_regions
// ---------------------------------------------------------------------------

pub(crate) fn itp_mapping_from_str(s: &str) -> PyResult<fdars_core::inference::ItpDomainMapping> {
    match s {
        "dominant" => Ok(fdars_core::inference::ItpDomainMapping::Dominant),
        "support" => Ok(fdars_core::inference::ItpDomainMapping::Support),
        _ => Err(PyValueError::new_err(format!(
            "mapping must be 'dominant' or 'support', got '{s}'"
        ))),
    }
}

/// Map the per-component adjusted p-values of a B-spline ITP to the grid.
///
/// Every grid point ``t`` gets an adjusted p-value from the components of
/// ``result``; because the ITP controls the interval-wise error rate,
/// ``{t : p(t) < alpha}`` is the set of domain points where the null is
/// rejected at level ``alpha``.
///
/// Parameters
/// ----------
/// result : dict
///     Result of ``itp_two_pop`` or ``itp_one_pop`` (or the ``"itp"`` entry of
///     ``itp_two_pop_regions``) computed with ``basis_type="bspline"`` on the
///     same ``argvals``. Its ``adjusted_pvalues``, ``n_basis`` and
///     ``basis_type`` are used.
/// argvals : numpy.ndarray
///     Evaluation grid of the ITP, length ``m``.
/// mapping : str, optional
///     ``"dominant"`` (default): ``p(t)`` is the adjusted p-value of the
///     component with the largest basis value at ``t`` (the ``fdatest``
///     nearest-component convention on fdars's B-spline basis).
///     ``"support"``: the largest adjusted p-value among the components whose
///     basis function is positive at ``t`` (conservative).
///
/// Returns
/// -------
/// numpy.ndarray
///     Adjusted p-value per grid point, shape ``(m,)``.
///
/// Raises
/// ------
/// ValueError
///     For a Fourier ITP (Fourier components are frequencies, not domain
///     locations), fewer than 2 grid points or ``n_basis < 6``, a
///     ``len(adjusted_pvalues) != n_basis`` mismatch, a ``result`` whose
///     ``n_basis`` does not fit ``argvals``, a missing key or an unknown
///     ``mapping``.
#[pyfunction]
#[pyo3(signature = (result, argvals, mapping="dominant"))]
pub fn itp_pointwise_pvalues<'py>(
    py: Python<'py>,
    result: &Bound<'py, PyDict>,
    argvals: PyReadonlyArray1<'py, f64>,
    mapping: &str,
) -> PyResult<Bound<'py, PyArray1<f64>>> {
    let get = |key: &str| -> PyResult<Bound<'py, PyAny>> {
        result
            .get_item(key)?
            .ok_or_else(|| PyValueError::new_err(format!("result has no '{key}' entry")))
    };
    let adjusted: Vec<f64> = get("adjusted_pvalues")?.extract()?;
    let n_basis: usize = get("n_basis")?.extract()?;
    let basis_type: String = get("basis_type")?.extract()?;
    let bt = basis_type_from_str(&basis_type)?;
    let mapping = itp_mapping_from_str(mapping)?;
    let av = numpy1d_to_vec(argvals);
    // `ItpResult` is #[non_exhaustive]: obtain one with this basis on this grid
    // from a one-permutation ITP of two dummy curves, then substitute the
    // caller's adjusted p-values. The core then validates and maps them.
    let m = av.len();
    let dummy = to_pyresult(fdars_core::FdMatrix::from_column_major(
        (0..m).flat_map(|j| [av[j], 1.0 - av[j]]).collect(),
        2,
        m,
    ))?;
    let mut itp = to_pyresult(fdars_core::inference::itp_one_pop(
        &dummy,
        &av,
        None,
        bt,
        n_basis.max(2),
        1,
        0,
    ))?;
    if itp.n_basis != n_basis {
        return Err(PyValueError::new_err(format!(
            "result has n_basis = {n_basis}, but that basis has {} functions on this argvals",
            itp.n_basis
        )));
    }
    itp.adjusted_pvalues = adjusted;
    let pw = to_pyresult(fdars_core::inference::itp_pointwise_pvalues(
        &itp, &av, mapping,
    ))?;
    Ok(vec_to_numpy1d(py, pw))
}

/// Grid regions where two mean functions differ, by a two-population B-spline ITP.
///
/// Runs ``itp_two_pop`` with a B-spline basis, maps the closure-adjusted
/// component p-values to the grid with ``itp_pointwise_pvalues`` and returns
/// the contiguous regions where the adjusted p-value is below ``alpha``, each
/// with the direction of the mean difference. The interval-wise error rate is
/// controlled at ``alpha`` (Pini & Vantini 2016).
///
/// Parameters
/// ----------
/// data_a : numpy.ndarray
///     First sample, shape ``(n_a, m)``, ``n_a >= 2``.
/// data_b : numpy.ndarray
///     Second sample, shape ``(n_b, m)``, ``n_b >= 2``.
/// argvals : numpy.ndarray
///     Evaluation grid, length ``m``.
/// nbasis : int, optional
///     Requested number of B-spline basis functions (default 15; the actual
///     count is ``itp["n_basis"]``, at least 6).
/// n_perm : int, optional
///     Number of permutations (default 999).
/// seed : int, optional
///     RNG seed (default 42).
/// alpha : float, optional
///     Interval-wise significance level in ``(0, 1)`` (default 0.05).
/// mapping : str, optional
///     Component-to-grid mapping, ``"dominant"`` (default) or ``"support"``;
///     see ``itp_pointwise_pvalues``.
///
/// Returns
/// -------
/// dict
///     ``itp`` (the ``itp_two_pop`` dict), ``pointwise_adjusted_pvalues``
///     (m,), ``mean_difference`` (m,) ``mean_a - mean_b`` and ``regions``:
///     list of dicts ``{start_idx, end_idx, t_start, t_end, direction,
///     min_adjusted_pvalue}`` for the runs with ``p(t) < alpha``, split where
///     the sign of ``mean_difference`` changes; ``direction`` is
///     ``"positive"`` (A above B) or ``"negative"``.
///
/// Raises
/// ------
/// ValueError
///     As ``itp_two_pop``; also for ``alpha`` outside ``(0, 1)`` or an
///     unknown ``mapping``.
#[pyfunction]
#[pyo3(signature = (data_a, data_b, argvals, nbasis=15, n_perm=999, seed=42, alpha=0.05, mapping="dominant"))]
pub fn itp_two_pop_regions<'py>(
    py: Python<'py>,
    data_a: PyReadonlyArray2<'py, f64>,
    data_b: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    nbasis: usize,
    n_perm: usize,
    seed: u64,
    alpha: f64,
    mapping: &str,
) -> PyResult<Bound<'py, PyDict>> {
    let mat_a = numpy2d_to_fdmatrix(data_a)?;
    let mat_b = numpy2d_to_fdmatrix(data_b)?;
    let av = numpy1d_to_vec(argvals);
    let mut cfg = fdars_core::inference::ItpRegionConfig::default();
    cfg.nbasis = nbasis;
    cfg.n_perm = n_perm;
    cfg.seed = seed;
    cfg.alpha = alpha;
    cfg.mapping = itp_mapping_from_str(mapping)?;
    let r = to_pyresult(fdars_core::inference::itp_two_pop_regions(
        &mat_a, &mat_b, &av, &cfg,
    ))?;
    let dict = PyDict::new(py);
    dict.set_item("itp", itp_result_to_pydict(py, r.itp)?)?;
    dict.set_item(
        "pointwise_adjusted_pvalues",
        vec_to_numpy1d(py, r.pointwise_adjusted_pvalues),
    )?;
    dict.set_item("mean_difference", vec_to_numpy1d(py, r.mean_difference))?;
    dict.set_item("regions", difference_regions_list(py, &r.regions, false)?)?;
    Ok(dict)
}

// ---------------------------------------------------------------------------
// itp_flm
// ---------------------------------------------------------------------------

/// Interval-wise testing procedure for the functional linear model.
///
/// Tests whether the functional predictor ``data`` is significantly
/// associated with the scalar response ``response`` at each
/// projection-basis coefficient. The FLM is re-fit internally from the
/// raw ``data`` and ``response`` — no persistent handle crosses the
/// Python boundary.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Functional predictors, shape ``(n, m)``. Requires ``n >= 2``.
/// response : numpy.ndarray
///     Scalar response vector, length ``n``.
/// argvals : numpy.ndarray
///     Evaluation grid, length ``m``. Must match the column count of ``data``.
/// basis_type : str, optional
///     Projection basis: ``"bspline"`` (default) or ``"fourier"``.
/// nbasis : int, optional
///     Number of basis functions to request (default 5). Must be >= 2.
/// n_perm : int, optional
///     Number of permutations (default 999). Must be >= 1.
/// seed : int or None, optional
///     RNG seed. ``None`` resolves to fixed default ``0`` — two calls with
///     ``seed=None`` and identical inputs are byte-identical.
///
/// Returns
/// -------
/// dict
///     ``{"adjusted_pvalues": ndarray(n_basis,), "raw_pvalues": ndarray(n_basis,),
///     "basis_type": str, "n_basis": int, "n_perm": int}``
///
/// Raises
/// ------
/// ValueError
///     If ``n < 2``, ``response.len() != n``, ``argvals`` length mismatches,
///     ``nbasis < 2``, ``n_perm == 0``, or basis projection fails.
#[pyfunction]
#[pyo3(signature = (data, response, argvals, basis_type="bspline", nbasis=5, n_perm=999, seed=None))]
pub fn itp_flm<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    response: PyReadonlyArray1<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    basis_type: &str,
    nbasis: usize,
    n_perm: usize,
    seed: Option<u64>,
) -> PyResult<Bound<'py, PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let y = numpy1d_to_vec(response);
    let av = numpy1d_to_vec(argvals);
    let bt = basis_type_from_str(basis_type)?;
    let s = seed.unwrap_or(0);
    let r = to_pyresult(fdars_core::inference::itp_flm(
        &mat, &y, &av, bt, nbasis, n_perm, s,
    ))?;
    itp_result_to_pydict(py, r)
}

// ---------------------------------------------------------------------------
// PERMANOVA on a distance matrix
// ---------------------------------------------------------------------------

/// PERMANOVA result → dict (shared with ``alignment.elastic_phase_amplitude_test``).
pub(crate) fn permanova_dict<'py>(
    py: Python<'py>,
    r: &fdars_core::inference::PermanovaResult,
) -> PyResult<Bound<'py, PyDict>> {
    let d = PyDict::new(py);
    d.set_item("statistic", r.statistic)?;
    d.set_item("p_value", r.p_value)?;
    d.set_item("ss_between", r.ss_between)?;
    d.set_item("ss_within", r.ss_within)?;
    d.set_item("ss_total", r.ss_total)?;
    d.set_item("r_squared", r.r_squared)?;
    d.set_item("df_between", r.df_between)?;
    d.set_item("df_within", r.df_within)?;
    d.set_item("n_perm", r.n_perm)?;
    Ok(d)
}

/// PERMANOVA (Anderson 2001) permutation test of group differences on a distance matrix.
///
/// The pseudo-F statistic of the between- vs within-group sums of squared
/// distances; the p-value is ``(1 + #{F_perm >= F}) / (n_perm + 1)`` over
/// seeded label permutations.
///
/// Parameters
/// ----------
/// dist : numpy.ndarray
///     Symmetric distance matrix with zero diagonal, shape (n, n).
/// labels : numpy.ndarray
///     Non-negative integer group labels, length n (need not be contiguous;
///     at least 2 groups and more observations than groups).
/// n_perm : int, optional
///     Number of permutations (default 999; 0 skips them, p_value = 1.0).
/// seed : int, optional
///     Permutation seed (default 42).
///
/// Returns
/// -------
/// dict
///     ``statistic`` (pseudo-F), ``p_value``, ``ss_between``, ``ss_within``,
///     ``ss_total``, ``r_squared``, ``df_between``, ``df_within``, ``n_perm``.
///
/// Raises
/// ------
/// ValueError
///     If ``dist`` is not a valid square symmetric distance matrix, labels
///     are negative or of the wrong length, or fewer than 2 groups.
#[pyfunction]
#[pyo3(signature = (dist, labels, n_perm=999, seed=42))]
pub fn permanova<'py>(
    py: Python<'py>,
    dist: PyReadonlyArray2<'py, f64>,
    labels: PyArrayLike1<'py, i64, AllowTypeChange>,
    n_perm: usize,
    seed: u64,
) -> PyResult<Bound<'py, PyDict>> {
    let d = numpy2d_to_fdmatrix(dist)?;
    let lab = nonneg_labels(&labels, "labels")?;
    let r = to_pyresult(fdars_core::inference::permanova(&d, &lab, n_perm, seed))?;
    permanova_dict(py, &r)
}

// ---------------------------------------------------------------------------
// Module registration
// ---------------------------------------------------------------------------

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(t_perm_test, m)?)?;
    m.add_function(wrap_pyfunction!(f_perm_test, m)?)?;
    m.add_function(wrap_pyfunction!(two_sample_mean_test, m)?)?;
    m.add_function(wrap_pyfunction!(mean_scb, m)?)?;
    m.add_function(wrap_pyfunction!(scb_two_sample_test, m)?)?;
    m.add_function(wrap_pyfunction!(scb_two_sample_band, m)?)?;
    m.add_function(wrap_pyfunction!(flm_f_test, m)?)?;
    m.add_function(wrap_pyfunction!(flm_gof_test, m)?)?;
    m.add_function(wrap_pyfunction!(oneway_anova_vstat, m)?)?;
    m.add_function(wrap_pyfunction!(itp_one_pop, m)?)?;
    m.add_function(wrap_pyfunction!(itp_two_pop, m)?)?;
    m.add_function(wrap_pyfunction!(itp_pointwise_pvalues, m)?)?;
    m.add_function(wrap_pyfunction!(itp_two_pop_regions, m)?)?;
    m.add_function(wrap_pyfunction!(itp_flm, m)?)?;
    m.add_function(wrap_pyfunction!(permanova, m)?)?;
    Ok(())
}
