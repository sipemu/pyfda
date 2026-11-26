//! The aeon elastic-distance family (DDTW, WDTW, WDDTW, ADTW, ERP, EDR, TWE,
//! MSM, LCSS, shape-DTW) as eight `metric=`-dispatching bindings (fdars-core
//! 0.48).
//!
//! Registered into the existing `fdars.metric` submodule by
//! `metric_mod::register`; it is not a submodule of its own.
//!
//! Every function takes the same flat kwargs: the DTW window of
//! `crate::options::dtw_window` plus the union of the per-metric parameters.
//! Parameters that the chosen metric does not use are ignored.

use crate::convert::*;
use crate::metric_dtw_mod::path_to_numpy;
use crate::options::dtw_window;
use fdars_core::matrix::FdMatrix;
use fdars_core::metric as fm;
use fdars_core::metric::{DtwWindow, ElasticDistancePath, ShapeDtwDescriptor};
use fdars_core::FdarError;
use numpy::{PyArray2, PyReadonlyArray1, PyReadonlyArray2};
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::PyDict;

// ---------------------------------------------------------------------------
// Private helpers
// ---------------------------------------------------------------------------

/// One elastic distance with its resolved parameters.
#[derive(Clone, Copy)]
enum Elastic {
    Ddtw,
    Wdtw(f64),
    Wddtw(f64),
    Adtw(f64),
    Erp(f64),
    Edr(Option<f64>),
    Twe(f64, f64),
    Msm(f64, bool),
    Lcss(f64),
    ShapeDtw(ShapeDtwDescriptor, usize),
}

/// Resolve `metric=` and the per-metric kwargs (defaults are aeon 1.6's).
fn elastic_from_kwargs(
    metric: &str,
    g: Option<f64>,
    warp_penalty: f64,
    epsilon: Option<f64>,
    nu: f64,
    lmbda: f64,
    c: f64,
    independent: bool,
    descriptor: &str,
    descriptor_param: Option<usize>,
    reach: usize,
) -> PyResult<Elastic> {
    Ok(match metric {
        "ddtw" => Elastic::Ddtw,
        "wdtw" => Elastic::Wdtw(g.unwrap_or(0.05)),
        "wddtw" => Elastic::Wddtw(g.unwrap_or(0.05)),
        "adtw" => Elastic::Adtw(warp_penalty),
        "erp" => Elastic::Erp(g.unwrap_or(0.0)),
        "edr" => Elastic::Edr(epsilon),
        "twe" => Elastic::Twe(nu, lmbda),
        "msm" => Elastic::Msm(c, independent),
        "lcss" => Elastic::Lcss(epsilon.unwrap_or(1.0)),
        "shape_dtw" => {
            let desc = match descriptor {
                "identity" => ShapeDtwDescriptor::Identity,
                "paa" => ShapeDtwDescriptor::Paa {
                    num_intervals: descriptor_param.unwrap_or(8),
                },
                "dwt" => ShapeDtwDescriptor::Dwt {
                    num_levels: descriptor_param.unwrap_or(3),
                },
                "slope" => ShapeDtwDescriptor::Slope {
                    num_intervals: descriptor_param.unwrap_or(8),
                },
                "derivative" => ShapeDtwDescriptor::Derivative,
                _ => {
                    return Err(PyValueError::new_err(format!(
                        "descriptor must be one of 'identity', 'paa', 'dwt', 'slope', \
                         'derivative', got '{descriptor}'"
                    )))
                }
            };
            Elastic::ShapeDtw(desc, reach)
        }
        _ => {
            return Err(PyValueError::new_err(format!(
                "metric must be one of 'ddtw', 'wdtw', 'wddtw', 'adtw', 'erp', 'edr', \
                 'twe', 'msm', 'lcss', 'shape_dtw', got '{metric}'"
            )))
        }
    })
}

/// Call the core function of the selected metric: `$f_<name>` idents in the
/// fixed order ddtw, wdtw, wddtw, adtw, erp, edr, twe, msm, lcss, shape_dtw.
macro_rules! dispatch {
    ($e:expr, ($($a:expr),*), $w:expr,
     $ddtw:ident, $wdtw:ident, $wddtw:ident, $adtw:ident, $erp:ident,
     $edr:ident, $twe:ident, $msm:ident, $lcss:ident, $shape:ident) => {
        match $e {
            Elastic::Ddtw => fm::$ddtw($($a,)* $w),
            Elastic::Wdtw(g) => fm::$wdtw($($a,)* $w, g),
            Elastic::Wddtw(g) => fm::$wddtw($($a,)* $w, g),
            Elastic::Adtw(wp) => fm::$adtw($($a,)* $w, wp),
            Elastic::Erp(g) => fm::$erp($($a,)* $w, g),
            Elastic::Edr(eps) => fm::$edr($($a,)* $w, eps),
            Elastic::Twe(nu, lmbda) => fm::$twe($($a,)* $w, nu, lmbda),
            Elastic::Msm(c, ind) => fm::$msm($($a,)* $w, c, ind),
            Elastic::Lcss(eps) => fm::$lcss($($a,)* $w, eps),
            Elastic::ShapeDtw(desc, reach) => fm::$shape($($a,)* $w, desc, reach),
        }
    };
}

fn distance_uni(e: Elastic, x: &[f64], y: &[f64], w: DtwWindow) -> Result<f64, FdarError> {
    dispatch!(
        e,
        (x, y),
        w,
        ddtw_distance,
        wdtw_distance,
        wddtw_distance,
        adtw_distance,
        erp_distance,
        edr_distance,
        twe_distance,
        msm_distance,
        lcss_distance,
        shape_dtw_distance
    )
}

fn pairwise_uni(
    e: Elastic,
    data: &FdMatrix,
    other: Option<&FdMatrix>,
    w: DtwWindow,
) -> Result<FdMatrix, FdarError> {
    dispatch!(
        e,
        (data, other),
        w,
        ddtw_pairwise_distance,
        wdtw_pairwise_distance,
        wddtw_pairwise_distance,
        adtw_pairwise_distance,
        erp_pairwise_distance,
        edr_pairwise_distance,
        twe_pairwise_distance,
        msm_pairwise_distance,
        lcss_pairwise_distance,
        shape_dtw_pairwise_distance
    )
}

fn cost_uni(e: Elastic, x: &[f64], y: &[f64], w: DtwWindow) -> Result<FdMatrix, FdarError> {
    dispatch!(
        e,
        (x, y),
        w,
        ddtw_cost_matrix,
        wdtw_cost_matrix,
        wddtw_cost_matrix,
        adtw_cost_matrix,
        erp_cost_matrix,
        edr_cost_matrix,
        twe_cost_matrix,
        msm_cost_matrix,
        lcss_cost_matrix,
        shape_dtw_cost_matrix
    )
}

fn path_uni(
    e: Elastic,
    x: &[f64],
    y: &[f64],
    w: DtwWindow,
) -> Result<ElasticDistancePath, FdarError> {
    dispatch!(
        e,
        (x, y),
        w,
        ddtw_alignment_path,
        wdtw_alignment_path,
        wddtw_alignment_path,
        adtw_alignment_path,
        erp_alignment_path,
        edr_alignment_path,
        twe_alignment_path,
        msm_alignment_path,
        lcss_alignment_path,
        shape_dtw_alignment_path
    )
}

fn distance_mv(e: Elastic, x: &FdMatrix, y: &FdMatrix, w: DtwWindow) -> Result<f64, FdarError> {
    dispatch!(
        e,
        (x, y),
        w,
        ddtw_distance_multivariate,
        wdtw_distance_multivariate,
        wddtw_distance_multivariate,
        adtw_distance_multivariate,
        erp_distance_multivariate,
        edr_distance_multivariate,
        twe_distance_multivariate,
        msm_distance_multivariate,
        lcss_distance_multivariate,
        shape_dtw_distance_multivariate
    )
}

fn pairwise_mv(
    e: Elastic,
    data: &[FdMatrix],
    other: Option<&[FdMatrix]>,
    w: DtwWindow,
) -> Result<FdMatrix, FdarError> {
    dispatch!(
        e,
        (data, other),
        w,
        ddtw_pairwise_distance_multivariate,
        wdtw_pairwise_distance_multivariate,
        wddtw_pairwise_distance_multivariate,
        adtw_pairwise_distance_multivariate,
        erp_pairwise_distance_multivariate,
        edr_pairwise_distance_multivariate,
        twe_pairwise_distance_multivariate,
        msm_pairwise_distance_multivariate,
        lcss_pairwise_distance_multivariate,
        shape_dtw_pairwise_distance_multivariate
    )
}

fn cost_mv(e: Elastic, x: &FdMatrix, y: &FdMatrix, w: DtwWindow) -> Result<FdMatrix, FdarError> {
    dispatch!(
        e,
        (x, y),
        w,
        ddtw_cost_matrix_multivariate,
        wdtw_cost_matrix_multivariate,
        wddtw_cost_matrix_multivariate,
        adtw_cost_matrix_multivariate,
        erp_cost_matrix_multivariate,
        edr_cost_matrix_multivariate,
        twe_cost_matrix_multivariate,
        msm_cost_matrix_multivariate,
        lcss_cost_matrix_multivariate,
        shape_dtw_cost_matrix_multivariate
    )
}

fn path_mv(
    e: Elastic,
    x: &FdMatrix,
    y: &FdMatrix,
    w: DtwWindow,
) -> Result<ElasticDistancePath, FdarError> {
    dispatch!(
        e,
        (x, y),
        w,
        ddtw_alignment_path_multivariate,
        wdtw_alignment_path_multivariate,
        wddtw_alignment_path_multivariate,
        adtw_alignment_path_multivariate,
        erp_alignment_path_multivariate,
        edr_alignment_path_multivariate,
        twe_alignment_path_multivariate,
        msm_alignment_path_multivariate,
        lcss_alignment_path_multivariate,
        shape_dtw_alignment_path_multivariate
    )
}

fn path_to_dict<'py>(py: Python<'py>, res: &ElasticDistancePath) -> PyResult<Bound<'py, PyDict>> {
    let d = PyDict::new(py);
    d.set_item("path", path_to_numpy(py, &res.path))?;
    d.set_item("distance", res.distance)?;
    Ok(d)
}

/// Window plus metric from the shared flat kwargs of every binding below.
macro_rules! window_and_metric {
    ($metric:expr, $window:expr, $radius:expr, $wf:expr, $ms:expr, $g:expr, $wp:expr,
     $eps:expr, $nu:expr, $lmbda:expr, $c:expr, $ind:expr, $desc:expr, $dp:expr, $reach:expr) => {
        (
            dtw_window($window, $radius, $wf, $ms)?,
            elastic_from_kwargs(
                $metric, $g, $wp, $eps, $nu, $lmbda, $c, $ind, $desc, $dp, $reach,
            )?,
        )
    };
}

// ---------------------------------------------------------------------------
// Univariate
// ---------------------------------------------------------------------------

/// Elastic distance between two series from the aeon family (DDTW, WDTW, ERP, EDR, TWE, MSM, LCSS, shape-DTW...).
///
/// Reproduces aeon 1.6 ``aeon.distances.<metric>_distance`` (golden-tested
/// in fdars-core to 1e-10), including aeon's normalisations.
///
/// Parameters
/// ----------
/// x, y : numpy.ndarray
///     Series (1D); lengths may differ.
/// metric : str
///     One of ``"ddtw"``, ``"wdtw"``, ``"wddtw"``, ``"adtw"``, ``"erp"``,
///     ``"edr"``, ``"twe"``, ``"msm"``, ``"lcss"``, ``"shape_dtw"``.
/// window, radius, window_fraction, max_slope
///     Global window, see `dtw_path`.  aeon's ``window=<fraction>`` is
///     ``window="sakoe_chiba_fraction"`` and ``itakura_max_slope=<fraction>``
///     is ``window="itakura_fraction"``.  For ddtw / wddtw the window applies
///     to the derivative series (length n - 2).
/// g : float, optional
///     wdtw / wddtw logistic weight steepness (default 0.05); erp gap value
///     (default 0.0).
/// warp_penalty : float, optional
///     adtw penalty per non-diagonal step (default 1.0).
/// epsilon : float, optional
///     edr match threshold (default None = ``max(sd x, sd y) / 4``); lcss
///     match threshold (default 1.0).
/// nu, lmbda : float, optional
///     twe stiffness (default 0.001) and edit penalty (default 1.0).
/// c : float, optional
///     msm move/split/merge cost (default 1.0).
/// independent : bool, optional
///     msm: absolute (True, default) or squared (False) cost.
/// descriptor : str, optional
///     shape_dtw subsequence descriptor: ``"identity"`` (default), ``"paa"``,
///     ``"dwt"``, ``"slope"`` or ``"derivative"``.
/// descriptor_param : int, optional
///     Number of PAA / slope intervals (default 8; ``1 <= v <= 2*reach+1``)
///     or DWT levels (default 3).
/// reach : int, optional
///     shape_dtw subsequence half-width (default 15, aeon's default).
///
/// Unused parameters for the chosen metric are ignored.
///
/// Returns
/// -------
/// float
///     The distance: accumulated cost for the DTW variants, erp, twe, msm
///     and shape_dtw; edits / max(n, m) for edr; ``1 - LCSS / min(n, m)``
///     for lcss.
#[pyfunction]
#[pyo3(signature = (x, y, metric, window="none", radius=None, window_fraction=None, max_slope=None, g=None, warp_penalty=1.0, epsilon=None, nu=0.001, lmbda=1.0, c=1.0, independent=true, descriptor="identity", descriptor_param=None, reach=15))]
pub fn elastic_ts_distance<'py>(
    x: PyReadonlyArray1<'py, f64>,
    y: PyReadonlyArray1<'py, f64>,
    metric: &str,
    window: &str,
    radius: Option<usize>,
    window_fraction: Option<f64>,
    max_slope: Option<f64>,
    g: Option<f64>,
    warp_penalty: f64,
    epsilon: Option<f64>,
    nu: f64,
    lmbda: f64,
    c: f64,
    independent: bool,
    descriptor: &str,
    descriptor_param: Option<usize>,
    reach: usize,
) -> PyResult<f64> {
    let (w, e) = window_and_metric!(
        metric,
        window,
        radius,
        window_fraction,
        max_slope,
        g,
        warp_penalty,
        epsilon,
        nu,
        lmbda,
        c,
        independent,
        descriptor,
        descriptor_param,
        reach
    );
    to_pyresult(distance_uni(e, &numpy1d_to_vec(x), &numpy1d_to_vec(y), w))
}

/// Pairwise elastic-distance matrix of a set of curves (aeon `<metric>_pairwise_distance`).
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Curves, shape (n, m).
/// metric : str
///     Elastic distance, see `elastic_ts_distance`.
/// other : numpy.ndarray, optional
///     Second set of curves (n_other, m'); default None gives the symmetric
///     self-distance matrix.
/// window, radius, window_fraction, max_slope, g, warp_penalty, epsilon, nu, lmbda, c, independent, descriptor, descriptor_param, reach
///     As in `elastic_ts_distance`.
///
/// Returns
/// -------
/// numpy.ndarray
///     (n, n) with zero diagonal, or (n, n_other).
#[pyfunction]
#[pyo3(signature = (data, metric, other=None, window="none", radius=None, window_fraction=None, max_slope=None, g=None, warp_penalty=1.0, epsilon=None, nu=0.001, lmbda=1.0, c=1.0, independent=true, descriptor="identity", descriptor_param=None, reach=15))]
pub fn elastic_ts_pairwise_distance<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    metric: &str,
    other: Option<PyReadonlyArray2<'py, f64>>,
    window: &str,
    radius: Option<usize>,
    window_fraction: Option<f64>,
    max_slope: Option<f64>,
    g: Option<f64>,
    warp_penalty: f64,
    epsilon: Option<f64>,
    nu: f64,
    lmbda: f64,
    c: f64,
    independent: bool,
    descriptor: &str,
    descriptor_param: Option<usize>,
    reach: usize,
) -> PyResult<Bound<'py, PyArray2<f64>>> {
    let (w, e) = window_and_metric!(
        metric,
        window,
        radius,
        window_fraction,
        max_slope,
        g,
        warp_penalty,
        epsilon,
        nu,
        lmbda,
        c,
        independent,
        descriptor,
        descriptor_param,
        reach
    );
    let data = numpy2d_to_fdmatrix(data)?;
    let other = other.map(numpy2d_to_fdmatrix).transpose()?;
    let res = to_pyresult(pairwise_uni(e, &data, other.as_ref(), w))?;
    Ok(fdmatrix_to_numpy2d(py, &res))
}

/// Accumulated elastic-distance cost matrix of two series (aeon `<metric>_cost_matrix`).
///
/// Parameters
/// ----------
/// x, y : numpy.ndarray
///     Series (1D).
/// metric : str
///     Elastic distance, see `elastic_ts_distance`.
/// window, radius, window_fraction, max_slope, g, warp_penalty, epsilon, nu, lmbda, c, independent, descriptor, descriptor_param, reach
///     As in `elastic_ts_distance`.
///
/// Returns
/// -------
/// numpy.ndarray
///     aeon's cost matrix: (n, m) in general, (n-2, m-2) for ddtw / wddtw
///     (derivative coordinates) and the padded (n+1, m+1) table for lcss.
///     Out-of-window cells hold aeon's fill value (inf, or 0 for lcss).
#[pyfunction]
#[pyo3(signature = (x, y, metric, window="none", radius=None, window_fraction=None, max_slope=None, g=None, warp_penalty=1.0, epsilon=None, nu=0.001, lmbda=1.0, c=1.0, independent=true, descriptor="identity", descriptor_param=None, reach=15))]
pub fn elastic_ts_cost_matrix<'py>(
    py: Python<'py>,
    x: PyReadonlyArray1<'py, f64>,
    y: PyReadonlyArray1<'py, f64>,
    metric: &str,
    window: &str,
    radius: Option<usize>,
    window_fraction: Option<f64>,
    max_slope: Option<f64>,
    g: Option<f64>,
    warp_penalty: f64,
    epsilon: Option<f64>,
    nu: f64,
    lmbda: f64,
    c: f64,
    independent: bool,
    descriptor: &str,
    descriptor_param: Option<usize>,
    reach: usize,
) -> PyResult<Bound<'py, PyArray2<f64>>> {
    let (w, e) = window_and_metric!(
        metric,
        window,
        radius,
        window_fraction,
        max_slope,
        g,
        warp_penalty,
        epsilon,
        nu,
        lmbda,
        c,
        independent,
        descriptor,
        descriptor_param,
        reach
    );
    let res = to_pyresult(cost_uni(e, &numpy1d_to_vec(x), &numpy1d_to_vec(y), w))?;
    Ok(fdmatrix_to_numpy2d(py, &res))
}

/// Optimal elastic-distance alignment path and distance (aeon `<metric>_alignment_path`).
///
/// Parameters
/// ----------
/// x, y : numpy.ndarray
///     Series (1D).
/// metric : str
///     Elastic distance, see `elastic_ts_distance`.
/// window, radius, window_fraction, max_slope, g, warp_penalty, epsilon, nu, lmbda, c, independent, descriptor, descriptor_param, reach
///     As in `elastic_ts_distance`.
///
/// Returns
/// -------
/// dict
///     ``path``: int64 array (L, 2) of aligned index pairs (derivative indices
///     for ddtw / wddtw; only the matched pairs for lcss, possibly empty);
///     ``distance``: the distance aeon reports with the path (for lcss
///     without the clamp at zero of `elastic_ts_distance`).
#[pyfunction]
#[pyo3(signature = (x, y, metric, window="none", radius=None, window_fraction=None, max_slope=None, g=None, warp_penalty=1.0, epsilon=None, nu=0.001, lmbda=1.0, c=1.0, independent=true, descriptor="identity", descriptor_param=None, reach=15))]
pub fn elastic_ts_alignment_path<'py>(
    py: Python<'py>,
    x: PyReadonlyArray1<'py, f64>,
    y: PyReadonlyArray1<'py, f64>,
    metric: &str,
    window: &str,
    radius: Option<usize>,
    window_fraction: Option<f64>,
    max_slope: Option<f64>,
    g: Option<f64>,
    warp_penalty: f64,
    epsilon: Option<f64>,
    nu: f64,
    lmbda: f64,
    c: f64,
    independent: bool,
    descriptor: &str,
    descriptor_param: Option<usize>,
    reach: usize,
) -> PyResult<Bound<'py, PyDict>> {
    let (w, e) = window_and_metric!(
        metric,
        window,
        radius,
        window_fraction,
        max_slope,
        g,
        warp_penalty,
        epsilon,
        nu,
        lmbda,
        c,
        independent,
        descriptor,
        descriptor_param,
        reach
    );
    let res = to_pyresult(path_uni(e, &numpy1d_to_vec(x), &numpy1d_to_vec(y), w))?;
    path_to_dict(py, &res)
}

// ---------------------------------------------------------------------------
// Multivariate
// ---------------------------------------------------------------------------

/// Elastic distance between two multivariate (d, m) series (aeon multichannel semantics).
///
/// Pointwise costs are dependent across channels (squared Euclidean, or its
/// root for erp / edr / twe / lcss); ddtw / wddtw differentiate every
/// channel; msm with ``independent=True`` sums per-channel costs.  With
/// ``d = 1`` the result is bit-identical to `elastic_ts_distance`.
///
/// Parameters
/// ----------
/// x, y : numpy.ndarray
///     Series of shape (d, n) and (d, m): one channel per row (aeon layout).
/// metric : str
///     Elastic distance, see `elastic_ts_distance`.
/// window, radius, window_fraction, max_slope, g, warp_penalty, epsilon, nu, lmbda, c, independent, descriptor, descriptor_param, reach
///     As in `elastic_ts_distance`.
///
/// Returns
/// -------
/// float
///     The distance.
#[pyfunction]
#[pyo3(signature = (x, y, metric, window="none", radius=None, window_fraction=None, max_slope=None, g=None, warp_penalty=1.0, epsilon=None, nu=0.001, lmbda=1.0, c=1.0, independent=true, descriptor="identity", descriptor_param=None, reach=15))]
pub fn elastic_ts_distance_multivariate<'py>(
    x: PyReadonlyArray2<'py, f64>,
    y: PyReadonlyArray2<'py, f64>,
    metric: &str,
    window: &str,
    radius: Option<usize>,
    window_fraction: Option<f64>,
    max_slope: Option<f64>,
    g: Option<f64>,
    warp_penalty: f64,
    epsilon: Option<f64>,
    nu: f64,
    lmbda: f64,
    c: f64,
    independent: bool,
    descriptor: &str,
    descriptor_param: Option<usize>,
    reach: usize,
) -> PyResult<f64> {
    let (w, e) = window_and_metric!(
        metric,
        window,
        radius,
        window_fraction,
        max_slope,
        g,
        warp_penalty,
        epsilon,
        nu,
        lmbda,
        c,
        independent,
        descriptor,
        descriptor_param,
        reach
    );
    to_pyresult(distance_mv(
        e,
        &numpy2d_to_fdmatrix(x)?,
        &numpy2d_to_fdmatrix(y)?,
        w,
    ))
}

/// Pairwise elastic-distance matrix of a collection of multivariate series.
///
/// Parameters
/// ----------
/// data : list of numpy.ndarray or numpy.ndarray
///     Series as a list of (d, m_i) arrays (lengths may differ) or a 3-D
///     (n, d, m) array.
/// metric : str
///     Elastic distance, see `elastic_ts_distance`.
/// other : list of numpy.ndarray or numpy.ndarray, optional
///     Second collection with the same channel count; default None gives the
///     symmetric self-distance matrix.
/// window, radius, window_fraction, max_slope, g, warp_penalty, epsilon, nu, lmbda, c, independent, descriptor, descriptor_param, reach
///     As in `elastic_ts_distance`.
///
/// Returns
/// -------
/// numpy.ndarray
///     (n, n) with zero diagonal, or (n, n_other).
#[pyfunction]
#[pyo3(signature = (data, metric, other=None, window="none", radius=None, window_fraction=None, max_slope=None, g=None, warp_penalty=1.0, epsilon=None, nu=0.001, lmbda=1.0, c=1.0, independent=true, descriptor="identity", descriptor_param=None, reach=15))]
pub fn elastic_ts_pairwise_distance_multivariate<'py>(
    py: Python<'py>,
    data: &Bound<'py, PyAny>,
    metric: &str,
    other: Option<&Bound<'py, PyAny>>,
    window: &str,
    radius: Option<usize>,
    window_fraction: Option<f64>,
    max_slope: Option<f64>,
    g: Option<f64>,
    warp_penalty: f64,
    epsilon: Option<f64>,
    nu: f64,
    lmbda: f64,
    c: f64,
    independent: bool,
    descriptor: &str,
    descriptor_param: Option<usize>,
    reach: usize,
) -> PyResult<Bound<'py, PyArray2<f64>>> {
    let (w, e) = window_and_metric!(
        metric,
        window,
        radius,
        window_fraction,
        max_slope,
        g,
        warp_penalty,
        epsilon,
        nu,
        lmbda,
        c,
        independent,
        descriptor,
        descriptor_param,
        reach
    );
    let series = series_collection(data, "elastic_ts_pairwise_distance_multivariate: data")?;
    let other = other
        .map(|o| series_collection(o, "elastic_ts_pairwise_distance_multivariate: other"))
        .transpose()?;
    let res = to_pyresult(pairwise_mv(e, &series, other.as_deref(), w))?;
    Ok(fdmatrix_to_numpy2d(py, &res))
}

/// Accumulated elastic-distance cost matrix of two multivariate (d, m) series.
///
/// Parameters
/// ----------
/// x, y : numpy.ndarray
///     Series of shape (d, n) and (d, m), channels as rows.
/// metric : str
///     Elastic distance, see `elastic_ts_distance`.
/// window, radius, window_fraction, max_slope, g, warp_penalty, epsilon, nu, lmbda, c, independent, descriptor, descriptor_param, reach
///     As in `elastic_ts_distance`.
///
/// Returns
/// -------
/// numpy.ndarray
///     The cost matrix, shaped as in `elastic_ts_cost_matrix`.
#[pyfunction]
#[pyo3(signature = (x, y, metric, window="none", radius=None, window_fraction=None, max_slope=None, g=None, warp_penalty=1.0, epsilon=None, nu=0.001, lmbda=1.0, c=1.0, independent=true, descriptor="identity", descriptor_param=None, reach=15))]
pub fn elastic_ts_cost_matrix_multivariate<'py>(
    py: Python<'py>,
    x: PyReadonlyArray2<'py, f64>,
    y: PyReadonlyArray2<'py, f64>,
    metric: &str,
    window: &str,
    radius: Option<usize>,
    window_fraction: Option<f64>,
    max_slope: Option<f64>,
    g: Option<f64>,
    warp_penalty: f64,
    epsilon: Option<f64>,
    nu: f64,
    lmbda: f64,
    c: f64,
    independent: bool,
    descriptor: &str,
    descriptor_param: Option<usize>,
    reach: usize,
) -> PyResult<Bound<'py, PyArray2<f64>>> {
    let (w, e) = window_and_metric!(
        metric,
        window,
        radius,
        window_fraction,
        max_slope,
        g,
        warp_penalty,
        epsilon,
        nu,
        lmbda,
        c,
        independent,
        descriptor,
        descriptor_param,
        reach
    );
    let res = to_pyresult(cost_mv(
        e,
        &numpy2d_to_fdmatrix(x)?,
        &numpy2d_to_fdmatrix(y)?,
        w,
    ))?;
    Ok(fdmatrix_to_numpy2d(py, &res))
}

/// Optimal elastic-distance alignment path and distance of two multivariate (d, m) series.
///
/// Parameters
/// ----------
/// x, y : numpy.ndarray
///     Series of shape (d, n) and (d, m), channels as rows.
/// metric : str
///     Elastic distance, see `elastic_ts_distance`.
/// window, radius, window_fraction, max_slope, g, warp_penalty, epsilon, nu, lmbda, c, independent, descriptor, descriptor_param, reach
///     As in `elastic_ts_distance`.
///
/// Returns
/// -------
/// dict
///     ``path`` (L, 2) int64 and ``distance``, as in `elastic_ts_alignment_path`.
#[pyfunction]
#[pyo3(signature = (x, y, metric, window="none", radius=None, window_fraction=None, max_slope=None, g=None, warp_penalty=1.0, epsilon=None, nu=0.001, lmbda=1.0, c=1.0, independent=true, descriptor="identity", descriptor_param=None, reach=15))]
pub fn elastic_ts_alignment_path_multivariate<'py>(
    py: Python<'py>,
    x: PyReadonlyArray2<'py, f64>,
    y: PyReadonlyArray2<'py, f64>,
    metric: &str,
    window: &str,
    radius: Option<usize>,
    window_fraction: Option<f64>,
    max_slope: Option<f64>,
    g: Option<f64>,
    warp_penalty: f64,
    epsilon: Option<f64>,
    nu: f64,
    lmbda: f64,
    c: f64,
    independent: bool,
    descriptor: &str,
    descriptor_param: Option<usize>,
    reach: usize,
) -> PyResult<Bound<'py, PyDict>> {
    let (w, e) = window_and_metric!(
        metric,
        window,
        radius,
        window_fraction,
        max_slope,
        g,
        warp_penalty,
        epsilon,
        nu,
        lmbda,
        c,
        independent,
        descriptor,
        descriptor_param,
        reach
    );
    let res = to_pyresult(path_mv(
        e,
        &numpy2d_to_fdmatrix(x)?,
        &numpy2d_to_fdmatrix(y)?,
        w,
    ))?;
    path_to_dict(py, &res)
}

/// Register the elastic-distance family into the `metric` submodule.
pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(elastic_ts_distance, m)?)?;
    m.add_function(wrap_pyfunction!(elastic_ts_pairwise_distance, m)?)?;
    m.add_function(wrap_pyfunction!(elastic_ts_cost_matrix, m)?)?;
    m.add_function(wrap_pyfunction!(elastic_ts_alignment_path, m)?)?;
    m.add_function(wrap_pyfunction!(elastic_ts_distance_multivariate, m)?)?;
    m.add_function(wrap_pyfunction!(
        elastic_ts_pairwise_distance_multivariate,
        m
    )?)?;
    m.add_function(wrap_pyfunction!(elastic_ts_cost_matrix_multivariate, m)?)?;
    m.add_function(wrap_pyfunction!(elastic_ts_alignment_path_multivariate, m)?)?;
    Ok(())
}
