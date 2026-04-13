//! Conformal prediction methods.

use crate::convert::*;
use numpy::{PyReadonlyArray1, PyReadonlyArray2};
use pyo3::prelude::*;

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
    response: PyReadonlyArray1<'py, f64>,
    test_data: PyReadonlyArray2<'py, f64>,
    ncomp: usize,
    max_iter: usize,
    tol: f64,
    cal_fraction: f64,
    alpha: f64,
    seed: u64,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let resp = numpy1d_to_vec(response);
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
    labels: PyReadonlyArray1<'py, i64>,
    test_data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    lambda: f64,
    cal_fraction: f64,
    alpha: f64,
    seed: u64,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let lab: Vec<i8> = numpy1d_to_vec_i8(labels);
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

/// Convert numpy 1D i64 array to Vec<i8>.
fn numpy1d_to_vec_i8(arr: PyReadonlyArray1<'_, i64>) -> Vec<i8> {
    arr.as_array().iter().map(|&x| x as i8).collect()
}

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(conformal_fregre_lm, m)?)?;
    m.add_function(wrap_pyfunction!(conformal_fregre_np, m)?)?;
    m.add_function(wrap_pyfunction!(conformal_classif, m)?)?;
    m.add_function(wrap_pyfunction!(conformal_elastic_regression, m)?)?;
    m.add_function(wrap_pyfunction!(conformal_elastic_pcr, m)?)?;
    m.add_function(wrap_pyfunction!(conformal_logistic, m)?)?;
    m.add_function(wrap_pyfunction!(conformal_elastic_logistic, m)?)?;
    Ok(())
}
