//! Statistical Process Monitoring for functional data.

use crate::convert::*;
use numpy::{PyArray1, PyReadonlyArray1, PyReadonlyArray2};
use pyo3::prelude::*;

/// SPM Phase I estimation.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     In-control data, shape (n, m).
/// argvals : numpy.ndarray
///     Evaluation points, length m.
/// ncomp : int, optional
///     Number of FPC components (default 3).
/// alpha : float, optional
///     Significance level (default 0.05).
///
/// Returns
/// -------
/// dict
///     t2 (n,), spe (n,), t2_limit, spe_limit,
///     mean (m,), loadings (m, ncomp), eigenvalues (ncomp,).
#[pyfunction]
#[pyo3(signature = (data, argvals, ncomp=3, alpha=0.05))]
pub fn spm_phase1<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    ncomp: usize,
    alpha: f64,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let config = fdars_core::spm::SpmConfig {
        ncomp,
        alpha,
        ..Default::default()
    };
    let result = to_pyresult(fdars_core::spm::spm_phase1(&mat, &av, &config))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("t2", vec_to_numpy1d(py, result.t2_phase1))?;
    dict.set_item("spe", vec_to_numpy1d(py, result.spe_phase1))?;
    dict.set_item("t2_limit", result.t2_limit.ucl)?;
    dict.set_item("spe_limit", result.spe_limit.ucl)?;
    dict.set_item("mean", vec_to_numpy1d(py, result.fpca.mean.clone()))?;
    dict.set_item("loadings", fdmatrix_to_numpy2d(py, &result.fpca.rotation))?;
    dict.set_item("weights", vec_to_numpy1d(py, result.fpca.weights.clone()))?;
    dict.set_item(
        "eigenvalues",
        vec_to_numpy1d(py, result.eigenvalues.clone()),
    )?;
    Ok(dict)
}

/// SPM Phase II monitoring.
///
/// Parameters
/// ----------
/// mean : numpy.ndarray
///     FPCA mean function, length m.
/// loadings : numpy.ndarray
///     FPCA rotation matrix, shape (m, ncomp).
/// weights : numpy.ndarray
///     FPCA integration weights, length m.
/// eigenvalues : numpy.ndarray
///     Eigenvalues, length ncomp.
/// t2_limit : float
///     T-squared upper control limit.
/// spe_limit : float
///     SPE upper control limit.
/// new_data : numpy.ndarray
///     New observations, shape (n_new, m).
/// argvals : numpy.ndarray
///     Evaluation points, length m.
///
/// Returns
/// -------
/// dict
///     t2 (n_new,), spe (n_new,),
///     t2_alarm (bool array), spe_alarm (bool array).
#[pyfunction]
pub fn spm_monitor<'py>(
    py: Python<'py>,
    mean: PyReadonlyArray1<'py, f64>,
    loadings: PyReadonlyArray2<'py, f64>,
    weights: PyReadonlyArray1<'py, f64>,
    eigenvalues: PyReadonlyArray1<'py, f64>,
    t2_limit: f64,
    spe_limit: f64,
    new_data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mn = numpy1d_to_vec(mean);
    let ld = numpy2d_to_fdmatrix(loadings)?;
    let wt = numpy1d_to_vec(weights);
    let ev = numpy1d_to_vec(eigenvalues);
    let nd = numpy2d_to_fdmatrix(new_data)?;
    let av = numpy1d_to_vec(argvals);

    let result = to_pyresult(fdars_core::spm::spm_monitor_from_fields(
        &mn, &ld, &wt, &ev, t2_limit, spe_limit, &nd, &av,
    ))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("t2", vec_to_numpy1d(py, result.t2))?;
    dict.set_item("spe", vec_to_numpy1d(py, result.spe))?;
    dict.set_item("t2_alarm", bool_vec_to_numpy1d(py, result.t2_alarm))?;
    dict.set_item("spe_alarm", bool_vec_to_numpy1d(py, result.spe_alarm))?;
    Ok(dict)
}

/// Hotelling T^2 statistic.
///
/// Parameters
/// ----------
/// scores : numpy.ndarray
///     FPC scores, shape (n, p).
/// eigenvalues : numpy.ndarray
///     Eigenvalues, length p.
///
/// Returns
/// -------
/// numpy.ndarray
///     T^2 statistics, length n.
#[pyfunction]
pub fn hotelling_t2<'py>(
    py: Python<'py>,
    scores: PyReadonlyArray2<'py, f64>,
    eigenvalues: PyReadonlyArray1<'py, f64>,
) -> PyResult<Bound<'py, PyArray1<f64>>> {
    let sc = numpy2d_to_fdmatrix(scores)?;
    let ev = numpy1d_to_vec(eigenvalues);
    let result = to_pyresult(fdars_core::spm::hotelling_t2(&sc, &ev))?;
    Ok(vec_to_numpy1d(py, result))
}

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(spm_phase1, m)?)?;
    m.add_function(wrap_pyfunction!(spm_monitor, m)?)?;
    m.add_function(wrap_pyfunction!(hotelling_t2, m)?)?;
    Ok(())
}
