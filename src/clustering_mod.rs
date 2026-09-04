//! Clustering for functional data.

use crate::convert::*;
use numpy::{IntoPyArray, PyReadonlyArray1, PyReadonlyArray2};
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

/// Silhouette score for cluster quality assessment (from data and argvals).
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Data, shape (n, m).
/// argvals : numpy.ndarray
///     Evaluation points, length m.
/// labels : numpy.ndarray
///     Cluster labels, shape (n,).
///
/// Returns
/// -------
/// list of float
///     Per-observation silhouette scores.
#[pyfunction]
pub fn silhouette_score_data<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    labels: PyReadonlyArray1<'py, i64>,
) -> PyResult<Bound<'py, PyAny>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let lab = numpy1d_to_usize_vec(labels);
    let scores = fdars_core::clustering::silhouette_score(&mat, &av, &lab);
    let arr = vec_to_numpy1d(py, scores);
    Ok(arr.into_any())
}

/// Calinski-Harabasz index for cluster quality (from data and argvals).
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Data, shape (n, m).
/// argvals : numpy.ndarray
///     Evaluation points, length m.
/// labels : numpy.ndarray
///     Cluster labels, shape (n,).
///
/// Returns
/// -------
/// float
///     Calinski-Harabasz score.
#[pyfunction]
pub fn calinski_harabasz_data(
    data: PyReadonlyArray2<'_, f64>,
    argvals: PyReadonlyArray1<'_, f64>,
    labels: PyReadonlyArray1<'_, i64>,
) -> PyResult<f64> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let lab = numpy1d_to_usize_vec(labels);
    Ok(fdars_core::clustering::calinski_harabasz(&mat, &av, &lab))
}

/// Density-based spatial clustering of functional data (DBSCAN).
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Data, shape (n, m).
/// argvals : numpy.ndarray
///     Evaluation points, length m.
/// eps : float, optional
///     Neighbourhood radius in L2 distance units (default 0.5).
/// min_points : int, optional
///     Minimum number of curves (including self) for a core point (default 3).
///
/// Returns
/// -------
/// dict
///     Dictionary with keys:
///     - cluster: numpy.ndarray, shape (n,), dtype int64. Cluster label for each
///       observation; -1 indicates a noise point, 0..n_clusters-1 are cluster ids.
///     - n_clusters: int. Number of clusters found (excluding noise).
///     - n_noise: int. Number of noise points.
///     - distances: numpy.ndarray, shape (n, n). Pairwise L2 distance matrix.
#[pyfunction]
#[pyo3(signature = (data, argvals, eps=0.5, min_points=3))]
pub fn dbscan_fd<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    eps: f64,
    min_points: usize,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let mut config = fdars_core::clustering_advanced::DbscanConfig::default();
    config.eps = eps;
    config.min_points = min_points;
    let result = to_pyresult(fdars_core::clustering_advanced::dbscan_fd(&mat, &av, &config))?;

    // Map None (noise) -> -1i64, Some(c) -> c as i64
    let cluster_i64: Vec<i64> = result.cluster.iter().map(|c| match c {
        None => -1,
        Some(v) => *v as i64,
    }).collect();

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("cluster", cluster_i64.into_pyarray(py))?;
    dict.set_item("n_clusters", result.n_clusters)?;
    dict.set_item("n_noise", result.n_noise)?;
    dict.set_item("distances", fdmatrix_to_numpy2d(py, &result.distances))?;
    Ok(dict)
}

/// K-means with per-cluster FPCA (KCFC) clustering for functional data.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Data, shape (n, m).
/// argvals : numpy.ndarray
///     Evaluation points, length m.
/// k : int, optional
///     Number of clusters (default 2).
/// ncomp : int, optional
///     Number of FPC components per cluster (default 3; clamped to min(n_k, m)).
/// max_iter : int, optional
///     Maximum iterations (default 50).
/// seed : int, optional
///     Random seed (default 42).
///
/// Returns
/// -------
/// dict
///     Dictionary with keys:
///     - cluster: numpy.ndarray, shape (n,), dtype int64. Cluster labels (0-based).
///     - reconstruction_errors: numpy.ndarray, shape (n, k). Per-observation reconstruction
///       error for each cluster.
///     - iterations: int. Number of iterations performed.
///     - converged: bool. Whether the algorithm converged.
///
/// Notes
/// -----
/// The internal ``fpca_models`` field is not exposed (internal Rust state).
#[pyfunction]
#[pyo3(signature = (data, argvals, k=2, ncomp=3, max_iter=50, seed=42))]
pub fn kcfc_cluster<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    k: usize,
    ncomp: usize,
    max_iter: usize,
    seed: u64,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let mut config = fdars_core::clustering_advanced::KcfcConfig::default();
    config.k = k;
    config.ncomp = ncomp;
    config.max_iter = max_iter;
    config.seed = seed;
    let result =
        to_pyresult(fdars_core::clustering_advanced::kcfc_cluster(&mat, &av, &config))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("cluster", usize_vec_to_numpy1d(py, result.cluster))?;
    dict.set_item(
        "reconstruction_errors",
        fdmatrix_to_numpy2d(py, &result.reconstruction_errors),
    )?;
    dict.set_item("iterations", result.iterations)?;
    dict.set_item("converged", result.converged)?;
    Ok(dict)
}

/// Fisher-EM discriminative functional clustering (FunFEM).
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Data, shape (n, m).
/// argvals : numpy.ndarray
///     Evaluation points, length m.
/// k : int, optional
///     Number of clusters (default 2).
/// ncomp : int, optional
///     Number of global FPC components (default 10; clamped to min(n, m)).
/// p_disc : int, optional
///     Discriminative subspace dimension (default 0 = auto: min(k-1, ncomp_eff)).
/// max_iter : int, optional
///     Maximum EM iterations (default 50).
/// tol : float, optional
///     Convergence tolerance (default 1e-6).
/// seed : int, optional
///     Random seed (default 42).
///
/// Returns
/// -------
/// dict
///     Dictionary with keys:
///     - cluster: numpy.ndarray, shape (n,), dtype int64. Hard cluster labels (0-based).
///     - membership: numpy.ndarray, shape (n, k). Soft assignment probabilities.
///     - disc_subspace: numpy.ndarray, shape (ncomp_eff, p_disc_eff). Discriminative
///       directions in FPC space.
///     - log_likelihood: float. Final log-likelihood value.
///     - iterations: int. Number of EM iterations performed.
///     - converged: bool. Whether the EM algorithm converged.
///
/// Notes
/// -----
/// ``p_disc=0`` (default) selects the discriminative dimension automatically as
/// ``min(k-1, ncomp_eff)``.
#[pyfunction]
#[pyo3(signature = (data, argvals, k=2, ncomp=10, p_disc=0, max_iter=50, tol=1e-6, seed=42))]
#[allow(clippy::too_many_arguments)]
pub fn funfem_cluster<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    k: usize,
    ncomp: usize,
    p_disc: usize,
    max_iter: usize,
    tol: f64,
    seed: u64,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let mut config = fdars_core::clustering_advanced::FunFemConfig::default();
    config.k = k;
    config.ncomp = ncomp;
    config.p_disc = p_disc;
    config.max_iter = max_iter;
    config.tol = tol;
    config.seed = seed;
    let result =
        to_pyresult(fdars_core::clustering_advanced::funfem_cluster(&mat, &av, &config))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("cluster", usize_vec_to_numpy1d(py, result.cluster))?;
    dict.set_item("membership", fdmatrix_to_numpy2d(py, &result.membership))?;
    dict.set_item("disc_subspace", fdmatrix_to_numpy2d(py, &result.disc_subspace))?;
    dict.set_item("log_likelihood", result.log_likelihood)?;
    dict.set_item("iterations", result.iterations)?;
    dict.set_item("converged", result.converged)?;
    Ok(dict)
}

/// Elastic-alignment functional clustering.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Data, shape (n, m).
/// argvals : numpy.ndarray
///     Evaluation points, length m.
/// k : int, optional
///     Number of clusters (default 2).
/// max_iter : int, optional
///     Maximum iterations (default 20).
/// seed : int, optional
///     Random seed (default 42).
/// use_amplitude_only : bool, optional
///     If True (default), use amplitude-only (shape-invariant) distance.
///     If False, use the full elastic distance.
/// elastic_lambda : float, optional
///     Penalty weight for the full elastic distance (default 0.0).
/// karcher_max_iter : int, optional
///     Maximum Karcher mean iterations (default 15).
/// karcher_tol : float, optional
///     Karcher mean convergence tolerance (default 1e-4).
///
/// Returns
/// -------
/// dict
///     Dictionary with keys:
///     - cluster: numpy.ndarray, shape (n,), dtype int64. Cluster labels (0-based).
///     - templates: list of numpy.ndarray. Length k; each array has shape (m,) and
///       represents the per-cluster template (Karcher mean) curve.
///     - distances: numpy.ndarray, shape (n, k). Elastic distance from each observation
///       to each cluster template.
///     - iterations: int. Number of iterations performed.
///     - converged: bool. Whether the algorithm converged.
#[pyfunction]
#[pyo3(signature = (data, argvals, k=2, max_iter=20, seed=42, use_amplitude_only=true, elastic_lambda=0.0, karcher_max_iter=15, karcher_tol=1e-4))]
#[allow(clippy::too_many_arguments)]
pub fn align_cluster_fd<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    k: usize,
    max_iter: usize,
    seed: u64,
    use_amplitude_only: bool,
    elastic_lambda: f64,
    karcher_max_iter: usize,
    karcher_tol: f64,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let mut config = fdars_core::clustering_advanced::AlignClusterConfig::default();
    config.k = k;
    config.max_iter = max_iter;
    config.seed = seed;
    config.use_amplitude_only = use_amplitude_only;
    config.elastic_lambda = elastic_lambda;
    config.karcher_max_iter = karcher_max_iter;
    config.karcher_tol = karcher_tol;
    let result =
        to_pyresult(fdars_core::clustering_advanced::align_cluster_fd(&mat, &av, &config))?;

    // Convert templates: Vec<Vec<f64>> -> PyList of (m,) numpy arrays
    let templates_list = pyo3::types::PyList::empty(py);
    for tmpl in result.templates {
        templates_list.append(vec_to_numpy1d(py, tmpl))?;
    }

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("cluster", usize_vec_to_numpy1d(py, result.cluster))?;
    dict.set_item("templates", templates_list)?;
    dict.set_item("distances", fdmatrix_to_numpy2d(py, &result.distances))?;
    dict.set_item("iterations", result.iterations)?;
    dict.set_item("converged", result.converged)?;
    Ok(dict)
}

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(kmeans_fd, m)?)?;
    m.add_function(wrap_pyfunction!(fuzzy_cmeans_fd, m)?)?;
    m.add_function(wrap_pyfunction!(gmm_cluster, m)?)?;
    m.add_function(wrap_pyfunction!(silhouette_score, m)?)?;
    m.add_function(wrap_pyfunction!(calinski_harabasz, m)?)?;
    m.add_function(wrap_pyfunction!(silhouette_score_data, m)?)?;
    m.add_function(wrap_pyfunction!(calinski_harabasz_data, m)?)?;
    m.add_function(wrap_pyfunction!(dbscan_fd, m)?)?;
    m.add_function(wrap_pyfunction!(kcfc_cluster, m)?)?;
    m.add_function(wrap_pyfunction!(funfem_cluster, m)?)?;
    m.add_function(wrap_pyfunction!(align_cluster_fd, m)?)?;
    Ok(())
}
