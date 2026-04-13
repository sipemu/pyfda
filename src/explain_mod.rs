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

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(fpc_permutation_importance, m)?)?;
    m.add_function(wrap_pyfunction!(functional_pdp, m)?)?;
    m.add_function(wrap_pyfunction!(fpc_shap_values, m)?)?;
    m.add_function(wrap_pyfunction!(significant_regions, m)?)?;
    m.add_function(wrap_pyfunction!(beta_decomposition, m)?)?;
    Ok(())
}
