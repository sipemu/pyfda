//! Multi-domain functional data container for pyfda.
//!
//! Exposes `PyMultiFunData` (opaque `#[pyclass]` handle) and
//! `multi_fdata_from_components` (builder from Python lists of 2-D arrays and
//! 1-D argvals vectors) as the `fdars.multi_fdata` submodule.
//!
//! This is pyfda's second opaque `#[pyclass]` handle (after `PyIrregFdata`).
//!
//! # fdars-core 0.33 — Standalone Container
//!
//! As of fdars-core 0.33, **no** mixed-model (`famm`), multivariate-FPCA
//! (`spm::mfpca`), or advanced-clustering function accepts `MultiFunData` as an
//! input parameter.  All three function families take plain `FdMatrix` or
//! `&[&FdMatrix]` slices.  `PyMultiFunData` is therefore a **standalone
//! multi-domain data holder** — it validates component layout once at
//! construction and provides `n_obs` / `n_components` accessors for Python
//! inspection.  Do NOT attempt to pass a `PyRef<PyMultiFunData>` into FAMM,
//! MFPCA, or clustering bindings — those bindings take plain numpy arrays.
//! (MULTI-02 phrase "where required" is vacuously satisfied: no 0.33 function
//! requires it.)

use crate::convert::{numpy1d_to_vec, numpy2d_to_fdmatrix, to_pyresult};
use numpy::PyUntypedArrayMethods;
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::PyList;

// ---------------------------------------------------------------------------
// Opaque #[pyclass] handle
// ---------------------------------------------------------------------------

/// Opaque handle wrapping fdars-core MultiFunData for multi-domain functional data.
///
/// Construct via `fdars.multi_fdata.multi_fdata_from_components(data_list, argvals_list)`.
///
/// As of fdars-core 0.33, no FAMM/MFPCA/clustering function accepts this handle as input —
/// it is a standalone multi-domain container.  Use `n_obs` and `n_components` to inspect it.
#[pyclass(name = "PyMultiFunData")]
pub struct PyMultiFunData {
    pub inner: fdars_core::multi_fdata::MultiFunData,
}

#[pymethods]
impl PyMultiFunData {
    /// Number of observations (curves) shared by all components.
    #[getter]
    pub fn n_obs(&self) -> usize {
        self.inner.n_obs()
    }

    /// Number of functional components (variables/domains).
    #[getter]
    pub fn n_components(&self) -> usize {
        self.inner.n_components()
    }
}

// ---------------------------------------------------------------------------
// #[pyfunction] multi_fdata_from_components
// ---------------------------------------------------------------------------

/// Build a PyMultiFunData handle from lists of 2-D data arrays and 1-D argvals vectors.
///
/// Parameters
/// ----------
/// data_list : list of ndarray, shape (n_obs, n_points_k)
///     One 2-D numpy array per component.  All components must share the same
///     number of rows (`n_obs`).  Each component may have a different number of
///     evaluation points (`n_points_k`).
/// argvals_list : list of ndarray, shape (n_points_k,)
///     One 1-D numpy array per component giving the evaluation grid.
///     `len(argvals_list[k])` must equal `data_list[k].shape[1]` for each `k`.
///
/// Returns
/// -------
/// PyMultiFunData
///     Opaque handle exposing `n_obs` and `n_components` accessors.
///
/// Raises
/// ------
/// ValueError
///     If `data_list` and `argvals_list` differ in length, if any `data_list[k]`
///     is 1-D (pass a 2-D matrix per component), if the number of rows differs
///     across components, or if `argvals_list[k]` length mismatches
///     `data_list[k].shape[1]`.
#[pyfunction]
pub fn multi_fdata_from_components<'py>(
    py: Python<'py>,
    data_list: &Bound<'py, PyList>,
    argvals_list: &Bound<'py, PyList>,
) -> PyResult<Py<PyMultiFunData>> {
    let n_data = data_list.len();
    let n_av = argvals_list.len();

    // Guard 1: outer-list length mismatch BEFORE the core constructor.
    if n_data != n_av {
        return Err(PyValueError::new_err(format!(
            "multi_fdata_from_components: data_list has {n_data} component(s) \
             but argvals_list has {n_av} component(s); lengths must match"
        )));
    }

    let mut components: Vec<fdars_core::multi_fdata::FdComponent> =
        Vec::with_capacity(n_data);

    for k in 0..n_data {
        let data_item = data_list.get_item(k)?;
        let av_item = argvals_list.get_item(k)?;

        // Guard 2: reject a 1-D numpy array passed as component data.
        // Cast to the untyped base (dtype-agnostic) and check ndim.
        let data_is_1d = data_item
            .cast::<numpy::PyUntypedArray>()
            .map(|a| a.ndim() == 1)
            .unwrap_or(false);
        if data_is_1d {
            return Err(PyValueError::new_err(format!(
                "multi_fdata_from_components: data_list[{k}] is 1-D; \
                 each component must be a 2-D numpy array of shape (n_obs, n_points)"
            )));
        }

        // Convert data component: 2-D numpy (n_obs, n_points) → FdMatrix (column-major).
        let data_arr = data_item
            .extract::<numpy::PyReadonlyArray2<f64>>()
            .map_err(|_| {
                PyValueError::new_err(format!(
                    "multi_fdata_from_components: data_list[{k}] must be a \
                     2-D numpy array of dtype float64"
                ))
            })?;
        let mat = numpy2d_to_fdmatrix(data_arr)?;

        // Convert argvals: 1-D numpy → Vec<f64>.
        let av_arr = av_item
            .extract::<numpy::PyReadonlyArray1<f64>>()
            .map_err(|_| {
                PyValueError::new_err(format!(
                    "multi_fdata_from_components: argvals_list[{k}] must be a \
                     1-D numpy array of dtype float64"
                ))
            })?;
        let av = numpy1d_to_vec(av_arr);

        components.push(fdars_core::multi_fdata::FdComponent { data: mat, argvals: av });
    }

    // Guard 3 (delegated): MultiFunData::new validates non-empty components,
    // shared nrows across components, and argvals.len()==data.ncols() per component.
    // FdarError is surfaced as PyValueError via to_pyresult.
    let inner = to_pyresult(fdars_core::multi_fdata::MultiFunData::new(components))?;
    Py::new(py, PyMultiFunData { inner })
}

// ---------------------------------------------------------------------------
// Module registration
// ---------------------------------------------------------------------------

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyMultiFunData>()?;
    m.add_function(wrap_pyfunction!(multi_fdata_from_components, m)?)?;
    Ok(())
}
