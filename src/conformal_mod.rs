//! Conformal prediction methods.

use crate::convert::*;
use fdars_core::conformal::{
    PartialAmplitudeBand, PartialBandScale, PartialBandwidthSelection, PartialConformalConfig,
    PartialConformalModel, PartialConformalPrediction, PartialObservation,
    PartialPredictorDistance,
};
use numpy::{
    AllowTypeChange, PyArray1, PyArray2, PyArrayLike1, PyArrayLike2, PyReadonlyArray1,
    PyReadonlyArray2,
};
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};

/// Conformal regression prediction intervals.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Functional predictors (training), shape (n, m).
/// response : numpy.ndarray
///     Scalar response, length n.
/// test_data : numpy.ndarray
///     Test functional predictors, shape (n_test, m).
/// ncomp : int, optional
///     Number of FPC components (default 3).
/// cal_fraction : float, optional
///     Calibration fraction (default 0.25).
/// alpha : float, optional
///     Miscoverage level (default 0.1).
/// seed : int, optional
///     Random seed (default 42).
///
/// Returns
/// -------
/// dict
///     lower (n_test,), upper (n_test,), predictions (n_test,), coverage.
#[pyfunction]
#[pyo3(signature = (data, response, test_data, ncomp=3, cal_fraction=0.25, alpha=0.1, seed=42))]
pub fn conformal_fregre_lm<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    response: PyReadonlyArray1<'py, f64>,
    test_data: PyReadonlyArray2<'py, f64>,
    ncomp: usize,
    cal_fraction: f64,
    alpha: f64,
    seed: u64,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let resp = numpy1d_to_vec(response);
    let tmat = numpy2d_to_fdmatrix(test_data)?;
    let result = to_pyresult(fdars_core::conformal::conformal_fregre_lm(
        &mat,
        &resp,
        &tmat,
        None,
        None,
        ncomp,
        cal_fraction,
        alpha,
        seed,
    ))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("lower", vec_to_numpy1d(py, result.lower))?;
    dict.set_item("upper", vec_to_numpy1d(py, result.upper))?;
    dict.set_item("predictions", vec_to_numpy1d(py, result.predictions))?;
    dict.set_item("coverage", result.coverage)?;
    Ok(dict)
}

/// Conformal nonparametric regression.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Functional predictors (training), shape (n, m).
/// response : numpy.ndarray
///     Scalar response, length n.
/// test_data : numpy.ndarray
///     Test functional predictors, shape (n_test, m).
/// argvals : numpy.ndarray
///     Evaluation points, length m.
/// cal_fraction : float, optional
///     Calibration fraction (default 0.25).
/// alpha : float, optional
///     Miscoverage level (default 0.1).
/// h_func : float, optional
///     Functional bandwidth (default 1.0).
/// h_scalar : float, optional
///     Scalar bandwidth (default 1.0).
/// seed : int, optional
///     Random seed (default 42).
///
/// Returns
/// -------
/// dict
///     lower (n_test,), upper (n_test,), predictions (n_test,), coverage.
#[pyfunction]
#[pyo3(signature = (data, response, test_data, argvals, cal_fraction=0.25, alpha=0.1, h_func=1.0, h_scalar=1.0, seed=42))]
pub fn conformal_fregre_np<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    response: PyReadonlyArray1<'py, f64>,
    test_data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    cal_fraction: f64,
    alpha: f64,
    h_func: f64,
    h_scalar: f64,
    seed: u64,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let resp = numpy1d_to_vec(response);
    let tmat = numpy2d_to_fdmatrix(test_data)?;
    let av = numpy1d_to_vec(argvals);
    let result = to_pyresult(fdars_core::conformal::conformal_fregre_np(
        &mat,
        &resp,
        &tmat,
        &av,
        None,
        None,
        h_func,
        h_scalar,
        cal_fraction,
        alpha,
        seed,
    ))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("lower", vec_to_numpy1d(py, result.lower))?;
    dict.set_item("upper", vec_to_numpy1d(py, result.upper))?;
    dict.set_item("predictions", vec_to_numpy1d(py, result.predictions))?;
    dict.set_item("coverage", result.coverage)?;
    Ok(dict)
}

/// Conformal classification prediction sets.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Functional predictors (training), shape (n, m).
/// labels : numpy.ndarray
///     Class labels, length n.
/// test_data : numpy.ndarray
///     Test functional predictors, shape (n_test, m).
/// ncomp : int, optional
///     Number of FPC components (default 3).
/// classifier : str, optional
///     "lda" (default), "qda", "knn".
/// cal_fraction : float, optional
///     Calibration fraction (default 0.25).
/// alpha : float, optional
///     Miscoverage level (default 0.1).
/// seed : int, optional
///     Random seed (default 42).
///
/// Returns
/// -------
/// dict
///     prediction_sets (list of lists), coverage.
#[pyfunction]
#[pyo3(signature = (data, labels, test_data, ncomp=3, classifier="lda", cal_fraction=0.25, alpha=0.1, seed=42))]
pub fn conformal_classif<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    labels: PyReadonlyArray1<'py, i64>,
    test_data: PyReadonlyArray2<'py, f64>,
    ncomp: usize,
    classifier: &str,
    cal_fraction: f64,
    alpha: f64,
    seed: u64,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let lab = numpy1d_to_usize_vec(labels);
    let tmat = numpy2d_to_fdmatrix(test_data)?;
    let result = to_pyresult(fdars_core::conformal::conformal_classif(
        &mat,
        &lab,
        &tmat,
        None,
        None,
        ncomp,
        classifier,
        5, // k_nn default
        fdars_core::conformal::ClassificationScore::Lac,
        cal_fraction,
        alpha,
        seed,
    ))?;

    let dict = pyo3::types::PyDict::new(py);
    let sets: Vec<Vec<i64>> = result
        .prediction_sets
        .iter()
        .map(|s| s.iter().map(|&x| x as i64).collect())
        .collect();
    dict.set_item("prediction_sets", sets)?;
    dict.set_item("coverage", result.coverage)?;
    Ok(dict)
}

/// Conformal elastic regression prediction intervals.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Functional predictors (training), shape (n, m).
/// response : numpy.ndarray
///     Scalar response, length n.
/// test_data : numpy.ndarray
///     Test functional predictors, shape (n_test, m).
/// argvals : numpy.ndarray
///     Evaluation points, length m.
/// ncomp_beta : int, optional
///     Number of beta components (default 3).
/// lambda : float, optional
///     Regularization parameter (default 0.0).
/// cal_fraction : float, optional
///     Calibration fraction (default 0.25).
/// alpha : float, optional
///     Miscoverage level (default 0.1).
/// seed : int, optional
///     Random seed (default 42).
///
/// Returns
/// -------
/// dict
///     lower (n_test,), upper (n_test,), predictions (n_test,), coverage.
#[pyfunction]
#[pyo3(signature = (data, response, test_data, argvals, ncomp_beta=3, lambda=0.0, cal_fraction=0.25, alpha=0.1, seed=42))]
pub fn conformal_elastic_regression<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    response: PyReadonlyArray1<'py, f64>,
    test_data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    ncomp_beta: usize,
    lambda: f64,
    cal_fraction: f64,
    alpha: f64,
    seed: u64,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let resp = numpy1d_to_vec(response);
    let tmat = numpy2d_to_fdmatrix(test_data)?;
    let av = numpy1d_to_vec(argvals);
    let result = to_pyresult(fdars_core::conformal::conformal_elastic_regression(
        &mat,
        &resp,
        &tmat,
        &av,
        ncomp_beta,
        lambda,
        cal_fraction,
        alpha,
        seed,
    ))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("lower", vec_to_numpy1d(py, result.lower))?;
    dict.set_item("upper", vec_to_numpy1d(py, result.upper))?;
    dict.set_item("predictions", vec_to_numpy1d(py, result.predictions))?;
    dict.set_item("coverage", result.coverage)?;
    Ok(dict)
}

/// Conformal elastic PCR prediction intervals.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Functional predictors (training), shape (n, m).
/// response : numpy.ndarray
///     Scalar response, length n.
/// test_data : numpy.ndarray
///     Test functional predictors, shape (n_test, m).
/// argvals : numpy.ndarray
///     Evaluation points, length m.
/// ncomp : int, optional
///     Number of components (default 3).
/// pca_method : str, optional
///     PCA method: "vertical" (default), "horizontal", "joint".
/// lambda : float, optional
///     Regularization parameter (default 0.0).
/// cal_fraction : float, optional
///     Calibration fraction (default 0.25).
/// alpha : float, optional
///     Miscoverage level (default 0.1).
/// seed : int, optional
///     Random seed (default 42).
///
/// Returns
/// -------
/// dict
///     lower (n_test,), upper (n_test,), predictions (n_test,), coverage.
#[pyfunction]
#[pyo3(signature = (data, response, test_data, argvals, ncomp=3, pca_method="vertical", lambda=0.0, cal_fraction=0.25, alpha=0.1, seed=42))]
pub fn conformal_elastic_pcr<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    response: PyReadonlyArray1<'py, f64>,
    test_data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    ncomp: usize,
    pca_method: &str,
    lambda: f64,
    cal_fraction: f64,
    alpha: f64,
    seed: u64,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let resp = numpy1d_to_vec(response);
    let tmat = numpy2d_to_fdmatrix(test_data)?;
    let av = numpy1d_to_vec(argvals);
    let pca = match pca_method {
        "vertical" => fdars_core::elastic_regression::PcaMethod::Vertical,
        "horizontal" => fdars_core::elastic_regression::PcaMethod::Horizontal,
        "joint" => fdars_core::elastic_regression::PcaMethod::Joint,
        _ => {
            return Err(pyo3::exceptions::PyValueError::new_err(
                "pca_method must be 'vertical', 'horizontal', or 'joint'",
            ))
        }
    };
    let result = to_pyresult(fdars_core::conformal::conformal_elastic_pcr(
        &mat,
        &resp,
        &tmat,
        &av,
        ncomp,
        pca,
        lambda,
        cal_fraction,
        alpha,
        seed,
    ))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("lower", vec_to_numpy1d(py, result.lower))?;
    dict.set_item("upper", vec_to_numpy1d(py, result.upper))?;
    dict.set_item("predictions", vec_to_numpy1d(py, result.predictions))?;
    dict.set_item("coverage", result.coverage)?;
    Ok(dict)
}

/// Conformal logistic regression prediction sets.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Functional predictors (training), shape (n, m).
/// response : numpy.ndarray
///     Binary response (0/1), length n.
/// test_data : numpy.ndarray
///     Test functional predictors, shape (n_test, m).
/// ncomp : int, optional
///     Number of FPC components (default 3).
/// max_iter : int, optional
///     Maximum logistic regression iterations (default 100).
/// tol : float, optional
///     Convergence tolerance (default 1e-6).
/// cal_fraction : float, optional
///     Calibration fraction (default 0.25).
/// alpha : float, optional
///     Miscoverage level (default 0.1).
/// seed : int, optional
///     Random seed (default 42).
///
/// Returns
/// -------
/// dict
///     prediction_sets (list of lists), coverage.
#[pyfunction]
#[pyo3(signature = (data, response, test_data, ncomp=3, max_iter=100, tol=1e-6, cal_fraction=0.25, alpha=0.1, seed=42))]
pub fn conformal_logistic<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    response: PyArrayLike1<'py, f64, AllowTypeChange>,
    test_data: PyReadonlyArray2<'py, f64>,
    ncomp: usize,
    max_iter: usize,
    tol: f64,
    cal_fraction: f64,
    alpha: f64,
    seed: u64,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let resp = response.as_array().to_vec();
    let tmat = numpy2d_to_fdmatrix(test_data)?;
    let result = to_pyresult(fdars_core::conformal::conformal_logistic(
        &mat,
        &resp,
        &tmat,
        None,
        None,
        ncomp,
        max_iter,
        tol,
        fdars_core::conformal::ClassificationScore::Lac,
        cal_fraction,
        alpha,
        seed,
    ))?;

    let dict = pyo3::types::PyDict::new(py);
    let sets: Vec<Vec<i64>> = result
        .prediction_sets
        .iter()
        .map(|s| s.iter().map(|&x| x as i64).collect())
        .collect();
    dict.set_item("prediction_sets", sets)?;
    dict.set_item("coverage", result.coverage)?;
    Ok(dict)
}

/// Conformal elastic logistic regression prediction sets.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Functional predictors (training), shape (n, m).
/// labels : numpy.ndarray
///     Binary labels (-1/+1), length n.
/// test_data : numpy.ndarray
///     Test functional predictors, shape (n_test, m).
/// argvals : numpy.ndarray
///     Evaluation points, length m.
/// lambda : float, optional
///     Regularization parameter (default 0.0).
/// cal_fraction : float, optional
///     Calibration fraction (default 0.25).
/// alpha : float, optional
///     Miscoverage level (default 0.1).
/// seed : int, optional
///     Random seed (default 42).
///
/// Returns
/// -------
/// dict
///     prediction_sets (list of lists), coverage.
#[pyfunction]
#[pyo3(signature = (data, labels, test_data, argvals, lambda=0.0, cal_fraction=0.25, alpha=0.1, seed=42))]
pub fn conformal_elastic_logistic<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    labels: PyArrayLike1<'py, i64, AllowTypeChange>,
    test_data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    lambda: f64,
    cal_fraction: f64,
    alpha: f64,
    seed: u64,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let lab: Vec<i8> = labels.as_array().iter().map(|&x| x as i8).collect();
    let tmat = numpy2d_to_fdmatrix(test_data)?;
    let av = numpy1d_to_vec(argvals);
    let result = to_pyresult(fdars_core::conformal::conformal_elastic_logistic(
        &mat,
        &lab,
        &tmat,
        &av,
        lambda,
        fdars_core::conformal::ClassificationScore::Lac,
        cal_fraction,
        alpha,
        seed,
    ))?;

    let dict = pyo3::types::PyDict::new(py);
    let sets: Vec<Vec<i64>> = result
        .prediction_sets
        .iter()
        .map(|s| s.iter().map(|&x| x as i64).collect())
        .collect();
    dict.set_item("prediction_sets", sets)?;
    dict.set_item("coverage", result.coverage)?;
    Ok(dict)
}

// ---------------------------------------------------------------------------
// Partial-curve conformal prediction (Wang, Kurtek & Zhang 2026)
// ---------------------------------------------------------------------------

/// Build a `PartialConformalConfig` from the shared ``**PC`` kwargs.
fn partial_config(
    alpha: f64,
    cal_fraction: f64,
    seed: u64,
    distance: &str,
    bandwidth: Option<f64>,
    lambda: f64,
    karcher_max_iter: usize,
    karcher_tol: f64,
    n_phase_radii: usize,
    band: &str,
    band_scale: Option<&Bound<'_, PyAny>>,
    tuning_fraction: Option<f64>,
    bandwidth_candidates: Option<Vec<f64>>,
) -> PyResult<PartialConformalConfig> {
    let mut c = PartialConformalConfig::default();
    c.alpha = alpha;
    c.cal_fraction = cal_fraction;
    c.seed = seed;
    c.distance = match distance {
        "l2" => PartialPredictorDistance::L2,
        "srsf" => PartialPredictorDistance::Srsf,
        "elastic" => PartialPredictorDistance::Elastic,
        _ => {
            return Err(PyValueError::new_err(format!(
                "distance must be one of 'l2', 'srsf', 'elastic', got '{distance}'"
            )))
        }
    };
    c.bandwidth = bandwidth;
    c.lambda = lambda;
    c.karcher_max_iter = karcher_max_iter;
    c.karcher_tol = karcher_tol;
    c.n_phase_radii = n_phase_radii;
    c.band = partial_band(band)?;
    c.band_scale = match band_scale {
        None => PartialBandScale::Constant,
        Some(obj) => {
            if let Ok(name) = obj.extract::<String>() {
                match name.as_str() {
                    "constant" => PartialBandScale::Constant,
                    "training_sd" => PartialBandScale::TrainingSd,
                    _ => {
                        return Err(PyValueError::new_err(format!(
                            "band_scale must be None, 'constant', 'training_sd' or a 1-D array, got '{name}'"
                        )))
                    }
                }
            } else {
                let arr = obj
                    .extract::<PyArrayLike1<'_, f64, AllowTypeChange>>()
                    .map_err(|_| {
                        PyValueError::new_err(
                            "band_scale must be None, 'constant', 'training_sd' or a 1-D array",
                        )
                    })?;
                PartialBandScale::Custom(arr.as_array().to_vec())
            }
        }
    };
    c.tuning_fraction = tuning_fraction;
    c.bandwidth_candidates = bandwidth_candidates.unwrap_or_default();
    Ok(c)
}

fn partial_band(band: &str) -> PyResult<PartialAmplitudeBand> {
    match band {
        "pointwise" => Ok(PartialAmplitudeBand::Pointwise),
        "simultaneous" => Ok(PartialAmplitudeBand::Simultaneous),
        _ => Err(PyValueError::new_err(format!(
            "band must be 'pointwise' or 'simultaneous', got '{band}'"
        ))),
    }
}

fn partial_band_name(band: PartialAmplitudeBand) -> &'static str {
    match band {
        PartialAmplitudeBand::Simultaneous => "simultaneous",
        _ => "pointwise",
    }
}

/// Parse the observation-pattern kwargs into a `PartialObservation`.
fn partial_observation(
    observation: &str,
    n_observed: Option<usize>,
    fragments: Option<PyArrayLike2<'_, i64, AllowTypeChange>>,
    times: Option<PyReadonlyArray1<'_, f64>>,
    n_values: Option<usize>,
) -> PyResult<PartialObservation> {
    match observation {
        "prefix" => {
            let n = n_observed
                .or(n_values)
                .ok_or_else(|| PyValueError::new_err("observation='prefix' needs n_observed"))?;
            Ok(PartialObservation::Prefix(n))
        }
        "fragments" => {
            let f = fragments.ok_or_else(|| {
                PyValueError::new_err("observation='fragments' needs fragments, a (K, 2) int array")
            })?;
            let a = f.as_array();
            if a.ncols() != 2 || a.iter().any(|&x| x < 0) {
                return Err(PyValueError::new_err(
                    "fragments must be a (K, 2) array of non-negative inclusive grid index ranges",
                ));
            }
            Ok(PartialObservation::Fragments(
                a.rows()
                    .into_iter()
                    .map(|r| (r[0] as usize, r[1] as usize))
                    .collect(),
            ))
        }
        "sparse" => {
            let t = times.ok_or_else(|| {
                PyValueError::new_err("observation='sparse' needs times, a 1-D array")
            })?;
            Ok(PartialObservation::Sparse(numpy1d_to_vec(t)))
        }
        _ => Err(PyValueError::new_err(format!(
            "observation must be 'prefix', 'fragments' or 'sparse', got '{observation}'"
        ))),
    }
}

fn partial_match_dict<'py>(
    py: Python<'py>,
    r: &fdars_core::alignment::PartialMatchResult,
) -> PyResult<Bound<'py, PyDict>> {
    let d = PyDict::new(py);
    d.set_item("start_index", r.start_index)?;
    d.set_item("end_index", r.end_index)?;
    d.set_item("gamma", vec_to_numpy1d(py, r.gamma.clone()))?;
    d.set_item("distance", r.distance)?;
    d.set_item("domain_fraction", r.domain_fraction)?;
    Ok(d)
}

fn bandwidth_selection_dict<'py>(
    py: Python<'py>,
    s: &PartialBandwidthSelection,
) -> PyResult<Bound<'py, PyDict>> {
    let d = PyDict::new(py);
    d.set_item("bandwidth", s.bandwidth)?;
    d.set_item("candidates", vec_to_numpy1d(py, s.candidates.clone()))?;
    d.set_item("mean_width", vec_to_numpy1d(py, s.mean_width.clone()))?;
    d.set_item("n_tuning", s.n_tuning)?;
    Ok(d)
}

fn partial_prediction_dict<'py>(
    py: Python<'py>,
    p: PartialConformalPrediction,
) -> PyResult<Bound<'py, PyDict>> {
    let d = PyDict::new(py);
    d.set_item("n_observed", p.n_observed)?;
    d.set_item("observed_end", p.observed_end)?;
    d.set_item("alpha", p.alpha)?;
    d.set_item("bandwidth", p.bandwidth)?;
    d.set_item("weights", vec_to_numpy1d(py, p.weights.clone()))?;
    d.set_item("registration", partial_match_dict(py, &p.registration)?)?;
    match &p.full_registration {
        Some(a) => {
            let fd = PyDict::new(py);
            fd.set_item("gamma", vec_to_numpy1d(py, a.gamma.clone()))?;
            fd.set_item("f_aligned", vec_to_numpy1d(py, a.f_aligned.clone()))?;
            fd.set_item("distance", a.distance)?;
            d.set_item("full_registration", fd)?;
        }
        None => d.set_item("full_registration", py.None())?,
    }
    let frags = PyList::empty(py);
    for f in &p.fragment_registrations {
        frags.append(partial_match_dict(py, f)?)?;
    }
    d.set_item("fragment_registrations", frags)?;
    d.set_item("band", partial_band_name(p.band))?;
    d.set_item("amplitude_radius", p.amplitude_radius)?;
    match &p.bandwidth_selection {
        Some(s) => d.set_item("bandwidth_selection", bandwidth_selection_dict(py, s)?)?,
        None => d.set_item("bandwidth_selection", py.None())?,
    }
    for (k, v) in [
        ("amplitude_center", &p.amplitude_center),
        ("amplitude_lower", &p.amplitude_lower),
        ("amplitude_upper", &p.amplitude_upper),
        ("phase_center", &p.phase_center),
        ("phase_lower", &p.phase_lower),
        ("phase_upper", &p.phase_upper),
    ] {
        d.set_item(k, vec_to_numpy1d(py, v.clone()))?;
    }
    d.set_item("phase_radius", p.phase_radius)?;
    d.set_item("phase_accepted", fdmatrix_to_numpy2d(py, &p.phase_accepted))?;
    d.set_item(
        "prediction",
        Py::new(py, PyPartialConformalPrediction { inner: p })?,
    )?;
    Ok(d)
}

/// Opaque handle wrapping a fitted partial-curve conformal model (PartialConformalModel).
///
/// Returned by `partial_conformal_fit` / `partial_conformal_fit_with_template`;
/// it stores the fit configuration, which the predict functions reuse.
#[pyclass(name = "PyPartialConformalModel")]
pub struct PyPartialConformalModel {
    pub inner: PartialConformalModel,
    pub config: PartialConformalConfig,
}

#[pymethods]
impl PyPartialConformalModel {
    /// Evaluation grid, length m.
    #[getter]
    pub fn argvals<'py>(&self, py: Python<'py>) -> Bound<'py, PyArray1<f64>> {
        vec_to_numpy1d(py, self.inner.argvals.clone())
    }

    /// Elastic (Karcher mean) template, length m.
    #[getter]
    pub fn template<'py>(&self, py: Python<'py>) -> Bound<'py, PyArray1<f64>> {
        vec_to_numpy1d(py, self.inner.template.clone())
    }

    /// Row indices of the template-estimation curves (empty for a supplied template).
    #[getter]
    pub fn training_indices<'py>(&self, py: Python<'py>) -> Bound<'py, PyArray1<i64>> {
        usize_vec_to_numpy1d(py, self.inner.training_indices.clone())
    }

    /// Row indices of the calibration curves.
    #[getter]
    pub fn calibration_indices<'py>(&self, py: Python<'py>) -> Bound<'py, PyArray1<i64>> {
        usize_vec_to_numpy1d(py, self.inner.calibration_indices.clone())
    }

    /// Raw calibration curves, shape (n_2, m).
    #[getter]
    pub fn calibration_data<'py>(&self, py: Python<'py>) -> Bound<'py, PyArray2<f64>> {
        fdmatrix_to_numpy2d(py, &self.inner.calibration_data)
    }

    /// Warps registering each calibration curve to the template, shape (n_2, m).
    #[getter]
    pub fn calibration_gammas<'py>(&self, py: Python<'py>) -> Bound<'py, PyArray2<f64>> {
        fdmatrix_to_numpy2d(py, &self.inner.calibration_gammas)
    }

    /// Aligned calibration curves, shape (n_2, m).
    #[getter]
    pub fn calibration_aligned<'py>(&self, py: Python<'py>) -> Bound<'py, PyArray2<f64>> {
        fdmatrix_to_numpy2d(py, &self.inner.calibration_aligned)
    }

    /// Row indices of the held-out bandwidth-tuning curves.
    #[getter]
    pub fn tuning_indices<'py>(&self, py: Python<'py>) -> Bound<'py, PyArray1<i64>> {
        usize_vec_to_numpy1d(py, self.inner.tuning_indices.clone())
    }

    /// Raw tuning curves, shape (n_T, m).
    #[getter]
    pub fn tuning_data<'py>(&self, py: Python<'py>) -> Bound<'py, PyArray2<f64>> {
        fdmatrix_to_numpy2d(py, &self.inner.tuning_data)
    }

    /// Tuning curves aligned to the template, shape (n_T, m).
    #[getter]
    pub fn tuning_aligned<'py>(&self, py: Python<'py>) -> Bound<'py, PyArray2<f64>> {
        fdmatrix_to_numpy2d(py, &self.inner.tuning_aligned)
    }

    /// Pointwise sd of the aligned training curves (None for a supplied template).
    #[getter]
    pub fn training_sd<'py>(&self, py: Python<'py>) -> Option<Bound<'py, PyArray1<f64>>> {
        self.inner
            .training_sd
            .clone()
            .map(|v| vec_to_numpy1d(py, v))
    }

    /// Miscoverage level of the stored configuration.
    #[getter]
    pub fn alpha(&self) -> f64 {
        self.config.alpha
    }

    /// Amplitude band type of the stored configuration.
    #[getter]
    pub fn band(&self) -> &'static str {
        partial_band_name(self.config.band)
    }
}

/// Opaque handle wrapping one partial-curve conformal prediction (PartialConformalPrediction).
///
/// Returned as ``"prediction"`` by the partial-conformal predict functions;
/// ``phase_set_contains`` tests exact membership in the phase prediction set.
#[pyclass(name = "PyPartialConformalPrediction")]
pub struct PyPartialConformalPrediction {
    pub inner: PartialConformalPrediction,
}

#[pymethods]
impl PyPartialConformalPrediction {
    /// Point prediction of the warp, length m.
    #[getter]
    pub fn phase_center<'py>(&self, py: Python<'py>) -> Bound<'py, PyArray1<f64>> {
        vec_to_numpy1d(py, self.inner.phase_center.clone())
    }

    /// Exact membership of a warp in the split-conformal phase prediction set.
    ///
    /// Parameters
    /// ----------
    /// gamma : numpy.ndarray
    ///     Warp on the ``argvals`` domain, length m.
    ///
    /// Returns
    /// -------
    /// bool
    pub fn phase_set_contains(&self, gamma: PyReadonlyArray1<'_, f64>) -> PyResult<bool> {
        to_pyresult(self.inner.phase_set_contains(gamma.as_slice()?))
    }
}

/// Fit the partial-curve conformal model: random split, elastic Karcher template, registration.
///
/// SFCP / SFCPP of Wang, Kurtek & Zhang (2026): the training part of the
/// split estimates the elastic template, the calibration part is registered
/// to it. Predict with ``partial_conformal_predict`` (prefix) or
/// ``partial_conformal_predict_observed`` (prefix, fragments, sparse).
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Fully observed curves, shape (n, m), n >= 4.
/// argvals : numpy.ndarray
///     Strictly increasing evaluation points, length m.
/// alpha : float, optional
///     Miscoverage level in (0, 1) (default 0.1).
/// cal_fraction : float, optional
///     Calibration share of the curves (default 0.5).
/// seed : int, optional
///     Split seed (default 42).
/// distance : str, optional
///     Predictor distance on the observed part: ``"l2"`` (default),
///     ``"srsf"`` or ``"elastic"``.
/// bandwidth : float or None, optional
///     Kernel bandwidth; None = median pairwise predictor distance (or the
///     tuned bandwidth when ``tuning_fraction`` is set).
/// lambda_ : float, optional
///     DP registration penalty (default 0.0).
/// karcher_max_iter, karcher_tol : optional
///     Template Karcher mean iterations (default 20) and tolerance
///     (default 1e-3).
/// n_phase_radii : int, optional
///     Radii per geodesic direction of the phase trial family (default 25).
/// band : str, optional
///     ``"pointwise"`` (default) or ``"simultaneous"`` amplitude band.
/// band_scale : str, numpy.ndarray or None, optional
///     Simultaneous-band modulation: None / ``"constant"`` (default),
///     ``"training_sd"`` or a positive array of length m.
/// tuning_fraction : float or None, optional
///     Reserve this share of the calibration curves for held-out
///     bandwidth tuning (default None = off).
/// bandwidth_candidates : sequence of float or None, optional
///     Tuning candidates (default: quantiles of the tuning distances).
///
/// Returns
/// -------
/// PyPartialConformalModel
#[pyfunction]
#[pyo3(signature = (data, argvals, alpha=0.1, cal_fraction=0.5, seed=42, distance="l2", bandwidth=None, lambda_=0.0, karcher_max_iter=20, karcher_tol=1e-3, n_phase_radii=25, band="pointwise", band_scale=None, tuning_fraction=None, bandwidth_candidates=None))]
pub fn partial_conformal_fit(
    data: PyReadonlyArray2<'_, f64>,
    argvals: PyReadonlyArray1<'_, f64>,
    alpha: f64,
    cal_fraction: f64,
    seed: u64,
    distance: &str,
    bandwidth: Option<f64>,
    lambda_: f64,
    karcher_max_iter: usize,
    karcher_tol: f64,
    n_phase_radii: usize,
    band: &str,
    band_scale: Option<&Bound<'_, PyAny>>,
    tuning_fraction: Option<f64>,
    bandwidth_candidates: Option<Vec<f64>>,
) -> PyResult<PyPartialConformalModel> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let config = partial_config(
        alpha,
        cal_fraction,
        seed,
        distance,
        bandwidth,
        lambda_,
        karcher_max_iter,
        karcher_tol,
        n_phase_radii,
        band,
        band_scale,
        tuning_fraction,
        bandwidth_candidates,
    )?;
    let inner = to_pyresult(fdars_core::conformal::partial_conformal_fit(
        &mat, &av, &config,
    ))?;
    Ok(PyPartialConformalModel { inner, config })
}

/// Fit the partial-curve conformal model with a supplied template (all curves calibrate).
///
/// Parameters
/// ----------
/// calibration : numpy.ndarray
///     Fully observed calibration curves, shape (n_2, m), n_2 >= 2.
/// argvals : numpy.ndarray
///     Strictly increasing evaluation points, length m.
/// template : numpy.ndarray
///     Template curve (independent of the calibration curves), length m.
/// alpha, cal_fraction, seed, distance, bandwidth, lambda_, karcher_max_iter, karcher_tol, n_phase_radii, band, band_scale, tuning_fraction, bandwidth_candidates : optional
///     As ``partial_conformal_fit`` (``band_scale="training_sd"`` is not
///     available without training curves).
///
/// Returns
/// -------
/// PyPartialConformalModel
#[pyfunction]
#[pyo3(signature = (calibration, argvals, template, alpha=0.1, cal_fraction=0.5, seed=42, distance="l2", bandwidth=None, lambda_=0.0, karcher_max_iter=20, karcher_tol=1e-3, n_phase_radii=25, band="pointwise", band_scale=None, tuning_fraction=None, bandwidth_candidates=None))]
pub fn partial_conformal_fit_with_template(
    calibration: PyReadonlyArray2<'_, f64>,
    argvals: PyReadonlyArray1<'_, f64>,
    template: PyReadonlyArray1<'_, f64>,
    alpha: f64,
    cal_fraction: f64,
    seed: u64,
    distance: &str,
    bandwidth: Option<f64>,
    lambda_: f64,
    karcher_max_iter: usize,
    karcher_tol: f64,
    n_phase_radii: usize,
    band: &str,
    band_scale: Option<&Bound<'_, PyAny>>,
    tuning_fraction: Option<f64>,
    bandwidth_candidates: Option<Vec<f64>>,
) -> PyResult<PyPartialConformalModel> {
    let mat = numpy2d_to_fdmatrix(calibration)?;
    let av = numpy1d_to_vec(argvals);
    let tmpl = numpy1d_to_vec(template);
    let config = partial_config(
        alpha,
        cal_fraction,
        seed,
        distance,
        bandwidth,
        lambda_,
        karcher_max_iter,
        karcher_tol,
        n_phase_radii,
        band,
        band_scale,
        tuning_fraction,
        bandwidth_candidates,
    )?;
    let inner = to_pyresult(fdars_core::conformal::partial_conformal_fit_with_template(
        &mat, &av, &tmpl, &config,
    ))?;
    Ok(PyPartialConformalModel { inner, config })
}

fn config_with_alpha(
    model: &PyPartialConformalModel,
    alpha: Option<f64>,
) -> PartialConformalConfig {
    let mut cfg = model.config.clone();
    if let Some(a) = alpha {
        cfg.alpha = a;
    }
    cfg
}

/// Conformal amplitude band and phase set for a curve observed on a grid prefix.
///
/// Parameters
/// ----------
/// model : PyPartialConformalModel
///     From ``partial_conformal_fit`` / ``partial_conformal_fit_with_template``.
/// observed : numpy.ndarray
///     Values on ``argvals[:len(observed)]`` (2 <= len <= m; all m values for a
///     fully observed curve).
/// alpha : float or None, optional
///     Override the model's miscoverage level.
///
/// Returns
/// -------
/// dict
///     ``n_observed``, ``observed_end``, ``alpha``, ``bandwidth``, ``weights``
///     (n_2,), ``registration`` (partial match: start_index, end_index,
///     gamma, distance, domain_fraction), ``full_registration`` (None or
///     {gamma, f_aligned, distance}), ``fragment_registrations`` (list),
///     ``band``, ``amplitude_radius`` (None for pointwise),
///     ``bandwidth_selection`` (None or {bandwidth, candidates, mean_width,
///     n_tuning}), ``amplitude_center`` / ``_lower`` / ``_upper``,
///     ``phase_center`` / ``_lower`` / ``_upper`` (m,), ``phase_radius``,
///     ``phase_accepted`` (n_accepted, m) and ``prediction``
///     (``PyPartialConformalPrediction`` with ``phase_set_contains``).
#[pyfunction]
#[pyo3(signature = (model, observed, alpha=None))]
pub fn partial_conformal_predict<'py>(
    py: Python<'py>,
    model: &PyPartialConformalModel,
    observed: PyReadonlyArray1<'py, f64>,
    alpha: Option<f64>,
) -> PyResult<Bound<'py, PyDict>> {
    let obs = numpy1d_to_vec(observed);
    let cfg = config_with_alpha(model, alpha);
    let p = to_pyresult(fdars_core::conformal::partial_conformal_predict(
        &model.inner,
        &obs,
        &cfg,
    ))?;
    partial_prediction_dict(py, p)
}

/// Conformal amplitude band and phase set for a curve observed on a prefix, fragments or sparse times.
///
/// Parameters
/// ----------
/// model : PyPartialConformalModel
///     Fitted model.
/// values : numpy.ndarray
///     Observed values in pattern order (fragments concatenated).
/// observation : str, optional
///     ``"prefix"`` (default), ``"fragments"`` or ``"sparse"``.
/// n_observed : int or None, optional
///     Prefix length (default ``len(values)``).
/// fragments : numpy.ndarray or None, optional
///     (K, 2) inclusive grid index ranges, strictly increasing and disjoint.
/// times : numpy.ndarray or None, optional
///     Sparse observation times inside the domain (strictly increasing).
/// alpha : float or None, optional
///     Override the model's miscoverage level.
///
/// Returns
/// -------
/// dict
///     As ``partial_conformal_predict``.
#[pyfunction]
#[pyo3(signature = (model, values, observation="prefix", n_observed=None, fragments=None, times=None, alpha=None))]
pub fn partial_conformal_predict_observed<'py>(
    py: Python<'py>,
    model: &PyPartialConformalModel,
    values: PyReadonlyArray1<'py, f64>,
    observation: &str,
    n_observed: Option<usize>,
    fragments: Option<PyArrayLike2<'py, i64, AllowTypeChange>>,
    times: Option<PyReadonlyArray1<'py, f64>>,
    alpha: Option<f64>,
) -> PyResult<Bound<'py, PyDict>> {
    let vals = numpy1d_to_vec(values);
    let obs = partial_observation(observation, n_observed, fragments, times, Some(vals.len()))?;
    let cfg = config_with_alpha(model, alpha);
    let p = to_pyresult(fdars_core::conformal::partial_conformal_predict_observed(
        &model.inner,
        &obs,
        &vals,
        &cfg,
    ))?;
    partial_prediction_dict(py, p)
}

/// Held-out bandwidth selection for partial-curve conformal prediction.
///
/// Each calibration curve of ``tuning_model`` is predicted from the others
/// under the given observation pattern; the bandwidth minimising the mean
/// amplitude band width wins. Using it as ``bandwidth`` for a model fitted on
/// other curves keeps exact finite-sample coverage.
///
/// Parameters
/// ----------
/// tuning_model : PyPartialConformalModel
///     Model whose calibration curves form the tuning set.
/// observation : str, optional
///     ``"prefix"`` (default), ``"fragments"`` or ``"sparse"``.
/// n_observed : int or None
///     Prefix length (required for ``"prefix"``).
/// fragments, times : optional
///     As ``partial_conformal_predict_observed``.
///
/// Returns
/// -------
/// dict
///     ``bandwidth``, ``candidates``, ``mean_width`` (per candidate),
///     ``n_tuning``.
#[pyfunction]
#[pyo3(signature = (tuning_model, observation="prefix", n_observed=None, fragments=None, times=None))]
pub fn partial_conformal_select_bandwidth<'py>(
    py: Python<'py>,
    tuning_model: &PyPartialConformalModel,
    observation: &str,
    n_observed: Option<usize>,
    fragments: Option<PyArrayLike2<'py, i64, AllowTypeChange>>,
    times: Option<PyReadonlyArray1<'py, f64>>,
) -> PyResult<Bound<'py, PyDict>> {
    let obs = partial_observation(observation, n_observed, fragments, times, None)?;
    let s = to_pyresult(fdars_core::conformal::partial_conformal_select_bandwidth(
        &tuning_model.inner,
        &obs,
        &tuning_model.config,
    ))?;
    bandwidth_selection_dict(py, &s)
}

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyPartialConformalModel>()?;
    m.add_class::<PyPartialConformalPrediction>()?;
    m.add_function(wrap_pyfunction!(conformal_fregre_lm, m)?)?;
    m.add_function(wrap_pyfunction!(conformal_fregre_np, m)?)?;
    m.add_function(wrap_pyfunction!(conformal_classif, m)?)?;
    m.add_function(wrap_pyfunction!(conformal_elastic_regression, m)?)?;
    m.add_function(wrap_pyfunction!(conformal_elastic_pcr, m)?)?;
    m.add_function(wrap_pyfunction!(conformal_logistic, m)?)?;
    m.add_function(wrap_pyfunction!(conformal_elastic_logistic, m)?)?;
    m.add_function(wrap_pyfunction!(partial_conformal_fit, m)?)?;
    m.add_function(wrap_pyfunction!(partial_conformal_fit_with_template, m)?)?;
    m.add_function(wrap_pyfunction!(partial_conformal_predict, m)?)?;
    m.add_function(wrap_pyfunction!(partial_conformal_predict_observed, m)?)?;
    m.add_function(wrap_pyfunction!(partial_conformal_select_bandwidth, m)?)?;
    Ok(())
}
