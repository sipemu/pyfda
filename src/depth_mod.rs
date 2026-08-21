//! Depth measures for functional data.

use crate::convert::*;
use fdars_core::depth::DepthMethod;
use numpy::{PyArray1, PyReadonlyArray1, PyReadonlyArray2};
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::PyDict;

/// Fraiman-Muniz depth for 1D functional data.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Data to compute depth for, shape (n, m).
/// ref_data : numpy.ndarray
///     Reference sample, shape (n_ref, m).
/// scale : bool, optional
///     Whether to scale the depth values (default True).
///
/// Returns
/// -------
/// numpy.ndarray
///     Depth values, length n.
#[pyfunction]
#[pyo3(signature = (data, ref_data, scale=true))]
pub fn fraiman_muniz_1d<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    ref_data: PyReadonlyArray2<'py, f64>,
    scale: bool,
) -> PyResult<Bound<'py, PyArray1<f64>>> {
    let d = numpy2d_to_fdmatrix(data)?;
    let r = numpy2d_to_fdmatrix(ref_data)?;
    let result = fdars_core::depth::fraiman_muniz_1d(&d, &r, scale);
    Ok(vec_to_numpy1d(py, result))
}

/// Fraiman-Muniz depth for 2D functional data.
#[pyfunction]
#[pyo3(signature = (data, ref_data, scale=true))]
pub fn fraiman_muniz_2d<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    ref_data: PyReadonlyArray2<'py, f64>,
    scale: bool,
) -> PyResult<Bound<'py, PyArray1<f64>>> {
    let d = numpy2d_to_fdmatrix(data)?;
    let r = numpy2d_to_fdmatrix(ref_data)?;
    let result = fdars_core::depth::fraiman_muniz_2d(&d, &r, scale);
    Ok(vec_to_numpy1d(py, result))
}

/// Modal depth for 1D functional data.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Data to compute depth for, shape (n, m).
/// ref_data : numpy.ndarray
///     Reference sample, shape (n_ref, m).
/// h : float, optional
///     Bandwidth (default 1.0).
///
/// Returns
/// -------
/// numpy.ndarray
///     Depth values, length n.
#[pyfunction]
#[pyo3(signature = (data, ref_data, h=1.0))]
pub fn modal_1d<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    ref_data: PyReadonlyArray2<'py, f64>,
    h: f64,
) -> PyResult<Bound<'py, PyArray1<f64>>> {
    let d = numpy2d_to_fdmatrix(data)?;
    let r = numpy2d_to_fdmatrix(ref_data)?;
    let result = fdars_core::depth::modal_1d(&d, &r, h);
    Ok(vec_to_numpy1d(py, result))
}

/// Modal depth for 2D functional data.
#[pyfunction]
#[pyo3(signature = (data, ref_data, h=1.0))]
pub fn modal_2d<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    ref_data: PyReadonlyArray2<'py, f64>,
    h: f64,
) -> PyResult<Bound<'py, PyArray1<f64>>> {
    let d = numpy2d_to_fdmatrix(data)?;
    let r = numpy2d_to_fdmatrix(ref_data)?;
    let result = fdars_core::depth::modal_2d(&d, &r, h);
    Ok(vec_to_numpy1d(py, result))
}

/// Random projection depth for 1D functional data.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Data, shape (n, m).
/// ref_data : numpy.ndarray
///     Reference, shape (n_ref, m).
/// n_proj : int, optional
///     Number of projections (default 50).
///
/// Returns
/// -------
/// numpy.ndarray
///     Depth values, length n.
#[pyfunction]
#[pyo3(signature = (data, ref_data, n_proj=50))]
pub fn random_projection_1d<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    ref_data: PyReadonlyArray2<'py, f64>,
    n_proj: usize,
) -> PyResult<Bound<'py, PyArray1<f64>>> {
    let d = numpy2d_to_fdmatrix(data)?;
    let r = numpy2d_to_fdmatrix(ref_data)?;
    let result = fdars_core::depth::random_projection_1d(&d, &r, n_proj);
    Ok(vec_to_numpy1d(py, result))
}

/// Random projection depth for 2D functional data.
#[pyfunction]
#[pyo3(signature = (data, ref_data, n_proj=50))]
pub fn random_projection_2d<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    ref_data: PyReadonlyArray2<'py, f64>,
    n_proj: usize,
) -> PyResult<Bound<'py, PyArray1<f64>>> {
    let d = numpy2d_to_fdmatrix(data)?;
    let r = numpy2d_to_fdmatrix(ref_data)?;
    let result = fdars_core::depth::random_projection_2d(&d, &r, n_proj);
    Ok(vec_to_numpy1d(py, result))
}

/// Random Tukey depth for 1D functional data.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Data, shape (n, m).
/// ref_data : numpy.ndarray
///     Reference, shape (n_ref, m).
/// n_proj : int, optional
///     Number of projections (default 50).
///
/// Returns
/// -------
/// numpy.ndarray
///     Depth values, length n.
#[pyfunction]
#[pyo3(signature = (data, ref_data, n_proj=50))]
pub fn random_tukey_1d<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    ref_data: PyReadonlyArray2<'py, f64>,
    n_proj: usize,
) -> PyResult<Bound<'py, PyArray1<f64>>> {
    let d = numpy2d_to_fdmatrix(data)?;
    let r = numpy2d_to_fdmatrix(ref_data)?;
    let result = fdars_core::depth::random_tukey_1d(&d, &r, n_proj);
    Ok(vec_to_numpy1d(py, result))
}

/// Random Tukey depth for 2D functional data.
#[pyfunction]
#[pyo3(signature = (data, ref_data, n_proj=50))]
pub fn random_tukey_2d<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    ref_data: PyReadonlyArray2<'py, f64>,
    n_proj: usize,
) -> PyResult<Bound<'py, PyArray1<f64>>> {
    let d = numpy2d_to_fdmatrix(data)?;
    let r = numpy2d_to_fdmatrix(ref_data)?;
    let result = fdars_core::depth::random_tukey_2d(&d, &r, n_proj);
    Ok(vec_to_numpy1d(py, result))
}

/// Band depth for 1D functional data.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Data, shape (n, m).
/// ref_data : numpy.ndarray
///     Reference, shape (n_ref, m).
///
/// Returns
/// -------
/// numpy.ndarray
///     Depth values, length n.
#[pyfunction]
pub fn band_1d<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    ref_data: PyReadonlyArray2<'py, f64>,
) -> PyResult<Bound<'py, PyArray1<f64>>> {
    let d = numpy2d_to_fdmatrix(data)?;
    let r = numpy2d_to_fdmatrix(ref_data)?;
    let result = fdars_core::depth::band_1d(&d, &r);
    Ok(vec_to_numpy1d(py, result))
}

/// Modified band depth for 1D functional data.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Data, shape (n, m).
/// ref_data : numpy.ndarray
///     Reference, shape (n_ref, m).
///
/// Returns
/// -------
/// numpy.ndarray
///     Depth values, length n.
#[pyfunction]
pub fn modified_band_1d<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    ref_data: PyReadonlyArray2<'py, f64>,
) -> PyResult<Bound<'py, PyArray1<f64>>> {
    let d = numpy2d_to_fdmatrix(data)?;
    let r = numpy2d_to_fdmatrix(ref_data)?;
    let result = fdars_core::depth::modified_band_1d(&d, &r);
    Ok(vec_to_numpy1d(py, result))
}

/// Modified epigraph index for 1D functional data.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Data, shape (n, m).
/// ref_data : numpy.ndarray
///     Reference, shape (n_ref, m).
///
/// Returns
/// -------
/// numpy.ndarray
///     Depth values, length n.
#[pyfunction]
pub fn modified_epigraph_index_1d<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    ref_data: PyReadonlyArray2<'py, f64>,
) -> PyResult<Bound<'py, PyArray1<f64>>> {
    let d = numpy2d_to_fdmatrix(data)?;
    let r = numpy2d_to_fdmatrix(ref_data)?;
    let result = fdars_core::depth::modified_epigraph_index_1d(&d, &r);
    Ok(vec_to_numpy1d(py, result))
}

/// Functional spatial depth for 1D data.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Data, shape (n, m).
/// ref_data : numpy.ndarray
///     Reference, shape (n_ref, m).
/// argvals : numpy.ndarray, optional
///     Evaluation points, length m. If None, uses uniform [0,1] grid.
///
/// Returns
/// -------
/// numpy.ndarray
///     Depth values, length n.
#[pyfunction]
#[pyo3(signature = (data, ref_data, argvals=None))]
pub fn functional_spatial_1d<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    ref_data: PyReadonlyArray2<'py, f64>,
    argvals: Option<PyReadonlyArray1<'py, f64>>,
) -> PyResult<Bound<'py, PyArray1<f64>>> {
    let d = numpy2d_to_fdmatrix(data)?;
    let r = numpy2d_to_fdmatrix(ref_data)?;
    let av = argvals.map(numpy1d_to_vec);
    let result = fdars_core::depth::functional_spatial_1d(&d, &r, av.as_deref());
    Ok(vec_to_numpy1d(py, result))
}

/// Functional spatial depth for 2D data.
#[pyfunction]
pub fn functional_spatial_2d<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    ref_data: PyReadonlyArray2<'py, f64>,
) -> PyResult<Bound<'py, PyArray1<f64>>> {
    let d = numpy2d_to_fdmatrix(data)?;
    let r = numpy2d_to_fdmatrix(ref_data)?;
    let result = fdars_core::depth::functional_spatial_2d(&d, &r);
    Ok(vec_to_numpy1d(py, result))
}

/// Kernel functional spatial depth for 1D data.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Data, shape (n, m).
/// ref_data : numpy.ndarray
///     Reference, shape (n_ref, m).
/// argvals : numpy.ndarray
///     Evaluation points, length m.
/// h : float, optional
///     Bandwidth (default 1.0).
///
/// Returns
/// -------
/// numpy.ndarray
///     Depth values, length n.
#[pyfunction]
#[pyo3(signature = (data, ref_data, argvals, h=1.0))]
pub fn kernel_functional_spatial_1d<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    ref_data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    h: f64,
) -> PyResult<Bound<'py, PyArray1<f64>>> {
    let d = numpy2d_to_fdmatrix(data)?;
    let r = numpy2d_to_fdmatrix(ref_data)?;
    let av = numpy1d_to_vec(argvals);
    let result = fdars_core::depth::kernel_functional_spatial_1d(&d, &r, &av, h);
    Ok(vec_to_numpy1d(py, result))
}

/// Kernel functional spatial depth for 2D data.
#[pyfunction]
#[pyo3(signature = (data, ref_data, h=1.0))]
pub fn kernel_functional_spatial_2d<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    ref_data: PyReadonlyArray2<'py, f64>,
    h: f64,
) -> PyResult<Bound<'py, PyArray1<f64>>> {
    let d = numpy2d_to_fdmatrix(data)?;
    let r = numpy2d_to_fdmatrix(ref_data)?;
    let result = fdars_core::depth::kernel_functional_spatial_2d(&d, &r, h);
    Ok(vec_to_numpy1d(py, result))
}

/// Random-projection depth using curves and their derivatives (RPD).
///
/// Projects both the curves and their `n_deriv`-order derivatives onto random
/// directions and combines the resulting univariate depths. Matches R
/// `depth(method = "RPD")` / `depth.RPD`.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Data to score, shape (n, m).
/// ref_data : numpy.ndarray
///     Reference sample, shape (n_ref, m).
/// argvals : numpy.ndarray, optional
///     Evaluation grid, length m. Defaults to a uniform [0, 1] grid.
/// n_proj : int, optional
///     Number of random projections (default 50).
/// n_deriv : int, optional
///     Derivative order to include (default 1).
/// seed : int, optional
///     Seed for reproducible projections.
///
/// Returns
/// -------
/// numpy.ndarray
///     Depth values, length n.
#[pyfunction]
#[pyo3(signature = (data, ref_data, argvals=None, n_proj=50, n_deriv=1, seed=None))]
pub fn random_projection_deriv_1d<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    ref_data: PyReadonlyArray2<'py, f64>,
    argvals: Option<PyReadonlyArray1<'py, f64>>,
    n_proj: usize,
    n_deriv: usize,
    seed: Option<u64>,
) -> PyResult<Bound<'py, PyArray1<f64>>> {
    let d = numpy2d_to_fdmatrix(data)?;
    let r = numpy2d_to_fdmatrix(ref_data)?;
    let m = d.ncols();
    let av = match argvals {
        Some(a) => numpy1d_to_vec(a),
        None => {
            if m <= 1 {
                vec![0.0; m]
            } else {
                (0..m).map(|i| i as f64 / (m - 1) as f64).collect()
            }
        }
    };
    let result = fdars_core::depth::rpd_depth_1d_seeded(&d, &r, &av, n_proj, n_deriv, seed);
    Ok(vec_to_numpy1d(py, result))
}

// ---------------------------------------------------------------------------
// Internal helper: map a method string to DepthMethod.
//
// The enum is #[non_exhaustive] — the wildcard arm is mandatory.  An unknown
// string becomes a Python ValueError listing the four accepted values.
// `seed=None` resolves to `0` here, matching the Phase 31 seed contract and
// giving byte-identical results for `random_projection` by default.
// ---------------------------------------------------------------------------

fn depth_method_from_str(
    method: &str,
    scale: bool,
    nproj: usize,
    seed: Option<u64>,
) -> PyResult<DepthMethod> {
    match method {
        "fraiman_muniz" => Ok(DepthMethod::FraimanMuniz { scale }),
        "band" => Ok(DepthMethod::Band),
        "modified_band" => Ok(DepthMethod::ModifiedBand),
        "random_projection" => Ok(DepthMethod::RandomProjection {
            nproj,
            seed: seed.unwrap_or(0),
        }),
        "total_variation" => Ok(DepthMethod::TotalVariation),
        "hypograph_index" => Ok(DepthMethod::HypographIndex),
        "modified_hypograph_index" => Ok(DepthMethod::ModifiedHypographIndex),
        "epigraph_index" => Ok(DepthMethod::EpigraphIndex),
        "half_region" => Ok(DepthMethod::HalfRegion),
        "modified_half_region" => Ok(DepthMethod::ModifiedHalfRegion),
        "extremal" => Ok(DepthMethod::Extremal),
        "extreme_rank_length" => Ok(DepthMethod::ExtremeRankLength),
        "l_infinity" => Ok(DepthMethod::LInfinity),
        other => Err(PyValueError::new_err(format!(
            "method must be one of 'fraiman_muniz', 'band', 'modified_band', \
             'random_projection', 'total_variation', 'hypograph_index', \
             'modified_hypograph_index', 'epigraph_index', 'half_region', \
             'modified_half_region', 'extremal', 'extreme_rank_length', \
             'l_infinity' (13 supported methods), got '{other}'"
        ))),
    }
}

// ---------------------------------------------------------------------------
// Internal helper: map a FunctionalBoxplotResult to a Python dict.
//
// The struct is #[non_exhaustive] — never struct-literal it; access each
// field individually.  Band fields (Vec<f64>, length m) become 1-D ndarrays
// via vec_to_numpy1d; outliers (Vec<usize>) become a Python list of ints.
// ---------------------------------------------------------------------------

fn boxplot_result_to_pydict<'py>(
    py: Python<'py>,
    r: fdars_core::depth::FunctionalBoxplotResult,
) -> PyResult<Bound<'py, PyDict>> {
    let dict = PyDict::new(py);
    dict.set_item("median", vec_to_numpy1d(py, r.median))?;
    dict.set_item("central_lower", vec_to_numpy1d(py, r.central_lower))?;
    dict.set_item("central_upper", vec_to_numpy1d(py, r.central_upper))?;
    dict.set_item("whisker_lower", vec_to_numpy1d(py, r.whisker_lower))?;
    dict.set_item("whisker_upper", vec_to_numpy1d(py, r.whisker_upper))?;
    dict.set_item(
        "outliers",
        r.outliers
            .into_iter()
            .map(|x| x as i64)
            .collect::<Vec<i64>>(),
    )?;
    dict.set_item("depths", vec_to_numpy1d(py, r.depths))?;
    Ok(dict)
}

/// Unified self-depth dispatcher for functional data.
///
/// Computes the self-depth of every curve in `data` with respect to the sample
/// itself, dispatching to the underlying depth algorithm selected by `method`.
/// Returns one depth per curve — an ndarray of shape `(n,)` where `n` is the
/// number of rows (observations) in `data`.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Functional data matrix, shape `(n, m)`. Rows are observations; columns
///     are evaluation points.
/// method : str, optional
///     Depth measure to use. One of 13 supported strings (default
///     ``"fraiman_muniz"``): ``"fraiman_muniz"``, ``"band"``,
///     ``"modified_band"``, ``"random_projection"``, ``"total_variation"``,
///     ``"hypograph_index"``, ``"modified_hypograph_index"``,
///     ``"epigraph_index"``, ``"half_region"``, ``"modified_half_region"``,
///     ``"extremal"``, ``"extreme_rank_length"``, ``"l_infinity"``.
///     An unknown string raises ``ValueError`` listing all 13.
/// scale : bool, optional
///     Applies only to ``"fraiman_muniz"``: whether to scale depths to
///     ``2·min(Fn, 1-Fn)`` form (default ``True``).
/// nproj : int, optional
///     Number of random projection directions; applies only to
///     ``"random_projection"`` (default 50). Must be ``>= 1``.
/// seed : int or None, optional
///     RNG seed for ``"random_projection"``. ``None`` resolves to fixed default
///     ``0`` — two calls with ``seed=None`` and identical inputs are
///     byte-identical. Pass an explicit integer to override.
///
/// Returns
/// -------
/// numpy.ndarray
///     Self-depth values, shape ``(n,)``.
///
/// Raises
/// ------
/// ValueError
///     If ``method`` is not one of the 13 accepted strings; if ``data`` is
///     empty; if a method requiring ``n >= 2`` (or ``n >= 3``) is called with
///     too few curves; or if ``nproj == 0`` for ``"random_projection"``.
#[pyfunction]
#[pyo3(signature = (data, method = "fraiman_muniz", scale = true, nproj = 50, seed = None))]
pub fn functional_depth<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    method: &str,
    scale: bool,
    nproj: usize,
    seed: Option<u64>,
) -> PyResult<Bound<'py, PyArray1<f64>>> {
    let d = numpy2d_to_fdmatrix(data)?;
    let depth_method = depth_method_from_str(method, scale, nproj, seed)?;
    let result = to_pyresult(fdars_core::depth::functional_depth(&d, depth_method))?;
    Ok(vec_to_numpy1d(py, result))
}

/// Canonical López-Pintado–Romo depth-fence functional boxplot (numeric only).
///
/// Ranks curves by self-depth, takes the deepest curve as the median, builds
/// the 50% central region as the pointwise envelope of the deepest half,
/// inflates it by `factor × (central width)` to form the fence/whiskers, and
/// flags any curve that exceeds the fence at any evaluation point as an outlier.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Functional data matrix, shape ``(n, m)``. Rows are observations.
///     Requires at least 2 rows.
/// method : str, optional
///     Depth measure used to rank curves. One of 13 supported strings
///     (default ``"modified_band"``): ``"fraiman_muniz"``, ``"band"``,
///     ``"modified_band"``, ``"random_projection"``, ``"total_variation"``,
///     ``"hypograph_index"``, ``"modified_hypograph_index"``,
///     ``"epigraph_index"``, ``"half_region"``, ``"modified_half_region"``,
///     ``"extremal"``, ``"extreme_rank_length"``, ``"l_infinity"``.
///     An unknown string raises ``ValueError`` listing all 13.
/// factor : float, optional
///     Fence inflation factor (default 1.5, the Tukey convention). Must be
///     finite and ``>= 0``. Negative or non-finite values raise ``ValueError``.
/// scale : bool, optional
///     Passed to ``"fraiman_muniz"`` (default ``True``).
/// nproj : int, optional
///     Number of projection directions for ``"random_projection"`` (default 50).
/// seed : int or None, optional
///     RNG seed for ``"random_projection"``. ``None`` resolves to ``0`` for
///     byte-identical results across calls.
///
/// Returns
/// -------
/// dict
///     A seven-key dict:
///
///     - ``"median"``: ndarray of shape ``(m,)`` — the deepest curve's values.
///     - ``"central_lower"``: ndarray of shape ``(m,)`` — pointwise lower bound
///       of the 50% central region.
///     - ``"central_upper"``: ndarray of shape ``(m,)`` — pointwise upper bound
///       of the 50% central region.
///     - ``"whisker_lower"``: ndarray of shape ``(m,)`` — lower fence values.
///     - ``"whisker_upper"``: ndarray of shape ``(m,)`` — upper fence values.
///     - ``"outliers"``: Python ``list`` of ``int`` — 0-based row indices of
///       curves flagged as outliers (length variable).
///     - ``"depths"``: ndarray of shape ``(n,)`` — per-curve self-depth.
///
/// Raises
/// ------
/// ValueError
///     If ``data`` has fewer than 2 rows, if ``data`` is empty, if ``factor``
///     is negative or non-finite, or if ``method`` is an unknown string.
#[pyfunction]
#[pyo3(signature = (data, method = "modified_band", factor = 1.5, scale = true, nproj = 50, seed = None))]
pub fn functional_boxplot<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    method: &str,
    factor: f64,
    scale: bool,
    nproj: usize,
    seed: Option<u64>,
) -> PyResult<Bound<'py, PyDict>> {
    let d = numpy2d_to_fdmatrix(data)?;
    let depth_method = depth_method_from_str(method, scale, nproj, seed)?;
    let result = to_pyresult(fdars_core::depth::functional_boxplot(
        &d,
        depth_method,
        factor,
    ))?;
    boxplot_result_to_pydict(py, result)
}

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(fraiman_muniz_1d, m)?)?;
    m.add_function(wrap_pyfunction!(random_projection_deriv_1d, m)?)?;
    m.add_function(wrap_pyfunction!(fraiman_muniz_2d, m)?)?;
    m.add_function(wrap_pyfunction!(modal_1d, m)?)?;
    m.add_function(wrap_pyfunction!(modal_2d, m)?)?;
    m.add_function(wrap_pyfunction!(random_projection_1d, m)?)?;
    m.add_function(wrap_pyfunction!(random_projection_2d, m)?)?;
    m.add_function(wrap_pyfunction!(random_tukey_1d, m)?)?;
    m.add_function(wrap_pyfunction!(random_tukey_2d, m)?)?;
    m.add_function(wrap_pyfunction!(band_1d, m)?)?;
    m.add_function(wrap_pyfunction!(modified_band_1d, m)?)?;
    m.add_function(wrap_pyfunction!(modified_epigraph_index_1d, m)?)?;
    m.add_function(wrap_pyfunction!(functional_spatial_1d, m)?)?;
    m.add_function(wrap_pyfunction!(functional_spatial_2d, m)?)?;
    m.add_function(wrap_pyfunction!(kernel_functional_spatial_1d, m)?)?;
    m.add_function(wrap_pyfunction!(kernel_functional_spatial_2d, m)?)?;
    m.add_function(wrap_pyfunction!(functional_depth, m)?)?;
    m.add_function(wrap_pyfunction!(functional_boxplot, m)?)?;
    Ok(())
}
