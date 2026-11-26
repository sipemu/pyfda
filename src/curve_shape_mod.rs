//! Elastic shape analysis of R^d curves (rotation / scale / seed / warp
//! quotients, open or closed), the general `(a, b)` elastic metrics, the exact
//! piecewise-linear `(a, b)` distance and sparse / irregular elastic curves of
//! fdars-core 0.48.
//!
//! A curve is a `(d, m)` array (row = coordinate); a set of curves is a list of
//! `(d, m)` arrays or a `(n, d, m)` array. Registered into the existing
//! `fdars.alignment` submodule by `alignment_mod::register`; it is not a
//! submodule of its own.

use crate::convert::*;
use crate::options::{outlier_threshold, warp_optim_from_dict};
use crate::pace_fpca_mod::PyIrregFdata;
use fdars_core::alignment::{
    CurveShapeAlignment, CurveShapeBoxplot, CurveShapeBoxplotConfig, CurveShapeCentre,
    CurveShapeCiConfig, CurveShapeCiMethod, CurveShapeConfig, CurveShapeKarcherResult,
    CurveShapeMetric, CurveShapeOutlierConfig, CurveShapePcaResult, SparseAlignConfig, SparseCurve,
    SparseElasticMeanConfig, SparseElasticMeanResult, SparseMeanType,
};
use fdars_core::matrix::FdMatrix;
use numpy::ndarray::Array2;
use numpy::{PyArray1, PyArray2, PyReadonlyArray1, PyReadonlyArray2};
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};

// ---------------------------------------------------------------------------
// Option builders and result converters
// ---------------------------------------------------------------------------

/// Build a `CurveShapeConfig` from the shared shape-quotient kwargs.
fn shape_config(
    rotation: bool,
    allow_reflection: bool,
    scale: bool,
    include_length: bool,
    closed: bool,
    seed_search: bool,
    seed_step: usize,
    reparam: bool,
    lambda: f64,
    align_iter: usize,
    metric: &str,
    a: Option<f64>,
    b: Option<f64>,
    branch_search: bool,
    warp_optim: Option<&Bound<'_, PyDict>>,
) -> PyResult<CurveShapeConfig> {
    let mut cfg = CurveShapeConfig::default();
    cfg.rotation = rotation;
    cfg.allow_reflection = allow_reflection;
    cfg.scale = scale;
    cfg.include_length = include_length;
    cfg.closed = closed;
    cfg.seed_search = seed_search;
    cfg.seed_step = seed_step;
    cfg.reparam = reparam;
    cfg.lambda = lambda;
    cfg.align_iter = align_iter;
    cfg.metric = match (metric, a, b) {
        ("srvf", None, None) => CurveShapeMetric::Srvf,
        ("srvf", _, _) => {
            return Err(PyValueError::new_err(
                "a and b are only used with metric='elastic' (the SRVF is a=1, b=0.5)",
            ))
        }
        ("elastic", Some(a), Some(b)) => CurveShapeMetric::Elastic { a, b },
        ("elastic", _, _) => {
            return Err(PyValueError::new_err(
                "metric='elastic' requires both a and b",
            ))
        }
        _ => {
            return Err(PyValueError::new_err(format!(
                "metric must be one of 'srvf', 'elastic', got '{metric}'"
            )))
        }
    };
    cfg.branch_search = branch_search;
    cfg.warp_optim = warp_optim_from_dict(warp_optim)?;
    Ok(cfg)
}

fn boxplot_config(alpha: f64, k_a: f64) -> CurveShapeBoxplotConfig {
    let mut cfg = CurveShapeBoxplotConfig::default();
    cfg.alpha = alpha;
    cfg.k_a = k_a;
    cfg
}

fn alignment_dict<'py>(py: Python<'py>, r: CurveShapeAlignment) -> PyResult<Bound<'py, PyDict>> {
    let dict = PyDict::new(py);
    dict.set_item("beta1", fdmatrix_to_numpy2d(py, &r.beta1))?;
    dict.set_item("beta2_aligned", fdmatrix_to_numpy2d(py, &r.beta2_aligned))?;
    dict.set_item("q1", fdmatrix_to_numpy2d(py, &r.q1))?;
    dict.set_item("q2_aligned", fdmatrix_to_numpy2d(py, &r.q2_aligned))?;
    dict.set_item("rotation", fdmatrix_to_numpy2d(py, &r.rotation))?;
    dict.set_item("gamma", vec_to_numpy1d(py, r.gamma))?;
    dict.set_item("seed", r.seed)?;
    dict.set_item("length1", r.length1)?;
    dict.set_item("length2", r.length2)?;
    dict.set_item("distance", r.distance)?;
    Ok(dict)
}

fn karcher_dict<'py>(py: Python<'py>, r: &CurveShapeKarcherResult) -> PyResult<Bound<'py, PyDict>> {
    let dict = PyDict::new(py);
    dict.set_item("mean", fdmatrix_to_numpy2d(py, &r.mean))?;
    dict.set_item("mean_srvf", fdmatrix_to_numpy2d(py, &r.mean_srvf))?;
    dict.set_item("aligned_curves", curveset_to_numpy3d(py, &r.aligned_curves))?;
    dict.set_item("aligned_srvfs", curveset_to_numpy3d(py, &r.aligned_srvfs))?;
    dict.set_item("rotations", stack_fdmatrices(py, &r.rotations))?;
    dict.set_item("gammas", fdmatrix_to_numpy2d(py, &r.gammas))?;
    dict.set_item("seeds", usize_vec_to_numpy1d(py, r.seeds.clone()))?;
    dict.set_item(
        "shooting_vectors",
        fdmatrix_to_numpy2d(py, &r.shooting_vectors),
    )?;
    dict.set_item("distances", vec_to_numpy1d(py, r.distances.clone()))?;
    dict.set_item("lengths", vec_to_numpy1d(py, r.lengths.clone()))?;
    dict.set_item("mean_length", r.mean_length)?;
    dict.set_item("energy", vec_to_numpy1d(py, r.energy.clone()))?;
    dict.set_item("n_iter", r.n_iter)?;
    dict.set_item("converged", r.converged)?;
    Ok(dict)
}

/// Karcher dict plus the reusable `"model"` handle.
fn karcher_dict_with_model<'py>(
    py: Python<'py>,
    r: CurveShapeKarcherResult,
) -> PyResult<Bound<'py, PyDict>> {
    let dict = karcher_dict(py, &r)?;
    dict.set_item("model", Py::new(py, PyCurveShapeKarcher { inner: r })?)?;
    Ok(dict)
}

fn pca_dict<'py>(py: Python<'py>, r: &CurveShapePcaResult) -> PyResult<Bound<'py, PyDict>> {
    let dict = PyDict::new(py);
    dict.set_item("scores", fdmatrix_to_numpy2d(py, &r.scores))?;
    dict.set_item("components", stack_fdmatrices(py, &r.components))?;
    dict.set_item("eigenvalues", vec_to_numpy1d(py, r.eigenvalues.clone()))?;
    dict.set_item(
        "cumulative_variance",
        vec_to_numpy1d(py, r.cumulative_variance.clone()),
    )?;
    dict.set_item("mean_tangent", fdmatrix_to_numpy2d(py, &r.mean_tangent))?;
    Ok(dict)
}

fn boxplot_dict<'py>(py: Python<'py>, r: &CurveShapeBoxplot) -> PyResult<Bound<'py, PyDict>> {
    let dict = PyDict::new(py);
    let mats: [(&str, &FdMatrix); 12] = [
        ("median", &r.median),
        ("median_srvf", &r.median_srvf),
        ("q1", &r.q1),
        ("q3", &r.q3),
        ("q1a", &r.q1a),
        ("q3a", &r.q3a),
        ("upper_whisker_srvf", &r.upper_whisker_srvf),
        ("lower_whisker_srvf", &r.lower_whisker_srvf),
        ("upper_whisker", &r.upper_whisker),
        ("lower_whisker", &r.lower_whisker),
        ("minimum", &r.minimum),
        ("maximum", &r.maximum),
    ];
    for (key, mat) in mats {
        dict.set_item(key, fdmatrix_to_numpy2d(py, mat))?;
    }
    dict.set_item("distances", vec_to_numpy1d(py, r.distances.clone()))?;
    dict.set_item("r50", r.r50)?;
    dict.set_item("ralpha", r.ralpha)?;
    dict.set_item("q1_index", r.q1_index)?;
    dict.set_item("q3_index", r.q3_index)?;
    dict.set_item("q1a_index", r.q1a_index)?;
    dict.set_item("q3a_index", r.q3a_index)?;
    dict.set_item("whisker_distance", r.whisker_distance)?;
    dict.set_item(
        "outlier_indices",
        usize_vec_to_numpy1d(py, r.outlier_indices.clone()),
    )?;
    dict.set_item("min_index", r.min_index)?;
    dict.set_item("max_index", r.max_index)?;
    Ok(dict)
}

fn check_curve_vector(v: &[f64], name: &str) -> PyResult<()> {
    if v.iter().any(|x| !x.is_finite()) {
        return Err(PyValueError::new_err(format!(
            "{name} contains non-finite values"
        )));
    }
    Ok(())
}

// ---------------------------------------------------------------------------
// Opaque #[pyclass] handles
// ---------------------------------------------------------------------------

/// Opaque handle wrapping a curve shape Karcher mean / median (CurveShapeKarcherResult).
///
/// Returned as ``"model"`` by `curve_shape_karcher_mean` / `_median` (and as
/// ``"centre_model"`` / ``"mean_model"`` by the outlier and confidence
/// functions). Consumed by `curve_shape_karcher_covariance`, `curve_shape_pca`,
/// `curve_shape_tsrvf`, `curve_shape_tangent_to_curve`, `curve_shape_boxplot`
/// and `PyCurveShapePca.mode_shape`.
#[pyclass(name = "PyCurveShapeKarcher")]
pub struct PyCurveShapeKarcher {
    pub inner: CurveShapeKarcherResult,
}

#[pymethods]
impl PyCurveShapeKarcher {
    /// Mean (or median) shape as a centred curve, shape (d, m).
    #[getter]
    pub fn mean<'py>(&self, py: Python<'py>) -> Bound<'py, PyArray2<f64>> {
        fdmatrix_to_numpy2d(py, &self.inner.mean)
    }

    /// SRVF (F-transform under the elastic metric) of the mean, shape (d, m).
    #[getter]
    pub fn mean_srvf<'py>(&self, py: Python<'py>) -> Bound<'py, PyArray2<f64>> {
        fdmatrix_to_numpy2d(py, &self.inner.mean_srvf)
    }

    /// Shape distance of every curve to the mean, shape (n,).
    #[getter]
    pub fn distances<'py>(&self, py: Python<'py>) -> Bound<'py, PyArray1<f64>> {
        vec_to_numpy1d(py, self.inner.distances.clone())
    }

    /// Whether the Karcher iteration converged.
    #[getter]
    pub fn converged(&self) -> bool {
        self.inner.converged
    }

    /// The full result as a dict (the keys of `curve_shape_karcher_mean`, without ``"model"``).
    pub fn to_dict<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyDict>> {
        karcher_dict(py, &self.inner)
    }
}

/// Opaque handle wrapping a curve shape PCA (CurveShapePcaResult).
///
/// Returned as ``"model"`` by `curve_shape_pca`; `mode_shape` walks along a
/// principal geodesic.
#[pyclass(name = "PyCurveShapePca")]
pub struct PyCurveShapePca {
    pub inner: CurveShapePcaResult,
}

#[pymethods]
impl PyCurveShapePca {
    /// Principal scores, shape (n, ncomp).
    #[getter]
    pub fn scores<'py>(&self, py: Python<'py>) -> Bound<'py, PyArray2<f64>> {
        fdmatrix_to_numpy2d(py, &self.inner.scores)
    }

    /// Eigenvalues of the retained components, shape (ncomp,).
    #[getter]
    pub fn eigenvalues<'py>(&self, py: Python<'py>) -> Bound<'py, PyArray1<f64>> {
        vec_to_numpy1d(py, self.inner.eigenvalues.clone())
    }

    /// Curve on principal geodesic ``component`` at ``coef`` standard deviations from the mean.
    ///
    /// Parameters
    /// ----------
    /// mean : PyCurveShapeKarcher
    ///     The Karcher result the PCA was computed from.
    /// component : int
    ///     Component index (0-based, < ncomp).
    /// coef : float
    ///     Position in standard deviations; 0 gives (approximately) the mean shape.
    ///
    /// Returns
    /// -------
    /// numpy.ndarray
    ///     Centred curve, shape (d, m).
    pub fn mode_shape<'py>(
        &self,
        py: Python<'py>,
        mean: &PyCurveShapeKarcher,
        component: usize,
        coef: f64,
    ) -> PyResult<Bound<'py, PyArray2<f64>>> {
        let beta = to_pyresult(self.inner.mode_shape(&mean.inner, component, coef))?;
        Ok(fdmatrix_to_numpy2d(py, &beta))
    }
}

/// Opaque handle wrapping a sparse-curve elastic mean (SparseElasticMeanResult).
///
/// Returned as ``"model"`` by `sparse_elastic_mean`; evaluates the mean SRV
/// spline and the mean curve at arbitrary parameter values.
#[pyclass(name = "PySparseElasticMean")]
pub struct PySparseElasticMean {
    pub inner: SparseElasticMeanResult,
}

#[pymethods]
impl PySparseElasticMean {
    /// SRV spline coefficients, shape (d, nbasis).
    #[getter]
    pub fn coefs<'py>(&self, py: Python<'py>) -> Bound<'py, PyArray2<f64>> {
        fdmatrix_to_numpy2d(py, &self.inner.coefs)
    }

    /// Knots of the mean SRV spline.
    #[getter]
    pub fn knots<'py>(&self, py: Python<'py>) -> Bound<'py, PyArray1<f64>> {
        vec_to_numpy1d(py, self.inner.knots.clone())
    }

    /// Evaluate the mean SRV at parameter values ``t`` in [0, 1]; shape (d, len(t)).
    pub fn srv_eval<'py>(
        &self,
        py: Python<'py>,
        t: PyReadonlyArray1<'py, f64>,
    ) -> PyResult<Bound<'py, PyArray2<f64>>> {
        let t = numpy1d_to_vec(t);
        check_curve_vector(&t, "t")?;
        Ok(fdmatrix_to_numpy2d(py, &self.inner.srv_eval(&t)))
    }

    /// Evaluate the mean curve at non-decreasing ``t_grid`` in [0, 1]; shape (d, len).
    ///
    /// The curve starts at the origin; with ``centering=True`` (default) the
    /// mean of the evaluated points is subtracted (elasdics ``get_evals``).
    #[pyo3(signature = (t_grid, centering=true))]
    pub fn mean_curve<'py>(
        &self,
        py: Python<'py>,
        t_grid: PyReadonlyArray1<'py, f64>,
        centering: bool,
    ) -> PyResult<Bound<'py, PyArray2<f64>>> {
        let t = numpy1d_to_vec(t_grid);
        let c = to_pyresult(self.inner.mean_curve(&t, centering))?;
        Ok(fdmatrix_to_numpy2d(py, &c))
    }

    /// Closure residual β(1) − β(0) of the mean curve, shape (d,); zero when closed.
    pub fn closure_residual<'py>(&self, py: Python<'py>) -> Bound<'py, PyArray1<f64>> {
        vec_to_numpy1d(py, self.inner.closure_residual())
    }
}

// ---------------------------------------------------------------------------
// Geometry helpers
// ---------------------------------------------------------------------------

/// Square-root velocity function q = β'/√‖β'‖ of an R^d curve on t ∈ [0, 1].
///
/// Parameters
/// ----------
/// beta : numpy.ndarray
///     Curve, shape (d, m) (row = coordinate), m >= 4.
/// scale : bool, optional
///     Rescale q to unit L² norm (default True; fails for a zero-length curve).
///
/// Returns
/// -------
/// numpy.ndarray
///     SRVF, shape (d, m).
#[pyfunction]
#[pyo3(signature = (beta, scale=true))]
pub fn curve_srvf<'py>(
    py: Python<'py>,
    beta: PyReadonlyArray2<'py, f64>,
    scale: bool,
) -> PyResult<Bound<'py, PyArray2<f64>>> {
    let b = numpy2d_to_fdmatrix(beta)?;
    let q = to_pyresult(fdars_core::alignment::curve_srvf(&b, scale))?;
    Ok(fdmatrix_to_numpy2d(py, &q))
}

/// Reconstruct a curve from its SRVF, β(t) = ∫₀ᵗ q‖q‖, starting at the origin.
///
/// Parameters
/// ----------
/// q : numpy.ndarray
///     SRVF, shape (d, m).
///
/// Returns
/// -------
/// numpy.ndarray
///     Curve, shape (d, m), with β(0) = 0.
#[pyfunction]
pub fn srvf_to_curve<'py>(
    py: Python<'py>,
    q: PyReadonlyArray2<'py, f64>,
) -> PyResult<Bound<'py, PyArray2<f64>>> {
    let q = numpy2d_to_fdmatrix(q)?;
    let b = to_pyresult(fdars_core::alignment::srvf_to_curve(&q))?;
    Ok(fdmatrix_to_numpy2d(py, &b))
}

/// Closure residual ∫ q‖q‖ dt of an SRVF: the displacement β(1) − β(0) (zero when closed).
///
/// Parameters
/// ----------
/// q : numpy.ndarray
///     SRVF, shape (d, m).
///
/// Returns
/// -------
/// numpy.ndarray
///     Residual, shape (d,).
#[pyfunction]
pub fn closure_residual<'py>(
    py: Python<'py>,
    q: PyReadonlyArray2<'py, f64>,
) -> PyResult<Bound<'py, PyArray1<f64>>> {
    let q = numpy2d_to_fdmatrix(q)?;
    let r = to_pyresult(fdars_core::alignment::closure_residual(&q))?;
    Ok(vec_to_numpy1d(py, r))
}

/// Project an SRVF onto the closed-curve manifold {q : ∫ q‖q‖ = 0}, preserving its L² norm.
///
/// Parameters
/// ----------
/// q : numpy.ndarray
///     SRVF, shape (d, m), d >= 2.
///
/// Returns
/// -------
/// numpy.ndarray
///     Projected SRVF, shape (d, m); its closure residual is below 1e-10·‖q‖².
///
/// Raises
/// ------
/// ValueError
///     For d < 2 or when the Newton iteration does not converge.
#[pyfunction]
pub fn project_closed_srvf<'py>(
    py: Python<'py>,
    q: PyReadonlyArray2<'py, f64>,
) -> PyResult<Bound<'py, PyArray2<f64>>> {
    let q = numpy2d_to_fdmatrix(q)?;
    let r = to_pyresult(fdars_core::alignment::project_closed_srvf(&q))?;
    Ok(fdmatrix_to_numpy2d(py, &r))
}

/// Kurtek-Needham F-transform of a planar curve for the (a, b) elastic metric.
///
/// F(c) = 2b |c'|^{1/2} (c'/|c'|)^{a/(2b)} (complex power on the continuous
/// tangent-angle lift); ``a=1, b=0.5`` gives the SRVF.
///
/// Parameters
/// ----------
/// beta : numpy.ndarray
///     Planar curve, shape (2, m), m >= 4.
/// a, b : float
///     Bending and stretching weights (finite, > 0).
///
/// Returns
/// -------
/// numpy.ndarray
///     Transform, shape (2, m).
#[pyfunction]
pub fn ab_transform<'py>(
    py: Python<'py>,
    beta: PyReadonlyArray2<'py, f64>,
    a: f64,
    b: f64,
) -> PyResult<Bound<'py, PyArray2<f64>>> {
    let beta = numpy2d_to_fdmatrix(beta)?;
    let f = to_pyresult(fdars_core::alignment::ab_transform(&beta, a, b))?;
    Ok(fdmatrix_to_numpy2d(py, &f))
}

/// Inverse of ``ab_transform``: the planar curve starting at the origin with transform ``f``.
///
/// A left inverse for λ = a/(2b) <= 1 (recovers c − c(0) up to quadrature
/// error); for λ >= 1 it returns one of several curves with transform ``f``.
///
/// Parameters
/// ----------
/// f : numpy.ndarray
///     F-transform, shape (2, m).
/// a, b : float
///     Bending and stretching weights (finite, > 0).
///
/// Returns
/// -------
/// numpy.ndarray
///     Curve, shape (2, m).
#[pyfunction]
pub fn ab_transform_inverse<'py>(
    py: Python<'py>,
    f: PyReadonlyArray2<'py, f64>,
    a: f64,
    b: f64,
) -> PyResult<Bound<'py, PyArray2<f64>>> {
    let f = numpy2d_to_fdmatrix(f)?;
    let c = to_pyresult(fdars_core::alignment::ab_transform_inverse(&f, a, b))?;
    Ok(fdmatrix_to_numpy2d(py, &c))
}

/// Closure residual c(1) − c(0) of the planar curve an (a, b) F-transform represents.
///
/// For ``a=1, b=0.5`` this equals ``closure_residual``.
///
/// Parameters
/// ----------
/// f : numpy.ndarray
///     F-transform, shape (2, m).
/// a, b : float
///     Bending and stretching weights (finite, > 0).
///
/// Returns
/// -------
/// numpy.ndarray
///     Residual, shape (2,).
#[pyfunction]
pub fn ab_closure_residual<'py>(
    py: Python<'py>,
    f: PyReadonlyArray2<'py, f64>,
    a: f64,
    b: f64,
) -> PyResult<Bound<'py, PyArray1<f64>>> {
    let f = numpy2d_to_fdmatrix(f)?;
    let r = to_pyresult(fdars_core::alignment::ab_closure_residual(&f, a, b))?;
    Ok(vec_to_numpy1d(py, r))
}

/// Project a planar (a, b) F-transform onto the closed-curve manifold, preserving its L² norm.
///
/// For λ = a/(2b) = 1 this is ``project_closed_srvf``.
///
/// Parameters
/// ----------
/// f : numpy.ndarray
///     F-transform, shape (2, m).
/// a, b : float
///     Bending and stretching weights (finite, > 0).
///
/// Returns
/// -------
/// numpy.ndarray
///     Projected transform, shape (2, m).
#[pyfunction]
pub fn ab_project_closed<'py>(
    py: Python<'py>,
    f: PyReadonlyArray2<'py, f64>,
    a: f64,
    b: f64,
) -> PyResult<Bound<'py, PyArray2<f64>>> {
    let f = numpy2d_to_fdmatrix(f)?;
    let r = to_pyresult(fdars_core::alignment::ab_project_closed(&f, a, b))?;
    Ok(fdmatrix_to_numpy2d(py, &r))
}

/// Optimal rotation R = argmax ⟨q1, R q2⟩ over SO(d) (or O(d)) by SVD Procrustes.
///
/// Parameters
/// ----------
/// q1, q2 : numpy.ndarray
///     SRVFs (or any vector fields), shape (d, m) each.
/// allow_reflection : bool, optional
///     Optimise over O(d) instead of SO(d) (default False).
///
/// Returns
/// -------
/// numpy.ndarray
///     Rotation, shape (d, d), applied as ``R @ q2``.
#[pyfunction]
#[pyo3(signature = (q1, q2, allow_reflection=false))]
pub fn optimal_rotation<'py>(
    py: Python<'py>,
    q1: PyReadonlyArray2<'py, f64>,
    q2: PyReadonlyArray2<'py, f64>,
    allow_reflection: bool,
) -> PyResult<Bound<'py, PyArray2<f64>>> {
    let q1 = numpy2d_to_fdmatrix(q1)?;
    let q2 = numpy2d_to_fdmatrix(q2)?;
    let r = to_pyresult(fdars_core::alignment::optimal_rotation(
        &q1,
        &q2,
        allow_reflection,
    ))?;
    Ok(fdmatrix_to_numpy2d(py, &r))
}

// ---------------------------------------------------------------------------
// Shape space: pairs, distance matrices, Karcher mean / median, PCA
// ---------------------------------------------------------------------------

/// Align curve ``beta2`` to ``beta1`` in elastic shape space (rotation, scale, seed, warp).
///
/// Parameters
/// ----------
/// beta1, beta2 : numpy.ndarray
///     Curves, shape (d, m) each (same d and m, m >= 4).
/// rotation : bool, optional
///     Quotient out rotations (SVD Procrustes; default True).
/// allow_reflection : bool, optional
///     Optimise rotations over O(d) instead of SO(d) (default False).
/// scale : bool, optional
///     Quotient out scale: unit-length curves, pre-shape sphere geometry
///     (default True).
/// include_length : bool, optional
///     With ``scale=True``, add the log SRVF-norm ratio to the distance
///     (fdasrsf ``elastic_distance_curve(scale=True)``; default False).
/// closed : bool, optional
///     Treat the curves as closed contours (closure projection and seed
///     search; default False).
/// seed_search : bool, optional
///     Search over starting points of closed contours (default True).
/// seed_step : int, optional
///     Coarse seed stride in samples (default 4, >= 1); refined locally.
/// reparam : bool, optional
///     Quotient out reparametrisations by the elastic DP (default True;
///     False gives rigid Procrustes shape analysis).
/// lambda_ : float, optional
///     Warp penalty weight λ ∫(γ' − 1)² (>= 0, default 0.0).
/// align_iter : int, optional
///     Rounds of the Procrustes / DP alternation per seed (default 2, >= 1).
/// metric : str, optional
///     ``"srvf"`` (default, any d) or ``"elastic"`` (general (a, b) metric,
///     planar curves; needs ``a`` and ``b``).
/// a, b : float, optional
///     Bending / stretching weights of ``metric="elastic"`` (a=1, b=0.5 is the SRVF).
/// branch_search : bool, optional
///     With ``metric="elastic"`` and ``rotation=False``, also try the
///     neighbouring F-transform branches (default False).
/// warp_optim : dict, optional
///     Warp optimiser options with the keys of ``elastic_align_pair_with_config``
///     (``method``, ``penalty``, ``optim_max_iter``, ``scl``, ``nbhd_dim``,
///     ``dp_scl``, ``dp_cost``, ``dp_prune``, ``lambda_scale``; ``lambda_`` and
///     ``band_frac`` must stay 0). Default: the classic DP.
///
/// Returns
/// -------
/// dict
///     beta1 (d, m) preprocessed target, beta2_aligned (d, m), q1 (d, m),
///     q2_aligned (d, m), rotation (d, d), gamma (m,), seed, length1, length2,
///     distance.
///
/// Raises
/// ------
/// ValueError
///     For mismatched shapes, an invalid configuration or a zero-length curve.
#[pyfunction]
#[pyo3(signature = (beta1, beta2, rotation=true, allow_reflection=false, scale=true, include_length=false, closed=false, seed_search=true, seed_step=4, reparam=true, lambda_=0.0, align_iter=2, metric="srvf", a=None, b=None, branch_search=false, warp_optim=None))]
pub fn curve_shape_align_pair<'py>(
    py: Python<'py>,
    beta1: PyReadonlyArray2<'py, f64>,
    beta2: PyReadonlyArray2<'py, f64>,
    rotation: bool,
    allow_reflection: bool,
    scale: bool,
    include_length: bool,
    closed: bool,
    seed_search: bool,
    seed_step: usize,
    reparam: bool,
    lambda_: f64,
    align_iter: usize,
    metric: &str,
    a: Option<f64>,
    b: Option<f64>,
    branch_search: bool,
    warp_optim: Option<&Bound<'py, PyDict>>,
) -> PyResult<Bound<'py, PyDict>> {
    let cfg = shape_config(
        rotation,
        allow_reflection,
        scale,
        include_length,
        closed,
        seed_search,
        seed_step,
        reparam,
        lambda_,
        align_iter,
        metric,
        a,
        b,
        branch_search,
        warp_optim,
    )?;
    let b1 = numpy2d_to_fdmatrix(beta1)?;
    let b2 = numpy2d_to_fdmatrix(beta2)?;
    let r = to_pyresult(fdars_core::alignment::curve_shape_align_pair(
        &b1, &b2, &cfg,
    ))?;
    alignment_dict(py, r)
}

/// Elastic shape distance between two R^d curves under the chosen quotient.
///
/// With ``scale=True`` the geodesic distance arccos⟨q1, q2*⟩ on the pre-shape
/// sphere; with ``scale=False`` the L² distance ‖q1 − q2*‖. The shape-quotient
/// keyword arguments are those of ``curve_shape_align_pair``.
///
/// Returns
/// -------
/// float
///     Shape distance.
#[pyfunction]
#[pyo3(signature = (beta1, beta2, rotation=true, allow_reflection=false, scale=true, include_length=false, closed=false, seed_search=true, seed_step=4, reparam=true, lambda_=0.0, align_iter=2, metric="srvf", a=None, b=None, branch_search=false, warp_optim=None))]
pub fn curve_shape_distance<'py>(
    beta1: PyReadonlyArray2<'py, f64>,
    beta2: PyReadonlyArray2<'py, f64>,
    rotation: bool,
    allow_reflection: bool,
    scale: bool,
    include_length: bool,
    closed: bool,
    seed_search: bool,
    seed_step: usize,
    reparam: bool,
    lambda_: f64,
    align_iter: usize,
    metric: &str,
    a: Option<f64>,
    b: Option<f64>,
    branch_search: bool,
    warp_optim: Option<&Bound<'py, PyDict>>,
) -> PyResult<f64> {
    let cfg = shape_config(
        rotation,
        allow_reflection,
        scale,
        include_length,
        closed,
        seed_search,
        seed_step,
        reparam,
        lambda_,
        align_iter,
        metric,
        a,
        b,
        branch_search,
        warp_optim,
    )?;
    let b1 = numpy2d_to_fdmatrix(beta1)?;
    let b2 = numpy2d_to_fdmatrix(beta2)?;
    to_pyresult(fdars_core::alignment::curve_shape_distance(&b1, &b2, &cfg))
}

/// Symmetric matrix of pairwise elastic shape distances between R^d curves.
///
/// Parameters
/// ----------
/// curves : list of numpy.ndarray or numpy.ndarray
///     n curves of shape (d, m): a list or a (n, d, m) array.
///
/// The shape-quotient keyword arguments are those of ``curve_shape_align_pair``.
///
/// Returns
/// -------
/// numpy.ndarray
///     Distances, shape (n, n), zero diagonal.
#[pyfunction]
#[pyo3(signature = (curves, rotation=true, allow_reflection=false, scale=true, include_length=false, closed=false, seed_search=true, seed_step=4, reparam=true, lambda_=0.0, align_iter=2, metric="srvf", a=None, b=None, branch_search=false, warp_optim=None))]
pub fn curve_shape_self_distance_matrix<'py>(
    py: Python<'py>,
    curves: &Bound<'py, PyAny>,
    rotation: bool,
    allow_reflection: bool,
    scale: bool,
    include_length: bool,
    closed: bool,
    seed_search: bool,
    seed_step: usize,
    reparam: bool,
    lambda_: f64,
    align_iter: usize,
    metric: &str,
    a: Option<f64>,
    b: Option<f64>,
    branch_search: bool,
    warp_optim: Option<&Bound<'py, PyDict>>,
) -> PyResult<Bound<'py, PyArray2<f64>>> {
    let cfg = shape_config(
        rotation,
        allow_reflection,
        scale,
        include_length,
        closed,
        seed_search,
        seed_step,
        reparam,
        lambda_,
        align_iter,
        metric,
        a,
        b,
        branch_search,
        warp_optim,
    )?;
    let set = curve_collection_to_set(curves, "curve_shape_self_distance_matrix")?;
    let d = to_pyresult(fdars_core::alignment::curve_shape_self_distance_matrix(
        &set, &cfg,
    ))?;
    Ok(fdmatrix_to_numpy2d(py, &d))
}

/// Karcher (Fréchet) mean shape of R^d curves in elastic shape space.
///
/// Parameters
/// ----------
/// curves : list of numpy.ndarray or numpy.ndarray
///     n curves of shape (d, m): a list or a (n, d, m) array.
/// max_iter : int, optional
///     Maximum Karcher iterations (default 20).
/// tol : float, optional
///     Tolerance on the mean shooting-vector norm (default 1e-3).
///
/// The shape-quotient keyword arguments are those of ``curve_shape_align_pair``.
///
/// Returns
/// -------
/// dict
///     mean (d, m), mean_srvf (d, m), aligned_curves (n, d, m),
///     aligned_srvfs (n, d, m), rotations (n, d, d), gammas (n, m), seeds (n,),
///     shooting_vectors (n, d*m; column k*m + j = coordinate k at sample j),
///     distances (n,), lengths (n,), mean_length, energy, n_iter, converged,
///     model (PyCurveShapeKarcher).
#[pyfunction]
#[pyo3(signature = (curves, max_iter=20, tol=1e-3, rotation=true, allow_reflection=false, scale=true, include_length=false, closed=false, seed_search=true, seed_step=4, reparam=true, lambda_=0.0, align_iter=2, metric="srvf", a=None, b=None, branch_search=false, warp_optim=None))]
pub fn curve_shape_karcher_mean<'py>(
    py: Python<'py>,
    curves: &Bound<'py, PyAny>,
    max_iter: usize,
    tol: f64,
    rotation: bool,
    allow_reflection: bool,
    scale: bool,
    include_length: bool,
    closed: bool,
    seed_search: bool,
    seed_step: usize,
    reparam: bool,
    lambda_: f64,
    align_iter: usize,
    metric: &str,
    a: Option<f64>,
    b: Option<f64>,
    branch_search: bool,
    warp_optim: Option<&Bound<'py, PyDict>>,
) -> PyResult<Bound<'py, PyDict>> {
    let cfg = shape_config(
        rotation,
        allow_reflection,
        scale,
        include_length,
        closed,
        seed_search,
        seed_step,
        reparam,
        lambda_,
        align_iter,
        metric,
        a,
        b,
        branch_search,
        warp_optim,
    )?;
    let set = curve_collection_to_set(curves, "curve_shape_karcher_mean")?;
    let r = to_pyresult(fdars_core::alignment::curve_shape_karcher_mean(
        &set, &cfg, max_iter, tol,
    ))?;
    karcher_dict_with_model(py, r)
}

/// Karcher (geometric) median shape of R^d curves in elastic shape space.
///
/// Minimises Σ d(μ, [βᵢ]) instead of Σ d² (fdasrvf ``ms="median"``); robust to
/// outlying curves. ``energy`` holds Σ dᵢ. Arguments and keys as
/// ``curve_shape_karcher_mean`` (``mean`` holds the median shape).
#[pyfunction]
#[pyo3(signature = (curves, max_iter=20, tol=1e-3, rotation=true, allow_reflection=false, scale=true, include_length=false, closed=false, seed_search=true, seed_step=4, reparam=true, lambda_=0.0, align_iter=2, metric="srvf", a=None, b=None, branch_search=false, warp_optim=None))]
pub fn curve_shape_karcher_median<'py>(
    py: Python<'py>,
    curves: &Bound<'py, PyAny>,
    max_iter: usize,
    tol: f64,
    rotation: bool,
    allow_reflection: bool,
    scale: bool,
    include_length: bool,
    closed: bool,
    seed_search: bool,
    seed_step: usize,
    reparam: bool,
    lambda_: f64,
    align_iter: usize,
    metric: &str,
    a: Option<f64>,
    b: Option<f64>,
    branch_search: bool,
    warp_optim: Option<&Bound<'py, PyDict>>,
) -> PyResult<Bound<'py, PyDict>> {
    let cfg = shape_config(
        rotation,
        allow_reflection,
        scale,
        include_length,
        closed,
        seed_search,
        seed_step,
        reparam,
        lambda_,
        align_iter,
        metric,
        a,
        b,
        branch_search,
        warp_optim,
    )?;
    let set = curve_collection_to_set(curves, "curve_shape_karcher_median")?;
    let r = to_pyresult(fdars_core::alignment::curve_shape_karcher_median(
        &set, &cfg, max_iter, tol,
    ))?;
    karcher_dict_with_model(py, r)
}

/// Sample covariance of the Karcher shooting vectors (tangent space at the mean).
///
/// Parameters
/// ----------
/// model : PyCurveShapeKarcher
///     ``"model"`` of ``curve_shape_karcher_mean`` / ``_median``.
///
/// Returns
/// -------
/// numpy.ndarray
///     Covariance, shape (d*m, d*m), indexed like ``shooting_vectors``.
///
/// Raises
/// ------
/// ValueError
///     If d*m > 10000 (use ``curve_shape_pca`` instead).
#[pyfunction]
pub fn curve_shape_karcher_covariance<'py>(
    py: Python<'py>,
    model: &PyCurveShapeKarcher,
) -> PyResult<Bound<'py, PyArray2<f64>>> {
    let c = to_pyresult(fdars_core::alignment::curve_shape_karcher_covariance(
        &model.inner,
    ))?;
    Ok(fdmatrix_to_numpy2d(py, &c))
}

/// Principal component analysis of curve shapes in the tangent space at the Karcher mean.
///
/// Parameters
/// ----------
/// model : PyCurveShapeKarcher
///     ``"model"`` of ``curve_shape_karcher_mean`` / ``_median``.
/// ncomp : int, optional
///     Number of components (default 3, >= 1; capped at n − 1).
///
/// Returns
/// -------
/// dict
///     scores (n, ncomp), components (ncomp, d, m), eigenvalues (ncomp,),
///     cumulative_variance (ncomp,), mean_tangent (d, m), model (PyCurveShapePca).
#[pyfunction]
#[pyo3(signature = (model, ncomp=3))]
pub fn curve_shape_pca<'py>(
    py: Python<'py>,
    model: &PyCurveShapeKarcher,
    ncomp: usize,
) -> PyResult<Bound<'py, PyDict>> {
    let r = to_pyresult(fdars_core::alignment::curve_shape_pca(&model.inner, ncomp))?;
    let dict = pca_dict(py, &r)?;
    dict.set_item("model", Py::new(py, PyCurveShapePca { inner: r })?)?;
    Ok(dict)
}

// ---------------------------------------------------------------------------
// Downstream: TSRVF, depth, outliers, box plots, confidence regions
// ---------------------------------------------------------------------------

/// TSRVF of R^d curves: align to the Karcher mean and map into its tangent space.
///
/// Applied to the curves the mean was computed from, it reproduces the
/// mean's ``shooting_vectors``; new curves on the same grid are accepted.
///
/// Parameters
/// ----------
/// model : PyCurveShapeKarcher
///     ``"model"`` of ``curve_shape_karcher_mean``.
/// curves : list of numpy.ndarray or numpy.ndarray
///     Curves of shape (d, m) (same d, m as the mean).
///
/// Returns
/// -------
/// dict
///     tangent_vectors (n, d*m), distances (n,), aligned_srvfs (n, d, m),
///     rotations (n, d, d), gammas (n, m), seeds (n,).
#[pyfunction]
pub fn curve_shape_tsrvf<'py>(
    py: Python<'py>,
    model: &PyCurveShapeKarcher,
    curves: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyDict>> {
    let set = curve_collection_to_set(curves, "curve_shape_tsrvf")?;
    let r = to_pyresult(fdars_core::alignment::curve_shape_tsrvf(&model.inner, &set))?;
    let dict = PyDict::new(py);
    dict.set_item(
        "tangent_vectors",
        fdmatrix_to_numpy2d(py, &r.tangent_vectors),
    )?;
    dict.set_item("distances", vec_to_numpy1d(py, r.distances))?;
    dict.set_item("aligned_srvfs", curveset_to_numpy3d(py, &r.aligned_srvfs))?;
    dict.set_item("rotations", stack_fdmatrices(py, &r.rotations))?;
    dict.set_item("gammas", fdmatrix_to_numpy2d(py, &r.gammas))?;
    dict.set_item("seeds", usize_vec_to_numpy1d(py, r.seeds))?;
    Ok(dict)
}

/// Map a tangent vector at the Karcher mean back to a curve (inverse of ``curve_shape_tsrvf``).
///
/// Parameters
/// ----------
/// model : PyCurveShapeKarcher
///     ``"model"`` of ``curve_shape_karcher_mean``.
/// v : numpy.ndarray
///     Tangent vector of length d*m (a row of ``tangent_vectors``).
///
/// Returns
/// -------
/// numpy.ndarray
///     Centred curve, shape (d, m).
#[pyfunction]
pub fn curve_shape_tangent_to_curve<'py>(
    py: Python<'py>,
    model: &PyCurveShapeKarcher,
    v: PyReadonlyArray1<'py, f64>,
) -> PyResult<Bound<'py, PyArray2<f64>>> {
    let v = numpy1d_to_vec(v);
    let c = to_pyresult(fdars_core::alignment::curve_shape_tangent_to_curve(
        &model.inner,
        &v,
    ))?;
    Ok(fdmatrix_to_numpy2d(py, &c))
}

/// Elastic amplitude and phase depth of R^d curves.
///
/// Parameters
/// ----------
/// curves : list of numpy.ndarray or numpy.ndarray
///     n curves of shape (d, m).
///
/// The shape-quotient keyword arguments are those of ``curve_shape_align_pair``.
///
/// Returns
/// -------
/// dict
///     amplitude_depth (n,), phase_depth (n,), amplitude_distances (n, n),
///     phase_distances (n, n).
#[pyfunction]
#[pyo3(signature = (curves, rotation=true, allow_reflection=false, scale=true, include_length=false, closed=false, seed_search=true, seed_step=4, reparam=true, lambda_=0.0, align_iter=2, metric="srvf", a=None, b=None, branch_search=false, warp_optim=None))]
pub fn curve_shape_depth<'py>(
    py: Python<'py>,
    curves: &Bound<'py, PyAny>,
    rotation: bool,
    allow_reflection: bool,
    scale: bool,
    include_length: bool,
    closed: bool,
    seed_search: bool,
    seed_step: usize,
    reparam: bool,
    lambda_: f64,
    align_iter: usize,
    metric: &str,
    a: Option<f64>,
    b: Option<f64>,
    branch_search: bool,
    warp_optim: Option<&Bound<'py, PyDict>>,
) -> PyResult<Bound<'py, PyDict>> {
    let cfg = shape_config(
        rotation,
        allow_reflection,
        scale,
        include_length,
        closed,
        seed_search,
        seed_step,
        reparam,
        lambda_,
        align_iter,
        metric,
        a,
        b,
        branch_search,
        warp_optim,
    )?;
    let set = curve_collection_to_set(curves, "curve_shape_depth")?;
    let r = to_pyresult(fdars_core::alignment::curve_shape_depth(&set, &cfg))?;
    let dict = PyDict::new(py);
    dict.set_item("amplitude_depth", vec_to_numpy1d(py, r.amplitude_depth))?;
    dict.set_item("phase_depth", vec_to_numpy1d(py, r.phase_depth))?;
    dict.set_item(
        "amplitude_distances",
        fdmatrix_to_numpy2d(py, &r.amplitude_distances),
    )?;
    dict.set_item(
        "phase_distances",
        fdmatrix_to_numpy2d(py, &r.phase_distances),
    )?;
    Ok(dict)
}

/// Shape outlier detection for R^d curves by distance to the Karcher median (or mean).
///
/// Parameters
/// ----------
/// curves : list of numpy.ndarray or numpy.ndarray
///     n >= 2 curves of shape (d, m).
/// centre : str, optional
///     ``"median"`` (default, robust) or ``"mean"``.
/// threshold_method : str, optional
///     ``"tukey"`` (fence Q3 + k·IQR, default) or ``"quantile"`` (the
///     (1 − alpha) quantile).
/// tukey_k : float, optional
///     Tukey fence multiplier (default 1.5).
/// alpha : float, optional
///     Tail fraction of the quantile rule (default 0.05).
/// max_iter : int, optional
///     Karcher iterations for the centre (default 20).
/// tol : float, optional
///     Karcher tolerance (default 1e-3).
///
/// The shape-quotient keyword arguments are those of ``curve_shape_align_pair``.
///
/// Returns
/// -------
/// dict
///     outlier_indices (k,), distances (n,), phase_distances (n,), threshold,
///     centre (dict with the keys of ``curve_shape_karcher_mean`` minus model),
///     centre_model (PyCurveShapeKarcher).
#[pyfunction]
#[pyo3(signature = (curves, centre="median", threshold_method="tukey", tukey_k=1.5, alpha=0.05, max_iter=20, tol=1e-3, rotation=true, allow_reflection=false, scale=true, include_length=false, closed=false, seed_search=true, seed_step=4, reparam=true, lambda_=0.0, align_iter=2, metric="srvf", a=None, b=None, branch_search=false, warp_optim=None))]
pub fn curve_shape_outlier_detection<'py>(
    py: Python<'py>,
    curves: &Bound<'py, PyAny>,
    centre: &str,
    threshold_method: &str,
    tukey_k: f64,
    alpha: f64,
    max_iter: usize,
    tol: f64,
    rotation: bool,
    allow_reflection: bool,
    scale: bool,
    include_length: bool,
    closed: bool,
    seed_search: bool,
    seed_step: usize,
    reparam: bool,
    lambda_: f64,
    align_iter: usize,
    metric: &str,
    a: Option<f64>,
    b: Option<f64>,
    branch_search: bool,
    warp_optim: Option<&Bound<'py, PyDict>>,
) -> PyResult<Bound<'py, PyDict>> {
    let mut cfg = CurveShapeOutlierConfig::default();
    cfg.shape = shape_config(
        rotation,
        allow_reflection,
        scale,
        include_length,
        closed,
        seed_search,
        seed_step,
        reparam,
        lambda_,
        align_iter,
        metric,
        a,
        b,
        branch_search,
        warp_optim,
    )?;
    cfg.centre = match centre {
        "median" => CurveShapeCentre::Median,
        "mean" => CurveShapeCentre::Mean,
        _ => {
            return Err(PyValueError::new_err(format!(
                "centre must be one of 'median', 'mean', got '{centre}'"
            )))
        }
    };
    cfg.threshold_method = outlier_threshold(threshold_method, tukey_k)?;
    cfg.alpha = alpha;
    cfg.max_iter = max_iter;
    cfg.tol = tol;
    let set = curve_collection_to_set(curves, "curve_shape_outlier_detection")?;
    let r = to_pyresult(fdars_core::alignment::curve_shape_outlier_detection(
        &set, &cfg,
    ))?;
    let dict = PyDict::new(py);
    dict.set_item(
        "outlier_indices",
        usize_vec_to_numpy1d(py, r.outlier_indices),
    )?;
    dict.set_item("distances", vec_to_numpy1d(py, r.distances))?;
    dict.set_item("phase_distances", vec_to_numpy1d(py, r.phase_distances))?;
    dict.set_item("threshold", r.threshold)?;
    dict.set_item("centre", karcher_dict(py, &r.centre)?)?;
    dict.set_item(
        "centre_model",
        Py::new(py, PyCurveShapeKarcher { inner: r.centre })?,
    )?;
    Ok(dict)
}

/// Elastic shape box plot of the curves summarised by a Karcher median (fdasrvf ``curve_boxplot``).
///
/// Parameters
/// ----------
/// model : PyCurveShapeKarcher
///     ``"model"`` of ``curve_shape_karcher_median`` (a mean is accepted and
///     gives the box plot around the mean).
/// alpha : float, optional
///     The outer central region holds round(n(1 − alpha)) curves (default 0.05).
/// k_a : float, optional
///     Whisker length in units of the IQR (default 1.0).
///
/// Returns
/// -------
/// dict
///     median, median_srvf, q1, q3, q1a, q3a, upper_whisker(_srvf),
///     lower_whisker(_srvf), minimum, maximum (all (d, m)); distances (n,),
///     r50, ralpha, whisker_distance, q1_index, q3_index, q1a_index, q3a_index,
///     min_index, max_index, outlier_indices.
#[pyfunction]
#[pyo3(signature = (model, alpha=0.05, k_a=1.0))]
pub fn curve_shape_boxplot<'py>(
    py: Python<'py>,
    model: &PyCurveShapeKarcher,
    alpha: f64,
    k_a: f64,
) -> PyResult<Bound<'py, PyDict>> {
    let r = to_pyresult(fdars_core::alignment::curve_shape_boxplot(
        &model.inner,
        &boxplot_config(alpha, k_a),
    ))?;
    boxplot_dict(py, &r)
}

/// Elastic shape box plot from SRVFs and curves already aligned to a median.
///
/// Parameters
/// ----------
/// median_srvf : numpy.ndarray
///     SRVF of the median, shape (d, m).
/// aligned_srvfs, aligned_curves : list of numpy.ndarray or numpy.ndarray
///     n aligned SRVFs / curves of shape (d, m).
/// scale : bool, optional
///     Whether scale was quotiented out (sphere geometry; default True).
/// alpha, k_a : float, optional
///     As in ``curve_shape_boxplot``.
///
/// Returns
/// -------
/// dict
///     The keys of ``curve_shape_boxplot``.
#[pyfunction]
#[pyo3(signature = (median_srvf, aligned_srvfs, aligned_curves, scale=true, alpha=0.05, k_a=1.0))]
pub fn curve_shape_boxplot_from_aligned<'py>(
    py: Python<'py>,
    median_srvf: PyReadonlyArray2<'py, f64>,
    aligned_srvfs: &Bound<'py, PyAny>,
    aligned_curves: &Bound<'py, PyAny>,
    scale: bool,
    alpha: f64,
    k_a: f64,
) -> PyResult<Bound<'py, PyDict>> {
    let med = numpy2d_to_fdmatrix(median_srvf)?;
    let qs = curve_collection_to_set(aligned_srvfs, "curve_shape_boxplot_from_aligned")?;
    let bs = curve_collection_to_set(aligned_curves, "curve_shape_boxplot_from_aligned")?;
    let r = to_pyresult(fdars_core::alignment::curve_shape_boxplot_from_aligned(
        &med,
        &qs,
        &bs,
        scale,
        &boxplot_config(alpha, k_a),
    ))?;
    boxplot_dict(py, &r)
}

/// Confidence region of the centre shape of R^d curves (bootstrap or fdasrvf model-based).
///
/// Parameters
/// ----------
/// curves : list of numpy.ndarray or numpy.ndarray
///     n curves of shape (d, m).
/// n_bootstrap : int, optional
///     Bootstrap resamples (default 200; ``method="bootstrap"``).
/// confidence_level : float, optional
///     Level in (0, 1) (default 0.95).
/// max_iter, tol : optional
///     Karcher iterations / tolerance per mean (defaults 15, 1e-3).
/// seed : int, optional
///     Random seed; resample b uses seed + b (default 42).
/// method : str, optional
///     ``"bootstrap"`` (Karcher-mean bootstrap, default) or ``"model_based"``
///     (fdasrvf ``shape_CI``: Gaussian tangent model at the Karcher median).
/// n_components : int, optional
///     Model-based: shape principal directions sampled (default 5).
/// n_samples : int, optional
///     Model-based: number of sampled shapes (default 100, >= 3).
/// n_warp_components : int, optional
///     Model-based: warp principal directions sampled (default 5).
///
/// The shape-quotient keyword arguments are those of ``curve_shape_align_pair``.
///
/// Returns
/// -------
/// dict
///     mean (Karcher dict of the full sample; the median for model_based),
///     mean_model (PyCurveShapeKarcher), bootstrap_means (B, d, m),
///     bootstrap_distances (B,), radius, lower_band (d, m), upper_band (d, m),
///     model (None, or for model_based a dict: q1a, q3a, boxplot, pca, scores,
///     shape_samples, shape_samples_srvf, samples, samples_srvf, warps, rotations).
#[pyfunction]
#[pyo3(signature = (curves, n_bootstrap=200, confidence_level=0.95, max_iter=15, tol=1e-3, seed=42, method="bootstrap", n_components=5, n_samples=100, n_warp_components=5, rotation=true, allow_reflection=false, scale=true, include_length=false, closed=false, seed_search=true, seed_step=4, reparam=true, lambda_=0.0, align_iter=2, metric="srvf", a=None, b=None, branch_search=false, warp_optim=None))]
pub fn curve_shape_confidence_interval<'py>(
    py: Python<'py>,
    curves: &Bound<'py, PyAny>,
    n_bootstrap: usize,
    confidence_level: f64,
    max_iter: usize,
    tol: f64,
    seed: u64,
    method: &str,
    n_components: usize,
    n_samples: usize,
    n_warp_components: usize,
    rotation: bool,
    allow_reflection: bool,
    scale: bool,
    include_length: bool,
    closed: bool,
    seed_search: bool,
    seed_step: usize,
    reparam: bool,
    lambda_: f64,
    align_iter: usize,
    metric: &str,
    a: Option<f64>,
    b: Option<f64>,
    branch_search: bool,
    warp_optim: Option<&Bound<'py, PyDict>>,
) -> PyResult<Bound<'py, PyDict>> {
    let shape = shape_config(
        rotation,
        allow_reflection,
        scale,
        include_length,
        closed,
        seed_search,
        seed_step,
        reparam,
        lambda_,
        align_iter,
        metric,
        a,
        b,
        branch_search,
        warp_optim,
    )?;
    let mut ci = CurveShapeCiConfig::default();
    ci.n_bootstrap = n_bootstrap;
    ci.confidence_level = confidence_level;
    ci.max_iter = max_iter;
    ci.tol = tol;
    ci.seed = seed;
    ci.method = match method {
        "bootstrap" => CurveShapeCiMethod::Bootstrap,
        "model_based" => CurveShapeCiMethod::ModelBased,
        _ => {
            return Err(PyValueError::new_err(format!(
                "method must be one of 'bootstrap', 'model_based', got '{method}'"
            )))
        }
    };
    ci.n_components = n_components;
    ci.n_samples = n_samples;
    ci.n_warp_components = n_warp_components;
    let set = curve_collection_to_set(curves, "curve_shape_confidence_interval")?;
    let r = to_pyresult(fdars_core::alignment::curve_shape_confidence_interval(
        &set, &shape, &ci,
    ))?;
    let dict = PyDict::new(py);
    dict.set_item("mean", karcher_dict(py, &r.mean)?)?;
    dict.set_item("bootstrap_means", stack_fdmatrices(py, &r.bootstrap_means))?;
    dict.set_item(
        "bootstrap_distances",
        vec_to_numpy1d(py, r.bootstrap_distances),
    )?;
    dict.set_item("radius", r.radius)?;
    dict.set_item("lower_band", fdmatrix_to_numpy2d(py, &r.lower_band))?;
    dict.set_item("upper_band", fdmatrix_to_numpy2d(py, &r.upper_band))?;
    match r.model {
        None => dict.set_item("model", py.None())?,
        Some(mc) => {
            let md = PyDict::new(py);
            md.set_item("q1a", fdmatrix_to_numpy2d(py, &mc.q1a))?;
            md.set_item("q3a", fdmatrix_to_numpy2d(py, &mc.q3a))?;
            md.set_item("boxplot", boxplot_dict(py, &mc.boxplot)?)?;
            md.set_item("pca", pca_dict(py, &mc.pca)?)?;
            md.set_item("scores", fdmatrix_to_numpy2d(py, &mc.scores))?;
            md.set_item("shape_samples", curveset_to_numpy3d(py, &mc.shape_samples))?;
            md.set_item(
                "shape_samples_srvf",
                curveset_to_numpy3d(py, &mc.shape_samples_srvf),
            )?;
            md.set_item("samples", curveset_to_numpy3d(py, &mc.samples))?;
            md.set_item("samples_srvf", curveset_to_numpy3d(py, &mc.samples_srvf))?;
            md.set_item("warps", fdmatrix_to_numpy2d(py, &mc.warps))?;
            md.set_item("rotations", stack_fdmatrices(py, &mc.rotations))?;
            dict.set_item("model", md)?;
        }
    }
    dict.set_item(
        "mean_model",
        Py::new(py, PyCurveShapeKarcher { inner: r.mean })?,
    )?;
    Ok(dict)
}

// ---------------------------------------------------------------------------
// Exact piecewise-linear (a, b) distance
// ---------------------------------------------------------------------------

/// Exact (a, b) elastic matching of two piecewise-linear curves (polygons).
///
/// Modulo translation and reparametrisation only (no rotation or scale
/// quotient). Cost O(N1² N2² (N1 + N2)) in the segment counts: meant for
/// polygons with tens of vertices; use ``curve_shape_distance`` for densely
/// sampled curves.
///
/// Parameters
/// ----------
/// c1, c2 : numpy.ndarray
///     Polygon vertices, shapes (d, m1) and (d, m2), m_i >= 2.
/// a, b : float
///     Bending and stretching weights (finite, > 0).
///
/// Returns
/// -------
/// dict
///     distance = 2b·√(L1 + L2 − 2S), similarity S, length1, length2,
///     path (K, 2): monotone polyline from (0, 0) to (1, 1) in normalised arc
///     length.
#[pyfunction]
pub fn ab_elastic_match_pl<'py>(
    py: Python<'py>,
    c1: PyReadonlyArray2<'py, f64>,
    c2: PyReadonlyArray2<'py, f64>,
    a: f64,
    b: f64,
) -> PyResult<Bound<'py, PyDict>> {
    let c1 = numpy2d_to_fdmatrix(c1)?;
    let c2 = numpy2d_to_fdmatrix(c2)?;
    let r = to_pyresult(fdars_core::alignment::ab_elastic_match_pl(&c1, &c2, a, b))?;
    let path = Array2::from_shape_fn((r.path.len(), 2), |(i, k)| {
        if k == 0 {
            r.path[i].0
        } else {
            r.path[i].1
        }
    });
    let dict = PyDict::new(py);
    dict.set_item("distance", r.distance)?;
    dict.set_item("similarity", r.similarity)?;
    dict.set_item("length1", r.length1)?;
    dict.set_item("length2", r.length2)?;
    dict.set_item("path", PyArray2::from_owned_array(py, path))?;
    Ok(dict)
}

/// Exact (a, b) elastic distance between two piecewise-linear curves.
///
/// The ``distance`` of ``ab_elastic_match_pl``.
///
/// Returns
/// -------
/// float
///     Elastic distance modulo translation and reparametrisation.
#[pyfunction]
pub fn ab_elastic_distance_pl(
    c1: PyReadonlyArray2<'_, f64>,
    c2: PyReadonlyArray2<'_, f64>,
    a: f64,
    b: f64,
) -> PyResult<f64> {
    let c1 = numpy2d_to_fdmatrix(c1)?;
    let c2 = numpy2d_to_fdmatrix(c2)?;
    to_pyresult(fdars_core::alignment::ab_elastic_distance_pl(
        &c1, &c2, a, b,
    ))
}

// ---------------------------------------------------------------------------
// Sparse / irregular elastic curves
// ---------------------------------------------------------------------------

fn sparse_curve(points: FdMatrix, param: Option<Vec<f64>>) -> SparseCurve {
    match param {
        Some(p) => SparseCurve::with_param(points, p),
        None => SparseCurve::new(points),
    }
}

/// Elastic alignment of two sparsely observed curves treated as polygons (elasdics ``align_curves``).
///
/// Parameters
/// ----------
/// points1, points2 : numpy.ndarray
///     Observed points, shapes (d, m1) and (d, m2) (m may differ, same d >= 1).
/// param1, param2 : numpy.ndarray, optional
///     Parametrisations of the points (lengths m1, m2); default arc length.
/// closed : bool, optional
///     Treat both curves as closed (default False).
/// eps : float, optional
///     Convergence tolerance of the coordinate-wise warp sweeps (default 0.01).
///
/// Returns
/// -------
/// dict
///     template_points (d, m1'), template_param (m1',), points (d, m2'),
///     param (m2',), param_optim (m2',), distance, closed, removed_duplicates.
#[pyfunction]
#[pyo3(signature = (points1, points2, param1=None, param2=None, closed=false, eps=0.01))]
pub fn sparse_elastic_align_pair<'py>(
    py: Python<'py>,
    points1: PyReadonlyArray2<'py, f64>,
    points2: PyReadonlyArray2<'py, f64>,
    param1: Option<PyReadonlyArray1<'py, f64>>,
    param2: Option<PyReadonlyArray1<'py, f64>>,
    closed: bool,
    eps: f64,
) -> PyResult<Bound<'py, PyDict>> {
    let c1 = sparse_curve(numpy2d_to_fdmatrix(points1)?, param1.map(numpy1d_to_vec));
    let c2 = sparse_curve(numpy2d_to_fdmatrix(points2)?, param2.map(numpy1d_to_vec));
    let mut cfg = SparseAlignConfig::default();
    cfg.closed = closed;
    cfg.eps = eps;
    let r = to_pyresult(fdars_core::alignment::sparse_elastic_align_pair(
        &c1, &c2, &cfg,
    ))?;
    let dict = PyDict::new(py);
    dict.set_item(
        "template_points",
        fdmatrix_to_numpy2d(py, &r.template_points),
    )?;
    dict.set_item("template_param", vec_to_numpy1d(py, r.template_param))?;
    dict.set_item("points", fdmatrix_to_numpy2d(py, &r.points))?;
    dict.set_item("param", vec_to_numpy1d(py, r.param))?;
    dict.set_item("param_optim", vec_to_numpy1d(py, r.param_optim))?;
    dict.set_item("distance", r.distance)?;
    dict.set_item("closed", r.closed)?;
    dict.set_item("removed_duplicates", r.removed_duplicates)?;
    Ok(dict)
}

/// Elastic (Fréchet) mean of sparsely observed curves with a spline SRV (elasdics ``compute_elastic_mean``).
///
/// Parameters
/// ----------
/// curves : list of numpy.ndarray
///     Observed points of every curve, shapes (d, m_i) (ragged m_i, same d).
/// params : list of (numpy.ndarray or None), optional
///     Per-curve parametrisations (length m_i); None or a None entry means
///     arc length.
/// knots : numpy.ndarray, optional
///     Strictly increasing spline knots from 0 to 1 (default [0, .25, .5, .75, 1];
///     closed means need >= 3).
/// mean_type : str, optional
///     ``"smooth"`` (linear SRV spline, default) or ``"polygon"`` (constant SRV
///     spline, polygonal mean).
/// eps : float, optional
///     Relative coefficient-change stopping tolerance (default 0.01).
/// max_iter : int, optional
///     Maximum fit/align iterations (default 50).
/// closed : bool, optional
///     Closed-curve mean (default False).
/// pen_factor : float, optional
///     Closed means: closedness penalty factor (default 100.0).
/// closure_steps : int, optional
///     Closed means: final closure steps (default 1, elasdics; more drive the
///     closure residual to round-off).
///
/// Returns
/// -------
/// dict
///     mean_type, knots, coefs (d, nbasis), curves (list of (d, m_i)),
///     params (list), params_optim (list), distances (n,), n_iter, converged,
///     closed, start_indices (n,), model (PySparseElasticMean).
#[pyfunction]
#[pyo3(signature = (curves, params=None, knots=None, mean_type="smooth", eps=0.01, max_iter=50, closed=false, pen_factor=100.0, closure_steps=1))]
pub fn sparse_elastic_mean<'py>(
    py: Python<'py>,
    curves: &Bound<'py, PyList>,
    params: Option<&Bound<'py, PyList>>,
    knots: Option<PyReadonlyArray1<'py, f64>>,
    mean_type: &str,
    eps: f64,
    max_iter: usize,
    closed: bool,
    pen_factor: f64,
    closure_steps: usize,
) -> PyResult<Bound<'py, PyDict>> {
    let points = list_to_fdmatrices(curves, "sparse_elastic_mean")?;
    let params: Vec<Option<Vec<f64>>> = match params {
        None => vec![None; points.len()],
        Some(list) => {
            if list.len() != points.len() {
                return Err(PyValueError::new_err(format!(
                    "sparse_elastic_mean: params has {} entries for {} curves",
                    list.len(),
                    points.len()
                )));
            }
            list.iter()
                .enumerate()
                .map(|(i, item)| {
                    if item.is_none() {
                        return Ok(None);
                    }
                    item.extract::<PyReadonlyArray1<f64>>()
                        .map(|a| Some(a.as_array().to_vec()))
                        .map_err(|_| {
                            PyValueError::new_err(format!(
                                "sparse_elastic_mean: params[{i}] must be None or a 1-D float64 array"
                            ))
                        })
                })
                .collect::<PyResult<_>>()?
        }
    };
    let sparse: Vec<SparseCurve> = points
        .into_iter()
        .zip(params)
        .map(|(p, t)| sparse_curve(p, t))
        .collect();
    let mut cfg = SparseElasticMeanConfig::default();
    if let Some(k) = knots {
        cfg.knots = numpy1d_to_vec(k);
    }
    cfg.mean_type = match mean_type {
        "smooth" => SparseMeanType::Smooth,
        "polygon" => SparseMeanType::Polygon,
        _ => {
            return Err(PyValueError::new_err(format!(
                "mean_type must be one of 'smooth', 'polygon', got '{mean_type}'"
            )))
        }
    };
    cfg.eps = eps;
    cfg.max_iter = max_iter;
    cfg.closed = closed;
    cfg.pen_factor = pen_factor;
    cfg.closure_steps = closure_steps;
    let r = to_pyresult(fdars_core::alignment::sparse_elastic_mean(&sparse, &cfg))?;
    let dict = PyDict::new(py);
    dict.set_item("mean_type", mean_type)?;
    dict.set_item("knots", vec_to_numpy1d(py, r.knots.clone()))?;
    dict.set_item("coefs", fdmatrix_to_numpy2d(py, &r.coefs))?;
    dict.set_item("curves", fdmatrices_to_pylist(py, &r.curves)?)?;
    let vec_list = |vs: &[Vec<f64>]| -> PyResult<Bound<'py, PyList>> {
        let list = PyList::empty(py);
        for v in vs {
            list.append(vec_to_numpy1d(py, v.clone()))?;
        }
        Ok(list)
    };
    dict.set_item("params", vec_list(&r.params)?)?;
    dict.set_item("params_optim", vec_list(&r.params_optim)?)?;
    dict.set_item("distances", vec_to_numpy1d(py, r.distances.clone()))?;
    dict.set_item("n_iter", r.n_iter)?;
    dict.set_item("converged", r.converged)?;
    dict.set_item("closed", r.closed)?;
    dict.set_item(
        "start_indices",
        usize_vec_to_numpy1d(py, r.start_indices.clone()),
    )?;
    dict.set_item("model", Py::new(py, PySparseElasticMean { inner: r })?)?;
    Ok(dict)
}

/// Convert 1-D irregular functional data into sparse curves for the sparse elastic functions.
///
/// Observation i becomes the (1, m_i) curve of its values, parametrised by
/// its own observed interval mapped to [0, 1].
///
/// Parameters
/// ----------
/// data : PyIrregFdata
///     Handle from ``fdars.pace_fpca.irreg_fdata_from_lists``.
///
/// Returns
/// -------
/// list of dict
///     One ``{"points": (1, m_i), "param": (m_i,) or None}`` per observation.
#[pyfunction]
pub fn sparse_curves_from_irreg<'py>(
    py: Python<'py>,
    data: &PyIrregFdata,
) -> PyResult<Bound<'py, PyList>> {
    let curves = to_pyresult(fdars_core::alignment::sparse_curves_from_irreg(&data.inner))?;
    let list = PyList::empty(py);
    for c in curves {
        let d = PyDict::new(py);
        d.set_item("points", fdmatrix_to_numpy2d(py, &c.points))?;
        match c.param {
            Some(p) => d.set_item("param", vec_to_numpy1d(py, p))?,
            None => d.set_item("param", py.None())?,
        }
        list.append(d)?;
    }
    Ok(list)
}

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyCurveShapeKarcher>()?;
    m.add_class::<PyCurveShapePca>()?;
    m.add_class::<PySparseElasticMean>()?;
    m.add_function(wrap_pyfunction!(curve_srvf, m)?)?;
    m.add_function(wrap_pyfunction!(srvf_to_curve, m)?)?;
    m.add_function(wrap_pyfunction!(closure_residual, m)?)?;
    m.add_function(wrap_pyfunction!(project_closed_srvf, m)?)?;
    m.add_function(wrap_pyfunction!(ab_transform, m)?)?;
    m.add_function(wrap_pyfunction!(ab_transform_inverse, m)?)?;
    m.add_function(wrap_pyfunction!(ab_closure_residual, m)?)?;
    m.add_function(wrap_pyfunction!(ab_project_closed, m)?)?;
    m.add_function(wrap_pyfunction!(optimal_rotation, m)?)?;
    m.add_function(wrap_pyfunction!(curve_shape_align_pair, m)?)?;
    m.add_function(wrap_pyfunction!(curve_shape_distance, m)?)?;
    m.add_function(wrap_pyfunction!(curve_shape_self_distance_matrix, m)?)?;
    m.add_function(wrap_pyfunction!(curve_shape_karcher_mean, m)?)?;
    m.add_function(wrap_pyfunction!(curve_shape_karcher_median, m)?)?;
    m.add_function(wrap_pyfunction!(curve_shape_karcher_covariance, m)?)?;
    m.add_function(wrap_pyfunction!(curve_shape_pca, m)?)?;
    m.add_function(wrap_pyfunction!(curve_shape_tsrvf, m)?)?;
    m.add_function(wrap_pyfunction!(curve_shape_tangent_to_curve, m)?)?;
    m.add_function(wrap_pyfunction!(curve_shape_depth, m)?)?;
    m.add_function(wrap_pyfunction!(curve_shape_outlier_detection, m)?)?;
    m.add_function(wrap_pyfunction!(curve_shape_boxplot, m)?)?;
    m.add_function(wrap_pyfunction!(curve_shape_boxplot_from_aligned, m)?)?;
    m.add_function(wrap_pyfunction!(curve_shape_confidence_interval, m)?)?;
    m.add_function(wrap_pyfunction!(ab_elastic_match_pl, m)?)?;
    m.add_function(wrap_pyfunction!(ab_elastic_distance_pl, m)?)?;
    m.add_function(wrap_pyfunction!(sparse_elastic_align_pair, m)?)?;
    m.add_function(wrap_pyfunction!(sparse_elastic_mean, m)?)?;
    m.add_function(wrap_pyfunction!(sparse_curves_from_irreg, m)?)?;
    Ok(())
}
