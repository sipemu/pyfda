//! Nonparametric smoothing for functional data.

use crate::convert::*;
use numpy::{PyArray1, PyArray2, PyReadonlyArray1};
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
    let result = to_pyresult(fdars_core::smoothing::knn_smoother(&xv, &yv, &xnv, k))?;
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
    let result = fdars_core::smoothing::optim_bandwidth(&xv, &yv, h_range, crit, kernel, n_grid);
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

/// Smoothing matrix for Nadaraya-Watson.
///
/// Parameters
/// ----------
/// x : numpy.ndarray
///     Predictor values, length n.
/// bandwidth : float
///     Kernel bandwidth.
/// kernel : str, optional
///     Kernel type: "gaussian" (default), "epanechnikov", or "tricube".
///
/// Returns
/// -------
/// numpy.ndarray
///     Smoother matrix S, shape (n, n), such that y_hat = S @ y.
#[pyfunction]
#[pyo3(signature = (x, bandwidth, kernel="gaussian"))]
pub fn smoothing_matrix_nw<'py>(
    py: Python<'py>,
    x: PyReadonlyArray1<'py, f64>,
    bandwidth: f64,
    kernel: &str,
) -> PyResult<Bound<'py, PyArray2<f64>>> {
    let xv = numpy1d_to_vec(x);
    let n = xv.len();
    let flat = to_pyresult(fdars_core::smoothing::smoothing_matrix_nw(
        &xv, bandwidth, kernel,
    ))?;
    // flat is column-major n x n; convert to FdMatrix for reuse of fdmatrix_to_numpy2d
    let mat = fdars_core::matrix::FdMatrix::from_column_major(flat, n, n)
        .map_err(|e| pyo3::exceptions::PyValueError::new_err(e.to_string()))?;
    Ok(fdmatrix_to_numpy2d(py, &mat))
}

/// LOO-CV score for a kernel smoother.
///
/// Parameters
/// ----------
/// x : numpy.ndarray
///     Predictor values, length n.
/// y : numpy.ndarray
///     Response values, length n.
/// bandwidth : float
///     Kernel bandwidth.
/// kernel : str, optional
///     Kernel type (default "gaussian").
///
/// Returns
/// -------
/// float
///     Mean squared LOO prediction error.
#[pyfunction]
#[pyo3(signature = (x, y, bandwidth, kernel="gaussian"))]
pub fn cv_smoother(
    x: PyReadonlyArray1<'_, f64>,
    y: PyReadonlyArray1<'_, f64>,
    bandwidth: f64,
    kernel: &str,
) -> f64 {
    let xv = numpy1d_to_vec(x);
    let yv = numpy1d_to_vec(y);
    fdars_core::smoothing::cv_smoother(&xv, &yv, bandwidth, kernel)
}

/// GCV score for a kernel smoother.
///
/// Parameters
/// ----------
/// x : numpy.ndarray
///     Predictor values, length n.
/// y : numpy.ndarray
///     Response values, length n.
/// bandwidth : float
///     Kernel bandwidth.
/// kernel : str, optional
///     Kernel type (default "gaussian").
///
/// Returns
/// -------
/// float
///     GCV score.
#[pyfunction]
#[pyo3(signature = (x, y, bandwidth, kernel="gaussian"))]
pub fn gcv_smoother(
    x: PyReadonlyArray1<'_, f64>,
    y: PyReadonlyArray1<'_, f64>,
    bandwidth: f64,
    kernel: &str,
) -> f64 {
    let xv = numpy1d_to_vec(x);
    let yv = numpy1d_to_vec(y);
    fdars_core::smoothing::gcv_smoother(&xv, &yv, bandwidth, kernel)
}

/// Global LOO-CV for kNN k selection.
///
/// Parameters
/// ----------
/// x : numpy.ndarray
///     Predictor values, length n.
/// y : numpy.ndarray
///     Response values, length n.
/// max_k : int
///     Maximum k to test.
///
/// Returns
/// -------
/// dict
///     optimal_k, cv_errors (max_k,).
#[pyfunction]
pub fn knn_gcv<'py>(
    py: Python<'py>,
    x: PyReadonlyArray1<'py, f64>,
    y: PyReadonlyArray1<'py, f64>,
    max_k: usize,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let xv = numpy1d_to_vec(x);
    let yv = numpy1d_to_vec(y);
    let result = fdars_core::smoothing::knn_gcv(&xv, &yv, max_k);

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("optimal_k", result.optimal_k)?;
    dict.set_item("cv_errors", vec_to_numpy1d(py, result.cv_errors))?;
    Ok(dict)
}

/// Local (per-observation) LOO-CV for kNN k selection.
///
/// Parameters
/// ----------
/// x : numpy.ndarray
///     Predictor values, length n.
/// y : numpy.ndarray
///     Response values, length n.
/// max_k : int
///     Maximum k to test.
///
/// Returns
/// -------
/// numpy.ndarray
///     Per-observation optimal k values (length n), as i64.
#[pyfunction]
pub fn knn_lcv<'py>(
    py: Python<'py>,
    x: PyReadonlyArray1<'py, f64>,
    y: PyReadonlyArray1<'py, f64>,
    max_k: usize,
) -> Bound<'py, PyArray1<i64>> {
    let xv = numpy1d_to_vec(x);
    let yv = numpy1d_to_vec(y);
    let result = fdars_core::smoothing::knn_lcv(&xv, &yv, max_k);
    usize_vec_to_numpy1d(py, result)
}

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(nadaraya_watson, m)?)?;
    m.add_function(wrap_pyfunction!(local_linear, m)?)?;
    m.add_function(wrap_pyfunction!(local_polynomial, m)?)?;
    m.add_function(wrap_pyfunction!(knn_smoother, m)?)?;
    m.add_function(wrap_pyfunction!(optim_bandwidth, m)?)?;
    // New bindings
    m.add_function(wrap_pyfunction!(smoothing_matrix_nw, m)?)?;
    m.add_function(wrap_pyfunction!(cv_smoother, m)?)?;
    m.add_function(wrap_pyfunction!(gcv_smoother, m)?)?;
    m.add_function(wrap_pyfunction!(knn_gcv, m)?)?;
    m.add_function(wrap_pyfunction!(knn_lcv, m)?)?;
    Ok(())
}
