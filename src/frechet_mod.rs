//! Fréchet regression and Fréchet mean over metric spaces (FRE-01).
//!
//! Exposes the `fdars.frechet` submodule with bindings for fdars-core 0.33's
//! frechet module: Fréchet ANOVA test, global and local density regression.
//!
//! Plan 69-02 (tracer): `frechet_anova` bound; submodule registered end-to-end.
//! Plan 69-02 expanded: `frechet_global_reg`, `frechet_local_reg` added.
//! Plan 69-03: `frechet_mean` (generic dispatch) added.

use crate::convert::{
    fdmatrix_to_numpy2d, numpy1d_to_vec, numpy2d_to_fdmatrix, to_pyresult,
    usize_vec_to_numpy1d, vec_to_numpy1d,
};
use numpy::{PyReadonlyArray1, PyReadonlyArray2};
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::PyDict;

// ---------------------------------------------------------------------------
// frechet_anova — Fréchet ANOVA test for equality of Fréchet means across groups
// ---------------------------------------------------------------------------

/// Fréchet ANOVA: test equality of Fréchet means across groups.
///
/// Uses the Dubey–Müller permutation test on density-response functional data.
/// Group labels must be contiguous integers starting at 0 (i.e., 0, 1, …, k-1).
///
/// Parameters
/// ----------
/// responses : numpy.ndarray
///     Density responses, shape (n, m) — n observations on m grid points.
/// argvals : numpy.ndarray
///     Strictly increasing evaluation grid, length m.
/// group_labels : numpy.ndarray
///     Group membership for each observation, length n.
///     Labels must be contiguous integers starting at 0.
/// n_perm : int, optional
///     Number of permutations for the permutation p-value. Default 999.
/// seed : int, optional
///     RNG seed for reproducible permutation p-value. Default 42.
///
/// Returns
/// -------
/// dict
///     statistic (float), p_value_asymptotic (float), p_value_permutation (float),
///     n_perm (int), group_frechet_variances (array, shape (k,)),
///     pooled_frechet_variance (float), fn_statistic (float), un_statistic (float),
///     group_labels (array, shape (n,) i64).
///
/// Raises
/// ------
/// ValueError
///     If group labels are not contiguous 0..k, dimensions are inconsistent,
///     or fewer than 2 distinct groups are present.
#[pyfunction]
#[pyo3(signature = (responses, argvals, group_labels, n_perm=999, seed=42))]
pub fn frechet_anova<'py>(
    py: Python<'py>,
    responses: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    group_labels: PyReadonlyArray1<'py, i64>,
    n_perm: usize,
    seed: u64,
) -> PyResult<Bound<'py, PyAny>> {
    let resp_mat = numpy2d_to_fdmatrix(responses)?;
    let av = numpy1d_to_vec(argvals);
    let labels = crate::convert::numpy1d_to_usize_vec(group_labels);

    // Pre-validate: group labels must be contiguous 0..k (Pitfall 4).
    {
        let mut sorted = labels.clone();
        sorted.sort_unstable();
        sorted.dedup();
        let k = sorted.len();
        let contiguous = sorted.iter().enumerate().all(|(i, &v)| v == i);
        if !contiguous || k == 0 {
            return Err(PyValueError::new_err(format!(
                "frechet_anova: group_labels must be contiguous integers starting at 0 \
                 (i.e., 0, 1, …, {max}); got labels {sorted:?}",
                max = k.saturating_sub(1)
            )));
        }
    }

    let result = to_pyresult(fdars_core::frechet::frechet_anova(
        &resp_mat, &av, &labels, n_perm, seed,
    ))?;

    let dict = PyDict::new(py);
    dict.set_item("statistic", result.statistic)?;
    dict.set_item("p_value_asymptotic", result.p_value_asymptotic)?;
    dict.set_item("p_value_permutation", result.p_value_permutation)?;
    dict.set_item("n_perm", result.n_perm as i64)?;
    dict.set_item(
        "group_frechet_variances",
        vec_to_numpy1d(py, result.group_frechet_variances),
    )?;
    dict.set_item("pooled_frechet_variance", result.pooled_frechet_variance)?;
    dict.set_item("fn_statistic", result.fn_statistic)?;
    dict.set_item("un_statistic", result.un_statistic)?;
    dict.set_item(
        "group_labels",
        usize_vec_to_numpy1d(py, result.group_labels),
    )?;
    Ok(dict.into_any())
}

// ---------------------------------------------------------------------------
// frechet_global_reg — Global Fréchet linear regression (density responses)
// ---------------------------------------------------------------------------

/// Global Fréchet linear regression for density-response functional data.
///
/// Fits a global linear model via signed-weight quantile averaging (Petersen–Müller
/// regression). Note: this is NOT equivalent to Wasserstein barycenter averaging
/// because Petersen–Müller regression weights can be negative (extrapolation case).
///
/// Parameters
/// ----------
/// predictors : numpy.ndarray
///     Scalar predictor matrix, shape (n, p).
/// responses : numpy.ndarray
///     Density response matrix, shape (n, m) — n observations on m grid points.
/// argvals : numpy.ndarray
///     Strictly increasing evaluation grid, length m.
/// xout : numpy.ndarray
///     Predictor values at which to predict, shape (n_out, p).
///
/// Returns
/// -------
/// dict
///     predicted (numpy 2D, shape (n_out, m)), xout (numpy 2D, shape (n_out, p)),
///     x_bar (numpy 1D, shape (p,)).
///
/// Raises
/// ------
/// ValueError
///     If dimensions are inconsistent, argvals is not strictly increasing,
///     or predictor/xout column counts differ.
#[pyfunction]
pub fn frechet_global_reg<'py>(
    py: Python<'py>,
    predictors: PyReadonlyArray2<'py, f64>,
    responses: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    xout: PyReadonlyArray2<'py, f64>,
) -> PyResult<Bound<'py, PyAny>> {
    let pred_mat = numpy2d_to_fdmatrix(predictors)?;
    let resp_mat = numpy2d_to_fdmatrix(responses)?;
    let av = numpy1d_to_vec(argvals);
    let xout_mat = numpy2d_to_fdmatrix(xout)?;

    let result = to_pyresult(fdars_core::frechet::frechet_global_reg(
        &pred_mat, &resp_mat, &av, &xout_mat,
    ))?;

    let dict = PyDict::new(py);
    // result.predicted is (n_out × m) FdMatrix — fdmatrix_to_numpy2d gives (n_out, m)
    dict.set_item("predicted", fdmatrix_to_numpy2d(py, &result.predicted))?;
    dict.set_item("xout", fdmatrix_to_numpy2d(py, &result.xout))?;
    dict.set_item("x_bar", vec_to_numpy1d(py, result.x_bar))?;
    Ok(dict.into_any())
}

// ---------------------------------------------------------------------------
// frechet_local_reg — Local Fréchet regression (density responses, kernel smoothing)
// ---------------------------------------------------------------------------

/// Local Fréchet regression for density-response functional data.
///
/// Fits a local (kernel-smoothed) Fréchet regression model via signed-weight
/// quantile averaging. The bandwidth controls the locality of the regression.
/// Uses the same signed-weight isotonic projection as `frechet_global_reg`
/// (NOT Wasserstein barycenter) because weights can be negative.
///
/// Parameters
/// ----------
/// predictors : numpy.ndarray
///     Scalar predictor matrix, shape (n, p).
/// responses : numpy.ndarray
///     Density response matrix, shape (n, m) — n observations on m grid points.
/// argvals : numpy.ndarray
///     Strictly increasing evaluation grid, length m.
/// xout : numpy.ndarray
///     Predictor values at which to predict, shape (n_out, p).
/// bandwidth : float
///     Kernel bandwidth. Must be positive and finite. No default — choose
///     based on the scale of your predictor data.
///
/// Returns
/// -------
/// dict
///     predicted (numpy 2D, shape (n_out, m)), xout (numpy 2D, shape (n_out, p)),
///     bandwidth (float — echoes the input bandwidth).
///
/// Raises
/// ------
/// ValueError
///     If bandwidth <= 0, dimensions are inconsistent, or argvals not strictly increasing.
#[pyfunction]
pub fn frechet_local_reg<'py>(
    py: Python<'py>,
    predictors: PyReadonlyArray2<'py, f64>,
    responses: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    xout: PyReadonlyArray2<'py, f64>,
    bandwidth: f64,
) -> PyResult<Bound<'py, PyAny>> {
    let pred_mat = numpy2d_to_fdmatrix(predictors)?;
    let resp_mat = numpy2d_to_fdmatrix(responses)?;
    let av = numpy1d_to_vec(argvals);
    let xout_mat = numpy2d_to_fdmatrix(xout)?;

    let result = to_pyresult(fdars_core::frechet::frechet_local_reg(
        &pred_mat, &resp_mat, &av, &xout_mat, bandwidth,
    ))?;

    let dict = PyDict::new(py);
    dict.set_item("predicted", fdmatrix_to_numpy2d(py, &result.predicted))?;
    dict.set_item("xout", fdmatrix_to_numpy2d(py, &result.xout))?;
    dict.set_item("bandwidth", result.bandwidth)?;
    Ok(dict.into_any())
}

// ---------------------------------------------------------------------------
// Module registration
// ---------------------------------------------------------------------------

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(frechet_anova, m)?)?;
    m.add_function(wrap_pyfunction!(frechet_global_reg, m)?)?;
    m.add_function(wrap_pyfunction!(frechet_local_reg, m)?)?;
    Ok(())
}
