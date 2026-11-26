//! Elastic-engine options (`*_with_config`), SRSF pre-smoothing and the
//! shift / landmark-shift / continuous / affine / pairwise registration
//! methods of fdars-core 0.48.
//!
//! Registered into the existing `fdars.alignment` submodule by
//! `alignment_mod::register`; it is not a submodule of its own.

use crate::convert::*;
use crate::options::{affine_config, linear_warp_class, shift_extrapolation, warp_optim};
use fdars_core::alignment::{
    ContinuousRegistrationConfig, ContinuousRegistrationCriterion, IterativeShiftConfig,
    LandmarkLocation, LandmarkShiftConfig, RobustKarcherConfig, ShiftTemplate, SrsfSmoothing,
    WfdaChoice, WfdaConfig, WfdaCostMeasure,
};
use fdars_core::error::FdarError;
use fdars_core::matrix::{FdCurveSet, FdMatrix};
use numpy::ndarray::{Array2, Array3};
use numpy::{
    AllowTypeChange, PyArray1, PyArray2, PyArray3, PyArrayLike1, PyReadonlyArray1,
    PyReadonlyArray2, PyReadonlyArray3,
};
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};
use std::cell::RefCell;

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/// `(d, m)` array → one R^d curve: d coordinate matrices of shape `1 × m`.
fn curve_to_set(arr: PyReadonlyArray2<'_, f64>) -> PyResult<FdCurveSet> {
    let a = arr.as_array();
    let dims = a
        .rows()
        .into_iter()
        .map(|row| FdMatrix::from_column_major(row.to_vec(), 1, row.len()).map_err(to_pyerr))
        .collect::<PyResult<Vec<_>>>()?;
    Ok(FdCurveSet { dims })
}

/// `(n, d, m)` array → n single-curve sets (the input of `karcher_mean_nd*`).
fn curves_to_sets(arr: PyReadonlyArray3<'_, f64>) -> PyResult<Vec<FdCurveSet>> {
    let a = arr.as_array();
    let (n, d, m) = a.dim();
    (0..n)
        .map(|i| {
            let dims = (0..d)
                .map(|k| {
                    let row: Vec<f64> = (0..m).map(|j| a[[i, k, j]]).collect();
                    FdMatrix::from_column_major(row, 1, m).map_err(to_pyerr)
                })
                .collect::<PyResult<Vec<_>>>()?;
            Ok(FdCurveSet { dims })
        })
        .collect()
}

/// `d` vectors of length m → `(d, m)` array.
fn vecs_to_numpy2d<'py>(py: Python<'py>, rows: &[Vec<f64>]) -> Bound<'py, PyArray2<f64>> {
    let m = rows.first().map_or(0, Vec::len);
    PyArray2::from_owned_array(
        py,
        Array2::from_shape_fn((rows.len(), m), |(k, j)| rows[k][j]),
    )
}

/// d coordinate matrices of shape `n × m` → `(n, d, m)` array.
fn dims_to_numpy3d<'py>(py: Python<'py>, dims: &[FdMatrix]) -> Bound<'py, PyArray3<f64>> {
    let (n, m) = dims.first().map_or((0, 0), FdMatrix::shape);
    PyArray3::from_owned_array(
        py,
        Array3::from_shape_fn((n, dims.len(), m), |(i, k, j)| dims[k][(i, j)]),
    )
}

/// Run `run` with the `ShiftTemplate` described by a Python `template` argument:
/// `None` or `"mean"` (re-estimated mean), a 1-D array (fixed template), or a
/// callable `f(curves (n, m)) -> (m,)` evaluated on the currently registered curves.
fn with_shift_template<'py, R>(
    py: Python<'py>,
    template: Option<&Bound<'py, PyAny>>,
    run: impl FnOnce(ShiftTemplate<'_>) -> Result<R, FdarError>,
) -> PyResult<R> {
    let Some(obj) = template else {
        return to_pyresult(run(ShiftTemplate::Mean));
    };
    if let Ok(name) = obj.extract::<String>() {
        if name == "mean" {
            return to_pyresult(run(ShiftTemplate::Mean));
        }
        return Err(PyValueError::new_err(format!(
            "template must be None, 'mean', a 1-D array or a callable, got '{name}'"
        )));
    }
    if obj.is_callable() {
        let err: RefCell<Option<PyErr>> = RefCell::new(None);
        let f = |x: &FdMatrix| -> Vec<f64> {
            if err.borrow().is_some() {
                return vec![f64::NAN; x.ncols()];
            }
            match obj.call1((fdmatrix_to_numpy2d(py, x),)).and_then(|r| {
                r.extract::<PyArrayLike1<'py, f64, AllowTypeChange>>()
                    .map(|a| a.as_array().to_vec())
            }) {
                Ok(v) => v,
                Err(e) => {
                    *err.borrow_mut() = Some(e);
                    vec![f64::NAN; x.ncols()]
                }
            }
        };
        let res = run(ShiftTemplate::Custom(&f));
        if let Some(e) = err.into_inner() {
            return Err(e);
        }
        return to_pyresult(res);
    }
    let arr = obj
        .extract::<PyArrayLike1<'py, f64, AllowTypeChange>>()
        .map_err(|_| {
            PyValueError::new_err("template must be None, 'mean', a 1-D array or a callable")
        })?;
    let fixed = arr.as_array().to_vec();
    to_pyresult(run(ShiftTemplate::Fixed(&fixed)))
}

/// Run `run` with the `LandmarkLocation` described by a Python `location`
/// argument: `None` or `"mean"`, `"midrange"`, a float (fixed target) or a
/// callable `f(landmarks (n,)) -> float`.
fn with_landmark_location<'py, R>(
    py: Python<'py>,
    location: Option<&Bound<'py, PyAny>>,
    run: impl FnOnce(LandmarkLocation<'_>) -> Result<R, FdarError>,
) -> PyResult<R> {
    let Some(obj) = location else {
        return to_pyresult(run(LandmarkLocation::Mean));
    };
    if let Ok(name) = obj.extract::<String>() {
        return match name.as_str() {
            "mean" => to_pyresult(run(LandmarkLocation::Mean)),
            "midrange" => to_pyresult(run(LandmarkLocation::MidRange)),
            _ => Err(PyValueError::new_err(format!(
                "location must be None, 'mean', 'midrange', a float or a callable, got '{name}'"
            ))),
        };
    }
    if obj.is_callable() {
        let err: RefCell<Option<PyErr>> = RefCell::new(None);
        let f = |lm: &[f64]| -> f64 {
            if err.borrow().is_some() {
                return f64::NAN;
            }
            match obj
                .call1((PyArray1::from_slice(py, lm),))
                .and_then(|r| r.extract::<f64>())
            {
                Ok(v) => v,
                Err(e) => {
                    *err.borrow_mut() = Some(e);
                    f64::NAN
                }
            }
        };
        let res = run(LandmarkLocation::Custom(&f));
        if let Some(e) = err.into_inner() {
            return Err(e);
        }
        return to_pyresult(res);
    }
    let fixed = obj.extract::<f64>().map_err(|_| {
        PyValueError::new_err("location must be None, 'mean', 'midrange', a float or a callable")
    })?;
    to_pyresult(run(LandmarkLocation::Fixed(fixed)))
}

fn srsf_smoothing(smoothing: &str, passes: usize) -> PyResult<SrsfSmoothing> {
    match smoothing {
        "none" => Ok(SrsfSmoothing::None),
        "box" => Ok(SrsfSmoothing::BoxFilter { passes }),
        "spline" => Ok(SrsfSmoothing::SmoothingSpline),
        _ => Err(PyValueError::new_err(format!(
            "smoothing must be one of 'none', 'box', 'spline', got '{smoothing}'"
        ))),
    }
}

fn karcher_dict<'py>(
    py: Python<'py>,
    mean: Vec<f64>,
    mean_srsf: Vec<f64>,
    aligned_data: &FdMatrix,
    gammas: &FdMatrix,
    n_iter: usize,
    converged: bool,
) -> PyResult<Bound<'py, PyDict>> {
    let dict = PyDict::new(py);
    dict.set_item("mean", vec_to_numpy1d(py, mean))?;
    dict.set_item("mean_srsf", vec_to_numpy1d(py, mean_srsf))?;
    dict.set_item("aligned_data", fdmatrix_to_numpy2d(py, aligned_data))?;
    dict.set_item("gammas", fdmatrix_to_numpy2d(py, gammas))?;
    dict.set_item("n_iter", n_iter)?;
    dict.set_item("converged", converged)?;
    Ok(dict)
}

// ---------------------------------------------------------------------------
// *_with_config: the elastic engine with a full WarpOptimConfig
// ---------------------------------------------------------------------------

/// Pairwise elastic alignment of two curves with a configurable warp optimiser.
///
/// The ``_with_config`` twin of ``elastic_align_pair``: with the default
/// options it returns bit-identical results.
///
/// Parameters
/// ----------
/// curve1, curve2 : numpy.ndarray
///     Curves, length m (curve2 is aligned to curve1).
/// argvals : numpy.ndarray
///     Strictly increasing evaluation points, length m.
/// method : str, optional
///     Warp optimiser: ``"dp"`` (exact dynamic programming, default) or
///     ``"rbfgs"`` (Riemannian L-BFGS refinement of a coarse DP warp, fdasrsf).
/// lambda_ : float, optional
///     Penalty weight (>= 0, default 0.0).
/// penalty : str, optional
///     In-objective warp penalty: ``"l2gam"`` (default), ``"l2psi"``,
///     ``"roughness"`` or ``"geodesic"`` (the last two need ``method="rbfgs"``
///     when ``lambda_ > 0``).
/// optim_max_iter : int, optional
///     RBFGS iteration cap (default 30; ignored by DP).
/// scl : int, optional
///     RBFGS fine-grid refinement factor (default 3, >= 1).
/// nbhd_dim : int, optional
///     DP move neighbourhood size in 1..=64 (default 7; fdasrsf DP2 uses 10).
/// dp_scl : int, optional
///     DP edge-cost refinement factor in 1..=64 (default 1 = off).
/// dp_cost : str, optional
///     DP edge cost: ``"piecewise_constant"`` (default) or ``"piecewise_linear"``.
/// dp_prune : bool, optional
///     Exact DP candidate pruning (default True; results are identical).
/// band_frac : float, optional
///     Sakoe-Chiba band as a fraction of the grid (default 0.0 = off).
/// lambda_scale : str, optional
///     Convention of ``lambda_``: ``"native"`` (default), ``"dp"`` or ``"fdasrsf"``.
///
/// Returns
/// -------
/// dict
///     f_aligned (m,), gamma (m,), distance.
///
/// Raises
/// ------
/// ValueError
///     For an unknown option name or an invalid configuration.
#[pyfunction]
#[pyo3(signature = (curve1, curve2, argvals, method="dp", lambda_=0.0, penalty="l2gam", optim_max_iter=30, scl=3, nbhd_dim=7, dp_scl=1, dp_cost="piecewise_constant", dp_prune=true, band_frac=0.0, lambda_scale="native"))]
pub fn elastic_align_pair_with_config<'py>(
    py: Python<'py>,
    curve1: PyReadonlyArray1<'py, f64>,
    curve2: PyReadonlyArray1<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    method: &str,
    lambda_: f64,
    penalty: &str,
    optim_max_iter: usize,
    scl: usize,
    nbhd_dim: usize,
    dp_scl: usize,
    dp_cost: &str,
    dp_prune: bool,
    band_frac: f64,
    lambda_scale: &str,
) -> PyResult<Bound<'py, PyDict>> {
    let cfg = warp_optim(
        method,
        lambda_,
        penalty,
        optim_max_iter,
        scl,
        nbhd_dim,
        dp_scl,
        dp_cost,
        dp_prune,
        band_frac,
        lambda_scale,
    )?;
    let c1 = numpy1d_to_vec(curve1);
    let c2 = numpy1d_to_vec(curve2);
    let av = numpy1d_to_vec(argvals);
    let r = to_pyresult(fdars_core::alignment::elastic_align_pair_with_config(
        &c1, &c2, &av, &cfg,
    ))?;
    let dict = PyDict::new(py);
    dict.set_item("f_aligned", vec_to_numpy1d(py, r.f_aligned))?;
    dict.set_item("gamma", vec_to_numpy1d(py, r.gamma))?;
    dict.set_item("distance", r.distance)?;
    Ok(dict)
}

/// Elastic (Fisher-Rao) distance between two curves with a configurable warp optimiser.
///
/// The ``_with_config`` twin of ``elastic_distance``; the warp-optimiser
/// keyword arguments are those of ``elastic_align_pair_with_config``.
///
/// Returns
/// -------
/// float
///     Elastic distance.
#[pyfunction]
#[pyo3(signature = (curve1, curve2, argvals, method="dp", lambda_=0.0, penalty="l2gam", optim_max_iter=30, scl=3, nbhd_dim=7, dp_scl=1, dp_cost="piecewise_constant", dp_prune=true, band_frac=0.0, lambda_scale="native"))]
pub fn elastic_distance_with_config(
    curve1: PyReadonlyArray1<'_, f64>,
    curve2: PyReadonlyArray1<'_, f64>,
    argvals: PyReadonlyArray1<'_, f64>,
    method: &str,
    lambda_: f64,
    penalty: &str,
    optim_max_iter: usize,
    scl: usize,
    nbhd_dim: usize,
    dp_scl: usize,
    dp_cost: &str,
    dp_prune: bool,
    band_frac: f64,
    lambda_scale: &str,
) -> PyResult<f64> {
    let cfg = warp_optim(
        method,
        lambda_,
        penalty,
        optim_max_iter,
        scl,
        nbhd_dim,
        dp_scl,
        dp_cost,
        dp_prune,
        band_frac,
        lambda_scale,
    )?;
    let c1 = numpy1d_to_vec(curve1);
    let c2 = numpy1d_to_vec(curve2);
    let av = numpy1d_to_vec(argvals);
    to_pyresult(fdars_core::alignment::elastic_distance_with_config(
        &c1, &c2, &av, &cfg,
    ))
}

/// Elastic self distance matrix with a configurable warp optimiser.
///
/// The ``_with_config`` twin of ``elastic_self_distance_matrix``; the
/// warp-optimiser keyword arguments are those of
/// ``elastic_align_pair_with_config``.
///
/// Returns
/// -------
/// numpy.ndarray
///     Distance matrix, shape (n, n).
#[pyfunction]
#[pyo3(signature = (data, argvals, method="dp", lambda_=0.0, penalty="l2gam", optim_max_iter=30, scl=3, nbhd_dim=7, dp_scl=1, dp_cost="piecewise_constant", dp_prune=true, band_frac=0.0, lambda_scale="native"))]
pub fn elastic_self_distance_matrix_with_config<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    method: &str,
    lambda_: f64,
    penalty: &str,
    optim_max_iter: usize,
    scl: usize,
    nbhd_dim: usize,
    dp_scl: usize,
    dp_cost: &str,
    dp_prune: bool,
    band_frac: f64,
    lambda_scale: &str,
) -> PyResult<Bound<'py, PyArray2<f64>>> {
    let cfg = warp_optim(
        method,
        lambda_,
        penalty,
        optim_max_iter,
        scl,
        nbhd_dim,
        dp_scl,
        dp_cost,
        dp_prune,
        band_frac,
        lambda_scale,
    )?;
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let r = to_pyresult(
        fdars_core::alignment::elastic_self_distance_matrix_with_config(&mat, &av, &cfg),
    )?;
    Ok(fdmatrix_to_numpy2d(py, &r))
}

/// Elastic cross distance matrix with a configurable warp optimiser.
///
/// The ``_with_config`` twin of ``elastic_cross_distance_matrix``; the
/// warp-optimiser keyword arguments are those of
/// ``elastic_align_pair_with_config``.
///
/// Returns
/// -------
/// numpy.ndarray
///     Distance matrix, shape (n1, n2).
#[pyfunction]
#[pyo3(signature = (data1, data2, argvals, method="dp", lambda_=0.0, penalty="l2gam", optim_max_iter=30, scl=3, nbhd_dim=7, dp_scl=1, dp_cost="piecewise_constant", dp_prune=true, band_frac=0.0, lambda_scale="native"))]
pub fn elastic_cross_distance_matrix_with_config<'py>(
    py: Python<'py>,
    data1: PyReadonlyArray2<'py, f64>,
    data2: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    method: &str,
    lambda_: f64,
    penalty: &str,
    optim_max_iter: usize,
    scl: usize,
    nbhd_dim: usize,
    dp_scl: usize,
    dp_cost: &str,
    dp_prune: bool,
    band_frac: f64,
    lambda_scale: &str,
) -> PyResult<Bound<'py, PyArray2<f64>>> {
    let cfg = warp_optim(
        method,
        lambda_,
        penalty,
        optim_max_iter,
        scl,
        nbhd_dim,
        dp_scl,
        dp_cost,
        dp_prune,
        band_frac,
        lambda_scale,
    )?;
    let m1 = numpy2d_to_fdmatrix(data1)?;
    let m2 = numpy2d_to_fdmatrix(data2)?;
    let av = numpy1d_to_vec(argvals);
    let r = to_pyresult(
        fdars_core::alignment::elastic_cross_distance_matrix_with_config(&m1, &m2, &av, &cfg),
    )?;
    Ok(fdmatrix_to_numpy2d(py, &r))
}

/// Karcher (Frechet) mean under the elastic metric with a configurable warp optimiser.
///
/// The ``_with_config`` twin of ``karcher_mean``; the warp-optimiser keyword
/// arguments are those of ``elastic_align_pair_with_config``.
///
/// Returns
/// -------
/// dict
///     mean (m,), mean_srsf (m,), aligned_data (n, m), gammas (n, m),
///     n_iter, converged, and aligned_srsfs (n, m) when the core returns it.
#[pyfunction]
#[pyo3(signature = (data, argvals, max_iter=20, tol=1e-4, method="dp", lambda_=0.0, penalty="l2gam", optim_max_iter=30, scl=3, nbhd_dim=7, dp_scl=1, dp_cost="piecewise_constant", dp_prune=true, band_frac=0.0, lambda_scale="native"))]
pub fn karcher_mean_with_config<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    max_iter: usize,
    tol: f64,
    method: &str,
    lambda_: f64,
    penalty: &str,
    optim_max_iter: usize,
    scl: usize,
    nbhd_dim: usize,
    dp_scl: usize,
    dp_cost: &str,
    dp_prune: bool,
    band_frac: f64,
    lambda_scale: &str,
) -> PyResult<Bound<'py, PyDict>> {
    let cfg = warp_optim(
        method,
        lambda_,
        penalty,
        optim_max_iter,
        scl,
        nbhd_dim,
        dp_scl,
        dp_cost,
        dp_prune,
        band_frac,
        lambda_scale,
    )?;
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let r = to_pyresult(fdars_core::alignment::karcher_mean_with_config(
        &mat, &av, max_iter, tol, &cfg,
    ))?;
    let dict = karcher_dict(
        py,
        r.mean,
        r.mean_srsf,
        &r.aligned_data,
        &r.gammas,
        r.n_iter,
        r.converged,
    )?;
    if let Some(q) = &r.aligned_srsfs {
        dict.set_item("aligned_srsfs", fdmatrix_to_numpy2d(py, q))?;
    }
    Ok(dict)
}

/// Elastic Karcher median (Weiszfeld) with a configurable warp optimiser.
///
/// The ``_with_config`` twin of ``karcher_median``; the warp-optimiser
/// keyword arguments are those of ``elastic_align_pair_with_config``.
///
/// Returns
/// -------
/// dict
///     mean (m,), mean_srsf (m,), aligned_data (n, m), gammas (n, m),
///     weights (n,), n_iter, converged.
#[pyfunction]
#[pyo3(signature = (data, argvals, max_iter=20, tol=1e-3, method="dp", lambda_=0.0, penalty="l2gam", optim_max_iter=30, scl=3, nbhd_dim=7, dp_scl=1, dp_cost="piecewise_constant", dp_prune=true, band_frac=0.0, lambda_scale="native"))]
pub fn karcher_median_with_config<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    max_iter: usize,
    tol: f64,
    method: &str,
    lambda_: f64,
    penalty: &str,
    optim_max_iter: usize,
    scl: usize,
    nbhd_dim: usize,
    dp_scl: usize,
    dp_cost: &str,
    dp_prune: bool,
    band_frac: f64,
    lambda_scale: &str,
) -> PyResult<Bound<'py, PyDict>> {
    let warp = warp_optim(
        method,
        lambda_,
        penalty,
        optim_max_iter,
        scl,
        nbhd_dim,
        dp_scl,
        dp_cost,
        dp_prune,
        band_frac,
        lambda_scale,
    )?;
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let mut config = RobustKarcherConfig::default();
    config.max_iter = max_iter;
    config.tol = tol;
    config.trim_fraction = 0.0;
    let r = to_pyresult(fdars_core::alignment::karcher_median_with_config(
        &mat, &av, &config, &warp,
    ))?;
    let dict = karcher_dict(
        py,
        r.mean,
        r.mean_srsf,
        &r.aligned_data,
        &r.gammas,
        r.n_iter,
        r.converged,
    )?;
    dict.set_item("weights", vec_to_numpy1d(py, r.weights))?;
    Ok(dict)
}

/// Trimmed robust Karcher mean with a configurable warp optimiser.
///
/// The ``_with_config`` twin of ``robust_karcher_mean``; the warp-optimiser
/// keyword arguments are those of ``elastic_align_pair_with_config``.
///
/// Returns
/// -------
/// dict
///     mean (m,), mean_srsf (m,), aligned_data (n, m), gammas (n, m),
///     weights (n,), n_iter, converged.
#[pyfunction]
#[pyo3(signature = (data, argvals, max_iter=20, tol=1e-3, trim_fraction=0.1, method="dp", lambda_=0.0, penalty="l2gam", optim_max_iter=30, scl=3, nbhd_dim=7, dp_scl=1, dp_cost="piecewise_constant", dp_prune=true, band_frac=0.0, lambda_scale="native"))]
pub fn robust_karcher_mean_with_config<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    max_iter: usize,
    tol: f64,
    trim_fraction: f64,
    method: &str,
    lambda_: f64,
    penalty: &str,
    optim_max_iter: usize,
    scl: usize,
    nbhd_dim: usize,
    dp_scl: usize,
    dp_cost: &str,
    dp_prune: bool,
    band_frac: f64,
    lambda_scale: &str,
) -> PyResult<Bound<'py, PyDict>> {
    let warp = warp_optim(
        method,
        lambda_,
        penalty,
        optim_max_iter,
        scl,
        nbhd_dim,
        dp_scl,
        dp_cost,
        dp_prune,
        band_frac,
        lambda_scale,
    )?;
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let mut config = RobustKarcherConfig::default();
    config.max_iter = max_iter;
    config.tol = tol;
    config.trim_fraction = trim_fraction;
    let r = to_pyresult(fdars_core::alignment::robust_karcher_mean_with_config(
        &mat, &av, &config, &warp,
    ))?;
    let dict = karcher_dict(
        py,
        r.mean,
        r.mean_srsf,
        &r.aligned_data,
        &r.gammas,
        r.n_iter,
        r.converged,
    )?;
    dict.set_item("weights", vec_to_numpy1d(py, r.weights))?;
    Ok(dict)
}

/// Align all curves to a single target curve with a configurable warp optimiser.
///
/// The ``_with_config`` twin of ``align_to_target``; the warp-optimiser
/// keyword arguments are those of ``elastic_align_pair_with_config``.
///
/// Returns
/// -------
/// dict
///     aligned_data (n, m), gammas (n, m), distances (n,).
#[pyfunction]
#[pyo3(signature = (data, target, argvals, method="dp", lambda_=0.0, penalty="l2gam", optim_max_iter=30, scl=3, nbhd_dim=7, dp_scl=1, dp_cost="piecewise_constant", dp_prune=true, band_frac=0.0, lambda_scale="native"))]
pub fn align_to_target_with_config<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    target: PyReadonlyArray1<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    method: &str,
    lambda_: f64,
    penalty: &str,
    optim_max_iter: usize,
    scl: usize,
    nbhd_dim: usize,
    dp_scl: usize,
    dp_cost: &str,
    dp_prune: bool,
    band_frac: f64,
    lambda_scale: &str,
) -> PyResult<Bound<'py, PyDict>> {
    let cfg = warp_optim(
        method,
        lambda_,
        penalty,
        optim_max_iter,
        scl,
        nbhd_dim,
        dp_scl,
        dp_cost,
        dp_prune,
        band_frac,
        lambda_scale,
    )?;
    let mat = numpy2d_to_fdmatrix(data)?;
    let tgt = numpy1d_to_vec(target);
    let av = numpy1d_to_vec(argvals);
    let r = to_pyresult(fdars_core::alignment::align_to_target_with_config(
        &mat, &tgt, &av, &cfg,
    ))?;
    let dict = PyDict::new(py);
    dict.set_item("aligned_data", fdmatrix_to_numpy2d(py, &r.aligned_data))?;
    dict.set_item("gammas", fdmatrix_to_numpy2d(py, &r.gammas))?;
    dict.set_item("distances", vec_to_numpy1d(py, r.distances))?;
    Ok(dict)
}

/// Align a closed (periodic) curve f2 to f1 with rotation search and a configurable warp optimiser.
///
/// The ``_with_config`` twin of ``elastic_align_pair_closed``; the
/// warp-optimiser keyword arguments are those of
/// ``elastic_align_pair_with_config``.
///
/// Returns
/// -------
/// dict
///     f_aligned (m,), gamma (m,), distance, optimal_rotation.
#[pyfunction]
#[pyo3(signature = (f1, f2, argvals, method="dp", lambda_=0.0, penalty="l2gam", optim_max_iter=30, scl=3, nbhd_dim=7, dp_scl=1, dp_cost="piecewise_constant", dp_prune=true, band_frac=0.0, lambda_scale="native"))]
pub fn elastic_align_pair_closed_with_config<'py>(
    py: Python<'py>,
    f1: PyReadonlyArray1<'py, f64>,
    f2: PyReadonlyArray1<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    method: &str,
    lambda_: f64,
    penalty: &str,
    optim_max_iter: usize,
    scl: usize,
    nbhd_dim: usize,
    dp_scl: usize,
    dp_cost: &str,
    dp_prune: bool,
    band_frac: f64,
    lambda_scale: &str,
) -> PyResult<Bound<'py, PyDict>> {
    let cfg = warp_optim(
        method,
        lambda_,
        penalty,
        optim_max_iter,
        scl,
        nbhd_dim,
        dp_scl,
        dp_cost,
        dp_prune,
        band_frac,
        lambda_scale,
    )?;
    let c1 = numpy1d_to_vec(f1);
    let c2 = numpy1d_to_vec(f2);
    let av = numpy1d_to_vec(argvals);
    let r = to_pyresult(
        fdars_core::alignment::elastic_align_pair_closed_with_config(&c1, &c2, &av, &cfg),
    )?;
    let dict = PyDict::new(py);
    dict.set_item("f_aligned", vec_to_numpy1d(py, r.f_aligned))?;
    dict.set_item("gamma", vec_to_numpy1d(py, r.gamma))?;
    dict.set_item("distance", r.distance)?;
    dict.set_item("optimal_rotation", r.optimal_rotation)?;
    Ok(dict)
}

/// Elastic distance between two closed curves with a configurable warp optimiser.
///
/// The ``_with_config`` twin of ``elastic_distance_closed``; the
/// warp-optimiser keyword arguments are those of
/// ``elastic_align_pair_with_config``.
///
/// Returns
/// -------
/// float
///     Elastic distance minimised over rotations.
#[pyfunction]
#[pyo3(signature = (f1, f2, argvals, method="dp", lambda_=0.0, penalty="l2gam", optim_max_iter=30, scl=3, nbhd_dim=7, dp_scl=1, dp_cost="piecewise_constant", dp_prune=true, band_frac=0.0, lambda_scale="native"))]
pub fn elastic_distance_closed_with_config(
    f1: PyReadonlyArray1<'_, f64>,
    f2: PyReadonlyArray1<'_, f64>,
    argvals: PyReadonlyArray1<'_, f64>,
    method: &str,
    lambda_: f64,
    penalty: &str,
    optim_max_iter: usize,
    scl: usize,
    nbhd_dim: usize,
    dp_scl: usize,
    dp_cost: &str,
    dp_prune: bool,
    band_frac: f64,
    lambda_scale: &str,
) -> PyResult<f64> {
    let cfg = warp_optim(
        method,
        lambda_,
        penalty,
        optim_max_iter,
        scl,
        nbhd_dim,
        dp_scl,
        dp_cost,
        dp_prune,
        band_frac,
        lambda_scale,
    )?;
    let c1 = numpy1d_to_vec(f1);
    let c2 = numpy1d_to_vec(f2);
    let av = numpy1d_to_vec(argvals);
    to_pyresult(fdars_core::alignment::elastic_distance_closed_with_config(
        &c1, &c2, &av, &cfg,
    ))
}

/// Karcher mean for closed (periodic) curves with a configurable warp optimiser.
///
/// The ``_with_config`` twin of ``karcher_mean_closed``; the warp-optimiser
/// keyword arguments are those of ``elastic_align_pair_with_config``.
///
/// Returns
/// -------
/// dict
///     mean (m,), mean_srsf (m,), aligned_data (n, m), gammas (n, m),
///     rotations (n,), n_iter, converged.
#[pyfunction]
#[pyo3(signature = (data, argvals, max_iter=20, tol=1e-4, method="dp", lambda_=0.0, penalty="l2gam", optim_max_iter=30, scl=3, nbhd_dim=7, dp_scl=1, dp_cost="piecewise_constant", dp_prune=true, band_frac=0.0, lambda_scale="native"))]
pub fn karcher_mean_closed_with_config<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    max_iter: usize,
    tol: f64,
    method: &str,
    lambda_: f64,
    penalty: &str,
    optim_max_iter: usize,
    scl: usize,
    nbhd_dim: usize,
    dp_scl: usize,
    dp_cost: &str,
    dp_prune: bool,
    band_frac: f64,
    lambda_scale: &str,
) -> PyResult<Bound<'py, PyDict>> {
    let cfg = warp_optim(
        method,
        lambda_,
        penalty,
        optim_max_iter,
        scl,
        nbhd_dim,
        dp_scl,
        dp_cost,
        dp_prune,
        band_frac,
        lambda_scale,
    )?;
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let r = to_pyresult(fdars_core::alignment::karcher_mean_closed_with_config(
        &mat, &av, max_iter, tol, &cfg,
    ))?;
    let dict = karcher_dict(
        py,
        r.mean,
        r.mean_srsf,
        &r.aligned_data,
        &r.gammas,
        r.n_iter,
        r.converged,
    )?;
    dict.set_item("rotations", usize_vec_to_numpy1d(py, r.rotations))?;
    Ok(dict)
}

/// Landmark-constrained elastic alignment with a configurable warp optimiser.
///
/// The ``_with_config`` twin of ``elastic_align_pair_constrained``: the warp
/// maps ``landmark_targets[k]`` (time on f1) to ``landmark_sources[k]`` (time
/// on f2). The warp-optimiser keyword arguments are those of
/// ``elastic_align_pair_with_config``; ``band_frac`` must be 0.
///
/// Returns
/// -------
/// dict
///     f_aligned (m,), gamma (m,), distance, enforced_landmarks (K, 2) of
///     the (target, source) pairs actually enforced after snapping to the grid.
#[pyfunction]
#[pyo3(signature = (f1, f2, argvals, landmark_targets, landmark_sources, method="dp", lambda_=0.0, penalty="l2gam", optim_max_iter=30, scl=3, nbhd_dim=7, dp_scl=1, dp_cost="piecewise_constant", dp_prune=true, band_frac=0.0, lambda_scale="native"))]
pub fn elastic_align_pair_constrained_with_config<'py>(
    py: Python<'py>,
    f1: PyReadonlyArray1<'py, f64>,
    f2: PyReadonlyArray1<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    landmark_targets: PyArrayLike1<'py, f64, AllowTypeChange>,
    landmark_sources: PyArrayLike1<'py, f64, AllowTypeChange>,
    method: &str,
    lambda_: f64,
    penalty: &str,
    optim_max_iter: usize,
    scl: usize,
    nbhd_dim: usize,
    dp_scl: usize,
    dp_cost: &str,
    dp_prune: bool,
    band_frac: f64,
    lambda_scale: &str,
) -> PyResult<Bound<'py, PyDict>> {
    let cfg = warp_optim(
        method,
        lambda_,
        penalty,
        optim_max_iter,
        scl,
        nbhd_dim,
        dp_scl,
        dp_cost,
        dp_prune,
        band_frac,
        lambda_scale,
    )?;
    let c1 = numpy1d_to_vec(f1);
    let c2 = numpy1d_to_vec(f2);
    let av = numpy1d_to_vec(argvals);
    let lt = landmark_targets.as_array().to_vec();
    let ls = landmark_sources.as_array().to_vec();
    let pairs: Vec<(f64, f64)> = lt.into_iter().zip(ls).collect();
    let r = to_pyresult(
        fdars_core::alignment::elastic_align_pair_constrained_with_config(
            &c1, &c2, &av, &pairs, &cfg,
        ),
    )?;
    let k = r.enforced_landmarks.len();
    let enforced = PyArray2::from_owned_array(
        py,
        Array2::from_shape_fn((k, 2), |(i, c)| {
            let (t, s) = r.enforced_landmarks[i];
            if c == 0 {
                t
            } else {
                s
            }
        }),
    );
    let dict = PyDict::new(py);
    dict.set_item("f_aligned", vec_to_numpy1d(py, r.f_aligned))?;
    dict.set_item("gamma", vec_to_numpy1d(py, r.gamma))?;
    dict.set_item("distance", r.distance)?;
    dict.set_item("enforced_landmarks", enforced)?;
    Ok(dict)
}

/// Elastic alignment of two R^d curves under one shared warp, with a configurable warp optimiser.
///
/// Parameters
/// ----------
/// f1, f2 : numpy.ndarray
///     Curves, shape (d, m) (row = coordinate); f2 is aligned to f1.
/// argvals : numpy.ndarray
///     Strictly increasing evaluation points, length m.
///
/// The warp-optimiser keyword arguments are those of
/// ``elastic_align_pair_with_config``.
///
/// Returns
/// -------
/// dict
///     f_aligned (d, m), gamma (m,), distance.
#[pyfunction]
#[pyo3(signature = (f1, f2, argvals, method="dp", lambda_=0.0, penalty="l2gam", optim_max_iter=30, scl=3, nbhd_dim=7, dp_scl=1, dp_cost="piecewise_constant", dp_prune=true, band_frac=0.0, lambda_scale="native"))]
pub fn elastic_align_pair_nd_with_config<'py>(
    py: Python<'py>,
    f1: PyReadonlyArray2<'py, f64>,
    f2: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    method: &str,
    lambda_: f64,
    penalty: &str,
    optim_max_iter: usize,
    scl: usize,
    nbhd_dim: usize,
    dp_scl: usize,
    dp_cost: &str,
    dp_prune: bool,
    band_frac: f64,
    lambda_scale: &str,
) -> PyResult<Bound<'py, PyDict>> {
    let cfg = warp_optim(
        method,
        lambda_,
        penalty,
        optim_max_iter,
        scl,
        nbhd_dim,
        dp_scl,
        dp_cost,
        dp_prune,
        band_frac,
        lambda_scale,
    )?;
    let s1 = curve_to_set(f1)?;
    let s2 = curve_to_set(f2)?;
    let av = numpy1d_to_vec(argvals);
    let r = to_pyresult(fdars_core::alignment::elastic_align_pair_nd_with_config(
        &s1, &s2, &av, &cfg,
    ))?;
    let dict = PyDict::new(py);
    dict.set_item("f_aligned", vecs_to_numpy2d(py, &r.f_aligned))?;
    dict.set_item("gamma", vec_to_numpy1d(py, r.gamma))?;
    dict.set_item("distance", r.distance)?;
    Ok(dict)
}

/// Elastic distance between two R^d curves with a configurable warp optimiser.
///
/// ``f1``, ``f2`` have shape (d, m); the warp-optimiser keyword arguments are
/// those of ``elastic_align_pair_with_config``.
///
/// Returns
/// -------
/// float
///     Elastic distance under the shared optimal warp.
#[pyfunction]
#[pyo3(signature = (f1, f2, argvals, method="dp", lambda_=0.0, penalty="l2gam", optim_max_iter=30, scl=3, nbhd_dim=7, dp_scl=1, dp_cost="piecewise_constant", dp_prune=true, band_frac=0.0, lambda_scale="native"))]
pub fn elastic_distance_nd_with_config(
    f1: PyReadonlyArray2<'_, f64>,
    f2: PyReadonlyArray2<'_, f64>,
    argvals: PyReadonlyArray1<'_, f64>,
    method: &str,
    lambda_: f64,
    penalty: &str,
    optim_max_iter: usize,
    scl: usize,
    nbhd_dim: usize,
    dp_scl: usize,
    dp_cost: &str,
    dp_prune: bool,
    band_frac: f64,
    lambda_scale: &str,
) -> PyResult<f64> {
    let cfg = warp_optim(
        method,
        lambda_,
        penalty,
        optim_max_iter,
        scl,
        nbhd_dim,
        dp_scl,
        dp_cost,
        dp_prune,
        band_frac,
        lambda_scale,
    )?;
    let s1 = curve_to_set(f1)?;
    let s2 = curve_to_set(f2)?;
    let av = numpy1d_to_vec(argvals);
    to_pyresult(fdars_core::alignment::elastic_distance_nd_with_config(
        &s1, &s2, &av, &cfg,
    ))
}

/// Karcher mean of R^d curves under shared warps, with a configurable warp optimiser.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Curves, shape (n, d, m), n >= 2.
/// argvals : numpy.ndarray
///     Strictly increasing evaluation points, length m.
/// max_iter : int, optional
///     Maximum Karcher iterations (default 20).
/// tol : float, optional
///     Convergence tolerance (default 1e-4).
///
/// The warp-optimiser keyword arguments are those of
/// ``elastic_align_pair_with_config``.
///
/// Returns
/// -------
/// dict
///     mean (d, m), mean_srsf (d, m), gammas (n, m), aligned_data (n, d, m),
///     n_iter, converged.
#[pyfunction]
#[pyo3(signature = (data, argvals, max_iter=20, tol=1e-4, method="dp", lambda_=0.0, penalty="l2gam", optim_max_iter=30, scl=3, nbhd_dim=7, dp_scl=1, dp_cost="piecewise_constant", dp_prune=true, band_frac=0.0, lambda_scale="native"))]
pub fn karcher_mean_nd_with_config<'py>(
    py: Python<'py>,
    data: PyReadonlyArray3<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    max_iter: usize,
    tol: f64,
    method: &str,
    lambda_: f64,
    penalty: &str,
    optim_max_iter: usize,
    scl: usize,
    nbhd_dim: usize,
    dp_scl: usize,
    dp_cost: &str,
    dp_prune: bool,
    band_frac: f64,
    lambda_scale: &str,
) -> PyResult<Bound<'py, PyDict>> {
    let cfg = warp_optim(
        method,
        lambda_,
        penalty,
        optim_max_iter,
        scl,
        nbhd_dim,
        dp_scl,
        dp_cost,
        dp_prune,
        band_frac,
        lambda_scale,
    )?;
    let sets = curves_to_sets(data)?;
    let av = numpy1d_to_vec(argvals);
    let r = to_pyresult(fdars_core::alignment::karcher_mean_nd_with_config(
        &sets, &av, max_iter, tol, &cfg,
    ))?;
    let dict = PyDict::new(py);
    dict.set_item("mean", vecs_to_numpy2d(py, &r.mean))?;
    dict.set_item("mean_srsf", vecs_to_numpy2d(py, &r.mean_srsf))?;
    dict.set_item("gammas", fdmatrix_to_numpy2d(py, &r.gammas))?;
    dict.set_item("aligned_data", dims_to_numpy3d(py, &r.aligned_data))?;
    dict.set_item("n_iter", r.n_iter)?;
    dict.set_item("converged", r.converged)?;
    Ok(dict)
}

// ---------------------------------------------------------------------------
// SRSF pre-smoothing
// ---------------------------------------------------------------------------

/// SRSF transform of every curve after optional pre-smoothing (fdasrvf semantics).
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Curves, shape (n, m).
/// argvals : numpy.ndarray
///     Evaluation points, length m.
/// smoothing : str, optional
///     ``"none"`` (default; identical to ``srsf_transform`` row by row),
///     ``"box"`` (fdasrvf ``smooth.data``: ``passes`` sweeps of the
///     (1, 2, 1)/4 filter, endpoints fixed; m >= 3) or ``"spline"`` (per-curve
///     GCV cubic smoothing spline, fdasrvf ``f_to_srvf(smooth=TRUE)``; m >= 4).
/// passes : int, optional
///     Number of box-filter sweeps (default 1; ignored unless ``"box"``).
///
/// Returns
/// -------
/// numpy.ndarray
///     SRSFs, shape (n, m).
#[pyfunction]
#[pyo3(signature = (data, argvals, smoothing="none", passes=1))]
pub fn srsf_transform_smoothed<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    smoothing: &str,
    passes: usize,
) -> PyResult<Bound<'py, PyArray2<f64>>> {
    let s = srsf_smoothing(smoothing, passes)?;
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let r = to_pyresult(fdars_core::alignment::srsf_transform_smoothed(
        &mat, &av, &s,
    ))?;
    Ok(fdmatrix_to_numpy2d(py, &r))
}

/// Pre-smoothed curves, the input that ``srsf_transform_smoothed`` differentiates.
///
/// Parameters are those of ``srsf_transform_smoothed``.
///
/// Returns
/// -------
/// numpy.ndarray
///     Smoothed curves, shape (n, m).
#[pyfunction]
#[pyo3(signature = (data, argvals, smoothing="none", passes=1))]
pub fn srsf_presmooth<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    smoothing: &str,
    passes: usize,
) -> PyResult<Bound<'py, PyArray2<f64>>> {
    let s = srsf_smoothing(smoothing, passes)?;
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let r = to_pyresult(fdars_core::alignment::srsf_presmooth(&mat, &av, &s))?;
    Ok(fdmatrix_to_numpy2d(py, &r))
}

// ---------------------------------------------------------------------------
// Shift and landmark-shift registration
// ---------------------------------------------------------------------------

/// Shift every curve rigidly in time: ``g_i(t) = f_i(t - shifts[i])``.
///
/// The counterpart of scikit-fda ``FData.shift(-delta, ...)`` (opposite sign).
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Curves, shape (n, m).
/// argvals : numpy.ndarray
///     Strictly increasing evaluation points, length m >= 2.
/// shifts : numpy.ndarray
///     Shifts delta_i, length n (positive moves a curve to the right).
/// extrapolation : str, optional
///     Out-of-domain values: ``"boundary"`` (clamp, default), ``"linear"``,
///     ``"periodic"`` or ``"zeros"``.
/// restrict_domain : bool, optional
///     Keep only the grid points observed by every shifted curve (default False).
///
/// Returns
/// -------
/// dict
///     data (n, m'), argvals (m',).
#[pyfunction]
#[pyo3(signature = (data, argvals, shifts, extrapolation="boundary", restrict_domain=false))]
pub fn shift_curves<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    shifts: PyArrayLike1<'py, f64, AllowTypeChange>,
    extrapolation: &str,
    restrict_domain: bool,
) -> PyResult<Bound<'py, PyDict>> {
    let ext = shift_extrapolation(extrapolation)?;
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let d = shifts.as_array().to_vec();
    let r = to_pyresult(fdars_core::alignment::shift_curves(
        &mat,
        &av,
        &d,
        ext,
        restrict_domain,
    ))?;
    let dict = PyDict::new(py);
    dict.set_item("data", fdmatrix_to_numpy2d(py, &r.data))?;
    dict.set_item("argvals", vec_to_numpy1d(py, r.argvals))?;
    Ok(dict)
}

/// Iterative least-squares shift registration to a template (scikit-fda LeastSquaresShiftRegistration).
///
/// Newton iterations on ``sum_i ||f_i(t - delta_i) - template||^2``; the
/// registered curves are ``f_i(t - shifts[i])``.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Curves, shape (n, m).
/// argvals : numpy.ndarray
///     Strictly increasing evaluation points, length m.
/// template : None, str, numpy.ndarray or callable, optional
///     ``None`` / ``"mean"`` (re-estimated cross-sectional mean, default), a
///     fixed template of length m, or ``f(curves (n, m)) -> (m,)`` applied to
///     the currently shifted curves on every iteration.
/// max_iter : int, optional
///     Maximum Newton iterations (default 5, scikit-fda).
/// tol : float, optional
///     Stop when ``max_i |delta_i change| <= tol`` (default 1e-2).
/// step_size : float, optional
///     Newton step multiplier (default 1.0).
/// restrict_domain : bool, optional
///     Integrate over / return the commonly observed sub-grid (default False).
/// extrapolation : str, optional
///     ``"boundary"`` (default), ``"linear"``, ``"periodic"`` or ``"zeros"``.
/// initial : numpy.ndarray, optional
///     Initial shifts, length n (default zeros).
///
/// Returns
/// -------
/// dict
///     registered_data (n, m'), registered_argvals (m',), shifts (n,),
///     template (m,), n_iter, converged.
#[pyfunction]
#[pyo3(signature = (data, argvals, template=None, max_iter=5, tol=1e-2, step_size=1.0, restrict_domain=false, extrapolation="boundary", initial=None))]
pub fn iterative_shift_registration<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    template: Option<&Bound<'py, PyAny>>,
    max_iter: usize,
    tol: f64,
    step_size: f64,
    restrict_domain: bool,
    extrapolation: &str,
    initial: Option<PyArrayLike1<'py, f64, AllowTypeChange>>,
) -> PyResult<Bound<'py, PyDict>> {
    let mut config = IterativeShiftConfig::default();
    config.max_iter = max_iter;
    config.tol = tol;
    config.step_size = step_size;
    config.restrict_domain = restrict_domain;
    config.extrapolation = shift_extrapolation(extrapolation)?;
    config.initial = initial.map(|a| a.as_array().to_vec());
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let r = with_shift_template(py, template, |t| {
        fdars_core::alignment::iterative_shift_registration(&mat, &av, t, &config)
    })?;
    let dict = PyDict::new(py);
    dict.set_item(
        "registered_data",
        fdmatrix_to_numpy2d(py, &r.registered_data),
    )?;
    dict.set_item(
        "registered_argvals",
        vec_to_numpy1d(py, r.registered_argvals),
    )?;
    dict.set_item("shifts", vec_to_numpy1d(py, r.shifts))?;
    dict.set_item("template", vec_to_numpy1d(py, r.template))?;
    dict.set_item("n_iter", r.n_iter)?;
    dict.set_item("converged", r.converged)?;
    Ok(dict)
}

/// Shifts that move each curve's landmark onto a common target: ``delta_i = tau - t_i``.
///
/// Equals minus scikit-fda ``landmark_shift_deltas`` (fdars sign convention).
///
/// Parameters
/// ----------
/// landmarks : numpy.ndarray
///     One landmark position per curve, length n.
/// location : None, str, float or callable, optional
///     Target tau: ``None`` / ``"mean"`` (default), ``"midrange"``
///     ((max + min) / 2), a fixed float, or ``f(landmarks (n,)) -> float``.
///
/// Returns
/// -------
/// numpy.ndarray
///     Shifts, length n.
#[pyfunction]
#[pyo3(signature = (landmarks, location=None))]
pub fn landmark_shift_deltas<'py>(
    py: Python<'py>,
    landmarks: PyArrayLike1<'py, f64, AllowTypeChange>,
    location: Option<&Bound<'py, PyAny>>,
) -> PyResult<Bound<'py, PyArray1<f64>>> {
    let lm = landmarks.as_array().to_vec();
    let d = with_landmark_location(py, location, |loc| {
        fdars_core::alignment::landmark_shift_deltas(&lm, loc)
    })?;
    Ok(vec_to_numpy1d(py, d))
}

/// Least-squares common shift per curve for several landmarks: ``delta_i = mean_k(tau_k - t_ik)``.
///
/// Parameters
/// ----------
/// landmarks : numpy.ndarray or list
///     Landmark positions, a 2-D (n, K) array or a list of n 1-D arrays of
///     equal length K.
/// targets : numpy.ndarray, optional
///     Target positions tau, length K (default: per-landmark mean over curves).
///
/// Returns
/// -------
/// numpy.ndarray
///     Shifts, length n.
#[pyfunction]
#[pyo3(signature = (landmarks, targets=None))]
pub fn landmark_shift_deltas_multi<'py>(
    py: Python<'py>,
    landmarks: &Bound<'py, PyAny>,
    targets: Option<PyArrayLike1<'py, f64, AllowTypeChange>>,
) -> PyResult<Bound<'py, PyArray1<f64>>> {
    let lm: Vec<Vec<f64>> = if let Ok(list) = landmarks.cast::<PyList>() {
        extract_ragged_vecs(list, "landmark_shift_deltas_multi")?
    } else {
        let arr = landmarks.extract::<PyReadonlyArray2<f64>>().map_err(|_| {
            PyValueError::new_err(
                "landmark_shift_deltas_multi: landmarks must be a 2-D (n, K) float array \
                     or a list of 1-D arrays",
            )
        })?;
        arr.as_array()
            .rows()
            .into_iter()
            .map(|r| r.to_vec())
            .collect()
    };
    let tg = targets.map(|t| t.as_array().to_vec());
    let d = to_pyresult(fdars_core::alignment::landmark_shift_deltas_multi(
        &lm,
        tg.as_deref(),
    ))?;
    Ok(vec_to_numpy1d(py, d))
}

/// Landmark shift registration: shift each curve so its landmark lands on a common target.
///
/// scikit-fda ``landmark_shift_registration``; registered curves are
/// ``f_i(t - shifts[i])`` with ``shifts[i] = target - landmarks[i]``.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Curves, shape (n, m).
/// argvals : numpy.ndarray
///     Strictly increasing evaluation points, length m.
/// landmarks : numpy.ndarray
///     One landmark position per curve, length n.
/// location : None, str, float or callable, optional
///     Target, as in ``landmark_shift_deltas`` (default mean).
/// extrapolation : str, optional
///     ``"boundary"`` (default), ``"linear"``, ``"periodic"`` or ``"zeros"``.
/// restrict_domain : bool, optional
///     Keep only the commonly observed grid points (default False).
///
/// Returns
/// -------
/// dict
///     registered_data (n, m'), registered_argvals (m',), shifts (n,), target.
#[pyfunction]
#[pyo3(signature = (data, argvals, landmarks, location=None, extrapolation="boundary", restrict_domain=false))]
pub fn landmark_shift_registration<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    landmarks: PyArrayLike1<'py, f64, AllowTypeChange>,
    location: Option<&Bound<'py, PyAny>>,
    extrapolation: &str,
    restrict_domain: bool,
) -> PyResult<Bound<'py, PyDict>> {
    let mut config = LandmarkShiftConfig::default();
    config.extrapolation = shift_extrapolation(extrapolation)?;
    config.restrict_domain = restrict_domain;
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let lm = landmarks.as_array().to_vec();
    let r = with_landmark_location(py, location, |loc| {
        fdars_core::alignment::landmark_shift_registration(&mat, &av, &lm, loc, &config)
    })?;
    let dict = PyDict::new(py);
    dict.set_item(
        "registered_data",
        fdmatrix_to_numpy2d(py, &r.registered_data),
    )?;
    dict.set_item(
        "registered_argvals",
        vec_to_numpy1d(py, r.registered_argvals),
    )?;
    dict.set_item("shifts", vec_to_numpy1d(py, r.shifts))?;
    dict.set_item("target", r.target)?;
    Ok(dict)
}

// ---------------------------------------------------------------------------
// Continuous (Ramsay-Li) registration
// ---------------------------------------------------------------------------

/// Ramsay-Li continuous registration with smooth monotone warps (R fda register.fd).
///
/// Each curve is warped by ``h_i(t) = a + (b - a) F_i(t) / F_i(b)``,
/// ``F_i(t) = int_a^t exp W_i``, ``W_i`` a clamped B-spline expansion, chosen
/// to minimise the least-squares or minimum-eigenvalue criterion against the
/// target plus ``lambda_ * int (D^L W_i)^2``.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Curves, shape (n, m), m >= 4.
/// argvals : numpy.ndarray
///     Strictly increasing evaluation points, length m.
/// target : numpy.ndarray, optional
///     Target curve on argvals (default: cross-sectional mean).
/// criterion : str, optional
///     ``"min_eigenvalue"`` (Ramsay-Li, R ``crit=2``, default) or
///     ``"least_squares"`` (R ``crit=1``).
/// nbasis : int, optional
///     Number of W basis functions (default 6, or 2 with ``r_defaults``).
/// norder : int, optional
///     B-spline order of W (default 4, or 2 with ``r_defaults``).
/// lambda_ : float, optional
///     Roughness penalty weight (default 0.0).
/// lfd_order : int, optional
///     Derivative order of the penalty, < norder (default 2, or 0 with
///     ``r_defaults``).
/// max_iter : int, optional
///     Gauss-Newton iterations per curve (default 50, or 20 with
///     ``r_defaults``; 0 returns identity warps).
/// tol : float, optional
///     Relative criterion-decrease tolerance (default 1e-8).
/// n_fine : int, optional
///     Fine-grid size of the criterion (default ``max(201, m)``).
/// max_template_iter : int, optional
///     Procrustes passes re-estimating the mean target (default 1).
/// template_tol : float, optional
///     Relative target-change tolerance of those passes (default 1e-4).
/// initial_coefficients : numpy.ndarray, optional
///     Initial W coefficients, shape (n, nbasis); column 0 is the initial
///     shift when ``periodic``.
/// periodic : bool, optional
///     Periodic registration with a free time shift per curve (R
///     ``periodic=TRUE``; curves are one period on [a, b]). Default False.
/// r_defaults : bool, optional
///     Start from R ``register.fd``'s defaults (nbasis 2, norder 2,
///     lfd_order 0, max_iter 20); explicitly passed values still win.
///
/// Returns
/// -------
/// dict
///     registered_data (n, m), warps (n, m), w_coefficients (n, nbasis),
///     w_knots (nbasis + norder,), criterion (n,), target (m,), n_iter (n,),
///     converged (n,), n_template_iter, shift (n,).
///
/// Notes
/// -----
/// ``converged[i]`` is also True when the Levenberg-Marquardt step control
/// stalls (no damping found a strictly decreasing step), not only when the
/// relative decrease fell below ``tol``.
#[pyfunction]
#[pyo3(signature = (data, argvals, target=None, criterion="min_eigenvalue", nbasis=None, norder=None, lambda_=0.0, lfd_order=None, max_iter=None, tol=1e-8, n_fine=None, max_template_iter=1, template_tol=1e-4, initial_coefficients=None, periodic=false, r_defaults=false))]
pub fn continuous_registration<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    target: Option<PyReadonlyArray1<'py, f64>>,
    criterion: &str,
    nbasis: Option<usize>,
    norder: Option<usize>,
    lambda_: f64,
    lfd_order: Option<usize>,
    max_iter: Option<usize>,
    tol: f64,
    n_fine: Option<usize>,
    max_template_iter: usize,
    template_tol: f64,
    initial_coefficients: Option<PyReadonlyArray2<'py, f64>>,
    periodic: bool,
    r_defaults: bool,
) -> PyResult<Bound<'py, PyDict>> {
    let mut cfg = if r_defaults {
        ContinuousRegistrationConfig::r_defaults()
    } else {
        ContinuousRegistrationConfig::default()
    };
    cfg.criterion = match criterion {
        "min_eigenvalue" => ContinuousRegistrationCriterion::MinEigenvalue,
        "least_squares" => ContinuousRegistrationCriterion::LeastSquares,
        _ => {
            return Err(PyValueError::new_err(format!(
                "criterion must be one of 'min_eigenvalue', 'least_squares', got '{criterion}'"
            )))
        }
    };
    if let Some(v) = nbasis {
        cfg.nbasis = v;
    }
    if let Some(v) = norder {
        cfg.norder = v;
    }
    if let Some(v) = lfd_order {
        cfg.lfd_order = v;
    }
    if let Some(v) = max_iter {
        cfg.max_iter = v;
    }
    cfg.lambda = lambda_;
    cfg.tol = tol;
    cfg.n_fine = n_fine;
    cfg.max_template_iter = max_template_iter;
    cfg.template_tol = template_tol;
    cfg.initial_coefficients = initial_coefficients.map(numpy2d_to_fdmatrix).transpose()?;
    cfg.periodic = periodic;
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let tg = target.map(numpy1d_to_vec);
    let r = to_pyresult(fdars_core::alignment::continuous_registration(
        &mat,
        &av,
        tg.as_deref(),
        &cfg,
    ))?;
    let dict = PyDict::new(py);
    dict.set_item(
        "registered_data",
        fdmatrix_to_numpy2d(py, &r.registered_data),
    )?;
    dict.set_item("warps", fdmatrix_to_numpy2d(py, &r.warps))?;
    dict.set_item("w_coefficients", fdmatrix_to_numpy2d(py, &r.w_coefficients))?;
    dict.set_item("w_knots", vec_to_numpy1d(py, r.w_knots))?;
    dict.set_item("criterion", vec_to_numpy1d(py, r.criterion))?;
    dict.set_item("target", vec_to_numpy1d(py, r.target))?;
    dict.set_item("n_iter", usize_vec_to_numpy1d(py, r.n_iter))?;
    dict.set_item("converged", bool_vec_to_numpy1d(py, r.converged))?;
    dict.set_item("n_template_iter", r.n_template_iter)?;
    dict.set_item("shift", vec_to_numpy1d(py, r.shift))?;
    Ok(dict)
}

// ---------------------------------------------------------------------------
// Shift / dilation / affine registration
// ---------------------------------------------------------------------------

/// Shift, dilation or affine warp registration ``h_i(t) = a_i t + b_i`` to a template (fdacluster).
///
/// The registered curves are ``g_i(s) = f_i((s - b_i) / a_i)``; if
/// ``f_i(t) = mu(a_i t + b_i)`` the registration recovers ``(a_i, b_i)`` (up
/// to the common frame fixed by centring when the template is re-estimated).
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Curves, shape (n, m).
/// argvals : numpy.ndarray
///     Strictly increasing evaluation points, length m.
/// warp_class : str, optional
///     ``"affine"`` (default), ``"shift"``, ``"dilation"`` (about t = 0) or ``"none"``.
/// template : None, str, numpy.ndarray or callable, optional
///     ``None`` / ``"mean"`` (re-estimated mean, default), a fixed template of
///     length m, or ``f(registered (n, m)) -> (m,)``.
/// metric : str, optional
///     ``"l2"`` (default), ``"normalized_l2"`` or ``"pearson"``.
/// domain : str, optional
///     ``"full"`` (default) or ``"overlap"`` (L2 is rejected there for
///     dilation / affine warps).
/// extrapolation : str, optional
///     ``"boundary"`` (default), ``"linear"``, ``"periodic"`` or ``"zeros"``.
/// max_dilation : float, optional
///     Dilation bound, a in [1 - max_dilation, 1 + max_dilation] (default 0.15).
/// max_shift : float, optional
///     Shift bound as a fraction of the domain length (default 0.15).
/// grid_size : int, optional
///     Coarse grid points per parameter (default 21, >= 3).
/// max_iter : int, optional
///     Template / warp iterations (default 20).
/// tol : float, optional
///     Parameter-change tolerance (default 1e-6).
/// center_warps : bool, optional
///     Centre warps to mean dilation 1 / mean shift 0 (default True; ignored
///     for a fixed template).
/// optim_tol : float, optional
///     Relative tolerance of the local refinement (default 1e-10).
///
/// Returns
/// -------
/// dict
///     registered_data (n, m), dilations (n,), shifts (n,), template (m,),
///     distances (n,), n_iter, converged.
#[pyfunction]
#[pyo3(signature = (data, argvals, warp_class="affine", template=None, metric="l2", domain="full", extrapolation="boundary", max_dilation=0.15, max_shift=0.15, grid_size=21, max_iter=20, tol=1e-6, center_warps=true, optim_tol=1e-10))]
pub fn affine_registration<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    warp_class: &str,
    template: Option<&Bound<'py, PyAny>>,
    metric: &str,
    domain: &str,
    extrapolation: &str,
    max_dilation: f64,
    max_shift: f64,
    grid_size: usize,
    max_iter: usize,
    tol: f64,
    center_warps: bool,
    optim_tol: f64,
) -> PyResult<Bound<'py, PyDict>> {
    let class = linear_warp_class(warp_class)?;
    let cfg = affine_config(
        metric,
        domain,
        extrapolation,
        max_dilation,
        max_shift,
        grid_size,
        max_iter,
        tol,
        center_warps,
        optim_tol,
    )?;
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let r = with_shift_template(py, template, |t| {
        fdars_core::alignment::affine_registration(&mat, &av, class, t, &cfg)
    })?;
    let dict = PyDict::new(py);
    dict.set_item(
        "registered_data",
        fdmatrix_to_numpy2d(py, &r.registered_data),
    )?;
    dict.set_item("dilations", vec_to_numpy1d(py, r.dilations))?;
    dict.set_item("shifts", vec_to_numpy1d(py, r.shifts))?;
    dict.set_item("template", vec_to_numpy1d(py, r.template))?;
    dict.set_item("distances", vec_to_numpy1d(py, r.distances))?;
    dict.set_item("n_iter", r.n_iter)?;
    dict.set_item("converged", r.converged)?;
    Ok(dict)
}

/// Apply linear warps: ``out[i, j] = f_i((t_j - shifts[i]) / dilations[i])``.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Curves, shape (n, m).
/// argvals : numpy.ndarray
///     Strictly increasing evaluation points, length m.
/// dilations : numpy.ndarray
///     Positive dilations a_i, length n.
/// shifts : numpy.ndarray
///     Shifts b_i, length n.
/// extrapolation : str, optional
///     ``"boundary"`` (default), ``"linear"``, ``"periodic"`` or ``"zeros"``.
///
/// Returns
/// -------
/// numpy.ndarray
///     Warped curves, shape (n, m).
#[pyfunction]
#[pyo3(signature = (data, argvals, dilations, shifts, extrapolation="boundary"))]
pub fn affine_warp_curves<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    dilations: PyArrayLike1<'py, f64, AllowTypeChange>,
    shifts: PyArrayLike1<'py, f64, AllowTypeChange>,
    extrapolation: &str,
) -> PyResult<Bound<'py, PyArray2<f64>>> {
    let ext = shift_extrapolation(extrapolation)?;
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let a = dilations.as_array().to_vec();
    let b = shifts.as_array().to_vec();
    let r = to_pyresult(fdars_core::alignment::affine_warp_curves(
        &mat, &av, &a, &b, ext,
    ))?;
    Ok(fdmatrix_to_numpy2d(py, &r))
}

// ---------------------------------------------------------------------------
// Tang-Mueller pairwise synchronisation
// ---------------------------------------------------------------------------

/// Tang-Mueller pairwise curve synchronisation (R fdapace WFDA).
///
/// Each curve's warp is the average of monotone pairwise warps to a random
/// subset of partner curves, so no template is needed.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Curves, shape (n, m), n >= 2, m >= 3.
/// argvals : numpy.ndarray
///     Strictly increasing evaluation points, length m.
/// choice : str, optional
///     ``"truncated"`` (drop partners above the cost quantile, default) or
///     ``"weighted"`` (inverse-cost weights).
/// subset_prop : float, optional
///     Fraction of the other curves used as partners, in (0, 1] (default 0.5).
/// nknots : int, optional
///     Interior knots of the piecewise-linear pairwise warps, 1..=7 (default 2).
/// is_pwl : bool, optional
///     Piecewise-linear knot optimisation (default True) instead of random search.
/// seed : int, optional
///     Seed of the partner draws (default 666, fdapace).
/// lambda_ : float, optional
///     Warp penalty (default None = fdapace's data-driven value).
/// cost_measure : str, optional
///     ``"pairwise_fit"`` (default) or ``"fdapace_legacy"`` (reproduces fdapace 0.6.0).
/// truncation_quantile : float, optional
///     Cost quantile of the truncated mean, in (0, 1] (default 0.9).
/// max_evals : int, optional
///     Optimiser evaluation budget per pairwise warp (default 4000).
/// optim_tol : float, optional
///     Optimiser tolerance (default 1e-12).
///
/// Returns
/// -------
/// dict
///     warps (n, m), inverse_warps (n, m), aligned (n, m), costs (n,),
///     lambda, partners (list of int arrays), pairwise_warps (list of (K, m)),
///     pairwise_costs (list of (K,)).
#[pyfunction]
#[pyo3(signature = (data, argvals, choice="truncated", subset_prop=0.5, nknots=2, is_pwl=true, seed=666, lambda_=None, cost_measure="pairwise_fit", truncation_quantile=0.9, max_evals=4000, optim_tol=1e-12))]
pub fn pairwise_synchronization<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    choice: &str,
    subset_prop: f64,
    nknots: usize,
    is_pwl: bool,
    seed: u64,
    lambda_: Option<f64>,
    cost_measure: &str,
    truncation_quantile: f64,
    max_evals: usize,
    optim_tol: f64,
) -> PyResult<Bound<'py, PyDict>> {
    let mut cfg = WfdaConfig::default();
    cfg.choice = match choice {
        "truncated" => WfdaChoice::Truncated,
        "weighted" => WfdaChoice::Weighted,
        _ => {
            return Err(PyValueError::new_err(format!(
                "choice must be one of 'truncated', 'weighted', got '{choice}'"
            )))
        }
    };
    cfg.cost_measure = match cost_measure {
        "pairwise_fit" => WfdaCostMeasure::PairwiseFit,
        "fdapace_legacy" => WfdaCostMeasure::FdapaceLegacy,
        _ => {
            return Err(PyValueError::new_err(format!(
                "cost_measure must be one of 'pairwise_fit', 'fdapace_legacy', got '{cost_measure}'"
            )))
        }
    };
    cfg.subset_prop = subset_prop;
    cfg.nknots = nknots;
    cfg.is_pwl = is_pwl;
    cfg.seed = seed;
    cfg.lambda = lambda_;
    cfg.truncation_quantile = truncation_quantile;
    cfg.max_evals = max_evals;
    cfg.optim_tol = optim_tol;
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let r = to_pyresult(fdars_core::alignment::pairwise_synchronization(
        &mat, &av, &cfg,
    ))?;
    let partners = PyList::empty(py);
    for p in r.partners {
        partners.append(usize_vec_to_numpy1d(py, p))?;
    }
    let pairwise_costs = PyList::empty(py);
    for c in r.pairwise_costs {
        pairwise_costs.append(vec_to_numpy1d(py, c))?;
    }
    let dict = PyDict::new(py);
    dict.set_item("warps", fdmatrix_to_numpy2d(py, &r.warps))?;
    dict.set_item("inverse_warps", fdmatrix_to_numpy2d(py, &r.inverse_warps))?;
    dict.set_item("aligned", fdmatrix_to_numpy2d(py, &r.aligned))?;
    dict.set_item("costs", vec_to_numpy1d(py, r.costs))?;
    dict.set_item("lambda", r.lambda)?;
    dict.set_item("partners", partners)?;
    dict.set_item(
        "pairwise_warps",
        fdmatrices_to_pylist(py, &r.pairwise_warps)?,
    )?;
    dict.set_item("pairwise_costs", pairwise_costs)?;
    Ok(dict)
}

// ---------------------------------------------------------------------------
// Phase box plot classification
// ---------------------------------------------------------------------------

/// Classify new warping functions against a phase box plot fitted on ``gammas``.
///
/// Refits ``phase_boxplot(gammas, argvals, factor)`` and applies its pointwise
/// rules: an outlier leaves the fences somewhere, a central warp lies inside
/// the 50% envelope everywhere, otherwise it is within the whiskers.
/// Classifying the training warps flags exactly its ``outlier_indices``.
///
/// Parameters
/// ----------
/// gammas : numpy.ndarray
///     Training warps, shape (n, m).
/// argvals : numpy.ndarray
///     Evaluation points, length m.
/// new_gammas : numpy.ndarray
///     Warps to classify, shape (n_new, m).
/// factor : float, optional
///     Whisker factor (default 1.5).
///
/// Returns
/// -------
/// numpy.ndarray
///     Region levels (n_new,), int8: 1 = 50% central region, 3 = within the
///     whiskers, 4 = outlier (fdasrsf levels; this box plot has no level 2).
#[pyfunction]
#[pyo3(signature = (gammas, argvals, new_gammas, factor=1.5))]
pub fn phase_boxplot_classify<'py>(
    py: Python<'py>,
    gammas: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    new_gammas: PyReadonlyArray2<'py, f64>,
    factor: f64,
) -> PyResult<Bound<'py, PyArray1<i8>>> {
    let g = numpy2d_to_fdmatrix(gammas)?;
    let av = numpy1d_to_vec(argvals);
    let new = numpy2d_to_fdmatrix(new_gammas)?;
    let bp = to_pyresult(fdars_core::alignment::phase_boxplot(&g, &av, factor))?;
    let regions = to_pyresult(bp.classify_warps(&new))?;
    let levels: Vec<i8> = regions.into_iter().map(|r| r.level() as i8).collect();
    Ok(PyArray1::from_vec(py, levels))
}

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(elastic_align_pair_with_config, m)?)?;
    m.add_function(wrap_pyfunction!(elastic_distance_with_config, m)?)?;
    m.add_function(wrap_pyfunction!(
        elastic_self_distance_matrix_with_config,
        m
    )?)?;
    m.add_function(wrap_pyfunction!(
        elastic_cross_distance_matrix_with_config,
        m
    )?)?;
    m.add_function(wrap_pyfunction!(karcher_mean_with_config, m)?)?;
    m.add_function(wrap_pyfunction!(karcher_median_with_config, m)?)?;
    m.add_function(wrap_pyfunction!(robust_karcher_mean_with_config, m)?)?;
    m.add_function(wrap_pyfunction!(align_to_target_with_config, m)?)?;
    m.add_function(wrap_pyfunction!(elastic_align_pair_closed_with_config, m)?)?;
    m.add_function(wrap_pyfunction!(elastic_distance_closed_with_config, m)?)?;
    m.add_function(wrap_pyfunction!(karcher_mean_closed_with_config, m)?)?;
    m.add_function(wrap_pyfunction!(
        elastic_align_pair_constrained_with_config,
        m
    )?)?;
    m.add_function(wrap_pyfunction!(elastic_align_pair_nd_with_config, m)?)?;
    m.add_function(wrap_pyfunction!(elastic_distance_nd_with_config, m)?)?;
    m.add_function(wrap_pyfunction!(karcher_mean_nd_with_config, m)?)?;
    m.add_function(wrap_pyfunction!(srsf_transform_smoothed, m)?)?;
    m.add_function(wrap_pyfunction!(srsf_presmooth, m)?)?;
    m.add_function(wrap_pyfunction!(shift_curves, m)?)?;
    m.add_function(wrap_pyfunction!(iterative_shift_registration, m)?)?;
    m.add_function(wrap_pyfunction!(landmark_shift_deltas, m)?)?;
    m.add_function(wrap_pyfunction!(landmark_shift_deltas_multi, m)?)?;
    m.add_function(wrap_pyfunction!(landmark_shift_registration, m)?)?;
    m.add_function(wrap_pyfunction!(continuous_registration, m)?)?;
    m.add_function(wrap_pyfunction!(affine_registration, m)?)?;
    m.add_function(wrap_pyfunction!(affine_warp_curves, m)?)?;
    m.add_function(wrap_pyfunction!(pairwise_synchronization, m)?)?;
    m.add_function(wrap_pyfunction!(phase_boxplot_classify, m)?)?;
    Ok(())
}
