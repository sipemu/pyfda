//! Outlier detection for functional data.

use crate::convert::*;
use numpy::PyReadonlyArray2;
use pyo3::prelude::*;
use pyo3::types::PyDict;

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
    let threshold =
        fdars_core::outliers::outliers_threshold_lrt(&mat, n_bootstrap, smo, trim, 42, percentile);
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

/// LRT-based outlier detection with bootstrap (returns threshold and null distribution).
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
/// seed : int, optional
///     Random seed (default 42).
///
/// Returns
/// -------
/// dict
///     outliers (bool array), threshold (float), null_distribution (1D array).
#[pyfunction]
#[pyo3(signature = (data, alpha=0.05, n_bootstrap=200, trim=0.1, smo=0.02, seed=42))]
pub fn detect_outliers_lrt_with_dist<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    alpha: f64,
    n_bootstrap: usize,
    trim: f64,
    smo: f64,
    seed: u64,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let percentile = 1.0 - alpha;
    let (threshold, null_dist) = fdars_core::outliers::outliers_threshold_lrt_with_dist(
        &mat,
        n_bootstrap,
        smo,
        trim,
        seed,
        percentile,
    );
    let outliers = fdars_core::outliers::detect_outliers_lrt(&mat, threshold, trim);

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("outliers", bool_vec_to_numpy1d(py, outliers))?;
    dict.set_item("threshold", threshold)?;
    dict.set_item("null_distribution", vec_to_numpy1d(py, null_dist))?;
    Ok(dict)
}

// ---------------------------------------------------------------------------
// Internal helper: TvdMssOutliers (#[non_exhaustive]) → PyDict.
//
// Accesses fields individually (never struct-literal on a #[non_exhaustive]
// type from a cross-crate dependency). Index sets via x as i64 collect
// (the boxplot_result_to_pydict pattern); score vectors via vec_to_numpy1d.
// ---------------------------------------------------------------------------

fn tvdmss_to_pydict<'py>(
    py: Python<'py>,
    r: fdars_core::outliers::TvdMssOutliers,
) -> PyResult<Bound<'py, PyDict>> {
    let dict = PyDict::new(py);
    dict.set_item(
        "magnitude_outliers",
        r.magnitude_outliers
            .into_iter()
            .map(|x| x as i64)
            .collect::<Vec<i64>>(),
    )?;
    dict.set_item(
        "shape_outliers",
        r.shape_outliers
            .into_iter()
            .map(|x| x as i64)
            .collect::<Vec<i64>>(),
    )?;
    dict.set_item("tvd", vec_to_numpy1d(py, r.tvd))?;
    dict.set_item("mss", vec_to_numpy1d(py, r.mss))?;
    Ok(dict)
}

/// TVD-MSS functional outlier detection.
///
/// Detects magnitude and shape outliers using Total Variation Depth (TVD) and
/// Modified Shape Similarity (MSS). Both config fields are fully deterministic
/// (no seed). Requires at least 3 observations.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Data, shape (n, m). Requires n >= 3.
/// emp_factor_mss : float, optional
///     Empirical factor for MSS outlier threshold (default 1.5).
/// emp_factor_tvd : float, optional
///     Empirical factor for TVD outlier threshold (default 1.5).
/// central_region_tvd : float, optional
///     Central region proportion for TVD (default 0.5).
///
/// Returns
/// -------
/// dict
///     magnitude_outliers (list[int]), shape_outliers (list[int]),
///     tvd (n,), mss (n,).
#[pyfunction]
#[pyo3(signature = (data, emp_factor_mss=1.5, emp_factor_tvd=1.5, central_region_tvd=0.5))]
pub fn tvdmss<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    emp_factor_mss: f64,
    emp_factor_tvd: f64,
    central_region_tvd: f64,
) -> PyResult<Bound<'py, PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let config = fdars_core::outliers::TvdMssConfig {
        emp_factor_mss,
        emp_factor_tvd,
        central_region_tvd,
    };
    let r = to_pyresult(fdars_core::outliers::tvdmss(&mat, config))?;
    tvdmss_to_pydict(py, r)
}

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(detect_outliers_lrt, m)?)?;
    m.add_function(wrap_pyfunction!(detect_outliers_lrt_with_dist, m)?)?;
    m.add_function(wrap_pyfunction!(outliergram, m)?)?;
    m.add_function(wrap_pyfunction!(magnitude_shape, m)?)?;
    m.add_function(wrap_pyfunction!(tvdmss, m)?)?;
    Ok(())
}
