//! Elastic alignment and shape analysis for functional data.

use crate::convert::*;
use numpy::{PyArray1, PyArray2, PyReadonlyArray1, PyReadonlyArray2};
use pyo3::prelude::*;

/// Pairwise elastic alignment of two curves.
///
/// Parameters
/// ----------
/// curve1 : numpy.ndarray
///     First curve, 1D array of length m.
/// curve2 : numpy.ndarray
///     Second curve, 1D array of length m.
/// argvals : numpy.ndarray
///     Evaluation points, length m.
/// lambda_ : float, optional
///     Regularization parameter (default 0.0).
///
/// Returns
/// -------
/// dict
///     f_aligned (m,), gamma (m,), distance.
#[pyfunction]
#[pyo3(signature = (curve1, curve2, argvals, lambda_=0.0))]
pub fn elastic_align_pair<'py>(
    py: Python<'py>,
    curve1: PyReadonlyArray1<'py, f64>,
    curve2: PyReadonlyArray1<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    lambda_: f64,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let c1 = numpy1d_to_vec(curve1);
    let c2 = numpy1d_to_vec(curve2);
    let av = numpy1d_to_vec(argvals);
    let result = fdars_core::alignment::elastic_align_pair(&c1, &c2, &av, lambda_);

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("f_aligned", vec_to_numpy1d(py, result.f_aligned))?;
    dict.set_item("gamma", vec_to_numpy1d(py, result.gamma))?;
    dict.set_item("distance", result.distance)?;
    Ok(dict)
}

/// Karcher (Frechet) mean under the elastic metric.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Data, shape (n, m).
/// argvals : numpy.ndarray
///     Evaluation points, length m.
/// lambda_ : float, optional
///     Regularization (default 0.0).
/// max_iter : int, optional
///     Maximum iterations (default 20).
/// tol : float, optional
///     Convergence tolerance (default 1e-4).
///
/// Returns
/// -------
/// dict
///     mean (m,), mean_srsf (m,), aligned_data (n, m), gammas (n, m),
///     n_iter, converged.
#[pyfunction]
#[pyo3(signature = (data, argvals, lambda_=0.0, max_iter=20, tol=1e-4))]
pub fn karcher_mean<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    lambda_: f64,
    max_iter: usize,
    tol: f64,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let result = fdars_core::alignment::karcher_mean(&mat, &av, max_iter, tol, lambda_);

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("mean", vec_to_numpy1d(py, result.mean))?;
    dict.set_item("mean_srsf", vec_to_numpy1d(py, result.mean_srsf))?;
    dict.set_item("aligned_data", fdmatrix_to_numpy2d(py, &result.aligned_data))?;
    dict.set_item("gammas", fdmatrix_to_numpy2d(py, &result.gammas))?;
    dict.set_item("n_iter", result.n_iter)?;
    dict.set_item("converged", result.converged)?;
    Ok(dict)
}

/// Karcher median under the elastic metric.
#[pyfunction]
#[pyo3(signature = (data, argvals, lambda_=0.0, max_iter=20, tol=1e-3))]
pub fn karcher_median<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    lambda_: f64,
    max_iter: usize,
    tol: f64,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let config = fdars_core::alignment::RobustKarcherConfig {
        max_iter,
        tol,
        lambda: lambda_,
        trim_fraction: 0.0,
    };
    let result = to_pyresult(fdars_core::alignment::karcher_median(&mat, &av, &config))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("mean", vec_to_numpy1d(py, result.mean))?;
    dict.set_item("mean_srsf", vec_to_numpy1d(py, result.mean_srsf))?;
    dict.set_item("aligned_data", fdmatrix_to_numpy2d(py, &result.aligned_data))?;
    dict.set_item("gammas", fdmatrix_to_numpy2d(py, &result.gammas))?;
    dict.set_item("weights", vec_to_numpy1d(py, result.weights))?;
    dict.set_item("n_iter", result.n_iter)?;
    dict.set_item("converged", result.converged)?;
    Ok(dict)
}

/// Robust Karcher mean (trimmed).
#[pyfunction]
#[pyo3(signature = (data, argvals, lambda_=0.0, max_iter=20, tol=1e-3, trim_fraction=0.1))]
pub fn robust_karcher_mean<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    lambda_: f64,
    max_iter: usize,
    tol: f64,
    trim_fraction: f64,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let config = fdars_core::alignment::RobustKarcherConfig {
        max_iter,
        tol,
        lambda: lambda_,
        trim_fraction,
    };
    let result = to_pyresult(fdars_core::alignment::robust_karcher_mean(&mat, &av, &config))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("mean", vec_to_numpy1d(py, result.mean))?;
    dict.set_item("mean_srsf", vec_to_numpy1d(py, result.mean_srsf))?;
    dict.set_item("aligned_data", fdmatrix_to_numpy2d(py, &result.aligned_data))?;
    dict.set_item("gammas", fdmatrix_to_numpy2d(py, &result.gammas))?;
    dict.set_item("weights", vec_to_numpy1d(py, result.weights))?;
    dict.set_item("n_iter", result.n_iter)?;
    dict.set_item("converged", result.converged)?;
    Ok(dict)
}

/// Elastic (Fisher-Rao) distance between two curves.
///
/// Parameters
/// ----------
/// curve1 : numpy.ndarray
///     First curve, length m.
/// curve2 : numpy.ndarray
///     Second curve, length m.
/// argvals : numpy.ndarray
///     Evaluation points, length m.
/// lambda_ : float, optional
///     Regularization (default 0.0).
///
/// Returns
/// -------
/// float
///     Elastic distance.
#[pyfunction]
#[pyo3(signature = (curve1, curve2, argvals, lambda_=0.0))]
pub fn elastic_distance(
    curve1: PyReadonlyArray1<'_, f64>,
    curve2: PyReadonlyArray1<'_, f64>,
    argvals: PyReadonlyArray1<'_, f64>,
    lambda_: f64,
) -> f64 {
    let c1 = numpy1d_to_vec(curve1);
    let c2 = numpy1d_to_vec(curve2);
    let av = numpy1d_to_vec(argvals);
    fdars_core::alignment::elastic_distance(&c1, &c2, &av, lambda_)
}

/// Elastic self distance matrix.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Data, shape (n, m).
/// argvals : numpy.ndarray
///     Evaluation points, length m.
/// lambda_ : float, optional
///     Regularization (default 0.0).
///
/// Returns
/// -------
/// numpy.ndarray
///     Distance matrix, shape (n, n).
#[pyfunction]
#[pyo3(signature = (data, argvals, lambda_=0.0))]
pub fn elastic_self_distance_matrix<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    lambda_: f64,
) -> PyResult<Bound<'py, PyArray2<f64>>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let result = fdars_core::alignment::elastic_self_distance_matrix(&mat, &av, lambda_);
    Ok(fdmatrix_to_numpy2d(py, &result))
}

/// Elastic cross distance matrix.
#[pyfunction]
#[pyo3(signature = (data1, data2, argvals, lambda_=0.0))]
pub fn elastic_cross_distance_matrix<'py>(
    py: Python<'py>,
    data1: PyReadonlyArray2<'py, f64>,
    data2: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    lambda_: f64,
) -> PyResult<Bound<'py, PyArray2<f64>>> {
    let m1 = numpy2d_to_fdmatrix(data1)?;
    let m2 = numpy2d_to_fdmatrix(data2)?;
    let av = numpy1d_to_vec(argvals);
    let result = fdars_core::alignment::elastic_cross_distance_matrix(&m1, &m2, &av, lambda_);
    Ok(fdmatrix_to_numpy2d(py, &result))
}

/// SRSF (Square Root Slope Function) transform.
///
/// Parameters
/// ----------
/// curve : numpy.ndarray
///     Curve values, length m.
/// argvals : numpy.ndarray
///     Evaluation points, length m.
///
/// Returns
/// -------
/// numpy.ndarray
///     SRSF values, length m.
#[pyfunction]
pub fn srsf_transform<'py>(
    py: Python<'py>,
    curve: PyReadonlyArray1<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
) -> PyResult<Bound<'py, PyArray1<f64>>> {
    let c = numpy1d_to_vec(curve);
    let av = numpy1d_to_vec(argvals);
    let m = c.len();
    // srsf_transform takes FdMatrix; wrap single curve as 1 x m matrix
    let mat = fdars_core::matrix::FdMatrix::from_slice(&c, 1, m)
        .map_err(to_pyerr)?;
    let result_mat = fdars_core::alignment::srsf_transform(&mat, &av);
    Ok(vec_to_numpy1d(py, result_mat.row(0)))
}

/// Inverse SRSF transform.
///
/// Parameters
/// ----------
/// srsf : numpy.ndarray
///     SRSF values, length m.
/// argvals : numpy.ndarray
///     Evaluation points, length m.
/// initial_value : float, optional
///     Starting value (default 0.0).
///
/// Returns
/// -------
/// numpy.ndarray
///     Reconstructed curve, length m.
#[pyfunction]
#[pyo3(signature = (srsf, argvals, initial_value=0.0))]
pub fn srsf_inverse<'py>(
    py: Python<'py>,
    srsf: PyReadonlyArray1<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    initial_value: f64,
) -> Bound<'py, PyArray1<f64>> {
    let s = numpy1d_to_vec(srsf);
    let av = numpy1d_to_vec(argvals);
    let result = fdars_core::alignment::srsf_inverse(&s, &av, initial_value);
    vec_to_numpy1d(py, result)
}

/// Compose two warping functions.
#[pyfunction]
pub fn compose_warps<'py>(
    py: Python<'py>,
    warp1: PyReadonlyArray1<'py, f64>,
    warp2: PyReadonlyArray1<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
) -> Bound<'py, PyArray1<f64>> {
    let w1 = numpy1d_to_vec(warp1);
    let w2 = numpy1d_to_vec(warp2);
    let av = numpy1d_to_vec(argvals);
    let result = fdars_core::alignment::compose_warps(&w1, &w2, &av);
    vec_to_numpy1d(py, result)
}

/// Invert a warping function.
#[pyfunction]
pub fn invert_warp<'py>(
    py: Python<'py>,
    warp: PyReadonlyArray1<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
) -> PyResult<Bound<'py, PyArray1<f64>>> {
    let w = numpy1d_to_vec(warp);
    let av = numpy1d_to_vec(argvals);
    let result = to_pyresult(fdars_core::alignment::invert_warp(&w, &av))?;
    Ok(vec_to_numpy1d(py, result))
}

/// Warp smoothness (bending energy).
#[pyfunction]
pub fn warp_smoothness(
    warp: PyReadonlyArray1<'_, f64>,
    argvals: PyReadonlyArray1<'_, f64>,
) -> f64 {
    let w = numpy1d_to_vec(warp);
    let av = numpy1d_to_vec(argvals);
    fdars_core::alignment::warp_smoothness(&w, &av)
}

/// Warp complexity (geodesic distance from identity).
#[pyfunction]
pub fn warp_complexity(
    warp: PyReadonlyArray1<'_, f64>,
    argvals: PyReadonlyArray1<'_, f64>,
) -> f64 {
    let w = numpy1d_to_vec(warp);
    let av = numpy1d_to_vec(argvals);
    fdars_core::alignment::warp_complexity(&w, &av)
}

/// Amplitude distance between two curves.
#[pyfunction]
#[pyo3(signature = (curve1, curve2, argvals, lambda_=0.0))]
pub fn amplitude_distance(
    curve1: PyReadonlyArray1<'_, f64>,
    curve2: PyReadonlyArray1<'_, f64>,
    argvals: PyReadonlyArray1<'_, f64>,
    lambda_: f64,
) -> f64 {
    let c1 = numpy1d_to_vec(curve1);
    let c2 = numpy1d_to_vec(curve2);
    let av = numpy1d_to_vec(argvals);
    fdars_core::alignment::amplitude_distance(&c1, &c2, &av, lambda_)
}

/// Phase distance between two curves.
#[pyfunction]
#[pyo3(signature = (curve1, curve2, argvals, lambda_=0.0))]
pub fn phase_distance(
    curve1: PyReadonlyArray1<'_, f64>,
    curve2: PyReadonlyArray1<'_, f64>,
    argvals: PyReadonlyArray1<'_, f64>,
    lambda_: f64,
) -> f64 {
    let c1 = numpy1d_to_vec(curve1);
    let c2 = numpy1d_to_vec(curve2);
    let av = numpy1d_to_vec(argvals);
    fdars_core::alignment::phase_distance_pair(&c1, &c2, &av, lambda_)
}

/// Elastic depth (depth under elastic metric).
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Data, shape (n, m).
/// argvals : numpy.ndarray
///     Evaluation points, length m.
/// lambda_ : float, optional
///     Regularization (default 0.0).
///
/// Returns
/// -------
/// dict
///     amplitude_depth (n,), phase_depth (n,), combined_depth (n,),
///     amplitude_distances (n, n), phase_distances (n, n).
#[pyfunction]
#[pyo3(signature = (data, argvals, lambda_=0.0))]
pub fn elastic_depth<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    lambda_: f64,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let result = to_pyresult(fdars_core::alignment::elastic_depth(&mat, &av, lambda_))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("amplitude_depth", vec_to_numpy1d(py, result.amplitude_depth))?;
    dict.set_item("phase_depth", vec_to_numpy1d(py, result.phase_depth))?;
    dict.set_item("combined_depth", vec_to_numpy1d(py, result.combined_depth))?;
    dict.set_item("amplitude_distances", fdmatrix_to_numpy2d(py, &result.amplitude_distances))?;
    dict.set_item("phase_distances", fdmatrix_to_numpy2d(py, &result.phase_distances))?;
    Ok(dict)
}

/// Shape distance (quotient space distance).
#[pyfunction]
#[pyo3(signature = (curve1, curve2, argvals, lambda_=0.0))]
pub fn shape_distance<'py>(
    py: Python<'py>,
    curve1: PyReadonlyArray1<'py, f64>,
    curve2: PyReadonlyArray1<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    lambda_: f64,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let c1 = numpy1d_to_vec(curve1);
    let c2 = numpy1d_to_vec(curve2);
    let av = numpy1d_to_vec(argvals);
    let result = to_pyresult(fdars_core::alignment::shape_distance(
        &c1,
        &c2,
        &av,
        fdars_core::alignment::ShapeQuotient::default(),
        lambda_,
    ))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("distance", result.distance)?;
    dict.set_item("gamma", vec_to_numpy1d(py, result.gamma))?;
    dict.set_item("f2_aligned", vec_to_numpy1d(py, result.f2_aligned))?;
    Ok(dict)
}

/// Vertical (amplitude) FPCA on aligned data.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Data, shape (n, m).
/// argvals : numpy.ndarray
///     Evaluation points, length m.
/// n_comp : int, optional
///     Number of components (default 3).
/// lambda_ : float, optional
///     Regularization (default 0.0).
/// max_iter : int, optional
///     Maximum Karcher mean iterations (default 20).
/// tol : float, optional
///     Convergence tolerance (default 1e-4).
///
/// Returns
/// -------
/// dict
///     scores (n, n_comp), eigenfunctions_q (n_comp, m+1),
///     eigenfunctions_f (n_comp, m), eigenvalues (n_comp,),
///     cumulative_variance (n_comp,), mean_q (m+1,).
#[pyfunction]
#[pyo3(signature = (data, argvals, n_comp=3, lambda_=0.0, max_iter=20, tol=1e-4))]
pub fn vert_fpca<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    n_comp: usize,
    lambda_: f64,
    max_iter: usize,
    tol: f64,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    // First compute Karcher mean, then run vert_fpca on the result
    let karcher = fdars_core::alignment::karcher_mean(&mat, &av, max_iter, tol, lambda_);
    let result = to_pyresult(fdars_core::elastic_fpca::vert_fpca(&karcher, &av, n_comp))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("scores", fdmatrix_to_numpy2d(py, &result.scores))?;
    dict.set_item("eigenfunctions_q", fdmatrix_to_numpy2d(py, &result.eigenfunctions_q))?;
    dict.set_item("eigenfunctions_f", fdmatrix_to_numpy2d(py, &result.eigenfunctions_f))?;
    dict.set_item("eigenvalues", vec_to_numpy1d(py, result.eigenvalues))?;
    dict.set_item("cumulative_variance", vec_to_numpy1d(py, result.cumulative_variance))?;
    dict.set_item("mean_q", vec_to_numpy1d(py, result.mean_q))?;
    Ok(dict)
}

/// Horizontal (phase) FPCA.
#[pyfunction]
#[pyo3(signature = (data, argvals, n_comp=3, lambda_=0.0, max_iter=20, tol=1e-4))]
pub fn horiz_fpca<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    n_comp: usize,
    lambda_: f64,
    max_iter: usize,
    tol: f64,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let karcher = fdars_core::alignment::karcher_mean(&mat, &av, max_iter, tol, lambda_);
    let result = to_pyresult(fdars_core::elastic_fpca::horiz_fpca(&karcher, &av, n_comp))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("scores", fdmatrix_to_numpy2d(py, &result.scores))?;
    dict.set_item("eigenfunctions_psi", fdmatrix_to_numpy2d(py, &result.eigenfunctions_psi))?;
    dict.set_item("eigenfunctions_gam", fdmatrix_to_numpy2d(py, &result.eigenfunctions_gam))?;
    dict.set_item("eigenvalues", vec_to_numpy1d(py, result.eigenvalues))?;
    dict.set_item("cumulative_variance", vec_to_numpy1d(py, result.cumulative_variance))?;
    dict.set_item("mean_psi", vec_to_numpy1d(py, result.mean_psi))?;
    dict.set_item("shooting_vectors", fdmatrix_to_numpy2d(py, &result.shooting_vectors))?;
    Ok(dict)
}

/// Joint (amplitude + phase) FPCA.
#[pyfunction]
#[pyo3(signature = (data, argvals, n_comp=3, lambda_=0.0, max_iter=20, tol=1e-4))]
pub fn joint_fpca<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    n_comp: usize,
    lambda_: f64,
    max_iter: usize,
    tol: f64,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let karcher = fdars_core::alignment::karcher_mean(&mat, &av, max_iter, tol, lambda_);
    let result = to_pyresult(fdars_core::elastic_fpca::joint_fpca(
        &karcher, &av, n_comp, None,
    ))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("scores", fdmatrix_to_numpy2d(py, &result.scores))?;
    dict.set_item("eigenvalues", vec_to_numpy1d(py, result.eigenvalues))?;
    dict.set_item("cumulative_variance", vec_to_numpy1d(py, result.cumulative_variance))?;
    dict.set_item("balance_c", result.balance_c)?;
    dict.set_item("vert_component", fdmatrix_to_numpy2d(py, &result.vert_component))?;
    dict.set_item("horiz_component", fdmatrix_to_numpy2d(py, &result.horiz_component))?;
    Ok(dict)
}

/// Elastic scalar-on-function regression.
#[pyfunction]
#[pyo3(signature = (data, argvals, response, ncomp_beta=10, lambda_=0.0, max_iter=20, tol=1e-4))]
pub fn elastic_regression<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    response: PyReadonlyArray1<'py, f64>,
    ncomp_beta: usize,
    lambda_: f64,
    max_iter: usize,
    tol: f64,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let resp = numpy1d_to_vec(response);
    let result = to_pyresult(fdars_core::elastic_regression::elastic_regression(
        &mat, &resp, &av, ncomp_beta, lambda_, max_iter, tol,
    ))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("alpha", result.alpha)?;
    dict.set_item("beta", vec_to_numpy1d(py, result.beta))?;
    dict.set_item("fitted_values", vec_to_numpy1d(py, result.fitted_values))?;
    dict.set_item("residuals", vec_to_numpy1d(py, result.residuals))?;
    dict.set_item("sse", result.sse)?;
    dict.set_item("r_squared", result.r_squared)?;
    dict.set_item("gammas", fdmatrix_to_numpy2d(py, &result.gammas))?;
    dict.set_item("n_iter", result.n_iter)?;
    Ok(dict)
}

/// Elastic logistic regression.
#[pyfunction]
#[pyo3(signature = (data, argvals, labels, ncomp_beta=10, lambda_=0.0, max_iter=20, tol=1e-4))]
pub fn elastic_logistic<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    labels: PyReadonlyArray1<'py, i64>,
    ncomp_beta: usize,
    lambda_: f64,
    max_iter: usize,
    tol: f64,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    // Convert i64 labels to i8 (elastic_logistic expects &[i8])
    let lab: Vec<i8> = labels.as_array().iter().map(|&x| x as i8).collect();
    let result = to_pyresult(fdars_core::elastic_regression::elastic_logistic(
        &mat, &lab, &av, ncomp_beta, lambda_, max_iter, tol,
    ))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("alpha", result.alpha)?;
    dict.set_item("beta", vec_to_numpy1d(py, result.beta))?;
    dict.set_item("probabilities", vec_to_numpy1d(py, result.probabilities))?;
    dict.set_item("predicted_classes", usize_vec_to_numpy1d(py, result.predicted_classes))?;
    dict.set_item("accuracy", result.accuracy)?;
    dict.set_item("loss", result.loss)?;
    dict.set_item("gammas", fdmatrix_to_numpy2d(py, &result.gammas))?;
    dict.set_item("n_iter", result.n_iter)?;
    Ok(dict)
}

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(elastic_align_pair, m)?)?;
    m.add_function(wrap_pyfunction!(karcher_mean, m)?)?;
    m.add_function(wrap_pyfunction!(karcher_median, m)?)?;
    m.add_function(wrap_pyfunction!(robust_karcher_mean, m)?)?;
    m.add_function(wrap_pyfunction!(elastic_distance, m)?)?;
    m.add_function(wrap_pyfunction!(elastic_self_distance_matrix, m)?)?;
    m.add_function(wrap_pyfunction!(elastic_cross_distance_matrix, m)?)?;
    m.add_function(wrap_pyfunction!(srsf_transform, m)?)?;
    m.add_function(wrap_pyfunction!(srsf_inverse, m)?)?;
    m.add_function(wrap_pyfunction!(compose_warps, m)?)?;
    m.add_function(wrap_pyfunction!(invert_warp, m)?)?;
    m.add_function(wrap_pyfunction!(warp_smoothness, m)?)?;
    m.add_function(wrap_pyfunction!(warp_complexity, m)?)?;
    m.add_function(wrap_pyfunction!(amplitude_distance, m)?)?;
    m.add_function(wrap_pyfunction!(phase_distance, m)?)?;
    m.add_function(wrap_pyfunction!(elastic_depth, m)?)?;
    m.add_function(wrap_pyfunction!(shape_distance, m)?)?;
    m.add_function(wrap_pyfunction!(vert_fpca, m)?)?;
    m.add_function(wrap_pyfunction!(horiz_fpca, m)?)?;
    m.add_function(wrap_pyfunction!(joint_fpca, m)?)?;
    m.add_function(wrap_pyfunction!(elastic_regression, m)?)?;
    m.add_function(wrap_pyfunction!(elastic_logistic, m)?)?;
    Ok(())
}
