//! Density functional data analysis: LQD transform, Wasserstein barycenter, density FPCA (FRE-02).
//!
//! Exposes the `fdars.density_fda` submodule with bindings for fdars-core 0.33's
//! density_fda module.
//!
//! Plan 69-04 (tracer): `normalize_density` bound; submodule registered end-to-end.
//! Plan 69-04 expanded: `lqd_transform`, `inverse_lqd`, `wasserstein_barycenter`, `lqd_fpca` added.

use crate::convert::{
    fdmatrix_to_numpy2d, numpy1d_to_vec, numpy2d_to_fdmatrix, to_pyresult, vec_to_numpy1d,
};
use numpy::{PyReadonlyArray1, PyReadonlyArray2};
use pyo3::prelude::*;
use pyo3::types::PyDict;

// ---------------------------------------------------------------------------
// normalize_density — normalize a density function to integrate to 1
// ---------------------------------------------------------------------------

/// Normalize a density function to integrate to 1.
///
/// Parameters
/// ----------
/// vals : numpy.ndarray
///     Non-negative density values, shape (m,).
/// argvals : numpy.ndarray
///     Strictly increasing evaluation grid, length m (at least 2).
///
/// Returns
/// -------
/// numpy.ndarray
///     Normalized density values, shape (m,), integrating to 1.
///
/// Raises
/// ------
/// ValueError
///     If vals and argvals have different lengths, argvals has fewer than 2 points,
///     argvals is not strictly increasing, any value is negative, or the integral is
///     effectively zero.
#[pyfunction]
#[pyo3(signature = (vals, argvals))]
fn normalize_density<'py>(
    py: Python<'py>,
    vals: PyReadonlyArray1<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
) -> PyResult<Bound<'py, numpy::PyArray1<f64>>> {
    let vals_vec = numpy1d_to_vec(vals);
    let argvals_vec = numpy1d_to_vec(argvals);
    let result = to_pyresult(fdars_core::density_fda::normalize_density(
        &vals_vec,
        &argvals_vec,
    ))?;
    Ok(vec_to_numpy1d(py, result))
}

// ---------------------------------------------------------------------------
// lqd_transform — log-quantile density (LQD) transform
// ---------------------------------------------------------------------------

/// Compute the log-quantile density (LQD) transform of a density function.
///
/// The LQD transform embeds a density into L²([0,1]) via the log of its quantile
/// density function (the derivative of the quantile function). This enables linear
/// functional data analysis of density observations.
///
/// **Important:** The density must be STRICTLY positive (> 0 everywhere). This is
/// stricter than `normalize_density`, which only requires non-negative values.
/// If the density has zero values (e.g., zero tails), add a small epsilon before
/// calling this function.
///
/// Parameters
/// ----------
/// density : numpy.ndarray
///     Strictly positive density values, shape (m,).
/// argvals : numpy.ndarray
///     Strictly increasing evaluation grid, length m.
/// n_quantile_pts : int, optional
///     Number of points in the uniform quantile grid. Default: max(m, 101).
///
/// Returns
/// -------
/// numpy.ndarray
///     LQD transform values (ψ) on the uniform quantile grid, shape (n_q,).
///
/// Raises
/// ------
/// ValueError
///     If density is not strictly positive, argvals is not strictly increasing, or
///     array lengths are inconsistent.
#[pyfunction]
#[pyo3(signature = (density, argvals, n_quantile_pts=None))]
fn lqd_transform<'py>(
    py: Python<'py>,
    density: PyReadonlyArray1<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    n_quantile_pts: Option<usize>,
) -> PyResult<Bound<'py, numpy::PyArray1<f64>>> {
    let density_vec = numpy1d_to_vec(density);
    let argvals_vec = numpy1d_to_vec(argvals);
    let result = to_pyresult(fdars_core::density_fda::lqd_transform(
        &density_vec,
        &argvals_vec,
        n_quantile_pts,
    ))?;
    Ok(vec_to_numpy1d(py, result))
}

// ---------------------------------------------------------------------------
// inverse_lqd — inverse LQD transform
// ---------------------------------------------------------------------------

/// Compute the inverse LQD transform: reconstruct a density from its LQD representation.
///
/// Parameters
/// ----------
/// psi : numpy.ndarray
///     LQD transform values, shape (n_q,).
/// t_grid : numpy.ndarray
///     Uniform quantile grid on [0, 1] corresponding to psi, shape (n_q,).
/// target_argvals : numpy.ndarray
///     Target evaluation grid for the reconstructed density, shape (m,).
///
/// Returns
/// -------
/// numpy.ndarray
///     Reconstructed density values on target_argvals, shape (m,).
///
/// Raises
/// ------
/// ValueError
///     If array lengths are inconsistent or t_grid is not in [0, 1].
#[pyfunction]
#[pyo3(signature = (psi, t_grid, target_argvals))]
fn inverse_lqd<'py>(
    py: Python<'py>,
    psi: PyReadonlyArray1<'py, f64>,
    t_grid: PyReadonlyArray1<'py, f64>,
    target_argvals: PyReadonlyArray1<'py, f64>,
) -> PyResult<Bound<'py, numpy::PyArray1<f64>>> {
    let psi_vec = numpy1d_to_vec(psi);
    let t_grid_vec = numpy1d_to_vec(t_grid);
    let target_vec = numpy1d_to_vec(target_argvals);
    let result = to_pyresult(fdars_core::density_fda::inverse_lqd(
        &psi_vec,
        &t_grid_vec,
        &target_vec,
    ))?;
    Ok(vec_to_numpy1d(py, result))
}

// ---------------------------------------------------------------------------
// wasserstein_barycenter — Wasserstein Fréchet mean of densities
// ---------------------------------------------------------------------------

/// Compute the Wasserstein Fréchet mean (barycenter) of a collection of densities.
///
/// Parameters
/// ----------
/// density_matrix : numpy.ndarray
///     Density observations, shape (n, m) — n densities on m grid points.
///     Each row must be a valid probability density (non-negative, integrating to 1).
/// argvals : numpy.ndarray
///     Strictly increasing evaluation grid, length m.
/// weights : numpy.ndarray, optional
///     Non-negative weights for each density, length n, summing to 1.
///     Default: uniform weights (1/n each).
///
/// Returns
/// -------
/// numpy.ndarray
///     Wasserstein barycenter density, shape (m,), integrating to ~1.
///
/// Raises
/// ------
/// ValueError
///     If density_matrix shape is inconsistent with argvals, weights are negative,
///     or weights do not sum to 1.
#[pyfunction]
#[pyo3(signature = (density_matrix, argvals, weights=None))]
fn wasserstein_barycenter<'py>(
    py: Python<'py>,
    density_matrix: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    weights: Option<PyReadonlyArray1<'py, f64>>,
) -> PyResult<Bound<'py, numpy::PyArray1<f64>>> {
    let mat = numpy2d_to_fdmatrix(density_matrix)?;
    let argvals_vec = numpy1d_to_vec(argvals);
    let weights_vec: Option<Vec<f64>> = weights.map(numpy1d_to_vec);
    let weights_ref: Option<&[f64]> = weights_vec.as_deref();
    let result = to_pyresult(fdars_core::density_fda::wasserstein_barycenter(
        &mat,
        &argvals_vec,
        weights_ref,
    ))?;
    Ok(vec_to_numpy1d(py, result))
}

// ---------------------------------------------------------------------------
// lqd_fpca — Functional PCA in LQD space
// ---------------------------------------------------------------------------

/// Functional PCA of densities via the LQD transform.
///
/// Applies the LQD transform to each density, then performs FPCA in L²([0,1]).
/// Returns the principal components (loadings), scores, and fraction of variance
/// explained in the LQD representation space.
///
/// Parameters
/// ----------
/// density_matrix : numpy.ndarray
///     Density observations, shape (n, m) — n densities on m grid points.
///     Each row must be a strictly positive density.
/// argvals : numpy.ndarray
///     Strictly increasing evaluation grid, length m.
/// ncomp : int, optional
///     Number of principal components to retain. Default: 3.
/// n_quantile_pts : int, optional
///     Number of quantile grid points for the LQD transform. Default: max(m, 101).
///
/// Returns
/// -------
/// dict
///     mean (array, shape (n_q,)): mean LQD function.
///     singular_values (array, shape (k,)): singular values of the LQD matrix.
///     loadings (array, shape (n_q, k)): principal component loadings (rotation matrix).
///     scores (array, shape (n, k)): FPCA scores for each observation.
///     fve (array, shape (k,)): fraction of variance explained, cumulative.
///     ncomp (int): actual number of retained components k.
///
/// Raises
/// ------
/// ValueError
///     If density_matrix contains non-strictly-positive values, ncomp exceeds the
///     rank, or array dimensions are inconsistent.
#[pyfunction]
#[pyo3(signature = (density_matrix, argvals, ncomp=3, n_quantile_pts=None))]
fn lqd_fpca<'py>(
    py: Python<'py>,
    density_matrix: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    ncomp: usize,
    n_quantile_pts: Option<usize>,
) -> PyResult<Bound<'py, PyDict>> {
    let mat = numpy2d_to_fdmatrix(density_matrix)?;
    let argvals_vec = numpy1d_to_vec(argvals);
    let result = to_pyresult(fdars_core::density_fda::lqd_fpca(
        &mat,
        &argvals_vec,
        ncomp,
        n_quantile_pts,
    ))?;

    let dict = PyDict::new(py);
    dict.set_item("mean", vec_to_numpy1d(py, result.fpca.mean))?;
    dict.set_item(
        "singular_values",
        vec_to_numpy1d(py, result.fpca.singular_values),
    )?;
    dict.set_item(
        "loadings",
        fdmatrix_to_numpy2d(py, &result.fpca.rotation),
    )?;
    dict.set_item("scores", fdmatrix_to_numpy2d(py, &result.fpca.scores))?;
    dict.set_item("fve", vec_to_numpy1d(py, result.fve))?;
    dict.set_item("ncomp", result.fpca.scores.ncols() as i64)?;
    Ok(dict)
}

// ---------------------------------------------------------------------------
// Registration
// ---------------------------------------------------------------------------

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(normalize_density, m)?)?;
    m.add_function(wrap_pyfunction!(lqd_transform, m)?)?;
    m.add_function(wrap_pyfunction!(inverse_lqd, m)?)?;
    m.add_function(wrap_pyfunction!(wasserstein_barycenter, m)?)?;
    m.add_function(wrap_pyfunction!(lqd_fpca, m)?)?;
    Ok(())
}
