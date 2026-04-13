//! Clustering for functional data.

use crate::convert::*;
use numpy::{PyReadonlyArray1, PyReadonlyArray2};
use pyo3::prelude::*;

/// K-means clustering for functional data.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Data, shape (n, m).
/// argvals : numpy.ndarray
///     Evaluation points, length m.
/// k : int
///     Number of clusters.
/// max_iter : int, optional
///     Maximum iterations (default 100).
/// tol : float, optional
///     Convergence tolerance (default 1e-6).
/// seed : int, optional
///     Random seed (default 42).
///
/// Returns
/// -------
/// dict
///     Dictionary with keys: cluster (n,), centers (k, m), tot_withinss (float),
///     iter (int), converged (bool).
#[pyfunction]
#[pyo3(signature = (data, argvals, k, max_iter=100, tol=1e-6, seed=42))]
pub fn kmeans_fd<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    k: usize,
    max_iter: usize,
    tol: f64,
    seed: u64,
) -> PyResult<Bound<'py, PyAny>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let result = to_pyresult(fdars_core::clustering::kmeans_fd(
        &mat, &av, k, max_iter, tol, seed,
    ))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("cluster", usize_vec_to_numpy1d(py, result.cluster))?;
    dict.set_item("centers", fdmatrix_to_numpy2d(py, &result.centers))?;
    dict.set_item("tot_withinss", result.tot_withinss)?;
    dict.set_item("iter", result.iter)?;
    dict.set_item("converged", result.converged)?;
    Ok(dict.into_any())
}

/// Fuzzy C-means clustering for functional data.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Data, shape (n, m).
/// argvals : numpy.ndarray
///     Evaluation points, length m.
/// k : int
///     Number of clusters.
/// fuzziness : float, optional
///     Fuzziness parameter (default 2.0).
/// max_iter : int, optional
///     Maximum iterations (default 100).
/// tol : float, optional
///     Convergence tolerance (default 1e-6).
/// seed : int, optional
///     Random seed (default 42).
///
/// Returns
/// -------
/// dict
///     Dictionary with keys: cluster (n,), membership (n, k), centers (k, m).
#[pyfunction]
#[pyo3(signature = (data, argvals, k, fuzziness=2.0, max_iter=100, tol=1e-6, seed=42))]
pub fn fuzzy_cmeans_fd<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    k: usize,
    fuzziness: f64,
    max_iter: usize,
    tol: f64,
    seed: u64,
) -> PyResult<Bound<'py, PyAny>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let result = to_pyresult(fdars_core::clustering::fuzzy_cmeans_fd(
        &mat, &av, k, fuzziness, max_iter, tol, seed,
    ))?;

    // Compute hard cluster assignments from membership matrix (argmax per row)
    let n = result.membership.nrows();
    let n_clusters = result.membership.ncols();
    let cluster: Vec<usize> = (0..n)
        .map(|i| {
            let mut best_c = 0;
            let mut best_val = f64::NEG_INFINITY;
            for c in 0..n_clusters {
                let val = result.membership[(i, c)];
                if val > best_val {
                    best_val = val;
                    best_c = c;
                }
            }
            best_c
        })
        .collect();

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("cluster", usize_vec_to_numpy1d(py, cluster))?;
    dict.set_item("membership", fdmatrix_to_numpy2d(py, &result.membership))?;
    dict.set_item("centers", fdmatrix_to_numpy2d(py, &result.centers))?;
    Ok(dict.into_any())
}

/// GMM clustering for functional data (via basis projection).
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Data, shape (n, m).
/// argvals : numpy.ndarray
///     Evaluation points, length m.
/// k_range : list of int
///     Range of K values to try.
/// nbasis : int, optional
///     Number of basis functions (default 5).
/// max_iter : int, optional
///     Maximum EM iterations (default 200).
/// tol : float, optional
///     Convergence tolerance (default 1e-6).
/// seed : int, optional
///     Random seed (default 42).
///
/// Returns
/// -------
/// dict
///     Dictionary with keys: cluster (n,), membership (n, k),
///     bic_values (list of tuples), icl_values (list of tuples).
#[pyfunction]
#[pyo3(signature = (data, argvals, k_range, nbasis=5, max_iter=200, tol=1e-6, seed=42))]
pub fn gmm_cluster<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    k_range: Vec<usize>,
    nbasis: usize,
    max_iter: usize,
    tol: f64,
    seed: u64,
) -> PyResult<Bound<'py, PyAny>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let mut config = fdars_core::gmm::GmmClusterConfig::default();
    config.nbasis = nbasis;
    config.max_iter = max_iter;
    config.tol = tol;
    config.seed = seed;
    let result = to_pyresult(fdars_core::gmm::gmm_cluster_with_config(
        &mat, &av, None, &k_range, &config,
    ))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("cluster", usize_vec_to_numpy1d(py, result.best.cluster))?;
    dict.set_item(
        "membership",
        fdmatrix_to_numpy2d(py, &result.best.membership),
    )?;
    let bic_list: Vec<(usize, f64)> = result.bic_values;
    dict.set_item("bic_values", bic_list)?;
    let icl_list: Vec<(usize, f64)> = result.icl_values;
    dict.set_item("icl_values", icl_list)?;
    Ok(dict.into_any())
}

/// Silhouette score for cluster quality assessment (from distance matrix).
///
/// Parameters
/// ----------
/// dist_matrix : numpy.ndarray
///     Distance matrix, shape (n, n).
/// labels : numpy.ndarray
///     Cluster labels, shape (n,).
///
/// Returns
/// -------
/// list of float
///     Per-observation silhouette scores.
#[pyfunction]
pub fn silhouette_score<'py>(
    py: Python<'py>,
    dist_matrix: PyReadonlyArray2<'py, f64>,
    labels: PyReadonlyArray1<'py, i64>,
) -> PyResult<Bound<'py, PyAny>> {
    let dm = numpy2d_to_fdmatrix(dist_matrix)?;
    let lab = numpy1d_to_usize_vec(labels);
    let scores = fdars_core::clustering::silhouette_score_from_distances(&dm, &lab);
    let arr = vec_to_numpy1d(py, scores);
    Ok(arr.into_any())
}

/// Calinski-Harabasz index for cluster quality (from distance matrix).
///
/// Parameters
/// ----------
/// dist_matrix : numpy.ndarray
///     Distance matrix, shape (n, n).
/// labels : numpy.ndarray
///     Cluster labels, shape (n,).
///
/// Returns
/// -------
/// float
///     Calinski-Harabasz score.
#[pyfunction]
pub fn calinski_harabasz(
    dist_matrix: PyReadonlyArray2<'_, f64>,
    labels: PyReadonlyArray1<'_, i64>,
) -> PyResult<f64> {
    let dm = numpy2d_to_fdmatrix(dist_matrix)?;
    let lab = numpy1d_to_usize_vec(labels);
    Ok(fdars_core::clustering::calinski_harabasz_from_distances(
        &dm, &lab,
    ))
}

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(kmeans_fd, m)?)?;
    m.add_function(wrap_pyfunction!(fuzzy_cmeans_fd, m)?)?;
    m.add_function(wrap_pyfunction!(gmm_cluster, m)?)?;
    m.add_function(wrap_pyfunction!(silhouette_score, m)?)?;
    m.add_function(wrap_pyfunction!(calinski_harabasz, m)?)?;
    Ok(())
}
