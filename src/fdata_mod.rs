//! Functional data operations: mean, center, derivatives, norms, median.

use crate::convert::*;
use numpy::{PyArray1, PyArray2, PyReadonlyArray1, PyReadonlyArray2};
use pyo3::prelude::*;

/// Compute the pointwise mean of 1D functional data.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     2D array of shape (n_obs, n_points).
///
/// Returns
/// -------
/// numpy.ndarray
///     1D array of length n_points.
#[pyfunction]
pub fn mean_1d<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
) -> PyResult<Bound<'py, PyArray1<f64>>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let result = fdars_core::fdata::mean_1d(&mat);
    Ok(vec_to_numpy1d(py, result))
}

/// Compute the pointwise mean of 2D functional data.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     2D array of shape (n_obs, m1*m2).
///
/// Returns
/// -------
/// numpy.ndarray
///     1D array of length m1*m2.
#[pyfunction]
pub fn mean_2d<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
) -> PyResult<Bound<'py, PyArray1<f64>>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let result = fdars_core::fdata::mean_2d(&mat);
    Ok(vec_to_numpy1d(py, result))
}

/// Center functional data by subtracting the pointwise mean.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     2D array of shape (n_obs, n_points).
///
/// Returns
/// -------
/// numpy.ndarray
///     Centered data of shape (n_obs, n_points).
#[pyfunction]
pub fn center_1d<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
) -> PyResult<Bound<'py, PyArray2<f64>>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let result = fdars_core::fdata::center_1d(&mat);
    Ok(fdmatrix_to_numpy2d(py, &result))
}

/// Compute numerical derivatives of 1D functional data.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     2D array of shape (n_obs, n_points).
/// argvals : numpy.ndarray
///     1D array of evaluation points.
/// nderiv : int, optional
///     Number of derivatives to compute (default 1).
///
/// Returns
/// -------
/// numpy.ndarray
///     Derivative data of shape (n_obs, n_points).
#[pyfunction]
#[pyo3(signature = (data, argvals, nderiv=1))]
pub fn deriv_1d<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    nderiv: usize,
) -> PyResult<Bound<'py, PyArray2<f64>>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let result = fdars_core::fdata::deriv_1d(&mat, &av, nderiv);
    Ok(fdmatrix_to_numpy2d(py, &result))
}

/// Compute numerical derivatives of 2D functional data.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     2D array of shape (n_obs, m1*m2).
/// argvals_s : numpy.ndarray
///     Grid points in first dimension (length m1).
/// argvals_t : numpy.ndarray
///     Grid points in second dimension (length m2).
///
/// Returns
/// -------
/// tuple
///     (ds, dt, dsdt) -- partial derivatives w.r.t. s, t, and mixed.
#[pyfunction]
pub fn deriv_2d<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals_s: PyReadonlyArray1<'py, f64>,
    argvals_t: PyReadonlyArray1<'py, f64>,
) -> PyResult<(
    Bound<'py, PyArray2<f64>>,
    Bound<'py, PyArray2<f64>>,
    Bound<'py, PyArray2<f64>>,
)> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let avs = numpy1d_to_vec(argvals_s.clone());
    let avt = numpy1d_to_vec(argvals_t.clone());
    let m1 = avs.len();
    let m2 = avt.len();
    let result = fdars_core::fdata::deriv_2d(&mat, &avs, &avt, m1, m2).ok_or_else(|| {
        pyo3::exceptions::PyValueError::new_err(
            "deriv_2d failed: check that data columns == m1*m2 and grid sizes >= 2",
        )
    })?;
    Ok((
        fdmatrix_to_numpy2d(py, &result.ds),
        fdmatrix_to_numpy2d(py, &result.dt),
        fdmatrix_to_numpy2d(py, &result.dsdt),
    ))
}

/// Compute Lp norms of 1D functional data.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     2D array of shape (n_obs, n_points).
/// argvals : numpy.ndarray
///     1D array of evaluation points for integration.
/// p : float, optional
///     Order of the norm (default 2.0 for L2).
///
/// Returns
/// -------
/// numpy.ndarray
///     1D array of Lp norms, length n_obs.
#[pyfunction]
#[pyo3(signature = (data, argvals, p=2.0))]
pub fn norm_lp_1d<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    p: f64,
) -> PyResult<Bound<'py, PyArray1<f64>>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let result = fdars_core::fdata::norm_lp_1d(&mat, &av, p);
    Ok(vec_to_numpy1d(py, result))
}

/// Compute the geometric (L1) median of 1D functional data.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     2D array of shape (n_obs, n_points).
/// argvals : numpy.ndarray
///     1D array of evaluation points for integration.
/// max_iter : int, optional
///     Maximum iterations (default 100).
/// tol : float, optional
///     Convergence tolerance (default 1e-8).
///
/// Returns
/// -------
/// numpy.ndarray
///     1D array of length n_points.
#[pyfunction]
#[pyo3(signature = (data, argvals, max_iter=100, tol=1e-8))]
pub fn geometric_median_1d<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    max_iter: usize,
    tol: f64,
) -> PyResult<Bound<'py, PyArray1<f64>>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let result = fdars_core::fdata::geometric_median_1d(&mat, &av, max_iter, tol);
    Ok(vec_to_numpy1d(py, result))
}

/// Compute the geometric (L1) median of 2D functional data.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     2D array of shape (n_obs, m1*m2).
/// argvals_s : numpy.ndarray
///     Grid points in first dimension.
/// argvals_t : numpy.ndarray
///     Grid points in second dimension.
/// max_iter : int, optional
///     Maximum iterations (default 100).
/// tol : float, optional
///     Convergence tolerance (default 1e-8).
///
/// Returns
/// -------
/// numpy.ndarray
///     1D array of length m1*m2.
#[pyfunction]
#[pyo3(signature = (data, argvals_s, argvals_t, max_iter=100, tol=1e-8))]
pub fn geometric_median_2d<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals_s: PyReadonlyArray1<'py, f64>,
    argvals_t: PyReadonlyArray1<'py, f64>,
    max_iter: usize,
    tol: f64,
) -> PyResult<Bound<'py, PyArray1<f64>>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let avs = numpy1d_to_vec(argvals_s);
    let avt = numpy1d_to_vec(argvals_t);
    let result = fdars_core::fdata::geometric_median_2d(&mat, &avs, &avt, max_iter, tol);
    Ok(vec_to_numpy1d(py, result))
}

/// Normalize functional data.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     2D array of shape (n_obs, n_points).
/// method : str
///     One of "center", "autoscale", "pareto", "range",
///     "curve_center", "curve_standardize", "curve_range".
///
/// Returns
/// -------
/// numpy.ndarray
///     Normalized data of shape (n_obs, n_points).
#[pyfunction]
#[pyo3(signature = (data, method="center"))]
pub fn normalize<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    method: &str,
) -> PyResult<Bound<'py, PyArray2<f64>>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let norm_method = match method {
        "center" => fdars_core::fdata::NormalizationMethod::Center,
        "autoscale" => fdars_core::fdata::NormalizationMethod::Autoscale,
        "pareto" => fdars_core::fdata::NormalizationMethod::Pareto,
        "range" => fdars_core::fdata::NormalizationMethod::Range,
        "curve_center" => fdars_core::fdata::NormalizationMethod::CurveCenter,
        "curve_standardize" => fdars_core::fdata::NormalizationMethod::CurveStandardize,
        "curve_range" => fdars_core::fdata::NormalizationMethod::CurveRange,
        _ => {
            return Err(pyo3::exceptions::PyValueError::new_err(
                "method must be one of: 'center', 'autoscale', 'pareto', 'range', \
                 'curve_center', 'curve_standardize', 'curve_range'",
            ))
        }
    };
    let result = fdars_core::fdata::normalize(&mat, norm_method);
    Ok(fdmatrix_to_numpy2d(py, &result))
}

/// Register fdata functions on the module.
pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(mean_1d, m)?)?;
    m.add_function(wrap_pyfunction!(mean_2d, m)?)?;
    m.add_function(wrap_pyfunction!(center_1d, m)?)?;
    m.add_function(wrap_pyfunction!(deriv_1d, m)?)?;
    m.add_function(wrap_pyfunction!(deriv_2d, m)?)?;
    m.add_function(wrap_pyfunction!(norm_lp_1d, m)?)?;
    m.add_function(wrap_pyfunction!(geometric_median_1d, m)?)?;
    m.add_function(wrap_pyfunction!(geometric_median_2d, m)?)?;
    m.add_function(wrap_pyfunction!(normalize, m)?)?;
    Ok(())
}
