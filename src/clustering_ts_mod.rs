//! Time-series clustering: k-Shape, SBD k-medoids and DTW k-means with DBA
//! centroids (fdars-core 0.48).
//!
//! Registered into the existing `fdars.clustering` submodule by
//! `clustering_mod::register`; it is not a submodule of its own.

use crate::convert::*;
use crate::options::dtw_window;
use fdars_core::{
    DtwKMeansConfig, DtwKMeansInit, DtwKMeansMultivariateResult, DtwKMeansResult, KShapeConfig,
    KShapeResult,
};
use numpy::{PyArray1, PyArray2, PyReadonlyArray2};
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};

// ---------------------------------------------------------------------------
// Opaque #[pyclass] handles
// ---------------------------------------------------------------------------

/// Opaque handle wrapping a fitted fdars-core k-Shape model (KShapeResult).
///
/// Returned as ``"model"`` by `kshape_fd`. Exposes `predict`, `centroids`,
/// `cluster`, `inertia` and `n_clusters`.
#[pyclass(name = "PyKShapeFit")]
pub struct PyKShapeFit {
    pub inner: KShapeResult,
}

#[pymethods]
impl PyKShapeFit {
    /// z-normalized centroids, shape (k, m).
    #[getter]
    pub fn centroids<'py>(&self, py: Python<'py>) -> Bound<'py, PyArray2<f64>> {
        fdmatrix_to_numpy2d(py, &self.inner.centroids)
    }

    /// Training cluster labels (n,), int64.
    #[getter]
    pub fn cluster<'py>(&self, py: Python<'py>) -> Bound<'py, PyArray1<i64>> {
        usize_vec_to_numpy1d(py, self.inner.cluster.clone())
    }

    /// Final inertia (sum of SBD distances to the assigned centroids).
    #[getter]
    pub fn inertia(&self) -> f64 {
        self.inner.inertia
    }

    /// Number of clusters k.
    #[getter]
    pub fn n_clusters(&self) -> usize {
        self.inner.n_clusters()
    }

    /// Assign new curves to the nearest stored centroid by shape-based distance.
    ///
    /// Parameters
    /// ----------
    /// new_data : numpy.ndarray
    ///     Curves, shape (n_new, m), on the training grid length m.
    ///
    /// Returns
    /// -------
    /// numpy.ndarray
    ///     Labels (n_new,), int64.  ``predict(train_data)`` reproduces
    ///     `cluster`.
    pub fn predict<'py>(
        &self,
        py: Python<'py>,
        new_data: PyReadonlyArray2<'py, f64>,
    ) -> PyResult<Bound<'py, PyArray1<i64>>> {
        let mat = numpy2d_to_fdmatrix(new_data)?;
        Ok(usize_vec_to_numpy1d(
            py,
            to_pyresult(self.inner.predict(&mat))?,
        ))
    }
}

/// Opaque handle wrapping a fitted fdars-core DTW k-means model (DtwKMeansResult).
///
/// Returned as ``"model"`` by `dtw_kmeans`. Exposes `predict` (same window
/// as the fit), `centroids`, `cluster` and `inertia`.
#[pyclass(name = "PyDtwKMeansFit")]
pub struct PyDtwKMeansFit {
    pub inner: DtwKMeansResult,
}

#[pymethods]
impl PyDtwKMeansFit {
    /// DBA centroids, shape (k, m).
    #[getter]
    pub fn centroids<'py>(&self, py: Python<'py>) -> Bound<'py, PyArray2<f64>> {
        fdmatrix_to_numpy2d(py, &self.inner.centroids)
    }

    /// Training cluster labels (n,), int64.
    #[getter]
    pub fn cluster<'py>(&self, py: Python<'py>) -> Bound<'py, PyArray1<i64>> {
        usize_vec_to_numpy1d(py, self.inner.cluster.clone())
    }

    /// Mean DTW cost of each training curve to its assigned centroid.
    #[getter]
    pub fn inertia(&self) -> f64 {
        self.inner.inertia
    }

    /// Assign new curves to the nearest fitted centroid (DTW cost, fitted window).
    ///
    /// Parameters
    /// ----------
    /// new_data : numpy.ndarray
    ///     Curves, shape (n_new, m').
    ///
    /// Returns
    /// -------
    /// numpy.ndarray
    ///     Labels (n_new,), int64.  ``predict(train_data)`` reproduces
    ///     `cluster`.
    pub fn predict<'py>(
        &self,
        py: Python<'py>,
        new_data: PyReadonlyArray2<'py, f64>,
    ) -> PyResult<Bound<'py, PyArray1<i64>>> {
        let mat = numpy2d_to_fdmatrix(new_data)?;
        Ok(usize_vec_to_numpy1d(
            py,
            to_pyresult(self.inner.predict(&mat))?,
        ))
    }
}

/// Opaque handle wrapping a fitted multivariate DTW k-means model.
///
/// Returned as ``"model"`` by `dtw_kmeans_multivariate`. Exposes `predict`,
/// `centroids` (list of (d, m) arrays), `cluster` and `inertia`.
#[pyclass(name = "PyDtwKMeansMultivariateFit")]
pub struct PyDtwKMeansMultivariateFit {
    pub inner: DtwKMeansMultivariateResult,
}

#[pymethods]
impl PyDtwKMeansMultivariateFit {
    /// DBA centroids as a list of k arrays of shape (d, m).
    #[getter]
    pub fn centroids<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyList>> {
        fdmatrices_to_pylist(py, &self.inner.centroids)
    }

    /// Training cluster labels (n,), int64.
    #[getter]
    pub fn cluster<'py>(&self, py: Python<'py>) -> Bound<'py, PyArray1<i64>> {
        usize_vec_to_numpy1d(py, self.inner.cluster.clone())
    }

    /// Mean multichannel DTW cost of each training series to its centroid.
    #[getter]
    pub fn inertia(&self) -> f64 {
        self.inner.inertia
    }

    /// Assign new (d, m) series to the nearest fitted centroid (fitted window).
    ///
    /// Parameters
    /// ----------
    /// new_data : list of numpy.ndarray or numpy.ndarray
    ///     Series as a list of (d, m_i) arrays or a 3-D (n_new, d, m) array,
    ///     with the training channel count d.
    ///
    /// Returns
    /// -------
    /// numpy.ndarray
    ///     Labels (n_new,), int64.
    pub fn predict<'py>(
        &self,
        py: Python<'py>,
        new_data: &Bound<'py, PyAny>,
    ) -> PyResult<Bound<'py, PyArray1<i64>>> {
        let series = series_collection(new_data, "predict: new_data")?;
        Ok(usize_vec_to_numpy1d(
            py,
            to_pyresult(self.inner.predict(&series))?,
        ))
    }
}

// ---------------------------------------------------------------------------
// Private helpers
// ---------------------------------------------------------------------------

/// `init=None` / `"k-means++"`, or `None` when it is something else.
fn is_kmeanspp(init: Option<&Bound<'_, PyAny>>) -> PyResult<bool> {
    match init {
        None => Ok(true),
        Some(obj) => match obj.extract::<String>() {
            Ok(s) if s == "k-means++" => Ok(true),
            Ok(s) => Err(PyValueError::new_err(format!(
                "init must be 'k-means++' or explicit initial centroids, got '{s}'"
            ))),
            Err(_) => Ok(false),
        },
    }
}

fn dtw_kmeans_config(
    n_clusters: usize,
    n_init: usize,
    max_iter: usize,
    tol: f64,
    seed: u64,
    window: &str,
    radius: Option<usize>,
    window_fraction: Option<f64>,
    max_slope: Option<f64>,
    dba_max_iter: usize,
    dba_tol: f64,
) -> PyResult<DtwKMeansConfig> {
    let mut c = DtwKMeansConfig::default();
    c.n_clusters = n_clusters;
    c.n_init = n_init;
    c.max_iter = max_iter;
    c.tol = tol;
    c.seed = seed;
    c.window = dtw_window(window, radius, window_fraction, max_slope)?;
    c.dba_max_iter = dba_max_iter;
    c.dba_tol = dba_tol;
    Ok(c)
}

// ---------------------------------------------------------------------------
// Fit functions
// ---------------------------------------------------------------------------

/// k-Shape clustering of curves by shape-based distance (Paparrizos & Gravano 2015).
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Curves, shape (n, m).
/// n_clusters : int, optional
///     Number of clusters k, ``1 <= k <= n`` (default 2).
/// n_init : int, optional
///     Random-partition restarts; the lowest-inertia run is returned
///     (default 10).
/// max_iter : int, optional
///     Maximum Lloyd iterations per restart (default 100).
/// tol : float, optional
///     Convergence tolerance on the absolute inertia decrease (default 1e-6).
/// seed : int, optional
///     Base RNG seed; restart r is seeded ``seed + r`` (default 0).
///
/// Returns
/// -------
/// dict
///     ``centroids`` (k, m) z-normalized, ``cluster`` (n,) int64,
///     ``inertia``, ``iter``, ``converged``, ``n_init_best`` (0-based winning
///     restart), and ``model``: a `PyKShapeFit` with ``predict(new_data)``.
#[pyfunction]
#[pyo3(signature = (data, n_clusters=2, n_init=10, max_iter=100, tol=1e-6, seed=0))]
pub fn kshape_fd<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    n_clusters: usize,
    n_init: usize,
    max_iter: usize,
    tol: f64,
    seed: u64,
) -> PyResult<Bound<'py, PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let mut config = KShapeConfig::default();
    config.n_clusters = n_clusters;
    config.n_init = n_init;
    config.max_iter = max_iter;
    config.tol = tol;
    config.seed = seed;
    let res = to_pyresult(fdars_core::kshape_fd(&mat, &config))?;
    let d = PyDict::new(py);
    d.set_item("centroids", fdmatrix_to_numpy2d(py, &res.centroids))?;
    d.set_item("cluster", usize_vec_to_numpy1d(py, res.cluster.clone()))?;
    d.set_item("inertia", res.inertia)?;
    d.set_item("iter", res.iter)?;
    d.set_item("converged", res.converged)?;
    d.set_item("n_init_best", res.n_init_best)?;
    d.set_item("model", Py::new(py, PyKShapeFit { inner: res })?)?;
    Ok(d)
}

/// k-medoids clustering of curves on the shape-based distance (SBD) matrix.
///
/// Equivalent to ``alignment.kmedoids_from_distances(metric.sbd_distance_matrix(data), ...)``.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Curves, shape (n, m).
/// k : int, optional
///     Number of clusters (default 2).
/// max_iter : int, optional
///     Maximum iterations (default 100).
/// seed : int, optional
///     Seed of the k-means++ medoid initialisation (default 42).
///
/// Returns
/// -------
/// dict
///     ``labels`` (n,), ``medoid_indices`` (k,), ``within_distances`` (k,),
///     ``total_within_distance``, ``n_iter``, ``converged`` (the keys of
///     `alignment.kmedoids_from_distances`).
#[pyfunction]
#[pyo3(signature = (data, k=2, max_iter=100, seed=42))]
pub fn sbd_kmedoids<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    k: usize,
    max_iter: usize,
    seed: u64,
) -> PyResult<Bound<'py, PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let mut config = fdars_core::alignment::KMedoidsConfig::default();
    config.k = k;
    config.max_iter = max_iter;
    config.seed = seed;
    let res = to_pyresult(fdars_core::sbd_kmedoids(&mat, &config))?;
    let d = PyDict::new(py);
    d.set_item("labels", usize_vec_to_numpy1d(py, res.labels))?;
    d.set_item(
        "medoid_indices",
        usize_vec_to_numpy1d(py, res.medoid_indices),
    )?;
    d.set_item("within_distances", vec_to_numpy1d(py, res.within_distances))?;
    d.set_item("total_within_distance", res.total_within_distance)?;
    d.set_item("n_iter", res.n_iter)?;
    d.set_item("converged", res.converged)?;
    Ok(d)
}

/// DTW k-means clustering with DBA centroids (tslearn TimeSeriesKMeans(metric="dtw")).
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Curves, shape (n, m); all values finite.
/// n_clusters : int, optional
///     Number of clusters k, ``1 <= k <= n`` (default 2).
/// n_init : int, optional
///     k-means++ restarts; the lowest-inertia run is returned (default 10).
/// max_iter : int, optional
///     Maximum Lloyd iterations per restart (default 50).
/// tol : float, optional
///     Stop when the absolute inertia change is below `tol` (default 1e-6).
/// seed : int, optional
///     Base RNG seed; restart r is seeded ``seed + r`` (default 0).
/// window, radius, window_fraction, max_slope
///     Global window for assignment and DBA, see `metric.dtw_path`.
/// init : str or numpy.ndarray, optional
///     ``None`` / ``"k-means++"`` (DTW k-means++ seeding, default) or a
///     (k, m) array of initial centroids (every restart then starts from it).
/// dba_max_iter : int, optional
///     Maximum DBA iterations per centroid update (default 30).
/// dba_tol : float, optional
///     DBA cost-change tolerance per centroid update (default 1e-5).
///
/// Returns
/// -------
/// dict
///     ``centroids`` (k, m), ``cluster`` (n,) int64, ``inertia`` (mean DTW
///     cost to the assigned centroid for the final centroids), ``iter``,
///     ``converged``, ``n_init_best``, and ``model``: a `PyDtwKMeansFit`
///     with ``predict(new_data)``.
#[pyfunction]
#[pyo3(signature = (data, n_clusters=2, n_init=10, max_iter=50, tol=1e-6, seed=0, window="none", radius=None, window_fraction=None, max_slope=None, init=None, dba_max_iter=30, dba_tol=1e-5))]
pub fn dtw_kmeans<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    n_clusters: usize,
    n_init: usize,
    max_iter: usize,
    tol: f64,
    seed: u64,
    window: &str,
    radius: Option<usize>,
    window_fraction: Option<f64>,
    max_slope: Option<f64>,
    init: Option<&Bound<'py, PyAny>>,
    dba_max_iter: usize,
    dba_tol: f64,
) -> PyResult<Bound<'py, PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let mut config = dtw_kmeans_config(
        n_clusters,
        n_init,
        max_iter,
        tol,
        seed,
        window,
        radius,
        window_fraction,
        max_slope,
        dba_max_iter,
        dba_tol,
    )?;
    if !is_kmeanspp(init)? {
        let arr = init
            .unwrap()
            .extract::<PyReadonlyArray2<'py, f64>>()
            .map_err(|_| {
                PyValueError::new_err("init must be 'k-means++' or a 2-D (k, m) float array")
            })?;
        config.init = DtwKMeansInit::Centroids(numpy2d_to_fdmatrix(arr)?);
    }
    let res = to_pyresult(fdars_core::dtw_kmeans(&mat, &config))?;
    let d = PyDict::new(py);
    d.set_item("centroids", fdmatrix_to_numpy2d(py, &res.centroids))?;
    d.set_item("cluster", usize_vec_to_numpy1d(py, res.cluster.clone()))?;
    d.set_item("inertia", res.inertia)?;
    d.set_item("iter", res.iter)?;
    d.set_item("converged", res.converged)?;
    d.set_item("n_init_best", res.n_init_best)?;
    d.set_item("model", Py::new(py, PyDtwKMeansFit { inner: res })?)?;
    Ok(d)
}

/// DTW k-means of multivariate (d, m) series with multivariate DBA centroids.
///
/// Parameters
/// ----------
/// data : list of numpy.ndarray or numpy.ndarray
///     Series as a list of (d, m) arrays (same shape) or a 3-D (n, d, m)
///     array, channels as rows.
/// n_clusters, n_init, max_iter, tol, seed, window, radius, window_fraction, max_slope, dba_max_iter, dba_tol
///     As in `dtw_kmeans`.
/// init : str, list of numpy.ndarray or numpy.ndarray, optional
///     ``None`` / ``"k-means++"`` (default), or k initial centroids as a list
///     of (d, m) arrays or a (k, d, m) array.
///
/// Returns
/// -------
/// dict
///     ``centroids`` (list of k (d, m) arrays), ``cluster``, ``inertia``,
///     ``iter``, ``converged``, ``n_init_best``, and ``model``: a
///     `PyDtwKMeansMultivariateFit` with ``predict(new_data)``.  With
///     ``d = 1`` the result is bit-identical to `dtw_kmeans`.
#[pyfunction]
#[pyo3(signature = (data, n_clusters=2, n_init=10, max_iter=50, tol=1e-6, seed=0, window="none", radius=None, window_fraction=None, max_slope=None, init=None, dba_max_iter=30, dba_tol=1e-5))]
pub fn dtw_kmeans_multivariate<'py>(
    py: Python<'py>,
    data: &Bound<'py, PyAny>,
    n_clusters: usize,
    n_init: usize,
    max_iter: usize,
    tol: f64,
    seed: u64,
    window: &str,
    radius: Option<usize>,
    window_fraction: Option<f64>,
    max_slope: Option<f64>,
    init: Option<&Bound<'py, PyAny>>,
    dba_max_iter: usize,
    dba_tol: f64,
) -> PyResult<Bound<'py, PyDict>> {
    let series = series_collection(data, "dtw_kmeans_multivariate: data")?;
    let mut config = dtw_kmeans_config(
        n_clusters,
        n_init,
        max_iter,
        tol,
        seed,
        window,
        radius,
        window_fraction,
        max_slope,
        dba_max_iter,
        dba_tol,
    )?;
    if !is_kmeanspp(init)? {
        let cents = series_collection(init.unwrap(), "dtw_kmeans_multivariate: init")?;
        config.init = DtwKMeansInit::CentroidsMultivariate(cents);
    }
    let res = to_pyresult(fdars_core::dtw_kmeans_multivariate(&series, &config))?;
    let d = PyDict::new(py);
    d.set_item("centroids", fdmatrices_to_pylist(py, &res.centroids)?)?;
    d.set_item("cluster", usize_vec_to_numpy1d(py, res.cluster.clone()))?;
    d.set_item("inertia", res.inertia)?;
    d.set_item("iter", res.iter)?;
    d.set_item("converged", res.converged)?;
    d.set_item("n_init_best", res.n_init_best)?;
    d.set_item(
        "model",
        Py::new(py, PyDtwKMeansMultivariateFit { inner: res })?,
    )?;
    Ok(d)
}

/// Register the time-series clustering functions into the `clustering` submodule.
pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyKShapeFit>()?;
    m.add_class::<PyDtwKMeansFit>()?;
    m.add_class::<PyDtwKMeansMultivariateFit>()?;
    m.add_function(wrap_pyfunction!(kshape_fd, m)?)?;
    m.add_function(wrap_pyfunction!(sbd_kmedoids, m)?)?;
    m.add_function(wrap_pyfunction!(dtw_kmeans, m)?)?;
    m.add_function(wrap_pyfunction!(dtw_kmeans_multivariate, m)?)?;
    Ok(())
}
