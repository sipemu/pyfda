//! Distance metrics for functional data.

use crate::convert::*;
use fdars_core::metric::gak::{
    gak as core_gak, gak_gram_matrix as core_gak_gram_matrix,
    gak_gram_predict as core_gak_gram_predict, gak_gram_train as core_gak_gram_train,
    sigma_gak as core_sigma_gak, GakConfig, GakGramTrain,
};

/// Build a GakConfig from an optional sigma value.
///
/// GakConfig is #[non_exhaustive], so struct literal syntax is not available
/// from outside the crate.  This helper constructs the config via the provided
/// public constructors (with_sigma / Default).
#[inline]
fn make_gak_config(sigma: Option<f64>) -> GakConfig {
    match sigma {
        Some(s) => GakConfig::with_sigma(s),
        None => GakConfig::default(),
    }
}
use numpy::{PyArray1, PyArray2, PyReadonlyArray1, PyReadonlyArray2};
use pyo3::prelude::*;

// ---------------------------------------------------------------------------
// Opaque #[pyclass] handle: PyGakGramTrain
// ---------------------------------------------------------------------------

/// Opaque handle wrapping fdars-core GakGramTrain for incremental GAK Gram computation.
///
/// Construct via `fdars.metric.gak_gram_train(data)`.
/// Use with `fdars.metric.gak_gram_predict(handle, new_data)` for the sklearn
/// precomputed-kernel workflow.
///
/// Exposes:
///   - `.gram` — (n_train, n_train) numpy array (the training Gram matrix)
///   - `.sigma` — the resolved bandwidth (float > 0)
///   - `.n_train` — number of training observations (int)
#[pyclass(name = "PyGakGramTrain")]
pub struct PyGakGramTrain {
    pub inner: GakGramTrain,
}

#[pymethods]
impl PyGakGramTrain {
    /// Training Gram matrix, shape (n_train, n_train).
    #[getter]
    pub fn gram<'py>(&self, py: Python<'py>) -> Bound<'py, PyArray2<f64>> {
        fdmatrix_to_numpy2d(py, &self.inner.gram)
    }

    /// Resolved GAK bandwidth (sigma > 0).
    #[getter]
    pub fn sigma(&self) -> f64 {
        self.inner.sigma
    }

    /// Number of training observations.
    #[getter]
    pub fn n_train(&self) -> usize {
        self.inner.gram.nrows()
    }
}

// ---------------------------------------------------------------------------
// GAK scalar functions
// ---------------------------------------------------------------------------

/// Global Alignment Kernel between two 1-D time series.
///
/// Parameters
/// ----------
/// x : numpy.ndarray
///     First series (1D).
/// y : numpy.ndarray
///     Second series (1D).
/// sigma : float
///     Bandwidth parameter (must be > 0).  Use `sigma_gak` to select
///     automatically from data.
///
/// Returns
/// -------
/// float
///     GAK similarity in [0, 1].  `gak(x, x, sigma)` == 1.0 exactly.
///     Returns 0.0 if `sigma <= 0` or either series is empty.
#[pyfunction]
pub fn gak<'py>(
    _py: Python<'py>,
    x: PyReadonlyArray1<'py, f64>,
    y: PyReadonlyArray1<'py, f64>,
    sigma: f64,
) -> PyResult<f64> {
    Ok(core_gak(x.as_slice()?, y.as_slice()?, sigma))
}

/// Heuristic GAK bandwidth: median pairwise Euclidean distance, floored at 1e-8.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     2D array of shape (n, m) — rows are observations.
///
/// Returns
/// -------
/// float
///     Bandwidth estimate (always > 0).
#[pyfunction]
pub fn sigma_gak<'py>(
    _py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
) -> PyResult<f64> {
    let mat = numpy2d_to_fdmatrix(data)?;
    Ok(core_sigma_gak(&mat))
}

/// Global Alignment Kernel Gram matrix (one-shot, symmetric).
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     2D array of shape (n, m) — rows are observations.
/// sigma : float, optional
///     Bandwidth.  If None (default), selected automatically via `sigma_gak`.
///
/// Returns
/// -------
/// numpy.ndarray
///     Symmetric PSD Gram matrix of shape (n, n) with unit diagonal.
///     Directly usable as a precomputed kernel with sklearn.
#[pyfunction]
#[pyo3(signature = (data, sigma=None))]
pub fn gak_gram_matrix<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    sigma: Option<f64>,
) -> PyResult<Bound<'py, PyArray2<f64>>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let config = make_gak_config(sigma);
    let result = to_pyresult(core_gak_gram_matrix(&mat, &config))?;
    Ok(fdmatrix_to_numpy2d(py, &result))
}

// ---------------------------------------------------------------------------
// GAK train/predict handle functions
// ---------------------------------------------------------------------------

/// Fit a GAK Gram handle for incremental train/predict computation.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Training data, shape (n_train, m).
/// sigma : float, optional
///     Bandwidth.  If None (default), selected automatically via `sigma_gak`.
///
/// Returns
/// -------
/// PyGakGramTrain
///     Opaque handle storing the training Gram, sigma, and auxiliary structures
///     needed by `gak_gram_predict`.
#[pyfunction]
#[pyo3(signature = (data, sigma=None))]
pub fn gak_gram_train<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    sigma: Option<f64>,
) -> PyResult<Py<PyGakGramTrain>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let config = make_gak_config(sigma);
    let inner = to_pyresult(core_gak_gram_train(&mat, &config))?;
    Py::new(py, PyGakGramTrain { inner })
}

/// Compute the GAK Gram matrix between new data and the training set.
///
/// Parameters
/// ----------
/// train : PyGakGramTrain
///     Handle returned by `gak_gram_train`.
/// new_data : numpy.ndarray
///     Test data, shape (n_test, m).  Must have the same number of columns as
///     the training data.
///
/// Returns
/// -------
/// numpy.ndarray
///     Gram matrix of shape (n_test, n_train).  Directly usable with sklearn
///     `SVC(kernel='precomputed').predict(K_test)`.
#[pyfunction]
pub fn gak_gram_predict<'py>(
    py: Python<'py>,
    train: &PyGakGramTrain,
    new_data: PyReadonlyArray2<'py, f64>,
) -> PyResult<Bound<'py, PyArray2<f64>>> {
    let mat = numpy2d_to_fdmatrix(new_data)?;
    let result = to_pyresult(core_gak_gram_predict(&train.inner, &mat))?;
    Ok(fdmatrix_to_numpy2d(py, &result))
}

/// Lp distance matrix (self) for 1D functional data.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     2D array of shape (n, m).
/// argvals : numpy.ndarray
///     Evaluation points, length m.
/// p : float, optional
///     Lp exponent (default 2.0). Use float('inf') for L-infinity.
///
/// Returns
/// -------
/// numpy.ndarray
///     Distance matrix of shape (n, n).
#[pyfunction]
#[pyo3(signature = (data, argvals, p=2.0))]
pub fn lp_self_1d<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    p: f64,
) -> PyResult<Bound<'py, PyArray2<f64>>> {
    let d = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let result = fdars_core::metric::lp_self_1d(&d, &av, p, &[]);
    Ok(fdmatrix_to_numpy2d(py, &result))
}

/// Lp distance matrix (cross) between two 1D functional datasets.
///
/// Parameters
/// ----------
/// data1 : numpy.ndarray
///     First dataset, shape (n1, m).
/// data2 : numpy.ndarray
///     Second dataset, shape (n2, m).
/// argvals : numpy.ndarray
///     Evaluation points, length m.
/// p : float, optional
///     Lp exponent (default 2.0).
///
/// Returns
/// -------
/// numpy.ndarray
///     Distance matrix of shape (n1, n2).
#[pyfunction]
#[pyo3(signature = (data1, data2, argvals, p=2.0))]
pub fn lp_cross_1d<'py>(
    py: Python<'py>,
    data1: PyReadonlyArray2<'py, f64>,
    data2: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    p: f64,
) -> PyResult<Bound<'py, PyArray2<f64>>> {
    let d1 = numpy2d_to_fdmatrix(data1)?;
    let d2 = numpy2d_to_fdmatrix(data2)?;
    let av = numpy1d_to_vec(argvals);
    let result = fdars_core::metric::lp_cross_1d(&d1, &d2, &av, p, &[]);
    Ok(fdmatrix_to_numpy2d(py, &result))
}

/// Lp distance matrix (self) for 2D functional data.
#[pyfunction]
#[pyo3(signature = (data, argvals_s, argvals_t, p=2.0))]
pub fn lp_self_2d<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals_s: PyReadonlyArray1<'py, f64>,
    argvals_t: PyReadonlyArray1<'py, f64>,
    p: f64,
) -> PyResult<Bound<'py, PyArray2<f64>>> {
    let d = numpy2d_to_fdmatrix(data)?;
    let avs = numpy1d_to_vec(argvals_s);
    let avt = numpy1d_to_vec(argvals_t);
    let result = fdars_core::metric::lp_self_2d(&d, &avs, &avt, p, &[]);
    Ok(fdmatrix_to_numpy2d(py, &result))
}

/// Lp cross distance for 2D data.
#[pyfunction]
#[pyo3(signature = (data1, data2, argvals_s, argvals_t, p=2.0))]
pub fn lp_cross_2d<'py>(
    py: Python<'py>,
    data1: PyReadonlyArray2<'py, f64>,
    data2: PyReadonlyArray2<'py, f64>,
    argvals_s: PyReadonlyArray1<'py, f64>,
    argvals_t: PyReadonlyArray1<'py, f64>,
    p: f64,
) -> PyResult<Bound<'py, PyArray2<f64>>> {
    let d1 = numpy2d_to_fdmatrix(data1)?;
    let d2 = numpy2d_to_fdmatrix(data2)?;
    let avs = numpy1d_to_vec(argvals_s);
    let avt = numpy1d_to_vec(argvals_t);
    let result = fdars_core::metric::lp_cross_2d(&d1, &d2, &avs, &avt, p, &[]);
    Ok(fdmatrix_to_numpy2d(py, &result))
}

/// Hausdorff distance matrix (self) for 1D data.
#[pyfunction]
pub fn hausdorff_self_1d<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
) -> PyResult<Bound<'py, PyArray2<f64>>> {
    let d = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let result = fdars_core::metric::hausdorff_self_1d(&d, &av);
    Ok(fdmatrix_to_numpy2d(py, &result))
}

/// Hausdorff cross distance for 1D data.
#[pyfunction]
pub fn hausdorff_cross_1d<'py>(
    py: Python<'py>,
    data1: PyReadonlyArray2<'py, f64>,
    data2: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
) -> PyResult<Bound<'py, PyArray2<f64>>> {
    let d1 = numpy2d_to_fdmatrix(data1)?;
    let d2 = numpy2d_to_fdmatrix(data2)?;
    let av = numpy1d_to_vec(argvals);
    let result = fdars_core::metric::hausdorff_cross_1d(&d1, &d2, &av);
    Ok(fdmatrix_to_numpy2d(py, &result))
}

/// Hausdorff self distance for 2D data.
#[pyfunction]
pub fn hausdorff_self_2d<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals_s: PyReadonlyArray1<'py, f64>,
    argvals_t: PyReadonlyArray1<'py, f64>,
) -> PyResult<Bound<'py, PyArray2<f64>>> {
    let d = numpy2d_to_fdmatrix(data)?;
    let avs = numpy1d_to_vec(argvals_s);
    let avt = numpy1d_to_vec(argvals_t);
    let result = fdars_core::metric::hausdorff_self_2d(&d, &avs, &avt);
    Ok(fdmatrix_to_numpy2d(py, &result))
}

/// Hausdorff cross distance for 2D data.
#[pyfunction]
pub fn hausdorff_cross_2d<'py>(
    py: Python<'py>,
    data1: PyReadonlyArray2<'py, f64>,
    data2: PyReadonlyArray2<'py, f64>,
    argvals_s: PyReadonlyArray1<'py, f64>,
    argvals_t: PyReadonlyArray1<'py, f64>,
) -> PyResult<Bound<'py, PyArray2<f64>>> {
    let d1 = numpy2d_to_fdmatrix(data1)?;
    let d2 = numpy2d_to_fdmatrix(data2)?;
    let avs = numpy1d_to_vec(argvals_s);
    let avt = numpy1d_to_vec(argvals_t);
    let result = fdars_core::metric::hausdorff_cross_2d(&d1, &d2, &avs, &avt);
    Ok(fdmatrix_to_numpy2d(py, &result))
}

/// DTW distance matrix (self) for 1D data.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Data, shape (n, m).
/// p : float, optional
///     Lp exponent for cost (default 2.0).
/// w : int, optional
///     Sakoe-Chiba band width (default 0 = no constraint).
///
/// Returns
/// -------
/// numpy.ndarray
///     Distance matrix of shape (n, n).
#[pyfunction]
#[pyo3(signature = (data, p=2.0, w=0))]
pub fn dtw_self_1d<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    p: f64,
    w: usize,
) -> PyResult<Bound<'py, PyArray2<f64>>> {
    let d = numpy2d_to_fdmatrix(data)?;
    let band = if w == 0 { d.ncols() } else { w };
    let result = fdars_core::metric::dtw_self_1d(&d, p, band);
    Ok(fdmatrix_to_numpy2d(py, &result))
}

/// DTW cross distance for 1D data.
///
/// Parameters
/// ----------
/// data1 : numpy.ndarray
///     First dataset, shape (n1, m1).
/// data2 : numpy.ndarray
///     Second dataset, shape (n2, m2).
/// p : float, optional
///     Lp exponent for cost (default 2.0).
/// w : int, optional
///     Sakoe-Chiba band width (default 0 = no constraint).
///
/// Returns
/// -------
/// numpy.ndarray
///     Distance matrix of shape (n1, n2).
#[pyfunction]
#[pyo3(signature = (data1, data2, p=2.0, w=0))]
pub fn dtw_cross_1d<'py>(
    py: Python<'py>,
    data1: PyReadonlyArray2<'py, f64>,
    data2: PyReadonlyArray2<'py, f64>,
    p: f64,
    w: usize,
) -> PyResult<Bound<'py, PyArray2<f64>>> {
    let d1 = numpy2d_to_fdmatrix(data1)?;
    let d2 = numpy2d_to_fdmatrix(data2)?;
    let band = if w == 0 {
        d1.ncols().max(d2.ncols())
    } else {
        w
    };
    let result = fdars_core::metric::dtw_cross_1d(&d1, &d2, p, band);
    Ok(fdmatrix_to_numpy2d(py, &result))
}

/// Soft-DTW distance matrix (self) for 1D data.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Data, shape (n, m).
/// gamma : float, optional
///     Smoothing parameter (default 1.0).
///
/// Returns
/// -------
/// numpy.ndarray
///     Distance matrix of shape (n, n).
#[pyfunction]
#[pyo3(signature = (data, gamma=1.0))]
pub fn soft_dtw_self_1d<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    gamma: f64,
) -> PyResult<Bound<'py, PyArray2<f64>>> {
    let d = numpy2d_to_fdmatrix(data)?;
    let result = fdars_core::metric::soft_dtw_self_1d(&d, gamma);
    Ok(fdmatrix_to_numpy2d(py, &result))
}

/// Soft-DTW cross distance for 1D data.
#[pyfunction]
#[pyo3(signature = (data1, data2, gamma=1.0))]
pub fn soft_dtw_cross_1d<'py>(
    py: Python<'py>,
    data1: PyReadonlyArray2<'py, f64>,
    data2: PyReadonlyArray2<'py, f64>,
    gamma: f64,
) -> PyResult<Bound<'py, PyArray2<f64>>> {
    let d1 = numpy2d_to_fdmatrix(data1)?;
    let d2 = numpy2d_to_fdmatrix(data2)?;
    let result = fdars_core::metric::soft_dtw_cross_1d(&d1, &d2, gamma);
    Ok(fdmatrix_to_numpy2d(py, &result))
}

/// Soft-DTW divergence distance matrix (self) for 1D data.
#[pyfunction]
#[pyo3(signature = (data, gamma=1.0))]
pub fn soft_dtw_div_self_1d<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    gamma: f64,
) -> PyResult<Bound<'py, PyArray2<f64>>> {
    let d = numpy2d_to_fdmatrix(data)?;
    let result = fdars_core::metric::soft_dtw_div_self_1d(&d, gamma);
    Ok(fdmatrix_to_numpy2d(py, &result))
}

/// Soft-DTW divergence cross distance.
#[pyfunction]
#[pyo3(signature = (data1, data2, gamma=1.0))]
pub fn soft_dtw_div_cross_1d<'py>(
    py: Python<'py>,
    data1: PyReadonlyArray2<'py, f64>,
    data2: PyReadonlyArray2<'py, f64>,
    gamma: f64,
) -> PyResult<Bound<'py, PyArray2<f64>>> {
    let d1 = numpy2d_to_fdmatrix(data1)?;
    let d2 = numpy2d_to_fdmatrix(data2)?;
    let result = fdars_core::metric::soft_dtw_div_cross_1d(&d1, &d2, gamma);
    Ok(fdmatrix_to_numpy2d(py, &result))
}

/// Fourier coefficient distance (self) for 1D data.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Data, shape (n, m).
/// n_basis : int, optional
///     Number of Fourier basis functions (default 5).
///
/// Returns
/// -------
/// numpy.ndarray
///     Distance matrix of shape (n, n).
#[pyfunction]
#[pyo3(signature = (data, n_basis=5))]
pub fn fourier_self_1d<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    n_basis: usize,
) -> PyResult<Bound<'py, PyArray2<f64>>> {
    let d = numpy2d_to_fdmatrix(data)?;
    let result = fdars_core::metric::fourier_self_1d(&d, n_basis);
    Ok(fdmatrix_to_numpy2d(py, &result))
}

/// Fourier coefficient distance (cross).
#[pyfunction]
#[pyo3(signature = (data1, data2, n_basis=5))]
pub fn fourier_cross_1d<'py>(
    py: Python<'py>,
    data1: PyReadonlyArray2<'py, f64>,
    data2: PyReadonlyArray2<'py, f64>,
    n_basis: usize,
) -> PyResult<Bound<'py, PyArray2<f64>>> {
    let d1 = numpy2d_to_fdmatrix(data1)?;
    let d2 = numpy2d_to_fdmatrix(data2)?;
    let result = fdars_core::metric::fourier_cross_1d(&d1, &d2, n_basis);
    Ok(fdmatrix_to_numpy2d(py, &result))
}

/// Horizontal shift distance (self) for 1D data.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Data, shape (n, m).
/// argvals : numpy.ndarray
///     Evaluation points, length m.
/// max_shift : int, optional
///     Maximum shift in grid points (default 0 = m/4).
///
/// Returns
/// -------
/// numpy.ndarray
///     Distance matrix of shape (n, n).
#[pyfunction]
#[pyo3(signature = (data, argvals, max_shift=0))]
pub fn hshift_self_1d<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    max_shift: usize,
) -> PyResult<Bound<'py, PyArray2<f64>>> {
    let d = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let shift = if max_shift == 0 {
        av.len() / 4
    } else {
        max_shift
    };
    let result = fdars_core::metric::hshift_self_1d(&d, &av, shift);
    Ok(fdmatrix_to_numpy2d(py, &result))
}

/// Horizontal shift distance (cross).
///
/// Parameters
/// ----------
/// data1 : numpy.ndarray
///     First dataset, shape (n1, m).
/// data2 : numpy.ndarray
///     Second dataset, shape (n2, m).
/// argvals : numpy.ndarray
///     Evaluation points, length m.
/// max_shift : int, optional
///     Maximum shift in grid points (default 0 = m/4).
///
/// Returns
/// -------
/// numpy.ndarray
///     Distance matrix of shape (n1, n2).
#[pyfunction]
#[pyo3(signature = (data1, data2, argvals, max_shift=0))]
pub fn hshift_cross_1d<'py>(
    py: Python<'py>,
    data1: PyReadonlyArray2<'py, f64>,
    data2: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    max_shift: usize,
) -> PyResult<Bound<'py, PyArray2<f64>>> {
    let d1 = numpy2d_to_fdmatrix(data1)?;
    let d2 = numpy2d_to_fdmatrix(data2)?;
    let av = numpy1d_to_vec(argvals);
    let shift = if max_shift == 0 {
        av.len() / 4
    } else {
        max_shift
    };
    let result = fdars_core::metric::hshift_cross_1d(&d1, &d2, &av, shift);
    Ok(fdmatrix_to_numpy2d(py, &result))
}

/// Simpson's-rule integral of each curve.
///
/// Matches R `int.simpson`. Returns one integral per row of `data`.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Curves, shape (n, m).
/// argvals : numpy.ndarray, optional
///     Evaluation grid, length m. Defaults to a uniform [0, 1] grid.
///
/// Returns
/// -------
/// numpy.ndarray
///     Integrals, length n.
#[pyfunction]
#[pyo3(signature = (data, argvals=None))]
pub fn int_simpson<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: Option<PyReadonlyArray1<'py, f64>>,
) -> PyResult<Bound<'py, PyArray1<f64>>> {
    let d = numpy2d_to_fdmatrix(data)?;
    let av = default_grid(argvals, d.ncols());
    let result: Vec<f64> = (0..d.nrows())
        .map(|i| fdars_core::utility::integrate_simpson(&d.row(i), &av))
        .collect();
    Ok(vec_to_numpy1d(py, result))
}

/// Inner product between two functional data sets (Simpson-integrated).
///
/// Matches R `inprod.fdata`. Returns the Gram matrix of inner products between
/// every row of `data1` and every row of `data2`.
///
/// Parameters
/// ----------
/// data1 : numpy.ndarray
///     Curves, shape (n1, m).
/// data2 : numpy.ndarray
///     Curves, shape (n2, m).
/// argvals : numpy.ndarray, optional
///     Evaluation grid, length m. Defaults to a uniform [0, 1] grid.
///
/// Returns
/// -------
/// numpy.ndarray
///     Inner-product matrix, shape (n1, n2).
#[pyfunction]
#[pyo3(signature = (data1, data2, argvals=None))]
pub fn inprod<'py>(
    py: Python<'py>,
    data1: PyReadonlyArray2<'py, f64>,
    data2: PyReadonlyArray2<'py, f64>,
    argvals: Option<PyReadonlyArray1<'py, f64>>,
) -> PyResult<Bound<'py, PyArray2<f64>>> {
    let a = numpy2d_to_fdmatrix(data1)?;
    let b = numpy2d_to_fdmatrix(data2)?;
    let av = default_grid(argvals, a.ncols());
    let (n1, n2) = (a.nrows(), b.nrows());
    // Build column-major (element (i, j) at index i + j * n1) for FdMatrix.
    let mut col_major = vec![0.0; n1 * n2];
    for j in 0..n2 {
        let rj = b.row(j);
        for i in 0..n1 {
            col_major[i + j * n1] = fdars_core::utility::inner_product(&a.row(i), &rj, &av);
        }
    }
    let out = fdars_core::FdMatrix::from_column_major(col_major, n1, n2).map_err(to_pyerr)?;
    Ok(fdmatrix_to_numpy2d(py, &out))
}

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(int_simpson, m)?)?;
    m.add_function(wrap_pyfunction!(inprod, m)?)?;
    m.add_function(wrap_pyfunction!(lp_self_1d, m)?)?;
    m.add_function(wrap_pyfunction!(lp_cross_1d, m)?)?;
    m.add_function(wrap_pyfunction!(lp_self_2d, m)?)?;
    m.add_function(wrap_pyfunction!(lp_cross_2d, m)?)?;
    m.add_function(wrap_pyfunction!(hausdorff_self_1d, m)?)?;
    m.add_function(wrap_pyfunction!(hausdorff_cross_1d, m)?)?;
    m.add_function(wrap_pyfunction!(hausdorff_self_2d, m)?)?;
    m.add_function(wrap_pyfunction!(hausdorff_cross_2d, m)?)?;
    m.add_function(wrap_pyfunction!(dtw_self_1d, m)?)?;
    m.add_function(wrap_pyfunction!(dtw_cross_1d, m)?)?;
    m.add_function(wrap_pyfunction!(soft_dtw_self_1d, m)?)?;
    m.add_function(wrap_pyfunction!(soft_dtw_cross_1d, m)?)?;
    m.add_function(wrap_pyfunction!(soft_dtw_div_self_1d, m)?)?;
    m.add_function(wrap_pyfunction!(soft_dtw_div_cross_1d, m)?)?;
    m.add_function(wrap_pyfunction!(fourier_self_1d, m)?)?;
    m.add_function(wrap_pyfunction!(fourier_cross_1d, m)?)?;
    m.add_function(wrap_pyfunction!(hshift_self_1d, m)?)?;
    m.add_function(wrap_pyfunction!(hshift_cross_1d, m)?)?;
    // GAK (Global Alignment Kernel) — SHAPE-02
    m.add_class::<PyGakGramTrain>()?;
    m.add_function(wrap_pyfunction!(gak, m)?)?;
    m.add_function(wrap_pyfunction!(sigma_gak, m)?)?;
    m.add_function(wrap_pyfunction!(gak_gram_matrix, m)?)?;
    m.add_function(wrap_pyfunction!(gak_gram_train, m)?)?;
    m.add_function(wrap_pyfunction!(gak_gram_predict, m)?)?;
    Ok(())
}
