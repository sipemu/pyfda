//! Outlier detection for functional data.

use crate::convert::*;
use numpy::PyReadonlyArray2;
use pyo3::prelude::*;

/// LRT-based outlier detection with bootstrap.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Data, shape (n, m).
/// alpha : float, optional
///     Significance level (default 0.05).
/// n_bootstrap : int, optional
///     Number of bootstrap samples (default 200).
/// trim : float, optional
///     Trimming proportion (default 0.1).
/// smo : float, optional
///     Smoothing parameter (default 0.02).
///
/// Returns
/// -------
/// dict
///     outliers (bool array), threshold.
#[pyfunction]
#[pyo3(signature = (data, alpha=0.05, n_bootstrap=200, trim=0.1, smo=0.02))]
pub fn detect_outliers_lrt<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    alpha: f64,
    n_bootstrap: usize,
    trim: f64,
    smo: f64,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let percentile = 1.0 - alpha;
    let threshold = fdars_core::outliers::outliers_threshold_lrt(
        &mat,
        n_bootstrap,
        smo,
        trim,
        42,
        percentile,
    );
    let outliers = fdars_core::outliers::detect_outliers_lrt(&mat, threshold, trim);

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("outliers", bool_vec_to_numpy1d(py, outliers))?;
    dict.set_item("threshold", threshold)?;
    Ok(dict)
}

/// Outliergram (MEI vs MBD plot).
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Data, shape (n, m).
/// factor : float, optional
///     Outlier factor (default 1.5).
///
/// Returns
/// -------
/// dict
///     mei (n,), mbd (n,), outliers (bool array).
#[pyfunction]
#[pyo3(signature = (data, factor=1.5))]
pub fn outliergram<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    factor: f64,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let result = to_pyresult(fdars_core::outliers::outliergram(&mat, factor))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("mei", vec_to_numpy1d(py, result.mei))?;
    dict.set_item("mbd", vec_to_numpy1d(py, result.mbd))?;
    dict.set_item("outliers", bool_vec_to_numpy1d(py, result.outlier_flags))?;
    Ok(dict)
}

/// Magnitude-shape outlyingness.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Data, shape (n, m).
///
/// Returns
/// -------
/// dict
///     magnitude (n,), shape (n,).
#[pyfunction]
pub fn magnitude_shape<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let result = to_pyresult(fdars_core::outliers::magnitude_shape_outlyingness(&mat))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("magnitude", vec_to_numpy1d(py, result.magnitude))?;
    dict.set_item("shape", vec_to_numpy1d(py, result.shape))?;
    Ok(dict)
}

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(detect_outliers_lrt, m)?)?;
    m.add_function(wrap_pyfunction!(outliergram, m)?)?;
    m.add_function(wrap_pyfunction!(magnitude_shape, m)?)?;
    Ok(())
}
