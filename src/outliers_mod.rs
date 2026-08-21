//! Outlier detection for functional data.

use crate::convert::*;
use crate::depth_mod::depth_method_from_str;
use numpy::PyReadonlyArray2;
use pyo3::exceptions::PyValueError;
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

// ---------------------------------------------------------------------------
// Internal helper: MuodResult (#[non_exhaustive]) → PyDict.
//
// 3 index sets (Vec<usize>) → list[int] via x as i64 collect.
// 3 score vectors (Vec<f64>) → 1-D numpy via vec_to_numpy1d.
// ---------------------------------------------------------------------------

fn muod_to_pydict<'py>(
    py: Python<'py>,
    r: fdars_core::outliers::MuodResult,
) -> PyResult<Bound<'py, PyDict>> {
    let dict = PyDict::new(py);
    dict.set_item(
        "shape_outliers",
        r.shape_outliers
            .into_iter()
            .map(|x| x as i64)
            .collect::<Vec<i64>>(),
    )?;
    dict.set_item(
        "magnitude_outliers",
        r.magnitude_outliers
            .into_iter()
            .map(|x| x as i64)
            .collect::<Vec<i64>>(),
    )?;
    dict.set_item(
        "amplitude_outliers",
        r.amplitude_outliers
            .into_iter()
            .map(|x| x as i64)
            .collect::<Vec<i64>>(),
    )?;
    dict.set_item("shape_index", vec_to_numpy1d(py, r.shape_index))?;
    dict.set_item("magnitude_index", vec_to_numpy1d(py, r.magnitude_index))?;
    dict.set_item("amplitude_index", vec_to_numpy1d(py, r.amplitude_index))?;
    Ok(dict)
}

/// MUOD (Massive Unsupervised Outlier Detection) for functional data.
///
/// Detects shape, magnitude, and amplitude outliers via three independent
/// outlyingness indices. Deterministic (no seed). Requires at least 3
/// observations and at least 2 evaluation points.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Data, shape (n, m). Requires n >= 3 and m >= 2.
/// factor : float, optional
///     Empirical factor for outlier thresholds (default 1.5).
///
/// Returns
/// -------
/// dict
///     shape_outliers (list[int]), magnitude_outliers (list[int]),
///     amplitude_outliers (list[int]), shape_index (n,),
///     magnitude_index (n,), amplitude_index (n,).
#[pyfunction]
#[pyo3(signature = (data, factor=1.5))]
pub fn muod<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    factor: f64,
) -> PyResult<Bound<'py, PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let config = fdars_core::outliers::MuodConfig { factor };
    let r = to_pyresult(fdars_core::outliers::muod(&mat, config))?;
    muod_to_pydict(py, r)
}

// ---------------------------------------------------------------------------
// SeqTransform string dispatcher.
//
// Lowercase tokens (consistent with all other pyfda method tokens).
// SeqTransform is #[non_exhaustive] — wildcard arm is mandatory.
// ---------------------------------------------------------------------------

fn seq_transform_from_str(s: &str) -> PyResult<fdars_core::outliers::SeqTransform> {
    match s {
        "t0" => Ok(fdars_core::outliers::SeqTransform::T0),
        "t1" => Ok(fdars_core::outliers::SeqTransform::T1),
        "t2" => Ok(fdars_core::outliers::SeqTransform::T2),
        "d1" => Ok(fdars_core::outliers::SeqTransform::D1),
        "d2" => Ok(fdars_core::outliers::SeqTransform::D2),
        other => Err(PyValueError::new_err(format!(
            "transform must be one of 't0', 't1', 't2', 'd1', 'd2', got '{other}'"
        ))),
    }
}

// Map a SeqTransform variant back to its lowercase string token.
// Wildcard required: SeqTransform is #[non_exhaustive].
fn seq_transform_variant_str(t: &fdars_core::outliers::SeqTransform) -> &'static str {
    match t {
        fdars_core::outliers::SeqTransform::T0 => "t0",
        fdars_core::outliers::SeqTransform::T1 => "t1",
        fdars_core::outliers::SeqTransform::T2 => "t2",
        fdars_core::outliers::SeqTransform::D1 => "d1",
        fdars_core::outliers::SeqTransform::D2 => "d2",
        _ => "unknown",
    }
}

// ---------------------------------------------------------------------------
// Internal helper: SeqTransformOutliers (#[non_exhaustive]) → PyDict.
//
// per_transform_outliers: Vec<(SeqTransform, Vec<usize>)> → list[dict]
// Each dict has "transform": str and "outliers": list[int].
// union_outliers: Vec<usize> → list[int].
// ---------------------------------------------------------------------------

fn seq_transform_to_pydict<'py>(
    py: Python<'py>,
    r: fdars_core::outliers::SeqTransformOutliers,
) -> PyResult<Bound<'py, PyDict>> {
    let dict = PyDict::new(py);

    let per_transform: Vec<Bound<'_, PyDict>> = r
        .per_transform_outliers
        .into_iter()
        .map(|(t, idxs)| {
            let sub = PyDict::new(py);
            sub.set_item("transform", seq_transform_variant_str(&t))?;
            sub.set_item(
                "outliers",
                idxs.into_iter().map(|x| x as i64).collect::<Vec<i64>>(),
            )?;
            Ok(sub)
        })
        .collect::<PyResult<Vec<_>>>()?;

    dict.set_item("per_transform_outliers", per_transform)?;
    dict.set_item(
        "union_outliers",
        r.union_outliers
            .into_iter()
            .map(|x| x as i64)
            .collect::<Vec<i64>>(),
    )?;
    Ok(dict)
}

/// Sequential transform outlier detection.
///
/// Applies a sequence of transforms (T0/T1/T2/D1/D2) to the data and detects
/// outliers at each step via functional depth. Fully deterministic (no seed).
/// Requires at least 2 observations.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Data, shape (n, m). Requires n >= 2.
/// transforms : list[str]
///     Sequence of transform tokens. Each must be one of 't0', 't1', 't2',
///     'd1', 'd2'. An unrecognised token raises ValueError.
/// depth_method : str, optional
///     Depth method for outlier scoring (default "modified_band"). Accepts the
///     same 13 tokens as fdars.depth.functional_depth.
/// emp_factor : float, optional
///     Empirical factor for outlier threshold (default 1.5).
///
/// Returns
/// -------
/// dict
///     per_transform_outliers (list[dict] each with transform:str +
///     outliers:list[int]), union_outliers (list[int]).
#[pyfunction]
#[pyo3(signature = (data, transforms, depth_method="modified_band", emp_factor=1.5))]
pub fn sequential_transform_outliers<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    transforms: Vec<String>,
    depth_method: &str,
    emp_factor: f64,
) -> PyResult<Bound<'py, PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let seq = transforms
        .iter()
        .map(|s| seq_transform_from_str(s))
        .collect::<PyResult<Vec<_>>>()?;
    let dm = depth_method_from_str(depth_method, true, 50, None)?;
    let config = fdars_core::outliers::SeqTransformConfig {
        depth_method: dm,
        emp_factor,
    };
    let r = to_pyresult(fdars_core::outliers::sequential_transform_outliers(
        &mat, &seq, config,
    ))?;
    seq_transform_to_pydict(py, r)
}

// ---------------------------------------------------------------------------
// Internal helper: DepthgramResult (#[non_exhaustive]) → PyDict.
//
// 8 score vectors (Vec<f64>) → 1-D numpy via vec_to_numpy1d.
// 2 index sets (Vec<usize>) → list[int] via x as i64 collect.
// ---------------------------------------------------------------------------

fn depthgram_to_pydict<'py>(
    py: Python<'py>,
    r: fdars_core::outliers::DepthgramResult,
) -> PyResult<Bound<'py, PyDict>> {
    let dict = PyDict::new(py);
    dict.set_item("mbd_mei_d", vec_to_numpy1d(py, r.mbd_mei_d))?;
    dict.set_item("mei_mbd_d", vec_to_numpy1d(py, r.mei_mbd_d))?;
    dict.set_item("mbd_mei_t", vec_to_numpy1d(py, r.mbd_mei_t))?;
    dict.set_item("mei_mbd_t", vec_to_numpy1d(py, r.mei_mbd_t))?;
    dict.set_item("mbd_mei_t2", vec_to_numpy1d(py, r.mbd_mei_t2))?;
    dict.set_item("mei_mbd_t2", vec_to_numpy1d(py, r.mei_mbd_t2))?;
    dict.set_item(
        "shape_outliers",
        r.shape_outliers
            .into_iter()
            .map(|x| x as i64)
            .collect::<Vec<i64>>(),
    )?;
    dict.set_item(
        "magnitude_outliers",
        r.magnitude_outliers
            .into_iter()
            .map(|x| x as i64)
            .collect::<Vec<i64>>(),
    )?;
    dict.set_item("mbd", vec_to_numpy1d(py, r.mbd))?;
    dict.set_item("mei", vec_to_numpy1d(py, r.mei))?;
    Ok(dict)
}

/// Depthgram functional outlier detection.
///
/// Combines Modified Band Depth (MBD) and Mean Epigraph Index (MEI) to produce
/// the depthgram diagram and identify outliers. Fully deterministic (no seed).
/// Requires at least 2 observations and at least 1 evaluation point.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Data, shape (n, m). Requires n >= 2 and m >= 1.
/// outliergram_factor : float, optional
///     Empirical factor for outliergram outlier threshold (default 1.5).
/// boxplot_factor : float, optional
///     Empirical factor for boxplot outlier threshold (default 1.5).
///
/// Returns
/// -------
/// dict
///     mbd_mei_d (n,), mei_mbd_d (n,), mbd_mei_t (n,), mei_mbd_t (n,),
///     mbd_mei_t2 (n,), mei_mbd_t2 (n,), shape_outliers (list[int]),
///     magnitude_outliers (list[int]), mbd (n,), mei (n,).
#[pyfunction]
#[pyo3(signature = (data, outliergram_factor=1.5, boxplot_factor=1.5))]
pub fn depthgram<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    outliergram_factor: f64,
    boxplot_factor: f64,
) -> PyResult<Bound<'py, PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let config = fdars_core::outliers::DepthgramConfig {
        outliergram_factor,
        boxplot_factor,
    };
    let r = to_pyresult(fdars_core::outliers::depthgram(&mat, config))?;
    depthgram_to_pydict(py, r)
}

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(detect_outliers_lrt, m)?)?;
    m.add_function(wrap_pyfunction!(detect_outliers_lrt_with_dist, m)?)?;
    m.add_function(wrap_pyfunction!(outliergram, m)?)?;
    m.add_function(wrap_pyfunction!(magnitude_shape, m)?)?;
    m.add_function(wrap_pyfunction!(tvdmss, m)?)?;
    m.add_function(wrap_pyfunction!(muod, m)?)?;
    m.add_function(wrap_pyfunction!(sequential_transform_outliers, m)?)?;
    m.add_function(wrap_pyfunction!(depthgram, m)?)?;
    Ok(())
}
