//! Functional time series bindings.
//!
//! Exposes the `fdars.fts` submodule with bindings for fdars-core 0.33's
//! functional time series module: FTSM model fit/forecast, functional ACF/PACF,
//! stationarity test, long-run covariance, spectral density, and dynamic FPCA.
//!
//! Plan 67-01 (tracer): `ftsm` bound.
//! Plan 67-02: `ftsm_forecast`, `ftsm_forecast_multistep`, `ftsm_update`, `fplsr` added.
//! Plans 67-03/04 will extend `register()` with the remaining 8 functions.

use crate::convert::*;
use numpy::{PyReadonlyArray1, PyReadonlyArray2};
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};

// ---------------------------------------------------------------------------
// Group A: Forecasting functions
// ---------------------------------------------------------------------------

/// Fit a Functional Time Series Model (FTSM) via FPCA + Yule-Walker AR fitting.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Time-ordered functional data, shape (n_obs, n_points).
///     Rows are time steps; columns are grid evaluation points.
/// argvals : numpy.ndarray
///     Evaluation grid, length n_points. Must match data columns exactly.
/// ncomp : int, optional
///     Number of FPC components to retain (default 3). Clamped internally to
///     min(ncomp, n_obs-1, n_points). Must be >= 1.
///
/// Returns
/// -------
/// dict
///     mean (n_points,), rotation (n_points, ncomp), scores (n_obs, ncomp),
///     fitted (n_obs, n_points), weights (n_points,), ncomp (int),
///     ar_models (list of dict with keys order, phi, sigma2).
///
/// Raises
/// ------
/// ValueError
///     If ncomp < 1, argvals length != n_points, or n_obs is too small.
#[pyfunction]
#[pyo3(signature = (data, argvals, ncomp=3))]
pub fn ftsm<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    ncomp: usize,
) -> PyResult<Bound<'py, PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let result = to_pyresult(fdars_core::fts::ftsm(&mat, ncomp, &av))?;
    ftsm_result_to_dict(py, &result)
}

// ---------------------------------------------------------------------------
// Private helper: convert FtsmResult to PyDict (reused by ftsm_update)
// ---------------------------------------------------------------------------

fn ftsm_result_to_dict<'py>(
    py: Python<'py>,
    result: &fdars_core::fts::FtsmResult,
) -> PyResult<Bound<'py, PyDict>> {
    let dict = PyDict::new(py);
    dict.set_item("mean", vec_to_numpy1d(py, result.mean.clone()))?;
    dict.set_item("rotation", fdmatrix_to_numpy2d(py, &result.rotation))?;
    dict.set_item("scores", fdmatrix_to_numpy2d(py, &result.scores))?;
    dict.set_item("fitted", fdmatrix_to_numpy2d(py, &result.fitted))?;
    dict.set_item("weights", vec_to_numpy1d(py, result.weights.clone()))?;
    dict.set_item("ncomp", result.ncomp)?;

    let py_ar_list = PyList::empty(py);
    for ar in &result.ar_models {
        let ar_dict = PyDict::new(py);
        ar_dict.set_item("order", ar.order)?;
        ar_dict.set_item("phi", vec_to_numpy1d(py, ar.phi.clone()))?;
        ar_dict.set_item("sigma2", ar.sigma2)?;
        py_ar_list.append(ar_dict)?;
    }
    dict.set_item("ar_models", py_ar_list)?;

    Ok(dict)
}

/// Fit an FTSM and produce a single- or multi-horizon forecast (single-step variant).
///
/// Uses the combined-function pattern: fits `ftsm` internally then calls
/// `ftsm_forecast`. Python cannot pass a Rust `FtsmResult` directly.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Time-ordered functional data, shape (n_obs, n_points).
/// argvals : numpy.ndarray
///     Evaluation grid, length n_points.
/// h : int, optional
///     Forecast horizon (default 1). Must be >= 1.
/// ncomp : int, optional
///     Number of FPC components to retain (default 3).
///
/// Returns
/// -------
/// dict
///     forecast (h, n_points), h (int).
///
/// Raises
/// ------
/// ValueError
///     If h < 1, ncomp < 1, or data is invalid.
#[pyfunction]
#[pyo3(signature = (data, argvals, h=1, ncomp=3))]
pub fn ftsm_forecast<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    h: usize,
    ncomp: usize,
) -> PyResult<Bound<'py, PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let fit = to_pyresult(fdars_core::fts::ftsm(&mat, ncomp, &av))?;
    let result = to_pyresult(fdars_core::fts::ftsm_forecast(&fit, h, &av))?;

    let dict = PyDict::new(py);
    dict.set_item("forecast", fdmatrix_to_numpy2d(py, &result.forecast))?;
    dict.set_item("h", result.h)?;
    Ok(dict)
}

/// Fit an FTSM and produce a multi-step forecast (iterative multi-step variant).
///
/// Uses the combined-function pattern: fits `ftsm` internally then calls
/// `ftsm_forecast_multistep`. At h=1, output is bit-identical to `ftsm_forecast`.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Time-ordered functional data, shape (n_obs, n_points).
/// argvals : numpy.ndarray
///     Evaluation grid, length n_points.
/// h : int, optional
///     Forecast horizon (default 5). Must be >= 1.
/// ncomp : int, optional
///     Number of FPC components to retain (default 3).
///
/// Returns
/// -------
/// dict
///     forecast (h, n_points), h (int).
///
/// Raises
/// ------
/// ValueError
///     If h < 1, ncomp < 1, or data is invalid.
#[pyfunction]
#[pyo3(signature = (data, argvals, h=5, ncomp=3))]
pub fn ftsm_forecast_multistep<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    h: usize,
    ncomp: usize,
) -> PyResult<Bound<'py, PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let fit = to_pyresult(fdars_core::fts::ftsm(&mat, ncomp, &av))?;
    let result = to_pyresult(fdars_core::fts::ftsm_forecast_multistep(&fit, h, &av))?;

    let dict = PyDict::new(py);
    dict.set_item("forecast", fdmatrix_to_numpy2d(py, &result.forecast))?;
    dict.set_item("h", result.h)?;
    Ok(dict)
}

/// Online update of an FTSM with one or more new curves.
///
/// Uses the combined-function pattern: re-fits `ftsm` on `data` (freezing the
/// mean and rotation), then calls `ftsm_update` to append `new_curve` and
/// re-fit AR models on the extended score series.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Original time-ordered functional data, shape (n_obs, n_points).
/// new_curve : numpy.ndarray
///     New observation(s) to append, shape (k_new, n_points). k_new >= 1.
/// argvals : numpy.ndarray
///     Evaluation grid, length n_points.
/// ncomp : int, optional
///     Number of FPC components to retain (default 3).
///
/// Returns
/// -------
/// dict
///     Updated FtsmResult with same 7 keys as `ftsm`: mean, rotation, scores
///     (n_obs+k_new, ncomp), fitted, weights, ncomp, ar_models.
///
/// Raises
/// ------
/// ValueError
///     If ncomp < 1, argvals mismatch, or new_curve has wrong n_points.
#[pyfunction]
#[pyo3(signature = (data, new_curve, argvals, ncomp=3))]
pub fn ftsm_update<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    new_curve: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    ncomp: usize,
) -> PyResult<Bound<'py, PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let new_mat = numpy2d_to_fdmatrix(new_curve)?;
    let av = numpy1d_to_vec(argvals);
    let fit = to_pyresult(fdars_core::fts::ftsm(&mat, ncomp, &av))?;
    let result = to_pyresult(fdars_core::fts::ftsm_update(&fit, &new_mat, &av))?;
    ftsm_result_to_dict(py, &result)
}

// ---------------------------------------------------------------------------
// Module registration
// ---------------------------------------------------------------------------

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(ftsm, m)?)?;
    m.add_function(wrap_pyfunction!(ftsm_forecast, m)?)?;
    m.add_function(wrap_pyfunction!(ftsm_forecast_multistep, m)?)?;
    m.add_function(wrap_pyfunction!(ftsm_update, m)?)?;
    // Plans 67-03/04 will append remaining wrap_pyfunction! lines here:
    //   fplsr, spectral_density, dpca, dpca_reconstruct,
    //   functional_acf, functional_pacf, functional_difference,
    //   stationarity_test, long_run_covariance
    Ok(())
}
