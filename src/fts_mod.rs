//! Functional time series bindings.
//!
//! Exposes the `fdars.fts` submodule with bindings for fdars-core 0.33's
//! functional time series module: FTSM model fit/forecast, functional ACF/PACF,
//! stationarity test, long-run covariance, spectral density, and dynamic FPCA.
//!
//! Plan 67-01 (tracer): only `ftsm` is bound here.
//! Plans 67-02/03/04 will extend `register()` with the remaining 12 functions.

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

    let dict = PyDict::new(py);
    dict.set_item("mean", vec_to_numpy1d(py, result.mean))?;
    dict.set_item("rotation", fdmatrix_to_numpy2d(py, &result.rotation))?;
    dict.set_item("scores", fdmatrix_to_numpy2d(py, &result.scores))?;
    dict.set_item("fitted", fdmatrix_to_numpy2d(py, &result.fitted))?;
    dict.set_item("weights", vec_to_numpy1d(py, result.weights))?;
    dict.set_item("ncomp", result.ncomp)?;

    // Build ar_models as a Python list of dicts (one per component)
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

// ---------------------------------------------------------------------------
// Module registration
// ---------------------------------------------------------------------------

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(ftsm, m)?)?;
    // Plans 67-02/03/04 will append remaining wrap_pyfunction! lines here:
    //   ftsm_forecast, ftsm_forecast_multistep, ftsm_update, fplsr,
    //   spectral_density, dpca, dpca_reconstruct,
    //   functional_acf, functional_pacf, functional_difference,
    //   stationarity_test, long_run_covariance
    Ok(())
}
