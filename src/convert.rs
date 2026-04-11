//! Conversion utilities between numpy arrays and fdars-core types.

use fdars_core::matrix::FdMatrix;
use fdars_core::FdarError;
use numpy::{PyArray1, PyArray2, PyReadonlyArray1, PyReadonlyArray2};
use pyo3::prelude::*;

/// Convert a numpy 2D array (row-major) to FdMatrix (column-major).
///
/// NumPy shape: (n_obs, n_points) in C order (row-major).
/// FdMatrix: column-major with nrows=n_obs, ncols=n_points.
pub fn numpy2d_to_fdmatrix(arr: PyReadonlyArray2<'_, f64>) -> PyResult<FdMatrix> {
    let (nrows, ncols) = arr.as_array().dim();

    // Build column-major flat vec from numpy row-major data
    let arr_ref = arr.as_array();
    let mut col_major = vec![0.0; nrows * ncols];
    for i in 0..nrows {
        for j in 0..ncols {
            col_major[i + j * nrows] = arr_ref[[i, j]];
        }
    }

    FdMatrix::from_column_major(col_major, nrows, ncols).map_err(to_pyerr)
}

/// Convert FdMatrix (column-major) to a numpy 2D array (row-major).
///
/// Returns shape (n_obs, n_points).
pub fn fdmatrix_to_numpy2d<'py>(py: Python<'py>, mat: &FdMatrix) -> Bound<'py, PyArray2<f64>> {
    let (nrows, ncols) = mat.shape();
    let row_major = mat.to_row_major();
    // Safety: row_major has exactly nrows * ncols elements
    PyArray2::from_vec2(
        py,
        &(0..nrows)
            .map(|i| row_major[i * ncols..(i + 1) * ncols].to_vec())
            .collect::<Vec<_>>(),
    )
    .unwrap()
}

/// Convert a numpy 1D array to a Vec<f64>.
pub fn numpy1d_to_vec(arr: PyReadonlyArray1<'_, f64>) -> Vec<f64> {
    arr.as_array().to_vec()
}

/// Convert a Vec<f64> to a numpy 1D array.
pub fn vec_to_numpy1d<'py>(py: Python<'py>, v: Vec<f64>) -> Bound<'py, PyArray1<f64>> {
    PyArray1::from_vec(py, v)
}

/// Convert a Vec<Vec<f64>> to a numpy 2D array.
pub fn vec2d_to_numpy2d<'py>(py: Python<'py>, v: &[Vec<f64>]) -> Bound<'py, PyArray2<f64>> {
    PyArray2::from_vec2(py, v).unwrap()
}

/// Convert a numpy 1D i64 array to Vec<usize>.
pub fn numpy1d_to_usize_vec(arr: PyReadonlyArray1<'_, i64>) -> Vec<usize> {
    arr.as_array().iter().map(|&x| x as usize).collect()
}

/// Convert Vec<usize> to numpy 1D i64 array.
pub fn usize_vec_to_numpy1d<'py>(py: Python<'py>, v: Vec<usize>) -> Bound<'py, PyArray1<i64>> {
    PyArray1::from_vec(py, v.into_iter().map(|x| x as i64).collect())
}

/// Convert Vec<bool> to numpy 1D bool array.
pub fn bool_vec_to_numpy1d<'py>(py: Python<'py>, v: Vec<bool>) -> Bound<'py, PyArray1<bool>> {
    PyArray1::from_vec(py, v)
}

/// Convert FdarError to PyErr (PyValueError).
pub fn to_pyerr(e: FdarError) -> PyErr {
    pyo3::exceptions::PyValueError::new_err(e.to_string())
}

/// Convert a Result<T, FdarError> to PyResult<T>.
pub fn to_pyresult<T>(r: Result<T, FdarError>) -> PyResult<T> {
    r.map_err(to_pyerr)
}
