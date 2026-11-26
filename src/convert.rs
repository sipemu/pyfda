//! Conversion utilities between numpy arrays and fdars-core types.

use fdars_core::matrix::{FdCurveSet, FdMatrix};
use fdars_core::FdarError;
use numpy::ndarray::{Array2, Array3};
use numpy::{PyArray1, PyArray2, PyArray3, PyReadonlyArray1, PyReadonlyArray2, PyReadonlyArray3};
use pyo3::prelude::*;
use pyo3::types::{PyList, PyTuple};

/// Resolve an optional argvals array to a concrete grid.
///
/// Returns the supplied argvals, or a uniform [0, 1] grid of length `m` when
/// `None` (matching the convention used across the core depth/metric routines).
pub fn default_grid(argvals: Option<PyReadonlyArray1<'_, f64>>, m: usize) -> Vec<f64> {
    match argvals {
        Some(a) => numpy1d_to_vec(a),
        None => {
            if m <= 1 {
                vec![0.0; m]
            } else {
                (0..m).map(|i| i as f64 / (m - 1) as f64).collect()
            }
        }
    }
}

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

/// Extract a Python list of 1-D arrays / lists / tuples into a Vec<Vec<f64>>.
///
/// Accepts each element as:
/// - A 1-D numpy f64 array (zero-copy via PyReadonlyArray1)
/// - A plain Python list of floats
/// - A Python tuple of floats
///
/// Error messages use `caller_name` to produce context-specific messages
/// (e.g. "frechet_mean: element [2] ..." vs "irreg_fdata_from_lists: element [2] ...").
///
/// Per-caller length-uniformity validation is the CALLER's responsibility —
/// this helper intentionally does NOT reject ragged (non-uniform) lengths.
pub fn extract_ragged_vecs(list: &Bound<'_, PyList>, caller_name: &str) -> PyResult<Vec<Vec<f64>>> {
    list.iter()
        .enumerate()
        .map(|(i, item)| {
            if let Ok(arr) = item.extract::<numpy::PyReadonlyArray1<f64>>() {
                Ok(arr.as_array().to_vec())
            } else if let Ok(seq) = item.cast::<PyList>() {
                seq.iter()
                    .map(|x| x.extract::<f64>())
                    .collect::<PyResult<Vec<_>>>()
            } else if let Ok(tup) = item.cast::<PyTuple>() {
                tup.iter()
                    .map(|x| x.extract::<f64>())
                    .collect::<PyResult<Vec<_>>>()
            } else {
                let type_name = item
                    .get_type()
                    .name()
                    .map(|s| s.to_string())
                    .unwrap_or_else(|_| "?".to_string());
                Err(pyo3::exceptions::PyValueError::new_err(format!(
                    "{caller_name}: element [{i}] is not a 1-D numpy array or \
                     list of floats; got {type_name}"
                )))
            }
        })
        .collect()
}

/// Convert a numpy 3D array `(n, d, m)` to `n` matrices of shape `d × m`.
///
/// Row = coordinate / channel, column = time point: the layout of the
/// multivariate DTW / elastic-distance functions and the R^d curve functions.
pub fn numpy3d_to_curves(arr: PyReadonlyArray3<'_, f64>) -> PyResult<Vec<FdMatrix>> {
    let a = arr.as_array();
    let (n, d, m) = a.dim();
    (0..n)
        .map(|i| {
            let mut col_major = vec![0.0; d * m];
            for k in 0..d {
                for j in 0..m {
                    col_major[k + j * d] = a[[i, k, j]];
                }
            }
            FdMatrix::from_column_major(col_major, d, m).map_err(to_pyerr)
        })
        .collect()
}

/// Extract a Python list of 2-D float arrays into matrices (ragged shapes allowed).
///
/// Error messages name `caller_name` and the offending list index.
pub fn list_to_fdmatrices(list: &Bound<'_, PyList>, caller_name: &str) -> PyResult<Vec<FdMatrix>> {
    list.iter()
        .enumerate()
        .map(|(i, item)| {
            let arr = item.extract::<PyReadonlyArray2<f64>>().map_err(|_| {
                pyo3::exceptions::PyValueError::new_err(format!(
                    "{caller_name}: element [{i}] must be a 2-D numpy array of dtype float64"
                ))
            })?;
            numpy2d_to_fdmatrix(arr)
        })
        .collect()
}

/// Extract a collection of 2-D series given as a list of `(d, m_i)` arrays or
/// a 3-D `(n, d, m)` array.
pub fn series_collection(obj: &Bound<'_, PyAny>, caller_name: &str) -> PyResult<Vec<FdMatrix>> {
    if let Ok(list) = obj.cast::<PyList>() {
        return list_to_fdmatrices(list, caller_name);
    }
    let arr = obj.extract::<PyReadonlyArray3<f64>>().map_err(|_| {
        pyo3::exceptions::PyValueError::new_err(format!(
            "{caller_name}: expected a list of 2-D (d, m) float arrays or a 3-D (n, d, m) float array"
        ))
    })?;
    numpy3d_to_curves(arr)
}

/// Convert matrices to a Python list of 2-D numpy arrays.
pub fn fdmatrices_to_pylist<'py>(
    py: Python<'py>,
    mats: &[FdMatrix],
) -> PyResult<Bound<'py, PyList>> {
    let list = PyList::empty(py);
    for mat in mats {
        list.append(fdmatrix_to_numpy2d(py, mat))?;
    }
    Ok(list)
}

/// `(d, m)` array → one R^d curve as a set: d coordinate matrices of shape `1 × m`
/// (the per-curve input of the `*_nd_with_config` functions).
pub fn nd_curveset_from_curve(arr: PyReadonlyArray2<'_, f64>) -> PyResult<FdCurveSet> {
    let a = arr.as_array();
    let dims = a
        .rows()
        .into_iter()
        .map(|row| FdMatrix::from_column_major(row.to_vec(), 1, row.len()).map_err(to_pyerr))
        .collect::<PyResult<Vec<_>>>()?;
    Ok(FdCurveSet { dims })
}

/// `(n, d, m)` array → n single-curve sets (the input of `karcher_mean_nd*`).
pub fn nd_curvesets_from_numpy3d(arr: PyReadonlyArray3<'_, f64>) -> PyResult<Vec<FdCurveSet>> {
    let a = arr.as_array();
    let (n, d, m) = a.dim();
    (0..n)
        .map(|i| {
            let dims = (0..d)
                .map(|k| {
                    let row: Vec<f64> = (0..m).map(|j| a[[i, k, j]]).collect();
                    FdMatrix::from_column_major(row, 1, m).map_err(to_pyerr)
                })
                .collect::<PyResult<Vec<_>>>()?;
            Ok(FdCurveSet { dims })
        })
        .collect()
}

/// A collection of equally shaped `(d, m)` curves (list of 2-D arrays or a
/// `(n, d, m)` array) → one `FdCurveSet` with d coordinate matrices `n × m`.
pub fn curve_collection_to_set(obj: &Bound<'_, PyAny>, caller_name: &str) -> PyResult<FdCurveSet> {
    let curves = series_collection(obj, caller_name)?;
    to_pyresult(fdars_core::alignment::curves_to_set(&curves))
}

/// `d` vectors of length m → `(d, m)` array.
pub fn rows_to_numpy2d<'py>(py: Python<'py>, rows: &[Vec<f64>]) -> Bound<'py, PyArray2<f64>> {
    let m = rows.first().map_or(0, Vec::len);
    PyArray2::from_owned_array(
        py,
        Array2::from_shape_fn((rows.len(), m), |(k, j)| rows[k][j]),
    )
}

/// d coordinate matrices of shape `n × m` → `(n, d, m)` array.
pub fn curve_dims_to_numpy3d<'py>(py: Python<'py>, dims: &[FdMatrix]) -> Bound<'py, PyArray3<f64>> {
    let (n, m) = dims.first().map_or((0, 0), FdMatrix::shape);
    PyArray3::from_owned_array(
        py,
        Array3::from_shape_fn((n, dims.len(), m), |(i, k, j)| dims[k][(i, j)]),
    )
}

/// `FdCurveSet` → `(n, d, m)` array, `out[i, k, j] = set.dims[k][(i, j)]`.
pub fn curveset_to_numpy3d<'py>(py: Python<'py>, set: &FdCurveSet) -> Bound<'py, PyArray3<f64>> {
    curve_dims_to_numpy3d(py, &set.dims)
}

/// Equally shaped matrices (e.g. n rotations `d × d`) → `(n, r, c)` array.
pub fn stack_fdmatrices<'py>(py: Python<'py>, mats: &[FdMatrix]) -> Bound<'py, PyArray3<f64>> {
    let (r, c) = mats.first().map_or((0, 0), FdMatrix::shape);
    PyArray3::from_owned_array(
        py,
        Array3::from_shape_fn((mats.len(), r, c), |(i, a, b)| mats[i][(a, b)]),
    )
}
