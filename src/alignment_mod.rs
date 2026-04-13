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
    dict.set_item(
        "aligned_data",
        fdmatrix_to_numpy2d(py, &result.aligned_data),
    )?;
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
    dict.set_item(
        "aligned_data",
        fdmatrix_to_numpy2d(py, &result.aligned_data),
    )?;
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
    let result = to_pyresult(fdars_core::alignment::robust_karcher_mean(
        &mat, &av, &config,
    ))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("mean", vec_to_numpy1d(py, result.mean))?;
    dict.set_item("mean_srsf", vec_to_numpy1d(py, result.mean_srsf))?;
    dict.set_item(
        "aligned_data",
        fdmatrix_to_numpy2d(py, &result.aligned_data),
    )?;
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
    let mat = fdars_core::matrix::FdMatrix::from_slice(&c, 1, m).map_err(to_pyerr)?;
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
pub fn warp_smoothness(warp: PyReadonlyArray1<'_, f64>, argvals: PyReadonlyArray1<'_, f64>) -> f64 {
    let w = numpy1d_to_vec(warp);
    let av = numpy1d_to_vec(argvals);
    fdars_core::alignment::warp_smoothness(&w, &av)
}

/// Warp complexity (geodesic distance from identity).
#[pyfunction]
pub fn warp_complexity(warp: PyReadonlyArray1<'_, f64>, argvals: PyReadonlyArray1<'_, f64>) -> f64 {
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
    dict.set_item(
        "amplitude_depth",
        vec_to_numpy1d(py, result.amplitude_depth),
    )?;
    dict.set_item("phase_depth", vec_to_numpy1d(py, result.phase_depth))?;
    dict.set_item("combined_depth", vec_to_numpy1d(py, result.combined_depth))?;
    dict.set_item(
        "amplitude_distances",
        fdmatrix_to_numpy2d(py, &result.amplitude_distances),
    )?;
    dict.set_item(
        "phase_distances",
        fdmatrix_to_numpy2d(py, &result.phase_distances),
    )?;
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
    dict.set_item(
        "eigenfunctions_q",
        fdmatrix_to_numpy2d(py, &result.eigenfunctions_q),
    )?;
    dict.set_item(
        "eigenfunctions_f",
        fdmatrix_to_numpy2d(py, &result.eigenfunctions_f),
    )?;
    dict.set_item("eigenvalues", vec_to_numpy1d(py, result.eigenvalues))?;
    dict.set_item(
        "cumulative_variance",
        vec_to_numpy1d(py, result.cumulative_variance),
    )?;
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
    dict.set_item(
        "eigenfunctions_psi",
        fdmatrix_to_numpy2d(py, &result.eigenfunctions_psi),
    )?;
    dict.set_item(
        "eigenfunctions_gam",
        fdmatrix_to_numpy2d(py, &result.eigenfunctions_gam),
    )?;
    dict.set_item("eigenvalues", vec_to_numpy1d(py, result.eigenvalues))?;
    dict.set_item(
        "cumulative_variance",
        vec_to_numpy1d(py, result.cumulative_variance),
    )?;
    dict.set_item("mean_psi", vec_to_numpy1d(py, result.mean_psi))?;
    dict.set_item(
        "shooting_vectors",
        fdmatrix_to_numpy2d(py, &result.shooting_vectors),
    )?;
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
    dict.set_item(
        "cumulative_variance",
        vec_to_numpy1d(py, result.cumulative_variance),
    )?;
    dict.set_item("balance_c", result.balance_c)?;
    dict.set_item(
        "vert_component",
        fdmatrix_to_numpy2d(py, &result.vert_component),
    )?;
    dict.set_item(
        "horiz_component",
        fdmatrix_to_numpy2d(py, &result.horiz_component),
    )?;
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
    dict.set_item(
        "predicted_classes",
        usize_vec_to_numpy1d(py, result.predicted_classes),
    )?;
    dict.set_item("accuracy", result.accuracy)?;
    dict.set_item("loss", result.loss)?;
    dict.set_item("gammas", fdmatrix_to_numpy2d(py, &result.gammas))?;
    dict.set_item("n_iter", result.n_iter)?;
    Ok(dict)
}

// ─── Penalized alignment ────────────────────────────────────────────────────

/// Elastic alignment with configurable penalty type.
///
/// Parameters
/// ----------
/// curve1 : numpy.ndarray
///     Target curve, length m.
/// curve2 : numpy.ndarray
///     Curve to align, length m.
/// argvals : numpy.ndarray
///     Evaluation points, length m.
/// lambda_ : float, optional
///     First-order penalty weight (default 0.0).
/// penalty_type : str, optional
///     "first_order" (default), "second_order", or "combined".
/// second_order_weight : float, optional
///     Weight for combined penalty (default 0.1).
///
/// Returns
/// -------
/// dict
///     f_aligned (m,), gamma (m,), distance.
#[pyfunction]
#[pyo3(signature = (curve1, curve2, argvals, lambda_=0.0, penalty_type="first_order", second_order_weight=0.1))]
pub fn elastic_align_pair_penalized<'py>(
    py: Python<'py>,
    curve1: PyReadonlyArray1<'py, f64>,
    curve2: PyReadonlyArray1<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    lambda_: f64,
    penalty_type: &str,
    second_order_weight: f64,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let c1 = numpy1d_to_vec(curve1);
    let c2 = numpy1d_to_vec(curve2);
    let av = numpy1d_to_vec(argvals);
    let pt = match penalty_type {
        "second_order" => fdars_core::alignment::WarpPenaltyType::SecondOrder,
        "combined" => fdars_core::alignment::WarpPenaltyType::Combined {
            second_order_weight,
        },
        _ => fdars_core::alignment::WarpPenaltyType::FirstOrder,
    };
    let result = fdars_core::alignment::elastic_align_pair_penalized(&c1, &c2, &av, lambda_, pt);

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("f_aligned", vec_to_numpy1d(py, result.f_aligned))?;
    dict.set_item("gamma", vec_to_numpy1d(py, result.gamma))?;
    dict.set_item("distance", result.distance)?;
    Ok(dict)
}

// ─── Bayesian alignment ─────────────────────────────────────────────────────

/// Bayesian pairwise alignment via pCN MCMC on the Hilbert sphere.
///
/// Parameters
/// ----------
/// f1 : numpy.ndarray
///     Target curve, length m.
/// f2 : numpy.ndarray
///     Curve to align, length m.
/// argvals : numpy.ndarray
///     Evaluation points, length m.
/// n_samples : int, optional
///     Number of posterior samples (default 1000).
/// burn_in : int, optional
///     Number of burn-in iterations (default 200).
/// step_size : float, optional
///     pCN step size in (0, 1) (default 0.1).
/// proposal_variance : float, optional
///     Variance scaling for proposals (default 1.0).
/// seed : int, optional
///     RNG seed (default 42).
///
/// Returns
/// -------
/// dict
///     posterior_gammas (n_samples, m), posterior_mean_gamma (m,),
///     credible_lower (m,), credible_upper (m,), acceptance_rate, f_aligned_mean (m,).
#[pyfunction]
#[pyo3(signature = (f1, f2, argvals, n_samples=1000, burn_in=200, step_size=0.1, proposal_variance=1.0, seed=42))]
pub fn bayesian_align_pair<'py>(
    py: Python<'py>,
    f1: PyReadonlyArray1<'py, f64>,
    f2: PyReadonlyArray1<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    n_samples: usize,
    burn_in: usize,
    step_size: f64,
    proposal_variance: f64,
    seed: u64,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let c1 = numpy1d_to_vec(f1);
    let c2 = numpy1d_to_vec(f2);
    let av = numpy1d_to_vec(argvals);
    let config = fdars_core::alignment::BayesianAlignConfig {
        n_samples,
        burn_in,
        step_size,
        proposal_variance,
        seed,
    };
    let result = to_pyresult(fdars_core::alignment::bayesian_align_pair(
        &c1, &c2, &av, &config,
    ))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item(
        "posterior_gammas",
        fdmatrix_to_numpy2d(py, &result.posterior_gammas),
    )?;
    dict.set_item(
        "posterior_mean_gamma",
        vec_to_numpy1d(py, result.posterior_mean_gamma),
    )?;
    dict.set_item("credible_lower", vec_to_numpy1d(py, result.credible_lower))?;
    dict.set_item("credible_upper", vec_to_numpy1d(py, result.credible_upper))?;
    dict.set_item("acceptance_rate", result.acceptance_rate)?;
    dict.set_item("f_aligned_mean", vec_to_numpy1d(py, result.f_aligned_mean))?;
    Ok(dict)
}

// ─── Closed curve alignment ─────────────────────────────────────────────────

/// Align closed (periodic) curve f2 to f1 with rotation search.
#[pyfunction]
#[pyo3(signature = (f1, f2, argvals, lambda_=0.0))]
pub fn elastic_align_pair_closed<'py>(
    py: Python<'py>,
    f1: PyReadonlyArray1<'py, f64>,
    f2: PyReadonlyArray1<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    lambda_: f64,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let c1 = numpy1d_to_vec(f1);
    let c2 = numpy1d_to_vec(f2);
    let av = numpy1d_to_vec(argvals);
    let result = to_pyresult(fdars_core::alignment::elastic_align_pair_closed(
        &c1, &c2, &av, lambda_,
    ))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("f_aligned", vec_to_numpy1d(py, result.f_aligned))?;
    dict.set_item("gamma", vec_to_numpy1d(py, result.gamma))?;
    dict.set_item("distance", result.distance)?;
    dict.set_item("optimal_rotation", result.optimal_rotation)?;
    Ok(dict)
}

/// Elastic distance between two closed curves.
#[pyfunction]
#[pyo3(signature = (f1, f2, argvals, lambda_=0.0))]
pub fn elastic_distance_closed(
    f1: PyReadonlyArray1<'_, f64>,
    f2: PyReadonlyArray1<'_, f64>,
    argvals: PyReadonlyArray1<'_, f64>,
    lambda_: f64,
) -> PyResult<f64> {
    let c1 = numpy1d_to_vec(f1);
    let c2 = numpy1d_to_vec(f2);
    let av = numpy1d_to_vec(argvals);
    to_pyresult(fdars_core::alignment::elastic_distance_closed(
        &c1, &c2, &av, lambda_,
    ))
}

/// Karcher mean for closed (periodic) curves.
#[pyfunction]
#[pyo3(signature = (data, argvals, max_iter=20, tol=1e-4, lambda_=0.0))]
pub fn karcher_mean_closed<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    max_iter: usize,
    tol: f64,
    lambda_: f64,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let result = to_pyresult(fdars_core::alignment::karcher_mean_closed(
        &mat, &av, max_iter, tol, lambda_,
    ))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("mean", vec_to_numpy1d(py, result.mean))?;
    dict.set_item("mean_srsf", vec_to_numpy1d(py, result.mean_srsf))?;
    dict.set_item(
        "aligned_data",
        fdmatrix_to_numpy2d(py, &result.aligned_data),
    )?;
    dict.set_item("gammas", fdmatrix_to_numpy2d(py, &result.gammas))?;
    dict.set_item("rotations", usize_vec_to_numpy1d(py, result.rotations))?;
    dict.set_item("n_iter", result.n_iter)?;
    dict.set_item("converged", result.converged)?;
    Ok(dict)
}

// ─── Constrained alignment ──────────────────────────────────────────────────

/// Landmark-constrained elastic alignment.
#[pyfunction]
#[pyo3(signature = (f1, f2, argvals, landmark_targets, landmark_sources, lambda_=0.0))]
pub fn elastic_align_pair_constrained<'py>(
    py: Python<'py>,
    f1: PyReadonlyArray1<'py, f64>,
    f2: PyReadonlyArray1<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    landmark_targets: PyReadonlyArray1<'py, f64>,
    landmark_sources: PyReadonlyArray1<'py, f64>,
    lambda_: f64,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let c1 = numpy1d_to_vec(f1);
    let c2 = numpy1d_to_vec(f2);
    let av = numpy1d_to_vec(argvals);
    let lt = numpy1d_to_vec(landmark_targets);
    let ls = numpy1d_to_vec(landmark_sources);
    let pairs: Vec<(f64, f64)> = lt.into_iter().zip(ls).collect();
    let result =
        fdars_core::alignment::elastic_align_pair_constrained(&c1, &c2, &av, &pairs, lambda_);

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("f_aligned", vec_to_numpy1d(py, result.f_aligned))?;
    dict.set_item("gamma", vec_to_numpy1d(py, result.gamma))?;
    dict.set_item("distance", result.distance)?;
    Ok(dict)
}

// ─── Clustering ─────────────────────────────────────────────────────────────

/// K-medoids clustering from a precomputed distance matrix.
#[pyfunction]
#[pyo3(signature = (dist_mat, k=2, max_iter=100, seed=42))]
pub fn kmedoids_from_distances<'py>(
    py: Python<'py>,
    dist_mat: PyReadonlyArray2<'py, f64>,
    k: usize,
    max_iter: usize,
    seed: u64,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(dist_mat)?;
    let config = fdars_core::alignment::KMedoidsConfig { k, max_iter, seed };
    let result = to_pyresult(fdars_core::alignment::kmedoids_from_distances(
        &mat, &config,
    ))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("labels", usize_vec_to_numpy1d(py, result.labels))?;
    dict.set_item(
        "medoid_indices",
        usize_vec_to_numpy1d(py, result.medoid_indices),
    )?;
    dict.set_item(
        "within_distances",
        vec_to_numpy1d(py, result.within_distances),
    )?;
    dict.set_item("total_within_distance", result.total_within_distance)?;
    dict.set_item("n_iter", result.n_iter)?;
    dict.set_item("converged", result.converged)?;
    Ok(dict)
}

/// Hierarchical agglomerative clustering from a precomputed distance matrix.
#[pyfunction]
#[pyo3(signature = (dist_mat, linkage="single"))]
pub fn hierarchical_from_distances<'py>(
    py: Python<'py>,
    dist_mat: PyReadonlyArray2<'py, f64>,
    linkage: &str,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(dist_mat)?;
    let link = match linkage {
        "complete" => fdars_core::alignment::Linkage::Complete,
        "average" => fdars_core::alignment::Linkage::Average,
        _ => fdars_core::alignment::Linkage::Single,
    };
    let result = to_pyresult(fdars_core::alignment::hierarchical_from_distances(
        &mat, link,
    ))?;

    let dict = pyo3::types::PyDict::new(py);
    // merges: list of (i, j, distance) tuples
    let merges_list = pyo3::types::PyList::empty(py);
    for (i, j, d) in &result.merges {
        let tuple = pyo3::types::PyTuple::new(py, [*i as f64, *j as f64, *d]).unwrap();
        merges_list.append(tuple)?;
    }
    dict.set_item("merges", merges_list)?;
    dict.set_item("n", result.n)?;
    Ok(dict)
}

/// Hierarchical clustering then cut to produce k clusters (convenience function).
#[pyfunction]
#[pyo3(signature = (dist_mat, k=2, linkage="single"))]
pub fn hierarchical_cut<'py>(
    py: Python<'py>,
    dist_mat: PyReadonlyArray2<'py, f64>,
    k: usize,
    linkage: &str,
) -> PyResult<Bound<'py, PyArray1<i64>>> {
    let mat = numpy2d_to_fdmatrix(dist_mat)?;
    let link = match linkage {
        "complete" => fdars_core::alignment::Linkage::Complete,
        "average" => fdars_core::alignment::Linkage::Average,
        _ => fdars_core::alignment::Linkage::Single,
    };
    let dendro = to_pyresult(fdars_core::alignment::hierarchical_from_distances(
        &mat, link,
    ))?;
    let labels = to_pyresult(fdars_core::alignment::cut_dendrogram(&dendro, k))?;
    Ok(usize_vec_to_numpy1d(py, labels))
}

// ─── Multi-resolution alignment ─────────────────────────────────────────────

/// Multi-resolution elastic alignment (coarse DP + gradient refinement).
#[pyfunction]
#[pyo3(signature = (f1, f2, argvals, coarsen_factor=4, n_refine_steps=10, step_size=0.01, lambda_=0.0))]
pub fn elastic_align_pair_multires<'py>(
    py: Python<'py>,
    f1: PyReadonlyArray1<'py, f64>,
    f2: PyReadonlyArray1<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    coarsen_factor: usize,
    n_refine_steps: usize,
    step_size: f64,
    lambda_: f64,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let c1 = numpy1d_to_vec(f1);
    let c2 = numpy1d_to_vec(f2);
    let av = numpy1d_to_vec(argvals);
    let config = fdars_core::alignment::MultiresConfig {
        coarsen_factor,
        n_refine_steps,
        step_size,
        lambda: lambda_,
    };
    let result = to_pyresult(fdars_core::alignment::elastic_align_pair_multires(
        &c1, &c2, &av, &config,
    ))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("f_aligned", vec_to_numpy1d(py, result.f_aligned))?;
    dict.set_item("gamma", vec_to_numpy1d(py, result.gamma))?;
    dict.set_item("distance", result.distance)?;
    Ok(dict)
}

// ─── Set alignment / decomposition ──────────────────────────────────────────

/// Align all curves to a single target curve.
#[pyfunction]
#[pyo3(signature = (data, target, argvals, lambda_=0.0))]
pub fn align_to_target<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    target: PyReadonlyArray1<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    lambda_: f64,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let tgt = numpy1d_to_vec(target);
    let av = numpy1d_to_vec(argvals);
    let result = fdars_core::alignment::align_to_target(&mat, &tgt, &av, lambda_);

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item(
        "aligned_data",
        fdmatrix_to_numpy2d(py, &result.aligned_data),
    )?;
    dict.set_item("gammas", fdmatrix_to_numpy2d(py, &result.gammas))?;
    dict.set_item("distances", vec_to_numpy1d(py, result.distances))?;
    Ok(dict)
}

/// Elastic phase-amplitude decomposition of two curves.
#[pyfunction]
#[pyo3(signature = (f1, f2, argvals, lambda_=0.0))]
pub fn elastic_decomposition<'py>(
    py: Python<'py>,
    f1: PyReadonlyArray1<'py, f64>,
    f2: PyReadonlyArray1<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    lambda_: f64,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let c1 = numpy1d_to_vec(f1);
    let c2 = numpy1d_to_vec(f2);
    let av = numpy1d_to_vec(argvals);
    let result = fdars_core::alignment::elastic_decomposition(&c1, &c2, &av, lambda_);

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("f_aligned", vec_to_numpy1d(py, result.alignment.f_aligned))?;
    dict.set_item("gamma", vec_to_numpy1d(py, result.alignment.gamma))?;
    dict.set_item("distance", result.alignment.distance)?;
    dict.set_item("d_amplitude", result.d_amplitude)?;
    dict.set_item("d_phase", result.d_phase)?;
    Ok(dict)
}

// ─── Distance matrices ──────────────────────────────────────────────────────

/// Amplitude self distance matrix (same as elastic self distance matrix).
#[pyfunction]
#[pyo3(signature = (data, argvals, lambda_=0.0))]
pub fn amplitude_self_distance_matrix<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    lambda_: f64,
) -> PyResult<Bound<'py, PyArray2<f64>>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let result = fdars_core::alignment::amplitude_self_distance_matrix(&mat, &av, lambda_);
    Ok(fdmatrix_to_numpy2d(py, &result))
}

/// Phase self distance matrix.
#[pyfunction]
#[pyo3(signature = (data, argvals, lambda_=0.0))]
pub fn phase_self_distance_matrix<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    lambda_: f64,
) -> PyResult<Bound<'py, PyArray2<f64>>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let result = fdars_core::alignment::phase_self_distance_matrix(&mat, &av, lambda_);
    Ok(fdmatrix_to_numpy2d(py, &result))
}

// ─── Diagnostics ────────────────────────────────────────────────────────────

/// Diagnose alignment quality for every curve after Karcher mean computation.
#[pyfunction]
#[pyo3(signature = (data, argvals, lambda_=0.0, max_iter=20, tol=1e-4, over_alignment_threshold=1.0, under_alignment_threshold=1e-6, max_bending_energy=100.0, min_improvement_ratio=0.5))]
pub fn diagnose_alignment<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    lambda_: f64,
    max_iter: usize,
    tol: f64,
    over_alignment_threshold: f64,
    under_alignment_threshold: f64,
    max_bending_energy: f64,
    min_improvement_ratio: f64,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let karcher = fdars_core::alignment::karcher_mean(&mat, &av, max_iter, tol, lambda_);
    let config = fdars_core::alignment::DiagnosticConfig {
        over_alignment_threshold,
        under_alignment_threshold,
        max_bending_energy,
        min_improvement_ratio,
    };
    let result = to_pyresult(fdars_core::alignment::diagnose_alignment(
        &mat, &karcher, &av, &config,
    ))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item(
        "flagged_indices",
        usize_vec_to_numpy1d(py, result.flagged_indices),
    )?;
    dict.set_item("n_flagged", result.n_flagged)?;
    dict.set_item("health_score", result.health_score)?;
    // Per-curve diagnostics as lists
    let wc: Vec<f64> = result
        .diagnostics
        .iter()
        .map(|d| d.warp_complexity)
        .collect();
    let ws: Vec<f64> = result
        .diagnostics
        .iter()
        .map(|d| d.warp_smoothness)
        .collect();
    let residuals: Vec<f64> = result.diagnostics.iter().map(|d| d.residual).collect();
    let flagged: Vec<bool> = result.diagnostics.iter().map(|d| d.flagged).collect();
    dict.set_item("warp_complexity", vec_to_numpy1d(py, wc))?;
    dict.set_item("warp_smoothness", vec_to_numpy1d(py, ws))?;
    dict.set_item("residuals", vec_to_numpy1d(py, residuals))?;
    dict.set_item("flagged", bool_vec_to_numpy1d(py, flagged))?;
    Ok(dict)
}

// ─── Generative models ──────────────────────────────────────────────────────

/// Generate random curves from a fitted Gaussian model on aligned data.
#[pyfunction]
#[pyo3(signature = (data, argvals, ncomp=3, n_samples=100, lambda_=0.0, max_iter=20, tol=1e-4, seed=42))]
pub fn gauss_model<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    ncomp: usize,
    n_samples: usize,
    lambda_: f64,
    max_iter: usize,
    tol: f64,
    seed: u64,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let karcher = fdars_core::alignment::karcher_mean(&mat, &av, max_iter, tol, lambda_);
    let result = to_pyresult(fdars_core::alignment::gauss_model(
        &karcher, &av, ncomp, n_samples, seed,
    ))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("samples", fdmatrix_to_numpy2d(py, &result.samples))?;
    dict.set_item("warps", fdmatrix_to_numpy2d(py, &result.warps))?;
    dict.set_item("scores", fdmatrix_to_numpy2d(py, &result.scores))?;
    Ok(dict)
}

/// Generate random curves from a joint Gaussian model preserving amplitude-phase correlation.
#[pyfunction]
#[pyo3(signature = (data, argvals, ncomp=3, n_samples=100, balance_c=1.0, lambda_=0.0, max_iter=20, tol=1e-4, seed=42))]
pub fn joint_gauss_model<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    ncomp: usize,
    n_samples: usize,
    balance_c: f64,
    lambda_: f64,
    max_iter: usize,
    tol: f64,
    seed: u64,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let karcher = fdars_core::alignment::karcher_mean(&mat, &av, max_iter, tol, lambda_);
    let result = to_pyresult(fdars_core::alignment::joint_gauss_model(
        &karcher, &av, ncomp, n_samples, balance_c, seed,
    ))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("samples", fdmatrix_to_numpy2d(py, &result.samples))?;
    dict.set_item("warps", fdmatrix_to_numpy2d(py, &result.warps))?;
    dict.set_item("scores", fdmatrix_to_numpy2d(py, &result.scores))?;
    Ok(dict)
}

// ─── Geodesic ───────────────────────────────────────────────────────────────

/// Compute the geodesic path between two 1-D curves in the elastic metric.
#[pyfunction]
#[pyo3(signature = (f1, f2, argvals, n_points=10, lambda_=0.0))]
pub fn curve_geodesic<'py>(
    py: Python<'py>,
    f1: PyReadonlyArray1<'py, f64>,
    f2: PyReadonlyArray1<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    n_points: usize,
    lambda_: f64,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let c1 = numpy1d_to_vec(f1);
    let c2 = numpy1d_to_vec(f2);
    let av = numpy1d_to_vec(argvals);
    let result = to_pyresult(fdars_core::alignment::curve_geodesic(
        &c1, &c2, &av, n_points, lambda_,
    ))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("curves", fdmatrix_to_numpy2d(py, &result.curves))?;
    dict.set_item("warps", fdmatrix_to_numpy2d(py, &result.warps))?;
    dict.set_item("distances", vec_to_numpy1d(py, result.distances))?;
    dict.set_item(
        "parameter_values",
        vec_to_numpy1d(py, result.parameter_values),
    )?;
    Ok(dict)
}

// ─── Lambda CV ──────────────────────────────────────────────────────────────

/// Cross-validation for the elastic alignment regularisation parameter lambda.
#[pyfunction]
#[pyo3(signature = (data, argvals, lambdas=None, n_folds=5, max_iter=15, tol=1e-3, seed=42))]
pub fn lambda_cv<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    lambdas: Option<PyReadonlyArray1<'py, f64>>,
    n_folds: usize,
    max_iter: usize,
    tol: f64,
    seed: u64,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let lams = match lambdas {
        Some(arr) => numpy1d_to_vec(arr),
        None => vec![0.0, 0.01, 0.1, 1.0, 10.0],
    };
    let config = fdars_core::alignment::LambdaCvConfig {
        lambdas: lams,
        n_folds,
        max_iter,
        tol,
        seed,
    };
    let result = to_pyresult(fdars_core::alignment::lambda_cv(&mat, &av, &config))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("best_lambda", result.best_lambda)?;
    dict.set_item("cv_scores", vec_to_numpy1d(py, result.cv_scores))?;
    dict.set_item("lambdas", vec_to_numpy1d(py, result.lambdas))?;
    Ok(dict)
}

// ─── Outlier detection ──────────────────────────────────────────────────────

/// Elastic outlier detection using distances and Tukey fence.
#[pyfunction]
#[pyo3(signature = (data, argvals, lambda_=0.0, alpha=0.05, use_median=true))]
pub fn elastic_outlier_detection<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    lambda_: f64,
    alpha: f64,
    use_median: bool,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let config = fdars_core::alignment::ElasticOutlierConfig {
        lambda: lambda_,
        alpha,
        use_median,
    };
    let result = to_pyresult(fdars_core::alignment::elastic_outlier_detection(
        &mat, &av, &config,
    ))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item(
        "outlier_indices",
        usize_vec_to_numpy1d(py, result.outlier_indices),
    )?;
    dict.set_item("distances", vec_to_numpy1d(py, result.distances))?;
    dict.set_item("threshold", result.threshold)?;
    dict.set_item(
        "amplitude_distances",
        vec_to_numpy1d(py, result.amplitude_distances),
    )?;
    dict.set_item(
        "phase_distances",
        vec_to_numpy1d(py, result.phase_distances),
    )?;
    Ok(dict)
}

// ─── Partial match ──────────────────────────────────────────────────────────

/// Elastic partial matching: find best-aligned subcurve of a longer curve.
#[pyfunction]
#[pyo3(signature = (template, target, argvals_template, argvals_target, lambda_=0.0, min_span=0.5))]
pub fn elastic_partial_match<'py>(
    py: Python<'py>,
    template: PyReadonlyArray1<'py, f64>,
    target: PyReadonlyArray1<'py, f64>,
    argvals_template: PyReadonlyArray1<'py, f64>,
    argvals_target: PyReadonlyArray1<'py, f64>,
    lambda_: f64,
    min_span: f64,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let tmpl = numpy1d_to_vec(template);
    let tgt = numpy1d_to_vec(target);
    let av_t = numpy1d_to_vec(argvals_template);
    let av_f = numpy1d_to_vec(argvals_target);
    let config = fdars_core::alignment::PartialMatchConfig {
        lambda: lambda_,
        min_span,
    };
    let result = to_pyresult(fdars_core::alignment::elastic_partial_match(
        &tmpl, &tgt, &av_t, &av_f, &config,
    ))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("start_index", result.start_index)?;
    dict.set_item("end_index", result.end_index)?;
    dict.set_item("gamma", vec_to_numpy1d(py, result.gamma))?;
    dict.set_item("distance", result.distance)?;
    dict.set_item("domain_fraction", result.domain_fraction)?;
    Ok(dict)
}

// ─── Peak persistence ───────────────────────────────────────────────────────

/// Peak persistence diagram for choosing the alignment regularisation parameter.
#[pyfunction]
#[pyo3(signature = (data, argvals, lambdas, max_iter=10, tol=1e-3))]
pub fn peak_persistence<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    lambdas: PyReadonlyArray1<'py, f64>,
    max_iter: usize,
    tol: f64,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let lams = numpy1d_to_vec(lambdas);
    let result = to_pyresult(fdars_core::alignment::peak_persistence(
        &mat, &av, &lams, max_iter, tol,
    ))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("lambdas", vec_to_numpy1d(py, result.lambdas))?;
    let peak_counts_f64: Vec<f64> = result.peak_counts.iter().map(|&c| c as f64).collect();
    dict.set_item("peak_counts", vec_to_numpy1d(py, peak_counts_f64))?;
    dict.set_item("optimal_lambda", result.optimal_lambda)?;
    dict.set_item("optimal_index", result.optimal_index)?;
    Ok(dict)
}

// ─── Phase boxplot ──────────────────────────────────────────────────────────

/// Phase (warping) box plot for functional data.
#[pyfunction]
#[pyo3(signature = (gammas, argvals, factor=1.5))]
pub fn phase_boxplot<'py>(
    py: Python<'py>,
    gammas: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    factor: f64,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(gammas)?;
    let av = numpy1d_to_vec(argvals);
    let result = to_pyresult(fdars_core::alignment::phase_boxplot(&mat, &av, factor))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("median", vec_to_numpy1d(py, result.median))?;
    dict.set_item("median_index", result.median_index)?;
    dict.set_item("central_lower", vec_to_numpy1d(py, result.central_lower))?;
    dict.set_item("central_upper", vec_to_numpy1d(py, result.central_upper))?;
    dict.set_item("whisker_lower", vec_to_numpy1d(py, result.whisker_lower))?;
    dict.set_item("whisker_upper", vec_to_numpy1d(py, result.whisker_upper))?;
    dict.set_item("depths", vec_to_numpy1d(py, result.depths))?;
    dict.set_item(
        "outlier_indices",
        usize_vec_to_numpy1d(py, result.outlier_indices),
    )?;
    dict.set_item("factor", result.factor)?;
    Ok(dict)
}

// ─── Quality ────────────────────────────────────────────────────────────────

/// Comprehensive alignment quality metrics.
#[pyfunction]
#[pyo3(signature = (data, argvals, lambda_=0.0, max_iter=20, tol=1e-4))]
pub fn alignment_quality<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    lambda_: f64,
    max_iter: usize,
    tol: f64,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let karcher = fdars_core::alignment::karcher_mean(&mat, &av, max_iter, tol, lambda_);
    let result = fdars_core::alignment::alignment_quality(&mat, &karcher, &av);

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item(
        "warp_complexity",
        vec_to_numpy1d(py, result.warp_complexity),
    )?;
    dict.set_item("mean_warp_complexity", result.mean_warp_complexity)?;
    dict.set_item(
        "warp_smoothness",
        vec_to_numpy1d(py, result.warp_smoothness),
    )?;
    dict.set_item("mean_warp_smoothness", result.mean_warp_smoothness)?;
    dict.set_item("total_variance", result.total_variance)?;
    dict.set_item("amplitude_variance", result.amplitude_variance)?;
    dict.set_item("phase_variance", result.phase_variance)?;
    dict.set_item("phase_amplitude_ratio", result.phase_amplitude_ratio)?;
    dict.set_item(
        "pointwise_variance_ratio",
        vec_to_numpy1d(py, result.pointwise_variance_ratio),
    )?;
    dict.set_item("mean_variance_reduction", result.mean_variance_reduction)?;
    Ok(dict)
}

/// Pairwise alignment consistency via triplet checks.
#[pyfunction]
#[pyo3(signature = (data, argvals, lambda_=0.0, max_triplets=0))]
pub fn pairwise_consistency(
    data: PyReadonlyArray2<'_, f64>,
    argvals: PyReadonlyArray1<'_, f64>,
    lambda_: f64,
    max_triplets: usize,
) -> PyResult<f64> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    Ok(fdars_core::alignment::pairwise_consistency(
        &mat,
        &av,
        lambda_,
        max_triplets,
    ))
}

// ─── Shape analysis ─────────────────────────────────────────────────────────

/// Shape mean of a set of curves.
#[pyfunction]
#[pyo3(signature = (data, argvals, quotient="reparameterization", lambda_=0.0, max_iter=20, tol=1e-4))]
pub fn shape_mean<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    quotient: &str,
    lambda_: f64,
    max_iter: usize,
    tol: f64,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let q = match quotient {
        "reparameterization_translation" => {
            fdars_core::alignment::ShapeQuotient::ReparameterizationTranslation
        }
        "reparameterization_translation_scale" => {
            fdars_core::alignment::ShapeQuotient::ReparameterizationTranslationScale
        }
        _ => fdars_core::alignment::ShapeQuotient::Reparameterization,
    };
    let result = to_pyresult(fdars_core::alignment::shape_mean(
        &mat, &av, q, lambda_, max_iter, tol,
    ))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("mean", vec_to_numpy1d(py, result.mean))?;
    dict.set_item("mean_srsf", vec_to_numpy1d(py, result.mean_srsf))?;
    dict.set_item(
        "aligned_data",
        fdmatrix_to_numpy2d(py, &result.aligned_data),
    )?;
    dict.set_item("gammas", fdmatrix_to_numpy2d(py, &result.gammas))?;
    dict.set_item("n_iter", result.n_iter)?;
    dict.set_item("converged", result.converged)?;
    Ok(dict)
}

/// Pairwise shape distance matrix.
#[pyfunction]
#[pyo3(signature = (data, argvals, quotient="reparameterization", lambda_=0.0))]
pub fn shape_self_distance_matrix<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    quotient: &str,
    lambda_: f64,
) -> PyResult<Bound<'py, PyArray2<f64>>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let q = match quotient {
        "reparameterization_translation" => {
            fdars_core::alignment::ShapeQuotient::ReparameterizationTranslation
        }
        "reparameterization_translation_scale" => {
            fdars_core::alignment::ShapeQuotient::ReparameterizationTranslationScale
        }
        _ => fdars_core::alignment::ShapeQuotient::Reparameterization,
    };
    let result = to_pyresult(fdars_core::alignment::shape_self_distance_matrix(
        &mat, &av, q, lambda_,
    ))?;
    Ok(fdmatrix_to_numpy2d(py, &result))
}

// ─── Shape confidence intervals ─────────────────────────────────────────────

/// Bootstrap confidence intervals for the elastic Karcher mean.
#[pyfunction]
#[pyo3(signature = (data, argvals, n_bootstrap=200, confidence_level=0.95, lambda_=0.0, max_iter=15, tol=1e-3, seed=42))]
pub fn shape_confidence_interval<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    n_bootstrap: usize,
    confidence_level: f64,
    lambda_: f64,
    max_iter: usize,
    tol: f64,
    seed: u64,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let config = fdars_core::alignment::ShapeCiConfig {
        n_bootstrap,
        confidence_level,
        lambda: lambda_,
        max_iter,
        tol,
        seed,
    };
    let result = to_pyresult(fdars_core::alignment::shape_confidence_interval(
        &mat, &av, &config,
    ))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("mean", vec_to_numpy1d(py, result.mean))?;
    dict.set_item("lower_band", vec_to_numpy1d(py, result.lower_band))?;
    dict.set_item("upper_band", vec_to_numpy1d(py, result.upper_band))?;
    dict.set_item(
        "bootstrap_means",
        fdmatrix_to_numpy2d(py, &result.bootstrap_means),
    )?;
    Ok(dict)
}

// ─── Transfer alignment ─────────────────────────────────────────────────────

/// Align curves from a target population to a source population's coordinate system.
#[pyfunction]
#[pyo3(signature = (source_data, target_data, argvals, lambda_=0.0, max_iter=15, tol=1e-3))]
pub fn transfer_alignment<'py>(
    py: Python<'py>,
    source_data: PyReadonlyArray2<'py, f64>,
    target_data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    lambda_: f64,
    max_iter: usize,
    tol: f64,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let src = numpy2d_to_fdmatrix(source_data)?;
    let tgt = numpy2d_to_fdmatrix(target_data)?;
    let av = numpy1d_to_vec(argvals);
    let config = fdars_core::alignment::TransferAlignConfig {
        lambda: lambda_,
        max_iter,
        tol,
    };
    let result = to_pyresult(fdars_core::alignment::transfer_alignment(
        &src, &tgt, &av, &config,
    ))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("source_mean", vec_to_numpy1d(py, result.source_mean))?;
    dict.set_item(
        "aligned_data",
        fdmatrix_to_numpy2d(py, &result.aligned_data),
    )?;
    dict.set_item("gammas", fdmatrix_to_numpy2d(py, &result.gammas))?;
    dict.set_item("bridging_gamma", vec_to_numpy1d(py, result.bridging_gamma))?;
    dict.set_item("distances", vec_to_numpy1d(py, result.distances))?;
    Ok(dict)
}

// ─── TSRVF ──────────────────────────────────────────────────────────────────

/// TSRVF (Transported SRSF) transform.
#[pyfunction]
#[pyo3(signature = (data, argvals, max_iter=20, tol=1e-4, lambda_=0.0))]
pub fn tsrvf_transform<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    max_iter: usize,
    tol: f64,
    lambda_: f64,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let result = fdars_core::alignment::tsrvf_transform(&mat, &av, max_iter, tol, lambda_);

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item(
        "tangent_vectors",
        fdmatrix_to_numpy2d(py, &result.tangent_vectors),
    )?;
    dict.set_item("mean", vec_to_numpy1d(py, result.mean))?;
    dict.set_item("mean_srsf", vec_to_numpy1d(py, result.mean_srsf))?;
    dict.set_item("mean_srsf_norm", result.mean_srsf_norm)?;
    dict.set_item("srsf_norms", vec_to_numpy1d(py, result.srsf_norms))?;
    dict.set_item("initial_values", vec_to_numpy1d(py, result.initial_values))?;
    dict.set_item("gammas", fdmatrix_to_numpy2d(py, &result.gammas))?;
    dict.set_item("converged", result.converged)?;
    Ok(dict)
}

/// TSRVF transform with configurable transport method.
#[pyfunction]
#[pyo3(signature = (data, argvals, max_iter=20, tol=1e-4, lambda_=0.0, method="log_map"))]
pub fn tsrvf_transform_with_method<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    max_iter: usize,
    tol: f64,
    lambda_: f64,
    method: &str,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let transport = match method {
        "schilds_ladder" => fdars_core::alignment::TransportMethod::SchildsLadder,
        "pole_ladder" => fdars_core::alignment::TransportMethod::PoleLadder,
        _ => fdars_core::alignment::TransportMethod::LogMap,
    };
    let result = fdars_core::alignment::tsrvf_transform_with_method(
        &mat, &av, max_iter, tol, lambda_, transport,
    );

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item(
        "tangent_vectors",
        fdmatrix_to_numpy2d(py, &result.tangent_vectors),
    )?;
    dict.set_item("mean", vec_to_numpy1d(py, result.mean))?;
    dict.set_item("mean_srsf", vec_to_numpy1d(py, result.mean_srsf))?;
    dict.set_item("mean_srsf_norm", result.mean_srsf_norm)?;
    dict.set_item("srsf_norms", vec_to_numpy1d(py, result.srsf_norms))?;
    dict.set_item("initial_values", vec_to_numpy1d(py, result.initial_values))?;
    dict.set_item("gammas", fdmatrix_to_numpy2d(py, &result.gammas))?;
    dict.set_item("converged", result.converged)?;
    Ok(dict)
}

// ─── Warp statistics ────────────────────────────────────────────────────────

/// Warp statistics: mean, variance, confidence bands, Karcher mean warp.
#[pyfunction]
#[pyo3(signature = (gammas, argvals, confidence_level=0.95))]
pub fn warp_statistics<'py>(
    py: Python<'py>,
    gammas: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    confidence_level: f64,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(gammas)?;
    let av = numpy1d_to_vec(argvals);
    let result = to_pyresult(fdars_core::alignment::warp_statistics(
        &mat,
        &av,
        confidence_level,
    ))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("mean", vec_to_numpy1d(py, result.mean))?;
    dict.set_item("variance", vec_to_numpy1d(py, result.variance))?;
    dict.set_item("std_dev", vec_to_numpy1d(py, result.std_dev))?;
    dict.set_item("lower_band", vec_to_numpy1d(py, result.lower_band))?;
    dict.set_item("upper_band", vec_to_numpy1d(py, result.upper_band))?;
    dict.set_item(
        "karcher_mean_warp",
        vec_to_numpy1d(py, result.karcher_mean_warp),
    )?;
    dict.set_item(
        "geodesic_distances",
        vec_to_numpy1d(py, result.geodesic_distances),
    )?;
    Ok(dict)
}

// ─── FPNS ───────────────────────────────────────────────────────────────────

/// Horizontal Functional Principal Nested Spheres (FPNS) analysis.
#[pyfunction]
#[pyo3(signature = (data, argvals, ncomp=3, lambda_=0.0, max_iter=20, tol=1e-4))]
pub fn horiz_fpns<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    ncomp: usize,
    lambda_: f64,
    max_iter: usize,
    tol: f64,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let karcher = fdars_core::alignment::karcher_mean(&mat, &av, max_iter, tol, lambda_);
    let result = to_pyresult(fdars_core::alignment::horiz_fpns(&karcher, &av, ncomp))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("components", fdmatrix_to_numpy2d(py, &result.components))?;
    dict.set_item("scores", fdmatrix_to_numpy2d(py, &result.scores))?;
    dict.set_item(
        "explained_variance",
        vec_to_numpy1d(py, result.explained_variance),
    )?;
    Ok(dict)
}

// ─── Reparameterize curve ───────────────────────────────────────────────────

/// Apply a warping function to a curve (reparameterize).
#[pyfunction]
pub fn reparameterize_curve<'py>(
    py: Python<'py>,
    curve: PyReadonlyArray1<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    gamma: PyReadonlyArray1<'py, f64>,
) -> Bound<'py, PyArray1<f64>> {
    let c = numpy1d_to_vec(curve);
    let av = numpy1d_to_vec(argvals);
    let g = numpy1d_to_vec(gamma);
    let result = fdars_core::alignment::reparameterize_curve(&c, &av, &g);
    vec_to_numpy1d(py, result)
}

/// Compute the L2 error of a warp inverse: ||gamma(gamma_inv(t)) - t||.
#[pyfunction]
pub fn warp_inverse_error(
    warp: PyReadonlyArray1<'_, f64>,
    argvals: PyReadonlyArray1<'_, f64>,
) -> PyResult<f64> {
    let w = numpy1d_to_vec(warp);
    let av = numpy1d_to_vec(argvals);
    let inv = to_pyresult(fdars_core::alignment::invert_warp(&w, &av))?;
    Ok(fdars_core::alignment::warp_inverse_error(&w, &inv, &av))
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
    // New bindings
    m.add_function(wrap_pyfunction!(elastic_align_pair_penalized, m)?)?;
    m.add_function(wrap_pyfunction!(bayesian_align_pair, m)?)?;
    m.add_function(wrap_pyfunction!(elastic_align_pair_closed, m)?)?;
    m.add_function(wrap_pyfunction!(elastic_distance_closed, m)?)?;
    m.add_function(wrap_pyfunction!(karcher_mean_closed, m)?)?;
    m.add_function(wrap_pyfunction!(elastic_align_pair_constrained, m)?)?;
    m.add_function(wrap_pyfunction!(kmedoids_from_distances, m)?)?;
    m.add_function(wrap_pyfunction!(hierarchical_from_distances, m)?)?;
    m.add_function(wrap_pyfunction!(hierarchical_cut, m)?)?;
    m.add_function(wrap_pyfunction!(elastic_align_pair_multires, m)?)?;
    m.add_function(wrap_pyfunction!(align_to_target, m)?)?;
    m.add_function(wrap_pyfunction!(elastic_decomposition, m)?)?;
    m.add_function(wrap_pyfunction!(amplitude_self_distance_matrix, m)?)?;
    m.add_function(wrap_pyfunction!(phase_self_distance_matrix, m)?)?;
    m.add_function(wrap_pyfunction!(diagnose_alignment, m)?)?;
    m.add_function(wrap_pyfunction!(gauss_model, m)?)?;
    m.add_function(wrap_pyfunction!(joint_gauss_model, m)?)?;
    m.add_function(wrap_pyfunction!(curve_geodesic, m)?)?;
    m.add_function(wrap_pyfunction!(lambda_cv, m)?)?;
    m.add_function(wrap_pyfunction!(elastic_outlier_detection, m)?)?;
    m.add_function(wrap_pyfunction!(elastic_partial_match, m)?)?;
    m.add_function(wrap_pyfunction!(peak_persistence, m)?)?;
    m.add_function(wrap_pyfunction!(phase_boxplot, m)?)?;
    m.add_function(wrap_pyfunction!(alignment_quality, m)?)?;
    m.add_function(wrap_pyfunction!(pairwise_consistency, m)?)?;
    m.add_function(wrap_pyfunction!(shape_mean, m)?)?;
    m.add_function(wrap_pyfunction!(shape_self_distance_matrix, m)?)?;
    m.add_function(wrap_pyfunction!(shape_confidence_interval, m)?)?;
    m.add_function(wrap_pyfunction!(transfer_alignment, m)?)?;
    m.add_function(wrap_pyfunction!(tsrvf_transform, m)?)?;
    m.add_function(wrap_pyfunction!(tsrvf_transform_with_method, m)?)?;
    m.add_function(wrap_pyfunction!(warp_statistics, m)?)?;
    m.add_function(wrap_pyfunction!(horiz_fpns, m)?)?;
    m.add_function(wrap_pyfunction!(reparameterize_curve, m)?)?;
    m.add_function(wrap_pyfunction!(warp_inverse_error, m)?)?;
    Ok(())
}
