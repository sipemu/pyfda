//! Tolerance bands and confidence regions.

use crate::convert::*;
use numpy::{PyReadonlyArray1, PyReadonlyArray2};
use pyo3::prelude::*;

/// FPCA-based tolerance band.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Data, shape (n, m).
/// ncomp : int, optional
///     Number of FPC components (default 3).
/// nb : int, optional
///     Number of bootstrap replicates (default 1000).
/// coverage : float, optional
///     Coverage level (default 0.95).
/// seed : int, optional
///     Random seed (default 42).
///
/// Returns
/// -------
/// dict
///     upper (m,), lower (m,), center (m,), half_width (m,).
#[pyfunction]
#[pyo3(signature = (data, ncomp=3, nb=1000, coverage=0.95, seed=42))]
pub fn fpca_tolerance_band<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    ncomp: usize,
    nb: usize,
    coverage: f64,
    seed: u64,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let result = to_pyresult(fdars_core::tolerance::fpca_tolerance_band(
        &mat,
        ncomp,
        nb,
        coverage,
        fdars_core::tolerance::BandType::Simultaneous,
        seed,
    ))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("upper", vec_to_numpy1d(py, result.upper))?;
    dict.set_item("lower", vec_to_numpy1d(py, result.lower))?;
    dict.set_item("center", vec_to_numpy1d(py, result.center))?;
    dict.set_item("half_width", vec_to_numpy1d(py, result.half_width))?;
    Ok(dict)
}

/// Conformal prediction band.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Data, shape (n, m).
/// coverage : float, optional
///     Coverage level (default 0.95).
/// cal_fraction : float, optional
///     Calibration fraction (default 0.25).
/// seed : int, optional
///     Random seed (default 42).
///
/// Returns
/// -------
/// dict
///     upper (m,), lower (m,), center (m,), half_width (m,).
#[pyfunction]
#[pyo3(signature = (data, coverage=0.95, cal_fraction=0.25, seed=42))]
pub fn conformal_prediction_band<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    coverage: f64,
    cal_fraction: f64,
    seed: u64,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let result = fdars_core::tolerance::conformal_prediction_band(
        &mat,
        cal_fraction,
        coverage,
        fdars_core::tolerance::NonConformityScore::SupNorm,
        seed,
    );

    match result {
        Some(band) => {
            let dict = pyo3::types::PyDict::new(py);
            dict.set_item("upper", vec_to_numpy1d(py, band.upper))?;
            dict.set_item("lower", vec_to_numpy1d(py, band.lower))?;
            dict.set_item("center", vec_to_numpy1d(py, band.center))?;
            dict.set_item("half_width", vec_to_numpy1d(py, band.half_width))?;
            Ok(dict)
        }
        None => Err(pyo3::exceptions::PyValueError::new_err(
            "conformal_prediction_band returned None (invalid input)",
        )),
    }
}

/// Simultaneous confidence band (Degras method).
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Data, shape (n, m).
/// argvals : numpy.ndarray
///     Evaluation points, length m.
/// bandwidth : float, optional
///     Bandwidth for kernel smoothing (default 0.0 for auto).
/// nb : int, optional
///     Number of bootstrap samples (default 1000).
/// confidence : float, optional
///     Confidence level (default 0.95).
///
/// Returns
/// -------
/// dict
///     upper (m,), lower (m,), center (m,), half_width (m,).
#[pyfunction]
#[pyo3(signature = (data, argvals, bandwidth=0.0, nb=1000, confidence=0.95))]
pub fn scb_mean_degras<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    bandwidth: f64,
    nb: usize,
    confidence: f64,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    // Use Gaussian multiplier distribution by default
    let result = to_pyresult(fdars_core::tolerance::scb_mean_degras(
        &mat,
        &av,
        bandwidth,
        nb,
        confidence,
        fdars_core::tolerance::MultiplierDistribution::Gaussian,
    ))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("upper", vec_to_numpy1d(py, result.upper))?;
    dict.set_item("lower", vec_to_numpy1d(py, result.lower))?;
    dict.set_item("center", vec_to_numpy1d(py, result.center))?;
    dict.set_item("half_width", vec_to_numpy1d(py, result.half_width))?;
    Ok(dict)
}

/// Functional equivalence test (TOST).
///
/// Parameters
/// ----------
/// data1 : numpy.ndarray
///     First group, shape (n1, m).
/// data2 : numpy.ndarray
///     Second group, shape (n2, m).
/// delta : float
///     Equivalence margin.
/// alpha : float, optional
///     Significance level (default 0.05).
/// nb : int, optional
///     Number of bootstrap replicates (default 1000).
/// seed : int, optional
///     Random seed (default 42).
///
/// Returns
/// -------
/// dict
///     equivalent (bool), p_value, test_statistic.
#[pyfunction]
#[pyo3(signature = (data1, data2, delta, alpha=0.05, nb=1000, seed=42))]
pub fn equivalence_test<'py>(
    py: Python<'py>,
    data1: PyReadonlyArray2<'py, f64>,
    data2: PyReadonlyArray2<'py, f64>,
    delta: f64,
    alpha: f64,
    nb: usize,
    seed: u64,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let m1 = numpy2d_to_fdmatrix(data1)?;
    let m2 = numpy2d_to_fdmatrix(data2)?;
    let result = fdars_core::tolerance::equivalence_test(
        &m1,
        &m2,
        delta,
        alpha,
        nb,
        fdars_core::tolerance::EquivalenceBootstrap::Multiplier(
            fdars_core::tolerance::MultiplierDistribution::Gaussian,
        ),
        seed,
    );

    match result {
        Some(res) => {
            let dict = pyo3::types::PyDict::new(py);
            dict.set_item("equivalent", res.equivalent)?;
            dict.set_item("p_value", res.p_value)?;
            dict.set_item("test_statistic", res.test_statistic)?;
            Ok(dict)
        }
        None => Err(pyo3::exceptions::PyValueError::new_err(
            "equivalence_test returned None (invalid input)",
        )),
    }
}

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(fpca_tolerance_band, m)?)?;
    m.add_function(wrap_pyfunction!(conformal_prediction_band, m)?)?;
    m.add_function(wrap_pyfunction!(scb_mean_degras, m)?)?;
    m.add_function(wrap_pyfunction!(equivalence_test, m)?)?;
    Ok(())
}
