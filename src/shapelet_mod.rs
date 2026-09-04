//! Shapelet discovery, transform, and classification for pyfda (SHAPE-01).
//!
//! Exposes the `fdars.shapelet` submodule with bindings for:
//! - `discover_shapelets` → summary dict `{n_shapelets, quality}`
//! - `shapelet_transform_fit` → `PyShapeletFit` opaque handle
//! - `shapelet_transform` → 2D numpy array (n_new, K)
//! - `shapelet_classifier_fit` → `PyShapeletClassifierFit` opaque handle
//! - `shapelet_distance` → `(float, int)` tuple
//!
//! Two `#[non_exhaustive]` enums are dispatched by string with mandatory Err arms:
//! - `QualityMeasure`: `"info_gain"` | `"f_statistic"`
//! - `ShapeletClassifier`: `"knn"` (+ k param) | `"lda"`
//!
//! Phase 71, Plan 01 (SHAPE-01).

use crate::convert::{fdmatrix_to_numpy2d, numpy2d_to_fdmatrix, to_pyresult, usize_vec_to_numpy1d};
use fdars_core::shapelet::{
    ShapeletClassifier, ShapeletClassifierConfig, ShapeletClassifierFit, ShapeletDiscoveryConfig,
    ShapeletTransformFit, QualityMeasure,
};
use numpy::{PyArray1, PyArray2, PyReadonlyArray1, PyReadonlyArray2};
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::PyDict;

// ---------------------------------------------------------------------------
// Private helpers: enum string dispatch (mandatory Err arms for #[non_exhaustive])
// ---------------------------------------------------------------------------

/// Parse quality measure string. Both variants listed in Err message (RESEARCH 3.1).
fn quality_from_str(s: &str) -> PyResult<QualityMeasure> {
    match s {
        "info_gain" => Ok(QualityMeasure::InfoGain),
        "f_statistic" => Ok(QualityMeasure::FStatistic),
        _ => Err(PyValueError::new_err(format!(
            "quality must be 'info_gain' or 'f_statistic', got '{s}'"
        ))),
    }
}

/// Parse classifier string. k is only used for "knn"; Lda is unit variant (RESEARCH 3.2, Pitfall 4).
fn classifier_from_str(classifier: &str, k: usize) -> PyResult<ShapeletClassifier> {
    match classifier {
        "knn" => {
            if k == 0 {
                return Err(PyValueError::new_err(
                    "k must be >= 1 for the 'knn' classifier",
                ));
            }
            Ok(ShapeletClassifier::Knn { k })
        }
        "lda" => Ok(ShapeletClassifier::Lda),
        _ => Err(PyValueError::new_err(format!(
            "classifier must be 'knn' or 'lda', got '{classifier}'"
        ))),
    }
}

/// Convert Python i64 label array to Vec<usize>, guarding against negative values (RESEARCH Pitfall 5).
fn labels_i64_to_usize(labels: PyReadonlyArray1<'_, i64>) -> PyResult<Vec<usize>> {
    labels
        .as_array()
        .iter()
        .enumerate()
        .map(|(i, &v)| {
            if v < 0 {
                Err(PyValueError::new_err(format!(
                    "labels[{i}] = {v} is negative; labels must be non-negative integers"
                )))
            } else {
                Ok(v as usize)
            }
        })
        .collect()
}

/// Map Python max_candidates sentinel: 0 → None (exhaustive), N → Some(N) (RESEARCH Pitfall 6).
fn max_candidates_opt(max_candidates: usize) -> Option<usize> {
    if max_candidates == 0 {
        None
    } else {
        Some(max_candidates)
    }
}

// ---------------------------------------------------------------------------
// Opaque #[pyclass] handles
// ---------------------------------------------------------------------------

/// Opaque handle wrapping fdars-core ShapeletTransformFit.
///
/// Returned by `shapelet_transform_fit`. Pass to `shapelet_transform` to apply
/// the fitted shapelet transform to new data.
#[pyclass(name = "PyShapeletFit")]
pub struct PyShapeletFit {
    pub inner: ShapeletTransformFit,
}

#[pymethods]
impl PyShapeletFit {
    /// Number of shapelets discovered during fitting.
    #[getter]
    pub fn n_shapelets(&self) -> usize {
        self.inner.shapelets().len()
    }

    /// Number of training observations used to fit the transform.
    #[getter]
    pub fn n_train(&self) -> usize {
        self.inner.features().nrows()
    }
}

/// Opaque handle wrapping fdars-core ShapeletClassifierFit.
///
/// Returned by `shapelet_classifier_fit`. Exposes `predict`, `train_accuracy`,
/// `classes`, `n_classes`, and `n_shapelets`.
#[pyclass(name = "PyShapeletClassifierFit")]
pub struct PyShapeletClassifierFit {
    pub inner: ShapeletClassifierFit,
}

#[pymethods]
impl PyShapeletClassifierFit {
    /// Number of shapelets discovered during fitting.
    #[getter]
    pub fn n_shapelets(&self) -> usize {
        self.inner.shapelets().len()
    }

    /// Training-set accuracy. Not a generalization estimate.
    #[getter]
    pub fn train_accuracy(&self) -> f64 {
        self.inner.train_accuracy()
    }

    /// Sorted unique original class labels as a 1D int64 numpy array.
    #[getter]
    pub fn classes<'py>(&self, py: Python<'py>) -> Bound<'py, PyArray1<i64>> {
        let v: Vec<usize> = self.inner.classes.clone();
        usize_vec_to_numpy1d(py, v)
    }

    /// Number of distinct classes.
    #[getter]
    pub fn n_classes(&self) -> usize {
        self.inner.classes.len()
    }

    /// Predict class labels for new data.
    ///
    /// Parameters
    /// ----------
    /// new_data : ndarray, shape (n_new, n_points)
    ///     New observations to classify.
    ///
    /// Returns
    /// -------
    /// ndarray, shape (n_new,), dtype int64
    ///     Predicted class labels.
    pub fn predict<'py>(
        &self,
        py: Python<'py>,
        new_data: PyReadonlyArray2<'py, f64>,
    ) -> PyResult<Bound<'py, PyArray1<i64>>> {
        let mat = numpy2d_to_fdmatrix(new_data)?;
        let labels_usize = to_pyresult(self.inner.predict(&mat))?;
        Ok(usize_vec_to_numpy1d(py, labels_usize))
    }
}

// ---------------------------------------------------------------------------
// #[pyfunction] discover_shapelets
// ---------------------------------------------------------------------------

/// Discover shapelets in labeled functional data and return a summary dict.
///
/// Returns a dict with keys:
/// - `n_shapelets` (int): number of shapelets discovered
/// - `quality` (str): quality measure used (`"info_gain"` or `"f_statistic"`)
///
/// Parameters
/// ----------
/// data : ndarray, shape (n_obs, n_points)
///     Functional data matrix (one curve per row).
/// labels : ndarray, shape (n_obs,), dtype int64
///     Integer class label for each observation. Must have ≥ 2 distinct values.
/// min_length : int, optional
///     Minimum shapelet length. Default 3.
/// max_length : int, optional
///     Maximum shapelet length. 0 = series length. Default 0.
/// max_candidates : int, optional
///     Maximum candidate shapelets to evaluate. 0 = exhaustive. Default 10000.
/// max_shapelets : int, optional
///     Maximum shapelets to retain. 0 = min(10*n, 1000). Default 0.
/// quality : str, optional
///     Quality measure: `"info_gain"` or `"f_statistic"`. Default `"info_gain"`.
/// seed : int, optional
///     RNG seed for reproducibility. Default 0.
///
/// Returns
/// -------
/// dict
///     `{n_shapelets: int, quality: str}`
///
/// Raises
/// ------
/// ValueError
///     If `quality` is not a recognised variant, labels contain negative values,
///     or the data/label dimensions are inconsistent.
#[pyfunction]
#[pyo3(signature = (data, labels, min_length=3, max_length=0, max_candidates=10000,
                    max_shapelets=0, quality="info_gain", seed=0))]
pub fn discover_shapelets<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    labels: PyReadonlyArray1<'py, i64>,
    min_length: usize,
    max_length: usize,
    max_candidates: usize,
    max_shapelets: usize,
    quality: &str,
    seed: u64,
) -> PyResult<Bound<'py, PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let label_vec = labels_i64_to_usize(labels)?;
    let quality_measure = quality_from_str(quality)?;
    let quality_str = quality.to_string();

    let config = ShapeletDiscoveryConfig {
        min_length,
        max_length,
        max_candidates: max_candidates_opt(max_candidates),
        max_shapelets,
        quality: quality_measure,
        seed,
    };

    let set = to_pyresult(fdars_core::shapelet::discover_shapelets(&mat, &label_vec, &config))?;

    let dict = PyDict::new(py);
    dict.set_item("n_shapelets", set.len())?;
    dict.set_item("quality", &quality_str)?;
    Ok(dict)
}

// ---------------------------------------------------------------------------
// #[pyfunction] shapelet_transform_fit → PyShapeletFit
// ---------------------------------------------------------------------------

/// Fit a shapelet transform on labeled functional data.
///
/// Discovers shapelets and computes the (n_train, K) training feature matrix.
/// Returns a `PyShapeletFit` opaque handle. Pass to `shapelet_transform` to
/// transform new data.
///
/// Parameters
/// ----------
/// data : ndarray, shape (n_obs, n_points)
///     Training functional data matrix.
/// labels : ndarray, shape (n_obs,), dtype int64
///     Integer class labels (≥ 2 distinct values required).
/// min_length, max_length, max_candidates, max_shapelets, quality, seed
///     See `discover_shapelets` for documentation.
///
/// Returns
/// -------
/// PyShapeletFit
///     Opaque handle with `n_shapelets` and `n_train` accessors.
///
/// Raises
/// ------
/// ValueError
///     On invalid parameters or insufficient data.
#[pyfunction]
#[pyo3(signature = (data, labels, min_length=3, max_length=0, max_candidates=10000,
                    max_shapelets=0, quality="info_gain", seed=0))]
pub fn shapelet_transform_fit<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    labels: PyReadonlyArray1<'py, i64>,
    min_length: usize,
    max_length: usize,
    max_candidates: usize,
    max_shapelets: usize,
    quality: &str,
    seed: u64,
) -> PyResult<Py<PyShapeletFit>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let label_vec = labels_i64_to_usize(labels)?;
    let quality_measure = quality_from_str(quality)?;

    let config = ShapeletDiscoveryConfig {
        min_length,
        max_length,
        max_candidates: max_candidates_opt(max_candidates),
        max_shapelets,
        quality: quality_measure,
        seed,
    };

    let fit = to_pyresult(fdars_core::shapelet::shapelet_transform_fit(
        &mat, &label_vec, &config,
    ))?;

    Py::new(py, PyShapeletFit { inner: fit })
}

// ---------------------------------------------------------------------------
// #[pyfunction] shapelet_transform
// ---------------------------------------------------------------------------

/// Apply a fitted shapelet transform to new functional data.
///
/// Uses the shapelet set stored in `fit` to compute per-shapelet distances
/// for each curve in `data`.
///
/// Parameters
/// ----------
/// fit : PyShapeletFit
///     Handle returned by `shapelet_transform_fit`.
/// data : ndarray, shape (n_new, n_points)
///     New functional data to transform (may differ in row count from training set).
///
/// Returns
/// -------
/// ndarray, shape (n_new, K), dtype float64
///     Shapelet distance feature matrix. K = `fit.n_shapelets`.
///
/// Raises
/// ------
/// ValueError
///     If evaluation-grid width mismatches the training set or data is malformed.
#[pyfunction]
pub fn shapelet_transform<'py>(
    py: Python<'py>,
    fit: &PyShapeletFit,
    data: PyReadonlyArray2<'py, f64>,
) -> PyResult<Bound<'py, PyArray2<f64>>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    // RESEARCH Pitfall 1: call fit.inner.shapelets() to get &ShapeletSet, NOT fit.inner directly.
    let feature_mat = to_pyresult(fdars_core::shapelet::shapelet_transform(
        fit.inner.shapelets(),
        &mat,
    ))?;
    Ok(fdmatrix_to_numpy2d(py, &feature_mat))
}

// ---------------------------------------------------------------------------
// #[pyfunction] shapelet_classifier_fit → PyShapeletClassifierFit
// ---------------------------------------------------------------------------

/// Fit a shapelet-based classifier on labeled functional data.
///
/// Discovers shapelets, computes feature matrix, then fits an inner classifier.
/// Returns a `PyShapeletClassifierFit` opaque handle with `predict` and
/// `train_accuracy` methods.
///
/// Parameters
/// ----------
/// data : ndarray, shape (n_obs, n_points)
///     Training functional data matrix.
/// labels : ndarray, shape (n_obs,), dtype int64
///     Integer class labels (≥ 2 distinct values required).
/// min_length, max_length, max_candidates, max_shapelets, quality, seed
///     Shapelet discovery parameters (see `discover_shapelets`).
/// classifier : str, optional
///     Inner classifier: `"knn"` (default) or `"lda"`.
/// k : int, optional
///     Number of nearest neighbours for the `"knn"` classifier. Default 1.
/// ncomp : int or None, optional
///     Number of PCA components to reduce features before classification.
///     None = no reduction (use all K shapelet features). Default None.
///
/// Returns
/// -------
/// PyShapeletClassifierFit
///     Opaque handle exposing `n_shapelets`, `train_accuracy`, `classes`,
///     `n_classes`, and `predict(new_data)`.
///
/// Raises
/// ------
/// ValueError
///     On invalid parameters, invalid classifier name, or insufficient data.
#[pyfunction]
#[pyo3(signature = (data, labels, min_length=3, max_length=0, max_candidates=10000,
                    max_shapelets=0, quality="info_gain", seed=0,
                    classifier="knn", k=1, ncomp=None))]
pub fn shapelet_classifier_fit<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    labels: PyReadonlyArray1<'py, i64>,
    min_length: usize,
    max_length: usize,
    max_candidates: usize,
    max_shapelets: usize,
    quality: &str,
    seed: u64,
    classifier: &str,
    k: usize,
    ncomp: Option<usize>,
) -> PyResult<Py<PyShapeletClassifierFit>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let label_vec = labels_i64_to_usize(labels)?;
    let quality_measure = quality_from_str(quality)?;
    let classifier_variant = classifier_from_str(classifier, k)?;

    let discovery = ShapeletDiscoveryConfig {
        min_length,
        max_length,
        max_candidates: max_candidates_opt(max_candidates),
        max_shapelets,
        quality: quality_measure,
        seed,
    };

    let config = ShapeletClassifierConfig {
        discovery,
        classifier: classifier_variant,
        ncomp,
    };

    let fit = to_pyresult(fdars_core::shapelet::shapelet_classifier_fit(
        &mat, &label_vec, &config,
    ))?;

    Py::new(py, PyShapeletClassifierFit { inner: fit })
}

// ---------------------------------------------------------------------------
// #[pyfunction] shapelet_distance
// ---------------------------------------------------------------------------

/// Compute the shapelet distance between a z-normalized shapelet and a series.
///
/// Uses early abandonment and per-window z-normalization internally.
///
/// Parameters
/// ----------
/// shapelet_z : ndarray, shape (L,), dtype float64
///     Pre-z-normalized shapelet subsequence values (length L).
/// series : ndarray, shape (m,), dtype float64
///     Raw series. Must have m ≥ L. Per-window z-normalization is done internally.
/// best_so_far : float, optional
///     Early-abandon bound. Pass `float('inf')` (default) to disable.
///
/// Returns
/// -------
/// tuple of (float, int)
///     `(min_distance, best_offset)` — minimum distance and corresponding start index.
///
/// Raises
/// ------
/// ValueError
///     If series is shorter than the shapelet, or other dimension errors.
#[pyfunction]
#[pyo3(signature = (shapelet_z, series, best_so_far=f64::INFINITY))]
pub fn shapelet_distance(
    shapelet_z: PyReadonlyArray1<'_, f64>,
    series: PyReadonlyArray1<'_, f64>,
    best_so_far: f64,
) -> PyResult<(f64, usize)> {
    let sz: Vec<f64> = shapelet_z.as_array().to_vec();
    let sv: Vec<f64> = series.as_array().to_vec();
    to_pyresult(fdars_core::shapelet::shapelet_distance(&sz, &sv, best_so_far))
}

// ---------------------------------------------------------------------------
// Module registration
// ---------------------------------------------------------------------------

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyShapeletFit>()?;
    m.add_class::<PyShapeletClassifierFit>()?;
    m.add_function(wrap_pyfunction!(discover_shapelets, m)?)?;
    m.add_function(wrap_pyfunction!(shapelet_transform_fit, m)?)?;
    m.add_function(wrap_pyfunction!(shapelet_transform, m)?)?;
    m.add_function(wrap_pyfunction!(shapelet_classifier_fit, m)?)?;
    m.add_function(wrap_pyfunction!(shapelet_distance, m)?)?;
    Ok(())
}
