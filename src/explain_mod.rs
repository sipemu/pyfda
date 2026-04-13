//! Explainability methods for functional regression models.

use crate::convert::*;
use numpy::{PyArray1, PyReadonlyArray1, PyReadonlyArray2};
use pyo3::prelude::*;

/// FPC-based permutation importance.
///
/// Fits a linear regression model internally, then computes permutation importance.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Functional predictors, shape (n, m).
/// response : numpy.ndarray
///     Scalar response, length n.
/// ncomp : int, optional
///     Number of FPC components (default 3).
/// n_perm : int, optional
///     Number of permutation repeats (default 10).
/// seed : int, optional
///     Random seed (default 42).
///
/// Returns
/// -------
/// dict
///     importance (ncomp,), baseline_metric, permuted_metric (ncomp,).
#[pyfunction]
#[pyo3(signature = (data, response, ncomp=3, n_perm=10, seed=42))]
pub fn fpc_permutation_importance<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    response: PyReadonlyArray1<'py, f64>,
    ncomp: usize,
    n_perm: usize,
    seed: u64,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let resp = numpy1d_to_vec(response);
    let fit = to_pyresult(fdars_core::scalar_on_function::fregre_lm(
        &mat, &resp, None, ncomp,
    ))?;
    let result = to_pyresult(fdars_core::explain::fpc_permutation_importance(
        &fit, &mat, &resp, n_perm, seed,
    ))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("importance", vec_to_numpy1d(py, result.importance))?;
    dict.set_item("baseline_metric", result.baseline_metric)?;
    dict.set_item(
        "permuted_metric",
        vec_to_numpy1d(py, result.permuted_metric),
    )?;
    Ok(dict)
}

/// Functional partial dependence plot.
///
/// Fits a linear regression model internally, then computes PDP.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Functional predictors, shape (n, m).
/// response : numpy.ndarray
///     Scalar response, length n.
/// ncomp : int, optional
///     Number of FPC components (default 3).
/// component : int, optional
///     Which FPC to plot PDP for (default 0).
/// n_grid : int, optional
///     Grid points for PDP (default 50).
///
/// Returns
/// -------
/// dict
///     grid_values (n_grid,), pdp_curve (n_grid,), component (int).
#[pyfunction]
#[pyo3(signature = (data, response, ncomp=3, component=0, n_grid=50))]
pub fn functional_pdp<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    response: PyReadonlyArray1<'py, f64>,
    ncomp: usize,
    component: usize,
    n_grid: usize,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let resp = numpy1d_to_vec(response);
    let fit = to_pyresult(fdars_core::scalar_on_function::fregre_lm(
        &mat, &resp, None, ncomp,
    ))?;
    let result = to_pyresult(fdars_core::explain::functional_pdp(
        &fit, &mat, None, component, n_grid,
    ))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("grid_values", vec_to_numpy1d(py, result.grid_values))?;
    dict.set_item("pdp_curve", vec_to_numpy1d(py, result.pdp_curve))?;
    dict.set_item("component", result.component)?;
    Ok(dict)
}

/// FPC SHAP values.
///
/// Fits a linear regression model internally, then computes SHAP values.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Functional predictors, shape (n, m).
/// response : numpy.ndarray
///     Scalar response, length n.
/// ncomp : int, optional
///     Number of FPC components (default 3).
///
/// Returns
/// -------
/// dict
///     values (n, ncomp), base_value.
#[pyfunction]
#[pyo3(signature = (data, response, ncomp=3))]
pub fn fpc_shap_values<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    response: PyReadonlyArray1<'py, f64>,
    ncomp: usize,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let resp = numpy1d_to_vec(response);
    let fit = to_pyresult(fdars_core::scalar_on_function::fregre_lm(
        &mat, &resp, None, ncomp,
    ))?;
    let result = to_pyresult(fdars_core::explain::fpc_shap_values(&fit, &mat, None))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("values", fdmatrix_to_numpy2d(py, &result.values))?;
    dict.set_item("base_value", result.base_value)?;
    Ok(dict)
}

/// Significant regions of the beta function.
///
/// Parameters
/// ----------
/// lower : numpy.ndarray
///     Lower CI bounds, length m.
/// upper : numpy.ndarray
///     Upper CI bounds, length m.
///
/// Returns
/// -------
/// list
///     List of (start_idx, end_idx, direction) tuples.
#[pyfunction]
pub fn significant_regions<'py>(
    py: Python<'py>,
    lower: PyReadonlyArray1<'py, f64>,
    upper: PyReadonlyArray1<'py, f64>,
) -> PyResult<Bound<'py, pyo3::types::PyList>> {
    let lo = numpy1d_to_vec(lower);
    let up = numpy1d_to_vec(upper);
    let result = to_pyresult(fdars_core::explain::significant_regions(&lo, &up))?;

    let regions: Vec<(usize, usize, &str)> = result
        .iter()
        .map(|r| {
            let dir = match r.direction {
                fdars_core::explain::SignificanceDirection::Positive => "positive",
                fdars_core::explain::SignificanceDirection::Negative => "negative",
                _ => "unknown",
            };
            (r.start_idx, r.end_idx, dir)
        })
        .collect();
    pyo3::types::PyList::new(py, regions)
}

/// Beta function decomposition.
///
/// Fits a linear regression model internally, then decomposes beta(t).
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Functional predictors, shape (n, m).
/// response : numpy.ndarray
///     Scalar response, length n.
/// ncomp : int, optional
///     Number of FPC components (default 3).
///
/// Returns
/// -------
/// dict
///     components (list of (m,) arrays), coefficients (ncomp,), variance_proportion (ncomp,).
#[pyfunction]
#[pyo3(signature = (data, response, ncomp=3))]
pub fn beta_decomposition<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    response: PyReadonlyArray1<'py, f64>,
    ncomp: usize,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let resp = numpy1d_to_vec(response);
    let fit = to_pyresult(fdars_core::scalar_on_function::fregre_lm(
        &mat, &resp, None, ncomp,
    ))?;
    let result = to_pyresult(fdars_core::explain::beta_decomposition(&fit))?;

    let dict = pyo3::types::PyDict::new(py);
    let components: Vec<Bound<'py, PyArray1<f64>>> = result
        .components
        .into_iter()
        .map(|c| vec_to_numpy1d(py, c))
        .collect();
    dict.set_item("components", components)?;
    dict.set_item("coefficients", vec_to_numpy1d(py, result.coefficients))?;
    dict.set_item(
        "variance_proportion",
        vec_to_numpy1d(py, result.variance_proportion),
    )?;
    Ok(dict)
}

/// Functional PDP/ICE for a logistic regression model.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Functional predictors, shape (n, m).
/// labels : numpy.ndarray
///     Binary labels (0/1), length n.
/// ncomp : int, optional
///     Number of FPC components (default 3).
/// component : int, optional
///     Which FPC to plot PDP for (default 0).
/// n_grid : int, optional
///     Grid points (default 50).
///
/// Returns
/// -------
/// dict
///     grid_values (n_grid,), pdp_curve (n_grid,), component (int).
#[pyfunction]
#[pyo3(signature = (data, labels, ncomp=3, component=0, n_grid=50))]
pub fn functional_pdp_logistic<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    labels: PyReadonlyArray1<'py, f64>,
    ncomp: usize,
    component: usize,
    n_grid: usize,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let lab = numpy1d_to_vec(labels);
    let fit = to_pyresult(fdars_core::scalar_on_function::functional_logistic(
        &mat, &lab, None, ncomp, 25, 1e-6,
    ))?;
    let result = to_pyresult(fdars_core::explain::functional_pdp_logistic(
        &fit, &mat, None, component, n_grid,
    ))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("grid_values", vec_to_numpy1d(py, result.grid_values))?;
    dict.set_item("pdp_curve", vec_to_numpy1d(py, result.pdp_curve))?;
    dict.set_item("component", result.component)?;
    Ok(dict)
}

/// Beta decomposition for a logistic regression model.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Functional predictors, shape (n, m).
/// labels : numpy.ndarray
///     Binary labels (0/1), length n.
/// ncomp : int, optional
///     Number of FPC components (default 3).
///
/// Returns
/// -------
/// dict
///     components (list of (m,) arrays), coefficients (ncomp,), variance_proportion (ncomp,).
#[pyfunction]
#[pyo3(signature = (data, labels, ncomp=3))]
pub fn beta_decomposition_logistic<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    labels: PyReadonlyArray1<'py, f64>,
    ncomp: usize,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let lab = numpy1d_to_vec(labels);
    let fit = to_pyresult(fdars_core::scalar_on_function::functional_logistic(
        &mat, &lab, None, ncomp, 25, 1e-6,
    ))?;
    let result = to_pyresult(fdars_core::explain::beta_decomposition_logistic(&fit))?;

    let dict = pyo3::types::PyDict::new(py);
    let components: Vec<Bound<'py, PyArray1<f64>>> = result
        .components
        .into_iter()
        .map(|c| vec_to_numpy1d(py, c))
        .collect();
    dict.set_item("components", components)?;
    dict.set_item("coefficients", vec_to_numpy1d(py, result.coefficients))?;
    dict.set_item(
        "variance_proportion",
        vec_to_numpy1d(py, result.variance_proportion),
    )?;
    Ok(dict)
}

/// Significant regions from beta(t) and its standard error.
///
/// Parameters
/// ----------
/// beta_t : numpy.ndarray
///     Beta function values, length m.
/// beta_se : numpy.ndarray
///     Standard errors, length m.
/// z_alpha : float, optional
///     Z critical value (default 1.96 for 95% CI).
///
/// Returns
/// -------
/// list
///     List of (start_idx, end_idx, direction) tuples.
#[pyfunction]
#[pyo3(signature = (beta_t, beta_se, z_alpha=1.96))]
pub fn significant_regions_from_se<'py>(
    py: Python<'py>,
    beta_t: PyReadonlyArray1<'py, f64>,
    beta_se: PyReadonlyArray1<'py, f64>,
    z_alpha: f64,
) -> PyResult<Bound<'py, pyo3::types::PyList>> {
    let bt = numpy1d_to_vec(beta_t);
    let bse = numpy1d_to_vec(beta_se);
    let result = to_pyresult(fdars_core::explain::significant_regions_from_se(
        &bt, &bse, z_alpha,
    ))?;

    let regions: Vec<(usize, usize, &str)> = result
        .iter()
        .map(|r| {
            let dir = match r.direction {
                fdars_core::explain::SignificanceDirection::Positive => "positive",
                fdars_core::explain::SignificanceDirection::Negative => "negative",
                _ => "unknown",
            };
            (r.start_idx, r.end_idx, dir)
        })
        .collect();
    pyo3::types::PyList::new(py, regions)
}

/// FPC permutation importance for a logistic model.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Functional predictors, shape (n, m).
/// labels : numpy.ndarray
///     Binary labels (0/1), length n.
/// ncomp : int, optional
///     Number of FPC components (default 3).
/// n_perm : int, optional
///     Number of permutation repeats (default 10).
/// seed : int, optional
///     Random seed (default 42).
///
/// Returns
/// -------
/// dict
///     importance (ncomp,), baseline_metric, permuted_metric (ncomp,).
#[pyfunction]
#[pyo3(signature = (data, labels, ncomp=3, n_perm=10, seed=42))]
pub fn fpc_permutation_importance_logistic<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    labels: PyReadonlyArray1<'py, f64>,
    ncomp: usize,
    n_perm: usize,
    seed: u64,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let lab = numpy1d_to_vec(labels);
    let fit = to_pyresult(fdars_core::scalar_on_function::functional_logistic(
        &mat, &lab, None, ncomp, 25, 1e-6,
    ))?;
    let result = to_pyresult(fdars_core::explain::fpc_permutation_importance_logistic(
        &fit, &mat, &lab, n_perm, seed,
    ))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("importance", vec_to_numpy1d(py, result.importance))?;
    dict.set_item("baseline_metric", result.baseline_metric)?;
    dict.set_item(
        "permuted_metric",
        vec_to_numpy1d(py, result.permuted_metric),
    )?;
    Ok(dict)
}

/// Pointwise variable importance for a linear regression model.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Functional predictors, shape (n, m).
/// response : numpy.ndarray
///     Scalar response, length n.
/// ncomp : int, optional
///     Number of FPC components (default 3).
///
/// Returns
/// -------
/// dict
///     importance (m,), importance_normalized (m,), component_importance (ncomp, m),
///     score_variance (ncomp,).
#[pyfunction]
#[pyo3(signature = (data, response, ncomp=3))]
pub fn pointwise_importance<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    response: PyReadonlyArray1<'py, f64>,
    ncomp: usize,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let resp = numpy1d_to_vec(response);
    let fit = to_pyresult(fdars_core::scalar_on_function::fregre_lm(
        &mat, &resp, None, ncomp,
    ))?;
    let result = to_pyresult(fdars_core::explain::pointwise_importance(&fit))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("importance", vec_to_numpy1d(py, result.importance))?;
    dict.set_item(
        "importance_normalized",
        vec_to_numpy1d(py, result.importance_normalized),
    )?;
    dict.set_item(
        "component_importance",
        fdmatrix_to_numpy2d(py, &result.component_importance),
    )?;
    dict.set_item("score_variance", vec_to_numpy1d(py, result.score_variance))?;
    Ok(dict)
}

/// Pointwise variable importance for a logistic regression model.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Functional predictors, shape (n, m).
/// labels : numpy.ndarray
///     Binary labels (0/1), length n.
/// ncomp : int, optional
///     Number of FPC components (default 3).
///
/// Returns
/// -------
/// dict
///     importance (m,), importance_normalized (m,), component_importance (ncomp, m),
///     score_variance (ncomp,).
#[pyfunction]
#[pyo3(signature = (data, labels, ncomp=3))]
pub fn pointwise_importance_logistic<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    labels: PyReadonlyArray1<'py, f64>,
    ncomp: usize,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let lab = numpy1d_to_vec(labels);
    let fit = to_pyresult(fdars_core::scalar_on_function::functional_logistic(
        &mat, &lab, None, ncomp, 25, 1e-6,
    ))?;
    let result = to_pyresult(fdars_core::explain::pointwise_importance_logistic(&fit))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("importance", vec_to_numpy1d(py, result.importance))?;
    dict.set_item(
        "importance_normalized",
        vec_to_numpy1d(py, result.importance_normalized),
    )?;
    dict.set_item(
        "component_importance",
        fdmatrix_to_numpy2d(py, &result.component_importance),
    )?;
    dict.set_item("score_variance", vec_to_numpy1d(py, result.score_variance))?;
    Ok(dict)
}

/// Conditional permutation importance for a linear regression model.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Functional predictors, shape (n, m).
/// response : numpy.ndarray
///     Scalar response, length n.
/// ncomp : int, optional
///     Number of FPC components (default 3).
/// n_bins : int, optional
///     Number of conditioning bins (default 5).
/// n_perm : int, optional
///     Number of permutation repeats (default 10).
/// seed : int, optional
///     Random seed (default 42).
///
/// Returns
/// -------
/// dict
///     importance (ncomp,), baseline_metric, permuted_metric (ncomp,),
///     unconditional_importance (ncomp,).
#[pyfunction]
#[pyo3(signature = (data, response, ncomp=3, n_bins=5, n_perm=10, seed=42))]
pub fn conditional_permutation_importance<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    response: PyReadonlyArray1<'py, f64>,
    ncomp: usize,
    n_bins: usize,
    n_perm: usize,
    seed: u64,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let resp = numpy1d_to_vec(response);
    let fit = to_pyresult(fdars_core::scalar_on_function::fregre_lm(
        &mat, &resp, None, ncomp,
    ))?;
    let result = to_pyresult(fdars_core::explain::conditional_permutation_importance(
        &fit, &mat, &resp, None, n_bins, n_perm, seed,
    ))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("importance", vec_to_numpy1d(py, result.importance))?;
    dict.set_item("baseline_metric", result.baseline_metric)?;
    dict.set_item(
        "permuted_metric",
        vec_to_numpy1d(py, result.permuted_metric),
    )?;
    dict.set_item(
        "unconditional_importance",
        vec_to_numpy1d(py, result.unconditional_importance),
    )?;
    Ok(dict)
}

/// Conditional permutation importance for a logistic regression model.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Functional predictors, shape (n, m).
/// labels : numpy.ndarray
///     Binary labels (0/1), length n.
/// ncomp : int, optional
///     Number of FPC components (default 3).
/// n_bins : int, optional
///     Number of conditioning bins (default 5).
/// n_perm : int, optional
///     Number of permutation repeats (default 10).
/// seed : int, optional
///     Random seed (default 42).
///
/// Returns
/// -------
/// dict
///     importance (ncomp,), baseline_metric, permuted_metric (ncomp,),
///     unconditional_importance (ncomp,).
#[pyfunction]
#[pyo3(signature = (data, labels, ncomp=3, n_bins=5, n_perm=10, seed=42))]
pub fn conditional_permutation_importance_logistic<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    labels: PyReadonlyArray1<'py, f64>,
    ncomp: usize,
    n_bins: usize,
    n_perm: usize,
    seed: u64,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let lab = numpy1d_to_vec(labels);
    let fit = to_pyresult(fdars_core::scalar_on_function::functional_logistic(
        &mat, &lab, None, ncomp, 25, 1e-6,
    ))?;
    let result = to_pyresult(
        fdars_core::explain::conditional_permutation_importance_logistic(
            &fit, &mat, &lab, None, n_bins, n_perm, seed,
        ),
    )?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("importance", vec_to_numpy1d(py, result.importance))?;
    dict.set_item("baseline_metric", result.baseline_metric)?;
    dict.set_item(
        "permuted_metric",
        vec_to_numpy1d(py, result.permuted_metric),
    )?;
    dict.set_item(
        "unconditional_importance",
        vec_to_numpy1d(py, result.unconditional_importance),
    )?;
    Ok(dict)
}

/// Influence diagnostics (Cook's distance, leverage).
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Functional predictors, shape (n, m).
/// response : numpy.ndarray
///     Scalar response, length n.
/// ncomp : int, optional
///     Number of FPC components (default 3).
///
/// Returns
/// -------
/// dict
///     leverage (n,), cooks_distance (n,), p (int), mse (float).
#[pyfunction]
#[pyo3(signature = (data, response, ncomp=3))]
pub fn influence_diagnostics<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    response: PyReadonlyArray1<'py, f64>,
    ncomp: usize,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let resp = numpy1d_to_vec(response);
    let fit = to_pyresult(fdars_core::scalar_on_function::fregre_lm(
        &mat, &resp, None, ncomp,
    ))?;
    let result = to_pyresult(fdars_core::explain::influence_diagnostics(&fit, &mat, None))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("leverage", vec_to_numpy1d(py, result.leverage))?;
    dict.set_item("cooks_distance", vec_to_numpy1d(py, result.cooks_distance))?;
    dict.set_item("p", result.p)?;
    dict.set_item("mse", result.mse)?;
    Ok(dict)
}

/// DFBETAS and DFFITS diagnostics.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Functional predictors, shape (n, m).
/// response : numpy.ndarray
///     Scalar response, length n.
/// ncomp : int, optional
///     Number of FPC components (default 3).
///
/// Returns
/// -------
/// dict
///     dfbetas (n, p), dffits (n,), studentized_residuals (n,), p (int),
///     dfbetas_cutoff, dffits_cutoff.
#[pyfunction]
#[pyo3(signature = (data, response, ncomp=3))]
pub fn dfbetas_dffits<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    response: PyReadonlyArray1<'py, f64>,
    ncomp: usize,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let resp = numpy1d_to_vec(response);
    let fit = to_pyresult(fdars_core::scalar_on_function::fregre_lm(
        &mat, &resp, None, ncomp,
    ))?;
    let result = to_pyresult(fdars_core::explain::dfbetas_dffits(&fit, &mat, None))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("dfbetas", fdmatrix_to_numpy2d(py, &result.dfbetas))?;
    dict.set_item("dffits", vec_to_numpy1d(py, result.dffits))?;
    dict.set_item(
        "studentized_residuals",
        vec_to_numpy1d(py, result.studentized_residuals),
    )?;
    dict.set_item("p", result.p)?;
    dict.set_item("dfbetas_cutoff", result.dfbetas_cutoff)?;
    dict.set_item("dffits_cutoff", result.dffits_cutoff)?;
    Ok(dict)
}

/// Prediction intervals for new observations.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Training data, shape (n, m).
/// response : numpy.ndarray
///     Training response, length n.
/// new_data : numpy.ndarray
///     New data, shape (n_new, m).
/// ncomp : int, optional
///     Number of FPC components (default 3).
/// confidence_level : float, optional
///     Confidence level (default 0.95).
///
/// Returns
/// -------
/// dict
///     predictions (n_new,), lower (n_new,), upper (n_new,),
///     prediction_se (n_new,), confidence_level, t_critical, residual_se.
#[pyfunction]
#[pyo3(signature = (data, response, new_data, ncomp=3, confidence_level=0.95))]
pub fn prediction_intervals<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    response: PyReadonlyArray1<'py, f64>,
    new_data: PyReadonlyArray2<'py, f64>,
    ncomp: usize,
    confidence_level: f64,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let resp = numpy1d_to_vec(response);
    let fit = to_pyresult(fdars_core::scalar_on_function::fregre_lm(
        &mat, &resp, None, ncomp,
    ))?;
    let new_mat = numpy2d_to_fdmatrix(new_data)?;
    let result = to_pyresult(fdars_core::explain::prediction_intervals(
        &fit,
        &mat,
        None,
        &new_mat,
        None,
        confidence_level,
    ))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("predictions", vec_to_numpy1d(py, result.predictions))?;
    dict.set_item("lower", vec_to_numpy1d(py, result.lower))?;
    dict.set_item("upper", vec_to_numpy1d(py, result.upper))?;
    dict.set_item("prediction_se", vec_to_numpy1d(py, result.prediction_se))?;
    dict.set_item("confidence_level", result.confidence_level)?;
    dict.set_item("t_critical", result.t_critical)?;
    dict.set_item("residual_se", result.residual_se)?;
    Ok(dict)
}

/// LOO-CV / PRESS diagnostics.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Functional predictors, shape (n, m).
/// response : numpy.ndarray
///     Scalar response, length n.
/// ncomp : int, optional
///     Number of FPC components (default 3).
///
/// Returns
/// -------
/// dict
///     loo_residuals (n,), press, loo_r_squared, leverage (n,), tss.
#[pyfunction]
#[pyo3(signature = (data, response, ncomp=3))]
pub fn loo_cv_press<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    response: PyReadonlyArray1<'py, f64>,
    ncomp: usize,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let resp = numpy1d_to_vec(response);
    let fit = to_pyresult(fdars_core::scalar_on_function::fregre_lm(
        &mat, &resp, None, ncomp,
    ))?;
    let result = to_pyresult(fdars_core::explain::loo_cv_press(&fit, &mat, &resp, None))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("loo_residuals", vec_to_numpy1d(py, result.loo_residuals))?;
    dict.set_item("press", result.press)?;
    dict.set_item("loo_r_squared", result.loo_r_squared)?;
    dict.set_item("leverage", vec_to_numpy1d(py, result.leverage))?;
    dict.set_item("tss", result.tss)?;
    Ok(dict)
}

/// Variance inflation factors for FPC scores.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Functional predictors, shape (n, m).
/// response : numpy.ndarray
///     Scalar response, length n.
/// ncomp : int, optional
///     Number of FPC components (default 3).
///
/// Returns
/// -------
/// dict
///     vif (ncomp,), labels (list of str), mean_vif, n_moderate, n_severe.
#[pyfunction]
#[pyo3(signature = (data, response, ncomp=3))]
pub fn fpc_vif<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    response: PyReadonlyArray1<'py, f64>,
    ncomp: usize,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let resp = numpy1d_to_vec(response);
    let fit = to_pyresult(fdars_core::scalar_on_function::fregre_lm(
        &mat, &resp, None, ncomp,
    ))?;
    let result = to_pyresult(fdars_core::explain::fpc_vif(&fit, &mat, None))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("vif", vec_to_numpy1d(py, result.vif))?;
    dict.set_item("labels", result.labels)?;
    dict.set_item("mean_vif", result.mean_vif)?;
    dict.set_item("n_moderate", result.n_moderate)?;
    dict.set_item("n_severe", result.n_severe)?;
    Ok(dict)
}

/// Variance inflation factors for a logistic model.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Functional predictors, shape (n, m).
/// labels : numpy.ndarray
///     Binary labels (0/1), length n.
/// ncomp : int, optional
///     Number of FPC components (default 3).
///
/// Returns
/// -------
/// dict
///     vif (ncomp,), labels (list of str), mean_vif, n_moderate, n_severe.
#[pyfunction]
#[pyo3(signature = (data, labels, ncomp=3))]
pub fn fpc_vif_logistic<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    labels: PyReadonlyArray1<'py, f64>,
    ncomp: usize,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let lab = numpy1d_to_vec(labels);
    let fit = to_pyresult(fdars_core::scalar_on_function::functional_logistic(
        &mat, &lab, None, ncomp, 25, 1e-6,
    ))?;
    let result = to_pyresult(fdars_core::explain::fpc_vif_logistic(&fit, &mat, None))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("vif", vec_to_numpy1d(py, result.vif))?;
    dict.set_item("labels", result.labels)?;
    dict.set_item("mean_vif", result.mean_vif)?;
    dict.set_item("n_moderate", result.n_moderate)?;
    dict.set_item("n_severe", result.n_severe)?;
    Ok(dict)
}

/// Kernel SHAP values for a logistic model.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Functional predictors, shape (n, m).
/// labels : numpy.ndarray
///     Binary labels (0/1), length n.
/// ncomp : int, optional
///     Number of FPC components (default 3).
/// n_samples : int, optional
///     Number of SHAP samples (default 100).
/// seed : int, optional
///     Random seed (default 42).
///
/// Returns
/// -------
/// dict
///     values (n, ncomp), base_value.
#[pyfunction]
#[pyo3(signature = (data, labels, ncomp=3, n_samples=100, seed=42))]
pub fn fpc_shap_values_logistic<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    labels: PyReadonlyArray1<'py, f64>,
    ncomp: usize,
    n_samples: usize,
    seed: u64,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let lab = numpy1d_to_vec(labels);
    let fit = to_pyresult(fdars_core::scalar_on_function::functional_logistic(
        &mat, &lab, None, ncomp, 25, 1e-6,
    ))?;
    let result = to_pyresult(fdars_core::explain::fpc_shap_values_logistic(
        &fit, &mat, None, n_samples, seed,
    ))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("values", fdmatrix_to_numpy2d(py, &result.values))?;
    dict.set_item("base_value", result.base_value)?;
    Ok(dict)
}

/// Friedman H-statistic for interaction between two FPC components (linear model).
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Functional predictors, shape (n, m).
/// response : numpy.ndarray
///     Scalar response, length n.
/// ncomp : int, optional
///     Number of FPC components (default 3).
/// component_j : int, optional
///     First component (default 0).
/// component_k : int, optional
///     Second component (default 1).
/// n_grid : int, optional
///     Grid size (default 20).
///
/// Returns
/// -------
/// dict
///     component_j, component_k, h_squared, grid_j (n_grid,), grid_k (n_grid,),
///     pdp_2d (n_grid, n_grid).
#[pyfunction]
#[pyo3(signature = (data, response, ncomp=3, component_j=0, component_k=1, n_grid=20))]
pub fn friedman_h_statistic<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    response: PyReadonlyArray1<'py, f64>,
    ncomp: usize,
    component_j: usize,
    component_k: usize,
    n_grid: usize,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let resp = numpy1d_to_vec(response);
    let fit = to_pyresult(fdars_core::scalar_on_function::fregre_lm(
        &mat, &resp, None, ncomp,
    ))?;
    let result = to_pyresult(fdars_core::explain::friedman_h_statistic(
        &fit,
        &mat,
        component_j,
        component_k,
        n_grid,
    ))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("component_j", result.component_j)?;
    dict.set_item("component_k", result.component_k)?;
    dict.set_item("h_squared", result.h_squared)?;
    dict.set_item("grid_j", vec_to_numpy1d(py, result.grid_j))?;
    dict.set_item("grid_k", vec_to_numpy1d(py, result.grid_k))?;
    dict.set_item("pdp_2d", fdmatrix_to_numpy2d(py, &result.pdp_2d))?;
    Ok(dict)
}

/// Friedman H-statistic for a logistic model.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Functional predictors, shape (n, m).
/// labels : numpy.ndarray
///     Binary labels (0/1), length n.
/// ncomp : int, optional
///     Number of FPC components (default 3).
/// component_j : int, optional
///     First component (default 0).
/// component_k : int, optional
///     Second component (default 1).
/// n_grid : int, optional
///     Grid size (default 20).
///
/// Returns
/// -------
/// dict
///     component_j, component_k, h_squared, grid_j (n_grid,), grid_k (n_grid,),
///     pdp_2d (n_grid, n_grid).
#[pyfunction]
#[pyo3(signature = (data, labels, ncomp=3, component_j=0, component_k=1, n_grid=20))]
pub fn friedman_h_statistic_logistic<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    labels: PyReadonlyArray1<'py, f64>,
    ncomp: usize,
    component_j: usize,
    component_k: usize,
    n_grid: usize,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let lab = numpy1d_to_vec(labels);
    let fit = to_pyresult(fdars_core::scalar_on_function::functional_logistic(
        &mat, &lab, None, ncomp, 25, 1e-6,
    ))?;
    let result = to_pyresult(fdars_core::explain::friedman_h_statistic_logistic(
        &fit,
        &mat,
        None,
        component_j,
        component_k,
        n_grid,
    ))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("component_j", result.component_j)?;
    dict.set_item("component_k", result.component_k)?;
    dict.set_item("h_squared", result.h_squared)?;
    dict.set_item("grid_j", vec_to_numpy1d(py, result.grid_j))?;
    dict.set_item("grid_k", vec_to_numpy1d(py, result.grid_k))?;
    dict.set_item("pdp_2d", fdmatrix_to_numpy2d(py, &result.pdp_2d))?;
    Ok(dict)
}

/// ALE plot for an FPC component (linear model).
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Functional predictors, shape (n, m).
/// response : numpy.ndarray
///     Scalar response, length n.
/// ncomp : int, optional
///     Number of FPC components (default 3).
/// component : int, optional
///     Which FPC to analyze (default 0).
/// n_bins : int, optional
///     Number of ALE bins (default 10).
///
/// Returns
/// -------
/// dict
///     bin_midpoints, ale_values, bin_edges, bin_counts, component.
#[pyfunction]
#[pyo3(signature = (data, response, ncomp=3, component=0, n_bins=10))]
pub fn fpc_ale<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    response: PyReadonlyArray1<'py, f64>,
    ncomp: usize,
    component: usize,
    n_bins: usize,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let resp = numpy1d_to_vec(response);
    let fit = to_pyresult(fdars_core::scalar_on_function::fregre_lm(
        &mat, &resp, None, ncomp,
    ))?;
    let result = to_pyresult(fdars_core::explain::fpc_ale(
        &fit, &mat, None, component, n_bins,
    ))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("bin_midpoints", vec_to_numpy1d(py, result.bin_midpoints))?;
    dict.set_item("ale_values", vec_to_numpy1d(py, result.ale_values))?;
    dict.set_item("bin_edges", vec_to_numpy1d(py, result.bin_edges))?;
    dict.set_item("bin_counts", usize_vec_to_numpy1d(py, result.bin_counts))?;
    dict.set_item("component", result.component)?;
    Ok(dict)
}

/// ALE plot for an FPC component (logistic model).
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Functional predictors, shape (n, m).
/// labels : numpy.ndarray
///     Binary labels (0/1), length n.
/// ncomp : int, optional
///     Number of FPC components (default 3).
/// component : int, optional
///     Which FPC to analyze (default 0).
/// n_bins : int, optional
///     Number of ALE bins (default 10).
///
/// Returns
/// -------
/// dict
///     bin_midpoints, ale_values, bin_edges, bin_counts, component.
#[pyfunction]
#[pyo3(signature = (data, labels, ncomp=3, component=0, n_bins=10))]
pub fn fpc_ale_logistic<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    labels: PyReadonlyArray1<'py, f64>,
    ncomp: usize,
    component: usize,
    n_bins: usize,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let lab = numpy1d_to_vec(labels);
    let fit = to_pyresult(fdars_core::scalar_on_function::functional_logistic(
        &mat, &lab, None, ncomp, 25, 1e-6,
    ))?;
    let result = to_pyresult(fdars_core::explain::fpc_ale_logistic(
        &fit, &mat, None, component, n_bins,
    ))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("bin_midpoints", vec_to_numpy1d(py, result.bin_midpoints))?;
    dict.set_item("ale_values", vec_to_numpy1d(py, result.ale_values))?;
    dict.set_item("bin_edges", vec_to_numpy1d(py, result.bin_edges))?;
    dict.set_item("bin_counts", usize_vec_to_numpy1d(py, result.bin_counts))?;
    dict.set_item("component", result.component)?;
    Ok(dict)
}

/// LIME explanation for a linear regression model.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Functional predictors, shape (n, m).
/// response : numpy.ndarray
///     Scalar response, length n.
/// ncomp : int, optional
///     Number of FPC components (default 3).
/// observation : int, optional
///     Index of observation to explain (default 0).
/// n_samples : int, optional
///     Number of LIME samples (default 100).
/// kernel_width : float, optional
///     Kernel width (default 1.0).
/// seed : int, optional
///     Random seed (default 42).
///
/// Returns
/// -------
/// dict
///     observation, attributions (ncomp,), local_intercept, local_r_squared, kernel_width.
#[pyfunction]
#[pyo3(signature = (data, response, ncomp=3, observation=0, n_samples=100, kernel_width=1.0, seed=42))]
pub fn lime_explanation<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    response: PyReadonlyArray1<'py, f64>,
    ncomp: usize,
    observation: usize,
    n_samples: usize,
    kernel_width: f64,
    seed: u64,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let resp = numpy1d_to_vec(response);
    let fit = to_pyresult(fdars_core::scalar_on_function::fregre_lm(
        &mat, &resp, None, ncomp,
    ))?;
    let result = to_pyresult(fdars_core::explain::lime_explanation(
        &fit,
        &mat,
        None,
        observation,
        n_samples,
        kernel_width,
        seed,
    ))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("observation", result.observation)?;
    dict.set_item("attributions", vec_to_numpy1d(py, result.attributions))?;
    dict.set_item("local_intercept", result.local_intercept)?;
    dict.set_item("local_r_squared", result.local_r_squared)?;
    dict.set_item("kernel_width", result.kernel_width)?;
    Ok(dict)
}

/// LIME explanation for a logistic regression model.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Functional predictors, shape (n, m).
/// labels : numpy.ndarray
///     Binary labels (0/1), length n.
/// ncomp : int, optional
///     Number of FPC components (default 3).
/// observation : int, optional
///     Index of observation to explain (default 0).
/// n_samples : int, optional
///     Number of LIME samples (default 100).
/// kernel_width : float, optional
///     Kernel width (default 1.0).
/// seed : int, optional
///     Random seed (default 42).
///
/// Returns
/// -------
/// dict
///     observation, attributions (ncomp,), local_intercept, local_r_squared, kernel_width.
#[pyfunction]
#[pyo3(signature = (data, labels, ncomp=3, observation=0, n_samples=100, kernel_width=1.0, seed=42))]
pub fn lime_explanation_logistic<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    labels: PyReadonlyArray1<'py, f64>,
    ncomp: usize,
    observation: usize,
    n_samples: usize,
    kernel_width: f64,
    seed: u64,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let lab = numpy1d_to_vec(labels);
    let fit = to_pyresult(fdars_core::scalar_on_function::functional_logistic(
        &mat, &lab, None, ncomp, 25, 1e-6,
    ))?;
    let result = to_pyresult(fdars_core::explain::lime_explanation_logistic(
        &fit,
        &mat,
        None,
        observation,
        n_samples,
        kernel_width,
        seed,
    ))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("observation", result.observation)?;
    dict.set_item("attributions", vec_to_numpy1d(py, result.attributions))?;
    dict.set_item("local_intercept", result.local_intercept)?;
    dict.set_item("local_r_squared", result.local_r_squared)?;
    dict.set_item("kernel_width", result.kernel_width)?;
    Ok(dict)
}

/// Sobol sensitivity indices (linear model).
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Functional predictors, shape (n, m).
/// response : numpy.ndarray
///     Scalar response, length n.
/// ncomp : int, optional
///     Number of FPC components (default 3).
///
/// Returns
/// -------
/// dict
///     first_order (ncomp,), total_order (ncomp,), var_y, component_variance (ncomp,).
#[pyfunction]
#[pyo3(signature = (data, response, ncomp=3))]
pub fn sobol_indices<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    response: PyReadonlyArray1<'py, f64>,
    ncomp: usize,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let resp = numpy1d_to_vec(response);
    let fit = to_pyresult(fdars_core::scalar_on_function::fregre_lm(
        &mat, &resp, None, ncomp,
    ))?;
    let result = to_pyresult(fdars_core::explain::sobol_indices(&fit, &mat, &resp, None))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("first_order", vec_to_numpy1d(py, result.first_order))?;
    dict.set_item("total_order", vec_to_numpy1d(py, result.total_order))?;
    dict.set_item("var_y", result.var_y)?;
    dict.set_item(
        "component_variance",
        vec_to_numpy1d(py, result.component_variance),
    )?;
    Ok(dict)
}

/// Sobol sensitivity indices (logistic model, Saltelli MC).
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Functional predictors, shape (n, m).
/// labels : numpy.ndarray
///     Binary labels (0/1), length n.
/// ncomp : int, optional
///     Number of FPC components (default 3).
/// n_samples : int, optional
///     Number of MC samples (default 1000).
/// seed : int, optional
///     Random seed (default 42).
///
/// Returns
/// -------
/// dict
///     first_order (ncomp,), total_order (ncomp,), var_y, component_variance (ncomp,).
#[pyfunction]
#[pyo3(signature = (data, labels, ncomp=3, n_samples=1000, seed=42))]
pub fn sobol_indices_logistic<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    labels: PyReadonlyArray1<'py, f64>,
    ncomp: usize,
    n_samples: usize,
    seed: u64,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let lab = numpy1d_to_vec(labels);
    let fit = to_pyresult(fdars_core::scalar_on_function::functional_logistic(
        &mat, &lab, None, ncomp, 25, 1e-6,
    ))?;
    let result = to_pyresult(fdars_core::explain::sobol_indices_logistic(
        &fit, &mat, None, n_samples, seed,
    ))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("first_order", vec_to_numpy1d(py, result.first_order))?;
    dict.set_item("total_order", vec_to_numpy1d(py, result.total_order))?;
    dict.set_item("var_y", result.var_y)?;
    dict.set_item(
        "component_variance",
        vec_to_numpy1d(py, result.component_variance),
    )?;
    Ok(dict)
}

/// Functional saliency maps (linear model).
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Functional predictors, shape (n, m).
/// response : numpy.ndarray
///     Scalar response, length n.
/// ncomp : int, optional
///     Number of FPC components (default 3).
///
/// Returns
/// -------
/// dict
///     saliency_map (n, m), mean_absolute_saliency (m,).
#[pyfunction]
#[pyo3(signature = (data, response, ncomp=3))]
pub fn functional_saliency<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    response: PyReadonlyArray1<'py, f64>,
    ncomp: usize,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let resp = numpy1d_to_vec(response);
    let fit = to_pyresult(fdars_core::scalar_on_function::fregre_lm(
        &mat, &resp, None, ncomp,
    ))?;
    let result = to_pyresult(fdars_core::explain::functional_saliency(&fit, &mat, None))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item(
        "saliency_map",
        fdmatrix_to_numpy2d(py, &result.saliency_map),
    )?;
    dict.set_item(
        "mean_absolute_saliency",
        vec_to_numpy1d(py, result.mean_absolute_saliency),
    )?;
    Ok(dict)
}

/// Functional saliency maps (logistic model, gradient-based).
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Functional predictors, shape (n, m).
/// labels : numpy.ndarray
///     Binary labels (0/1), length n.
/// ncomp : int, optional
///     Number of FPC components (default 3).
///
/// Returns
/// -------
/// dict
///     saliency_map (n, m), mean_absolute_saliency (m,).
#[pyfunction]
#[pyo3(signature = (data, labels, ncomp=3))]
pub fn functional_saliency_logistic<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    labels: PyReadonlyArray1<'py, f64>,
    ncomp: usize,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let lab = numpy1d_to_vec(labels);
    let fit = to_pyresult(fdars_core::scalar_on_function::functional_logistic(
        &mat, &lab, None, ncomp, 25, 1e-6,
    ))?;
    let result = to_pyresult(fdars_core::explain::functional_saliency_logistic(&fit))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item(
        "saliency_map",
        fdmatrix_to_numpy2d(py, &result.saliency_map),
    )?;
    dict.set_item(
        "mean_absolute_saliency",
        vec_to_numpy1d(py, result.mean_absolute_saliency),
    )?;
    Ok(dict)
}

/// Domain selection / interval importance (linear model).
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Functional predictors, shape (n, m).
/// response : numpy.ndarray
///     Scalar response, length n.
/// ncomp : int, optional
///     Number of FPC components (default 3).
/// window_width : int, optional
///     Sliding window width (default 5).
/// threshold : float, optional
///     Importance threshold (default 0.0).
///
/// Returns
/// -------
/// dict
///     pointwise_importance (m,), intervals (list of dicts), window_width, threshold.
#[pyfunction]
#[pyo3(signature = (data, response, ncomp=3, window_width=5, threshold=0.0))]
pub fn domain_selection<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    response: PyReadonlyArray1<'py, f64>,
    ncomp: usize,
    window_width: usize,
    threshold: f64,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let resp = numpy1d_to_vec(response);
    let fit = to_pyresult(fdars_core::scalar_on_function::fregre_lm(
        &mat, &resp, None, ncomp,
    ))?;
    let result = to_pyresult(fdars_core::explain::domain_selection(
        &fit,
        window_width,
        threshold,
    ))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item(
        "pointwise_importance",
        vec_to_numpy1d(py, result.pointwise_importance),
    )?;
    let intervals: Vec<(usize, usize, f64)> = result
        .intervals
        .iter()
        .map(|iv| (iv.start_idx, iv.end_idx, iv.importance))
        .collect();
    dict.set_item("intervals", intervals)?;
    dict.set_item("window_width", result.window_width)?;
    dict.set_item("threshold", result.threshold)?;
    Ok(dict)
}

/// Domain selection / interval importance (logistic model).
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Functional predictors, shape (n, m).
/// labels : numpy.ndarray
///     Binary labels (0/1), length n.
/// ncomp : int, optional
///     Number of FPC components (default 3).
/// window_width : int, optional
///     Sliding window width (default 5).
/// threshold : float, optional
///     Importance threshold (default 0.0).
///
/// Returns
/// -------
/// dict
///     pointwise_importance (m,), intervals (list of tuples), window_width, threshold.
#[pyfunction]
#[pyo3(signature = (data, labels, ncomp=3, window_width=5, threshold=0.0))]
pub fn domain_selection_logistic<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    labels: PyReadonlyArray1<'py, f64>,
    ncomp: usize,
    window_width: usize,
    threshold: f64,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let lab = numpy1d_to_vec(labels);
    let fit = to_pyresult(fdars_core::scalar_on_function::functional_logistic(
        &mat, &lab, None, ncomp, 25, 1e-6,
    ))?;
    let result = to_pyresult(fdars_core::explain::domain_selection_logistic(
        &fit,
        window_width,
        threshold,
    ))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item(
        "pointwise_importance",
        vec_to_numpy1d(py, result.pointwise_importance),
    )?;
    let intervals: Vec<(usize, usize, f64)> = result
        .intervals
        .iter()
        .map(|iv| (iv.start_idx, iv.end_idx, iv.importance))
        .collect();
    dict.set_item("intervals", intervals)?;
    dict.set_item("window_width", result.window_width)?;
    dict.set_item("threshold", result.threshold)?;
    Ok(dict)
}

/// Counterfactual explanation (linear regression).
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Functional predictors, shape (n, m).
/// response : numpy.ndarray
///     Scalar response, length n.
/// ncomp : int, optional
///     Number of FPC components (default 3).
/// observation : int, optional
///     Index of observation (default 0).
/// target_value : float, optional
///     Target prediction value (default 0.0).
///
/// Returns
/// -------
/// dict
///     observation, original_scores, counterfactual_scores, delta_scores,
///     delta_function (m,), distance, original_prediction,
///     counterfactual_prediction, found.
#[pyfunction]
#[pyo3(signature = (data, response, ncomp=3, observation=0, target_value=0.0))]
pub fn counterfactual_regression<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    response: PyReadonlyArray1<'py, f64>,
    ncomp: usize,
    observation: usize,
    target_value: f64,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let resp = numpy1d_to_vec(response);
    let fit = to_pyresult(fdars_core::scalar_on_function::fregre_lm(
        &mat, &resp, None, ncomp,
    ))?;
    let result = to_pyresult(fdars_core::explain::counterfactual_regression(
        &fit,
        &mat,
        None,
        observation,
        target_value,
    ))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("observation", result.observation)?;
    dict.set_item(
        "original_scores",
        vec_to_numpy1d(py, result.original_scores),
    )?;
    dict.set_item(
        "counterfactual_scores",
        vec_to_numpy1d(py, result.counterfactual_scores),
    )?;
    dict.set_item("delta_scores", vec_to_numpy1d(py, result.delta_scores))?;
    dict.set_item("delta_function", vec_to_numpy1d(py, result.delta_function))?;
    dict.set_item("distance", result.distance)?;
    dict.set_item("original_prediction", result.original_prediction)?;
    dict.set_item(
        "counterfactual_prediction",
        result.counterfactual_prediction,
    )?;
    dict.set_item("found", result.found)?;
    Ok(dict)
}

/// Counterfactual explanation (logistic model, gradient descent).
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Functional predictors, shape (n, m).
/// labels : numpy.ndarray
///     Binary labels (0/1), length n.
/// ncomp : int, optional
///     Number of FPC components (default 3).
/// observation : int, optional
///     Index of observation (default 0).
/// max_iter : int, optional
///     Maximum iterations (default 100).
/// step_size : float, optional
///     Gradient descent step size (default 0.1).
///
/// Returns
/// -------
/// dict
///     observation, original_scores, counterfactual_scores, delta_scores,
///     delta_function (m,), distance, original_prediction,
///     counterfactual_prediction, found.
#[pyfunction]
#[pyo3(signature = (data, labels, ncomp=3, observation=0, max_iter=100, step_size=0.1))]
pub fn counterfactual_logistic<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    labels: PyReadonlyArray1<'py, f64>,
    ncomp: usize,
    observation: usize,
    max_iter: usize,
    step_size: f64,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let lab = numpy1d_to_vec(labels);
    let fit = to_pyresult(fdars_core::scalar_on_function::functional_logistic(
        &mat, &lab, None, ncomp, 25, 1e-6,
    ))?;
    let result = to_pyresult(fdars_core::explain::counterfactual_logistic(
        &fit,
        &mat,
        None,
        observation,
        max_iter,
        step_size,
    ))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("observation", result.observation)?;
    dict.set_item(
        "original_scores",
        vec_to_numpy1d(py, result.original_scores),
    )?;
    dict.set_item(
        "counterfactual_scores",
        vec_to_numpy1d(py, result.counterfactual_scores),
    )?;
    dict.set_item("delta_scores", vec_to_numpy1d(py, result.delta_scores))?;
    dict.set_item("delta_function", vec_to_numpy1d(py, result.delta_function))?;
    dict.set_item("distance", result.distance)?;
    dict.set_item("original_prediction", result.original_prediction)?;
    dict.set_item(
        "counterfactual_prediction",
        result.counterfactual_prediction,
    )?;
    dict.set_item("found", result.found)?;
    Ok(dict)
}

/// Prototype/criticism selection (MMD-based).
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Functional predictors, shape (n, m).
/// ncomp : int, optional
///     Number of FPC components (default 3).
/// n_prototypes : int, optional
///     Number of prototypes (default 5).
/// n_criticisms : int, optional
///     Number of criticisms (default 5).
///
/// Returns
/// -------
/// dict
///     prototype_indices, prototype_witness, criticism_indices,
///     criticism_witness, bandwidth.
#[pyfunction]
#[pyo3(signature = (data, ncomp=3, n_prototypes=5, n_criticisms=5))]
pub fn prototype_criticism<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    ncomp: usize,
    n_prototypes: usize,
    n_criticisms: usize,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let argvals: Vec<f64> = {
        let m = mat.ncols();
        (0..m).map(|j| j as f64 / (m - 1).max(1) as f64).collect()
    };
    let fpca = to_pyresult(fdars_core::regression::fdata_to_pc_1d(
        &mat, ncomp, &argvals,
    ))?;
    let result = to_pyresult(fdars_core::explain::prototype_criticism(
        &fpca,
        ncomp,
        n_prototypes,
        n_criticisms,
    ))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item(
        "prototype_indices",
        usize_vec_to_numpy1d(py, result.prototype_indices),
    )?;
    dict.set_item(
        "prototype_witness",
        vec_to_numpy1d(py, result.prototype_witness),
    )?;
    dict.set_item(
        "criticism_indices",
        usize_vec_to_numpy1d(py, result.criticism_indices),
    )?;
    dict.set_item(
        "criticism_witness",
        vec_to_numpy1d(py, result.criticism_witness),
    )?;
    dict.set_item("bandwidth", result.bandwidth)?;
    Ok(dict)
}

/// Calibration diagnostics for a logistic model.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Functional predictors, shape (n, m).
/// labels : numpy.ndarray
///     Binary labels (0/1), length n.
/// ncomp : int, optional
///     Number of FPC components (default 3).
/// n_groups : int, optional
///     Number of calibration groups (default 10).
///
/// Returns
/// -------
/// dict
///     brier_score, log_loss, hosmer_lemeshow_chi2, hosmer_lemeshow_df,
///     n_groups, reliability_bins, bin_counts.
#[pyfunction]
#[pyo3(signature = (data, labels, ncomp=3, n_groups=10))]
pub fn calibration_diagnostics<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    labels: PyReadonlyArray1<'py, f64>,
    ncomp: usize,
    n_groups: usize,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let lab = numpy1d_to_vec(labels);
    let fit = to_pyresult(fdars_core::scalar_on_function::functional_logistic(
        &mat, &lab, None, ncomp, 25, 1e-6,
    ))?;
    let result = to_pyresult(fdars_core::explain::calibration_diagnostics(
        &fit, &lab, n_groups,
    ))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("brier_score", result.brier_score)?;
    dict.set_item("log_loss", result.log_loss)?;
    dict.set_item("hosmer_lemeshow_chi2", result.hosmer_lemeshow_chi2)?;
    dict.set_item("hosmer_lemeshow_df", result.hosmer_lemeshow_df)?;
    dict.set_item("n_groups", result.n_groups)?;
    dict.set_item("reliability_bins", result.reliability_bins)?;
    dict.set_item("bin_counts", usize_vec_to_numpy1d(py, result.bin_counts))?;
    Ok(dict)
}

/// Expected calibration error (ECE, MCE, ACE).
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Functional predictors, shape (n, m).
/// labels : numpy.ndarray
///     Binary labels (0/1), length n.
/// ncomp : int, optional
///     Number of FPC components (default 3).
/// n_bins : int, optional
///     Number of bins (default 10).
///
/// Returns
/// -------
/// dict
///     ece, mce, ace, n_bins, bin_ece_contributions (n_bins,).
#[pyfunction]
#[pyo3(signature = (data, labels, ncomp=3, n_bins=10))]
pub fn expected_calibration_error<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    labels: PyReadonlyArray1<'py, f64>,
    ncomp: usize,
    n_bins: usize,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let lab = numpy1d_to_vec(labels);
    let fit = to_pyresult(fdars_core::scalar_on_function::functional_logistic(
        &mat, &lab, None, ncomp, 25, 1e-6,
    ))?;
    let result = to_pyresult(fdars_core::explain::expected_calibration_error(
        &fit, &lab, n_bins,
    ))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("ece", result.ece)?;
    dict.set_item("mce", result.mce)?;
    dict.set_item("ace", result.ace)?;
    dict.set_item("n_bins", result.n_bins)?;
    dict.set_item(
        "bin_ece_contributions",
        vec_to_numpy1d(py, result.bin_ece_contributions),
    )?;
    Ok(dict)
}

/// Split-conformal prediction intervals.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Training data, shape (n, m).
/// response : numpy.ndarray
///     Training response, length n.
/// test_data : numpy.ndarray
///     Test data, shape (n_test, m).
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
///     predictions (n_test,), lower (n_test,), upper (n_test,),
///     residual_quantile, coverage, calibration_scores.
#[pyfunction]
#[pyo3(signature = (data, response, test_data, ncomp=3, cal_fraction=0.25, alpha=0.1, seed=42))]
pub fn conformal_prediction_residuals<'py>(
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
    let fit = to_pyresult(fdars_core::scalar_on_function::fregre_lm(
        &mat, &resp, None, ncomp,
    ))?;
    let test_mat = numpy2d_to_fdmatrix(test_data)?;
    let result = to_pyresult(fdars_core::explain::conformal_prediction_residuals(
        &fit,
        &mat,
        &resp,
        &test_mat,
        None,
        None,
        cal_fraction,
        alpha,
        seed,
    ))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("predictions", vec_to_numpy1d(py, result.predictions))?;
    dict.set_item("lower", vec_to_numpy1d(py, result.lower))?;
    dict.set_item("upper", vec_to_numpy1d(py, result.upper))?;
    dict.set_item("residual_quantile", result.residual_quantile)?;
    dict.set_item("coverage", result.coverage)?;
    dict.set_item(
        "calibration_scores",
        vec_to_numpy1d(py, result.calibration_scores),
    )?;
    Ok(dict)
}

/// Regression depth diagnostics (linear model).
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Functional predictors, shape (n, m).
/// response : numpy.ndarray
///     Scalar response, length n.
/// ncomp : int, optional
///     Number of FPC components (default 3).
/// n_boot : int, optional
///     Number of bootstrap iterations (default 100).
/// depth_type : str, optional
///     "fraiman_muniz" (default), "modified_band", or "functional_spatial".
/// seed : int, optional
///     Random seed (default 42).
///
/// Returns
/// -------
/// dict
///     beta_depth, score_depths (n,), mean_score_depth, depth_type, n_boot_success.
#[pyfunction]
#[pyo3(signature = (data, response, ncomp=3, n_boot=100, depth_type="fraiman_muniz", seed=42))]
pub fn regression_depth<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    response: PyReadonlyArray1<'py, f64>,
    ncomp: usize,
    n_boot: usize,
    depth_type: &str,
    seed: u64,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let resp = numpy1d_to_vec(response);
    let fit = to_pyresult(fdars_core::scalar_on_function::fregre_lm(
        &mat, &resp, None, ncomp,
    ))?;
    let dt = match depth_type {
        "modified_band" => fdars_core::explain::DepthType::ModifiedBand,
        "functional_spatial" => fdars_core::explain::DepthType::FunctionalSpatial,
        _ => fdars_core::explain::DepthType::FraimanMuniz,
    };
    let result = to_pyresult(fdars_core::explain::regression_depth(
        &fit, &mat, &resp, None, n_boot, dt, seed,
    ))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("beta_depth", result.beta_depth)?;
    dict.set_item("score_depths", vec_to_numpy1d(py, result.score_depths))?;
    dict.set_item("mean_score_depth", result.mean_score_depth)?;
    dict.set_item("depth_type", depth_type)?;
    dict.set_item("n_boot_success", result.n_boot_success)?;
    Ok(dict)
}

/// Regression depth diagnostics (logistic model).
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Functional predictors, shape (n, m).
/// labels : numpy.ndarray
///     Binary labels (0/1), length n.
/// ncomp : int, optional
///     Number of FPC components (default 3).
/// n_boot : int, optional
///     Number of bootstrap iterations (default 100).
/// depth_type : str, optional
///     "fraiman_muniz" (default), "modified_band", or "functional_spatial".
/// seed : int, optional
///     Random seed (default 42).
///
/// Returns
/// -------
/// dict
///     beta_depth, score_depths (n,), mean_score_depth, depth_type, n_boot_success.
#[pyfunction]
#[pyo3(signature = (data, labels, ncomp=3, n_boot=100, depth_type="fraiman_muniz", seed=42))]
pub fn regression_depth_logistic<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    labels: PyReadonlyArray1<'py, f64>,
    ncomp: usize,
    n_boot: usize,
    depth_type: &str,
    seed: u64,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let lab = numpy1d_to_vec(labels);
    let fit = to_pyresult(fdars_core::scalar_on_function::functional_logistic(
        &mat, &lab, None, ncomp, 25, 1e-6,
    ))?;
    let dt = match depth_type {
        "modified_band" => fdars_core::explain::DepthType::ModifiedBand,
        "functional_spatial" => fdars_core::explain::DepthType::FunctionalSpatial,
        _ => fdars_core::explain::DepthType::FraimanMuniz,
    };
    let result = to_pyresult(fdars_core::explain::regression_depth_logistic(
        &fit, &mat, &lab, None, n_boot, dt, seed,
    ))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("beta_depth", result.beta_depth)?;
    dict.set_item("score_depths", vec_to_numpy1d(py, result.score_depths))?;
    dict.set_item("mean_score_depth", result.mean_score_depth)?;
    dict.set_item("depth_type", depth_type)?;
    dict.set_item("n_boot_success", result.n_boot_success)?;
    Ok(dict)
}

/// Bootstrap stability analysis (linear model).
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Functional predictors, shape (n, m).
/// response : numpy.ndarray
///     Scalar response, length n.
/// ncomp : int, optional
///     Number of FPC components (default 3).
/// n_boot : int, optional
///     Number of bootstrap iterations (default 100).
/// seed : int, optional
///     Random seed (default 42).
///
/// Returns
/// -------
/// dict
///     beta_t_std (m,), coefficient_std (ncomp,), metric_std,
///     beta_t_cv (m,), importance_stability, n_boot_success.
#[pyfunction]
#[pyo3(signature = (data, response, ncomp=3, n_boot=100, seed=42))]
pub fn explanation_stability<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    response: PyReadonlyArray1<'py, f64>,
    ncomp: usize,
    n_boot: usize,
    seed: u64,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let resp = numpy1d_to_vec(response);
    let result = to_pyresult(fdars_core::explain::explanation_stability(
        &mat, &resp, None, ncomp, n_boot, seed,
    ))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("beta_t_std", vec_to_numpy1d(py, result.beta_t_std))?;
    dict.set_item(
        "coefficient_std",
        vec_to_numpy1d(py, result.coefficient_std),
    )?;
    dict.set_item("metric_std", result.metric_std)?;
    dict.set_item("beta_t_cv", vec_to_numpy1d(py, result.beta_t_cv))?;
    dict.set_item("importance_stability", result.importance_stability)?;
    dict.set_item("n_boot_success", result.n_boot_success)?;
    Ok(dict)
}

/// Bootstrap stability analysis (logistic model).
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Functional predictors, shape (n, m).
/// labels : numpy.ndarray
///     Binary labels (0/1), length n.
/// ncomp : int, optional
///     Number of FPC components (default 3).
/// n_boot : int, optional
///     Number of bootstrap iterations (default 100).
/// seed : int, optional
///     Random seed (default 42).
///
/// Returns
/// -------
/// dict
///     beta_t_std (m,), coefficient_std (ncomp,), metric_std,
///     beta_t_cv (m,), importance_stability, n_boot_success.
#[pyfunction]
#[pyo3(signature = (data, labels, ncomp=3, n_boot=100, seed=42))]
pub fn explanation_stability_logistic<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    labels: PyReadonlyArray1<'py, f64>,
    ncomp: usize,
    n_boot: usize,
    seed: u64,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let lab = numpy1d_to_vec(labels);
    let result = to_pyresult(fdars_core::explain::explanation_stability_logistic(
        &mat, &lab, None, ncomp, n_boot, seed,
    ))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("beta_t_std", vec_to_numpy1d(py, result.beta_t_std))?;
    dict.set_item(
        "coefficient_std",
        vec_to_numpy1d(py, result.coefficient_std),
    )?;
    dict.set_item("metric_std", result.metric_std)?;
    dict.set_item("beta_t_cv", vec_to_numpy1d(py, result.beta_t_cv))?;
    dict.set_item("importance_stability", result.importance_stability)?;
    dict.set_item("n_boot_success", result.n_boot_success)?;
    Ok(dict)
}

/// Anchor explanation (linear model).
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Functional predictors, shape (n, m).
/// response : numpy.ndarray
///     Scalar response, length n.
/// ncomp : int, optional
///     Number of FPC components (default 3).
/// observation : int, optional
///     Index of observation (default 0).
/// precision_threshold : float, optional
///     Minimum precision (default 0.95).
/// n_bins : int, optional
///     Number of quantile bins (default 4).
///
/// Returns
/// -------
/// dict
///     observation, predicted_value, conditions (list), precision, coverage, n_matching.
#[pyfunction]
#[pyo3(signature = (data, response, ncomp=3, observation=0, precision_threshold=0.95, n_bins=4))]
pub fn anchor_explanation<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    response: PyReadonlyArray1<'py, f64>,
    ncomp: usize,
    observation: usize,
    precision_threshold: f64,
    n_bins: usize,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let resp = numpy1d_to_vec(response);
    let fit = to_pyresult(fdars_core::scalar_on_function::fregre_lm(
        &mat, &resp, None, ncomp,
    ))?;
    let result = to_pyresult(fdars_core::explain::anchor_explanation(
        &fit,
        &mat,
        None,
        observation,
        precision_threshold,
        n_bins,
    ))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("observation", result.observation)?;
    dict.set_item("predicted_value", result.predicted_value)?;
    let conditions: Vec<(usize, f64, f64)> = result
        .rule
        .conditions
        .iter()
        .map(|c| (c.component, c.lower_bound, c.upper_bound))
        .collect();
    dict.set_item("conditions", conditions)?;
    dict.set_item("precision", result.rule.precision)?;
    dict.set_item("coverage", result.rule.coverage)?;
    dict.set_item("n_matching", result.rule.n_matching)?;
    Ok(dict)
}

/// Anchor explanation (logistic model).
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Functional predictors, shape (n, m).
/// labels : numpy.ndarray
///     Binary labels (0/1), length n.
/// ncomp : int, optional
///     Number of FPC components (default 3).
/// observation : int, optional
///     Index of observation (default 0).
/// precision_threshold : float, optional
///     Minimum precision (default 0.95).
/// n_bins : int, optional
///     Number of quantile bins (default 4).
///
/// Returns
/// -------
/// dict
///     observation, predicted_value, conditions (list), precision, coverage, n_matching.
#[pyfunction]
#[pyo3(signature = (data, labels, ncomp=3, observation=0, precision_threshold=0.95, n_bins=4))]
pub fn anchor_explanation_logistic<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    labels: PyReadonlyArray1<'py, f64>,
    ncomp: usize,
    observation: usize,
    precision_threshold: f64,
    n_bins: usize,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let lab = numpy1d_to_vec(labels);
    let fit = to_pyresult(fdars_core::scalar_on_function::functional_logistic(
        &mat, &lab, None, ncomp, 25, 1e-6,
    ))?;
    let result = to_pyresult(fdars_core::explain::anchor_explanation_logistic(
        &fit,
        &mat,
        None,
        observation,
        precision_threshold,
        n_bins,
    ))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("observation", result.observation)?;
    dict.set_item("predicted_value", result.predicted_value)?;
    let conditions: Vec<(usize, f64, f64)> = result
        .rule
        .conditions
        .iter()
        .map(|c| (c.component, c.lower_bound, c.upper_bound))
        .collect();
    dict.set_item("conditions", conditions)?;
    dict.set_item("precision", result.rule.precision)?;
    dict.set_item("coverage", result.rule.coverage)?;
    dict.set_item("n_matching", result.rule.n_matching)?;
    Ok(dict)
}

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(fpc_permutation_importance, m)?)?;
    m.add_function(wrap_pyfunction!(functional_pdp, m)?)?;
    m.add_function(wrap_pyfunction!(fpc_shap_values, m)?)?;
    m.add_function(wrap_pyfunction!(significant_regions, m)?)?;
    m.add_function(wrap_pyfunction!(beta_decomposition, m)?)?;
    m.add_function(wrap_pyfunction!(functional_pdp_logistic, m)?)?;
    m.add_function(wrap_pyfunction!(beta_decomposition_logistic, m)?)?;
    m.add_function(wrap_pyfunction!(significant_regions_from_se, m)?)?;
    m.add_function(wrap_pyfunction!(fpc_permutation_importance_logistic, m)?)?;
    m.add_function(wrap_pyfunction!(pointwise_importance, m)?)?;
    m.add_function(wrap_pyfunction!(pointwise_importance_logistic, m)?)?;
    m.add_function(wrap_pyfunction!(conditional_permutation_importance, m)?)?;
    m.add_function(wrap_pyfunction!(
        conditional_permutation_importance_logistic,
        m
    )?)?;
    m.add_function(wrap_pyfunction!(influence_diagnostics, m)?)?;
    m.add_function(wrap_pyfunction!(dfbetas_dffits, m)?)?;
    m.add_function(wrap_pyfunction!(prediction_intervals, m)?)?;
    m.add_function(wrap_pyfunction!(loo_cv_press, m)?)?;
    m.add_function(wrap_pyfunction!(fpc_vif, m)?)?;
    m.add_function(wrap_pyfunction!(fpc_vif_logistic, m)?)?;
    m.add_function(wrap_pyfunction!(fpc_shap_values_logistic, m)?)?;
    m.add_function(wrap_pyfunction!(friedman_h_statistic, m)?)?;
    m.add_function(wrap_pyfunction!(friedman_h_statistic_logistic, m)?)?;
    m.add_function(wrap_pyfunction!(fpc_ale, m)?)?;
    m.add_function(wrap_pyfunction!(fpc_ale_logistic, m)?)?;
    m.add_function(wrap_pyfunction!(lime_explanation, m)?)?;
    m.add_function(wrap_pyfunction!(lime_explanation_logistic, m)?)?;
    m.add_function(wrap_pyfunction!(sobol_indices, m)?)?;
    m.add_function(wrap_pyfunction!(sobol_indices_logistic, m)?)?;
    m.add_function(wrap_pyfunction!(functional_saliency, m)?)?;
    m.add_function(wrap_pyfunction!(functional_saliency_logistic, m)?)?;
    m.add_function(wrap_pyfunction!(domain_selection, m)?)?;
    m.add_function(wrap_pyfunction!(domain_selection_logistic, m)?)?;
    m.add_function(wrap_pyfunction!(counterfactual_regression, m)?)?;
    m.add_function(wrap_pyfunction!(counterfactual_logistic, m)?)?;
    m.add_function(wrap_pyfunction!(prototype_criticism, m)?)?;
    m.add_function(wrap_pyfunction!(calibration_diagnostics, m)?)?;
    m.add_function(wrap_pyfunction!(expected_calibration_error, m)?)?;
    m.add_function(wrap_pyfunction!(conformal_prediction_residuals, m)?)?;
    m.add_function(wrap_pyfunction!(regression_depth, m)?)?;
    m.add_function(wrap_pyfunction!(regression_depth_logistic, m)?)?;
    m.add_function(wrap_pyfunction!(explanation_stability, m)?)?;
    m.add_function(wrap_pyfunction!(explanation_stability_logistic, m)?)?;
    m.add_function(wrap_pyfunction!(anchor_explanation, m)?)?;
    m.add_function(wrap_pyfunction!(anchor_explanation_logistic, m)?)?;
    Ok(())
}
