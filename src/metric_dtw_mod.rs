//! Windowed DTW, DTW lower bounds and nearest-neighbour search, DTW / soft-DTW
//! barycenters, shape-based distance, and multivariate (d, m) DTW / DBA
//! (fdars-core 0.48).
//!
//! Registered into the existing `fdars.metric` submodule by
//! `metric_mod::register`; it is not a submodule of its own.
//!
//! Every function that accepts a global DTW window takes the same flat kwargs
//! `window="none", radius=None, window_fraction=None, max_slope=None`, parsed
//! by `crate::options::dtw_window`.

use crate::convert::*;
use crate::options::dtw_window;
use fdars_core::metric::{
    dtw_barycenter_averaging as core_dba, DbaConfig, DbaInit, DtwSearchStats,
    SoftDtwBarycenterConfig,
};
use numpy::{IntoPyArray, PyArray2, PyReadonlyArray1, PyReadonlyArray2};
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::PyDict;

// ---------------------------------------------------------------------------
// Private helpers
// ---------------------------------------------------------------------------

/// Warping path `[(i, j), ...]` as an int64 array of shape (L, 2) (also (0, 2)).
pub(crate) fn path_to_numpy<'py>(
    py: Python<'py>,
    path: &[(usize, usize)],
) -> Bound<'py, PyArray2<i64>> {
    let flat: Vec<i64> = path
        .iter()
        .flat_map(|&(i, j)| [i as i64, j as i64])
        .collect();
    numpy::ndarray::Array2::from_shape_vec((path.len(), 2), flat)
        .unwrap()
        .into_pyarray(py)
}

/// Nearest-neighbour search counters as a dict.
fn stats_to_dict<'py>(py: Python<'py>, s: &DtwSearchStats) -> PyResult<Bound<'py, PyDict>> {
    let d = PyDict::new(py);
    d.set_item("pruned_lb_keogh", s.pruned_lb_keogh)?;
    d.set_item("pruned_lb_kim", s.pruned_lb_kim)?;
    d.set_item("pruned_lb_webb", s.pruned_lb_webb)?;
    d.set_item("early_abandoned", s.early_abandoned)?;
    d.set_item("dtw_completed", s.dtw_completed)?;
    Ok(d)
}

// ---------------------------------------------------------------------------
// Windowed DTW / soft-DTW / GAK
// ---------------------------------------------------------------------------

/// DTW optimal warping path and accumulated cost under an optional global window.
///
/// Parameters
/// ----------
/// x : numpy.ndarray
///     First series (1D, length n).
/// y : numpy.ndarray
///     Second series (1D, length m).
/// p : float, optional
///     Exponent of the local cost `|x_i - y_j|^p` (default 2.0).
/// window : str, optional
///     Global constraint: ``"none"`` (default), ``"sakoe_chiba"`` (needs
///     `radius`), ``"itakura"`` (needs `max_slope` >= 1),
///     ``"sakoe_chiba_fraction"`` (needs `window_fraction` in [0, 1], aeon
///     semantics) or ``"itakura_fraction"`` (needs `max_slope` in (0, 1],
///     aeon semantics).
/// radius : int, optional
///     Sakoe-Chiba band radius in samples (tslearn semantics).
/// window_fraction : float, optional
///     Band half-width as a fraction of `min(n, m)`.
/// max_slope : float, optional
///     Itakura parallelogram slope.
///
/// Returns
/// -------
/// dict
///     ``path``: int64 array (L, 2) of matched index pairs ``(i, j)`` from
///     ``(0, 0)`` to ``(n-1, m-1)``; ``cost``: accumulated cost
///     ``sum |x_i - y_j|^p`` along the path (no root), equal to
///     `dtw_distance_windowed`.
#[pyfunction]
#[pyo3(signature = (x, y, p=2.0, window="none", radius=None, window_fraction=None, max_slope=None))]
pub fn dtw_path<'py>(
    py: Python<'py>,
    x: PyReadonlyArray1<'py, f64>,
    y: PyReadonlyArray1<'py, f64>,
    p: f64,
    window: &str,
    radius: Option<usize>,
    window_fraction: Option<f64>,
    max_slope: Option<f64>,
) -> PyResult<Bound<'py, PyDict>> {
    let w = dtw_window(window, radius, window_fraction, max_slope)?;
    let res = to_pyresult(fdars_core::metric::dtw_path(
        &numpy1d_to_vec(x),
        &numpy1d_to_vec(y),
        p,
        w,
    ))?;
    let d = PyDict::new(py);
    d.set_item("path", path_to_numpy(py, &res.path))?;
    d.set_item("cost", res.cost)?;
    Ok(d)
}

/// DTW distance between two series under an optional global window (O(m) memory).
///
/// Parameters
/// ----------
/// x, y : numpy.ndarray
///     Series (1D); lengths may differ.
/// p : float, optional
///     Exponent of the local cost (default 2.0).
/// window, radius, window_fraction, max_slope
///     Global window, see `dtw_path`.
///
/// Returns
/// -------
/// float
///     Accumulated cost ``sum |x_i - y_j|^p`` of the optimal admissible path
///     (no root).  With ``window="none"`` this equals the unconstrained DTW of
///     `dtw_self_1d`.
#[pyfunction]
#[pyo3(signature = (x, y, p=2.0, window="none", radius=None, window_fraction=None, max_slope=None))]
pub fn dtw_distance_windowed<'py>(
    x: PyReadonlyArray1<'py, f64>,
    y: PyReadonlyArray1<'py, f64>,
    p: f64,
    window: &str,
    radius: Option<usize>,
    window_fraction: Option<f64>,
    max_slope: Option<f64>,
) -> PyResult<f64> {
    let w = dtw_window(window, radius, window_fraction, max_slope)?;
    to_pyresult(fdars_core::metric::dtw_distance_windowed(
        &numpy1d_to_vec(x),
        &numpy1d_to_vec(y),
        p,
        w,
    ))
}

/// Boolean admissibility grid of a DTW global window for series lengths n and m.
///
/// Parameters
/// ----------
/// n, m : int
///     Lengths of the two series (both > 0).
/// window, radius, window_fraction, max_slope
///     Global window, see `dtw_path`.
///
/// Returns
/// -------
/// numpy.ndarray
///     Boolean array (n, m); ``mask[i, j]`` is True when cell ``(i, j)`` is
///     admissible (the zero entries of tslearn's ``sakoe_chiba_mask`` /
///     ``itakura_mask``).
#[pyfunction]
#[pyo3(signature = (n, m, window="none", radius=None, window_fraction=None, max_slope=None))]
pub fn dtw_window_mask<'py>(
    py: Python<'py>,
    n: usize,
    m: usize,
    window: &str,
    radius: Option<usize>,
    window_fraction: Option<f64>,
    max_slope: Option<f64>,
) -> PyResult<Bound<'py, PyArray2<bool>>> {
    let w = dtw_window(window, radius, window_fraction, max_slope)?;
    let mask = to_pyresult(w.mask(n, m))?;
    Ok(PyArray2::from_vec2(py, &mask).unwrap())
}

/// Soft-DTW value between two series under an optional global window.
///
/// Parameters
/// ----------
/// x, y : numpy.ndarray
///     Series (1D).
/// gamma : float, optional
///     Smoothing parameter, finite and > 0 (default 1.0).
/// window, radius, window_fraction, max_slope
///     Global window, see `dtw_path`.  Masked cells are excluded from the
///     soft minimum.
///
/// Returns
/// -------
/// float
///     Soft-DTW value (squared-Euclidean local cost).  With ``window="none"``
///     this equals `soft_dtw_self_1d` entries.
#[pyfunction]
#[pyo3(signature = (x, y, gamma=1.0, window="none", radius=None, window_fraction=None, max_slope=None))]
pub fn soft_dtw_distance_windowed<'py>(
    x: PyReadonlyArray1<'py, f64>,
    y: PyReadonlyArray1<'py, f64>,
    gamma: f64,
    window: &str,
    radius: Option<usize>,
    window_fraction: Option<f64>,
    max_slope: Option<f64>,
) -> PyResult<f64> {
    let w = dtw_window(window, radius, window_fraction, max_slope)?;
    to_pyresult(fdars_core::metric::soft_dtw_distance_windowed(
        &numpy1d_to_vec(x),
        &numpy1d_to_vec(y),
        gamma,
        w,
    ))
}

/// Soft-DTW value plus the expected alignment matrix (tslearn soft_dtw_alignment).
///
/// Parameters
/// ----------
/// x : numpy.ndarray
///     First series (1D, length n).
/// y : numpy.ndarray
///     Second series (1D, length m).
/// gamma : float, optional
///     Smoothing parameter, finite and > 0 (default 1.0).
/// window, radius, window_fraction, max_slope
///     Global window, see `dtw_path`.  Masked cells get zero weight.
///
/// Returns
/// -------
/// dict
///     ``value``: soft-DTW value; ``alignment``: (n, m) expected
///     path-membership weight of each cell under the Gibbs distribution over
///     paths (corners are 1, rows do not sum to 1; tends to the hard DTW path
///     indicator as ``gamma -> 0``).
#[pyfunction]
#[pyo3(signature = (x, y, gamma=1.0, window="none", radius=None, window_fraction=None, max_slope=None))]
pub fn soft_dtw_alignment<'py>(
    py: Python<'py>,
    x: PyReadonlyArray1<'py, f64>,
    y: PyReadonlyArray1<'py, f64>,
    gamma: f64,
    window: &str,
    radius: Option<usize>,
    window_fraction: Option<f64>,
    max_slope: Option<f64>,
) -> PyResult<Bound<'py, PyDict>> {
    let w = dtw_window(window, radius, window_fraction, max_slope)?;
    let res = to_pyresult(fdars_core::metric::soft_dtw_alignment(
        &numpy1d_to_vec(x),
        &numpy1d_to_vec(y),
        gamma,
        w,
    ))?;
    let d = PyDict::new(py);
    d.set_item("value", res.value)?;
    d.set_item("alignment", fdmatrix_to_numpy2d(py, &res.alignment))?;
    Ok(d)
}

/// Triangular Global Alignment Kernel (Cuturi 2011) between two 1-D series.
///
/// Parameters
/// ----------
/// x, y : numpy.ndarray
///     Series (1D).
/// sigma : float
///     Bandwidth (> 0); see `sigma_gak`.
/// triangular : int, optional
///     Triangular band parameter T: cells with ``|i - j| >= T`` are excluded.
///     ``0`` (default) disables the band, which equals `gak`.
///
/// Returns
/// -------
/// float
///     Normalised kernel value in [0, 1]; ``gak_triangular(x, x, s, T) == 1``.
#[pyfunction]
#[pyo3(signature = (x, y, sigma, triangular=0))]
pub fn gak_triangular<'py>(
    x: PyReadonlyArray1<'py, f64>,
    y: PyReadonlyArray1<'py, f64>,
    sigma: f64,
    triangular: usize,
) -> PyResult<f64> {
    to_pyresult(fdars_core::metric::gak_triangular(
        &numpy1d_to_vec(x),
        &numpy1d_to_vec(y),
        sigma,
        triangular,
    ))
}

// ---------------------------------------------------------------------------
// Barycenters
// ---------------------------------------------------------------------------

/// Soft-DTW barycenter of a set of curves (L-BFGS with random restarts).
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Curves, shape (n, m), n >= 1.
/// gamma : float, optional
///     Soft-DTW smoothing, finite and > 0 (default 1.0).  Smaller values
///     approach hard DTW; larger values approach the pointwise mean.
/// max_iter : int, optional
///     Maximum L-BFGS iterations per restart (default 100).
/// tol : float, optional
///     Convergence tolerance on gradient norm / relative cost change
///     (default 1e-6).
/// n_restarts : int, optional
///     Number of runs (default 10; 0 is treated as 1).  Run 0 starts from the
///     pointwise mean, the others from Gaussian-perturbed means; the run with
///     the lowest total soft-DTW cost is returned.  ``n_restarts=1, seed=0``
///     reproduces the single-start fdars-core 0.33 ``soft_dtw_barycenter``.
/// seed : int, optional
///     RNG seed for the perturbations (default 0).
///
/// Returns
/// -------
/// dict
///     ``barycenter`` (m,), ``n_iter`` (int), ``converged`` (bool).
#[pyfunction]
#[pyo3(signature = (data, gamma=1.0, max_iter=100, tol=1e-6, n_restarts=10, seed=0))]
pub fn soft_dtw_barycenter<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    gamma: f64,
    max_iter: usize,
    tol: f64,
    n_restarts: usize,
    seed: u64,
) -> PyResult<Bound<'py, PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    if mat.nrows() == 0 || mat.ncols() == 0 {
        return Err(PyValueError::new_err(
            "soft_dtw_barycenter: data must have at least one curve and one point",
        ));
    }
    if !(gamma.is_finite() && gamma > 0.0) {
        return Err(PyValueError::new_err(format!(
            "soft_dtw_barycenter: gamma must be finite and > 0, got {gamma}"
        )));
    }
    let mut config = SoftDtwBarycenterConfig::default();
    config.gamma = gamma;
    config.max_iter = max_iter;
    config.tol = tol;
    config.n_restarts = n_restarts;
    config.seed = seed;
    let res = fdars_core::metric::soft_dtw_barycenter_with_config(&mat, &config);
    let d = PyDict::new(py);
    d.set_item("barycenter", vec_to_numpy1d(py, res.barycenter))?;
    d.set_item("n_iter", res.n_iter)?;
    d.set_item("converged", res.converged)?;
    Ok(d)
}

/// DTW Barycenter Averaging (DBA, Petitjean et al. 2011) of a set of curves.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Curves, shape (n, m); all values finite.
/// max_iter : int, optional
///     Maximum number of DBA refinement iterations (default 30).
/// tol : float, optional
///     Stop when the relative decrease of the mean DTW cost is below `tol`
///     (default 1e-5).
/// window, radius, window_fraction, max_slope
///     Global window used by every DTW alignment, see `dtw_path`.
/// init : str or numpy.ndarray, optional
///     Initial barycenter: ``None`` / ``"mean"`` (pointwise mean, default),
///     ``"medoid"`` (the curve with smallest total DTW cost), or a 1-D array
///     used as is.
/// barycenter_size : int, optional
///     Length of the barycenter (default: the curve length m).
/// weights : numpy.ndarray, optional
///     Non-negative per-curve weights (n,), default uniform.
///
/// Returns
/// -------
/// dict
///     ``barycenter`` (barycenter_size,), ``cost`` (weighted mean DTW cost to
///     the curves, squared-Euclidean local cost), ``n_iter``, ``converged``.
#[pyfunction]
#[pyo3(signature = (
    data, max_iter=30, tol=1e-5, window="none", radius=None, window_fraction=None,
    max_slope=None, init=None, barycenter_size=None, weights=None
))]
pub fn dtw_barycenter_averaging<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    max_iter: usize,
    tol: f64,
    window: &str,
    radius: Option<usize>,
    window_fraction: Option<f64>,
    max_slope: Option<f64>,
    init: Option<&Bound<'py, PyAny>>,
    barycenter_size: Option<usize>,
    weights: Option<PyReadonlyArray1<'py, f64>>,
) -> PyResult<Bound<'py, PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let mut config = DbaConfig::default();
    config.max_iter = max_iter;
    config.tol = tol;
    config.window = dtw_window(window, radius, window_fraction, max_slope)?;
    config.init = match init {
        None => DbaInit::Mean,
        Some(obj) => match obj.extract::<String>() {
            Ok(s) => match s.as_str() {
                "mean" => DbaInit::Mean,
                "medoid" => DbaInit::Medoid,
                _ => {
                    return Err(PyValueError::new_err(format!(
                        "init must be 'mean', 'medoid' or a 1-D array, got '{s}'"
                    )))
                }
            },
            Err(_) => {
                let arr = obj.extract::<PyReadonlyArray1<'py, f64>>().map_err(|_| {
                    PyValueError::new_err("init must be 'mean', 'medoid' or a 1-D float array")
                })?;
                DbaInit::Custom(numpy1d_to_vec(arr))
            }
        },
    };
    config.barycenter_size = barycenter_size;
    config.weights = weights.map(numpy1d_to_vec);
    let res = to_pyresult(core_dba(&mat, &config))?;
    let d = PyDict::new(py);
    d.set_item("barycenter", vec_to_numpy1d(py, res.barycenter))?;
    d.set_item("cost", res.cost)?;
    d.set_item("n_iter", res.n_iter)?;
    d.set_item("converged", res.converged)?;
    Ok(d)
}

// ---------------------------------------------------------------------------
// Lower bounds and early abandoning
// ---------------------------------------------------------------------------

/// LB_Keogh envelope of a series for a Sakoe-Chiba band of the given radius.
///
/// Parameters
/// ----------
/// x : numpy.ndarray
///     Series (1D).
/// radius : int
///     Band radius in samples.
///
/// Returns
/// -------
/// dict
///     ``lower``, ``upper``: running min / max of `x` over ``[i - radius,
///     i + radius]``, each of length ``len(x)``.
#[pyfunction]
pub fn lb_envelope<'py>(
    py: Python<'py>,
    x: PyReadonlyArray1<'py, f64>,
    radius: usize,
) -> PyResult<Bound<'py, PyDict>> {
    let env = to_pyresult(fdars_core::metric::lb_envelope(&numpy1d_to_vec(x), radius))?;
    let d = PyDict::new(py);
    d.set_item("lower", vec_to_numpy1d(py, env.lower))?;
    d.set_item("upper", vec_to_numpy1d(py, env.upper))?;
    Ok(d)
}

/// LB_Keogh envelope of a candidate series under any DTW window, for a query length.
///
/// Parameters
/// ----------
/// y : numpy.ndarray
///     Candidate series (1D, length m).
/// query_len : int
///     Length n of the queries the envelope will bound.
/// window, radius, window_fraction, max_slope
///     Global window, see `dtw_path`.
///
/// Returns
/// -------
/// dict
///     ``lower``, ``upper``: arrays of length `query_len`; entry i is the
///     min / max of `y` over the columns admissible in window row i.
///     With ``window="sakoe_chiba"`` and ``query_len == len(y)`` this equals
///     ``lb_envelope(y, radius)``.
#[pyfunction]
#[pyo3(signature = (y, query_len, window="none", radius=None, window_fraction=None, max_slope=None))]
pub fn lb_envelope_windowed<'py>(
    py: Python<'py>,
    y: PyReadonlyArray1<'py, f64>,
    query_len: usize,
    window: &str,
    radius: Option<usize>,
    window_fraction: Option<f64>,
    max_slope: Option<f64>,
) -> PyResult<Bound<'py, PyDict>> {
    let w = dtw_window(window, radius, window_fraction, max_slope)?;
    let env = to_pyresult(fdars_core::metric::lb_envelope_windowed(
        &numpy1d_to_vec(y),
        query_len,
        w,
    ))?;
    let d = PyDict::new(py);
    d.set_item("lower", vec_to_numpy1d(py, env.lower))?;
    d.set_item("upper", vec_to_numpy1d(py, env.upper))?;
    Ok(d)
}

/// LB_Keogh lower bound on the windowed DTW distance between a query and a candidate.
///
/// The candidate's envelope is built internally with
/// ``lb_envelope_windowed(candidate, len(query), window...)`` (fdars-core's
/// envelope type cannot be constructed from Python), then the query is
/// scored against it.
///
/// Parameters
/// ----------
/// query : numpy.ndarray
///     Query series (1D).
/// candidate : numpy.ndarray
///     Candidate series (1D).
/// p : float, optional
///     Exponent of the local cost (default 2.0).
/// window, radius, window_fraction, max_slope
///     Global window, see `dtw_path`.
///
/// Returns
/// -------
/// float
///     A lower bound on ``dtw_distance_windowed(query, candidate, p, window)``.
#[pyfunction]
#[pyo3(signature = (query, candidate, p=2.0, window="none", radius=None, window_fraction=None, max_slope=None))]
pub fn lb_keogh<'py>(
    query: PyReadonlyArray1<'py, f64>,
    candidate: PyReadonlyArray1<'py, f64>,
    p: f64,
    window: &str,
    radius: Option<usize>,
    window_fraction: Option<f64>,
    max_slope: Option<f64>,
) -> PyResult<f64> {
    let w = dtw_window(window, radius, window_fraction, max_slope)?;
    let q = numpy1d_to_vec(query);
    let env = to_pyresult(fdars_core::metric::lb_envelope_windowed(
        &numpy1d_to_vec(candidate),
        q.len(),
        w,
    ))?;
    to_pyresult(fdars_core::metric::lb_keogh(&q, &env, p))
}

/// LB_Kim lower bound on DTW from first / last / min / max features (O(1) after O(n)).
///
/// Parameters
/// ----------
/// x, y : numpy.ndarray
///     Series (1D).
/// p : float, optional
///     Exponent of the local cost (default 2.0).
///
/// Returns
/// -------
/// float
///     A lower bound on the DTW distance under any window.
#[pyfunction]
#[pyo3(signature = (x, y, p=2.0))]
pub fn lb_kim<'py>(
    x: PyReadonlyArray1<'py, f64>,
    y: PyReadonlyArray1<'py, f64>,
    p: f64,
) -> PyResult<f64> {
    to_pyresult(fdars_core::metric::lb_kim(
        &numpy1d_to_vec(x),
        &numpy1d_to_vec(y),
        p,
    ))
}

/// LB_Webb lower bound on windowed DTW (Webb and Petitjean 2021).
///
/// Parameters
/// ----------
/// x, y : numpy.ndarray
///     Series (1D).
/// p : float, optional
///     Exponent of the local cost (default 2.0).
/// window, radius, window_fraction, max_slope
///     Global window, see `dtw_path`.
///
/// Returns
/// -------
/// float
///     A lower bound on ``dtw_distance_windowed(x, y, p, window)``.
#[pyfunction]
#[pyo3(signature = (x, y, p=2.0, window="none", radius=None, window_fraction=None, max_slope=None))]
pub fn lb_webb<'py>(
    x: PyReadonlyArray1<'py, f64>,
    y: PyReadonlyArray1<'py, f64>,
    p: f64,
    window: &str,
    radius: Option<usize>,
    window_fraction: Option<f64>,
    max_slope: Option<f64>,
) -> PyResult<f64> {
    let w = dtw_window(window, radius, window_fraction, max_slope)?;
    to_pyresult(fdars_core::metric::lb_webb(
        &numpy1d_to_vec(x),
        &numpy1d_to_vec(y),
        p,
        w,
    ))
}

/// LB_Improved lower bound on windowed DTW (Lemire 2009), at least as tight as LB_Keogh.
///
/// Parameters
/// ----------
/// x, y : numpy.ndarray
///     Series (1D).
/// p : float, optional
///     Exponent of the local cost (default 2.0).
/// window, radius, window_fraction, max_slope
///     Global window, see `dtw_path`.
///
/// Returns
/// -------
/// float
///     A lower bound on ``dtw_distance_windowed(x, y, p, window)``.
#[pyfunction]
#[pyo3(signature = (x, y, p=2.0, window="none", radius=None, window_fraction=None, max_slope=None))]
pub fn lb_improved<'py>(
    x: PyReadonlyArray1<'py, f64>,
    y: PyReadonlyArray1<'py, f64>,
    p: f64,
    window: &str,
    radius: Option<usize>,
    window_fraction: Option<f64>,
    max_slope: Option<f64>,
) -> PyResult<f64> {
    let w = dtw_window(window, radius, window_fraction, max_slope)?;
    to_pyresult(fdars_core::metric::lb_improved(
        &numpy1d_to_vec(x),
        &numpy1d_to_vec(y),
        p,
        w,
    ))
}

/// LB_Enhanced lower bound on windowed DTW (Tan et al. 2019) with v boundary bands.
///
/// Parameters
/// ----------
/// x, y : numpy.ndarray
///     Series (1D).
/// v : int
///     Number of left / right boundary bands (>= 1).  The effective value is
///     ``min(v, (min(n, m) - 1) // 2)``.
/// p : float, optional
///     Exponent of the local cost (default 2.0).
/// window, radius, window_fraction, max_slope
///     Global window, see `dtw_path`.
///
/// Returns
/// -------
/// float
///     A lower bound on ``dtw_distance_windowed(x, y, p, window)``.
#[pyfunction]
#[pyo3(signature = (x, y, v, p=2.0, window="none", radius=None, window_fraction=None, max_slope=None))]
pub fn lb_enhanced<'py>(
    x: PyReadonlyArray1<'py, f64>,
    y: PyReadonlyArray1<'py, f64>,
    v: usize,
    p: f64,
    window: &str,
    radius: Option<usize>,
    window_fraction: Option<f64>,
    max_slope: Option<f64>,
) -> PyResult<f64> {
    let w = dtw_window(window, radius, window_fraction, max_slope)?;
    to_pyresult(fdars_core::metric::lb_enhanced(
        &numpy1d_to_vec(x),
        &numpy1d_to_vec(y),
        p,
        w,
        v,
    ))
}

/// Early-abandoning windowed DTW: the distance, or None once it must exceed `cutoff`.
///
/// Parameters
/// ----------
/// x, y : numpy.ndarray
///     Series (1D).
/// cutoff : float
///     Abandon threshold (not NaN; ``inf`` never abandons).
/// p : float, optional
///     Exponent of the local cost (default 2.0).
/// window, radius, window_fraction, max_slope
///     Global window, see `dtw_path`.
///
/// Returns
/// -------
/// float or None
///     ``dtw_distance_windowed(x, y, p, window)`` when it is ``<= cutoff``,
///     otherwise None.
#[pyfunction]
#[pyo3(signature = (x, y, cutoff, p=2.0, window="none", radius=None, window_fraction=None, max_slope=None))]
pub fn dtw_distance_early_abandon<'py>(
    x: PyReadonlyArray1<'py, f64>,
    y: PyReadonlyArray1<'py, f64>,
    cutoff: f64,
    p: f64,
    window: &str,
    radius: Option<usize>,
    window_fraction: Option<f64>,
    max_slope: Option<f64>,
) -> PyResult<Option<f64>> {
    let w = dtw_window(window, radius, window_fraction, max_slope)?;
    to_pyresult(fdars_core::metric::dtw_distance_early_abandon(
        &numpy1d_to_vec(x),
        &numpy1d_to_vec(y),
        p,
        w,
        cutoff,
    ))
}

// ---------------------------------------------------------------------------
// Nearest-neighbour search
// ---------------------------------------------------------------------------

/// Exact 1-NN search under windowed DTW with a lower-bound cascade (UCR-suite style).
///
/// Parameters
/// ----------
/// queries : numpy.ndarray
///     Query curves, shape (n_q, n).
/// references : numpy.ndarray
///     Reference curves, shape (n_r, m).
/// p : float, optional
///     Exponent of the local cost (default 2.0).
/// window, radius, window_fraction, max_slope
///     Global window, see `dtw_path`.
///
/// Returns
/// -------
/// dict
///     ``indices`` int64 (n_q,): nearest reference per query;
///     ``distances`` (n_q,): its windowed DTW distance;
///     ``stats``: dict of pruning counters ``pruned_lb_keogh``,
///     ``pruned_lb_kim``, ``pruned_lb_webb``, ``early_abandoned``,
///     ``dtw_completed``.
#[pyfunction]
#[pyo3(signature = (queries, references, p=2.0, window="none", radius=None, window_fraction=None, max_slope=None))]
pub fn dtw_nearest_neighbor<'py>(
    py: Python<'py>,
    queries: PyReadonlyArray2<'py, f64>,
    references: PyReadonlyArray2<'py, f64>,
    p: f64,
    window: &str,
    radius: Option<usize>,
    window_fraction: Option<f64>,
    max_slope: Option<f64>,
) -> PyResult<Bound<'py, PyDict>> {
    let w = dtw_window(window, radius, window_fraction, max_slope)?;
    let q = numpy2d_to_fdmatrix(queries)?;
    let r = numpy2d_to_fdmatrix(references)?;
    let res = to_pyresult(fdars_core::metric::dtw_nearest_neighbor(&q, &r, p, w))?;
    let d = PyDict::new(py);
    d.set_item("indices", usize_vec_to_numpy1d(py, res.indices))?;
    d.set_item("distances", vec_to_numpy1d(py, res.distances))?;
    d.set_item("stats", stats_to_dict(py, &res.stats)?)?;
    Ok(d)
}

/// Exact k-NN search under windowed DTW with a lower-bound cascade.
///
/// Parameters
/// ----------
/// queries : numpy.ndarray
///     Query curves, shape (n_q, n).
/// references : numpy.ndarray
///     Reference curves, shape (n_r, m).
/// k : int, optional
///     Number of neighbours, ``1 <= k <= n_r`` (default 1).
/// p : float, optional
///     Exponent of the local cost (default 2.0).
/// window, radius, window_fraction, max_slope
///     Global window, see `dtw_path`.
///
/// Returns
/// -------
/// dict
///     ``indices`` int64 (n_q, k) and ``distances`` (n_q, k), each row sorted
///     by increasing distance; ``stats``: pruning counters as in
///     `dtw_nearest_neighbor`.
#[pyfunction]
#[pyo3(signature = (queries, references, k=1, p=2.0, window="none", radius=None, window_fraction=None, max_slope=None))]
pub fn dtw_k_nearest_neighbors<'py>(
    py: Python<'py>,
    queries: PyReadonlyArray2<'py, f64>,
    references: PyReadonlyArray2<'py, f64>,
    k: usize,
    p: f64,
    window: &str,
    radius: Option<usize>,
    window_fraction: Option<f64>,
    max_slope: Option<f64>,
) -> PyResult<Bound<'py, PyDict>> {
    let w = dtw_window(window, radius, window_fraction, max_slope)?;
    let q = numpy2d_to_fdmatrix(queries)?;
    let r = numpy2d_to_fdmatrix(references)?;
    let res = to_pyresult(fdars_core::metric::dtw_k_nearest_neighbors(&q, &r, k, p, w))?;
    let indices: Vec<Vec<i64>> = res
        .indices
        .iter()
        .map(|row| row.iter().map(|&i| i as i64).collect())
        .collect();
    let d = PyDict::new(py);
    d.set_item("indices", PyArray2::from_vec2(py, &indices).unwrap())?;
    d.set_item(
        "distances",
        PyArray2::from_vec2(py, &res.distances).unwrap(),
    )?;
    d.set_item("stats", stats_to_dict(py, &res.stats)?)?;
    Ok(d)
}

// ---------------------------------------------------------------------------
// Shape-based distance (k-Shape)
// ---------------------------------------------------------------------------

/// Shape-based distance (Paparrizos and Gravano 2015) and the optimal signed lag.
///
/// Parameters
/// ----------
/// x, y : numpy.ndarray
///     Series (1D), same length m.  Both are z-normalised internally, so the
///     distance is invariant to offset and positive scaling.  The lag search
///     uses zero-padded (linear, not circular) cross-correlation, so a shifted
///     copy scores close to, but not exactly, 0 (the overhang is lost).
///
/// Returns
/// -------
/// dict
///     ``distance``: ``1 - max_w NCC_c(x, y)`` in [0, 2] (a constant series
///     gives 1.0); ``shift``: the signed lag ``w`` in ``-(m-1) .. m-1`` by
///     which `y` aligns to `x`.
#[pyfunction]
pub fn sbd<'py>(
    py: Python<'py>,
    x: PyReadonlyArray1<'py, f64>,
    y: PyReadonlyArray1<'py, f64>,
) -> PyResult<Bound<'py, PyDict>> {
    let res = to_pyresult(fdars_core::metric::sbd(
        &numpy1d_to_vec(x),
        &numpy1d_to_vec(y),
    ))?;
    let d = PyDict::new(py);
    d.set_item("distance", res.distance)?;
    d.set_item("shift", res.shift)?;
    Ok(d)
}

/// Pairwise shape-based distance matrix of a set of curves.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Curves, shape (n, m).
///
/// Returns
/// -------
/// numpy.ndarray
///     Symmetric (n, n) matrix of `sbd` distances with zero diagonal.
#[pyfunction]
pub fn sbd_distance_matrix<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
) -> PyResult<Bound<'py, PyArray2<f64>>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let res = to_pyresult(fdars_core::metric::sbd_distance_matrix(&mat))?;
    Ok(fdmatrix_to_numpy2d(py, &res))
}

// ---------------------------------------------------------------------------
// Multivariate DTW and DBA
// ---------------------------------------------------------------------------

/// Dependent multichannel DTW distance between two (d, m) series.
///
/// Parameters
/// ----------
/// x : numpy.ndarray
///     First series, shape (d, n): one channel per row, one time point per
///     column (aeon layout).
/// y : numpy.ndarray
///     Second series, shape (d, m); same number of channels, length may differ.
/// p : float, optional
///     Exponent of the local cost ``(sum_c (x_ci - y_cj)^2)^(p/2)``
///     (default 2.0, the squared Euclidean distance across channels).
/// window, radius, window_fraction, max_slope
///     Global window, see `dtw_path`.
///
/// Returns
/// -------
/// float
///     Accumulated cost of the optimal admissible path (no root).  With
///     ``d = 1`` this is bit-identical to `dtw_distance_windowed`.
#[pyfunction]
#[pyo3(signature = (x, y, p=2.0, window="none", radius=None, window_fraction=None, max_slope=None))]
pub fn dtw_distance_multivariate<'py>(
    x: PyReadonlyArray2<'py, f64>,
    y: PyReadonlyArray2<'py, f64>,
    p: f64,
    window: &str,
    radius: Option<usize>,
    window_fraction: Option<f64>,
    max_slope: Option<f64>,
) -> PyResult<f64> {
    let w = dtw_window(window, radius, window_fraction, max_slope)?;
    to_pyresult(fdars_core::metric::dtw_distance_multivariate(
        &numpy2d_to_fdmatrix(x)?,
        &numpy2d_to_fdmatrix(y)?,
        p,
        w,
    ))
}

/// Dependent multichannel DTW optimal warping path and accumulated cost.
///
/// Parameters
/// ----------
/// x, y : numpy.ndarray
///     Series of shape (d, n) and (d, m), channels as rows.
/// p : float, optional
///     Exponent of the local cost, see `dtw_distance_multivariate` (default 2.0).
/// window, radius, window_fraction, max_slope
///     Global window, see `dtw_path`.
///
/// Returns
/// -------
/// dict
///     ``path``: int64 array (L, 2) of matched time-index pairs; ``cost``:
///     accumulated cost, equal to `dtw_distance_multivariate`.
#[pyfunction]
#[pyo3(signature = (x, y, p=2.0, window="none", radius=None, window_fraction=None, max_slope=None))]
pub fn dtw_path_multivariate<'py>(
    py: Python<'py>,
    x: PyReadonlyArray2<'py, f64>,
    y: PyReadonlyArray2<'py, f64>,
    p: f64,
    window: &str,
    radius: Option<usize>,
    window_fraction: Option<f64>,
    max_slope: Option<f64>,
) -> PyResult<Bound<'py, PyDict>> {
    let w = dtw_window(window, radius, window_fraction, max_slope)?;
    let res = to_pyresult(fdars_core::metric::dtw_path_multivariate(
        &numpy2d_to_fdmatrix(x)?,
        &numpy2d_to_fdmatrix(y)?,
        p,
        w,
    ))?;
    let d = PyDict::new(py);
    d.set_item("path", path_to_numpy(py, &res.path))?;
    d.set_item("cost", res.cost)?;
    Ok(d)
}

/// Pairwise dependent multichannel DTW distance matrix of a collection of series.
///
/// Parameters
/// ----------
/// data : list of numpy.ndarray or numpy.ndarray
///     Series as a list of (d, m_i) arrays (lengths may differ) or a 3-D
///     (n, d, m) array.
/// other : list of numpy.ndarray or numpy.ndarray, optional
///     Second collection with the same channel count; default None gives the
///     self-distance matrix.
/// p : float, optional
///     Exponent of the local cost (default 2.0).
/// window, radius, window_fraction, max_slope
///     Global window, see `dtw_path` (sized per pair).
///
/// Returns
/// -------
/// numpy.ndarray
///     (n, n) symmetric matrix with zero diagonal, or (n, n_other).
#[pyfunction]
#[pyo3(signature = (data, other=None, p=2.0, window="none", radius=None, window_fraction=None, max_slope=None))]
pub fn dtw_pairwise_distance_multivariate<'py>(
    py: Python<'py>,
    data: &Bound<'py, PyAny>,
    other: Option<&Bound<'py, PyAny>>,
    p: f64,
    window: &str,
    radius: Option<usize>,
    window_fraction: Option<f64>,
    max_slope: Option<f64>,
) -> PyResult<Bound<'py, PyArray2<f64>>> {
    let w = dtw_window(window, radius, window_fraction, max_slope)?;
    let series = series_collection(data, "dtw_pairwise_distance_multivariate: data")?;
    let other = other
        .map(|o| series_collection(o, "dtw_pairwise_distance_multivariate: other"))
        .transpose()?;
    let res = to_pyresult(fdars_core::metric::dtw_pairwise_distance_multivariate(
        &series,
        other.as_deref(),
        p,
        w,
    ))?;
    Ok(fdmatrix_to_numpy2d(py, &res))
}

/// DTW Barycenter Averaging of multivariate (d, m) series (tslearn DBA on (n, sz, d) data).
///
/// Parameters
/// ----------
/// data : list of numpy.ndarray or numpy.ndarray
///     Series as a list of (d, m_i) arrays (lengths may differ, channel
///     count may not) or a 3-D (n, d, m) array; all values finite.
/// max_iter : int, optional
///     Maximum number of DBA refinement iterations (default 30).
/// tol : float, optional
///     Stop when the relative decrease of the mean DTW cost is below `tol`
///     (default 1e-5).
/// window, radius, window_fraction, max_slope
///     Global window used by every alignment, see `dtw_path`.
/// init : str or numpy.ndarray, optional
///     Initial barycenter: ``None`` / ``"mean"`` (pointwise mean over the
///     series reaching each time point, default), ``"medoid"``, or a (d, L)
///     array used as is.
/// barycenter_size : int, optional
///     Length of the barycenter (default: the longest series length for
///     ``"mean"``, the first series' length for ``"medoid"``, which is
///     resampled linearly to it).
/// weights : numpy.ndarray, optional
///     Non-negative per-series weights (n,), default uniform.
///
/// Returns
/// -------
/// dict
///     ``barycenter`` (d, L), ``cost`` (weighted mean multichannel DTW cost),
///     ``n_iter``, ``converged``.  With ``d = 1`` the result is bit-identical
///     to `dtw_barycenter_averaging`.
#[pyfunction]
#[pyo3(signature = (data, max_iter=30, tol=1e-5, window="none", radius=None, window_fraction=None, max_slope=None, init=None, barycenter_size=None, weights=None))]
pub fn dtw_barycenter_averaging_multivariate<'py>(
    py: Python<'py>,
    data: &Bound<'py, PyAny>,
    max_iter: usize,
    tol: f64,
    window: &str,
    radius: Option<usize>,
    window_fraction: Option<f64>,
    max_slope: Option<f64>,
    init: Option<&Bound<'py, PyAny>>,
    barycenter_size: Option<usize>,
    weights: Option<PyReadonlyArray1<'py, f64>>,
) -> PyResult<Bound<'py, PyDict>> {
    let series = series_collection(data, "dtw_barycenter_averaging_multivariate: data")?;
    let mut config = DbaConfig::default();
    config.max_iter = max_iter;
    config.tol = tol;
    config.window = dtw_window(window, radius, window_fraction, max_slope)?;
    config.init = match init {
        None => DbaInit::Mean,
        Some(obj) => match obj.extract::<String>() {
            Ok(s) => match s.as_str() {
                "mean" => DbaInit::Mean,
                "medoid" => DbaInit::Medoid,
                _ => {
                    return Err(PyValueError::new_err(format!(
                        "init must be 'mean', 'medoid' or a 2-D (d, L) array, got '{s}'"
                    )))
                }
            },
            Err(_) => {
                let arr = obj.extract::<PyReadonlyArray2<'py, f64>>().map_err(|_| {
                    PyValueError::new_err(
                        "init must be 'mean', 'medoid' or a 2-D (d, L) float array",
                    )
                })?;
                DbaInit::CustomMultivariate(numpy2d_to_fdmatrix(arr)?)
            }
        },
    };
    config.barycenter_size = barycenter_size;
    config.weights = weights.map(numpy1d_to_vec);
    let res = to_pyresult(fdars_core::metric::dtw_barycenter_averaging_multivariate(
        &series, &config,
    ))?;
    let d = PyDict::new(py);
    d.set_item("barycenter", fdmatrix_to_numpy2d(py, &res.barycenter))?;
    d.set_item("cost", res.cost)?;
    d.set_item("n_iter", res.n_iter)?;
    d.set_item("converged", res.converged)?;
    Ok(d)
}

/// Register the DTW / SBD functions into the `metric` submodule.
pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(dtw_path, m)?)?;
    m.add_function(wrap_pyfunction!(dtw_distance_windowed, m)?)?;
    m.add_function(wrap_pyfunction!(dtw_window_mask, m)?)?;
    m.add_function(wrap_pyfunction!(soft_dtw_distance_windowed, m)?)?;
    m.add_function(wrap_pyfunction!(soft_dtw_alignment, m)?)?;
    m.add_function(wrap_pyfunction!(gak_triangular, m)?)?;
    m.add_function(wrap_pyfunction!(soft_dtw_barycenter, m)?)?;
    m.add_function(wrap_pyfunction!(dtw_barycenter_averaging, m)?)?;
    m.add_function(wrap_pyfunction!(lb_envelope, m)?)?;
    m.add_function(wrap_pyfunction!(lb_envelope_windowed, m)?)?;
    m.add_function(wrap_pyfunction!(lb_keogh, m)?)?;
    m.add_function(wrap_pyfunction!(lb_kim, m)?)?;
    m.add_function(wrap_pyfunction!(lb_webb, m)?)?;
    m.add_function(wrap_pyfunction!(lb_improved, m)?)?;
    m.add_function(wrap_pyfunction!(lb_enhanced, m)?)?;
    m.add_function(wrap_pyfunction!(dtw_distance_early_abandon, m)?)?;
    m.add_function(wrap_pyfunction!(dtw_nearest_neighbor, m)?)?;
    m.add_function(wrap_pyfunction!(dtw_k_nearest_neighbors, m)?)?;
    m.add_function(wrap_pyfunction!(sbd, m)?)?;
    m.add_function(wrap_pyfunction!(sbd_distance_matrix, m)?)?;
    m.add_function(wrap_pyfunction!(dtw_distance_multivariate, m)?)?;
    m.add_function(wrap_pyfunction!(dtw_path_multivariate, m)?)?;
    m.add_function(wrap_pyfunction!(dtw_pairwise_distance_multivariate, m)?)?;
    m.add_function(wrap_pyfunction!(dtw_barycenter_averaging_multivariate, m)?)?;
    Ok(())
}
