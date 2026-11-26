//! PACE FPCA and IrregFdata bindings for irregular/sparse functional data.
//!
//! Exposes `PyIrregFdata` (opaque #[pyclass] handle), `irreg_fdata_from_lists`
//! (builder from Python ragged lists), and `pace_fpca` (PACE FPCA over
//! irregular data) as the `fdars.pace_fpca` submodule, plus the reusable
//! `PyPaceFpcaFit` handle and the fdars-core 0.48 optimal-design functions
//! (`design_criterion`, `optimal_design`).
//!
//! This is pyfda's first `#[pyclass]` opaque handle — introduced so the PACE
//! input type has a named Python type and validates once at construction.

use crate::convert::{
    fdmatrix_to_numpy2d, nonneg_labels, to_pyresult, usize_vec_to_numpy1d, vec_to_numpy1d,
};
use fdars_core::optimal_design::{DesignCriterion, OptDesConfig, OptimalityKind};
use fdars_core::pace_fpca::PaceFpcaResult;
use numpy::{AllowTypeChange, PyArray1, PyArrayLike1, PyUntypedArrayMethods};
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};

// ---------------------------------------------------------------------------
// Opaque #[pyclass] handle
// ---------------------------------------------------------------------------

/// Opaque handle wrapping fdars-core IrregFdata for irregular/sparse functional data.
///
/// Construct via `fdars.pace_fpca.irreg_fdata_from_lists(argvals_list, values_list)`.
/// Pass to `fdars.pace_fpca.pace_fpca(handle, ...)`.
#[pyclass(name = "PyIrregFdata")]
pub struct PyIrregFdata {
    pub inner: fdars_core::irreg_fdata::IrregFdata,
}

// ---------------------------------------------------------------------------
// #[pyfunction] irreg_fdata_from_lists
// ---------------------------------------------------------------------------

/// Build an IrregFdata handle from two Python lists of ragged 1-D arrays.
///
/// Parameters
/// ----------
/// argvals_list : list of array-like
///     One 1-D array per curve giving evaluation points (ragged; lengths may differ).
/// values_list : list of array-like
///     One 1-D array per curve giving observed values; must match the corresponding
///     argvals entry in length.
///
/// Returns
/// -------
/// PyIrregFdata
///     Opaque handle for use with `pace_fpca`.
///
/// Raises
/// ------
/// ValueError
///     If a 2-D numpy array is passed (dense data), if the outer lengths differ,
///     or if any curve's argvals and values lengths differ.
#[pyfunction]
pub fn irreg_fdata_from_lists<'py>(
    py: Python<'py>,
    argvals_list: &Bound<'py, PyAny>,
    values_list: &Bound<'py, PyAny>,
) -> PyResult<Py<PyIrregFdata>> {
    // Guard: reject dense 2-D numpy arrays of any dtype (T-38-03, CR-01).
    // is_instance_of::<PyArray2<f64>>() checks both ndim==2 AND dtype==f64, so
    // arrays of other dtypes (int32, float32, int64, …) would bypass the guard.
    // Instead, downcast to the untyped PyUntypedArray base (any numpy ndarray)
    // and inspect its ndim — dtype-agnostic.
    let arg_is_2d = argvals_list
        .cast::<numpy::PyUntypedArray>()
        .map(|a| a.ndim() == 2)
        .unwrap_or(false);
    let val_is_2d = values_list
        .cast::<numpy::PyUntypedArray>()
        .map(|a| a.ndim() == 2)
        .unwrap_or(false);
    if arg_is_2d || val_is_2d {
        return Err(PyValueError::new_err(
            "irreg_fdata_from_lists: received a 2-D numpy array; \
             pass two Python lists of 1-D arrays (one per curve), not a dense matrix. \
             For dense functional data, use fdars.fdata functions directly.",
        ));
    }

    // Downcast both to PyList
    let av_list = argvals_list
        .cast::<PyList>()
        .map_err(|_| PyValueError::new_err("argvals_list must be a Python list of 1-D arrays"))?;
    let vl_list = values_list
        .cast::<PyList>()
        .map_err(|_| PyValueError::new_err("values_list must be a Python list of 1-D arrays"))?;

    // Extract ragged vecs
    let av_vecs = crate::convert::extract_ragged_vecs(av_list, "irreg_fdata_from_lists")?;
    let vl_vecs = crate::convert::extract_ragged_vecs(vl_list, "irreg_fdata_from_lists")?;

    // Guard: outer-length mismatch BEFORE from_lists (which would assert_eq! and panic)
    if av_vecs.len() != vl_vecs.len() {
        return Err(PyValueError::new_err(format!(
            "irreg_fdata_from_lists: argvals_list has {} curves but values_list has {} curves",
            av_vecs.len(),
            vl_vecs.len()
        )));
    }

    // Guard: per-curve length mismatch BEFORE from_lists
    for i in 0..av_vecs.len() {
        if av_vecs[i].len() != vl_vecs[i].len() {
            return Err(PyValueError::new_err(format!(
                "irreg_fdata_from_lists: curve {}: argvals has {} points but values has {} points",
                i,
                av_vecs[i].len(),
                vl_vecs[i].len()
            )));
        }
    }

    let inner = fdars_core::irreg_fdata::IrregFdata::from_lists(&av_vecs, &vl_vecs);
    Py::new(py, PyIrregFdata { inner })
}

// ---------------------------------------------------------------------------
// Full 10-key PaceFpcaResult converter
// ---------------------------------------------------------------------------

/// Convert PaceFpcaResult to a Python dict with all 10 keys.
///
/// `eigenfunctions` is shape (m, ncomp) — column k is the k-th eigenfunction;
/// `scores` is shape (n, ncomp). Both use `result.ncomp` (actual, may be <
/// config.ncomp) so shapes are always consistent with the returned `ncomp`.
fn pace_fpca_result_to_pydict<'py>(
    py: Python<'py>,
    r: fdars_core::pace_fpca::PaceFpcaResult,
) -> PyResult<Bound<'py, PyDict>> {
    let dict = PyDict::new(py);
    dict.set_item("mean", vec_to_numpy1d(py, r.mean))?;
    // eigenvalues length = r.ncomp (ACTUAL count, may be < config.ncomp)
    dict.set_item("eigenvalues", vec_to_numpy1d(py, r.eigenvalues))?;
    // eigenfunctions: FdMatrix nrows=m, ncols=ncomp → numpy (m, ncomp)
    // column k is the k-th eigenfunction; access as ef[:, k]
    dict.set_item("eigenfunctions", fdmatrix_to_numpy2d(py, &r.eigenfunctions))?;
    // scores: FdMatrix nrows=n, ncols=ncomp → numpy (n, ncomp)
    dict.set_item("scores", fdmatrix_to_numpy2d(py, &r.scores))?;
    // fitted trajectories on work grid: each (n, m)
    dict.set_item("fitted", fdmatrix_to_numpy2d(py, &r.fitted))?;
    dict.set_item("fitted_lower", fdmatrix_to_numpy2d(py, &r.fitted_lower))?;
    dict.set_item("fitted_upper", fdmatrix_to_numpy2d(py, &r.fitted_upper))?;
    // argvals = work grid echoed from config
    dict.set_item("argvals", vec_to_numpy1d(py, r.argvals))?;
    // sigma2: echoed from config (scalar)
    dict.set_item("sigma2", r.sigma2)?;
    // ncomp: ACTUAL components extracted (may be < requested config.ncomp)
    dict.set_item("ncomp", r.ncomp)?;
    Ok(dict)
}

// ---------------------------------------------------------------------------
// #[pyfunction] run_pace_fpca — exposed to Python as "pace_fpca"
// ---------------------------------------------------------------------------

/// Run PACE FPCA on irregular/sparse functional data.
///
/// Parameters
/// ----------
/// data : PyIrregFdata
///     Opaque handle from `irreg_fdata_from_lists`.
/// ncomp : int, optional
///     Number of components to extract (default 3).
/// bandwidth : float, optional
///     Kernel bandwidth for mean/covariance smoothing (default 0.1).
///     Use >= 0.15 for data on [0,1] with few points per curve.
/// sigma2 : float, optional
///     Measurement error variance (default 0.01).
/// work_grid : list of float, optional
///     Evaluation grid; defaults to 51 uniform points on [0, 1].
/// alpha : float, optional
///     Pointwise confidence level for fitted bands (default 0.05).
///
/// Returns
/// -------
/// dict
///     Keys: mean(m,), eigenvalues(ncomp,), eigenfunctions(m,ncomp),
///     scores(n,ncomp), fitted(n,m), fitted_lower(n,m), fitted_upper(n,m),
///     argvals(m,), sigma2(float), ncomp(int).
///     `ncomp` in the dict is the ACTUAL count extracted (may be < requested).
#[pyfunction(name = "pace_fpca")]
#[pyo3(signature = (data, ncomp=3, bandwidth=0.1, sigma2=0.01, work_grid=None, alpha=0.05))]
pub fn run_pace_fpca<'py>(
    py: Python<'py>,
    data: &PyIrregFdata,
    ncomp: usize,
    bandwidth: f64,
    sigma2: f64,
    work_grid: Option<Vec<f64>>,
    alpha: f64,
) -> PyResult<Bound<'py, PyDict>> {
    let config = pace_config(ncomp, bandwidth, sigma2, work_grid, alpha);
    let result = to_pyresult(fdars_core::pace_fpca::pace_fpca(&data.inner, &config))?;
    pace_fpca_result_to_pydict(py, result)
}

// ---------------------------------------------------------------------------
// Reusable PACE model handle + optimal design (fdars-core 0.48 `optimal_design`)
// ---------------------------------------------------------------------------

/// Fitted PACE FPCA model handle (from `pace_fpca_fit`), consumed by the optimal-design functions.
#[pyclass(name = "PyPaceFpcaFit")]
pub struct PyPaceFpcaFit {
    pub inner: PaceFpcaResult,
}

#[pymethods]
impl PyPaceFpcaFit {
    /// Number of components actually extracted.
    #[getter]
    pub fn ncomp(&self) -> usize {
        self.inner.ncomp
    }

    /// Work grid the model lives on, length m (design indices refer to it).
    #[getter]
    pub fn argvals<'py>(&self, py: Python<'py>) -> Bound<'py, PyArray1<f64>> {
        vec_to_numpy1d(py, self.inner.argvals.clone())
    }

    /// Measurement-error variance.
    #[getter]
    pub fn sigma2(&self) -> f64 {
        self.inner.sigma2
    }

    /// Eigenvalues, length ncomp.
    #[getter]
    pub fn eigenvalues<'py>(&self, py: Python<'py>) -> Bound<'py, PyArray1<f64>> {
        vec_to_numpy1d(py, self.inner.eigenvalues.clone())
    }

    /// The full fit as the dict returned by `pace_fpca`.
    pub fn to_dict<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyDict>> {
        pace_fpca_result_to_pydict(py, self.inner.clone())
    }
}

fn pace_config(
    ncomp: usize,
    bandwidth: f64,
    sigma2: f64,
    work_grid: Option<Vec<f64>>,
    alpha: f64,
) -> fdars_core::pace_fpca::PaceFpcaConfig {
    fdars_core::pace_fpca::PaceFpcaConfig {
        ncomp,
        bandwidth,
        sigma2,
        // Default: 51 uniform points on [0, 1] matching core PaceFpcaConfig::default()
        work_grid: work_grid.unwrap_or_else(|| (0..51).map(|i| i as f64 / 50.0).collect()),
        alpha,
    }
}

/// Fit PACE FPCA on sparse data and keep the fitted model as a reusable handle.
///
/// Same arguments and core call as `pace_fpca`, but returns a
/// ``PyPaceFpcaFit`` for `design_criterion` / `optimal_design`; use
/// ``.to_dict()`` for the plain result.
///
/// Parameters
/// ----------
/// data : PyIrregFdata
///     Opaque handle from `irreg_fdata_from_lists`.
/// ncomp, bandwidth, sigma2, work_grid, alpha
///     As in `pace_fpca` (defaults 3, 0.1, 0.01, 51 points on [0, 1], 0.05).
///
/// Returns
/// -------
/// PyPaceFpcaFit
///     Getters ``ncomp``, ``argvals``, ``sigma2``, ``eigenvalues``; ``to_dict()``.
#[pyfunction]
#[pyo3(signature = (data, ncomp=3, bandwidth=0.1, sigma2=0.01, work_grid=None, alpha=0.05))]
pub fn pace_fpca_fit(
    py: Python<'_>,
    data: &PyIrregFdata,
    ncomp: usize,
    bandwidth: f64,
    sigma2: f64,
    work_grid: Option<Vec<f64>>,
    alpha: f64,
) -> PyResult<Py<PyPaceFpcaFit>> {
    let config = pace_config(ncomp, bandwidth, sigma2, work_grid, alpha);
    let inner = to_pyresult(fdars_core::pace_fpca::pace_fpca(&data.inner, &config))?;
    Py::new(py, PyPaceFpcaFit { inner })
}

fn design_criterion_from_str(s: &str) -> PyResult<DesignCriterion> {
    match s {
        "trajectory" => Ok(DesignCriterion::Trajectory),
        "a" => Ok(DesignCriterion::Score(OptimalityKind::A)),
        "d" => Ok(DesignCriterion::Score(OptimalityKind::D)),
        _ => Err(PyValueError::new_err(format!(
            "criterion must be one of 'trajectory', 'a', 'd', got '{s}'"
        ))),
    }
}

/// Score a set of design points (work-grid indices) against a fitted PACE model.
///
/// Parameters
/// ----------
/// model : PyPaceFpcaFit
///     Handle from `pace_fpca_fit`.
/// selected : array-like of int
///     0-based indices into ``model.argvals`` (may be empty).
/// criterion : str, optional
///     ``"trajectory"`` (default; integrated conditional BLUP reconstruction
///     MSE of x(t)), ``"a"`` (trace of the posterior score covariance) or
///     ``"d"`` (its log-determinant).
///
/// Returns
/// -------
/// float
///     Criterion value (smaller is better; non-increasing as points are
///     added). The empty design gives ``sum(eigenvalues)`` for
///     trajectory / A and ``sum(log(eigenvalues))`` for D.
///
/// Raises
/// ------
/// ValueError
///     For a negative or out-of-range index or an unknown criterion.
#[pyfunction]
#[pyo3(signature = (model, selected, criterion="trajectory"))]
pub fn design_criterion(
    model: &PyPaceFpcaFit,
    selected: PyArrayLike1<'_, i64, AllowTypeChange>,
    criterion: &str,
) -> PyResult<f64> {
    let crit = design_criterion_from_str(criterion)?;
    let sel = nonneg_labels(&selected, "selected")?;
    to_pyresult(fdars_core::optimal_design::design_criterion(
        &model.inner,
        &sel,
        crit,
    ))
}

/// Greedy optimal design: choose the work-grid points that best reduce a PACE criterion.
///
/// Sequential forward selection over the candidate points of a fitted PACE
/// model (read-only; no re-estimation), minimising `design_criterion` at
/// every step. Deterministic, ties go to the smallest grid index.
///
/// Parameters
/// ----------
/// model : PyPaceFpcaFit
///     Handle from `pace_fpca_fit`.
/// budget : int, optional
///     Number of points to select (default 1), <= number of distinct candidates.
/// candidate_grid : array-like, optional
///     Candidate time points, each on ``model.argvals`` within 1e-9;
///     None (default) uses all of ``model.argvals``.
/// criterion : str, optional
///     ``"trajectory"`` (default), ``"a"`` or ``"d"`` (see `design_criterion`).
///
/// Returns
/// -------
/// dict
///     ``selected_indices`` (int, selection order, distinct),
///     ``selected_argvals`` and ``criterion_trace`` (criterion after each
///     step, non-increasing), each of length ``budget``.
///
/// Raises
/// ------
/// ValueError
///     For ``budget == 0``, a budget above the distinct candidate count, an
///     off-grid candidate or an unknown criterion.
#[pyfunction]
#[pyo3(signature = (model, budget=1, candidate_grid=None, criterion="trajectory"))]
pub fn optimal_design<'py>(
    py: Python<'py>,
    model: &PyPaceFpcaFit,
    budget: usize,
    candidate_grid: Option<Vec<f64>>,
    criterion: &str,
) -> PyResult<Bound<'py, PyDict>> {
    let config = OptDesConfig {
        candidate_grid: candidate_grid.unwrap_or_else(|| model.inner.argvals.clone()),
        budget,
        criterion: design_criterion_from_str(criterion)?,
    };
    let r = to_pyresult(fdars_core::optimal_design::optimal_design(
        &model.inner,
        &config,
    ))?;
    let dict = PyDict::new(py);
    dict.set_item(
        "selected_indices",
        usize_vec_to_numpy1d(py, r.selected_indices),
    )?;
    dict.set_item("selected_argvals", vec_to_numpy1d(py, r.selected_argvals))?;
    dict.set_item("criterion_trace", vec_to_numpy1d(py, r.criterion_trace))?;
    Ok(dict)
}

// ---------------------------------------------------------------------------
// Module registration
// ---------------------------------------------------------------------------

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyIrregFdata>()?;
    m.add_function(wrap_pyfunction!(irreg_fdata_from_lists, m)?)?;
    m.add_function(wrap_pyfunction!(run_pace_fpca, m)?)?;
    m.add_class::<PyPaceFpcaFit>()?;
    m.add_function(wrap_pyfunction!(pace_fpca_fit, m)?)?;
    m.add_function(wrap_pyfunction!(design_criterion, m)?)?;
    m.add_function(wrap_pyfunction!(optimal_design, m)?)?;
    Ok(())
}
