//! Functional time series bindings.
//!
//! Exposes the `fdars.fts` submodule with bindings for fdars-core 0.33's
//! functional time series module: FTSM model fit/forecast, functional ACF/PACF,
//! stationarity test, long-run covariance, spectral density, and dynamic FPCA.
//!
//! Plan 67-01 (tracer): `ftsm` bound.
//! Plan 67-02: `ftsm_forecast`, `ftsm_forecast_multistep`, `ftsm_update`, `fplsr` added.
//! Plan 67-03: `functional_acf`, `functional_pacf`, `functional_difference`,
//!             `stationarity_test`, `long_run_covariance` added.
//! Plan 67-04 will extend `register()` with spectral density and DPCA functions.

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

/// Functional Partial Least Squares Regression (fPLSR) one-step-ahead forecast.
///
/// Fits a PLS model on lag-1 pairs from the time-ordered functional data and
/// produces a one-step-ahead forecast plus the in-sample lag-1 fitted curves.
/// Requires n_obs >= 3 (needs at least 2 training pairs + 1 forecast origin).
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Time-ordered functional data, shape (n_obs, n_points). n_obs >= 3.
/// argvals : numpy.ndarray
///     Evaluation grid, length n_points.
/// ncomp : int, optional
///     Number of PLS components (default 3). Clamped to min(ncomp, n_obs-1, n_points).
///
/// Returns
/// -------
/// dict
///     forecast (1, n_points), fitted (n_obs-1, n_points), ncomp (int).
///
/// Raises
/// ------
/// ValueError
///     If n_obs < 3, ncomp < 1, or argvals length mismatch.
#[pyfunction]
#[pyo3(signature = (data, argvals, ncomp=3))]
pub fn fplsr<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    ncomp: usize,
) -> PyResult<Bound<'py, PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let result = to_pyresult(fdars_core::fts::fplsr(&mat, ncomp, &av))?;

    let dict = PyDict::new(py);
    dict.set_item("forecast", fdmatrix_to_numpy2d(py, &result.forecast))?;
    dict.set_item("fitted", fdmatrix_to_numpy2d(py, &result.fitted))?;
    dict.set_item("ncomp", result.ncomp)?;
    Ok(dict)
}

// ---------------------------------------------------------------------------
// Group B: Diagnostics functions
// ---------------------------------------------------------------------------

/// Compute the functional autocorrelation function (ACF) with Monte Carlo bands.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Time-ordered functional data, shape (n_obs, n_points).
/// argvals : numpy.ndarray
///     Evaluation grid, length n_points.
/// max_lag : int or None, optional
///     Maximum lag to compute (default None → min(20, N/4)). Must be >= 1 if set.
/// n_sim : int, optional
///     Monte Carlo replications for white-noise band (default 999). Must be >= 1.
/// ci : float, optional
///     Confidence level for the white-noise band (default 0.95). Must be in (0, 1).
/// seed : int, optional
///     RNG seed for Monte Carlo band (default 42). Same seed → identical result.
///
/// Returns
/// -------
/// dict
///     lags (int64 numpy 1D), acf (numpy 1D), pacf (numpy 1D), upper_band (numpy 1D).
///
/// Raises
/// ------
/// ValueError
///     If n_sim < 1, ci outside (0,1), max_lag=0, or max_lag >= n_obs.
#[pyfunction]
#[pyo3(signature = (data, argvals, max_lag=None, n_sim=999, ci=0.95, seed=42))]
pub fn functional_acf<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    max_lag: Option<usize>,
    n_sim: usize,
    ci: f64,
    seed: u64,
) -> PyResult<Bound<'py, PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let result = to_pyresult(fdars_core::fts::functional_acf(&mat, &av, max_lag, n_sim, ci, seed))?;

    // FacfResult.lags is Vec<u32> — cast to i64 for a numpy int array.
    // Do NOT pass u32 to vec_to_numpy1d (which expects Vec<f64>).
    let lags_i64: Vec<i64> = result.lags.into_iter().map(|v| v as i64).collect();

    let dict = PyDict::new(py);
    dict.set_item("lags", numpy::PyArray1::from_vec(py, lags_i64))?;
    dict.set_item("acf", vec_to_numpy1d(py, result.acf))?;
    dict.set_item("pacf", vec_to_numpy1d(py, result.pacf))?;
    dict.set_item("upper_band", vec_to_numpy1d(py, result.upper_band))?;
    Ok(dict)
}

/// Compute the functional partial autocorrelation function (PACF) with Monte Carlo bands.
///
/// Delegates upstream to `functional_acf` and returns the same `FacfResult` struct
/// (both acf and pacf fields are populated in the result).
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Time-ordered functional data, shape (n_obs, n_points).
/// argvals : numpy.ndarray
///     Evaluation grid, length n_points.
/// max_lag : int or None, optional
///     Maximum lag to compute (default None → min(20, N/4)). Must be >= 1 if set.
/// n_sim : int, optional
///     Monte Carlo replications for white-noise band (default 999). Must be >= 1.
/// ci : float, optional
///     Confidence level for the white-noise band (default 0.95). Must be in (0, 1).
/// seed : int, optional
///     RNG seed for Monte Carlo band (default 42). Same seed → identical result.
///
/// Returns
/// -------
/// dict
///     lags (int64 numpy 1D), acf (numpy 1D), pacf (numpy 1D), upper_band (numpy 1D).
///
/// Raises
/// ------
/// ValueError
///     If n_sim < 1, ci outside (0,1), max_lag=0, or max_lag >= n_obs.
#[pyfunction]
#[pyo3(signature = (data, argvals, max_lag=None, n_sim=999, ci=0.95, seed=42))]
pub fn functional_pacf<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    max_lag: Option<usize>,
    n_sim: usize,
    ci: f64,
    seed: u64,
) -> PyResult<Bound<'py, PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let result = to_pyresult(fdars_core::fts::functional_pacf(&mat, &av, max_lag, n_sim, ci, seed))?;

    // FacfResult.lags is Vec<u32> — cast to i64.
    let lags_i64: Vec<i64> = result.lags.into_iter().map(|v| v as i64).collect();

    let dict = PyDict::new(py);
    dict.set_item("lags", numpy::PyArray1::from_vec(py, lags_i64))?;
    dict.set_item("acf", vec_to_numpy1d(py, result.acf))?;
    dict.set_item("pacf", vec_to_numpy1d(py, result.pacf))?;
    dict.set_item("upper_band", vec_to_numpy1d(py, result.upper_band))?;
    Ok(dict)
}

/// Compute the first-order functional difference (lag-1 differencing).
///
/// Takes only data (no argvals). Returns a naked 2D numpy array — NOT a PyDict.
/// Output shape: (n_obs - 1, n_points).
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Time-ordered functional data, shape (n_obs, n_points). n_obs >= 2.
///
/// Returns
/// -------
/// numpy.ndarray
///     Differenced functional data, shape (n_obs - 1, n_points).
///
/// Raises
/// ------
/// ValueError
///     If n_obs < 2 (cannot compute lag-1 differences with fewer than 2 curves).
#[pyfunction]
pub fn functional_difference<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
) -> PyResult<Bound<'py, numpy::PyArray2<f64>>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let result = to_pyresult(fdars_core::fts::functional_difference(&mat))?;
    Ok(fdmatrix_to_numpy2d(py, &result))
}

/// Test stationarity of functional time series via permutation test.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Time-ordered functional data, shape (n_obs, n_points).
/// argvals : numpy.ndarray
///     Evaluation grid, length n_points.
/// n_perm : int, optional
///     Number of permutations for MC p-value (default 999). Must be >= 1.
/// seed : int, optional
///     RNG seed for Fisher-Yates shuffle (default 42). Same seed → identical p_value.
///
/// Returns
/// -------
/// dict
///     statistic (float), p_value (float), n_perm (int).
///
/// Raises
/// ------
/// ValueError
///     If n_perm < 1 or argvals length mismatch.
#[pyfunction]
#[pyo3(signature = (data, argvals, n_perm=999, seed=42))]
pub fn stationarity_test<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    n_perm: usize,
    seed: u64,
) -> PyResult<Bound<'py, PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let result = to_pyresult(fdars_core::fts::stationarity_test(&mat, &av, n_perm, seed))?;

    let dict = PyDict::new(py);
    dict.set_item("statistic", result.statistic)?;
    dict.set_item("p_value", result.p_value)?;
    dict.set_item("n_perm", result.n_perm)?;
    Ok(dict)
}

/// Estimate the long-run covariance operator of a functional time series.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Time-ordered functional data, shape (n_obs, n_points).
/// argvals : numpy.ndarray
///     Evaluation grid, length n_points.
/// bandwidth : int or None, optional
///     Bartlett kernel bandwidth (default None → ⌊N^{1/3}⌋).
///     bandwidth=0 returns the sample covariance C_0 (valid, not rejected).
///
/// Returns
/// -------
/// dict
///     cov_matrix (numpy 2D, shape (n_points, n_points)), m (int), bandwidth (int), n_curves (int).
///     cov_matrix is symmetric within numerical precision.
///
/// Raises
/// ------
/// ValueError
///     If argvals length mismatch or data has < 2 curves.
#[pyfunction]
#[pyo3(signature = (data, argvals, bandwidth=None))]
pub fn long_run_covariance<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    bandwidth: Option<usize>,
) -> PyResult<Bound<'py, PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let result = to_pyresult(fdars_core::fts::long_run_covariance(&mat, &av, bandwidth))?;

    // LongRunCovResult.cov_matrix is a flat column-major Vec<f64> of length m×m.
    // Reshape via FdMatrix::from_column_major then fdmatrix_to_numpy2d (correctly
    // transposes column-major to row-major). Without this reshape the matrix is
    // silently transposed.
    let m = result.m;
    let fd_cov = fdars_core::matrix::FdMatrix::from_column_major(result.cov_matrix, m, m)
        .map_err(to_pyerr)?;

    let dict = PyDict::new(py);
    dict.set_item("cov_matrix", fdmatrix_to_numpy2d(py, &fd_cov))?;
    dict.set_item("m", result.m)?;
    dict.set_item("bandwidth", result.bandwidth)?;
    dict.set_item("n_curves", result.n_curves)?;
    Ok(dict)
}

// ---------------------------------------------------------------------------
// Group C: Spectral / dimension-reduction functions
// ---------------------------------------------------------------------------

/// Estimate the spectral density operator of a functional time series.
///
/// Uses the Bartlett kernel smoother applied to the periodogram operator.
/// Returns the real and imaginary parts of the estimated spectral density
/// at each Fourier frequency.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Time-ordered functional data, shape (n_obs, n_points).
/// argvals : numpy.ndarray
///     Evaluation grid, length n_points.
/// bandwidth : int or None, optional
///     Bartlett kernel bandwidth (default None → max(1, ⌊N^{1/3}⌋)).
///     bandwidth=0 raises ValueError (rejected by upstream, unlike long_run_covariance).
///
/// Returns
/// -------
/// dict
///     freqs : numpy 1D (N,) — Fourier frequencies θ_j = 2πj/N.
///     re : list of N numpy 2D (n_points, n_points) — real parts per frequency.
///     im : list of N numpy 2D (n_points, n_points) — imaginary parts per frequency.
///     m : int — grid dimension.
///     n_curves : int — number of curves N.
///     bandwidth : int — Bartlett bandwidth used.
///
/// Notes
/// -----
/// To get a 3D array: ``np.stack(result["re"])`` yields shape (N, n_points, n_points).
///
/// Raises
/// ------
/// ValueError
///     If bandwidth=0 or argvals length mismatch.
#[pyfunction]
#[pyo3(signature = (data, argvals, bandwidth=None))]
pub fn spectral_density<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    bandwidth: Option<usize>,
) -> PyResult<Bound<'py, PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let result = to_pyresult(fdars_core::fts::spectral_density(&mat, &av, bandwidth))?;

    let m = result.m;

    // re[k] and im[k] are flat column-major m×m buffers (one per Fourier frequency).
    // Reshape each via FdMatrix::from_column_major to get a correct (m, m) numpy 2D.
    let re_list = PyList::empty(py);
    for freq_re in &result.re {
        let fd_re = fdars_core::matrix::FdMatrix::from_column_major(freq_re.clone(), m, m)
            .map_err(to_pyerr)?;
        re_list.append(fdmatrix_to_numpy2d(py, &fd_re))?;
    }

    let im_list = PyList::empty(py);
    for freq_im in &result.im {
        let fd_im = fdars_core::matrix::FdMatrix::from_column_major(freq_im.clone(), m, m)
            .map_err(to_pyerr)?;
        im_list.append(fdmatrix_to_numpy2d(py, &fd_im))?;
    }

    let dict = PyDict::new(py);
    dict.set_item("freqs", vec_to_numpy1d(py, result.freqs))?;
    dict.set_item("re", re_list)?;
    dict.set_item("im", im_list)?;
    dict.set_item("m", result.m)?;
    dict.set_item("n_curves", result.n_curves)?;
    dict.set_item("bandwidth", result.bandwidth)?;
    Ok(dict)
}

// ---------------------------------------------------------------------------
// Private helper: convert DpcaResult to PyDict (reused by dpca_reconstruct)
// ---------------------------------------------------------------------------

fn dpca_result_to_dict<'py>(
    py: Python<'py>,
    result: &fdars_core::fts::DpcaResult,
) -> PyResult<Bound<'py, PyDict>> {
    // filters: Vec<FdMatrix> — each is a (2L+1) × m matrix → list of numpy 2D
    let filters_list = PyList::empty(py);
    for f in &result.filters {
        filters_list.append(fdmatrix_to_numpy2d(py, f))?;
    }

    // eigenvalues: Vec<Vec<f64>> — per-component trajectory → list of numpy 1D
    let ev_list = PyList::empty(py);
    for ev in &result.eigenvalues {
        ev_list.append(vec_to_numpy1d(py, ev.clone()))?;
    }

    let dict = PyDict::new(py);
    dict.set_item("filters", filters_list)?;
    dict.set_item("scores", fdmatrix_to_numpy2d(py, &result.scores))?;
    dict.set_item("eigenvalues", ev_list)?;
    dict.set_item("n_freqs", result.n_freqs)?;
    dict.set_item("filter_lag", result.filter_lag)?;
    dict.set_item("ncomp", result.ncomp)?;
    // valid_range: (usize, usize) → Python 2-tuple (int, int)
    dict.set_item("valid_range", (result.valid_range.0, result.valid_range.1))?;
    Ok(dict)
}

/// Fit Dynamic Functional Principal Components Analysis (DPCA).
///
/// Decomposes the functional time series into dynamic principal components
/// using the spectral density operator. Returns filters, dynamic scores,
/// and per-component eigenvalue trajectories.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Time-ordered functional data, shape (n_obs, n_points).
/// argvals : numpy.ndarray
///     Evaluation grid, length n_points.
/// ncomp : int, optional
///     Number of dynamic components to retain (default 3). Must be in 1..=n_points.
/// bandwidth : int or None, optional
///     Bandwidth for the internal spectral density estimate (default None → auto).
///     bandwidth=0 raises ValueError.
/// filter_lag : int or None, optional
///     Filter half-width L (default None → uses resolved bandwidth).
///     filter_lag >= N/2 raises ValueError.
///
/// Returns
/// -------
/// dict
///     filters : list of ncomp numpy 2D (2L+1, n_points) — dynamic eigen-filters.
///     scores : numpy 2D (N-2L, ncomp) — dynamic score series.
///     eigenvalues : list of ncomp numpy 1D (N,) — per-component eigenvalue trajectory.
///     n_freqs : int — number of Fourier frequencies.
///     filter_lag : int — filter half-width L used.
///     ncomp : int — retained dynamic components.
///     valid_range : tuple (int, int) — interior time range (L, N-1-L).
///
/// Raises
/// ------
/// ValueError
///     If ncomp out of range, bandwidth=0, or filter_lag >= N/2.
#[pyfunction]
#[pyo3(signature = (data, argvals, ncomp=3, bandwidth=None, filter_lag=None))]
pub fn dpca<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    ncomp: usize,
    bandwidth: Option<usize>,
    filter_lag: Option<usize>,
) -> PyResult<Bound<'py, PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let result = to_pyresult(fdars_core::fts::dpca(&mat, &av, ncomp, bandwidth, filter_lag))?;
    dpca_result_to_dict(py, &result)
}

/// Fit DPCA and reconstruct the functional time series from dynamic components.
///
/// Uses the combined-function pattern: fits `dpca` internally, then calls
/// `dpca_reconstruct`. Python cannot pass a Rust `DpcaResult` directly.
/// Returns a merged dict with all DPCA fields plus the reconstruction.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Time-ordered functional data, shape (n_obs, n_points).
/// argvals : numpy.ndarray
///     Evaluation grid, length n_points.
/// ncomp : int, optional
///     Number of dynamic components (default 3). Must be in 1..=n_points.
/// bandwidth : int or None, optional
///     Bandwidth forwarded to spectral density (default None → auto).
/// filter_lag : int or None, optional
///     Filter half-width L (default None → uses resolved bandwidth).
///
/// Returns
/// -------
/// dict
///     All keys from `dpca` (filters, scores, eigenvalues, n_freqs, filter_lag,
///     ncomp, valid_range) plus:
///     fitted_reconstruction : numpy 2D (N-2L, n_points) — reconstructed curves.
///     reconstruction_error : numpy 1D (ncomp,) — per-K integrated-L2 error
///         (monotone non-increasing: adding components reduces reconstruction error).
///
/// Raises
/// ------
/// ValueError
///     If ncomp out of range, bandwidth=0, or filter_lag >= N/2.
#[pyfunction]
#[pyo3(signature = (data, argvals, ncomp=3, bandwidth=None, filter_lag=None))]
pub fn dpca_reconstruct<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    ncomp: usize,
    bandwidth: Option<usize>,
    filter_lag: Option<usize>,
) -> PyResult<Bound<'py, PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);

    // Combined-function pattern: fit dpca internally, then reconstruct.
    // Python cannot pass &DpcaResult, so we fit it here.
    let dp = to_pyresult(fdars_core::fts::dpca(&mat, &av, ncomp, bandwidth, filter_lag))?;
    let recon = to_pyresult(fdars_core::fts::dpca_reconstruct(&mat, &av, &dp))?;

    // Build the merged dict: start with all DpcaResult fields, then add reconstruction
    let dict = dpca_result_to_dict(py, &dp)?;
    dict.set_item("fitted_reconstruction", fdmatrix_to_numpy2d(py, &recon.fitted))?;
    dict.set_item(
        "reconstruction_error",
        vec_to_numpy1d(py, recon.reconstruction_error),
    )?;
    Ok(dict)
}

// ---------------------------------------------------------------------------
// Module registration
// ---------------------------------------------------------------------------

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(ftsm, m)?)?;
    m.add_function(wrap_pyfunction!(ftsm_forecast, m)?)?;
    m.add_function(wrap_pyfunction!(ftsm_forecast_multistep, m)?)?;
    m.add_function(wrap_pyfunction!(ftsm_update, m)?)?;
    m.add_function(wrap_pyfunction!(fplsr, m)?)?;
    m.add_function(wrap_pyfunction!(spectral_density, m)?)?;
    m.add_function(wrap_pyfunction!(dpca, m)?)?;
    m.add_function(wrap_pyfunction!(dpca_reconstruct, m)?)?;
    m.add_function(wrap_pyfunction!(functional_acf, m)?)?;
    m.add_function(wrap_pyfunction!(functional_pacf, m)?)?;
    m.add_function(wrap_pyfunction!(functional_difference, m)?)?;
    m.add_function(wrap_pyfunction!(stationarity_test, m)?)?;
    m.add_function(wrap_pyfunction!(long_run_covariance, m)?)?;
    Ok(())
}
