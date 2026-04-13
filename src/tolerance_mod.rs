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

/// Elastic tolerance band (amplitude only, after alignment).
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Data, shape (n, m).
/// argvals : numpy.ndarray
///     Evaluation points, length m.
/// ncomp : int, optional
///     Number of FPC components (default 3).
/// nb : int, optional
///     Number of bootstrap replicates (default 200).
/// coverage : float, optional
///     Coverage level (default 0.95).
/// band_type : str, optional
///     "simultaneous" (default) or "pointwise".
/// max_iter : int, optional
///     Maximum Karcher mean iterations (default 20).
/// seed : int, optional
///     Random seed (default 42).
///
/// Returns
/// -------
/// dict
///     upper (m,), lower (m,), center (m,), half_width (m,).
#[pyfunction]
#[pyo3(signature = (data, argvals, ncomp=3, nb=200, coverage=0.95, band_type="simultaneous", max_iter=20, seed=42))]
pub fn elastic_tolerance_band<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    ncomp: usize,
    nb: usize,
    coverage: f64,
    band_type: &str,
    max_iter: usize,
    seed: u64,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let bt = match band_type {
        "simultaneous" => fdars_core::tolerance::BandType::Simultaneous,
        "pointwise" => fdars_core::tolerance::BandType::Pointwise,
        _ => {
            return Err(pyo3::exceptions::PyValueError::new_err(
                "band_type must be 'simultaneous' or 'pointwise'",
            ))
        }
    };
    let result = to_pyresult(fdars_core::tolerance::elastic_tolerance_band(
        &mat, &av, ncomp, nb, coverage, bt, max_iter, seed,
    ))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("upper", vec_to_numpy1d(py, result.upper))?;
    dict.set_item("lower", vec_to_numpy1d(py, result.lower))?;
    dict.set_item("center", vec_to_numpy1d(py, result.center))?;
    dict.set_item("half_width", vec_to_numpy1d(py, result.half_width))?;
    Ok(dict)
}

/// Phase tolerance band on warping functions.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Data, shape (n, m).
/// argvals : numpy.ndarray
///     Evaluation points, length m.
/// ncomp : int, optional
///     Number of FPC components (default 3).
/// nb : int, optional
///     Number of bootstrap replicates (default 200).
/// coverage : float, optional
///     Coverage level (default 0.95).
/// band_type : str, optional
///     "simultaneous" (default) or "pointwise".
/// max_iter : int, optional
///     Maximum Karcher mean iterations (default 20).
/// seed : int, optional
///     Random seed (default 42).
///
/// Returns
/// -------
/// dict
///     gamma_lower (m,), gamma_upper (m,), gamma_center (m,),
///     tangent_band dict with upper, lower, center, half_width.
#[pyfunction]
#[pyo3(signature = (data, argvals, ncomp=3, nb=200, coverage=0.95, band_type="simultaneous", max_iter=20, seed=42))]
pub fn phase_tolerance_band<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    ncomp: usize,
    nb: usize,
    coverage: f64,
    band_type: &str,
    max_iter: usize,
    seed: u64,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let bt = match band_type {
        "simultaneous" => fdars_core::tolerance::BandType::Simultaneous,
        "pointwise" => fdars_core::tolerance::BandType::Pointwise,
        _ => {
            return Err(pyo3::exceptions::PyValueError::new_err(
                "band_type must be 'simultaneous' or 'pointwise'",
            ))
        }
    };
    let result = to_pyresult(fdars_core::tolerance::phase_tolerance_band(
        &mat, &av, ncomp, nb, coverage, bt, max_iter, seed,
    ))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("gamma_lower", vec_to_numpy1d(py, result.gamma_lower))?;
    dict.set_item("gamma_upper", vec_to_numpy1d(py, result.gamma_upper))?;
    dict.set_item("gamma_center", vec_to_numpy1d(py, result.gamma_center))?;
    let tangent = pyo3::types::PyDict::new(py);
    tangent.set_item("upper", vec_to_numpy1d(py, result.tangent_band.upper))?;
    tangent.set_item("lower", vec_to_numpy1d(py, result.tangent_band.lower))?;
    tangent.set_item("center", vec_to_numpy1d(py, result.tangent_band.center))?;
    tangent.set_item(
        "half_width",
        vec_to_numpy1d(py, result.tangent_band.half_width),
    )?;
    dict.set_item("tangent_band", tangent)?;
    Ok(dict)
}

/// Joint amplitude and phase elastic tolerance bands.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Data, shape (n, m).
/// argvals : numpy.ndarray
///     Evaluation points, length m.
/// ncomp_amplitude : int, optional
///     Number of FPC components for amplitude (default 3).
/// ncomp_phase : int, optional
///     Number of FPC components for phase (default 3).
/// nb : int, optional
///     Number of bootstrap replicates (default 200).
/// coverage : float, optional
///     Coverage level (default 0.95).
/// band_type : str, optional
///     "pointwise" (default) or "simultaneous".
/// max_iter : int, optional
///     Maximum Karcher mean iterations (default 20).
/// tol : float, optional
///     Convergence tolerance (default 1e-4).
/// seed : int, optional
///     Random seed (default 42).
///
/// Returns
/// -------
/// dict
///     amplitude (dict with upper, lower, center, half_width),
///     phase (dict with gamma_lower, gamma_upper, gamma_center, tangent_band).
#[pyfunction]
#[pyo3(signature = (data, argvals, ncomp_amplitude=3, ncomp_phase=3, nb=200, coverage=0.95, band_type="pointwise", max_iter=20, tol=1e-4, seed=42))]
pub fn elastic_tolerance_band_with_config<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    ncomp_amplitude: usize,
    ncomp_phase: usize,
    nb: usize,
    coverage: f64,
    band_type: &str,
    max_iter: usize,
    tol: f64,
    seed: u64,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let bt = match band_type {
        "simultaneous" => fdars_core::tolerance::BandType::Simultaneous,
        "pointwise" => fdars_core::tolerance::BandType::Pointwise,
        _ => {
            return Err(pyo3::exceptions::PyValueError::new_err(
                "band_type must be 'simultaneous' or 'pointwise'",
            ))
        }
    };
    let mut config = fdars_core::tolerance::ElasticToleranceConfig::default();
    config.ncomp_amplitude = ncomp_amplitude;
    config.ncomp_phase = ncomp_phase;
    config.nb = nb;
    config.coverage = coverage;
    config.band_type = bt;
    config.max_iter = max_iter;
    config.tol = tol;
    config.seed = seed;
    let result = to_pyresult(fdars_core::tolerance::elastic_tolerance_band_with_config(
        &mat, &av, &config,
    ))?;

    let dict = pyo3::types::PyDict::new(py);

    // Amplitude band
    let amp = pyo3::types::PyDict::new(py);
    amp.set_item("upper", vec_to_numpy1d(py, result.amplitude.upper))?;
    amp.set_item("lower", vec_to_numpy1d(py, result.amplitude.lower))?;
    amp.set_item("center", vec_to_numpy1d(py, result.amplitude.center))?;
    amp.set_item(
        "half_width",
        vec_to_numpy1d(py, result.amplitude.half_width),
    )?;
    dict.set_item("amplitude", amp)?;

    // Phase band
    let phase = pyo3::types::PyDict::new(py);
    phase.set_item("gamma_lower", vec_to_numpy1d(py, result.phase.gamma_lower))?;
    phase.set_item("gamma_upper", vec_to_numpy1d(py, result.phase.gamma_upper))?;
    phase.set_item(
        "gamma_center",
        vec_to_numpy1d(py, result.phase.gamma_center),
    )?;
    let tangent = pyo3::types::PyDict::new(py);
    tangent.set_item("upper", vec_to_numpy1d(py, result.phase.tangent_band.upper))?;
    tangent.set_item("lower", vec_to_numpy1d(py, result.phase.tangent_band.lower))?;
    tangent.set_item(
        "center",
        vec_to_numpy1d(py, result.phase.tangent_band.center),
    )?;
    tangent.set_item(
        "half_width",
        vec_to_numpy1d(py, result.phase.tangent_band.half_width),
    )?;
    phase.set_item("tangent_band", tangent)?;
    dict.set_item("phase", phase)?;

    Ok(dict)
}

/// One-sample equivalence test.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Data, shape (n, m).
/// mu0 : numpy.ndarray
///     Reference function, length m.
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
#[pyo3(signature = (data, mu0, delta, alpha=0.05, nb=1000, seed=42))]
pub fn equivalence_test_one_sample<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    mu0: PyReadonlyArray1<'py, f64>,
    delta: f64,
    alpha: f64,
    nb: usize,
    seed: u64,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let mu0_vec = numpy1d_to_vec(mu0);
    let result = fdars_core::tolerance::equivalence_test_one_sample(
        &mat,
        &mu0_vec,
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
            "equivalence_test_one_sample returned None (invalid input)",
        )),
    }
}

/// Exponential family tolerance band.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Data, shape (n, m).
/// family : str
///     "gaussian", "binomial", or "poisson".
/// ncomp : int, optional
///     Number of FPC components (default 3).
/// nb : int, optional
///     Number of bootstrap replicates (default 200).
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
#[pyo3(signature = (data, family="gaussian", ncomp=3, nb=200, coverage=0.95, seed=42))]
pub fn exponential_family_tolerance_band<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    family: &str,
    ncomp: usize,
    nb: usize,
    coverage: f64,
    seed: u64,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let fam = match family {
        "gaussian" => fdars_core::tolerance::ExponentialFamily::Gaussian,
        "binomial" => fdars_core::tolerance::ExponentialFamily::Binomial,
        "poisson" => fdars_core::tolerance::ExponentialFamily::Poisson,
        _ => {
            return Err(pyo3::exceptions::PyValueError::new_err(
                "family must be 'gaussian', 'binomial', or 'poisson'",
            ))
        }
    };
    let result = to_pyresult(fdars_core::tolerance::exponential_family_tolerance_band(
        &mat, fam, ncomp, nb, coverage, seed,
    ))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("upper", vec_to_numpy1d(py, result.upper))?;
    dict.set_item("lower", vec_to_numpy1d(py, result.lower))?;
    dict.set_item("center", vec_to_numpy1d(py, result.center))?;
    dict.set_item("half_width", vec_to_numpy1d(py, result.half_width))?;
    Ok(dict)
}

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(fpca_tolerance_band, m)?)?;
    m.add_function(wrap_pyfunction!(conformal_prediction_band, m)?)?;
    m.add_function(wrap_pyfunction!(scb_mean_degras, m)?)?;
    m.add_function(wrap_pyfunction!(equivalence_test, m)?)?;
    m.add_function(wrap_pyfunction!(elastic_tolerance_band, m)?)?;
    m.add_function(wrap_pyfunction!(phase_tolerance_band, m)?)?;
    m.add_function(wrap_pyfunction!(elastic_tolerance_band_with_config, m)?)?;
    m.add_function(wrap_pyfunction!(equivalence_test_one_sample, m)?)?;
    m.add_function(wrap_pyfunction!(exponential_family_tolerance_band, m)?)?;
    Ok(())
}
