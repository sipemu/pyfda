//! Elastic uncertainty quantification and exponential-family registration of
//! fdars-core 0.48: elastic amplitude / phase box plots, elastic DP-means,
//! the amplitude / phase PERMANOVA test, Bayesian group alignment (pCN and
//! infHMC, parallel tempering, convergence diagnostics) and registr-style
//! registration of exponential-family curves with generalized FPCA.
//!
//! Registered into the existing `fdars.alignment` submodule by
//! `alignment_mod::register`; it is not a submodule of its own.

use crate::convert::*;
use crate::inference_mod::permanova_dict;
use crate::pace_fpca_mod::PyIrregFdata;
use fdars_core::alignment::{
    AmplitudeBoxplot, AmplitudeMetric, BayesianGroupConfig, BayesianGroupResult, BayesianSampler,
    BoxplotClassification, BoxplotRegion, BoxplotSide, CurveIncompleteness, DpMeansConfig,
    ElasticBoxplotConfig, ElasticBoxplots, ElasticPhaseBoxplot, ExpFamRegistration, ExpFamily,
    FpcaType, GfpcaConfig, GfpcaResult, NpcCriterion, PhaseAmplitudeTestConfig, RegisterFpcaConfig,
    RegisterFpcaResult, WarpingType,
};
use fdars_core::irreg_fdata::IrregFdata;
use numpy::{AllowTypeChange, PyArray1, PyArrayLike1, PyReadonlyArray1, PyReadonlyArray2};
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

fn boxplot_config(alpha: f64, k_a: f64) -> ElasticBoxplotConfig {
    let mut c = ElasticBoxplotConfig::default();
    c.alpha = alpha;
    c.k_a = k_a;
    c
}

fn region_levels<'py>(py: Python<'py>, regions: &[BoxplotRegion]) -> Bound<'py, PyArray1<i8>> {
    let v: Vec<i8> = regions.iter().map(|r| r.level() as i8).collect();
    PyArray1::from_vec(py, v)
}

fn side_names(sides: &[BoxplotSide]) -> Vec<&'static str> {
    sides
        .iter()
        .map(|s| match s {
            BoxplotSide::Q1 => "q1",
            _ => "q3",
        })
        .collect()
}

fn classification_dict<'py>(
    py: Python<'py>,
    c: &BoxplotClassification,
) -> PyResult<Bound<'py, PyDict>> {
    let d = PyDict::new(py);
    d.set_item("distances", vec_to_numpy1d(py, c.distances.clone()))?;
    d.set_item("regions", region_levels(py, &c.regions))?;
    d.set_item("sides", side_names(&c.sides))?;
    Ok(d)
}

fn amplitude_boxplot_dict<'py>(
    py: Python<'py>,
    b: &AmplitudeBoxplot,
) -> PyResult<Bound<'py, PyDict>> {
    let d = PyDict::new(py);
    for (k, v) in [
        ("median", &b.median),
        ("median_srsf", &b.median_srsf),
        ("q1", &b.q1),
        ("q3", &b.q3),
        ("q1a", &b.q1a),
        ("q3a", &b.q3a),
        ("min_extreme", &b.min_extreme),
        ("max_extreme", &b.max_extreme),
        ("q1_srsf", &b.q1_srsf),
        ("q3_srsf", &b.q3_srsf),
        ("lower_whisker_srsf", &b.lower_whisker_srsf),
        ("upper_whisker_srsf", &b.upper_whisker_srsf),
        ("distances", &b.distances),
    ] {
        d.set_item(k, vec_to_numpy1d(py, v.clone()))?;
    }
    d.set_item("q1_index", b.q1_index)?;
    d.set_item("q3_index", b.q3_index)?;
    d.set_item("q1a_index", b.q1a_index)?;
    d.set_item("q3a_index", b.q3a_index)?;
    d.set_item("min_index", b.min_index)?;
    d.set_item("max_index", b.max_index)?;
    d.set_item("r50", b.r50)?;
    d.set_item("ralpha", b.ralpha)?;
    d.set_item("whisker_distance", b.whisker_distance)?;
    d.set_item(
        "outlier_indices",
        usize_vec_to_numpy1d(py, b.outlier_indices.clone()),
    )?;
    d.set_item("alpha", b.alpha)?;
    d.set_item("k_a", b.k_a)?;
    Ok(d)
}

fn phase_boxplot_dict<'py>(
    py: Python<'py>,
    b: &ElasticPhaseBoxplot,
) -> PyResult<Bound<'py, PyDict>> {
    let d = PyDict::new(py);
    for (k, v) in [
        ("median", &b.median),
        ("median_psi", &b.median_psi),
        ("q1", &b.q1),
        ("q3", &b.q3),
        ("q1a", &b.q1a),
        ("q3a", &b.q3a),
        ("min_extreme", &b.min_extreme),
        ("max_extreme", &b.max_extreme),
        ("distances", &b.distances),
    ] {
        d.set_item(k, vec_to_numpy1d(py, v.clone()))?;
    }
    d.set_item(
        "shooting_vectors",
        fdmatrix_to_numpy2d(py, &b.shooting_vectors),
    )?;
    d.set_item("q1_index", b.q1_index)?;
    d.set_item("q3_index", b.q3_index)?;
    d.set_item("q1a_index", b.q1a_index)?;
    d.set_item("q3a_index", b.q3a_index)?;
    d.set_item("min_index", b.min_index)?;
    d.set_item("max_index", b.max_index)?;
    d.set_item("r50", b.r50)?;
    d.set_item("ralpha", b.ralpha)?;
    d.set_item("whisker_distance", b.whisker_distance)?;
    d.set_item(
        "outlier_indices",
        usize_vec_to_numpy1d(py, b.outlier_indices.clone()),
    )?;
    d.set_item("alpha", b.alpha)?;
    d.set_item("k_a", b.k_a)?;
    d.set_item("median_iter", b.median_iter)?;
    Ok(d)
}

fn vecs_to_pylist<'py>(py: Python<'py>, rows: &[Vec<f64>]) -> PyResult<Bound<'py, PyList>> {
    let list = PyList::empty(py);
    for r in rows {
        list.append(vec_to_numpy1d(py, r.clone()))?;
    }
    Ok(list)
}

// ---------------------------------------------------------------------------
// Elastic box plots (#[pyclass] handles)
// ---------------------------------------------------------------------------

/// Opaque handle wrapping a fitted elastic amplitude + phase box plot pair (ElasticBoxplots).
///
/// Returned as ``"model"`` by `elastic_boxplots`; ``classify`` aligns new
/// curves to the fitted median and places them in both box plots.
#[pyclass(name = "PyElasticBoxplots")]
pub struct PyElasticBoxplots {
    pub inner: ElasticBoxplots,
}

#[pymethods]
impl PyElasticBoxplots {
    /// SRSF of the Karcher median template, length m.
    #[getter]
    pub fn template_srsf<'py>(&self, py: Python<'py>) -> Bound<'py, PyArray1<f64>> {
        vec_to_numpy1d(py, self.inner.template_srsf.clone())
    }

    /// Alignment penalty the box plots were fitted with.
    #[getter]
    pub fn lambda_(&self) -> f64 {
        self.inner.lambda
    }

    /// Classify new curves against the fitted amplitude and phase box plots.
    ///
    /// Each curve is DP-aligned to the fitted median (same ``lambda_``) and
    /// classified by its aligned SRSF (amplitude) and warp (phase).
    ///
    /// Parameters
    /// ----------
    /// new_data : numpy.ndarray
    ///     Curves, shape (k, m), on the fitted grid.
    /// argvals : numpy.ndarray
    ///     Evaluation points, length m.
    ///
    /// Returns
    /// -------
    /// dict
    ///     ``amplitude`` / ``phase`` (each ``{distances, regions, sides}``;
    ///     regions are int8 levels 1 = 50% region, 2 = (1-alpha) region,
    ///     3 = within whiskers, 4 = outlier; sides ``"q1"``/``"q3"``),
    ///     ``aligned_data``, ``aligned_srsfs``, ``gammas`` (k, m).
    pub fn classify<'py>(
        &self,
        py: Python<'py>,
        new_data: PyReadonlyArray2<'py, f64>,
        argvals: PyReadonlyArray1<'py, f64>,
    ) -> PyResult<Bound<'py, PyDict>> {
        let mat = numpy2d_to_fdmatrix(new_data)?;
        let av = numpy1d_to_vec(argvals);
        let c = to_pyresult(self.inner.classify(&mat, &av))?;
        let d = PyDict::new(py);
        d.set_item("amplitude", classification_dict(py, &c.amplitude)?)?;
        d.set_item("phase", classification_dict(py, &c.phase)?)?;
        d.set_item("aligned_data", fdmatrix_to_numpy2d(py, &c.aligned_data))?;
        d.set_item("aligned_srsfs", fdmatrix_to_numpy2d(py, &c.aligned_srsfs))?;
        d.set_item("gammas", fdmatrix_to_numpy2d(py, &c.gammas))?;
        Ok(d)
    }
}

/// Opaque handle wrapping a fitted elastic amplitude box plot (AmplitudeBoxplot).
///
/// Returned as ``"model"`` by `amplitude_boxplot_from_aligned`;
/// ``classify_srsfs`` classifies already-aligned SRSFs.
#[pyclass(name = "PyAmplitudeBoxplot")]
pub struct PyAmplitudeBoxplot {
    pub inner: AmplitudeBoxplot,
}

#[pymethods]
impl PyAmplitudeBoxplot {
    /// Median SRSF, length m.
    #[getter]
    pub fn median_srsf<'py>(&self, py: Python<'py>) -> Bound<'py, PyArray1<f64>> {
        vec_to_numpy1d(py, self.inner.median_srsf.clone())
    }

    /// Classify already-aligned SRSFs by their L2 distance to the median SRSF.
    ///
    /// Parameters
    /// ----------
    /// aligned_srsfs : numpy.ndarray
    ///     SRSFs aligned to the median, shape (k, m).
    /// argvals : numpy.ndarray
    ///     Evaluation points, length m.
    ///
    /// Returns
    /// -------
    /// dict
    ///     ``distances`` (k,), ``regions`` (int8 levels 1-4), ``sides``.
    pub fn classify_srsfs<'py>(
        &self,
        py: Python<'py>,
        aligned_srsfs: PyReadonlyArray2<'py, f64>,
        argvals: PyReadonlyArray1<'py, f64>,
    ) -> PyResult<Bound<'py, PyDict>> {
        let q = numpy2d_to_fdmatrix(aligned_srsfs)?;
        let av = numpy1d_to_vec(argvals);
        let c = to_pyresult(self.inner.classify_srsfs(&q, &av))?;
        classification_dict(py, &c)
    }
}

/// Opaque handle wrapping a fitted elastic phase box plot (ElasticPhaseBoxplot).
///
/// Returned as ``"model"`` by `elastic_phase_boxplot`; ``classify_warps``
/// classifies warping functions on the Hilbert sphere.
#[pyclass(name = "PyElasticPhaseBoxplot")]
pub struct PyElasticPhaseBoxplot {
    pub inner: ElasticPhaseBoxplot,
}

#[pymethods]
impl PyElasticPhaseBoxplot {
    /// Median warp, length m.
    #[getter]
    pub fn median<'py>(&self, py: Python<'py>) -> Bound<'py, PyArray1<f64>> {
        vec_to_numpy1d(py, self.inner.median.clone())
    }

    /// Classify warps by their shooting-vector length from the median warp.
    ///
    /// Parameters
    /// ----------
    /// gammas : numpy.ndarray
    ///     Warping functions, shape (k, m), on the ``argvals`` domain.
    /// argvals : numpy.ndarray
    ///     Evaluation points, length m.
    ///
    /// Returns
    /// -------
    /// dict
    ///     ``distances`` (k,), ``regions`` (int8 levels 1-4), ``sides``.
    pub fn classify_warps<'py>(
        &self,
        py: Python<'py>,
        gammas: PyReadonlyArray2<'py, f64>,
        argvals: PyReadonlyArray1<'py, f64>,
    ) -> PyResult<Bound<'py, PyDict>> {
        let g = numpy2d_to_fdmatrix(gammas)?;
        let av = numpy1d_to_vec(argvals);
        let c = to_pyresult(self.inner.classify_warps(&g, &av))?;
        classification_dict(py, &c)
    }
}

/// Elastic amplitude and phase functional box plots (fdasrsf ``ampbox`` / ``phbox``).
///
/// Aligns the curves to their robust Karcher median, then builds an amplitude
/// box plot from the aligned SRSFs and a phase box plot from the warps on the
/// Hilbert sphere (Xie, Kurtek, Bharath & Sun 2017).
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Curves, shape (n, m).
/// argvals : numpy.ndarray
///     Strictly increasing evaluation points, length m.
/// lambda_ : float, optional
///     Alignment penalty of the Karcher median (default 0.0).
/// alpha : float, optional
///     Quantile level in (0, 1): the outer region holds round(n(1-alpha))
///     curves (default 0.05).
/// k_a : float, optional
///     Whisker scale (> 0): whiskers extend Q1/Q3 by k_a * IQR (default 1.0).
///
/// Returns
/// -------
/// dict
///     ``amplitude`` (dict: median, q1, q3, q1a, q3a, min/max_extreme, SRSF
///     quartiles and whiskers, ``*_index``, distances, r50, ralpha,
///     whisker_distance, outlier_indices, alpha, k_a), ``phase`` (dict: the
///     same for warps plus median_psi, shooting_vectors, median_iter),
///     ``template_srsf``, ``aligned_data``, ``aligned_srsfs``, ``gammas``,
///     ``lambda_`` and ``model`` (``PyElasticBoxplots`` with ``classify``).
#[pyfunction]
#[pyo3(signature = (data, argvals, lambda_=0.0, alpha=0.05, k_a=1.0))]
pub fn elastic_boxplots<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    lambda_: f64,
    alpha: f64,
    k_a: f64,
) -> PyResult<Bound<'py, PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let r = to_pyresult(fdars_core::alignment::elastic_boxplots(
        &mat,
        &av,
        lambda_,
        &boxplot_config(alpha, k_a),
    ))?;
    let d = PyDict::new(py);
    d.set_item("amplitude", amplitude_boxplot_dict(py, &r.amplitude)?)?;
    d.set_item("phase", phase_boxplot_dict(py, &r.phase)?)?;
    d.set_item("template_srsf", vec_to_numpy1d(py, r.template_srsf.clone()))?;
    d.set_item("aligned_data", fdmatrix_to_numpy2d(py, &r.aligned_data))?;
    d.set_item("aligned_srsfs", fdmatrix_to_numpy2d(py, &r.aligned_srsfs))?;
    d.set_item("gammas", fdmatrix_to_numpy2d(py, &r.gammas))?;
    d.set_item("lambda_", r.lambda)?;
    d.set_item("model", Py::new(py, PyElasticBoxplots { inner: r })?)?;
    Ok(d)
}

/// Elastic amplitude box plot from curves already aligned to a median.
///
/// Parameters
/// ----------
/// aligned_data : numpy.ndarray
///     Aligned curves, shape (n, m).
/// aligned_srsfs : numpy.ndarray
///     Their SRSFs, shape (n, m).
/// median, median_srsf : numpy.ndarray
///     Median curve and its SRSF, length m.
/// argvals : numpy.ndarray
///     Strictly increasing evaluation points, length m.
/// alpha : float, optional
///     Quantile level in (0, 1) (default 0.05).
/// k_a : float, optional
///     Whisker scale (> 0, default 1.0).
///
/// Returns
/// -------
/// dict
///     The amplitude box plot fields (see ``elastic_boxplots``) and
///     ``model`` (``PyAmplitudeBoxplot`` with ``classify_srsfs``).
#[pyfunction]
#[pyo3(signature = (aligned_data, aligned_srsfs, median, median_srsf, argvals, alpha=0.05, k_a=1.0))]
pub fn amplitude_boxplot_from_aligned<'py>(
    py: Python<'py>,
    aligned_data: PyReadonlyArray2<'py, f64>,
    aligned_srsfs: PyReadonlyArray2<'py, f64>,
    median: PyReadonlyArray1<'py, f64>,
    median_srsf: PyReadonlyArray1<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    alpha: f64,
    k_a: f64,
) -> PyResult<Bound<'py, PyDict>> {
    let f = numpy2d_to_fdmatrix(aligned_data)?;
    let q = numpy2d_to_fdmatrix(aligned_srsfs)?;
    let med = numpy1d_to_vec(median);
    let med_q = numpy1d_to_vec(median_srsf);
    let av = numpy1d_to_vec(argvals);
    let r = to_pyresult(fdars_core::alignment::amplitude_boxplot_from_aligned(
        &f,
        &q,
        &med,
        &med_q,
        &av,
        &boxplot_config(alpha, k_a),
    ))?;
    let d = amplitude_boxplot_dict(py, &r)?;
    d.set_item("model", Py::new(py, PyAmplitudeBoxplot { inner: r })?)?;
    Ok(d)
}

/// Elastic phase box plot of warping functions on the Hilbert sphere.
///
/// Warps are mapped to square-root slope functions; the median is the
/// spherical median and distances are shooting-vector lengths from it.
///
/// Parameters
/// ----------
/// gammas : numpy.ndarray
///     Warping functions, shape (n, m), on the ``argvals`` domain.
/// argvals : numpy.ndarray
///     Strictly increasing evaluation points, length m.
/// alpha : float, optional
///     Quantile level in (0, 1) (default 0.05).
/// k_a : float, optional
///     Whisker scale (> 0, default 1.0).
///
/// Returns
/// -------
/// dict
///     The phase box plot fields (see ``elastic_boxplots``) and ``model``
///     (``PyElasticPhaseBoxplot`` with ``classify_warps``).
#[pyfunction]
#[pyo3(signature = (gammas, argvals, alpha=0.05, k_a=1.0))]
pub fn elastic_phase_boxplot<'py>(
    py: Python<'py>,
    gammas: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    alpha: f64,
    k_a: f64,
) -> PyResult<Bound<'py, PyDict>> {
    let g = numpy2d_to_fdmatrix(gammas)?;
    let av = numpy1d_to_vec(argvals);
    let r = to_pyresult(fdars_core::alignment::elastic_phase_boxplot(
        &g,
        &av,
        &boxplot_config(alpha, k_a),
    ))?;
    let d = phase_boxplot_dict(py, &r)?;
    d.set_item("model", Py::new(py, PyElasticPhaseBoxplot { inner: r })?)?;
    Ok(d)
}

// ---------------------------------------------------------------------------
// Elastic DP-means
// ---------------------------------------------------------------------------

/// Elastic DP-means clustering: the number of clusters follows from a distance penalty.
///
/// A sequential DP-means sweep in the elastic metric (fdasrsf ``kmeans_align``
/// DP-means variant): a curve farther than ``penalty`` from every template
/// opens a new cluster; templates are re-estimated as centred Karcher means.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Curves, shape (n, m).
/// argvals : numpy.ndarray
///     Strictly increasing evaluation points, length m.
/// penalty : float or None, optional
///     Cluster penalty (an elastic distance). ``None`` (default) uses the
///     fdasrsf k-means++ heuristic (seeded by ``seed``).
/// lambda_ : float, optional
///     Alignment roughness penalty (default 0.0).
/// max_iter : int, optional
///     Maximum passes (default 20).
/// tol : float, optional
///     Relative objective change for convergence (default 0.01).
/// align : bool, optional
///     Align to templates (default True; False = plain DP-means on SRSFs).
/// seed : int, optional
///     Seed of the penalty heuristic (default 42).
///
/// Returns
/// -------
/// dict
///     ``labels`` (n,), ``k``, ``templates`` / ``templates_srsf`` (k, m),
///     ``aligned_data``, ``aligned_srsfs``, ``gammas`` (n, m),
///     ``gamma_inverse`` (k, m), ``objective`` (per pass), ``penalty``,
///     ``n_iter``, ``converged``.
#[pyfunction]
#[pyo3(signature = (data, argvals, penalty=None, lambda_=0.0, max_iter=20, tol=0.01, align=true, seed=42))]
pub fn elastic_dpmeans<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    penalty: Option<f64>,
    lambda_: f64,
    max_iter: usize,
    tol: f64,
    align: bool,
    seed: u64,
) -> PyResult<Bound<'py, PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let mut cfg = DpMeansConfig::default();
    cfg.penalty = penalty;
    cfg.lambda = lambda_;
    cfg.max_iter = max_iter;
    cfg.tol = tol;
    cfg.align = align;
    cfg.seed = seed;
    let r = to_pyresult(fdars_core::alignment::elastic_dpmeans(&mat, &av, &cfg))?;
    let d = PyDict::new(py);
    d.set_item("labels", usize_vec_to_numpy1d(py, r.labels))?;
    d.set_item("k", r.k)?;
    d.set_item("templates", fdmatrix_to_numpy2d(py, &r.templates))?;
    d.set_item("templates_srsf", fdmatrix_to_numpy2d(py, &r.templates_srsf))?;
    d.set_item("aligned_data", fdmatrix_to_numpy2d(py, &r.aligned_data))?;
    d.set_item("aligned_srsfs", fdmatrix_to_numpy2d(py, &r.aligned_srsfs))?;
    d.set_item("gammas", fdmatrix_to_numpy2d(py, &r.gammas))?;
    d.set_item("gamma_inverse", fdmatrix_to_numpy2d(py, &r.gamma_inverse))?;
    d.set_item("objective", vec_to_numpy1d(py, r.objective))?;
    d.set_item("penalty", r.penalty)?;
    d.set_item("n_iter", r.n_iter)?;
    d.set_item("converged", r.converged)?;
    Ok(d)
}

// ---------------------------------------------------------------------------
// Amplitude / phase PERMANOVA
// ---------------------------------------------------------------------------

/// Separate PERMANOVA tests of group differences in amplitude and in phase.
///
/// Curves are aligned label-free to their common Karcher mean; a one-way
/// PERMANOVA (Anderson 2001) is then run on the elastic amplitude distances
/// and on the Fisher-Rao distances of the warps, and optionally on the joint
/// distance d_J^2 = d_A^2 / mean(d_A^2) + d_P^2 / mean(d_P^2). All tests use
/// the same permutations (same ``seed``), so their p-values are coupled.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Curves, shape (n, m), n >= 3.
/// argvals : numpy.ndarray
///     Strictly increasing evaluation points, length m >= 3.
/// labels : numpy.ndarray
///     Non-negative integer group labels, length n (at least 2 groups,
///     more curves than groups).
/// n_perm : int, optional
///     Number of permutations (default 999; 0 skips them, p-values = 1.0).
/// seed : int, optional
///     Permutation seed (default 42).
/// lambda_ : float, optional
///     Alignment penalty (default 0.0).
/// max_iter : int, optional
///     Karcher mean iterations (default 20).
/// tol : float, optional
///     Karcher mean tolerance (default 1e-4).
/// amplitude_metric : str, optional
///     ``"pairwise"`` (pairwise elastic distances, default) or
///     ``"template_aligned"`` (L2 distances of the template-aligned SRSFs).
/// joint : bool, optional
///     Also test the joint amplitude-phase distance (default True).
///
/// Returns
/// -------
/// dict
///     ``amplitude``, ``phase`` and ``joint`` (None if ``joint=False``)
///     PERMANOVA dicts (statistic, p_value, ss_between, ss_within, ss_total,
///     r_squared, df_between, df_within, n_perm), ``amplitude_distances`` /
///     ``phase_distances`` (n, n), ``alignment`` (Karcher mean dict: mean,
///     mean_srsf, gammas, aligned_data, n_iter, converged), ``group_labels``
///     (distinct labels) and ``group_sizes``.
#[pyfunction]
#[pyo3(signature = (data, argvals, labels, n_perm=999, seed=42, lambda_=0.0, max_iter=20, tol=1e-4, amplitude_metric="pairwise", joint=true))]
pub fn elastic_phase_amplitude_test<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    labels: PyArrayLike1<'py, i64, AllowTypeChange>,
    n_perm: usize,
    seed: u64,
    lambda_: f64,
    max_iter: usize,
    tol: f64,
    amplitude_metric: &str,
    joint: bool,
) -> PyResult<Bound<'py, PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let lab = nonneg_labels(&labels, "labels")?;
    let mut cfg = PhaseAmplitudeTestConfig::default();
    cfg.n_perm = n_perm;
    cfg.seed = seed;
    cfg.lambda = lambda_;
    cfg.max_iter = max_iter;
    cfg.tol = tol;
    cfg.amplitude_metric = match amplitude_metric {
        "pairwise" => AmplitudeMetric::Pairwise,
        "template_aligned" => AmplitudeMetric::TemplateAligned,
        _ => {
            return Err(PyValueError::new_err(format!(
            "amplitude_metric must be 'pairwise' or 'template_aligned', got '{amplitude_metric}'"
        )))
        }
    };
    cfg.joint = joint;
    let r = to_pyresult(fdars_core::alignment::elastic_phase_amplitude_test(
        &mat, &av, &lab, &cfg,
    ))?;
    let d = PyDict::new(py);
    d.set_item("amplitude", permanova_dict(py, &r.amplitude)?)?;
    d.set_item("phase", permanova_dict(py, &r.phase)?)?;
    match &r.joint {
        Some(j) => d.set_item("joint", permanova_dict(py, j)?)?,
        None => d.set_item("joint", py.None())?,
    }
    d.set_item(
        "amplitude_distances",
        fdmatrix_to_numpy2d(py, &r.amplitude_distances),
    )?;
    d.set_item(
        "phase_distances",
        fdmatrix_to_numpy2d(py, &r.phase_distances),
    )?;
    let a = PyDict::new(py);
    a.set_item("mean", vec_to_numpy1d(py, r.alignment.mean.clone()))?;
    a.set_item(
        "mean_srsf",
        vec_to_numpy1d(py, r.alignment.mean_srsf.clone()),
    )?;
    a.set_item("gammas", fdmatrix_to_numpy2d(py, &r.alignment.gammas))?;
    a.set_item(
        "aligned_data",
        fdmatrix_to_numpy2d(py, &r.alignment.aligned_data),
    )?;
    a.set_item("n_iter", r.alignment.n_iter)?;
    a.set_item("converged", r.alignment.converged)?;
    d.set_item("alignment", a)?;
    d.set_item("group_labels", usize_vec_to_numpy1d(py, r.group_labels))?;
    d.set_item("group_sizes", usize_vec_to_numpy1d(py, r.group_sizes))?;
    Ok(d)
}

// ---------------------------------------------------------------------------
// Bayesian group alignment
// ---------------------------------------------------------------------------

fn bayesian_result_dict<'py>(
    py: Python<'py>,
    r: BayesianGroupResult,
    return_draws: bool,
) -> PyResult<Bound<'py, PyDict>> {
    let d = PyDict::new(py);
    for (k, v) in [
        ("gammas", &r.gammas),
        ("gammas_median", &r.gammas_median),
        ("gammas_lower", &r.gammas_lower),
        ("gammas_upper", &r.gammas_upper),
        ("aligned_data", &r.aligned_data),
    ] {
        d.set_item(k, fdmatrix_to_numpy2d(py, v))?;
    }
    for (k, v) in [
        ("template_srsf", &r.template_srsf),
        ("template_srsf_lower", &r.template_srsf_lower),
        ("template_srsf_upper", &r.template_srsf_upper),
        ("template", &r.template),
        ("template_lower", &r.template_lower),
        ("template_upper", &r.template_upper),
        ("warp_acceptance", &r.warp_acceptance),
        ("rhat_warps", &r.rhat_warps),
        ("mode_spread", &r.mode_spread),
        ("ess_warps", &r.ess_warps),
        ("warp_bimodality", &r.warp_bimodality),
    ] {
        d.set_item(k, vec_to_numpy1d(py, v.clone()))?;
    }
    d.set_item("sigma2_mean", r.sigma2_mean)?;
    d.set_item("sigma2_lower", r.sigma2_lower)?;
    d.set_item("sigma2_upper", r.sigma2_upper)?;
    d.set_item("template_acceptance", r.template_acceptance)?;
    d.set_item("rhat_sigma2", r.rhat_sigma2)?;
    d.set_item("rhat_log_likelihood", r.rhat_log_likelihood)?;
    d.set_item("ess_sigma2", r.ess_sigma2)?;
    d.set_item("ess_log_likelihood", r.ess_log_likelihood)?;
    d.set_item(
        "multimodal_curves",
        bool_vec_to_numpy1d(py, r.multimodal_curves.clone()),
    )?;
    if return_draws {
        d.set_item("gamma_draws", stack_fdmatrices(py, &r.gamma_draws))?;
        d.set_item(
            "template_srsf_draws",
            fdmatrix_to_numpy2d(py, &r.template_srsf_draws),
        )?;
        d.set_item("sigma2_draws", vec_to_numpy1d(py, r.sigma2_draws.clone()))?;
    } else {
        d.set_item("gamma_draws", py.None())?;
        d.set_item("template_srsf_draws", py.None())?;
        d.set_item("sigma2_draws", py.None())?;
    }
    let chains = PyList::empty(py);
    for c in &r.chains {
        let cd = PyDict::new(py);
        cd.set_item("seed", c.seed)?;
        cd.set_item(
            "posterior_mean_gammas",
            fdmatrix_to_numpy2d(py, &c.posterior_mean_gammas),
        )?;
        cd.set_item("mode_gammas", fdmatrix_to_numpy2d(py, &c.mode_gammas))?;
        cd.set_item("mode_log_likelihood", c.mode_log_likelihood)?;
        for (k, v) in [
            ("mode_template_srsf", &c.mode_template_srsf),
            ("template_srsf_mean", &c.template_srsf_mean),
            ("warp_acceptance", &c.warp_acceptance),
            ("sigma2_trace", &c.sigma2_trace),
            ("log_likelihood_trace", &c.log_likelihood_trace),
            ("warp_step_sizes", &c.warp_step_sizes),
            ("swap_acceptance", &c.swap_acceptance),
        ] {
            cd.set_item(k, vec_to_numpy1d(py, v.clone()))?;
        }
        cd.set_item("template_acceptance", c.template_acceptance)?;
        chains.append(cd)?;
    }
    d.set_item("chains", chains)?;
    Ok(d)
}

/// Bayesian group alignment by MCMC with posterior credible bands for warps and template.
///
/// Samples the joint posterior of a template SRSF (quadratic B-splines), one
/// warp per curve (Fourier shooting vectors on the Hilbert sphere) and the
/// SRSF noise variance (fdasrsf ``time_warping_bayes`` / ``_infHMC``), with
/// several chains, optional parallel tempering and split-R-hat / ESS /
/// bimodality diagnostics.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Curves, shape (n, m), m >= 4.
/// argvals : numpy.ndarray
///     Strictly increasing evaluation points, length m.
/// n_iter, burn_in, thin : int, optional
///     Iterations per chain (default 2000), discarded burn-in
///     (1 <= burn_in < n_iter, default 1000) and thinning (default 1).
/// n_chains : int, optional
///     Independent chains, chain k uses ``seed + k`` (default 1).
/// seed : int, optional
///     Base seed (default 42).
/// alpha0, beta0 : float, optional
///     Inverse-gamma prior of sigma^2 (default 0.1, 0.1).
/// pcn_betas, pcn_probs : sequence of float or None, optional
///     Z-mixture pCN step sizes in (0, 1] and their probabilities. ``None``
///     uses the core defaults (0.5, 0.5, 0.005, 0.0001) and
///     (0.1, 0.1, 0.7, 0.1).
/// warp_prior_sd : float, optional
///     Prior sd of the first warp harmonic (default 4.0).
/// n_warp_harmonics : int, optional
///     Fourier harmonics of the warp shooting vector (default 10).
/// n_template_basis : int, optional
///     B-spline basis size of the template SRSF (>= 3, default 30).
/// n_points : int, optional
///     Internal grid size; 0 uses m (default 0).
/// center_every : int, optional
///     Re-centre warps / template every this many iterations (0 = off,
///     default 100).
/// credible_level : float, optional
///     Level of the pointwise credible bands (default 0.95).
/// center_draws : bool, optional
///     Summarise Karcher-centred draws (default True; False summarises the
///     raw chain states as fdasrsf).
/// init_dp : bool, optional
///     Start from the DP alignment (default True).
/// sampler : str, optional
///     ``"pcn"`` (default) or ``"infhmc"``.
/// hmc_step_size, hmc_max_leapfrog, hmc_adapt, hmc_target_accept : optional
///     infHMC step size in (0, pi/2] (default 0.1), maximum leapfrog steps
///     (default 10), dual-averaging adaptation (default True) and its target
///     acceptance (default 0.65).
/// injective_warps : bool, optional
///     Truncate the warp prior to ||v|| < pi (default False; always on for
///     infHMC).
/// n_temperatures : int, optional
///     Parallel-tempering replicas per chain (default 1 = off).
/// pt_min_inv_temp : float, optional
///     Smallest inverse temperature of the ladder, in (0, 1) (default 0.1).
/// return_draws : bool, optional
///     Include the pooled draws ``gamma_draws`` (n, n_draws, m),
///     ``template_srsf_draws`` (n_draws, m) and ``sigma2_draws`` (default
///     True; False sets them to None to save memory).
///
/// Returns
/// -------
/// dict
///     ``gammas`` (posterior mean), ``gammas_median``, ``gammas_lower``,
///     ``gammas_upper``, ``aligned_data`` (n, m); ``template_srsf`` /
///     ``template`` with ``_lower`` / ``_upper`` bands (m,); ``sigma2_mean``,
///     ``sigma2_lower``, ``sigma2_upper``; ``warp_acceptance`` (n,),
///     ``template_acceptance``; diagnostics ``rhat_sigma2``,
///     ``rhat_log_likelihood``, ``rhat_warps``, ``mode_spread``,
///     ``ess_sigma2``, ``ess_log_likelihood``, ``ess_warps``,
///     ``warp_bimodality``, ``multimodal_curves``; the draws; and ``chains``
///     (list of per-chain dicts incl. ``sigma2_trace``,
///     ``log_likelihood_trace``, ``warp_step_sizes``, ``swap_acceptance``).
#[pyfunction]
#[pyo3(signature = (data, argvals, n_iter=2000, burn_in=1000, thin=1, n_chains=1, seed=42, alpha0=0.1, beta0=0.1, pcn_betas=None, pcn_probs=None, warp_prior_sd=4.0, n_warp_harmonics=10, n_template_basis=30, n_points=0, center_every=100, credible_level=0.95, center_draws=true, init_dp=true, sampler="pcn", hmc_step_size=0.1, hmc_max_leapfrog=10, hmc_adapt=true, hmc_target_accept=0.65, injective_warps=false, n_temperatures=1, pt_min_inv_temp=0.1, return_draws=true))]
pub fn bayesian_align_group<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    n_iter: usize,
    burn_in: usize,
    thin: usize,
    n_chains: usize,
    seed: u64,
    alpha0: f64,
    beta0: f64,
    pcn_betas: Option<Vec<f64>>,
    pcn_probs: Option<Vec<f64>>,
    warp_prior_sd: f64,
    n_warp_harmonics: usize,
    n_template_basis: usize,
    n_points: usize,
    center_every: usize,
    credible_level: f64,
    center_draws: bool,
    init_dp: bool,
    sampler: &str,
    hmc_step_size: f64,
    hmc_max_leapfrog: usize,
    hmc_adapt: bool,
    hmc_target_accept: f64,
    injective_warps: bool,
    n_temperatures: usize,
    pt_min_inv_temp: f64,
    return_draws: bool,
) -> PyResult<Bound<'py, PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let mut cfg = BayesianGroupConfig::default();
    cfg.n_iter = n_iter;
    cfg.burn_in = burn_in;
    cfg.thin = thin;
    cfg.n_chains = n_chains;
    cfg.seed = seed;
    cfg.alpha0 = alpha0;
    cfg.beta0 = beta0;
    if let Some(b) = pcn_betas {
        cfg.pcn_betas = b;
    }
    if let Some(p) = pcn_probs {
        cfg.pcn_probs = p;
    }
    cfg.warp_prior_sd = warp_prior_sd;
    cfg.n_warp_harmonics = n_warp_harmonics;
    cfg.n_template_basis = n_template_basis;
    cfg.n_points = n_points;
    cfg.center_every = center_every;
    cfg.credible_level = credible_level;
    cfg.center_draws = center_draws;
    cfg.init_dp = init_dp;
    cfg.sampler = match sampler {
        "pcn" => BayesianSampler::Pcn,
        "infhmc" => BayesianSampler::InfHmc,
        _ => {
            return Err(PyValueError::new_err(format!(
                "sampler must be 'pcn' or 'infhmc', got '{sampler}'"
            )))
        }
    };
    cfg.hmc_step_size = hmc_step_size;
    cfg.hmc_max_leapfrog = hmc_max_leapfrog;
    cfg.hmc_adapt = hmc_adapt;
    cfg.hmc_target_accept = hmc_target_accept;
    cfg.injective_warps = injective_warps;
    cfg.n_temperatures = n_temperatures;
    cfg.pt_min_inv_temp = pt_min_inv_temp;
    let r = to_pyresult(fdars_core::alignment::bayesian_align_group(&mat, &av, &cfg))?;
    bayesian_result_dict(py, r, return_draws)
}

// ---------------------------------------------------------------------------
// Exponential-family registration + generalized FPCA
// ---------------------------------------------------------------------------

fn exp_family(name: &str) -> PyResult<ExpFamily> {
    match name {
        "gaussian" => Ok(ExpFamily::Gaussian),
        "binomial" => Ok(ExpFamily::Binomial),
        "gamma" => Ok(ExpFamily::Gamma),
        "poisson" => Ok(ExpFamily::Poisson),
        _ => Err(PyValueError::new_err(format!(
            "family must be one of 'gaussian', 'binomial', 'gamma', 'poisson', got '{name}'"
        ))),
    }
}

fn exp_family_name(f: ExpFamily) -> &'static str {
    match f {
        ExpFamily::Gaussian => "gaussian",
        ExpFamily::Binomial => "binomial",
        ExpFamily::Gamma => "gamma",
        ExpFamily::Poisson => "poisson",
        _ => "unknown",
    }
}

fn fpca_type_name(f: FpcaType) -> &'static str {
    match f {
        FpcaType::VariationalEm => "variational_em",
        FpcaType::TwoStep => "two_step",
        _ => "unknown",
    }
}

/// Build a `GfpcaConfig` from the shared ``**GF`` kwargs.
fn gfpca_config(
    npc: usize,
    kt: usize,
    fpca_max_iter: usize,
    error_thresh: f64,
    seed: u64,
    psi_init: Option<PyReadonlyArray2<'_, f64>>,
    xi_init: Option<f64>,
    npc_var_explained: Option<f64>,
    npc_min_component_share: Option<f64>,
    periodic: bool,
    index_significant_digits: Option<u32>,
) -> PyResult<GfpcaConfig> {
    let mut c = GfpcaConfig::default();
    c.npc = npc;
    c.kt = kt;
    c.max_iter = fpca_max_iter;
    c.error_thresh = error_thresh;
    c.seed = seed;
    c.psi_init = psi_init.map(numpy2d_to_fdmatrix).transpose()?;
    c.xi_init = xi_init;
    c.npc_criterion = match (npc_var_explained, npc_min_component_share) {
        (None, None) => None,
        (Some(v), None) => Some(NpcCriterion::new(v)),
        (Some(v), Some(s)) => Some(NpcCriterion::with_min_share(v, s)),
        (None, Some(_)) => {
            return Err(PyValueError::new_err(
                "npc_min_component_share requires npc_var_explained",
            ))
        }
    };
    c.periodic = periodic;
    c.index_significant_digits = index_significant_digits;
    Ok(c)
}

/// Build a `RegisterFpcaConfig` from the registration kwargs and a GFPCA config.
fn register_config(
    family: &str,
    kh: usize,
    incompleteness: Option<&str>,
    lambda_inc: f64,
    max_iterations: usize,
    warp_max_iter: usize,
    warp_tol: f64,
    gamma_scale_init: f64,
    fpca_type: &str,
    warping: &str,
    prior_sd: Option<f64>,
    fpca: GfpcaConfig,
) -> PyResult<RegisterFpcaConfig> {
    let mut c = RegisterFpcaConfig::default();
    c.family = exp_family(family)?;
    c.kh = kh;
    c.incompleteness = match incompleteness {
        None => None,
        Some("leading") => Some(CurveIncompleteness::Leading),
        Some("trailing") => Some(CurveIncompleteness::Trailing),
        Some("full") => Some(CurveIncompleteness::Full),
        Some(other) => {
            return Err(PyValueError::new_err(format!(
                "incompleteness must be None, 'leading', 'trailing' or 'full', got '{other}'"
            )))
        }
    };
    c.lambda_inc = lambda_inc;
    c.max_iterations = max_iterations;
    c.warp_max_iter = warp_max_iter;
    c.warp_tol = warp_tol;
    c.gamma_scale_init = gamma_scale_init;
    c.fpca_type = match fpca_type {
        "variational_em" => FpcaType::VariationalEm,
        "two_step" => FpcaType::TwoStep,
        _ => {
            return Err(PyValueError::new_err(format!(
                "fpca_type must be 'variational_em' or 'two_step', got '{fpca_type}'"
            )))
        }
    };
    c.warping = match warping {
        "nonparametric" => WarpingType::Nonparametric,
        "piecewise_linear2" => WarpingType::PiecewiseLinear2,
        _ => {
            return Err(PyValueError::new_err(format!(
                "warping must be 'nonparametric' or 'piecewise_linear2', got '{warping}'"
            )))
        }
    };
    c.prior_sd = prior_sd;
    c.fpca = fpca;
    Ok(c)
}

fn opt_vec(py: Python<'_>, v: &Option<Vec<f64>>) -> Py<PyAny> {
    match v {
        Some(x) => vec_to_numpy1d(py, x.clone()).into_any().unbind(),
        None => py.None(),
    }
}

fn gfpca_dict<'py>(py: Python<'py>, r: &GfpcaResult) -> PyResult<Bound<'py, PyDict>> {
    let d = PyDict::new(py);
    d.set_item("fpca_type", fpca_type_name(r.fpca_type))?;
    d.set_item("em_family", exp_family_name(r.em_family))?;
    d.set_item("knots", vec_to_numpy1d(py, r.knots.clone()))?;
    d.set_item("domain", (r.domain[0], r.domain[1]))?;
    d.set_item("alpha_coefs", vec_to_numpy1d(py, r.alpha_coefs.clone()))?;
    d.set_item("psi_coefs", fdmatrix_to_numpy2d(py, &r.psi_coefs))?;
    d.set_item("t_vec", vec_to_numpy1d(py, r.t_vec.clone()))?;
    d.set_item("mean", vec_to_numpy1d(py, r.mean.clone()))?;
    d.set_item("efunctions", fdmatrix_to_numpy2d(py, &r.efunctions))?;
    d.set_item("evalues", vec_to_numpy1d(py, r.evalues.clone()))?;
    d.set_item("scores", fdmatrix_to_numpy2d(py, &r.scores))?;
    d.set_item("subject_coefs", fdmatrix_to_numpy2d(py, &r.subject_coefs))?;
    d.set_item("fitted", vecs_to_pylist(py, &r.fitted)?)?;
    d.set_item("sigma2", r.sigma2)?;
    d.set_item("n_iter", r.n_iter)?;
    d.set_item("converged", r.converged)?;
    d.set_item("evalues_sum", r.evalues_sum)?;
    d.set_item("variance_components", opt_vec(py, &r.variance_components))?;
    match &r.yhat {
        Some(y) => d.set_item("yhat", fdmatrix_to_numpy2d(py, y))?,
        None => d.set_item("yhat", py.None())?,
    }
    Ok(d)
}

fn registration_dict<'py>(py: Python<'py>, r: &ExpFamRegistration) -> PyResult<Bound<'py, PyDict>> {
    let d = PyDict::new(py);
    d.set_item("t_hat", vecs_to_pylist(py, &r.t_hat)?)?;
    d.set_item("hinv_beta", vecs_to_pylist(py, &r.hinv_beta)?)?;
    d.set_item("hinv_inner_knots", vecs_to_pylist(py, &r.hinv_inner_knots)?)?;
    d.set_item("curve_loss", vec_to_numpy1d(py, r.curve_loss.clone()))?;
    d.set_item("loss", r.loss)?;
    d.set_item("gamma_scales", opt_vec(py, &r.gamma_scales))?;
    d.set_item(
        "template_knots",
        vec_to_numpy1d(py, r.template_knots.clone()),
    )?;
    d.set_item(
        "template_coefs",
        vec_to_numpy1d(py, r.template_coefs.clone()),
    )?;
    d.set_item("converged", bool_vec_to_numpy1d(py, r.converged.clone()))?;
    Ok(d)
}

/// Add ``registered_data`` (PyIrregFdata), ``registered_argvals`` and
/// ``registered_values`` (lists of arrays) to `d`.
fn add_registered<'py>(
    py: Python<'py>,
    d: &Bound<'py, PyDict>,
    registered: IrregFdata,
) -> PyResult<()> {
    let n = registered.n_obs();
    let av = PyList::empty(py);
    let vals = PyList::empty(py);
    for i in 0..n {
        let (t, y) = registered.get_obs(i);
        av.append(PyArray1::from_slice(py, t))?;
        vals.append(PyArray1::from_slice(py, y))?;
    }
    d.set_item("registered_argvals", av)?;
    d.set_item("registered_values", vals)?;
    d.set_item(
        "registered_data",
        Py::new(py, PyIrregFdata { inner: registered })?,
    )?;
    Ok(())
}

fn register_fpca_dict<'py>(
    py: Python<'py>,
    r: &RegisterFpcaResult,
    data: &IrregFdata,
) -> PyResult<Bound<'py, PyDict>> {
    let d = PyDict::new(py);
    d.set_item("registration", registration_dict(py, &r.registration)?)?;
    d.set_item("fpca", gfpca_dict(py, &r.fpca)?)?;
    d.set_item("converged", r.converged)?;
    d.set_item("iterations", r.iterations)?;
    d.set_item("delta_index", vec_to_numpy1d(py, r.delta_index.clone()))?;
    d.set_item(
        "registration_loss",
        vec_to_numpy1d(py, r.registration_loss.clone()),
    )?;
    add_registered(py, &d, r.registered_data(data))?;
    Ok(d)
}

/// Joint registration and generalized FPCA of exponential-family curves (registr ``register_fpca``).
///
/// Curves (gaussian, binary, gamma or count valued; irregular grids allowed)
/// are modelled as g(E[Y_i(t)]) = theta_i(h_i^{-1}(t)) with a GFPCA template
/// theta_i and monotone B-spline inverse warps h_i^{-1}. Registration and
/// GFPCA (variational EM or two-step) alternate until the warps stabilise
/// (Wrobel, Zipunnikov, Schrack & Goldsmith 2019).
///
/// Parameters
/// ----------
/// data : PyIrregFdata
///     Curves from ``fdars.pace_fpca.irreg_fdata_from_lists``.
/// template : PyIrregFdata or None, optional
///     Curves whose population mean is the initial template (default: the
///     data).
/// family : str, optional
///     ``"gaussian"`` (default), ``"binomial"`` (values in [0, 1]),
///     ``"gamma"`` (> 0) or ``"poisson"`` (>= 0).
/// kh : int, optional
///     Inverse-warp B-spline basis size (>= 4, default 4).
/// incompleteness : str or None, optional
///     ``None`` (complete curves, default), ``"leading"``, ``"trailing"`` or
///     ``"full"``: which warp end(s) may leave the diagonal.
/// lambda_inc : float, optional
///     Endpoint penalty for incomplete curves (default 0.0).
/// max_iterations : int, optional
///     Registration / GFPCA iterations (default 10).
/// warp_max_iter : int, optional
///     L-BFGS iterations per curve and pass (default 500).
/// warp_tol : float, optional
///     Relative loss tolerance of the per-curve optimiser (default 1e-12).
/// gamma_scale_init : float, optional
///     Initial gamma scale (default 1.5).
/// fpca_type : str, optional
///     ``"variational_em"`` (default) or ``"two_step"``.
/// warping : str, optional
///     ``"nonparametric"`` (default) or ``"piecewise_linear2"``.
/// prior_sd : float or None, optional
///     Normal prior sd on the piecewise-linear knots (binomial +
///     piecewise_linear2 only; default None).
/// npc, kt, fpca_max_iter, error_thresh, seed : optional
///     GFPCA components (default 1), spline basis size (default 8), EM
///     iterations (default 50), EM tolerance (default 1e-4), seed of the
///     random start (default 1988).
/// psi_init : numpy.ndarray or None, optional
///     Initial FPC spline coefficients (kt, npc).
/// xi_init : float or None, optional
///     Initial variational parameter for binary data.
/// npc_var_explained, npc_min_component_share : float or None, optional
///     Choose npc by explained-variance share (registr ``npc_criterion``).
/// periodic : bool, optional
///     Periodic B-spline basis (default False).
/// index_significant_digits : int or None, optional
///     Two-step grid rounding digits (default 4; None disables).
///
/// Returns
/// -------
/// dict
///     ``registration`` (t_hat, hinv_beta, hinv_inner_knots: lists of arrays;
///     curve_loss, loss, gamma_scales, template_knots, template_coefs,
///     converged), ``fpca`` (GFPCA dict), ``converged``, ``iterations``,
///     ``delta_index``, ``registration_loss``, ``registered_data``
///     (PyIrregFdata), ``registered_argvals`` and ``registered_values``.
#[pyfunction]
#[pyo3(signature = (data, template=None, family="gaussian", kh=4, incompleteness=None, lambda_inc=0.0, max_iterations=10, warp_max_iter=500, warp_tol=1e-12, gamma_scale_init=1.5, fpca_type="variational_em", warping="nonparametric", prior_sd=None, npc=1, kt=8, fpca_max_iter=50, error_thresh=1e-4, seed=1988, psi_init=None, xi_init=None, npc_var_explained=None, npc_min_component_share=None, periodic=false, index_significant_digits=4))]
pub fn register_fpca<'py>(
    py: Python<'py>,
    data: &PyIrregFdata,
    template: Option<&PyIrregFdata>,
    family: &str,
    kh: usize,
    incompleteness: Option<&str>,
    lambda_inc: f64,
    max_iterations: usize,
    warp_max_iter: usize,
    warp_tol: f64,
    gamma_scale_init: f64,
    fpca_type: &str,
    warping: &str,
    prior_sd: Option<f64>,
    npc: usize,
    kt: usize,
    fpca_max_iter: usize,
    error_thresh: f64,
    seed: u64,
    psi_init: Option<PyReadonlyArray2<'py, f64>>,
    xi_init: Option<f64>,
    npc_var_explained: Option<f64>,
    npc_min_component_share: Option<f64>,
    periodic: bool,
    index_significant_digits: Option<u32>,
) -> PyResult<Bound<'py, PyDict>> {
    let gf = gfpca_config(
        npc,
        kt,
        fpca_max_iter,
        error_thresh,
        seed,
        psi_init,
        xi_init,
        npc_var_explained,
        npc_min_component_share,
        periodic,
        index_significant_digits,
    )?;
    let cfg = register_config(
        family,
        kh,
        incompleteness,
        lambda_inc,
        max_iterations,
        warp_max_iter,
        warp_tol,
        gamma_scale_init,
        fpca_type,
        warping,
        prior_sd,
        gf,
    )?;
    let r = to_pyresult(fdars_core::alignment::register_fpca(
        &data.inner,
        template.map(|t| &t.inner),
        &cfg,
    ))?;
    register_fpca_dict(py, &r, &data.inner)
}

/// Joint registration and generalized FPCA of exponential-family curves on a common grid.
///
/// ``register_fpca`` for an (n, m) matrix whose rows are observed on
/// ``argvals``; same keyword arguments (no ``template``) and output.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Curves, shape (n, m).
/// argvals : numpy.ndarray
///     Evaluation points, length m.
/// **kwargs
///     As ``register_fpca``.
///
/// Returns
/// -------
/// dict
///     As ``register_fpca``.
#[pyfunction]
#[pyo3(signature = (data, argvals, family="gaussian", kh=4, incompleteness=None, lambda_inc=0.0, max_iterations=10, warp_max_iter=500, warp_tol=1e-12, gamma_scale_init=1.5, fpca_type="variational_em", warping="nonparametric", prior_sd=None, npc=1, kt=8, fpca_max_iter=50, error_thresh=1e-4, seed=1988, psi_init=None, xi_init=None, npc_var_explained=None, npc_min_component_share=None, periodic=false, index_significant_digits=4))]
pub fn register_fpca_regular<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    family: &str,
    kh: usize,
    incompleteness: Option<&str>,
    lambda_inc: f64,
    max_iterations: usize,
    warp_max_iter: usize,
    warp_tol: f64,
    gamma_scale_init: f64,
    fpca_type: &str,
    warping: &str,
    prior_sd: Option<f64>,
    npc: usize,
    kt: usize,
    fpca_max_iter: usize,
    error_thresh: f64,
    seed: u64,
    psi_init: Option<PyReadonlyArray2<'py, f64>>,
    xi_init: Option<f64>,
    npc_var_explained: Option<f64>,
    npc_min_component_share: Option<f64>,
    periodic: bool,
    index_significant_digits: Option<u32>,
) -> PyResult<Bound<'py, PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let gf = gfpca_config(
        npc,
        kt,
        fpca_max_iter,
        error_thresh,
        seed,
        psi_init,
        xi_init,
        npc_var_explained,
        npc_min_component_share,
        periodic,
        index_significant_digits,
    )?;
    let cfg = register_config(
        family,
        kh,
        incompleteness,
        lambda_inc,
        max_iterations,
        warp_max_iter,
        warp_tol,
        gamma_scale_init,
        fpca_type,
        warping,
        prior_sd,
        gf,
    )?;
    let r = to_pyresult(fdars_core::alignment::register_fpca_regular(
        &mat, &av, &cfg,
    ))?;
    let n = mat.nrows();
    let t: Vec<Vec<f64>> = (0..n).map(|_| av.clone()).collect();
    let y: Vec<Vec<f64>> = (0..n).map(|i| mat.row(i)).collect();
    register_fpca_dict(py, &r, &IrregFdata::from_lists(&t, &y))
}

/// One exponential-family registration pass of every curve to a population-mean template (registr ``registr``).
///
/// The template is the spline GLM mean of ``template`` (default: the data)
/// on the link scale; each curve's monotone inverse warp maximises its
/// likelihood under it.
///
/// Parameters
/// ----------
/// data : PyIrregFdata
///     Curves from ``fdars.pace_fpca.irreg_fdata_from_lists``.
/// template : PyIrregFdata or None, optional
///     Curves defining the template (default: the data).
/// family, kh, incompleteness, lambda_inc, warp_max_iter, warp_tol, gamma_scale_init, warping, prior_sd : optional
///     As ``register_fpca``.
/// kt : int, optional
///     Template B-spline basis size (>= 4, default 8).
/// periodic : bool, optional
///     Periodic template basis (default False).
///
/// Returns
/// -------
/// dict
///     The registration fields (see ``register_fpca``) plus
///     ``registered_data`` (PyIrregFdata), ``registered_argvals`` and
///     ``registered_values``.
#[pyfunction]
#[pyo3(signature = (data, template=None, family="gaussian", kh=4, incompleteness=None, lambda_inc=0.0, warp_max_iter=500, warp_tol=1e-12, gamma_scale_init=1.5, warping="nonparametric", prior_sd=None, kt=8, periodic=false))]
pub fn register_expfam<'py>(
    py: Python<'py>,
    data: &PyIrregFdata,
    template: Option<&PyIrregFdata>,
    family: &str,
    kh: usize,
    incompleteness: Option<&str>,
    lambda_inc: f64,
    warp_max_iter: usize,
    warp_tol: f64,
    gamma_scale_init: f64,
    warping: &str,
    prior_sd: Option<f64>,
    kt: usize,
    periodic: bool,
) -> PyResult<Bound<'py, PyDict>> {
    let mut gf = GfpcaConfig::default();
    gf.kt = kt;
    gf.periodic = periodic;
    let cfg = register_config(
        family,
        kh,
        incompleteness,
        lambda_inc,
        RegisterFpcaConfig::default().max_iterations,
        warp_max_iter,
        warp_tol,
        gamma_scale_init,
        "variational_em",
        warping,
        prior_sd,
        gf,
    )?;
    let r = to_pyresult(fdars_core::alignment::register_expfam(
        &data.inner,
        template.map(|t| &t.inner),
        &cfg,
    ))?;
    let d = registration_dict(py, &r)?;
    add_registered(py, &d, r.registered_data(&data.inner))?;
    Ok(d)
}

/// Generalized FPCA of exponential-family curves by variational EM (registr ``bfpca`` / ``fpca_gauss``).
///
/// Binary data use the variational EM of ``bfpca``; gaussian, gamma and
/// poisson data use the gaussian EM ``fpca_gauss`` (as registr).
///
/// Parameters
/// ----------
/// data : PyIrregFdata
///     Curves from ``fdars.pace_fpca.irreg_fdata_from_lists``.
/// family : str, optional
///     ``"gaussian"`` (default), ``"binomial"``, ``"gamma"`` or ``"poisson"``.
/// npc, kt, fpca_max_iter, error_thresh, seed, psi_init, xi_init, npc_var_explained, npc_min_component_share, periodic, index_significant_digits : optional
///     As ``register_fpca``.
///
/// Returns
/// -------
/// dict
///     ``fpca_type``, ``em_family``, ``knots``, ``domain`` (tuple),
///     ``alpha_coefs``, ``psi_coefs`` (kt, npc), ``t_vec``, ``mean``,
///     ``efunctions`` (len(t_vec), npc), ``evalues``, ``scores`` (n, npc),
///     ``subject_coefs`` (n, kt), ``fitted`` (list of arrays), ``sigma2``,
///     ``n_iter``, ``converged``, ``evalues_sum``, ``variance_components``,
///     ``yhat``.
#[pyfunction]
#[pyo3(signature = (data, family="gaussian", npc=1, kt=8, fpca_max_iter=50, error_thresh=1e-4, seed=1988, psi_init=None, xi_init=None, npc_var_explained=None, npc_min_component_share=None, periodic=false, index_significant_digits=4))]
pub fn gfpca_variational<'py>(
    py: Python<'py>,
    data: &PyIrregFdata,
    family: &str,
    npc: usize,
    kt: usize,
    fpca_max_iter: usize,
    error_thresh: f64,
    seed: u64,
    psi_init: Option<PyReadonlyArray2<'py, f64>>,
    xi_init: Option<f64>,
    npc_var_explained: Option<f64>,
    npc_min_component_share: Option<f64>,
    periodic: bool,
    index_significant_digits: Option<u32>,
) -> PyResult<Bound<'py, PyDict>> {
    let cfg = gfpca_config(
        npc,
        kt,
        fpca_max_iter,
        error_thresh,
        seed,
        psi_init,
        xi_init,
        npc_var_explained,
        npc_min_component_share,
        periodic,
        index_significant_digits,
    )?;
    let r = to_pyresult(fdars_core::alignment::gfpca_variational(
        &data.inner,
        exp_family(family)?,
        &cfg,
    ))?;
    gfpca_dict(py, &r)
}

/// Two-step generalized FPCA of exponential-family curves (registr ``gfpca_twoStep``).
///
/// Family-specific for all four families: a P-spline mean and covariance
/// smooth on the latent scale, then a GLMM for the scores (Gertheiss,
/// Goldsmith & Staicu 2017).
///
/// Parameters
/// ----------
/// data : PyIrregFdata
///     Curves from ``fdars.pace_fpca.irreg_fdata_from_lists``.
/// family : str, optional
///     ``"gaussian"`` (default), ``"binomial"``, ``"gamma"`` or ``"poisson"``.
/// npc, kt, fpca_max_iter, error_thresh, seed, psi_init, xi_init, npc_var_explained, npc_min_component_share, periodic, index_significant_digits : optional
///     As ``register_fpca``.
///
/// Returns
/// -------
/// dict
///     As ``gfpca_variational`` (``t_vec`` is the sorted unique rounded time
///     grid; ``variance_components`` and ``yhat`` are set).
#[pyfunction]
#[pyo3(signature = (data, family="gaussian", npc=1, kt=8, fpca_max_iter=50, error_thresh=1e-4, seed=1988, psi_init=None, xi_init=None, npc_var_explained=None, npc_min_component_share=None, periodic=false, index_significant_digits=4))]
pub fn gfpca_two_step<'py>(
    py: Python<'py>,
    data: &PyIrregFdata,
    family: &str,
    npc: usize,
    kt: usize,
    fpca_max_iter: usize,
    error_thresh: f64,
    seed: u64,
    psi_init: Option<PyReadonlyArray2<'py, f64>>,
    xi_init: Option<f64>,
    npc_var_explained: Option<f64>,
    npc_min_component_share: Option<f64>,
    periodic: bool,
    index_significant_digits: Option<u32>,
) -> PyResult<Bound<'py, PyDict>> {
    let cfg = gfpca_config(
        npc,
        kt,
        fpca_max_iter,
        error_thresh,
        seed,
        psi_init,
        xi_init,
        npc_var_explained,
        npc_min_component_share,
        periodic,
        index_significant_digits,
    )?;
    let r = to_pyresult(fdars_core::alignment::gfpca_two_step(
        &data.inner,
        exp_family(family)?,
        &cfg,
    ))?;
    gfpca_dict(py, &r)
}

/// Evaluate one curve's registr inverse warp h^{-1}(t) from its B-spline coefficients.
///
/// Parameters
/// ----------
/// beta : numpy.ndarray
///     Coefficients (``registration["hinv_beta"][i]``), length
///     len(inner_knots) + 4.
/// inner_knots : numpy.ndarray
///     Interior knots (``registration["hinv_inner_knots"][i]``).
/// t_lo, t_hi : float
///     The curve's observed range (t_hi > t_lo).
/// t : numpy.ndarray
///     Evaluation points inside [t_lo, t_hi].
///
/// Returns
/// -------
/// numpy.ndarray
///     h^{-1}(t), shape (len(t),).
#[pyfunction]
#[pyo3(signature = (beta, inner_knots, t_lo, t_hi, t))]
pub fn evaluate_inverse_warp<'py>(
    py: Python<'py>,
    beta: PyReadonlyArray1<'py, f64>,
    inner_knots: PyReadonlyArray1<'py, f64>,
    t_lo: f64,
    t_hi: f64,
    t: PyReadonlyArray1<'py, f64>,
) -> PyResult<Bound<'py, PyArray1<f64>>> {
    let b = numpy1d_to_vec(beta);
    let k = numpy1d_to_vec(inner_knots);
    let tv = numpy1d_to_vec(t);
    let r = to_pyresult(fdars_core::alignment::evaluate_inverse_warp(
        &b, &k, t_lo, t_hi, &tv,
    ))?;
    Ok(vec_to_numpy1d(py, r))
}

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyElasticBoxplots>()?;
    m.add_class::<PyAmplitudeBoxplot>()?;
    m.add_class::<PyElasticPhaseBoxplot>()?;
    m.add_function(wrap_pyfunction!(elastic_boxplots, m)?)?;
    m.add_function(wrap_pyfunction!(amplitude_boxplot_from_aligned, m)?)?;
    m.add_function(wrap_pyfunction!(elastic_phase_boxplot, m)?)?;
    m.add_function(wrap_pyfunction!(elastic_dpmeans, m)?)?;
    m.add_function(wrap_pyfunction!(elastic_phase_amplitude_test, m)?)?;
    m.add_function(wrap_pyfunction!(bayesian_align_group, m)?)?;
    m.add_function(wrap_pyfunction!(register_fpca, m)?)?;
    m.add_function(wrap_pyfunction!(register_fpca_regular, m)?)?;
    m.add_function(wrap_pyfunction!(register_expfam, m)?)?;
    m.add_function(wrap_pyfunction!(gfpca_variational, m)?)?;
    m.add_function(wrap_pyfunction!(gfpca_two_step, m)?)?;
    m.add_function(wrap_pyfunction!(evaluate_inverse_warp, m)?)?;
    Ok(())
}
