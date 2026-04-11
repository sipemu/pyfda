//! Depth measures for functional data.

use crate::convert::*;
use numpy::{PyArray1, PyReadonlyArray1, PyReadonlyArray2};
use pyo3::prelude::*;

/// Fraiman-Muniz depth for 1D functional data.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Data to compute depth for, shape (n, m).
/// ref_data : numpy.ndarray
///     Reference sample, shape (n_ref, m).
/// scale : bool, optional
///     Whether to scale the depth values (default True).
///
/// Returns
/// -------
/// numpy.ndarray
///     Depth values, length n.
#[pyfunction]
#[pyo3(signature = (data, ref_data, scale=true))]
pub fn fraiman_muniz_1d<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    ref_data: PyReadonlyArray2<'py, f64>,
    scale: bool,
) -> PyResult<Bound<'py, PyArray1<f64>>> {
    let d = numpy2d_to_fdmatrix(data)?;
    let r = numpy2d_to_fdmatrix(ref_data)?;
    let result = fdars_core::depth::fraiman_muniz_1d(&d, &r, scale);
    Ok(vec_to_numpy1d(py, result))
}

/// Fraiman-Muniz depth for 2D functional data.
#[pyfunction]
#[pyo3(signature = (data, ref_data, scale=true))]
pub fn fraiman_muniz_2d<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    ref_data: PyReadonlyArray2<'py, f64>,
    scale: bool,
) -> PyResult<Bound<'py, PyArray1<f64>>> {
    let d = numpy2d_to_fdmatrix(data)?;
    let r = numpy2d_to_fdmatrix(ref_data)?;
    let result = fdars_core::depth::fraiman_muniz_2d(&d, &r, scale);
    Ok(vec_to_numpy1d(py, result))
}

/// Modal depth for 1D functional data.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Data to compute depth for, shape (n, m).
/// ref_data : numpy.ndarray
///     Reference sample, shape (n_ref, m).
/// h : float, optional
///     Bandwidth (default 1.0).
///
/// Returns
/// -------
/// numpy.ndarray
///     Depth values, length n.
#[pyfunction]
#[pyo3(signature = (data, ref_data, h=1.0))]
pub fn modal_1d<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    ref_data: PyReadonlyArray2<'py, f64>,
    h: f64,
) -> PyResult<Bound<'py, PyArray1<f64>>> {
    let d = numpy2d_to_fdmatrix(data)?;
    let r = numpy2d_to_fdmatrix(ref_data)?;
    let result = fdars_core::depth::modal_1d(&d, &r, h);
    Ok(vec_to_numpy1d(py, result))
}

/// Modal depth for 2D functional data.
#[pyfunction]
#[pyo3(signature = (data, ref_data, h=1.0))]
pub fn modal_2d<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    ref_data: PyReadonlyArray2<'py, f64>,
    h: f64,
) -> PyResult<Bound<'py, PyArray1<f64>>> {
    let d = numpy2d_to_fdmatrix(data)?;
    let r = numpy2d_to_fdmatrix(ref_data)?;
    let result = fdars_core::depth::modal_2d(&d, &r, h);
    Ok(vec_to_numpy1d(py, result))
}

/// Random projection depth for 1D functional data.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Data, shape (n, m).
/// ref_data : numpy.ndarray
///     Reference, shape (n_ref, m).
/// n_proj : int, optional
///     Number of projections (default 50).
///
/// Returns
/// -------
/// numpy.ndarray
///     Depth values, length n.
#[pyfunction]
#[pyo3(signature = (data, ref_data, n_proj=50))]
pub fn random_projection_1d<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    ref_data: PyReadonlyArray2<'py, f64>,
    n_proj: usize,
) -> PyResult<Bound<'py, PyArray1<f64>>> {
    let d = numpy2d_to_fdmatrix(data)?;
    let r = numpy2d_to_fdmatrix(ref_data)?;
    let result = fdars_core::depth::random_projection_1d(&d, &r, n_proj);
    Ok(vec_to_numpy1d(py, result))
}

/// Random projection depth for 2D functional data.
#[pyfunction]
#[pyo3(signature = (data, ref_data, n_proj=50))]
pub fn random_projection_2d<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    ref_data: PyReadonlyArray2<'py, f64>,
    n_proj: usize,
) -> PyResult<Bound<'py, PyArray1<f64>>> {
    let d = numpy2d_to_fdmatrix(data)?;
    let r = numpy2d_to_fdmatrix(ref_data)?;
    let result = fdars_core::depth::random_projection_2d(&d, &r, n_proj);
    Ok(vec_to_numpy1d(py, result))
}

/// Random Tukey depth for 1D functional data.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Data, shape (n, m).
/// ref_data : numpy.ndarray
///     Reference, shape (n_ref, m).
/// n_proj : int, optional
///     Number of projections (default 50).
///
/// Returns
/// -------
/// numpy.ndarray
///     Depth values, length n.
#[pyfunction]
#[pyo3(signature = (data, ref_data, n_proj=50))]
pub fn random_tukey_1d<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    ref_data: PyReadonlyArray2<'py, f64>,
    n_proj: usize,
) -> PyResult<Bound<'py, PyArray1<f64>>> {
    let d = numpy2d_to_fdmatrix(data)?;
    let r = numpy2d_to_fdmatrix(ref_data)?;
    let result = fdars_core::depth::random_tukey_1d(&d, &r, n_proj);
    Ok(vec_to_numpy1d(py, result))
}

/// Random Tukey depth for 2D functional data.
#[pyfunction]
#[pyo3(signature = (data, ref_data, n_proj=50))]
pub fn random_tukey_2d<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    ref_data: PyReadonlyArray2<'py, f64>,
    n_proj: usize,
) -> PyResult<Bound<'py, PyArray1<f64>>> {
    let d = numpy2d_to_fdmatrix(data)?;
    let r = numpy2d_to_fdmatrix(ref_data)?;
    let result = fdars_core::depth::random_tukey_2d(&d, &r, n_proj);
    Ok(vec_to_numpy1d(py, result))
}

/// Band depth for 1D functional data.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Data, shape (n, m).
/// ref_data : numpy.ndarray
///     Reference, shape (n_ref, m).
///
/// Returns
/// -------
/// numpy.ndarray
///     Depth values, length n.
#[pyfunction]
pub fn band_1d<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    ref_data: PyReadonlyArray2<'py, f64>,
) -> PyResult<Bound<'py, PyArray1<f64>>> {
    let d = numpy2d_to_fdmatrix(data)?;
    let r = numpy2d_to_fdmatrix(ref_data)?;
    let result = fdars_core::depth::band_1d(&d, &r);
    Ok(vec_to_numpy1d(py, result))
}

/// Modified band depth for 1D functional data.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Data, shape (n, m).
/// ref_data : numpy.ndarray
///     Reference, shape (n_ref, m).
///
/// Returns
/// -------
/// numpy.ndarray
///     Depth values, length n.
#[pyfunction]
pub fn modified_band_1d<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    ref_data: PyReadonlyArray2<'py, f64>,
) -> PyResult<Bound<'py, PyArray1<f64>>> {
    let d = numpy2d_to_fdmatrix(data)?;
    let r = numpy2d_to_fdmatrix(ref_data)?;
    let result = fdars_core::depth::modified_band_1d(&d, &r);
    Ok(vec_to_numpy1d(py, result))
}

/// Modified epigraph index for 1D functional data.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Data, shape (n, m).
/// ref_data : numpy.ndarray
///     Reference, shape (n_ref, m).
///
/// Returns
/// -------
/// numpy.ndarray
///     Depth values, length n.
#[pyfunction]
pub fn modified_epigraph_index_1d<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    ref_data: PyReadonlyArray2<'py, f64>,
) -> PyResult<Bound<'py, PyArray1<f64>>> {
    let d = numpy2d_to_fdmatrix(data)?;
    let r = numpy2d_to_fdmatrix(ref_data)?;
    let result = fdars_core::depth::modified_epigraph_index_1d(&d, &r);
    Ok(vec_to_numpy1d(py, result))
}

/// Functional spatial depth for 1D data.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Data, shape (n, m).
/// ref_data : numpy.ndarray
///     Reference, shape (n_ref, m).
/// argvals : numpy.ndarray, optional
///     Evaluation points, length m. If None, uses uniform [0,1] grid.
///
/// Returns
/// -------
/// numpy.ndarray
///     Depth values, length n.
#[pyfunction]
#[pyo3(signature = (data, ref_data, argvals=None))]
pub fn functional_spatial_1d<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    ref_data: PyReadonlyArray2<'py, f64>,
    argvals: Option<PyReadonlyArray1<'py, f64>>,
) -> PyResult<Bound<'py, PyArray1<f64>>> {
    let d = numpy2d_to_fdmatrix(data)?;
    let r = numpy2d_to_fdmatrix(ref_data)?;
    let av = argvals.map(numpy1d_to_vec);
    let result = fdars_core::depth::functional_spatial_1d(&d, &r, av.as_deref());
    Ok(vec_to_numpy1d(py, result))
}

/// Functional spatial depth for 2D data.
#[pyfunction]
pub fn functional_spatial_2d<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    ref_data: PyReadonlyArray2<'py, f64>,
) -> PyResult<Bound<'py, PyArray1<f64>>> {
    let d = numpy2d_to_fdmatrix(data)?;
    let r = numpy2d_to_fdmatrix(ref_data)?;
    let result = fdars_core::depth::functional_spatial_2d(&d, &r);
    Ok(vec_to_numpy1d(py, result))
}

/// Kernel functional spatial depth for 1D data.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Data, shape (n, m).
/// ref_data : numpy.ndarray
///     Reference, shape (n_ref, m).
/// argvals : numpy.ndarray
///     Evaluation points, length m.
/// h : float, optional
///     Bandwidth (default 1.0).
///
/// Returns
/// -------
/// numpy.ndarray
///     Depth values, length n.
#[pyfunction]
#[pyo3(signature = (data, ref_data, argvals, h=1.0))]
pub fn kernel_functional_spatial_1d<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    ref_data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    h: f64,
) -> PyResult<Bound<'py, PyArray1<f64>>> {
    let d = numpy2d_to_fdmatrix(data)?;
    let r = numpy2d_to_fdmatrix(ref_data)?;
    let av = numpy1d_to_vec(argvals);
    let result = fdars_core::depth::kernel_functional_spatial_1d(&d, &r, &av, h);
    Ok(vec_to_numpy1d(py, result))
}

/// Kernel functional spatial depth for 2D data.
#[pyfunction]
#[pyo3(signature = (data, ref_data, h=1.0))]
pub fn kernel_functional_spatial_2d<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    ref_data: PyReadonlyArray2<'py, f64>,
    h: f64,
) -> PyResult<Bound<'py, PyArray1<f64>>> {
    let d = numpy2d_to_fdmatrix(data)?;
    let r = numpy2d_to_fdmatrix(ref_data)?;
    let result = fdars_core::depth::kernel_functional_spatial_2d(&d, &r, h);
    Ok(vec_to_numpy1d(py, result))
}

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(fraiman_muniz_1d, m)?)?;
    m.add_function(wrap_pyfunction!(fraiman_muniz_2d, m)?)?;
    m.add_function(wrap_pyfunction!(modal_1d, m)?)?;
    m.add_function(wrap_pyfunction!(modal_2d, m)?)?;
    m.add_function(wrap_pyfunction!(random_projection_1d, m)?)?;
    m.add_function(wrap_pyfunction!(random_projection_2d, m)?)?;
    m.add_function(wrap_pyfunction!(random_tukey_1d, m)?)?;
    m.add_function(wrap_pyfunction!(random_tukey_2d, m)?)?;
    m.add_function(wrap_pyfunction!(band_1d, m)?)?;
    m.add_function(wrap_pyfunction!(modified_band_1d, m)?)?;
    m.add_function(wrap_pyfunction!(modified_epigraph_index_1d, m)?)?;
    m.add_function(wrap_pyfunction!(functional_spatial_1d, m)?)?;
    m.add_function(wrap_pyfunction!(functional_spatial_2d, m)?)?;
    m.add_function(wrap_pyfunction!(kernel_functional_spatial_1d, m)?)?;
    m.add_function(wrap_pyfunction!(kernel_functional_spatial_2d, m)?)?;
    Ok(())
}
