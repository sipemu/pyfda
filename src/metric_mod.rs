//! Distance metrics for functional data.

use crate::convert::*;
use numpy::{PyArray2, PyReadonlyArray1, PyReadonlyArray2};
use pyo3::prelude::*;

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

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
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
    Ok(())
}
