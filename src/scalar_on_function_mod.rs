//! Scalar-on-function additive and variable selection regression bindings.
//!
//! Exposes the `fdars.scalar_on_function` submodule with bindings for fdars-core 0.33's
//! scalar_on_function module: FAM, GKAM, GSAM additive models, variable selection,
//! and model selection via information criteria.
//!
//! Plan 68-03 (tracer): `fam` bound.
//! Plan 68-03 expanded: `fregre_gkam`, `fregre_gsam`, `variable_selection`,
//!                      `model_selection_ncomp` added.
//! fdars-core 0.48: PEER / LPEER structured-penalty regression and the
//!                  wavelet-domain WCR / WNET regressors.

use crate::convert::*;
use crate::options::{boundary_mode, boundary_mode_name, wavelet_family, wavelet_family_name};
use fdars_core::peer::{
    LambdaChoice, LambdaMethod, LocalPeerResult, PeerConfig, PeerPenalty, PeerResult,
};
use fdars_core::wavelet::regression::{WcrConfig, WcrMethod, WcrResult, WnetConfig, WnetResult};
use numpy::{AllowTypeChange, PyArray1, PyArrayLike1, PyReadonlyArray1, PyReadonlyArray2};
use pyo3::exceptions::PyValueError;
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
fn penalty_from_str(s: &str) -> PyResult<fdars_core::scalar_on_function::VarSelectPenalty> {
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
// PEER / LPEER — structured-penalty scalar-on-function regression
// ---------------------------------------------------------------------------

fn peer_config(
    penalty: &str,
    decree_q: Option<PyReadonlyArray2<'_, f64>>,
    lambda: Option<&Bound<'_, PyAny>>,
) -> PyResult<PeerConfig> {
    let mut cfg = PeerConfig::default();
    cfg.penalty = match (penalty, decree_q) {
        ("ridge", None) => PeerPenalty::Ridge,
        ("difference", None) => PeerPenalty::Difference { order: 2 },
        ("decree", Some(q)) => {
            let q = q.as_array();
            let (r, c) = q.dim();
            if r != c {
                return Err(PyValueError::new_err(format!(
                    "decree_q must be a square (m, m) array, got ({r}, {c})"
                )));
            }
            PeerPenalty::Decree(q.iter().copied().collect(), r)
        }
        ("decree", None) => {
            return Err(PyValueError::new_err(
                "penalty='decree' requires decree_q, an (m, m) symmetric PSD array",
            ))
        }
        ("ridge" | "difference", Some(_)) => {
            return Err(PyValueError::new_err(
                "decree_q is only used with penalty='decree'",
            ))
        }
        (other, _) => {
            return Err(PyValueError::new_err(format!(
                "penalty must be one of 'ridge', 'difference', 'decree', got '{other}'"
            )))
        }
    };
    cfg.lambda = match lambda {
        None => LambdaChoice::Gcv,
        Some(obj) => {
            if let Ok(name) = obj.extract::<String>() {
                match name.as_str() {
                    "gcv" => LambdaChoice::Gcv,
                    "reml" => LambdaChoice::Reml,
                    _ => {
                        return Err(PyValueError::new_err(format!(
                            "lambda_ must be a float, 'gcv' or 'reml', got '{name}'"
                        )))
                    }
                }
            } else {
                let v: f64 = obj.extract().map_err(|_| {
                    PyValueError::new_err("lambda_ must be a float, 'gcv' or 'reml'")
                })?;
                if !v.is_finite() || v < 0.0 {
                    return Err(PyValueError::new_err(format!(
                        "lambda_ must be finite and >= 0, got {v}"
                    )));
                }
                LambdaChoice::Fixed(v)
            }
        }
    };
    Ok(cfg)
}

fn peer_penalty_name(p: &PeerPenalty) -> &'static str {
    match p {
        PeerPenalty::Ridge => "ridge",
        PeerPenalty::Decree(..) => "decree",
        _ => "difference",
    }
}

fn lambda_method_name(m: &LambdaMethod) -> &'static str {
    match m {
        LambdaMethod::Fixed => "fixed",
        LambdaMethod::Reml => "reml",
        _ => "gcv",
    }
}

/// Fitted PEER model (from `peer`); predicts scalar responses for new curves.
#[pyclass(name = "PyPeerFit")]
pub struct PyPeerFit {
    pub inner: PeerResult,
}

#[pymethods]
impl PyPeerFit {
    /// Estimated coefficient function beta(t), length m.
    #[getter]
    pub fn beta<'py>(&self, py: Python<'py>) -> Bound<'py, PyArray1<f64>> {
        vec_to_numpy1d(py, self.inner.beta.clone())
    }

    /// Intercept (mean of the training response).
    #[getter]
    pub fn intercept(&self) -> f64 {
        self.inner.intercept
    }

    /// Smoothing parameter the model was fitted with.
    #[getter]
    pub fn lambda_(&self) -> f64 {
        self.inner.lambda
    }

    /// Predict scalar responses for new curves.
    ///
    /// Parameters
    /// ----------
    /// new_data : numpy.ndarray
    ///     Curves, shape (k, m), on the training grid.
    /// argvals : numpy.ndarray
    ///     Evaluation grid, length m.
    ///
    /// Returns
    /// -------
    /// numpy.ndarray
    ///     Predictions, length k. On the training curves these equal
    ///     ``fitted_values``.
    pub fn predict<'py>(
        &self,
        py: Python<'py>,
        new_data: PyReadonlyArray2<'py, f64>,
        argvals: PyReadonlyArray1<'py, f64>,
    ) -> PyResult<Bound<'py, PyArray1<f64>>> {
        let mat = numpy2d_to_fdmatrix(new_data)?;
        let av = numpy1d_to_vec(argvals);
        Ok(vec_to_numpy1d(
            py,
            to_pyresult(self.inner.predict(&mat, &av))?,
        ))
    }
}

/// Fitted longitudinal PEER model (from `lpeer`); marginal predictions for new curves.
#[pyclass(name = "PyLocalPeerFit")]
pub struct PyLocalPeerFit {
    pub inner: LocalPeerResult,
}

#[pymethods]
impl PyLocalPeerFit {
    /// Estimated coefficient function beta(t), length m.
    #[getter]
    pub fn beta<'py>(&self, py: Python<'py>) -> Bound<'py, PyArray1<f64>> {
        vec_to_numpy1d(py, self.inner.beta.clone())
    }

    /// Intercept (mean of the training response).
    #[getter]
    pub fn intercept(&self) -> f64 {
        self.inner.intercept
    }

    /// Smoothing parameter the model was fitted with.
    #[getter]
    pub fn lambda_(&self) -> f64 {
        self.inner.lambda
    }

    /// Marginal (fixed-effect only) predictions for new curves.
    ///
    /// Parameters
    /// ----------
    /// new_data : numpy.ndarray
    ///     Curves, shape (k, m), on the training grid.
    /// argvals : numpy.ndarray
    ///     Evaluation grid, length m.
    ///
    /// Returns
    /// -------
    /// numpy.ndarray
    ///     Predictions, length k (new-subject random effect = 0).
    pub fn predict<'py>(
        &self,
        py: Python<'py>,
        new_data: PyReadonlyArray2<'py, f64>,
        argvals: PyReadonlyArray1<'py, f64>,
    ) -> PyResult<Bound<'py, PyArray1<f64>>> {
        let mat = numpy2d_to_fdmatrix(new_data)?;
        let av = numpy1d_to_vec(argvals);
        Ok(vec_to_numpy1d(
            py,
            to_pyresult(self.inner.predict(&mat, &av))?,
        ))
    }
}

/// PEER structured-penalty scalar-on-function regression with GCV / REML / fixed lambda.
///
/// Solves the penalized normal equations ``(W_c'W_c + lambda Q) beta = W_c'y_c``
/// where ``W_c`` is the centred, Simpson-weighted design, so
/// ``y_i ~ intercept + integral x_i(t) beta(t) dt``.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Functional predictor, shape (n, m).
/// y : numpy.ndarray
///     Scalar response, length n.
/// argvals : numpy.ndarray
///     Evaluation grid, length m.
/// penalty : str, optional
///     ``"difference"`` (default; second-difference roughness D'D),
///     ``"ridge"`` (identity) or ``"decree"`` (user matrix ``decree_q``).
/// decree_q : numpy.ndarray, optional
///     Symmetric PSD penalty matrix, shape (m, m); required for
///     ``penalty="decree"`` and rejected otherwise.
/// lambda_ : float or str, optional
///     A fixed lambda >= 0, ``"gcv"`` (40-point log grid on [1e-6, 1e4]) or
///     ``"reml"`` (REML EM). None (default) means ``"gcv"``.
///
/// Returns
/// -------
/// dict
///     ``beta`` (m,), ``intercept``, ``w_bar`` (m,), ``fitted_values`` (n,),
///     ``effective_df``, ``lambda_``, ``penalty_type``, ``gcv`` (float, or None
///     unless GCV ran), ``lambda_method`` (``"fixed"|"gcv"|"reml"``) and
///     ``model`` (``PyPeerFit`` with ``predict(new_data, argvals)``).
///
/// Raises
/// ------
/// ValueError
///     For inconsistent dimensions, non-finite inputs, an unknown penalty or
///     lambda spec, or a numerically singular system.
#[pyfunction]
#[pyo3(signature = (data, y, argvals, penalty="difference", decree_q=None, lambda_=None))]
pub fn peer<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    y: PyReadonlyArray1<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    penalty: &str,
    decree_q: Option<PyReadonlyArray2<'py, f64>>,
    lambda_: Option<&Bound<'py, PyAny>>,
) -> PyResult<Bound<'py, PyDict>> {
    let cfg = peer_config(penalty, decree_q, lambda_)?;
    let mat = numpy2d_to_fdmatrix(data)?;
    let yv = numpy1d_to_vec(y);
    let av = numpy1d_to_vec(argvals);
    let r = to_pyresult(fdars_core::peer::peer(&mat, &yv, &av, &cfg))?;

    let dict = PyDict::new(py);
    dict.set_item("beta", vec_to_numpy1d(py, r.beta.clone()))?;
    dict.set_item("intercept", r.intercept)?;
    dict.set_item("w_bar", vec_to_numpy1d(py, r.w_bar.clone()))?;
    dict.set_item("fitted_values", vec_to_numpy1d(py, r.fitted_values.clone()))?;
    dict.set_item("effective_df", r.effective_df)?;
    dict.set_item("lambda_", r.lambda)?;
    dict.set_item("penalty_type", peer_penalty_name(&r.penalty_type))?;
    dict.set_item("gcv", r.gcv)?;
    dict.set_item("lambda_method", lambda_method_name(&r.lambda_method))?;
    dict.set_item("model", Py::new(py, PyPeerFit { inner: r })?)?;
    Ok(dict)
}

/// Longitudinal PEER: structured-penalty regression with a subject random intercept.
///
/// Fits ``y_ij = intercept + integral x_ij(t) beta(t) dt + u_i + e_ij`` with
/// ``u_i ~ N(0, sigma2_subject)``, ``e_ij ~ N(0, sigma2_resid)`` (REML on
/// FPC scores, then a penalized-GLS re-solve with the PEER penalty).
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Functional predictor, shape (n, m) (all visits of all subjects).
/// y : numpy.ndarray
///     Scalar response, length n.
/// argvals : numpy.ndarray
///     Evaluation grid, length m.
/// subject_ids : numpy.ndarray
///     Non-negative integer subject label per row, length n (any labels;
///     re-indexed internally). At least 2 distinct subjects.
/// penalty, decree_q, lambda_
///     As in ``peer``.
///
/// Returns
/// -------
/// dict
///     ``beta`` (m,), ``intercept``, ``w_bar`` (m,), ``fitted_values`` (n,;
///     marginal), ``sigma2_subject``, ``sigma2_resid``, ``n_subjects``,
///     ``lambda_``, ``penalty_type``, ``gcv``, ``lambda_method`` and ``model``
///     (``PyLocalPeerFit`` with ``predict(new_data, argvals)``).
///
/// Raises
/// ------
/// ValueError
///     For inconsistent dimensions, negative or single-subject labels, or an
///     unknown penalty / lambda spec.
#[pyfunction]
#[pyo3(signature = (data, y, argvals, subject_ids, penalty="difference", decree_q=None, lambda_=None))]
pub fn lpeer<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    y: PyReadonlyArray1<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    subject_ids: PyArrayLike1<'py, i64, AllowTypeChange>,
    penalty: &str,
    decree_q: Option<PyReadonlyArray2<'py, f64>>,
    lambda_: Option<&Bound<'py, PyAny>>,
) -> PyResult<Bound<'py, PyDict>> {
    let cfg = peer_config(penalty, decree_q, lambda_)?;
    let sids = nonneg_labels(&subject_ids, "subject_ids")?;
    let mat = numpy2d_to_fdmatrix(data)?;
    let yv = numpy1d_to_vec(y);
    let av = numpy1d_to_vec(argvals);
    let r = to_pyresult(fdars_core::peer::lpeer(&mat, &yv, &av, &sids, &cfg))?;

    let dict = PyDict::new(py);
    dict.set_item("beta", vec_to_numpy1d(py, r.beta.clone()))?;
    dict.set_item("intercept", r.intercept)?;
    dict.set_item("w_bar", vec_to_numpy1d(py, r.w_bar.clone()))?;
    dict.set_item("fitted_values", vec_to_numpy1d(py, r.fitted_values.clone()))?;
    dict.set_item("sigma2_subject", r.sigma2_subject)?;
    dict.set_item("sigma2_resid", r.sigma2_resid)?;
    dict.set_item("n_subjects", r.n_subjects)?;
    dict.set_item("lambda_", r.lambda)?;
    dict.set_item("penalty_type", peer_penalty_name(&r.penalty_type))?;
    dict.set_item("gcv", r.gcv)?;
    dict.set_item("lambda_method", lambda_method_name(&r.lambda_method))?;
    dict.set_item("model", Py::new(py, PyLocalPeerFit { inner: r })?)?;
    Ok(dict)
}

// ---------------------------------------------------------------------------
// WCR / WNET — wavelet-domain scalar-on-function regression
// ---------------------------------------------------------------------------

/// Fitted wavelet-domain PCR/PLS model (from `wcr`); predicts responses for new curves.
#[pyclass(name = "PyWcrFit")]
pub struct PyWcrFit {
    pub inner: WcrResult,
}

#[pymethods]
impl PyWcrFit {
    /// Time-domain coefficient function beta(t), length m.
    #[getter]
    pub fn beta_t<'py>(&self, py: Python<'py>) -> Bound<'py, PyArray1<f64>> {
        vec_to_numpy1d(py, self.inner.beta_t.clone())
    }

    /// Affine intercept of the prediction formula.
    #[getter]
    pub fn intercept(&self) -> f64 {
        self.inner.intercept
    }

    /// Predict responses for new curves (same length m as the training curves).
    ///
    /// Parameters
    /// ----------
    /// new_data : numpy.ndarray
    ///     Curves, shape (k, m).
    ///
    /// Returns
    /// -------
    /// numpy.ndarray
    ///     Predictions, length k.
    pub fn predict<'py>(
        &self,
        py: Python<'py>,
        new_data: PyReadonlyArray2<'py, f64>,
    ) -> PyResult<Bound<'py, PyArray1<f64>>> {
        let mat = numpy2d_to_fdmatrix(new_data)?;
        Ok(vec_to_numpy1d(py, to_pyresult(self.inner.predict(&mat))?))
    }
}

/// Fitted wavelet-domain elastic-net model (from `wnet`); predicts responses for new curves.
#[pyclass(name = "PyWnetFit")]
pub struct PyWnetFit {
    pub inner: WnetResult,
}

#[pymethods]
impl PyWnetFit {
    /// Time-domain coefficient function beta(t), length m.
    #[getter]
    pub fn beta_t<'py>(&self, py: Python<'py>) -> Bound<'py, PyArray1<f64>> {
        vec_to_numpy1d(py, self.inner.beta_t.clone())
    }

    /// Affine intercept of the prediction formula.
    #[getter]
    pub fn intercept(&self) -> f64 {
        self.inner.intercept
    }

    /// Predict responses for new curves (same length m as the training curves).
    ///
    /// Parameters
    /// ----------
    /// new_data : numpy.ndarray
    ///     Curves, shape (k, m).
    ///
    /// Returns
    /// -------
    /// numpy.ndarray
    ///     Predictions, length k.
    pub fn predict<'py>(
        &self,
        py: Python<'py>,
        new_data: PyReadonlyArray2<'py, f64>,
    ) -> PyResult<Bound<'py, PyArray1<f64>>> {
        let mat = numpy2d_to_fdmatrix(new_data)?;
        Ok(vec_to_numpy1d(py, to_pyresult(self.inner.predict(&mat))?))
    }
}

/// Wavelet-domain scalar-on-function regression (PCR or PLS on DWT coefficients).
///
/// Each curve is transformed into its concatenated DWT coefficient vector, a
/// PCR/PLS fit is done in coefficient space, and the coefficient weights are
/// mapped back to beta(t) by the inverse DWT. The model is
/// ``y_i ~ intercept + sum_j x_i[j] beta_t[j]`` on the sampling index (no
/// quadrature weights, so no ``argvals``).
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Functional predictor, shape (n, m), n >= 3.
/// y : numpy.ndarray
///     Scalar response, length n.
/// wavelet : str, optional
///     ``"haar"`` or ``"db1"`` .. ``"db10"`` (default ``"db4"``).
/// mode : str, optional
///     ``"periodic"`` (default) or ``"symmetric"``.
/// level : int, optional
///     DWT depth; None (default) uses the maximum useful level.
/// ncomp : int, optional
///     Number of coefficient-space components (default 5).
/// method : str, optional
///     ``"pcr"`` (default) or ``"pls"``.
///
/// Returns
/// -------
/// dict
///     ``intercept``, ``beta_t`` (m,), ``fitted_values`` (n,), ``residuals``
///     (n,), ``ncomp`` (effective), ``method``, ``coeff_weights`` (P,),
///     ``wavelet``, ``mode``, ``level`` (effective) and ``model``
///     (``PyWcrFit`` with ``predict(new_data)``).
///
/// Raises
/// ------
/// ValueError
///     For fewer than 3 curves, ``ncomp == 0``, an unknown wavelet / mode /
///     method, or an invalid level.
#[pyfunction]
#[pyo3(signature = (data, y, wavelet="db4", mode="periodic", level=None, ncomp=5, method="pcr"))]
pub fn wcr<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    y: PyReadonlyArray1<'py, f64>,
    wavelet: &str,
    mode: &str,
    level: Option<usize>,
    ncomp: usize,
    method: &str,
) -> PyResult<Bound<'py, PyDict>> {
    let mut cfg = WcrConfig::default();
    cfg.family = wavelet_family(wavelet)?;
    cfg.mode = boundary_mode(mode)?;
    cfg.level = level;
    cfg.ncomp = ncomp;
    cfg.method = match method {
        "pcr" => WcrMethod::Pcr,
        "pls" => WcrMethod::Pls,
        _ => {
            return Err(PyValueError::new_err(format!(
                "method must be one of 'pcr', 'pls', got '{method}'"
            )))
        }
    };
    let mat = numpy2d_to_fdmatrix(data)?;
    let yv = numpy1d_to_vec(y);
    let r = to_pyresult(fdars_core::wavelet::regression::wcr(&mat, &yv, &cfg))?;

    let dict = PyDict::new(py);
    dict.set_item("intercept", r.intercept)?;
    dict.set_item("beta_t", vec_to_numpy1d(py, r.beta_t.clone()))?;
    dict.set_item("fitted_values", vec_to_numpy1d(py, r.fitted_values.clone()))?;
    dict.set_item("residuals", vec_to_numpy1d(py, r.residuals.clone()))?;
    dict.set_item("ncomp", r.ncomp)?;
    dict.set_item(
        "method",
        if r.method == WcrMethod::Pls {
            "pls"
        } else {
            "pcr"
        },
    )?;
    dict.set_item("coeff_weights", vec_to_numpy1d(py, r.coeff_weights.clone()))?;
    dict.set_item("wavelet", wavelet_family_name(&r.family))?;
    dict.set_item("mode", boundary_mode_name(r.mode))?;
    dict.set_item("level", r.level)?;
    dict.set_item("model", Py::new(py, PyWcrFit { inner: r })?)?;
    Ok(dict)
}

/// Wavelet-domain elastic-net scalar-on-function regression with cross-validated lambda.
///
/// Fits a per-coefficient elastic net (coordinate descent) on the DWT
/// coefficient design, choosing lambda by deterministic K-fold CV, then maps
/// the sparse coefficient weights back to beta(t) by the inverse DWT. Same
/// model scale as ``wcr`` (sampling index, no ``argvals``).
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Functional predictor, shape (n, m), n >= 3.
/// y : numpy.ndarray
///     Scalar response, length n.
/// wavelet : str, optional
///     ``"haar"`` or ``"db1"`` .. ``"db10"`` (default ``"db4"``).
/// mode : str, optional
///     ``"periodic"`` (default) or ``"symmetric"``.
/// level : int, optional
///     DWT depth; None (default) uses the maximum useful level.
/// alpha : float, optional
///     L1/L2 mix in [0, 1]: 1 = lasso, 0 = ridge (default 0.5).
/// lambda_grid : array-like, optional
///     Explicit lambda grid; None (default) builds a geometric grid.
/// n_lambda : int, optional
///     Size of the automatic grid (default 50).
/// n_folds : int, optional
///     CV folds, 2 <= n_folds <= n (default 5).
/// seed : int, optional
///     Seed of the fold partition (default 0).
/// max_iter : int, optional
///     Maximum coordinate-descent sweeps (default 1000).
/// tol : float, optional
///     Coordinate-descent tolerance on max |delta beta| (default 1e-6).
///
/// Returns
/// -------
/// dict
///     ``intercept``, ``beta_t`` (m,), ``fitted_values`` (n,), ``residuals``
///     (n,), ``coeff_weights`` (P,; sparse), ``selected`` (int indices of
///     non-zero coefficients), ``lambda_`` (CV choice), ``alpha``,
///     ``wavelet``, ``mode``, ``level`` and ``model`` (``PyWnetFit`` with
///     ``predict(new_data)``).
///
/// Raises
/// ------
/// ValueError
///     For fewer than 3 curves, alpha outside [0, 1], invalid folds /
///     iterations / tolerance, an empty lambda grid, or an unknown wavelet / mode.
#[pyfunction]
#[pyo3(signature = (data, y, wavelet="db4", mode="periodic", level=None, alpha=0.5, lambda_grid=None, n_lambda=50, n_folds=5, seed=0, max_iter=1000, tol=1e-6))]
pub fn wnet<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    y: PyReadonlyArray1<'py, f64>,
    wavelet: &str,
    mode: &str,
    level: Option<usize>,
    alpha: f64,
    lambda_grid: Option<Vec<f64>>,
    n_lambda: usize,
    n_folds: usize,
    seed: u64,
    max_iter: usize,
    tol: f64,
) -> PyResult<Bound<'py, PyDict>> {
    let mut cfg = WnetConfig::default();
    cfg.family = wavelet_family(wavelet)?;
    cfg.mode = boundary_mode(mode)?;
    cfg.level = level;
    cfg.alpha = alpha;
    cfg.lambda_grid = lambda_grid;
    cfg.n_lambda = n_lambda;
    cfg.n_folds = n_folds;
    cfg.seed = seed;
    cfg.max_iter = max_iter;
    cfg.tol = tol;
    let mat = numpy2d_to_fdmatrix(data)?;
    let yv = numpy1d_to_vec(y);
    let r = to_pyresult(fdars_core::wavelet::regression::wnet(&mat, &yv, &cfg))?;

    let dict = PyDict::new(py);
    dict.set_item("intercept", r.intercept)?;
    dict.set_item("beta_t", vec_to_numpy1d(py, r.beta_t.clone()))?;
    dict.set_item("fitted_values", vec_to_numpy1d(py, r.fitted_values.clone()))?;
    dict.set_item("residuals", vec_to_numpy1d(py, r.residuals.clone()))?;
    dict.set_item("coeff_weights", vec_to_numpy1d(py, r.coeff_weights.clone()))?;
    dict.set_item("selected", usize_vec_to_numpy1d(py, r.selected.clone()))?;
    dict.set_item("lambda_", r.lambda)?;
    dict.set_item("alpha", r.alpha)?;
    dict.set_item("wavelet", wavelet_family_name(&r.family))?;
    dict.set_item("mode", boundary_mode_name(r.mode))?;
    dict.set_item("level", r.level)?;
    dict.set_item("model", Py::new(py, PyWnetFit { inner: r })?)?;
    Ok(dict)
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
    m.add_class::<PyPeerFit>()?;
    m.add_class::<PyLocalPeerFit>()?;
    m.add_class::<PyWcrFit>()?;
    m.add_class::<PyWnetFit>()?;
    m.add_function(wrap_pyfunction!(peer, m)?)?;
    m.add_function(wrap_pyfunction!(lpeer, m)?)?;
    m.add_function(wrap_pyfunction!(wcr, m)?)?;
    m.add_function(wrap_pyfunction!(wnet, m)?)?;
    Ok(())
}
