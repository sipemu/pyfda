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

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
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
    Ok(())
}
