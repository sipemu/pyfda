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
//! `seed=None` resolves to fixed default `0` for [`t_perm_test`] and [`f_perm_test`],
//! giving byte-identical results across calls with the same inputs.
//! [`mean_scb`] and [`scb_two_sample_test`] accept no `seed` parameter; their
//! bootstrap randomness is internal to fdars-core and not externally seeded.

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

fn itp_result_to_pydict<'py>(
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
// Module registration
// ---------------------------------------------------------------------------

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(t_perm_test, m)?)?;
    m.add_function(wrap_pyfunction!(f_perm_test, m)?)?;
    m.add_function(wrap_pyfunction!(two_sample_mean_test, m)?)?;
    m.add_function(wrap_pyfunction!(mean_scb, m)?)?;
    m.add_function(wrap_pyfunction!(scb_two_sample_test, m)?)?;
    m.add_function(wrap_pyfunction!(flm_f_test, m)?)?;
    m.add_function(wrap_pyfunction!(flm_gof_test, m)?)?;
    m.add_function(wrap_pyfunction!(oneway_anova_vstat, m)?)?;
    m.add_function(wrap_pyfunction!(itp_one_pop, m)?)?;
    m.add_function(wrap_pyfunction!(itp_two_pop, m)?)?;
    Ok(())
}
