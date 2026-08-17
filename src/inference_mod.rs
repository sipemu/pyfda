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
//!
//! All fallible functions route errors through `to_pyresult()` — no `.unwrap()`
//! appears in this module. Degenerate inputs raise `ValueError` on the Python side.
//! `seed=None` resolves to fixed default `0` for byte-identical reproducibility
//! across runs (required for offline docs fences and advisor determinism).

use crate::convert::*;
use numpy::{PyReadonlyArray1, PyReadonlyArray2};
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::PyDict;

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
// Module registration
// ---------------------------------------------------------------------------

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(t_perm_test, m)?)?;
    m.add_function(wrap_pyfunction!(f_perm_test, m)?)?;
    m.add_function(wrap_pyfunction!(two_sample_mean_test, m)?)?;
    m.add_function(wrap_pyfunction!(mean_scb, m)?)?;
    m.add_function(wrap_pyfunction!(scb_two_sample_test, m)?)?;
    Ok(())
}
