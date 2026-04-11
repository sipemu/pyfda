//! Nonparametric smoothing for functional data.

use crate::convert::*;
use numpy::{PyArray1, PyReadonlyArray1};
use pyo3::prelude::*;

/// Nadaraya-Watson kernel smoother.
///
/// Parameters
/// ----------
/// x : numpy.ndarray
///     Predictor values, length n.
/// y : numpy.ndarray
///     Response values, length n.
/// x_new : numpy.ndarray
///     Evaluation points.
/// bandwidth : float
///     Kernel bandwidth.
/// kernel : str, optional
///     Kernel type: "gaussian" (default), "epanechnikov", or "tricube".
///
/// Returns
/// -------
/// numpy.ndarray
///     Smoothed values at x_new.
#[pyfunction]
#[pyo3(signature = (x, y, x_new, bandwidth, kernel="gaussian"))]
pub fn nadaraya_watson<'py>(
    py: Python<'py>,
    x: PyReadonlyArray1<'py, f64>,
    y: PyReadonlyArray1<'py, f64>,
    x_new: PyReadonlyArray1<'py, f64>,
    bandwidth: f64,
    kernel: &str,
) -> PyResult<Bound<'py, PyArray1<f64>>> {
    let xv = numpy1d_to_vec(x);
    let yv = numpy1d_to_vec(y);
    let xnv = numpy1d_to_vec(x_new);
    let result = to_pyresult(fdars_core::smoothing::nadaraya_watson(
        &xv, &yv, &xnv, bandwidth, kernel,
    ))?;
    Ok(vec_to_numpy1d(py, result))
}

/// Local linear regression smoother.
///
/// Parameters
/// ----------
/// x : numpy.ndarray
///     Predictor values, length n.
/// y : numpy.ndarray
///     Response values, length n.
/// x_new : numpy.ndarray
///     Evaluation points.
/// bandwidth : float
///     Kernel bandwidth.
/// kernel : str, optional
///     Kernel type: "gaussian" (default), "epanechnikov", or "tricube".
///
/// Returns
/// -------
/// numpy.ndarray
///     Smoothed values at x_new.
#[pyfunction]
#[pyo3(signature = (x, y, x_new, bandwidth, kernel="gaussian"))]
pub fn local_linear<'py>(
    py: Python<'py>,
    x: PyReadonlyArray1<'py, f64>,
    y: PyReadonlyArray1<'py, f64>,
    x_new: PyReadonlyArray1<'py, f64>,
    bandwidth: f64,
    kernel: &str,
) -> PyResult<Bound<'py, PyArray1<f64>>> {
    let xv = numpy1d_to_vec(x);
    let yv = numpy1d_to_vec(y);
    let xnv = numpy1d_to_vec(x_new);
    let result = to_pyresult(fdars_core::smoothing::local_linear(
        &xv, &yv, &xnv, bandwidth, kernel,
    ))?;
    Ok(vec_to_numpy1d(py, result))
}

/// Local polynomial regression smoother.
///
/// Parameters
/// ----------
/// x : numpy.ndarray
///     Predictor values, length n.
/// y : numpy.ndarray
///     Response values, length n.
/// x_new : numpy.ndarray
///     Evaluation points.
/// bandwidth : float
///     Kernel bandwidth.
/// degree : int, optional
///     Polynomial degree (default 1).
/// kernel : str, optional
///     Kernel type: "gaussian" (default), "epanechnikov", or "tricube".
///
/// Returns
/// -------
/// numpy.ndarray
///     Smoothed values at x_new.
#[pyfunction]
#[pyo3(signature = (x, y, x_new, bandwidth, degree=1, kernel="gaussian"))]
pub fn local_polynomial<'py>(
    py: Python<'py>,
    x: PyReadonlyArray1<'py, f64>,
    y: PyReadonlyArray1<'py, f64>,
    x_new: PyReadonlyArray1<'py, f64>,
    bandwidth: f64,
    degree: usize,
    kernel: &str,
) -> PyResult<Bound<'py, PyArray1<f64>>> {
    let xv = numpy1d_to_vec(x);
    let yv = numpy1d_to_vec(y);
    let xnv = numpy1d_to_vec(x_new);
    let result = to_pyresult(fdars_core::smoothing::local_polynomial(
        &xv, &yv, &xnv, bandwidth, degree, kernel,
    ))?;
    Ok(vec_to_numpy1d(py, result))
}

/// K-nearest neighbors smoother.
///
/// Parameters
/// ----------
/// x : numpy.ndarray
///     Predictor values, length n.
/// y : numpy.ndarray
///     Response values, length n.
/// x_new : numpy.ndarray
///     Evaluation points.
/// k : int
///     Number of nearest neighbors.
///
/// Returns
/// -------
/// numpy.ndarray
///     Smoothed values at x_new.
#[pyfunction]
pub fn knn_smoother<'py>(
    py: Python<'py>,
    x: PyReadonlyArray1<'py, f64>,
    y: PyReadonlyArray1<'py, f64>,
    x_new: PyReadonlyArray1<'py, f64>,
    k: usize,
) -> PyResult<Bound<'py, PyArray1<f64>>> {
    let xv = numpy1d_to_vec(x);
    let yv = numpy1d_to_vec(y);
    let xnv = numpy1d_to_vec(x_new);
    let result = to_pyresult(fdars_core::smoothing::knn_smoother(
        &xv, &yv, &xnv, k,
    ))?;
    Ok(vec_to_numpy1d(py, result))
}

/// Optimal bandwidth selection via cross-validation.
///
/// Parameters
/// ----------
/// x : numpy.ndarray
///     Predictor values, length n.
/// y : numpy.ndarray
///     Response values, length n.
/// criterion : str, optional
///     "gcv" (default) or "cv".
/// kernel : str, optional
///     Kernel type: "gaussian" (default), "epanechnikov", or "tricube".
/// n_grid : int, optional
///     Number of grid points for search (default 50).
/// h_min : float or None, optional
///     Minimum bandwidth. If None, auto-selected.
/// h_max : float or None, optional
///     Maximum bandwidth. If None, auto-selected.
///
/// Returns
/// -------
/// dict
///     Dictionary with keys: h_opt, criterion, value
#[pyfunction]
#[pyo3(signature = (x, y, criterion="gcv", kernel="gaussian", n_grid=50, h_min=None, h_max=None))]
pub fn optim_bandwidth<'py>(
    py: Python<'py>,
    x: PyReadonlyArray1<'py, f64>,
    y: PyReadonlyArray1<'py, f64>,
    criterion: &str,
    kernel: &str,
    n_grid: usize,
    h_min: Option<f64>,
    h_max: Option<f64>,
) -> PyResult<Bound<'py, PyAny>> {
    let xv = numpy1d_to_vec(x);
    let yv = numpy1d_to_vec(y);
    let crit = match criterion {
        "cv" => fdars_core::smoothing::CvCriterion::Cv,
        "gcv" => fdars_core::smoothing::CvCriterion::Gcv,
        _ => {
            return Err(pyo3::exceptions::PyValueError::new_err(
                "criterion must be 'cv' or 'gcv'",
            ))
        }
    };
    let h_range = match (h_min, h_max) {
        (Some(lo), Some(hi)) => Some((lo, hi)),
        _ => None,
    };
    let result = fdars_core::smoothing::optim_bandwidth(
        &xv, &yv, h_range, crit, kernel, n_grid,
    );
    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("h_opt", result.h_opt)?;
    let crit_str = match result.criterion {
        fdars_core::smoothing::CvCriterion::Cv => "cv",
        fdars_core::smoothing::CvCriterion::Gcv => "gcv",
    };
    dict.set_item("criterion", crit_str)?;
    dict.set_item("value", result.value)?;
    Ok(dict.into_any())
}

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(nadaraya_watson, m)?)?;
    m.add_function(wrap_pyfunction!(local_linear, m)?)?;
    m.add_function(wrap_pyfunction!(local_polynomial, m)?)?;
    m.add_function(wrap_pyfunction!(knn_smoother, m)?)?;
    m.add_function(wrap_pyfunction!(optim_bandwidth, m)?)?;
    Ok(())
}
