//! Seasonal analysis and period detection.

use crate::convert::*;
use numpy::{PyReadonlyArray1, PyReadonlyArray2};
use pyo3::prelude::*;

/// SAZED period detection algorithm.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Data, shape (n, m).
/// argvals : numpy.ndarray
///     Evaluation points, length m.
/// tolerance : float, optional
///     Relative tolerance for period matching (default None -> 0.05).
///
/// Returns
/// -------
/// dict
///     period (float), confidence (float), agreeing_components (int).
#[pyfunction]
#[pyo3(signature = (data, argvals, tolerance=None))]
pub fn sazed<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    tolerance: Option<f64>,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let result = fdars_core::seasonal::sazed_fdata(&mat, &av, tolerance);

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("period", result.period)?;
    dict.set_item("confidence", result.confidence)?;
    dict.set_item("agreeing_components", result.agreeing_components)?;
    Ok(dict)
}

/// Autoperiod algorithm for period detection.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Data, shape (n, m).
/// argvals : numpy.ndarray
///     Evaluation points, length m.
/// n_candidates : int, optional
///     Max FFT peaks to consider (default None -> 5).
/// gradient_steps : int, optional
///     Gradient ascent refinement steps (default None -> 10).
///
/// Returns
/// -------
/// dict
///     period (float), confidence (float), fft_power (float), acf_validation (float).
#[pyfunction]
#[pyo3(signature = (data, argvals, n_candidates=None, gradient_steps=None))]
pub fn autoperiod<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    n_candidates: Option<usize>,
    gradient_steps: Option<usize>,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let result = fdars_core::seasonal::autoperiod_fdata(&mat, &av, n_candidates, gradient_steps);

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("period", result.period)?;
    dict.set_item("confidence", result.confidence)?;
    dict.set_item("fft_power", result.fft_power)?;
    dict.set_item("acf_validation", result.acf_validation)?;
    Ok(dict)
}

/// CFD autoperiod for period detection.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Data, shape (n, m).
/// argvals : numpy.ndarray
///     Evaluation points, length m.
/// cluster_tolerance : float, optional
///     Clustering tolerance (default None -> 0.1).
/// min_cluster_size : int, optional
///     Minimum cluster size (default None -> 1).
///
/// Returns
/// -------
/// dict
///     period (float), confidence (float), periods list, confidences list.
#[pyfunction]
#[pyo3(signature = (data, argvals, cluster_tolerance=None, min_cluster_size=None))]
pub fn cfd_autoperiod<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    cluster_tolerance: Option<f64>,
    min_cluster_size: Option<usize>,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let result =
        fdars_core::seasonal::cfd_autoperiod_fdata(&mat, &av, cluster_tolerance, min_cluster_size);

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("period", result.period)?;
    dict.set_item("confidence", result.confidence)?;
    dict.set_item("periods", vec_to_numpy1d(py, result.periods))?;
    dict.set_item("confidences", vec_to_numpy1d(py, result.confidences))?;
    Ok(dict)
}

/// Detect peaks in functional data.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Data matrix, shape (n, m).
/// argvals : numpy.ndarray
///     Evaluation points, length m.
/// min_distance : float, optional
///     Minimum distance between peaks (default None).
/// min_prominence : float, optional
///     Minimum prominence (default None).
/// smooth_first : bool, optional
///     Whether to smooth before detection (default false).
/// smooth_nbasis : int, optional
///     Number of basis functions for smoothing (default None).
///
/// Returns
/// -------
/// dict
///     peaks (list of list of dicts), mean_period (float).
#[pyfunction]
#[pyo3(signature = (data, argvals, min_distance=None, min_prominence=None, smooth_first=false, smooth_nbasis=None))]
pub fn detect_peaks<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    min_distance: Option<f64>,
    min_prominence: Option<f64>,
    smooth_first: bool,
    smooth_nbasis: Option<usize>,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let result = fdars_core::seasonal::detect_peaks(
        &mat,
        &av,
        min_distance,
        min_prominence,
        smooth_first,
        smooth_nbasis,
    );

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("mean_period", result.mean_period)?;
    // Convert peaks to list of lists of dicts
    let peaks_py: Vec<Vec<(f64, f64, f64)>> = result
        .peaks
        .into_iter()
        .map(|sample_peaks| {
            sample_peaks
                .into_iter()
                .map(|p| (p.time, p.value, p.prominence))
                .collect()
        })
        .collect();
    dict.set_item("peaks", peaks_py)?;
    Ok(dict)
}

/// STL decomposition of functional data.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Functional data, shape (n, m).
/// period : int
///     Seasonal period.
/// s_window : int, optional
///     Seasonal smoothing window (default None -> auto).
/// t_window : int, optional
///     Trend smoothing window (default None -> auto).
/// robust : bool, optional
///     Use robust weights (default false).
///
/// Returns
/// -------
/// dict
///     trend (n,m), seasonal (n,m), remainder (n,m) as 2D arrays.
#[pyfunction]
#[pyo3(signature = (data, period, s_window=None, t_window=None, robust=false))]
pub fn stl_decompose<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    period: usize,
    s_window: Option<usize>,
    t_window: Option<usize>,
    robust: bool,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let result = fdars_core::detrend::stl::stl_decompose(
        &mat, period, s_window, t_window, None, robust, None, None,
    );

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("trend", fdmatrix_to_numpy2d(py, &result.trend))?;
    dict.set_item("seasonal", fdmatrix_to_numpy2d(py, &result.seasonal))?;
    dict.set_item("remainder", fdmatrix_to_numpy2d(py, &result.remainder))?;
    Ok(dict)
}

/// Seasonal strength measure (variance method).
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Data, shape (n, m).
/// argvals : numpy.ndarray
///     Evaluation points, length m.
/// period : float
///     Estimated period for strength computation.
/// method : str, optional
///     "variance" (default) or "spectral".
///
/// Returns
/// -------
/// float
///     Seasonal strength value.
#[pyfunction]
#[pyo3(signature = (data, argvals, period, method="variance"))]
pub fn seasonal_strength<'py>(
    _py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    period: f64,
    method: &str,
) -> PyResult<f64> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let result = match method {
        "variance" => fdars_core::seasonal::seasonal_strength_variance(&mat, &av, period, 3),
        "spectral" => fdars_core::seasonal::seasonal_strength_spectral(&mat, &av, period),
        _ => {
            return Err(pyo3::exceptions::PyValueError::new_err(
                "method must be 'variance' or 'spectral'",
            ))
        }
    };
    Ok(result)
}

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(sazed, m)?)?;
    m.add_function(wrap_pyfunction!(autoperiod, m)?)?;
    m.add_function(wrap_pyfunction!(cfd_autoperiod, m)?)?;
    m.add_function(wrap_pyfunction!(detect_peaks, m)?)?;
    m.add_function(wrap_pyfunction!(stl_decompose, m)?)?;
    m.add_function(wrap_pyfunction!(seasonal_strength, m)?)?;
    Ok(())
}
