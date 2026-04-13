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

/// Estimate period using FFT periodogram.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Data, shape (n, m).
/// argvals : numpy.ndarray
///     Evaluation points, length m.
///
/// Returns
/// -------
/// dict
///     period, frequency, power, confidence.
#[pyfunction]
pub fn estimate_period_fft<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let result = fdars_core::seasonal::estimate_period_fft(&mat, &av);
    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("period", result.period)?;
    dict.set_item("frequency", result.frequency)?;
    dict.set_item("power", result.power)?;
    dict.set_item("confidence", result.confidence)?;
    Ok(dict)
}

/// Lomb-Scargle periodogram for functional data.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Data, shape (n, m).
/// argvals : numpy.ndarray
///     Evaluation points, length m.
/// oversampling : float, optional
///     Oversampling factor (default None -> 4.0).
/// nyquist_factor : float, optional
///     Maximum frequency multiplier (default None -> 1.0).
///
/// Returns
/// -------
/// dict
///     frequencies, periods, power, peak_period, peak_frequency,
///     peak_power, false_alarm_probability, significance.
#[pyfunction]
#[pyo3(signature = (data, argvals, oversampling=None, nyquist_factor=None))]
pub fn lomb_scargle_fdata<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    oversampling: Option<f64>,
    nyquist_factor: Option<f64>,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let result = fdars_core::seasonal::lomb_scargle_fdata(&mat, &av, oversampling, nyquist_factor);
    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("frequencies", vec_to_numpy1d(py, result.frequencies))?;
    dict.set_item("periods", vec_to_numpy1d(py, result.periods))?;
    dict.set_item("power", vec_to_numpy1d(py, result.power))?;
    dict.set_item("peak_period", result.peak_period)?;
    dict.set_item("peak_frequency", result.peak_frequency)?;
    dict.set_item("peak_power", result.peak_power)?;
    dict.set_item("false_alarm_probability", result.false_alarm_probability)?;
    dict.set_item("significance", result.significance)?;
    Ok(dict)
}

/// Matrix Profile analysis for functional data.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Data, shape (n, m).
/// subsequence_length : int, optional
///     Length of subsequences (default None -> auto).
/// exclusion_zone : float, optional
///     Exclusion zone fraction (default None -> 0.5).
///
/// Returns
/// -------
/// dict
///     profile, profile_index, subsequence_length, detected_periods,
///     primary_period, confidence.
#[pyfunction]
#[pyo3(signature = (data, subsequence_length=None, exclusion_zone=None))]
pub fn matrix_profile_fdata<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    subsequence_length: Option<usize>,
    exclusion_zone: Option<f64>,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let result =
        fdars_core::seasonal::matrix_profile_fdata(&mat, subsequence_length, exclusion_zone);
    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("profile", vec_to_numpy1d(py, result.profile))?;
    dict.set_item(
        "profile_index",
        usize_vec_to_numpy1d(py, result.profile_index),
    )?;
    dict.set_item("subsequence_length", result.subsequence_length)?;
    dict.set_item(
        "detected_periods",
        vec_to_numpy1d(py, result.detected_periods),
    )?;
    dict.set_item("primary_period", result.primary_period)?;
    dict.set_item("confidence", result.confidence)?;
    Ok(dict)
}

/// Singular Spectrum Analysis for functional data.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Data, shape (n, m).
/// window_length : int, optional
///     SSA window length (default None -> auto).
/// n_components : int, optional
///     Number of SSA components (default None -> 10).
///
/// Returns
/// -------
/// dict
///     trend, seasonal, noise, singular_values, contributions,
///     window_length, n_components, detected_period, confidence.
#[pyfunction]
#[pyo3(signature = (data, window_length=None, n_components=None))]
pub fn ssa_fdata<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    window_length: Option<usize>,
    n_components: Option<usize>,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let result = fdars_core::seasonal::ssa_fdata(&mat, window_length, n_components);
    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("trend", vec_to_numpy1d(py, result.trend))?;
    dict.set_item("seasonal", vec_to_numpy1d(py, result.seasonal))?;
    dict.set_item("noise", vec_to_numpy1d(py, result.noise))?;
    dict.set_item(
        "singular_values",
        vec_to_numpy1d(py, result.singular_values),
    )?;
    dict.set_item("contributions", vec_to_numpy1d(py, result.contributions))?;
    dict.set_item("window_length", result.window_length)?;
    dict.set_item("n_components", result.n_components)?;
    dict.set_item("detected_period", result.detected_period)?;
    dict.set_item("confidence", result.confidence)?;
    Ok(dict)
}

/// Instantaneous period estimation via Hilbert transform.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Data, shape (n, m).
/// argvals : numpy.ndarray
///     Evaluation points, length m.
///
/// Returns
/// -------
/// dict
///     period (m,), frequency (m,), amplitude (m,).
#[pyfunction]
pub fn instantaneous_period<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let result = fdars_core::seasonal::instantaneous_period(&mat, &av);
    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("period", vec_to_numpy1d(py, result.period))?;
    dict.set_item("frequency", vec_to_numpy1d(py, result.frequency))?;
    dict.set_item("amplitude", vec_to_numpy1d(py, result.amplitude))?;
    Ok(dict)
}

/// Detect seasonality change points.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Data, shape (n, m).
/// argvals : numpy.ndarray
///     Evaluation points, length m.
/// period : float
///     Seasonal period.
/// threshold : float
///     Strength threshold for seasonal/non-seasonal.
/// window_size : float
///     Window size for local strength estimation.
/// min_duration : float
///     Minimum duration to confirm a change.
///
/// Returns
/// -------
/// dict
///     change_points (list of dicts), strength_curve (m,).
#[pyfunction]
pub fn detect_seasonality_changes<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    period: f64,
    threshold: f64,
    window_size: f64,
    min_duration: f64,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let result = fdars_core::seasonal::detect_seasonality_changes(
        &mat,
        &av,
        period,
        threshold,
        window_size,
        min_duration,
    );
    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("strength_curve", vec_to_numpy1d(py, result.strength_curve))?;
    let cps = pyo3::types::PyList::empty(py);
    for cp in &result.change_points {
        let cpd = pyo3::types::PyDict::new(py);
        cpd.set_item("time", cp.time)?;
        cpd.set_item("change_type", format!("{:?}", cp.change_type))?;
        cpd.set_item("strength_before", cp.strength_before)?;
        cpd.set_item("strength_after", cp.strength_after)?;
        cps.append(cpd)?;
    }
    dict.set_item("change_points", cps)?;
    Ok(dict)
}

/// Classify seasonality type.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Data, shape (n, m).
/// argvals : numpy.ndarray
///     Evaluation points, length m.
/// period : float
///     Known seasonal period.
/// strength_threshold : float, optional
///     Threshold for seasonal/non-seasonal (default None -> 0.3).
/// timing_threshold : float, optional
///     Max std of normalized timing for "stable" (default None -> 0.05).
///
/// Returns
/// -------
/// dict
///     is_seasonal, has_stable_timing, timing_variability,
///     seasonal_strength, classification.
#[pyfunction]
#[pyo3(signature = (data, argvals, period, strength_threshold=None, timing_threshold=None))]
pub fn classify_seasonality<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    period: f64,
    strength_threshold: Option<f64>,
    timing_threshold: Option<f64>,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let result = fdars_core::seasonal::classify_seasonality(
        &mat,
        &av,
        period,
        strength_threshold,
        timing_threshold,
    );
    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("is_seasonal", result.is_seasonal)?;
    dict.set_item("has_stable_timing", result.has_stable_timing)?;
    dict.set_item("timing_variability", result.timing_variability)?;
    dict.set_item("seasonal_strength", result.seasonal_strength)?;
    dict.set_item("classification", format!("{:?}", result.classification))?;
    dict.set_item(
        "cycle_strengths",
        vec_to_numpy1d(py, result.cycle_strengths),
    )?;
    dict.set_item(
        "weak_seasons",
        usize_vec_to_numpy1d(py, result.weak_seasons),
    )?;
    Ok(dict)
}

/// Analyze peak timing variability.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Data, shape (n, m).
/// argvals : numpy.ndarray
///     Evaluation points, length m.
/// period : float
///     Known period.
/// smooth_nbasis : int, optional
///     Number of Fourier basis functions for smoothing (default None -> auto).
///
/// Returns
/// -------
/// dict
///     peak_times, peak_values, normalized_timing, mean_timing,
///     std_timing, range_timing, variability_score, timing_trend.
#[pyfunction]
#[pyo3(signature = (data, argvals, period, smooth_nbasis=None))]
pub fn analyze_peak_timing<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    period: f64,
    smooth_nbasis: Option<usize>,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let result = fdars_core::seasonal::analyze_peak_timing(&mat, &av, period, smooth_nbasis);
    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("peak_times", vec_to_numpy1d(py, result.peak_times))?;
    dict.set_item("peak_values", vec_to_numpy1d(py, result.peak_values))?;
    dict.set_item(
        "normalized_timing",
        vec_to_numpy1d(py, result.normalized_timing),
    )?;
    dict.set_item("mean_timing", result.mean_timing)?;
    dict.set_item("std_timing", result.std_timing)?;
    dict.set_item("range_timing", result.range_timing)?;
    dict.set_item("variability_score", result.variability_score)?;
    dict.set_item("timing_trend", result.timing_trend)?;
    Ok(dict)
}

/// Seasonal strength using wavelet method.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Data, shape (n, m).
/// argvals : numpy.ndarray
///     Evaluation points, length m.
/// period : float
///     Estimated period.
///
/// Returns
/// -------
/// float
///     Seasonal strength value.
#[pyfunction]
pub fn seasonal_strength_wavelet<'py>(
    _py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    period: f64,
) -> PyResult<f64> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    Ok(fdars_core::seasonal::seasonal_strength_wavelet(
        &mat, &av, period,
    ))
}

/// Time-varying seasonal strength using windowed estimation.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Data, shape (n, m).
/// argvals : numpy.ndarray
///     Evaluation points, length m.
/// period : float
///     Seasonal period.
/// window_size : float
///     Window width (recommended: 2 * period).
/// method : str, optional
///     "variance" (default) or "spectral".
///
/// Returns
/// -------
/// numpy.ndarray
///     Seasonal strength at each time point, length m.
#[pyfunction]
#[pyo3(signature = (data, argvals, period, window_size, method="variance"))]
pub fn seasonal_strength_windowed<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    period: f64,
    window_size: f64,
    method: &str,
) -> PyResult<Bound<'py, numpy::PyArray1<f64>>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let m = match method {
        "variance" => fdars_core::seasonal::StrengthMethod::Variance,
        "spectral" => fdars_core::seasonal::StrengthMethod::Spectral,
        _ => {
            return Err(pyo3::exceptions::PyValueError::new_err(
                "method must be 'variance' or 'spectral'",
            ))
        }
    };
    let result =
        fdars_core::seasonal::seasonal_strength_windowed(&mat, &av, period, window_size, m);
    Ok(vec_to_numpy1d(py, result))
}

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(sazed, m)?)?;
    m.add_function(wrap_pyfunction!(autoperiod, m)?)?;
    m.add_function(wrap_pyfunction!(cfd_autoperiod, m)?)?;
    m.add_function(wrap_pyfunction!(detect_peaks, m)?)?;
    m.add_function(wrap_pyfunction!(stl_decompose, m)?)?;
    m.add_function(wrap_pyfunction!(seasonal_strength, m)?)?;
    m.add_function(wrap_pyfunction!(estimate_period_fft, m)?)?;
    m.add_function(wrap_pyfunction!(lomb_scargle_fdata, m)?)?;
    m.add_function(wrap_pyfunction!(matrix_profile_fdata, m)?)?;
    m.add_function(wrap_pyfunction!(ssa_fdata, m)?)?;
    m.add_function(wrap_pyfunction!(instantaneous_period, m)?)?;
    m.add_function(wrap_pyfunction!(detect_seasonality_changes, m)?)?;
    m.add_function(wrap_pyfunction!(classify_seasonality, m)?)?;
    m.add_function(wrap_pyfunction!(analyze_peak_timing, m)?)?;
    m.add_function(wrap_pyfunction!(seasonal_strength_wavelet, m)?)?;
    m.add_function(wrap_pyfunction!(seasonal_strength_windowed, m)?)?;
    Ok(())
}
