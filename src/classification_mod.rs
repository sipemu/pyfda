//! Classification methods for functional data.

use crate::convert::*;
use numpy::{PyReadonlyArray1, PyReadonlyArray2};
use pyo3::prelude::*;

/// LDA classification for functional data via FPC scores.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Data, shape (n, m).
/// labels : numpy.ndarray
///     Class labels, length n.
/// ncomp : int, optional
///     Number of FPC components (default 3).
///
/// Returns
/// -------
/// dict
///     predicted (n,), accuracy.
#[pyfunction]
#[pyo3(signature = (data, labels, ncomp=3))]
pub fn fclassif_lda<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    labels: PyReadonlyArray1<'py, i64>,
    ncomp: usize,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let lab = numpy1d_to_usize_vec(labels);
    let result = to_pyresult(fdars_core::classification::fclassif_lda(
        &mat, &lab, None, ncomp,
    ))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("predicted", usize_vec_to_numpy1d(py, result.predicted))?;
    dict.set_item("accuracy", result.accuracy)?;
    Ok(dict)
}

/// QDA classification for functional data.
#[pyfunction]
#[pyo3(signature = (data, labels, ncomp=3))]
pub fn fclassif_qda<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    labels: PyReadonlyArray1<'py, i64>,
    ncomp: usize,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let lab = numpy1d_to_usize_vec(labels);
    let result = to_pyresult(fdars_core::classification::fclassif_qda(
        &mat, &lab, None, ncomp,
    ))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("predicted", usize_vec_to_numpy1d(py, result.predicted))?;
    dict.set_item("accuracy", result.accuracy)?;
    Ok(dict)
}

/// k-NN classification for functional data.
#[pyfunction]
#[pyo3(signature = (data, labels, ncomp=3, k=5))]
pub fn fclassif_knn<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    labels: PyReadonlyArray1<'py, i64>,
    ncomp: usize,
    k: usize,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let lab = numpy1d_to_usize_vec(labels);
    let result = to_pyresult(fdars_core::classification::fclassif_knn(
        &mat, &lab, None, ncomp, k,
    ))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("predicted", usize_vec_to_numpy1d(py, result.predicted))?;
    dict.set_item("accuracy", result.accuracy)?;
    Ok(dict)
}

/// Kernel classification for functional data.
#[pyfunction]
#[pyo3(signature = (data, argvals, labels, h_func=1.0, h_scalar=1.0))]
pub fn fclassif_kernel<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    labels: PyReadonlyArray1<'py, i64>,
    h_func: f64,
    h_scalar: f64,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let lab = numpy1d_to_usize_vec(labels);
    let result = to_pyresult(fdars_core::classification::fclassif_kernel(
        &mat, &lab, &av, None, h_func, h_scalar,
    ))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("predicted", usize_vec_to_numpy1d(py, result.predicted))?;
    dict.set_item("accuracy", result.accuracy)?;
    Ok(dict)
}

/// Cross-validated classification.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Data, shape (n, m).
/// argvals : numpy.ndarray
///     Evaluation points, length m.
/// labels : numpy.ndarray
///     Class labels, length n.
/// method : str, optional
///     "lda" (default), "qda", "knn", "kernel".
/// ncomp : int, optional
///     Number of FPC components (default 3).
/// nfold : int, optional
///     Number of CV folds (default 5).
///
/// Returns
/// -------
/// dict
///     error_rate, fold_errors (nfold,), best_ncomp.
#[pyfunction]
#[pyo3(signature = (data, argvals, labels, method="lda", ncomp=3, nfold=5))]
pub fn fclassif_cv<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    labels: PyReadonlyArray1<'py, i64>,
    method: &str,
    ncomp: usize,
    nfold: usize,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let lab = numpy1d_to_usize_vec(labels);
    let config = fdars_core::classification::ClassifCvConfig {
        method: method.to_string(),
        ncomp,
        nfold,
        ..Default::default()
    };
    let result = to_pyresult(fdars_core::classification::fclassif_cv_with_config(
        &mat, &av, &lab, None, &config,
    ))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("error_rate", result.error_rate)?;
    dict.set_item("fold_errors", vec_to_numpy1d(py, result.fold_errors))?;
    dict.set_item("best_ncomp", result.best_ncomp)?;
    Ok(dict)
}

/// Depth-based DD-classifier for functional data.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Data, shape (n, m).
/// labels : numpy.ndarray
///     Class labels, length n.
///
/// Returns
/// -------
/// dict
///     predicted (n,), accuracy.
#[pyfunction]
pub fn fclassif_dd<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    labels: PyReadonlyArray1<'py, i64>,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let lab = numpy1d_to_usize_vec(labels);
    let result = to_pyresult(fdars_core::classification::fclassif_dd(&mat, &lab, None))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("predicted", usize_vec_to_numpy1d(py, result.predicted))?;
    dict.set_item("accuracy", result.accuracy)?;
    Ok(dict)
}

/// k-NN classification from a precomputed distance matrix.
///
/// Parameters
/// ----------
/// dist_matrix : numpy.ndarray
///     Distance matrix, shape (n, n).
/// labels : numpy.ndarray
///     Class labels, length n.
/// k : int, optional
///     Number of nearest neighbors (default 5).
///
/// Returns
/// -------
/// dict
///     predicted (n,), accuracy.
#[pyfunction]
#[pyo3(signature = (dist_matrix, labels, k=5))]
pub fn knn_classify_from_distances<'py>(
    py: Python<'py>,
    dist_matrix: PyReadonlyArray2<'py, f64>,
    labels: PyReadonlyArray1<'py, i64>,
    k: usize,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let dm = numpy2d_to_fdmatrix(dist_matrix)?;
    let lab = numpy1d_to_usize_vec(labels);
    let result = to_pyresult(fdars_core::classification::knn_classify_from_distances(
        &dm, &lab, k,
    ))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("predicted", usize_vec_to_numpy1d(py, result.predicted))?;
    dict.set_item("accuracy", result.accuracy)?;
    Ok(dict)
}

/// Kernel classification from a precomputed functional distance matrix.
///
/// Parameters
/// ----------
/// func_dists : numpy.ndarray
///     Flat n x n functional distance matrix, shape (n, n).
/// labels : numpy.ndarray
///     Class labels, length n.
/// h_func : float, optional
///     Functional bandwidth (default 1.0, 0 = auto via LOO-CV).
/// h_scalar : float, optional
///     Scalar bandwidth (default 1.0).
///
/// Returns
/// -------
/// dict
///     predicted (n,), accuracy.
#[pyfunction]
#[pyo3(signature = (func_dists, labels, h_func=1.0, h_scalar=1.0))]
pub fn kernel_classify_from_distances<'py>(
    py: Python<'py>,
    func_dists: PyReadonlyArray2<'py, f64>,
    labels: PyReadonlyArray1<'py, i64>,
    h_func: f64,
    h_scalar: f64,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let dm = numpy2d_to_fdmatrix(func_dists)?;
    let lab = numpy1d_to_usize_vec(labels);
    // Flatten the distance matrix to a Vec<f64> (row-major)
    let flat_dists = dm.to_row_major();
    let result = to_pyresult(fdars_core::classification::kernel_classify_from_distances(
        &flat_dists,
        &lab,
        None,
        h_func,
        h_scalar,
    ))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("predicted", usize_vec_to_numpy1d(py, result.predicted))?;
    dict.set_item("accuracy", result.accuracy)?;
    Ok(dict)
}

// ---------------------------------------------------------------------------
// Elastic multinomial classification
// ---------------------------------------------------------------------------

/// Convert ElasticMultinomialResult to a Python dict (5 keys; class_models omitted).
///
/// `class_models: Vec<ElasticLogisticResult>` is deliberately NOT exposed — it is a
/// complex nested type whose fields are not needed for CLASS-01 (omission mirrors the
/// FunctionalGlmResult.fpca precedent).
fn elastic_multinomial_result_to_pydict<'py>(
    py: Python<'py>,
    r: fdars_core::elastic_regression::ElasticMultinomialResult,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("n_classes", r.n_classes)?;
    dict.set_item("classes", usize_vec_to_numpy1d(py, r.classes))?;
    // train_probabilities: FdMatrix shape (n, K) — each row sums to 1.0
    dict.set_item(
        "train_probabilities",
        fdmatrix_to_numpy2d(py, &r.train_probabilities),
    )?;
    dict.set_item(
        "predicted_classes",
        usize_vec_to_numpy1d(py, r.predicted_classes),
    )?;
    dict.set_item("train_accuracy", r.train_accuracy)?;
    Ok(dict)
}

/// K-class elastic multinomial classifier for functional data (one-vs-rest).
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Functional data, shape (n, m).
/// labels : numpy.ndarray
///     Class labels, dtype int64, 0-indexed contiguous (0..K). Must be non-negative.
/// argvals : numpy.ndarray
///     Evaluation points, length m.
/// ncomp_beta : int, optional
///     Number of B-spline basis functions per OvR model (default 10).
/// lambda_ : float, optional
///     Roughness penalty on beta (default 0.1).
/// max_iter : int, optional
///     IRLS max iterations per OvR binary fit (default 100).
/// tol : float, optional
///     Convergence tolerance (default 1e-4).
///
/// Returns
/// -------
/// dict
///     Keys: n_classes (int), classes (K,), train_probabilities (n,K),
///     predicted_classes (n,), train_accuracy (float).
///     `class_models` is NOT exposed.
///
/// Raises
/// ------
/// ValueError
///     If labels contain negative values (CR-01 guard fires before i64→usize cast).
///     If labels are non-contiguous (e.g. [0,2]) — surfaced from core via to_pyresult.
#[pyfunction]
#[pyo3(signature = (data, labels, argvals, ncomp_beta=10, lambda_=0.1, max_iter=100, tol=1e-4))]
pub fn elastic_multinomial<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    labels: PyReadonlyArray1<'py, i64>,
    argvals: PyReadonlyArray1<'py, f64>,
    ncomp_beta: usize,
    lambda_: f64,
    max_iter: usize,
    tol: f64,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);

    // CR-01 guard (T-38-02): negative label wraps to usize::MAX without this check;
    // mirrors oneway_anova_vstat pattern in inference_mod.rs:532-537
    let raw = labels.as_array();
    if raw.iter().any(|&x| x < 0) {
        return Err(pyo3::exceptions::PyValueError::new_err(
            "elastic_multinomial: labels must be non-negative 0-indexed integers; \
             got at least one negative value. Remap to 0..K before calling.",
        ));
    }
    let lab: Vec<usize> = raw.iter().map(|&x| x as usize).collect();

    let result = to_pyresult(fdars_core::elastic_regression::elastic_multinomial(
        &mat, &lab, &av, ncomp_beta, lambda_, max_iter, tol,
    ))?;
    elastic_multinomial_result_to_pydict(py, result)
}

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(fclassif_lda, m)?)?;
    m.add_function(wrap_pyfunction!(fclassif_qda, m)?)?;
    m.add_function(wrap_pyfunction!(fclassif_knn, m)?)?;
    m.add_function(wrap_pyfunction!(fclassif_kernel, m)?)?;
    m.add_function(wrap_pyfunction!(fclassif_cv, m)?)?;
    m.add_function(wrap_pyfunction!(fclassif_dd, m)?)?;
    m.add_function(wrap_pyfunction!(knn_classify_from_distances, m)?)?;
    m.add_function(wrap_pyfunction!(kernel_classify_from_distances, m)?)?;
    m.add_function(wrap_pyfunction!(elastic_multinomial, m)?)?;
    Ok(())
}
