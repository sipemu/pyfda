//! Regression methods for functional data.

use crate::convert::*;
use numpy::{PyReadonlyArray1, PyReadonlyArray2};
use pyo3::prelude::*;

/// Functional principal component analysis (FPCA).
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Data, shape (n, m).
/// argvals : numpy.ndarray
///     Evaluation points, length m.
/// n_comp : int, optional
///     Number of components (default 3).
///
/// Returns
/// -------
/// dict
///     scores (n, n_comp), rotation (m, n_comp), singular_values (n_comp,),
///     mean (m,), centered (n, m), weights (m,).
#[pyfunction]
#[pyo3(signature = (data, argvals, n_comp=3))]
pub fn fpca<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    n_comp: usize,
) -> PyResult<Bound<'py, PyAny>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let result = to_pyresult(fdars_core::regression::fdata_to_pc_1d(&mat, n_comp, &av))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("scores", fdmatrix_to_numpy2d(py, &result.scores))?;
    dict.set_item("rotation", fdmatrix_to_numpy2d(py, &result.rotation))?;
    dict.set_item(
        "singular_values",
        vec_to_numpy1d(py, result.singular_values),
    )?;
    dict.set_item("mean", vec_to_numpy1d(py, result.mean))?;
    dict.set_item("centered", fdmatrix_to_numpy2d(py, &result.centered))?;
    dict.set_item("weights", vec_to_numpy1d(py, result.weights))?;
    Ok(dict.into_any())
}

/// Functional PLS (Partial Least Squares).
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Data, shape (n, m).
/// argvals : numpy.ndarray
///     Evaluation points, length m.
/// response : numpy.ndarray
///     Response values, length n.
/// n_comp : int, optional
///     Number of components (default 3).
///
/// Returns
/// -------
/// dict
///     scores (n, n_comp), loadings (m, n_comp), weights (m, n_comp),
///     x_means (m,), integration_weights (m,).
#[pyfunction]
#[pyo3(signature = (data, argvals, response, n_comp=3))]
pub fn fpls<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    response: PyReadonlyArray1<'py, f64>,
    n_comp: usize,
) -> PyResult<Bound<'py, PyAny>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let resp = numpy1d_to_vec(response);
    let result = to_pyresult(fdars_core::regression::fdata_to_pls_1d(
        &mat, &resp, n_comp, &av,
    ))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("scores", fdmatrix_to_numpy2d(py, &result.scores))?;
    dict.set_item("loadings", fdmatrix_to_numpy2d(py, &result.loadings))?;
    dict.set_item("weights", fdmatrix_to_numpy2d(py, &result.weights))?;
    dict.set_item("x_means", vec_to_numpy1d(py, result.x_means))?;
    dict.set_item(
        "integration_weights",
        vec_to_numpy1d(py, result.integration_weights),
    )?;
    Ok(dict.into_any())
}

/// Scalar-on-function linear regression via FPCs.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Functional predictors, shape (n, m).
/// response : numpy.ndarray
///     Scalar response, length n.
/// n_comp : int, optional
///     Number of FPC components (default 3).
///
/// Returns
/// -------
/// dict
///     fitted_values (n,), residuals (n,), beta_t (m,), r_squared,
///     coefficients, intercept.
#[pyfunction]
#[pyo3(signature = (data, response, n_comp=3))]
pub fn fregre_lm<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    response: PyReadonlyArray1<'py, f64>,
    n_comp: usize,
) -> PyResult<Bound<'py, PyAny>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let resp = numpy1d_to_vec(response);
    let result = to_pyresult(fdars_core::scalar_on_function::fregre_lm(
        &mat, &resp, None, n_comp,
    ))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("fitted_values", vec_to_numpy1d(py, result.fitted_values))?;
    dict.set_item("residuals", vec_to_numpy1d(py, result.residuals))?;
    dict.set_item("beta_t", vec_to_numpy1d(py, result.beta_t))?;
    dict.set_item("r_squared", result.r_squared)?;
    dict.set_item("coefficients", vec_to_numpy1d(py, result.coefficients))?;
    dict.set_item("intercept", result.intercept)?;
    Ok(dict.into_any())
}

/// Scalar-on-function PLS regression.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Functional predictors, shape (n, m).
/// argvals : numpy.ndarray
///     Evaluation points, length m.
/// response : numpy.ndarray
///     Scalar response, length n.
/// n_comp : int, optional
///     Number of PLS components (default 3).
///
/// Returns
/// -------
/// dict
///     fitted_values (n,), residuals (n,), beta_t (m,), r_squared.
#[pyfunction]
#[pyo3(signature = (data, argvals, response, n_comp=3))]
pub fn fregre_pls<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    response: PyReadonlyArray1<'py, f64>,
    n_comp: usize,
) -> PyResult<Bound<'py, PyAny>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let resp = numpy1d_to_vec(response);
    let result = to_pyresult(fdars_core::scalar_on_function::fregre_pls(
        &mat, &resp, &av, n_comp, None,
    ))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("fitted_values", vec_to_numpy1d(py, result.fitted_values))?;
    dict.set_item("residuals", vec_to_numpy1d(py, result.residuals))?;
    dict.set_item("beta_t", vec_to_numpy1d(py, result.beta_t))?;
    dict.set_item("r_squared", result.r_squared)?;
    Ok(dict.into_any())
}

/// Nonparametric kernel regression for functional data (from distance matrix).
///
/// Parameters
/// ----------
/// dist_matrix : numpy.ndarray
///     Distance matrix, shape (n, n).
/// response : numpy.ndarray
///     Scalar response, length n.
/// h : float, optional
///     Bandwidth (default 0.0, meaning automatic selection).
///
/// Returns
/// -------
/// dict
///     fitted_values (n,), residuals (n,), h_func, r_squared.
#[pyfunction]
#[pyo3(signature = (dist_matrix, response, h=0.0))]
pub fn fregre_np<'py>(
    py: Python<'py>,
    dist_matrix: PyReadonlyArray2<'py, f64>,
    response: PyReadonlyArray1<'py, f64>,
    h: f64,
) -> PyResult<Bound<'py, PyAny>> {
    let dm = numpy2d_to_fdmatrix(dist_matrix)?;
    let resp = numpy1d_to_vec(response);
    // fregre_np_from_distances takes flat &[f64] of length n*n
    let flat_dists = dm.to_row_major();
    let result = to_pyresult(fdars_core::scalar_on_function::fregre_np_from_distances(
        &flat_dists,
        &resp,
        None,
        h,
        0.0,
    ))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("fitted_values", vec_to_numpy1d(py, result.fitted_values))?;
    dict.set_item("residuals", vec_to_numpy1d(py, result.residuals))?;
    dict.set_item("h_func", result.h_func)?;
    dict.set_item("r_squared", result.r_squared)?;
    Ok(dict.into_any())
}

/// L1 robust regression for functional data.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Functional predictors, shape (n, m).
/// response : numpy.ndarray
///     Scalar response, length n.
/// n_comp : int, optional
///     Number of FPC components (default 3).
///
/// Returns
/// -------
/// dict
///     fitted_values (n,), residuals (n,), beta_t (m,).
#[pyfunction]
#[pyo3(signature = (data, response, n_comp=3))]
pub fn fregre_l1<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    response: PyReadonlyArray1<'py, f64>,
    n_comp: usize,
) -> PyResult<Bound<'py, PyAny>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let resp = numpy1d_to_vec(response);
    let result = to_pyresult(fdars_core::scalar_on_function::fregre_l1(
        &mat, &resp, None, n_comp,
    ))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("fitted_values", vec_to_numpy1d(py, result.fitted_values))?;
    dict.set_item("residuals", vec_to_numpy1d(py, result.residuals))?;
    dict.set_item("beta_t", vec_to_numpy1d(py, result.beta_t))?;
    Ok(dict.into_any())
}

/// Huber M-estimation regression for functional data.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Functional predictors, shape (n, m).
/// response : numpy.ndarray
///     Scalar response, length n.
/// n_comp : int, optional
///     Number of FPC components (default 3).
/// huber_k : float, optional
///     Huber tuning constant (default 1.345).
///
/// Returns
/// -------
/// dict
///     fitted_values (n,), residuals (n,), beta_t (m,).
#[pyfunction]
#[pyo3(signature = (data, response, n_comp=3, huber_k=1.345))]
pub fn fregre_huber<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    response: PyReadonlyArray1<'py, f64>,
    n_comp: usize,
    huber_k: f64,
) -> PyResult<Bound<'py, PyAny>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let resp = numpy1d_to_vec(response);
    let result = to_pyresult(fdars_core::scalar_on_function::fregre_huber(
        &mat, &resp, None, n_comp, huber_k,
    ))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("fitted_values", vec_to_numpy1d(py, result.fitted_values))?;
    dict.set_item("residuals", vec_to_numpy1d(py, result.residuals))?;
    dict.set_item("beta_t", vec_to_numpy1d(py, result.beta_t))?;
    Ok(dict.into_any())
}

/// Functional logistic regression.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Functional predictors, shape (n, m).
/// labels : numpy.ndarray
///     Binary labels (0/1), length n.
/// n_comp : int, optional
///     Number of FPC components (default 3).
/// max_iter : int, optional
///     Maximum IRLS iterations (default 25).
/// tol : float, optional
///     Convergence tolerance (default 1e-6).
///
/// Returns
/// -------
/// dict
///     probabilities (n,), predicted_classes (n,), beta_t (m,),
///     intercept, coefficients.
#[pyfunction]
#[pyo3(signature = (data, labels, n_comp=3, max_iter=25, tol=1e-6))]
pub fn functional_logistic<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    labels: PyReadonlyArray1<'py, f64>,
    n_comp: usize,
    max_iter: usize,
    tol: f64,
) -> PyResult<Bound<'py, PyAny>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let lab = numpy1d_to_vec(labels);
    let result = to_pyresult(fdars_core::scalar_on_function::functional_logistic(
        &mat, &lab, None, n_comp, max_iter, tol,
    ))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("probabilities", vec_to_numpy1d(py, result.probabilities))?;
    dict.set_item(
        "predicted_classes",
        usize_vec_to_numpy1d(py, result.predicted_classes),
    )?;
    dict.set_item("beta_t", vec_to_numpy1d(py, result.beta_t))?;
    dict.set_item("intercept", result.intercept)?;
    dict.set_item("coefficients", vec_to_numpy1d(py, result.coefficients))?;
    Ok(dict.into_any())
}

/// Function-on-scalar regression (FOSR).
///
/// Parameters
/// ----------
/// response : numpy.ndarray
///     Functional response, shape (n, m).
/// predictors : numpy.ndarray
///     Scalar predictors, shape (n, p).
/// lambda_ : float, optional
///     Roughness penalty (default 0.0, negative for GCV selection).
///
/// Returns
/// -------
/// dict
///     fitted (n, m), beta (p, m), residuals (n, m), r_squared.
#[pyfunction]
#[pyo3(signature = (response, predictors, lambda_=0.0))]
pub fn fosr<'py>(
    py: Python<'py>,
    response: PyReadonlyArray2<'py, f64>,
    predictors: PyReadonlyArray2<'py, f64>,
    lambda_: f64,
) -> PyResult<Bound<'py, PyAny>> {
    let resp_mat = numpy2d_to_fdmatrix(response)?;
    let pred_mat = numpy2d_to_fdmatrix(predictors)?;
    let result = to_pyresult(fdars_core::function_on_scalar::fosr(
        &resp_mat, &pred_mat, lambda_,
    ))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("fitted", fdmatrix_to_numpy2d(py, &result.fitted))?;
    dict.set_item("beta", fdmatrix_to_numpy2d(py, &result.beta))?;
    dict.set_item("residuals", fdmatrix_to_numpy2d(py, &result.residuals))?;
    dict.set_item("r_squared", result.r_squared)?;
    Ok(dict.into_any())
}

/// Functional ANOVA.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Functional data, shape (n, m).
/// groups : numpy.ndarray
///     Group labels, length n.
/// n_perm : int, optional
///     Number of permutations for p-value (default 999).
///
/// Returns
/// -------
/// dict
///     f_statistic_t (m,), p_value (float), group_means (k, m),
///     global_statistic (float).
#[allow(deprecated)] // fdars-core 0.30: soft-deprecated; migration deferred (Phase 66 CONTINGENCY)
#[pyfunction]
#[pyo3(signature = (data, groups, n_perm=999))]
pub fn fanova<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    groups: PyReadonlyArray1<'py, i64>,
    n_perm: usize,
) -> PyResult<Bound<'py, PyAny>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let grp = numpy1d_to_usize_vec(groups);
    let result = to_pyresult(fdars_core::function_on_scalar::fanova(&mat, &grp, n_perm))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("f_statistic_t", vec_to_numpy1d(py, result.f_statistic_t))?;
    dict.set_item("p_value", result.p_value)?;
    dict.set_item("group_means", fdmatrix_to_numpy2d(py, &result.group_means))?;
    dict.set_item("global_statistic", result.global_statistic)?;
    Ok(dict.into_any())
}

/// Cross-validated selection of number of FPC components.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Functional predictors, shape (n, m).
/// response : numpy.ndarray
///     Scalar response, length n.
/// max_comp : int, optional
///     Maximum number of components to test (default 10).
/// criterion : str, optional
///     Selection criterion: "gcv" (default), "aic", or "bic".
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

/// Predict new responses using a fitted functional linear model.
///
/// Parameters
/// ----------
/// data_fit : numpy.ndarray
///     Original functional predictors used for fitting, shape (n, m).
/// response : numpy.ndarray
///     Original scalar response, length n.
/// new_data : numpy.ndarray
///     New functional predictors, shape (n_new, m).
/// n_comp : int, optional
///     Number of FPC components (default 3).
///
/// Returns
/// -------
/// numpy.ndarray
///     Predicted values, length n_new.
#[pyfunction]
#[pyo3(signature = (data_fit, response, new_data, n_comp=3))]
pub fn predict_fregre_lm<'py>(
    py: Python<'py>,
    data_fit: PyReadonlyArray2<'py, f64>,
    response: PyReadonlyArray1<'py, f64>,
    new_data: PyReadonlyArray2<'py, f64>,
    n_comp: usize,
) -> PyResult<Bound<'py, PyAny>> {
    let mat = numpy2d_to_fdmatrix(data_fit)?;
    let resp = numpy1d_to_vec(response);
    let fit = to_pyresult(fdars_core::scalar_on_function::fregre_lm(
        &mat, &resp, None, n_comp,
    ))?;
    let new_mat = numpy2d_to_fdmatrix(new_data)?;
    let preds = fdars_core::scalar_on_function::predict_fregre_lm(&fit, &new_mat, None);
    Ok(vec_to_numpy1d(py, preds).into_any())
}

/// Predict new responses using a fitted PLS regression.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Functional predictors, shape (n, m).
/// argvals : numpy.ndarray
///     Evaluation points, length m.
/// response : numpy.ndarray
///     Scalar response, length n.
/// new_data : numpy.ndarray
///     New functional predictors, shape (n_new, m).
/// n_comp : int, optional
///     Number of PLS components (default 3).
///
/// Returns
/// -------
/// numpy.ndarray
///     Predicted values, length n_new.
#[pyfunction]
#[pyo3(signature = (data, argvals, response, new_data, n_comp=3))]
pub fn predict_fregre_pls<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    response: PyReadonlyArray1<'py, f64>,
    new_data: PyReadonlyArray2<'py, f64>,
    n_comp: usize,
) -> PyResult<Bound<'py, PyAny>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let resp = numpy1d_to_vec(response);
    let fit = to_pyresult(fdars_core::scalar_on_function::fregre_pls(
        &mat, &resp, &av, n_comp, None,
    ))?;
    let new_mat = numpy2d_to_fdmatrix(new_data)?;
    let preds = to_pyresult(fdars_core::scalar_on_function::predict_fregre_pls(
        &fit, &new_mat, None,
    ))?;
    Ok(vec_to_numpy1d(py, preds).into_any())
}

/// Predict new responses using a fitted robust regression (L1 or Huber).
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Functional predictors, shape (n, m).
/// response : numpy.ndarray
///     Scalar response, length n.
/// new_data : numpy.ndarray
///     New functional predictors, shape (n_new, m).
/// n_comp : int, optional
///     Number of FPC components (default 3).
/// method : str, optional
///     "l1" (default) or "huber".
/// huber_k : float, optional
///     Huber tuning constant (default 1.345, only used with method="huber").
///
/// Returns
/// -------
/// numpy.ndarray
///     Predicted values, length n_new.
#[pyfunction]
#[pyo3(signature = (data, response, new_data, n_comp=3, method="l1", huber_k=1.345))]
pub fn predict_fregre_robust<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    response: PyReadonlyArray1<'py, f64>,
    new_data: PyReadonlyArray2<'py, f64>,
    n_comp: usize,
    method: &str,
    huber_k: f64,
) -> PyResult<Bound<'py, PyAny>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let resp = numpy1d_to_vec(response);
    let fit = match method {
        "huber" => to_pyresult(fdars_core::scalar_on_function::fregre_huber(
            &mat, &resp, None, n_comp, huber_k,
        ))?,
        _ => to_pyresult(fdars_core::scalar_on_function::fregre_l1(
            &mat, &resp, None, n_comp,
        ))?,
    };
    let new_mat = numpy2d_to_fdmatrix(new_data)?;
    let preds = fdars_core::scalar_on_function::predict_fregre_robust(&fit, &new_mat, None);
    Ok(vec_to_numpy1d(py, preds).into_any())
}

/// Predict probabilities for new data using a fitted functional logistic model.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Functional predictors, shape (n, m).
/// labels : numpy.ndarray
///     Binary labels (0/1), length n.
/// new_data : numpy.ndarray
///     New functional predictors, shape (n_new, m).
/// n_comp : int, optional
///     Number of FPC components (default 3).
/// max_iter : int, optional
///     Maximum IRLS iterations (default 25).
/// tol : float, optional
///     Convergence tolerance (default 1e-6).
///
/// Returns
/// -------
/// numpy.ndarray
///     Predicted probabilities, length n_new.
#[pyfunction]
#[pyo3(signature = (data, labels, new_data, n_comp=3, max_iter=25, tol=1e-6))]
pub fn predict_functional_logistic<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    labels: PyReadonlyArray1<'py, f64>,
    new_data: PyReadonlyArray2<'py, f64>,
    n_comp: usize,
    max_iter: usize,
    tol: f64,
) -> PyResult<Bound<'py, PyAny>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let lab = numpy1d_to_vec(labels);
    let fit = to_pyresult(fdars_core::scalar_on_function::functional_logistic(
        &mat, &lab, None, n_comp, max_iter, tol,
    ))?;
    let new_mat = numpy2d_to_fdmatrix(new_data)?;
    let preds = fdars_core::scalar_on_function::predict_functional_logistic(&fit, &new_mat, None);
    Ok(vec_to_numpy1d(py, preds).into_any())
}

/// Cross-validated selection of number of FPC components using K-fold CV.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Functional predictors, shape (n, m).
/// response : numpy.ndarray
///     Scalar response, length n.
/// k_min : int, optional
///     Minimum number of components to test (default 1).
/// k_max : int, optional
///     Maximum number of components to test (default 10).
/// n_folds : int, optional
///     Number of CV folds (default 5).
///
/// Returns
/// -------
/// dict
///     optimal_k, min_cv_error, k_values, cv_errors, oof_predictions,
///     fold_assignments, fold_errors.
#[pyfunction]
#[pyo3(signature = (data, response, k_min=1, k_max=10, n_folds=5))]
pub fn fregre_cv<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    response: PyReadonlyArray1<'py, f64>,
    k_min: usize,
    k_max: usize,
    n_folds: usize,
) -> PyResult<Bound<'py, PyAny>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let resp = numpy1d_to_vec(response);
    let result = to_pyresult(fdars_core::scalar_on_function::fregre_cv(
        &mat, &resp, None, k_min, k_max, n_folds,
    ))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("optimal_k", result.optimal_k)?;
    dict.set_item("min_cv_error", result.min_cv_error)?;
    dict.set_item("k_values", usize_vec_to_numpy1d(py, result.k_values))?;
    dict.set_item("cv_errors", vec_to_numpy1d(py, result.cv_errors))?;
    dict.set_item(
        "oof_predictions",
        vec_to_numpy1d(py, result.oof_predictions),
    )?;
    dict.set_item(
        "fold_assignments",
        usize_vec_to_numpy1d(py, result.fold_assignments),
    )?;
    dict.set_item("fold_errors", vec_to_numpy1d(py, result.fold_errors))?;
    Ok(dict.into_any())
}

/// Bootstrap confidence intervals for beta(t) from a functional linear model.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Functional predictors, shape (n, m).
/// response : numpy.ndarray
///     Scalar response, length n.
/// n_comp : int, optional
///     Number of FPC components (default 3).
/// n_boot : int, optional
///     Number of bootstrap replicates (default 200).
/// alpha : float, optional
///     Significance level (default 0.05 for 95% CI).
/// seed : int, optional
///     Random seed (default 42).
///
/// Returns
/// -------
/// dict
///     lower (m,), upper (m,), center (m,), sim_lower (m,), sim_upper (m,),
///     n_boot_success.
#[pyfunction]
#[pyo3(signature = (data, response, n_comp=3, n_boot=200, alpha=0.05, seed=42))]
pub fn bootstrap_ci_fregre_lm<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    response: PyReadonlyArray1<'py, f64>,
    n_comp: usize,
    n_boot: usize,
    alpha: f64,
    seed: u64,
) -> PyResult<Bound<'py, PyAny>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let resp = numpy1d_to_vec(response);
    let result = to_pyresult(fdars_core::scalar_on_function::bootstrap_ci_fregre_lm(
        &mat, &resp, None, n_comp, n_boot, alpha, seed,
    ))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("lower", vec_to_numpy1d(py, result.lower))?;
    dict.set_item("upper", vec_to_numpy1d(py, result.upper))?;
    dict.set_item("center", vec_to_numpy1d(py, result.center))?;
    dict.set_item("sim_lower", vec_to_numpy1d(py, result.sim_lower))?;
    dict.set_item("sim_upper", vec_to_numpy1d(py, result.sim_upper))?;
    dict.set_item("n_boot_success", result.n_boot_success)?;
    Ok(dict.into_any())
}

/// Bootstrap confidence intervals for beta(t) from a functional logistic model.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Functional predictors, shape (n, m).
/// labels : numpy.ndarray
///     Binary labels (0/1), length n.
/// n_comp : int, optional
///     Number of FPC components (default 3).
/// n_boot : int, optional
///     Number of bootstrap replicates (default 200).
/// alpha : float, optional
///     Significance level (default 0.05).
/// seed : int, optional
///     Random seed (default 42).
/// max_iter : int, optional
///     Maximum IRLS iterations (default 25).
/// tol : float, optional
///     Convergence tolerance (default 1e-6).
///
/// Returns
/// -------
/// dict
///     lower (m,), upper (m,), center (m,), sim_lower (m,), sim_upper (m,),
///     n_boot_success.
#[pyfunction]
#[pyo3(signature = (data, labels, n_comp=3, n_boot=200, alpha=0.05, seed=42, max_iter=25, tol=1e-6))]
pub fn bootstrap_ci_functional_logistic<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    labels: PyReadonlyArray1<'py, f64>,
    n_comp: usize,
    n_boot: usize,
    alpha: f64,
    seed: u64,
    max_iter: usize,
    tol: f64,
) -> PyResult<Bound<'py, PyAny>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let lab = numpy1d_to_vec(labels);
    let result = to_pyresult(
        fdars_core::scalar_on_function::bootstrap_ci_functional_logistic(
            &mat, &lab, None, n_comp, n_boot, alpha, seed, max_iter, tol,
        ),
    )?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("lower", vec_to_numpy1d(py, result.lower))?;
    dict.set_item("upper", vec_to_numpy1d(py, result.upper))?;
    dict.set_item("center", vec_to_numpy1d(py, result.center))?;
    dict.set_item("sim_lower", vec_to_numpy1d(py, result.sim_lower))?;
    dict.set_item("sim_upper", vec_to_numpy1d(py, result.sim_upper))?;
    dict.set_item("n_boot_success", result.n_boot_success)?;
    Ok(dict.into_any())
}

/// Function-on-scalar regression via FPCs (FOSR-FPC).
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Functional response, shape (n, m).
/// predictors : numpy.ndarray
///     Scalar predictors, shape (n, p).
/// n_comp : int, optional
///     Number of FPC components (default 3).
///
/// Returns
/// -------
/// dict
///     intercept (m,), beta (p, m), fitted (n, m), residuals (n, m),
///     r_squared_t (m,), r_squared, ncomp.
#[pyfunction]
#[pyo3(signature = (data, predictors, n_comp=3))]
pub fn fosr_fpc<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    predictors: PyReadonlyArray2<'py, f64>,
    n_comp: usize,
) -> PyResult<Bound<'py, PyAny>> {
    let data_mat = numpy2d_to_fdmatrix(data)?;
    let pred_mat = numpy2d_to_fdmatrix(predictors)?;
    let result = to_pyresult(fdars_core::function_on_scalar::fosr_fpc(
        &data_mat, &pred_mat, n_comp,
    ))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("intercept", vec_to_numpy1d(py, result.intercept))?;
    dict.set_item("beta", fdmatrix_to_numpy2d(py, &result.beta))?;
    dict.set_item("fitted", fdmatrix_to_numpy2d(py, &result.fitted))?;
    dict.set_item("residuals", fdmatrix_to_numpy2d(py, &result.residuals))?;
    dict.set_item("r_squared_t", vec_to_numpy1d(py, result.r_squared_t))?;
    dict.set_item("r_squared", result.r_squared)?;
    dict.set_item("ncomp", result.ncomp)?;
    Ok(dict.into_any())
}

/// Predict new functional responses from a fitted FOSR model.
///
/// Parameters
/// ----------
/// response : numpy.ndarray
///     Functional response, shape (n, m).
/// predictors : numpy.ndarray
///     Scalar predictors used for fitting, shape (n, p).
/// new_predictors : numpy.ndarray
///     New scalar predictors, shape (n_new, p).
/// lambda_ : float, optional
///     Roughness penalty (default 0.0).
///
/// Returns
/// -------
/// numpy.ndarray
///     Predicted functional values, shape (n_new, m).
#[pyfunction]
#[pyo3(signature = (response, predictors, new_predictors, lambda_=0.0))]
pub fn predict_fosr<'py>(
    py: Python<'py>,
    response: PyReadonlyArray2<'py, f64>,
    predictors: PyReadonlyArray2<'py, f64>,
    new_predictors: PyReadonlyArray2<'py, f64>,
    lambda_: f64,
) -> PyResult<Bound<'py, PyAny>> {
    let resp_mat = numpy2d_to_fdmatrix(response)?;
    let pred_mat = numpy2d_to_fdmatrix(predictors)?;
    let fit = to_pyresult(fdars_core::function_on_scalar::fosr(
        &resp_mat, &pred_mat, lambda_,
    ))?;
    let new_pred_mat = numpy2d_to_fdmatrix(new_predictors)?;
    let predicted = fdars_core::function_on_scalar::predict_fosr(&fit, &new_pred_mat);
    Ok(fdmatrix_to_numpy2d(py, &predicted).into_any())
}

/// Cross-validated bandwidth selection for nonparametric functional regression.
///
/// Matches R `fregre.np.cv`. Runs k-fold CV over a grid of bandwidths (built
/// automatically if `h_range` is omitted) and reports the optimum.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Functional predictors, shape (n, m).
/// response : numpy.ndarray
///     Scalar response, length n.
/// argvals : numpy.ndarray
///     Evaluation points, length m.
/// n_folds : int, optional
///     Number of CV folds (default 5).
/// h_range : numpy.ndarray, optional
///     Candidate bandwidths. Auto-selected when omitted.
/// scalar_covariates : numpy.ndarray, optional
///     Additional scalar covariates, shape (n, q).
///
/// Returns
/// -------
/// dict
///     ``optimal_h``, ``cv_errors``, ``cv_se``, ``h_values``, ``min_cv_error``.
#[pyfunction]
#[pyo3(signature = (data, response, argvals, n_folds=5, h_range=None, scalar_covariates=None))]
pub fn fregre_np_cv<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    response: PyReadonlyArray1<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    n_folds: usize,
    h_range: Option<PyReadonlyArray1<'py, f64>>,
    scalar_covariates: Option<PyReadonlyArray2<'py, f64>>,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let y = numpy1d_to_vec(response);
    let av = numpy1d_to_vec(argvals);
    let h_vec = h_range.map(numpy1d_to_vec);
    let sc = scalar_covariates.map(numpy2d_to_fdmatrix).transpose()?;
    let result = to_pyresult(fdars_core::scalar_on_function::fregre_np_cv(
        &mat,
        &y,
        &av,
        n_folds,
        h_vec.as_deref(),
        sc.as_ref(),
    ))?;
    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("optimal_h", result.optimal_h)?;
    dict.set_item("cv_errors", vec_to_numpy1d(py, result.cv_errors))?;
    dict.set_item("cv_se", vec_to_numpy1d(py, result.cv_se))?;
    dict.set_item("h_values", vec_to_numpy1d(py, result.h_values))?;
    dict.set_item("min_cv_error", result.min_cv_error)?;
    Ok(dict)
}

/// Nonparametric functional regression mixing functional and scalar predictors.
///
/// Matches R `fregre.np.mixed`. Kernel regression with separate bandwidths for
/// the functional-distance kernel and the scalar-covariate kernel.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Functional predictors, shape (n, m).
/// response : numpy.ndarray
///     Scalar response, length n.
/// argvals : numpy.ndarray
///     Evaluation points, length m.
/// h_func : float
///     Bandwidth for the functional-distance kernel.
/// h_scalar : float, optional
///     Bandwidth for the scalar-covariate kernel (default 1.0).
/// scalar_covariates : numpy.ndarray, optional
///     Additional scalar covariates, shape (n, q).
///
/// Returns
/// -------
/// dict
///     ``fitted_values``, ``residuals``, ``r_squared``, ``h_func``,
///     ``h_scalar``, ``cv_error``.
#[pyfunction]
#[pyo3(signature = (data, response, argvals, h_func, h_scalar=1.0, scalar_covariates=None))]
pub fn fregre_np_mixed<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    response: PyReadonlyArray1<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    h_func: f64,
    h_scalar: f64,
    scalar_covariates: Option<PyReadonlyArray2<'py, f64>>,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let y = numpy1d_to_vec(response);
    let av = numpy1d_to_vec(argvals);
    let sc = scalar_covariates.map(numpy2d_to_fdmatrix).transpose()?;
    let result = to_pyresult(fdars_core::scalar_on_function::fregre_np_mixed(
        &mat,
        &y,
        &av,
        sc.as_ref(),
        h_func,
        h_scalar,
    ))?;
    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("fitted_values", vec_to_numpy1d(py, result.fitted_values))?;
    dict.set_item("residuals", vec_to_numpy1d(py, result.residuals))?;
    dict.set_item("r_squared", result.r_squared)?;
    dict.set_item("h_func", result.h_func)?;
    dict.set_item("h_scalar", result.h_scalar)?;
    dict.set_item("cv_error", result.cv_error)?;
    Ok(dict)
}

// ---------------------------------------------------------------------------
// Internal helper: ConcurrentRegrResult → Python dict.
//
// The struct is #[non_exhaustive] — access each field by name; never
// struct-literal it.
//
// Shape note: beta_curve is (p, m) where rows index predictors and columns
// index grid points — NOT (n_obs, m) as with every other FdMatrix in pyfda.
// fdmatrix_to_numpy2d faithfully preserves this (p, m) shape.
// ---------------------------------------------------------------------------

fn concurrent_regr_result_to_pydict<'py>(
    py: Python<'py>,
    r: fdars_core::concurrent_regression::ConcurrentRegrResult,
) -> PyResult<Bound<'py, PyAny>> {
    let dict = pyo3::types::PyDict::new(py);
    // beta_curve: shape (p, m) — rows are predictor curves, NOT observations
    dict.set_item("beta_curve", fdmatrix_to_numpy2d(py, &r.beta_curve))?;
    dict.set_item("intercept", vec_to_numpy1d(py, r.intercept))?;
    dict.set_item("fitted", fdmatrix_to_numpy2d(py, &r.fitted))?;
    dict.set_item("residuals", fdmatrix_to_numpy2d(py, &r.residuals))?;
    dict.set_item("argvals", vec_to_numpy1d(py, r.argvals))?;
    Ok(dict.into_any())
}

/// Concurrent (varying-coefficient) functional regression.
///
/// Estimates a time-varying regression model where each predictor has its own
/// smooth coefficient curve β_j(t). The response functional curve is modelled
/// as ``y(t) = β₀(t) + β₁(t)·x₁(t) + … + β_p(t)·x_p(t)`` and the
/// coefficients are estimated pointwise via local-linear kernel smoothing.
///
/// Parameters
/// ----------
/// predictors : list[numpy.ndarray]
///     List of p predictor matrices, each shape (n, m). One matrix per
///     predictor; the list must be non-empty.
/// response : numpy.ndarray
///     Functional response matrix, shape (n, m).
/// argvals : numpy.ndarray, optional
///     Evaluation grid, length m. ``None`` generates a uniform [0, 1] grid.
/// bandwidth : float, optional
///     Kernel bandwidth (must be > 0 and finite, default 0.2).
/// kernel : str, optional
///     Kernel name: ``"gaussian"``, ``"epanechnikov"``, or ``"tricube"``
///     (default ``"gaussian"``).
///
/// Returns
/// -------
/// dict
///     beta_curve (p, m), intercept (m,), fitted (n, m),
///     residuals (n, m), argvals (m,).
///
/// Raises
/// ------
/// ValueError
///     On empty predictor list, bandwidth <= 0, shape mismatches, or
///     underdetermined systems (n <= p).
#[pyfunction]
#[pyo3(signature = (predictors, response, argvals=None, bandwidth=0.2, kernel="gaussian"))]
pub fn concurrent_regression<'py>(
    py: Python<'py>,
    predictors: Vec<PyReadonlyArray2<'py, f64>>,
    response: PyReadonlyArray2<'py, f64>,
    argvals: Option<PyReadonlyArray1<'py, f64>>,
    bandwidth: f64,
    kernel: &str,
) -> PyResult<Bound<'py, PyAny>> {
    let pred_mats: Vec<fdars_core::matrix::FdMatrix> = predictors
        .into_iter()
        .map(numpy2d_to_fdmatrix)
        .collect::<PyResult<Vec<_>>>()?;
    let resp_mat = numpy2d_to_fdmatrix(response)?;
    let av: Option<Vec<f64>> = argvals.map(numpy1d_to_vec);
    let result = to_pyresult(fdars_core::concurrent_regression::concurrent_regression(
        &resp_mat,
        &pred_mats,
        av.as_deref(),
        bandwidth,
        kernel,
    ))?;
    concurrent_regr_result_to_pydict(py, result)
}

// ---------------------------------------------------------------------------
// Internal helper: &str → GlmFamily dispatch.
//
// GlmFamily is #[non_exhaustive] — the wildcard arm is mandatory so that a
// future upstream variant cannot silently pass through as a compile error.
// An unknown string becomes a Python ValueError listing the accepted values.
// ---------------------------------------------------------------------------

fn family_from_str(s: &str) -> PyResult<fdars_core::scalar_on_function::GlmFamily> {
    use fdars_core::scalar_on_function::GlmFamily;
    match s {
        "binomial" => Ok(GlmFamily::Binomial),
        "poisson" => Ok(GlmFamily::Poisson),
        "gamma" => Ok(GlmFamily::Gamma),
        "gaussian" => Ok(GlmFamily::Gaussian),
        _ => Err(pyo3::exceptions::PyValueError::new_err(format!(
            "family must be 'binomial', 'poisson', 'gamma', or 'gaussian', got '{s}'"
        ))),
    }
}

// ---------------------------------------------------------------------------
// Internal helper: FunctionalGlmResult → Python dict.
//
// The struct is #[non_exhaustive] — access each field by name.
// 15 keys are exposed (the 14 non-fpca struct fields plus a derived "family"
// string); r.fpca is intentionally NOT inserted — the embedded FpcaResult is
// consumed internally for fit only (mirrors flm_f_test pattern).
//
// DOCS caveat (Phase 41, DOCS-08):
//   - Gamma uses inverse canonical link g(μ)=1/μ, NOT log-link (unlike R default).
//   - functional_glm AIC magnitude is not comparable to R glm() AIC.
// ---------------------------------------------------------------------------

fn functional_glm_result_to_pydict<'py>(
    py: Python<'py>,
    r: fdars_core::scalar_on_function::FunctionalGlmResult,
) -> PyResult<Bound<'py, PyAny>> {
    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("intercept", r.intercept)?;
    dict.set_item("beta_t", vec_to_numpy1d(py, r.beta_t))?;
    dict.set_item("beta_se", vec_to_numpy1d(py, r.beta_se))?;
    dict.set_item("gamma", vec_to_numpy1d(py, r.gamma))?;
    dict.set_item("fitted_values", vec_to_numpy1d(py, r.fitted_values))?;
    dict.set_item("linear_predictors", vec_to_numpy1d(py, r.linear_predictors))?;
    dict.set_item("ncomp", r.ncomp)?;
    dict.set_item("coefficients", vec_to_numpy1d(py, r.coefficients))?;
    dict.set_item("std_errors", vec_to_numpy1d(py, r.std_errors))?;
    dict.set_item("log_likelihood", r.log_likelihood)?;
    dict.set_item("deviance", r.deviance)?;
    dict.set_item("iterations", r.iterations)?;
    dict.set_item("aic", r.aic)?;
    dict.set_item("bic", r.bic)?;
    // family exposed as string matching the accepted input tokens
    let family_str = match r.family {
        fdars_core::scalar_on_function::GlmFamily::Binomial => "binomial",
        fdars_core::scalar_on_function::GlmFamily::Poisson => "poisson",
        fdars_core::scalar_on_function::GlmFamily::Gamma => "gamma",
        fdars_core::scalar_on_function::GlmFamily::Gaussian => "gaussian",
        // wildcard required: GlmFamily is #[non_exhaustive]
        _ => "unknown",
    };
    dict.set_item("family", family_str)?;
    // r.fpca is intentionally NOT inserted — embedded for internal use only
    Ok(dict.into_any())
}

/// Functional generalised linear model (GLM) via FPC scores.
///
/// Fits an exponential-family GLM where the linear predictor is formed by
/// projecting functional data onto functional principal components. FPCA is
/// re-fitted from raw data inside this call (no persistent handle required).
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Functional predictors, shape (n, m).
/// response : numpy.ndarray
///     Scalar response, length n. Domain constraints vary by family:
///     Binomial y ∈ {0.0, 1.0}; Poisson y ≥ 0 (integers); Gamma y > 0.
/// family : str, optional
///     Link family: ``"gaussian"`` (identity), ``"binomial"`` (logit),
///     ``"poisson"`` (log), or ``"gamma"`` (inverse link, NOT log).
///     Default ``"gaussian"``.
/// n_comp : int, optional
///     Number of FPC components (default 3; clamped to min(n-1, m) by core).
/// scalar_covariates : numpy.ndarray, optional
///     Additional scalar predictors, shape (n, q). ``None`` if unused.
/// max_iter : int, optional
///     Maximum IRLS iterations (default 25).
/// tol : float, optional
///     Convergence tolerance (default 1e-6).
///
/// Returns
/// -------
/// dict
///     intercept, beta_t (m,), beta_se (m,), gamma (q,), fitted_values (n,),
///     linear_predictors (n,), ncomp, coefficients, std_errors,
///     log_likelihood, deviance, iterations, aic, bic, family.
///
/// Raises
/// ------
/// ValueError
///     On invalid family string, out-of-domain response values, shape
///     mismatches, or insufficient observations (n < 3).
#[pyfunction]
#[pyo3(signature = (data, response, family="gaussian", n_comp=3, scalar_covariates=None, max_iter=25, tol=1e-6))]
pub fn functional_glm<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    response: PyReadonlyArray1<'py, f64>,
    family: &str,
    n_comp: usize,
    scalar_covariates: Option<PyReadonlyArray2<'py, f64>>,
    max_iter: usize,
    tol: f64,
) -> PyResult<Bound<'py, PyAny>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let y = numpy1d_to_vec(response);
    let fam = family_from_str(family)?;
    let sc = scalar_covariates.map(numpy2d_to_fdmatrix).transpose()?;
    let result = to_pyresult(fdars_core::scalar_on_function::functional_glm(
        &mat,
        &y,
        fam,
        sc.as_ref(),
        n_comp,
        max_iter,
        tol,
    ))?;
    functional_glm_result_to_pydict(py, result)
}

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(fregre_np_cv, m)?)?;
    m.add_function(wrap_pyfunction!(fregre_np_mixed, m)?)?;
    m.add_function(wrap_pyfunction!(fpca, m)?)?;
    m.add_function(wrap_pyfunction!(fpls, m)?)?;
    m.add_function(wrap_pyfunction!(fregre_lm, m)?)?;
    m.add_function(wrap_pyfunction!(fregre_pls, m)?)?;
    m.add_function(wrap_pyfunction!(fregre_np, m)?)?;
    m.add_function(wrap_pyfunction!(fregre_l1, m)?)?;
    m.add_function(wrap_pyfunction!(fregre_huber, m)?)?;
    m.add_function(wrap_pyfunction!(functional_logistic, m)?)?;
    m.add_function(wrap_pyfunction!(fosr, m)?)?;
    m.add_function(wrap_pyfunction!(fanova, m)?)?;
    m.add_function(wrap_pyfunction!(model_selection_ncomp, m)?)?;
    m.add_function(wrap_pyfunction!(predict_fregre_lm, m)?)?;
    m.add_function(wrap_pyfunction!(predict_fregre_pls, m)?)?;
    m.add_function(wrap_pyfunction!(predict_fregre_robust, m)?)?;
    m.add_function(wrap_pyfunction!(predict_functional_logistic, m)?)?;
    m.add_function(wrap_pyfunction!(fregre_cv, m)?)?;
    m.add_function(wrap_pyfunction!(bootstrap_ci_fregre_lm, m)?)?;
    m.add_function(wrap_pyfunction!(bootstrap_ci_functional_logistic, m)?)?;
    m.add_function(wrap_pyfunction!(fosr_fpc, m)?)?;
    m.add_function(wrap_pyfunction!(predict_fosr, m)?)?;
    m.add_function(wrap_pyfunction!(concurrent_regression, m)?)?;
    m.add_function(wrap_pyfunction!(functional_glm, m)?)?;
    m.add_function(wrap_pyfunction!(fof_regression, m)?)?;
    m.add_function(wrap_pyfunction!(predict_fof, m)?)?;
    m.add_function(wrap_pyfunction!(fof_cv, m)?)?;
    m.add_function(wrap_pyfunction!(fof_re_regression, m)?)?;
    m.add_function(wrap_pyfunction!(predict_fof_re, m)?)?;
    Ok(())
}

// ---------------------------------------------------------------------------
// Function-on-Function Regression (Phase 68, Plans 01-02)
// ---------------------------------------------------------------------------

/// Function-on-function linear regression via FPC basis decomposition.
///
/// Fits a linear model mapping a functional predictor X(t) to a functional
/// response Y(s) through the integral equation:
/// Y(s) = α(s) + ∫ β(s,t) X(t) dt + ε(s).
///
/// Parameters
/// ----------
/// x_data : numpy.ndarray
///     Functional predictor, shape (n, m_x). Rows are observations, columns
///     are evaluation points on the predictor grid.
/// y_data : numpy.ndarray
///     Functional response, shape (n, m_y). Rows are observations, columns
///     are evaluation points on the response grid.
/// x_argvals : numpy.ndarray
///     Predictor grid evaluation points, length m_x.
/// y_argvals : numpy.ndarray
///     Response grid evaluation points, length m_y.
/// ncomp_x : int, optional
///     Number of predictor FPC components (default 3).
/// ncomp_y : int, optional
///     Number of response FPC components (default 3).
///
/// Returns
/// -------
/// dict
///     intercept (m_y,), beta_surface (m_y, m_x), fitted (n, m_y),
///     residuals (n, m_y), r_squared_t (m_y,), r_squared (float),
///     ncomp_x (int), ncomp_y (int), coef_matrix (ncomp_x, ncomp_y).
///
/// Notes
/// -----
/// ``beta_surface`` has shape ``(m_y, m_x)``: rows index the response grid,
/// columns index the predictor grid. The embedded ``fpca_x`` and ``fpca_y``
/// fields of the internal result are intentionally excluded from the returned
/// dict — they are internal FPCA state not needed by callers.
///
/// Raises
/// ------
/// ValueError
///     If n_obs mismatch between x_data and y_data, argvals length mismatch,
///     n < 3, or ncomp_x / ncomp_y is 0.
#[pyfunction]
#[pyo3(signature = (x_data, y_data, x_argvals, y_argvals, ncomp_x=3, ncomp_y=3))]
pub fn fof_regression<'py>(
    py: Python<'py>,
    x_data: PyReadonlyArray2<'py, f64>,
    y_data: PyReadonlyArray2<'py, f64>,
    x_argvals: PyReadonlyArray1<'py, f64>,
    y_argvals: PyReadonlyArray1<'py, f64>,
    ncomp_x: usize,
    ncomp_y: usize,
) -> PyResult<Bound<'py, PyAny>> {
    let x_mat = numpy2d_to_fdmatrix(x_data)?;
    let y_mat = numpy2d_to_fdmatrix(y_data)?;
    let ax = numpy1d_to_vec(x_argvals);
    let ay = numpy1d_to_vec(y_argvals);
    let result = to_pyresult(fdars_core::fof_regression::fof_regression(
        &x_mat, &y_mat, &ax, &ay, ncomp_x, ncomp_y,
    ))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("intercept", vec_to_numpy1d(py, result.intercept))?;
    dict.set_item("beta_surface", fdmatrix_to_numpy2d(py, &result.beta_surface))?;
    dict.set_item("fitted", fdmatrix_to_numpy2d(py, &result.fitted))?;
    dict.set_item("residuals", fdmatrix_to_numpy2d(py, &result.residuals))?;
    dict.set_item("r_squared_t", vec_to_numpy1d(py, result.r_squared_t))?;
    dict.set_item("r_squared", result.r_squared)?;
    dict.set_item("ncomp_x", result.ncomp_x)?;
    dict.set_item("ncomp_y", result.ncomp_y)?;
    dict.set_item("coef_matrix", fdmatrix_to_numpy2d(py, &result.coef_matrix))?;
    // fpca_x and fpca_y are intentionally NOT exposed — internal FPCA state
    Ok(dict.into_any())
}

/// Predict functional responses for new predictor curves using a function-on-function model.
///
/// Uses the combined-refit pattern: the model is re-fitted from training data
/// internally, then applied to ``new_x``. No opaque model handle is required.
///
/// Parameters
/// ----------
/// x_data : numpy.ndarray
///     Training predictor, shape (n, m_x).
/// y_data : numpy.ndarray
///     Training response, shape (n, m_y).
/// new_x : numpy.ndarray
///     New predictor curves to predict for, shape (n_new, m_x).
/// x_argvals : numpy.ndarray
///     Predictor grid evaluation points, length m_x.
/// y_argvals : numpy.ndarray
///     Response grid evaluation points, length m_y.
/// ncomp_x : int, optional
///     Number of predictor FPC components (default 3).
/// ncomp_y : int, optional
///     Number of response FPC components (default 3).
///
/// Returns
/// -------
/// numpy.ndarray
///     Predicted response curves, shape (n_new, m_y).
///
/// Raises
/// ------
/// ValueError
///     If shape mismatches, n < 3, argvals length mismatch, or ncomp_x/ncomp_y is 0.
#[pyfunction]
#[pyo3(signature = (x_data, y_data, new_x, x_argvals, y_argvals, ncomp_x=3, ncomp_y=3))]
pub fn predict_fof<'py>(
    py: Python<'py>,
    x_data: PyReadonlyArray2<'py, f64>,
    y_data: PyReadonlyArray2<'py, f64>,
    new_x: PyReadonlyArray2<'py, f64>,
    x_argvals: PyReadonlyArray1<'py, f64>,
    y_argvals: PyReadonlyArray1<'py, f64>,
    ncomp_x: usize,
    ncomp_y: usize,
) -> PyResult<Bound<'py, PyAny>> {
    let x_mat = numpy2d_to_fdmatrix(x_data)?;
    let y_mat = numpy2d_to_fdmatrix(y_data)?;
    let new_x_mat = numpy2d_to_fdmatrix(new_x)?;
    let ax = numpy1d_to_vec(x_argvals);
    let ay = numpy1d_to_vec(y_argvals);
    let fit = to_pyresult(fdars_core::fof_regression::fof_regression(
        &x_mat, &y_mat, &ax, &ay, ncomp_x, ncomp_y,
    ))?;
    let predicted = to_pyresult(fdars_core::fof_regression::predict_fof(&fit, &new_x_mat))?;
    Ok(fdmatrix_to_numpy2d(py, &predicted).into_any())
}

/// Cross-validated selection of FPC component counts for function-on-function regression.
///
/// Performs K-fold CV over a grid of ``(ncomp_x, ncomp_y)`` pairs and returns
/// the pair that minimises the integrated CV-MSE.
///
/// Parameters
/// ----------
/// x_data : numpy.ndarray
///     Functional predictor, shape (n, m_x).
/// y_data : numpy.ndarray
///     Functional response, shape (n, m_y).
/// x_argvals : numpy.ndarray
///     Predictor grid evaluation points, length m_x.
/// y_argvals : numpy.ndarray
///     Response grid evaluation points, length m_y.
/// ncomp_x_max : int, optional
///     Maximum predictor FPC components to test (default 5).
/// ncomp_y_max : int, optional
///     Maximum response FPC components to test (default 5).
/// n_folds : int, optional
///     Number of CV folds (default 5). Must be <= n.
/// seed : int, optional
///     Random seed for fold assignment (default 42).
///
/// Returns
/// -------
/// dict
///     candidates (list of (int, int)), cv_errors (n_candidates,),
///     optimal (tuple (int, int)), min_cv_mse (float).
///
/// Raises
/// ------
/// ValueError
///     If n < n_folds, or no valid component pair produces CV errors.
#[pyfunction]
#[pyo3(signature = (x_data, y_data, x_argvals, y_argvals, ncomp_x_max=5, ncomp_y_max=5, n_folds=5, seed=42))]
pub fn fof_cv<'py>(
    py: Python<'py>,
    x_data: PyReadonlyArray2<'py, f64>,
    y_data: PyReadonlyArray2<'py, f64>,
    x_argvals: PyReadonlyArray1<'py, f64>,
    y_argvals: PyReadonlyArray1<'py, f64>,
    ncomp_x_max: usize,
    ncomp_y_max: usize,
    n_folds: usize,
    seed: u64,
) -> PyResult<Bound<'py, PyAny>> {
    let x_mat = numpy2d_to_fdmatrix(x_data)?;
    let y_mat = numpy2d_to_fdmatrix(y_data)?;
    let ax = numpy1d_to_vec(x_argvals);
    let ay = numpy1d_to_vec(y_argvals);
    let result = to_pyresult(fdars_core::fof_regression::fof_cv(
        &x_mat, &y_mat, &ax, &ay, ncomp_x_max, ncomp_y_max, n_folds, seed,
    ))?;

    let dict = pyo3::types::PyDict::new(py);
    // candidates: Vec<(usize, usize)> → Vec<(i64, i64)> for Python
    let candidates_list: Vec<(i64, i64)> = result
        .candidates
        .iter()
        .map(|&(x, y)| (x as i64, y as i64))
        .collect();
    dict.set_item("candidates", candidates_list)?;
    dict.set_item("cv_errors", vec_to_numpy1d(py, result.cv_errors))?;
    // optimal: (usize, usize) → (i64, i64) tuple
    dict.set_item(
        "optimal",
        (result.optimal.0 as i64, result.optimal.1 as i64),
    )?;
    dict.set_item("min_cv_mse", result.min_cv_mse)?;
    Ok(dict.into_any())
}

// ---------------------------------------------------------------------------
// Internal helper: validate subject_ids for fof_re_regression.
//
// REG-02 validation: upstream validates length mismatch via FdarError, but does
// NOT enforce ≥2 distinct groups. The binding adds this check before calling core.
// ---------------------------------------------------------------------------

fn validate_subject_ids(
    sid: &[usize],
    n_obs: usize,
) -> PyResult<()> {
    if sid.len() != n_obs {
        return Err(pyo3::exceptions::PyValueError::new_err(format!(
            "subject_ids length {} does not match x_data rows {}",
            sid.len(),
            n_obs
        )));
    }
    let n_subjects = {
        let mut sorted = sid.to_vec();
        sorted.sort_unstable();
        sorted.dedup();
        sorted.len()
    };
    if n_subjects < 2 {
        return Err(pyo3::exceptions::PyValueError::new_err(
            "subject_ids must contain at least 2 distinct subjects for random-effects regression",
        ));
    }
    Ok(())
}

/// Function-on-function random-effects regression (mixed model).
///
/// Fits a mixed-effects FOF model with subject-specific random intercept
/// functions. Requires ≥ 2 distinct subjects (groups) in ``subject_ids``.
///
/// Parameters
/// ----------
/// x_data : numpy.ndarray
///     Functional predictor, shape (n, m_x).
/// y_data : numpy.ndarray
///     Functional response, shape (n, m_y).
/// subject_ids : numpy.ndarray
///     Integer group label per observation, length n. Must be non-negative
///     i64 values; at least 2 distinct groups are required.
/// x_argvals : numpy.ndarray
///     Predictor grid evaluation points, length m_x.
/// y_argvals : numpy.ndarray
///     Response grid evaluation points, length m_y.
/// ncomp_x : int, optional
///     Number of predictor FPC components (default 3).
/// ncomp_y : int, optional
///     Number of response FPC components (default 3).
/// max_iter : int, optional
///     Maximum REML EM iterations (default 50).
/// tol : float, optional
///     Convergence tolerance (default 1e-10).
///
/// Returns
/// -------
/// dict
///     intercept (m_y,), beta_surface (m_y, m_x), fitted (n, m_y),
///     residuals (n, m_y), r_squared_t (m_y,), r_squared (float),
///     ncomp_x (int), ncomp_y (int), coef_matrix (ncomp_x, ncomp_y),
///     random_effects (n_subjects, m_y), sigma2_u (ncomp_y,),
///     sigma2_eps (float), n_subjects (int).
///
/// Raises
/// ------
/// ValueError
///     If subject_ids length != n, fewer than 2 distinct subjects,
///     shape mismatches, n < 3, argvals length mismatch, or ncomp is 0.
#[pyfunction]
#[pyo3(signature = (x_data, y_data, subject_ids, x_argvals, y_argvals, ncomp_x=3, ncomp_y=3, max_iter=50, tol=1e-10))]
pub fn fof_re_regression<'py>(
    py: Python<'py>,
    x_data: PyReadonlyArray2<'py, f64>,
    y_data: PyReadonlyArray2<'py, f64>,
    subject_ids: PyReadonlyArray1<'py, i64>,
    x_argvals: PyReadonlyArray1<'py, f64>,
    y_argvals: PyReadonlyArray1<'py, f64>,
    ncomp_x: usize,
    ncomp_y: usize,
    max_iter: usize,
    tol: f64,
) -> PyResult<Bound<'py, PyAny>> {
    let x_mat = numpy2d_to_fdmatrix(x_data)?;
    let y_mat = numpy2d_to_fdmatrix(y_data)?;
    let sid = numpy1d_to_usize_vec(subject_ids);
    let ax = numpy1d_to_vec(x_argvals);
    let ay = numpy1d_to_vec(y_argvals);

    // REG-02: validate subject_ids before calling upstream
    validate_subject_ids(&sid, x_mat.nrows())?;

    let config = fdars_core::fof_regression::FofReConfig {
        ncomp_x,
        ncomp_y,
        max_iter,
        tol,
    };
    let result = to_pyresult(fdars_core::fof_regression::fof_re_regression(
        &x_mat, &y_mat, &sid, &ax, &ay, &config,
    ))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("intercept", vec_to_numpy1d(py, result.intercept))?;
    dict.set_item("beta_surface", fdmatrix_to_numpy2d(py, &result.beta_surface))?;
    dict.set_item("fitted", fdmatrix_to_numpy2d(py, &result.fitted))?;
    dict.set_item("residuals", fdmatrix_to_numpy2d(py, &result.residuals))?;
    dict.set_item("r_squared_t", vec_to_numpy1d(py, result.r_squared_t))?;
    dict.set_item("r_squared", result.r_squared)?;
    dict.set_item("ncomp_x", result.ncomp_x)?;
    dict.set_item("ncomp_y", result.ncomp_y)?;
    dict.set_item("coef_matrix", fdmatrix_to_numpy2d(py, &result.coef_matrix))?;
    dict.set_item("random_effects", fdmatrix_to_numpy2d(py, &result.random_effects))?;
    dict.set_item("sigma2_u", vec_to_numpy1d(py, result.sigma2_u))?;
    dict.set_item("sigma2_eps", result.sigma2_eps)?;
    dict.set_item("n_subjects", result.n_subjects)?;
    // fpca_x and fpca_y are intentionally NOT exposed — internal FPCA state
    Ok(dict.into_any())
}

/// Predict functional responses using a function-on-function random-effects model.
///
/// Uses the combined-refit pattern: the mixed model is re-fitted from training
/// data internally, then applied to ``new_x``. Unseen subjects (not in
/// ``subject_ids``) receive population-level (fixed-effect-only) predictions.
///
/// Parameters
/// ----------
/// x_data : numpy.ndarray
///     Training predictor, shape (n, m_x).
/// y_data : numpy.ndarray
///     Training response, shape (n, m_y).
/// subject_ids : numpy.ndarray
///     Integer group label per observation, length n. Must have ≥ 2 distinct
///     groups.
/// new_x : numpy.ndarray
///     New predictor curves to predict for, shape (n_new, m_x).
/// x_argvals : numpy.ndarray
///     Predictor grid evaluation points, length m_x.
/// y_argvals : numpy.ndarray
///     Response grid evaluation points, length m_y.
/// ncomp_x : int, optional
///     Number of predictor FPC components (default 3).
/// ncomp_y : int, optional
///     Number of response FPC components (default 3).
/// max_iter : int, optional
///     Maximum REML EM iterations (default 50).
/// tol : float, optional
///     Convergence tolerance (default 1e-10).
///
/// Returns
/// -------
/// numpy.ndarray
///     Predicted response curves, shape (n_new, m_y).
///
/// Raises
/// ------
/// ValueError
///     If subject_ids length != n, fewer than 2 distinct subjects,
///     shape mismatches, n < 3, argvals length mismatch, or ncomp is 0.
#[pyfunction]
#[pyo3(signature = (x_data, y_data, subject_ids, new_x, x_argvals, y_argvals, ncomp_x=3, ncomp_y=3, max_iter=50, tol=1e-10))]
pub fn predict_fof_re<'py>(
    py: Python<'py>,
    x_data: PyReadonlyArray2<'py, f64>,
    y_data: PyReadonlyArray2<'py, f64>,
    subject_ids: PyReadonlyArray1<'py, i64>,
    new_x: PyReadonlyArray2<'py, f64>,
    x_argvals: PyReadonlyArray1<'py, f64>,
    y_argvals: PyReadonlyArray1<'py, f64>,
    ncomp_x: usize,
    ncomp_y: usize,
    max_iter: usize,
    tol: f64,
) -> PyResult<Bound<'py, PyAny>> {
    let x_mat = numpy2d_to_fdmatrix(x_data)?;
    let y_mat = numpy2d_to_fdmatrix(y_data)?;
    let sid = numpy1d_to_usize_vec(subject_ids);
    let new_x_mat = numpy2d_to_fdmatrix(new_x)?;
    let ax = numpy1d_to_vec(x_argvals);
    let ay = numpy1d_to_vec(y_argvals);

    // REG-02: same subject-id validation as fof_re_regression
    validate_subject_ids(&sid, x_mat.nrows())?;

    let config = fdars_core::fof_regression::FofReConfig {
        ncomp_x,
        ncomp_y,
        max_iter,
        tol,
    };
    let fit = to_pyresult(fdars_core::fof_regression::fof_re_regression(
        &x_mat, &y_mat, &sid, &ax, &ay, &config,
    ))?;
    let predicted = to_pyresult(fdars_core::fof_regression::predict_fof_re(&fit, &new_x_mat))?;
    Ok(fdmatrix_to_numpy2d(py, &predicted).into_any())
}
