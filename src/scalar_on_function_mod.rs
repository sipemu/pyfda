//! Scalar-on-function additive and variable selection regression bindings.
//!
//! Exposes the `fdars.scalar_on_function` submodule with bindings for fdars-core 0.33's
//! scalar_on_function module: FAM, GKAM, GSAM additive models, variable selection,
//! and model selection via information criteria.
//!
//! Plan 68-03 (tracer): `fam` bound.
//! Plan 68-03 expanded: `fregre_gkam`, `fregre_gsam`, `variable_selection`,
//!                      `model_selection_ncomp` added.

use crate::convert::*;
use numpy::{PyReadonlyArray1, PyReadonlyArray2};
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};

// ---------------------------------------------------------------------------
// Helper: penalty string → VarSelectPenalty enum
// ---------------------------------------------------------------------------

/// Convert a penalty string to a `VarSelectPenalty` enum variant.
///
/// `VarSelectPenalty` is `#[non_exhaustive]` so a wildcard arm is mandatory.
/// `GroupMcp` and `GroupScad` are proactively rejected here with a clear
/// message because they raise `FdarError::InvalidParameter` upstream anyway.
fn penalty_from_str(
    s: &str,
) -> PyResult<fdars_core::scalar_on_function::VarSelectPenalty> {
    use fdars_core::scalar_on_function::VarSelectPenalty;
    match s {
        "group_lasso" => Ok(VarSelectPenalty::GroupLasso),
        "ls" => Ok(VarSelectPenalty::Ls),
        _ => Err(pyo3::exceptions::PyValueError::new_err(format!(
            "penalty must be 'group_lasso' or 'ls', got '{s}' \
             (GroupMcp/GroupScad not yet implemented upstream)"
        ))),
    }
}

// ---------------------------------------------------------------------------
// fam — Functional Additive Model (single functional predictor)
// ---------------------------------------------------------------------------

/// Fit a Functional Additive Model (FAM) with a single functional predictor.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Functional predictor, shape (n, m).
/// y : numpy.ndarray
///     Scalar response, length n.
/// argvals : numpy.ndarray
///     Evaluation grid, length m.
/// scalar_covariates : numpy.ndarray, optional
///     Optional scalar covariates, shape (n, q). Default None.
/// ncomp : int, optional
///     Number of FPC components (0 = auto via GCV). Default 0.
/// bandwidth : float, optional
///     Bandwidth (0.0 = auto per component via GCV). Default 0.0.
/// kernel : str, optional
///     Kernel function: "gaussian", "epanechnikov", "tricube". Default "gaussian".
/// n_grid_bandwidth : int, optional
///     Number of bandwidth grid points for optimisation. Default 20.
///
/// Returns
/// -------
/// dict
///     fitted_values (n,), residuals (n,), component_fits (list of 1D arrays),
///     intercept (float), bandwidths (ncomp,), ncomp (int), r_squared (float).
///
/// Raises
/// ------
/// ValueError
///     If dimensions are inconsistent or the fit fails.
#[pyfunction]
#[pyo3(signature = (data, y, argvals, scalar_covariates=None, ncomp=0, bandwidth=0.0, kernel="gaussian", n_grid_bandwidth=20))]
pub fn fam<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    y: PyReadonlyArray1<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    scalar_covariates: Option<PyReadonlyArray2<'py, f64>>,
    ncomp: usize,
    bandwidth: f64,
    kernel: &str,
    n_grid_bandwidth: usize,
) -> PyResult<Bound<'py, PyAny>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let y_vec = numpy1d_to_vec(y);
    let av = numpy1d_to_vec(argvals);
    let sc = scalar_covariates.map(numpy2d_to_fdmatrix).transpose()?;

    let mut cfg = fdars_core::scalar_on_function::FamConfig::default();
    cfg.ncomp = ncomp;
    cfg.bandwidth = bandwidth;
    cfg.kernel = kernel.to_string();
    cfg.n_grid_bandwidth = n_grid_bandwidth;

    let result = to_pyresult(fdars_core::scalar_on_function::fam(
        &mat,
        &y_vec,
        &av,
        sc.as_ref(),
        &cfg,
    ))?;

    let dict = PyDict::new(py);
    dict.set_item("fitted_values", vec_to_numpy1d(py, result.fitted_values))?;
    dict.set_item("residuals", vec_to_numpy1d(py, result.residuals))?;
    let cf_list = PyList::empty(py);
    for cf in result.component_fits {
        cf_list.append(vec_to_numpy1d(py, cf))?;
    }
    dict.set_item("component_fits", cf_list)?;
    dict.set_item("intercept", result.intercept)?;
    dict.set_item("bandwidths", vec_to_numpy1d(py, result.bandwidths))?;
    dict.set_item("ncomp", result.ncomp)?;
    dict.set_item("r_squared", result.r_squared)?;
    Ok(dict.into_any())
}

// ---------------------------------------------------------------------------
// fregre_gsam — Generalised Structured Additive Model (single predictor)
// ---------------------------------------------------------------------------

/// Fit a Generalised Structured Additive Model (GSAM) with a single functional predictor.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Functional predictor, shape (n, m).
/// y : numpy.ndarray
///     Scalar response, length n.
/// argvals : numpy.ndarray
///     Evaluation grid, length m.
/// scalar_covariates : numpy.ndarray, optional
///     Optional scalar covariates, shape (n, q). Default None.
/// ncomp : int, optional
///     Number of FPC components (0 = auto via GCV). Default 0.
/// bandwidth : float, optional
///     Bandwidth (0.0 = auto per component via GCV). Default 0.0.
/// kernel : str, optional
///     Kernel function: "gaussian", "epanechnikov", "tricube". Default "gaussian".
/// n_grid_bandwidth : int, optional
///     Number of bandwidth grid points for optimisation. Default 20.
///
/// Returns
/// -------
/// dict
///     fitted_values (n,), residuals (n,), component_fits (list of 1D arrays),
///     intercept (float), bandwidths (ncomp,), ncomp (int), r_squared (float).
///
/// Raises
/// ------
/// ValueError
///     If dimensions are inconsistent or the fit fails.
#[pyfunction]
#[pyo3(signature = (data, y, argvals, scalar_covariates=None, ncomp=0, bandwidth=0.0, kernel="gaussian", n_grid_bandwidth=20))]
pub fn fregre_gsam<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    y: PyReadonlyArray1<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    scalar_covariates: Option<PyReadonlyArray2<'py, f64>>,
    ncomp: usize,
    bandwidth: f64,
    kernel: &str,
    n_grid_bandwidth: usize,
) -> PyResult<Bound<'py, PyAny>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let y_vec = numpy1d_to_vec(y);
    let av = numpy1d_to_vec(argvals);
    let sc = scalar_covariates.map(numpy2d_to_fdmatrix).transpose()?;

    let mut cfg = fdars_core::scalar_on_function::GsamConfig::default();
    cfg.ncomp = ncomp;
    cfg.bandwidth = bandwidth;
    cfg.kernel = kernel.to_string();
    cfg.n_grid_bandwidth = n_grid_bandwidth;

    let result = to_pyresult(fdars_core::scalar_on_function::fregre_gsam(
        &mat,
        &y_vec,
        &av,
        sc.as_ref(),
        &cfg,
    ))?;

    let dict = PyDict::new(py);
    dict.set_item("fitted_values", vec_to_numpy1d(py, result.fitted_values))?;
    dict.set_item("residuals", vec_to_numpy1d(py, result.residuals))?;
    let cf_list = PyList::empty(py);
    for cf in result.component_fits {
        cf_list.append(vec_to_numpy1d(py, cf))?;
    }
    dict.set_item("component_fits", cf_list)?;
    dict.set_item("intercept", result.intercept)?;
    dict.set_item("bandwidths", vec_to_numpy1d(py, result.bandwidths))?;
    dict.set_item("ncomp", result.ncomp)?;
    dict.set_item("r_squared", result.r_squared)?;
    Ok(dict.into_any())
}

// ---------------------------------------------------------------------------
// fregre_gkam — Generalised Kernel Additive Model (multi-predictor)
// ---------------------------------------------------------------------------

/// Fit a Generalised Kernel Additive Model (GKAM) with multiple functional predictors.
///
/// Parameters
/// ----------
/// predictors : list of numpy.ndarray
///     List of P functional predictor matrices, each shape (n, m_p).
/// y : numpy.ndarray
///     Scalar response, length n.
/// argvals_list : list of numpy.ndarray
///     List of P evaluation grids, one per predictor.
/// scalar_covariates : numpy.ndarray, optional
///     Optional scalar covariates, shape (n, q). Default None.
/// bandwidth : float, optional
///     Bandwidth (0.0 = auto via LOO-CV). Default 0.0.
/// kernel : str, optional
///     Kernel function. Default "gaussian".
/// max_iter : int, optional
///     Maximum backfitting iterations. Default 50.
/// epsilon : float, optional
///     Convergence threshold. Default 1e-6.
///
/// Returns
/// -------
/// dict
///     fitted_values (n,), residuals (n,), component_fits (list of 1D arrays),
///     intercept (float), bandwidths (P,), iterations (int), converged (bool),
///     r_squared (float).
///
/// Raises
/// ------
/// ValueError
///     If dimensions are inconsistent or the fit fails.
#[pyfunction]
#[pyo3(signature = (predictors, y, argvals_list, scalar_covariates=None, bandwidth=0.0, kernel="gaussian", max_iter=50, epsilon=1e-6))]
pub fn fregre_gkam<'py>(
    py: Python<'py>,
    predictors: Vec<PyReadonlyArray2<'py, f64>>,
    y: PyReadonlyArray1<'py, f64>,
    argvals_list: Vec<PyReadonlyArray1<'py, f64>>,
    scalar_covariates: Option<PyReadonlyArray2<'py, f64>>,
    bandwidth: f64,
    kernel: &str,
    max_iter: usize,
    epsilon: f64,
) -> PyResult<Bound<'py, PyAny>> {
    let pred_mats: Vec<fdars_core::matrix::FdMatrix> = predictors
        .into_iter()
        .map(numpy2d_to_fdmatrix)
        .collect::<PyResult<Vec<_>>>()?;
    let pred_refs: Vec<&fdars_core::matrix::FdMatrix> = pred_mats.iter().collect();

    let y_vec = numpy1d_to_vec(y);

    let argvals_vecs: Vec<Vec<f64>> = argvals_list.into_iter().map(numpy1d_to_vec).collect();
    let argvals_refs: Vec<&[f64]> = argvals_vecs.iter().map(|v| v.as_slice()).collect();

    let sc = scalar_covariates.map(numpy2d_to_fdmatrix).transpose()?;

    let mut cfg = fdars_core::scalar_on_function::GkamConfig::default();
    cfg.bandwidth = bandwidth;
    cfg.kernel = kernel.to_string();
    cfg.max_iter = max_iter;
    cfg.epsilon = epsilon;

    let result = to_pyresult(fdars_core::scalar_on_function::fregre_gkam(
        &pred_refs,
        &y_vec,
        &argvals_refs,
        sc.as_ref(),
        &cfg,
    ))?;

    let dict = PyDict::new(py);
    dict.set_item("fitted_values", vec_to_numpy1d(py, result.fitted_values))?;
    dict.set_item("residuals", vec_to_numpy1d(py, result.residuals))?;
    let cf_list = PyList::empty(py);
    for cf in result.component_fits {
        cf_list.append(vec_to_numpy1d(py, cf))?;
    }
    dict.set_item("component_fits", cf_list)?;
    dict.set_item("intercept", result.intercept)?;
    dict.set_item("bandwidths", vec_to_numpy1d(py, result.bandwidths))?;
    dict.set_item("iterations", result.iterations)?;
    dict.set_item("converged", result.converged)?;
    dict.set_item("r_squared", result.r_squared)?;
    Ok(dict.into_any())
}

// ---------------------------------------------------------------------------
// variable_selection — Group-lasso variable selection (multi-predictor)
// ---------------------------------------------------------------------------

/// Functional variable selection via group-lasso penalised regression.
///
/// Parameters
/// ----------
/// predictors : list of numpy.ndarray
///     List of P functional predictor matrices, each shape (n, m_p).
/// y : numpy.ndarray
///     Scalar response, length n.
/// argvals_list : list of numpy.ndarray
///     List of P evaluation grids, one per predictor.
/// scalar_covariates : numpy.ndarray, optional
///     Optional scalar covariates, shape (n, q). Default None.
/// ncomp : int, optional
///     Number of FPC components per predictor (0 = auto via GCV). Default 3.
/// penalty : str, optional
///     Penalty type: "group_lasso" (default) or "ls" (no penalty / OLS).
///     "group_mcp" and "group_scad" are not yet implemented upstream.
/// lambda_ : float, optional
///     Regularisation strength (0.0 = CV-select over grid). Default 0.0.
/// max_iter : int, optional
///     Coordinate-descent maximum iterations. Default 100.
/// epsilon : float, optional
///     Convergence threshold. Default 1e-5.
/// lambda_n_grid : int, optional
///     Grid size for lambda selection. Default 20.
///
/// Returns
/// -------
/// dict
///     active_predictors (bool array, P,), coefficients (list of 1D arrays),
///     fitted_values (n,), residuals (n,), intercept (float), lambda (float),
///     r_squared (float), iterations (int), converged (bool).
///
/// Raises
/// ------
/// ValueError
///     If penalty string is invalid, dimensions are inconsistent, or the fit fails.
#[pyfunction]
#[pyo3(signature = (predictors, y, argvals_list, scalar_covariates=None, ncomp=3, penalty="group_lasso", lambda_=0.0, max_iter=100, epsilon=1e-5, lambda_n_grid=20))]
pub fn variable_selection<'py>(
    py: Python<'py>,
    predictors: Vec<PyReadonlyArray2<'py, f64>>,
    y: PyReadonlyArray1<'py, f64>,
    argvals_list: Vec<PyReadonlyArray1<'py, f64>>,
    scalar_covariates: Option<PyReadonlyArray2<'py, f64>>,
    ncomp: usize,
    penalty: &str,
    lambda_: f64,
    max_iter: usize,
    epsilon: f64,
    lambda_n_grid: usize,
) -> PyResult<Bound<'py, PyAny>> {
    let pred_mats: Vec<fdars_core::matrix::FdMatrix> = predictors
        .into_iter()
        .map(numpy2d_to_fdmatrix)
        .collect::<PyResult<Vec<_>>>()?;
    let pred_refs: Vec<&fdars_core::matrix::FdMatrix> = pred_mats.iter().collect();

    let y_vec = numpy1d_to_vec(y);

    let argvals_vecs: Vec<Vec<f64>> = argvals_list.into_iter().map(numpy1d_to_vec).collect();
    let argvals_refs: Vec<&[f64]> = argvals_vecs.iter().map(|v| v.as_slice()).collect();

    let sc = scalar_covariates.map(numpy2d_to_fdmatrix).transpose()?;

    let mut cfg = fdars_core::scalar_on_function::VarSelectConfig::default();
    cfg.ncomp = ncomp;
    cfg.penalty = penalty_from_str(penalty)?;
    cfg.lambda = lambda_;
    cfg.max_iter = max_iter;
    cfg.epsilon = epsilon;
    cfg.lambda_n_grid = lambda_n_grid;

    let result = to_pyresult(fdars_core::scalar_on_function::variable_selection(
        &pred_refs,
        &y_vec,
        &argvals_refs,
        sc.as_ref(),
        &cfg,
    ))?;

    let dict = PyDict::new(py);
    dict.set_item(
        "active_predictors",
        bool_vec_to_numpy1d(py, result.active_predictors),
    )?;
    let coef_list = PyList::empty(py);
    for c in result.coefficients {
        coef_list.append(vec_to_numpy1d(py, c))?;
    }
    dict.set_item("coefficients", coef_list)?;
    dict.set_item("fitted_values", vec_to_numpy1d(py, result.fitted_values))?;
    dict.set_item("residuals", vec_to_numpy1d(py, result.residuals))?;
    dict.set_item("intercept", result.intercept)?;
    dict.set_item("lambda", result.lambda)?;
    dict.set_item("r_squared", result.r_squared)?;
    dict.set_item("iterations", result.iterations)?;
    dict.set_item("converged", result.converged)?;
    Ok(dict.into_any())
}

// ---------------------------------------------------------------------------
// model_selection_ncomp — Select number of FPC components via AIC/BIC/GCV
// (copied verbatim from regression_mod.rs — second registration in sof submodule)
// ---------------------------------------------------------------------------

/// Select the optimal number of FPC components for scalar-on-function regression.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Functional predictor, shape (n, m).
/// response : numpy.ndarray
///     Scalar response, length n.
/// max_comp : int, optional
///     Maximum number of components to evaluate. Default 10.
/// criterion : str, optional
///     Selection criterion: "aic", "bic", or "gcv" (default).
///
/// Returns
/// -------
/// dict
///     best_ncomp (int), criteria (list of (ncomp, aic, bic, gcv) tuples).
#[pyfunction]
#[pyo3(signature = (data, response, max_comp=10, criterion="gcv"))]
pub fn model_selection_ncomp<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    response: PyReadonlyArray1<'py, f64>,
    max_comp: usize,
    criterion: &str,
) -> PyResult<Bound<'py, PyAny>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let resp = numpy1d_to_vec(response);
    let crit = match criterion {
        "aic" => fdars_core::scalar_on_function::SelectionCriterion::Aic,
        "bic" => fdars_core::scalar_on_function::SelectionCriterion::Bic,
        _ => fdars_core::scalar_on_function::SelectionCriterion::Gcv,
    };
    let result = to_pyresult(fdars_core::scalar_on_function::model_selection_ncomp(
        &mat, &resp, None, max_comp, crit,
    ))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("best_ncomp", result.best_ncomp)?;
    // criteria is Vec<(usize, f64, f64, f64)> - convert to Python list of tuples
    let criteria_list: Vec<(usize, f64, f64, f64)> = result.criteria;
    dict.set_item("criteria", criteria_list)?;
    Ok(dict.into_any())
}

// ---------------------------------------------------------------------------
// Module registration
// ---------------------------------------------------------------------------

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(fam, m)?)?;
    m.add_function(wrap_pyfunction!(fregre_gkam, m)?)?;
    m.add_function(wrap_pyfunction!(fregre_gsam, m)?)?;
    m.add_function(wrap_pyfunction!(variable_selection, m)?)?;
    m.add_function(wrap_pyfunction!(model_selection_ncomp, m)?)?;
    Ok(())
}
