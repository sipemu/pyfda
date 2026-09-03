//! Functional Additive Mixed-Model (FAMM) bindings.
//!
//! Exposes `fdars.famm` with three functions from fdars-core 0.33's `famm` module:
//!
//! - `dense_flmm` — REML-EM functional linear mixed model; returns 14-key PyDict.
//! - `fast_fmm`   — fast functional mixed model (Wald inference); returns 6-key PyDict.
//! - `multi_famm` — multi-variable FAMM (list of 2-D arrays); returns 4-key PyDict.
//!
//! # fdars-core 0.33 — Plain FdMatrix Inputs Only
//!
//! None of the three FAMM functions accept `MultiFunData`.  All take plain
//! `FdMatrix` (or `&[FdMatrix]` for `multi_famm`) plus a subject-ID slice and an
//! optional covariate matrix.  `PyMultiFunData` must NOT be passed here.
//! MULTI-02 phrase "consume PyMultiFunData where required" is vacuously satisfied:
//! no 0.33 FAMM function requires it.

use crate::convert::{
    fdmatrix_to_numpy2d, numpy1d_to_usize_vec, numpy2d_to_fdmatrix, to_pyresult, vec_to_numpy1d,
};
use numpy::{PyReadonlyArray1, PyReadonlyArray2};
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};

// ---------------------------------------------------------------------------
// Private helper: DenseFlmmResult → PyDict  (reused by multi_famm for each
// per-dimension component dict)
// ---------------------------------------------------------------------------

fn dense_flmm_result_to_pydict<'py>(
    py: Python<'py>,
    r: fdars_core::famm::DenseFlmmResult,
) -> PyResult<Bound<'py, PyDict>> {
    let dict = PyDict::new(py);
    // --- scalar fields ---
    dict.set_item("sigma2_eps", r.sigma2_eps)?;
    dict.set_item("ncomp", r.ncomp)?;
    dict.set_item("n_subjects", r.n_subjects)?;
    dict.set_item("n_iter", r.n_iter)?;
    dict.set_item("converged", r.converged)?;
    // --- 1-D array fields ---
    dict.set_item("mean_function", vec_to_numpy1d(py, r.mean_function))?;
    dict.set_item("random_variance", vec_to_numpy1d(py, r.random_variance))?;
    dict.set_item("sigma2_u", vec_to_numpy1d(py, r.sigma2_u))?;
    dict.set_item("sigma2_slope", vec_to_numpy1d(py, r.sigma2_slope))?;
    dict.set_item("eigenvalues", vec_to_numpy1d(py, r.eigenvalues))?;
    // --- 2-D array fields (FdMatrix) ---
    dict.set_item("beta_functions", fdmatrix_to_numpy2d(py, &r.beta_functions))?;
    dict.set_item("random_effects", fdmatrix_to_numpy2d(py, &r.random_effects))?;
    dict.set_item("fitted", fdmatrix_to_numpy2d(py, &r.fitted))?;
    dict.set_item("residuals", fdmatrix_to_numpy2d(py, &r.residuals))?;
    Ok(dict)
}

// ---------------------------------------------------------------------------
// dense_flmm
// ---------------------------------------------------------------------------

/// Fit a Functional Linear Mixed Model (FLMM) via REML-EM.
///
/// Parameters
/// ----------
/// data : numpy.ndarray, shape (n_total, m)
///     Observed curves; rows are individual visits/measurements, columns are
///     evaluation-grid points.  ``n_total = n_subjects * n_visits`` (balanced)
///     or variable per subject (unbalanced).
/// subject_ids : numpy.ndarray, shape (n_total,), dtype int64
///     Curve-to-subject mapping.  ``subject_ids[i]`` is the subject index (0-based)
///     for curve ``i``.
/// covariates : numpy.ndarray, shape (n_total, p), optional
///     Fixed-effect covariate matrix (one row per observation).  Pass ``None``
///     (default) when there are no covariates (``p = 0``).
/// ncomp : int, optional
///     Number of functional principal components for the random-effect basis
///     (default 3).
/// max_iter : int, optional
///     Maximum REML-EM iterations (default 50).
/// tol : float, optional
///     Convergence tolerance on the relative change in log-likelihood (default 1e-10).
///
/// Returns
/// -------
/// dict
///     mean_function (m,), beta_functions (p, m), random_effects (n_subjects, m),
///     fitted (n_total, m), residuals (n_total, m), random_variance (m,),
///     sigma2_eps (float), sigma2_u (ncomp,), sigma2_slope (ncomp,),
///     eigenvalues (ncomp,), ncomp (int), n_subjects (int), n_iter (int),
///     converged (bool).
///
/// Raises
/// ------
/// ValueError
///     If dimensions are inconsistent, ``random_slopes=True`` is attempted
///     (not yet implemented in fdars-core 0.33), or convergence fails fatally.
#[pyfunction]
#[pyo3(signature = (data, subject_ids, covariates=None, ncomp=3, max_iter=50, tol=1e-10))]
pub fn dense_flmm<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    subject_ids: PyReadonlyArray1<'py, i64>,
    covariates: Option<PyReadonlyArray2<'py, f64>>,
    ncomp: usize,
    max_iter: usize,
    tol: f64,
) -> PyResult<Bound<'py, PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let sids = numpy1d_to_usize_vec(subject_ids);
    let cov: Option<fdars_core::matrix::FdMatrix> = covariates
        .map(numpy2d_to_fdmatrix)
        .transpose()?;

    let mut config = fdars_core::famm::DenseFlmmConfig::default();
    config.ncomp = ncomp;
    config.max_iter = max_iter;
    config.tol = tol;

    let result = to_pyresult(fdars_core::famm::dense_flmm(
        &mat,
        &sids,
        cov.as_ref(),
        &config,
    ))?;
    dense_flmm_result_to_pydict(py, result)
}

// ---------------------------------------------------------------------------
// fast_fmm
// ---------------------------------------------------------------------------

/// Fit a fast Functional Mixed Model (FMM) with optional Wald inference.
///
/// Parameters
/// ----------
/// data : numpy.ndarray, shape (n_total, m)
///     Observed curves; rows are observations, columns are grid points.
/// subject_ids : numpy.ndarray, shape (n_total,), dtype int64
///     Curve-to-subject mapping (0-based).
/// covariates : numpy.ndarray, shape (n_total, p), optional
///     Fixed-effect covariate matrix.  When ``None`` (default), ``p = 0`` and
///     ``beta_matrix``, ``t_stats``, ``p_values`` are all shape ``(0, m)``.
/// smooth_window : int, optional
///     Bartlett smoothing window for local variance estimation (default 3;
///     ``1`` = no smoothing; must be ≥ 1).
/// max_iter : int, optional
///     Maximum iterations (default 30; must be ≥ 1).
/// tol : float, optional
///     Convergence tolerance (default 1e-8).
/// compute_inference : bool, optional
///     Whether to compute Wald t-statistics and p-values (default ``True``).
///     When ``False``, ``t_stats`` is zero-filled and ``p_values`` is one-filled.
///
/// Returns
/// -------
/// dict
///     beta_matrix (p, m), t_stats (p, m), p_values (p, m),
///     sigma2_eps (m,), sigma2_u (m,), n_grid (int).
///
/// Raises
/// ------
/// ValueError
///     If dimensions are inconsistent or ``smooth_window < 1`` / ``max_iter < 1``.
#[pyfunction]
#[pyo3(signature = (data, subject_ids, covariates=None, smooth_window=3, max_iter=30, tol=1e-8, compute_inference=true))]
pub fn fast_fmm<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    subject_ids: PyReadonlyArray1<'py, i64>,
    covariates: Option<PyReadonlyArray2<'py, f64>>,
    smooth_window: usize,
    max_iter: usize,
    tol: f64,
    compute_inference: bool,
) -> PyResult<Bound<'py, PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let sids = numpy1d_to_usize_vec(subject_ids);
    let cov: Option<fdars_core::matrix::FdMatrix> = covariates
        .map(numpy2d_to_fdmatrix)
        .transpose()?;

    let mut config = fdars_core::famm::FastFmmConfig::default();
    config.smooth_window = smooth_window;
    config.max_iter = max_iter;
    config.tol = tol;
    config.compute_inference = compute_inference;

    let result = to_pyresult(fdars_core::famm::fast_fmm(
        &mat,
        &sids,
        cov.as_ref(),
        &config,
    ))?;

    let dict = PyDict::new(py);
    dict.set_item("beta_matrix", fdmatrix_to_numpy2d(py, &result.beta_matrix))?;
    dict.set_item("t_stats", fdmatrix_to_numpy2d(py, &result.t_stats))?;
    dict.set_item("p_values", fdmatrix_to_numpy2d(py, &result.p_values))?;
    dict.set_item("sigma2_eps", vec_to_numpy1d(py, result.sigma2_eps))?;
    dict.set_item("sigma2_u", vec_to_numpy1d(py, result.sigma2_u))?;
    dict.set_item("n_grid", result.n_grid)?;
    Ok(dict)
}

// ---------------------------------------------------------------------------
// multi_famm
// ---------------------------------------------------------------------------

/// Fit a multi-variable Functional Additive Mixed Model (multiFAMM).
///
/// Jointly models multiple functional variables observed on potentially different
/// grids, sharing the same subject-ID structure.  Internally runs ``dense_flmm``
/// per dimension and returns a compact summary.
///
/// Parameters
/// ----------
/// data_list : list of numpy.ndarray, each shape (n_total, m)
///     One 2-D numpy array per functional variable/domain.  All arrays must share
///     the same number of columns (``m``) and the same number of rows (``n_total``).
/// subject_ids : numpy.ndarray, shape (n_total,), dtype int64
///     Curve-to-subject mapping (0-based), shared across all variables.
/// covariates : numpy.ndarray, shape (n_total, p), optional
///     Fixed-effect covariate matrix (shared across variables).
/// ncomp : int, optional
///     Number of FPC components per variable (default 3).
/// max_iter : int, optional
///     Maximum REML-EM iterations per variable (default 50).
/// tol : float, optional
///     Convergence tolerance (default 1e-10).
///
/// Returns
/// -------
/// dict
///     n_dims (int), stacked_fitted (n_total*n_dims, m),
///     stacked_residuals (n_total*n_dims, m),
///     components (list of dict) — each dict has the same 14 keys as ``dense_flmm``.
///
/// Raises
/// ------
/// ValueError
///     If any element of ``data_list`` is not a 2-D float64 array, if columns
///     differ across variables, or if fdars-core raises a dimension error.
#[pyfunction]
#[pyo3(signature = (data_list, subject_ids, covariates=None, ncomp=3, max_iter=50, tol=1e-10))]
pub fn multi_famm<'py>(
    py: Python<'py>,
    data_list: &Bound<'py, PyList>,
    subject_ids: PyReadonlyArray1<'py, i64>,
    covariates: Option<PyReadonlyArray2<'py, f64>>,
    ncomp: usize,
    max_iter: usize,
    tol: f64,
) -> PyResult<Bound<'py, PyDict>> {
    // Build Vec<FdMatrix> from the Python list of 2-D arrays.
    let mats: Vec<fdars_core::matrix::FdMatrix> = data_list
        .iter()
        .enumerate()
        .map(|(i, item)| {
            let arr = item
                .extract::<PyReadonlyArray2<f64>>()
                .map_err(|_| {
                    pyo3::exceptions::PyValueError::new_err(format!(
                        "multi_famm: data_list[{i}] must be a 2-D numpy array of dtype float64"
                    ))
                })?;
            numpy2d_to_fdmatrix(arr)
        })
        .collect::<PyResult<Vec<_>>>()?;

    let sids = numpy1d_to_usize_vec(subject_ids);
    let cov: Option<fdars_core::matrix::FdMatrix> = covariates
        .map(numpy2d_to_fdmatrix)
        .transpose()?;

    let mut config = fdars_core::famm::MultiFammConfig::default();
    config.ncomp = ncomp;
    config.max_iter = max_iter;
    config.tol = tol;

    let result = to_pyresult(fdars_core::famm::multi_famm(
        mats.as_slice(),
        &sids,
        cov.as_ref(),
        &config,
    ))?;

    // Build the per-dimension component list using the shared helper.
    let components_list = PyList::empty(py);
    for comp in result.components {
        let comp_dict = dense_flmm_result_to_pydict(py, comp)?;
        components_list.append(comp_dict)?;
    }

    let dict = PyDict::new(py);
    dict.set_item("n_dims", result.n_dims)?;
    dict.set_item("stacked_fitted", fdmatrix_to_numpy2d(py, &result.stacked_fitted))?;
    dict.set_item(
        "stacked_residuals",
        fdmatrix_to_numpy2d(py, &result.stacked_residuals),
    )?;
    dict.set_item("components", components_list)?;
    Ok(dict)
}

// ---------------------------------------------------------------------------
// Module registration
// ---------------------------------------------------------------------------

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(dense_flmm, m)?)?;
    m.add_function(wrap_pyfunction!(fast_fmm, m)?)?;
    m.add_function(wrap_pyfunction!(multi_famm, m)?)?;
    Ok(())
}
