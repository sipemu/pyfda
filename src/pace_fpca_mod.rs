//! PACE FPCA and IrregFdata bindings for irregular/sparse functional data.
//!
//! Exposes `PyIrregFdata` (opaque #[pyclass] handle), `irreg_fdata_from_lists`
//! (builder from Python ragged lists), and `pace_fpca` (PACE FPCA over
//! irregular data) as the `fdars.pace_fpca` submodule.
//!
//! This is pyfda's first `#[pyclass]` opaque handle — introduced so the PACE
//! input type has a named Python type and validates once at construction.

use crate::convert::{fdmatrix_to_numpy2d, to_pyresult, vec_to_numpy1d};
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};

// ---------------------------------------------------------------------------
// Opaque #[pyclass] handle
// ---------------------------------------------------------------------------

/// Opaque handle wrapping fdars-core IrregFdata for irregular/sparse functional data.
///
/// Construct via `fdars.pace_fpca.irreg_fdata_from_lists(argvals_list, values_list)`.
/// Pass to `fdars.pace_fpca.pace_fpca(handle, ...)`.
#[pyclass(name = "PyIrregFdata")]
pub struct PyIrregFdata {
    pub inner: fdars_core::irreg_fdata::IrregFdata,
}

// ---------------------------------------------------------------------------
// Private helper: extract Vec<Vec<f64>> from a Python list of 1-D arrays
// ---------------------------------------------------------------------------

fn extract_list_of_vecs(list: &Bound<'_, PyList>) -> PyResult<Vec<Vec<f64>>> {
    list.iter()
        .enumerate()
        .map(|(i, item)| {
            // Accept a 1-D numpy array — use extract to get a readonly view
            if let Ok(arr) = item.extract::<numpy::PyReadonlyArray1<f64>>() {
                Ok(arr.as_array().to_vec())
            } else if let Ok(seq) = item.cast::<PyList>() {
                // Accept a plain Python list of floats
                seq.iter()
                    .map(|x| x.extract::<f64>())
                    .collect::<PyResult<Vec<_>>>()
            } else {
                let type_name = item
                    .get_type()
                    .name()
                    .map(|s| s.to_string())
                    .unwrap_or_else(|_| "?".to_string());
                Err(PyValueError::new_err(format!(
                    "irreg_fdata_from_lists: element [{}] is not a 1-D numpy array or list of floats; \
                     got {}",
                    i,
                    type_name
                )))
            }
        })
        .collect()
}

// ---------------------------------------------------------------------------
// #[pyfunction] irreg_fdata_from_lists
// ---------------------------------------------------------------------------

/// Build an IrregFdata handle from two Python lists of ragged 1-D arrays.
///
/// Parameters
/// ----------
/// argvals_list : list of array-like
///     One 1-D array per curve giving evaluation points (ragged; lengths may differ).
/// values_list : list of array-like
///     One 1-D array per curve giving observed values; must match the corresponding
///     argvals entry in length.
///
/// Returns
/// -------
/// PyIrregFdata
///     Opaque handle for use with `pace_fpca`.
///
/// Raises
/// ------
/// ValueError
///     If a 2-D numpy array is passed (dense data), if the outer lengths differ,
///     or if any curve's argvals and values lengths differ.
#[pyfunction]
pub fn irreg_fdata_from_lists<'py>(
    py: Python<'py>,
    argvals_list: &Bound<'py, PyAny>,
    values_list: &Bound<'py, PyAny>,
) -> PyResult<Py<PyIrregFdata>> {
    // Guard: reject dense 2-D numpy arrays (T-38-03)
    if argvals_list.is_instance_of::<numpy::PyArray2<f64>>()
        || values_list.is_instance_of::<numpy::PyArray2<f64>>()
    {
        return Err(PyValueError::new_err(
            "irreg_fdata_from_lists: received a 2-D numpy array; \
             pass two Python lists of 1-D arrays (one per curve), not a dense matrix. \
             For dense functional data, use fdars.fdata functions directly.",
        ));
    }

    // Downcast both to PyList
    let av_list = argvals_list
        .cast::<PyList>()
        .map_err(|_| PyValueError::new_err("argvals_list must be a Python list of 1-D arrays"))?;
    let vl_list = values_list
        .cast::<PyList>()
        .map_err(|_| PyValueError::new_err("values_list must be a Python list of 1-D arrays"))?;

    // Extract ragged vecs
    let av_vecs = extract_list_of_vecs(av_list)?;
    let vl_vecs = extract_list_of_vecs(vl_list)?;

    // Guard: outer-length mismatch BEFORE from_lists (which would assert_eq! and panic)
    if av_vecs.len() != vl_vecs.len() {
        return Err(PyValueError::new_err(format!(
            "irreg_fdata_from_lists: argvals_list has {} curves but values_list has {} curves",
            av_vecs.len(),
            vl_vecs.len()
        )));
    }

    // Guard: per-curve length mismatch BEFORE from_lists
    for i in 0..av_vecs.len() {
        if av_vecs[i].len() != vl_vecs[i].len() {
            return Err(PyValueError::new_err(format!(
                "irreg_fdata_from_lists: curve {}: argvals has {} points but values has {} points",
                i,
                av_vecs[i].len(),
                vl_vecs[i].len()
            )));
        }
    }

    let inner = fdars_core::irreg_fdata::IrregFdata::from_lists(&av_vecs, &vl_vecs);
    Py::new(py, PyIrregFdata { inner })
}

// ---------------------------------------------------------------------------
// Full 10-key PaceFpcaResult converter
// ---------------------------------------------------------------------------

/// Convert PaceFpcaResult to a Python dict with all 10 keys.
///
/// `eigenfunctions` is shape (m, ncomp) — column k is the k-th eigenfunction;
/// `scores` is shape (n, ncomp). Both use `result.ncomp` (actual, may be <
/// config.ncomp) so shapes are always consistent with the returned `ncomp`.
fn pace_fpca_result_to_pydict<'py>(
    py: Python<'py>,
    r: fdars_core::pace_fpca::PaceFpcaResult,
) -> PyResult<Bound<'py, PyDict>> {
    let dict = PyDict::new(py);
    dict.set_item("mean", vec_to_numpy1d(py, r.mean))?;
    // eigenvalues length = r.ncomp (ACTUAL count, may be < config.ncomp)
    dict.set_item("eigenvalues", vec_to_numpy1d(py, r.eigenvalues))?;
    // eigenfunctions: FdMatrix nrows=m, ncols=ncomp → numpy (m, ncomp)
    // column k is the k-th eigenfunction; access as ef[:, k]
    dict.set_item("eigenfunctions", fdmatrix_to_numpy2d(py, &r.eigenfunctions))?;
    // scores: FdMatrix nrows=n, ncols=ncomp → numpy (n, ncomp)
    dict.set_item("scores", fdmatrix_to_numpy2d(py, &r.scores))?;
    // fitted trajectories on work grid: each (n, m)
    dict.set_item("fitted", fdmatrix_to_numpy2d(py, &r.fitted))?;
    dict.set_item("fitted_lower", fdmatrix_to_numpy2d(py, &r.fitted_lower))?;
    dict.set_item("fitted_upper", fdmatrix_to_numpy2d(py, &r.fitted_upper))?;
    // argvals = work grid echoed from config
    dict.set_item("argvals", vec_to_numpy1d(py, r.argvals))?;
    // sigma2: echoed from config (scalar)
    dict.set_item("sigma2", r.sigma2)?;
    // ncomp: ACTUAL components extracted (may be < requested config.ncomp)
    dict.set_item("ncomp", r.ncomp)?;
    Ok(dict)
}

// ---------------------------------------------------------------------------
// #[pyfunction] run_pace_fpca — exposed to Python as "pace_fpca"
// ---------------------------------------------------------------------------

/// Run PACE FPCA on irregular/sparse functional data.
///
/// Parameters
/// ----------
/// data : PyIrregFdata
///     Opaque handle from `irreg_fdata_from_lists`.
/// ncomp : int, optional
///     Number of components to extract (default 3).
/// bandwidth : float, optional
///     Kernel bandwidth for mean/covariance smoothing (default 0.1).
///     Use >= 0.15 for data on [0,1] with few points per curve.
/// sigma2 : float, optional
///     Measurement error variance (default 0.01).
/// work_grid : list of float, optional
///     Evaluation grid; defaults to 51 uniform points on [0, 1].
/// alpha : float, optional
///     Pointwise confidence level for fitted bands (default 0.05).
///
/// Returns
/// -------
/// dict
///     Keys: mean(m,), eigenvalues(ncomp,), eigenfunctions(m,ncomp),
///     scores(n,ncomp), fitted(n,m), fitted_lower(n,m), fitted_upper(n,m),
///     argvals(m,), sigma2(float), ncomp(int).
///     `ncomp` in the dict is the ACTUAL count extracted (may be < requested).
#[pyfunction(name = "pace_fpca")]
#[pyo3(signature = (data, ncomp=3, bandwidth=0.1, sigma2=0.01, work_grid=None, alpha=0.05))]
pub fn run_pace_fpca<'py>(
    py: Python<'py>,
    data: &PyIrregFdata,
    ncomp: usize,
    bandwidth: f64,
    sigma2: f64,
    work_grid: Option<Vec<f64>>,
    alpha: f64,
) -> PyResult<Bound<'py, PyDict>> {
    let config = fdars_core::pace_fpca::PaceFpcaConfig {
        ncomp,
        bandwidth,
        sigma2,
        // Default: 51 uniform points on [0, 1] matching core PaceFpcaConfig::default()
        work_grid: work_grid.unwrap_or_else(|| (0..51).map(|i| i as f64 / 50.0).collect()),
        alpha,
    };
    let result = to_pyresult(fdars_core::pace_fpca::pace_fpca(&data.inner, &config))?;
    pace_fpca_result_to_pydict(py, result)
}

// ---------------------------------------------------------------------------
// Module registration
// ---------------------------------------------------------------------------

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyIrregFdata>()?;
    m.add_function(wrap_pyfunction!(irreg_fdata_from_lists, m)?)?;
    m.add_function(wrap_pyfunction!(run_pace_fpca, m)?)?;
    Ok(())
}
