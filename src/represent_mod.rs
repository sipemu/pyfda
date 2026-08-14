//! Interpolation and imputation for functional data (fdars.represent submodule).
//!
//! Exposes spline interpolation with configurable extrapolation policy and
//! NaN imputation via fdars-core 0.17.0 helpers. All matrix returns route
//! through `convert::fdmatrix_to_numpy2d` to guard the column-major (#33)
//! transposition class.

use crate::convert::*;
use numpy::{PyArray2, PyReadonlyArray1, PyReadonlyArray2};
use pyo3::prelude::*;

/// Interpolate functional data onto a new set of query points using B-splines.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Functional data matrix, shape (n, m). Rows are observations.
/// argvals : numpy.ndarray
///     Original evaluation points, length m. Must be sorted.
/// query_points : numpy.ndarray
///     Points to evaluate at. Must lie within ``[argvals[0], argvals[-1]]``.
/// order : int, optional
///     B-spline order (1=linear, 4=cubic, default 4). Must be in ``[1, m)``.
///
/// Returns
/// -------
/// numpy.ndarray
///     Interpolated data, shape (n, len(query_points)).
///
/// Raises
/// ------
/// ValueError
///     If query points lie outside the domain, order is invalid, or argvals
///     length does not match the data columns.
#[pyfunction]
#[pyo3(signature = (data, argvals, query_points, order=4))]
pub fn spline_interpolate<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    query_points: PyReadonlyArray1<'py, f64>,
    order: usize,
) -> PyResult<Bound<'py, PyArray2<f64>>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let qp = numpy1d_to_vec(query_points);
    let result = to_pyresult(fdars_core::spline_interpolate(&mat, &av, &qp, order))?;
    Ok(fdmatrix_to_numpy2d(py, &result))
}

/// Interpolate functional data with explicit extrapolation control (spline variant).
///
/// Like ``spline_interpolate`` but applies `policy` for query points that fall
/// outside the domain ``[argvals[0], argvals[-1]]``.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Functional data matrix, shape (n, m).
/// argvals : numpy.ndarray
///     Original evaluation points, length m. Must be sorted.
/// query_points : numpy.ndarray
///     Points to evaluate at (may include out-of-range values).
/// policy : str, optional
///     One of ``'boundary'``, ``'exception'``, ``'fill'``, ``'periodic'``.
///     Default ``'exception'``.
/// fill_value : float, optional
///     Constant to use for out-of-domain cells when ``policy='fill'``.
///     Default 0.0.
/// order : int, optional
///     B-spline order (default 4).
///
/// Returns
/// -------
/// numpy.ndarray
///     Interpolated data, shape (n, len(query_points)).
///
/// Raises
/// ------
/// ValueError
///     If policy is unknown, or ``policy='exception'`` and a query point is
///     out of domain, or any other argument is invalid.
#[pyfunction]
#[pyo3(signature = (data, argvals, query_points, policy="exception", fill_value=0.0, order=4))]
pub fn spline_interpolate_with_policy<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    query_points: PyReadonlyArray1<'py, f64>,
    policy: &str,
    fill_value: f64,
    order: usize,
) -> PyResult<Bound<'py, PyArray2<f64>>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let qp = numpy1d_to_vec(query_points);
    let ep = parse_extrapolation_policy(policy, fill_value)?;
    let result =
        to_pyresult(fdars_core::spline_interpolate_with_policy(&mat, &av, &qp, order, ep))?;
    Ok(fdmatrix_to_numpy2d(py, &result))
}

/// Interpolate functional data with explicit extrapolation control (linear/cubic variant).
///
/// Uses piecewise linear or cubic Hermite interpolation (not B-splines). Applies
/// `policy` for query points outside the domain.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Functional data matrix, shape (n, m).
/// argvals : numpy.ndarray
///     Original evaluation points, length m. Must be sorted.
/// query_points : numpy.ndarray
///     Points to evaluate at (may include out-of-range values).
/// policy : str, optional
///     One of ``'boundary'``, ``'exception'``, ``'fill'``, ``'periodic'``.
///     Default ``'exception'``.
/// fill_value : float, optional
///     Constant to use for out-of-domain cells when ``policy='fill'``.
///     Default 0.0.
/// method : str, optional
///     Interpolation method: ``'linear'`` (default) or ``'cubic_hermite'``.
///
/// Returns
/// -------
/// numpy.ndarray
///     Interpolated data, shape (n, len(query_points)).
///
/// Raises
/// ------
/// ValueError
///     If policy or method is unknown, or ``policy='exception'`` and a query
///     point is out of domain.
#[pyfunction]
#[pyo3(signature = (data, argvals, query_points, policy="exception", fill_value=0.0, method="linear"))]
pub fn fdata_interpolate_with_policy<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    query_points: PyReadonlyArray1<'py, f64>,
    policy: &str,
    fill_value: f64,
    method: &str,
) -> PyResult<Bound<'py, PyArray2<f64>>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let qp = numpy1d_to_vec(query_points);
    let ep = parse_extrapolation_policy(policy, fill_value)?;
    let im = parse_interpolation_method(method)?;
    let result =
        to_pyresult(fdars_core::fdata_interpolate_with_policy(&mat, &av, &qp, im, ep))?;
    Ok(fdmatrix_to_numpy2d(py, &result))
}

/// Impute NaN values in a functional data matrix.
///
/// Returns a new matrix with NaN entries replaced according to `method`.
/// Non-NaN entries are copied through unchanged.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Functional data matrix, shape (n, m). May contain NaN.
/// argvals : numpy.ndarray
///     Evaluation points, length m. Must be sorted.
/// method : str, optional
///     One of ``'linear'`` (default), ``'mean'``, ``'constant'``.
/// constant_value : float, optional
///     Replacement value when ``method='constant'``. Default 0.0.
///
/// Returns
/// -------
/// numpy.ndarray
///     Imputed matrix, shape (n, m), no NaN entries.
///
/// Raises
/// ------
/// ValueError
///     If method is unknown, argvals length mismatches, or any curve consists
///     entirely of NaN values.
#[pyfunction]
#[pyo3(signature = (data, argvals, method="linear", constant_value=0.0))]
pub fn impute_missing_values<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    method: &str,
    constant_value: f64,
) -> PyResult<Bound<'py, PyArray2<f64>>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let im = parse_imputation_method(method, constant_value)?;
    let result = to_pyresult(fdars_core::impute_missing_values(&mat, &av, im))?;
    Ok(fdmatrix_to_numpy2d(py, &result))
}

// ── Helpers ────────────────────────────────────────────────────────────────

fn parse_extrapolation_policy(
    policy: &str,
    fill_value: f64,
) -> PyResult<fdars_core::ExtrapolationPolicy> {
    match policy {
        "boundary" => Ok(fdars_core::ExtrapolationPolicy::Boundary),
        "exception" => Ok(fdars_core::ExtrapolationPolicy::Exception),
        "fill" => Ok(fdars_core::ExtrapolationPolicy::Fill(fill_value)),
        "periodic" => Ok(fdars_core::ExtrapolationPolicy::Periodic),
        _ => Err(pyo3::exceptions::PyValueError::new_err(
            "policy must be 'boundary', 'exception', 'fill', or 'periodic'",
        )),
    }
}

fn parse_interpolation_method(method: &str) -> PyResult<fdars_core::InterpolationMethod> {
    match method {
        "linear" => Ok(fdars_core::InterpolationMethod::Linear),
        "cubic_hermite" => Ok(fdars_core::InterpolationMethod::CubicHermite),
        _ => Err(pyo3::exceptions::PyValueError::new_err(
            "method must be 'linear' or 'cubic_hermite'",
        )),
    }
}

fn parse_imputation_method(method: &str, constant_value: f64) -> PyResult<fdars_core::ImputationMethod> {
    match method {
        "linear" => Ok(fdars_core::ImputationMethod::Linear),
        "mean" => Ok(fdars_core::ImputationMethod::Mean),
        "constant" => Ok(fdars_core::ImputationMethod::Constant(constant_value)),
        _ => Err(pyo3::exceptions::PyValueError::new_err(
            "method must be 'linear', 'mean', or 'constant'",
        )),
    }
}

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(spline_interpolate, m)?)?;
    m.add_function(wrap_pyfunction!(spline_interpolate_with_policy, m)?)?;
    m.add_function(wrap_pyfunction!(fdata_interpolate_with_policy, m)?)?;
    m.add_function(wrap_pyfunction!(impute_missing_values, m)?)?;
    Ok(())
}
