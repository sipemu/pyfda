//! Prediction-scoring metrics for functional data (fdars.scoring submodule).
//!
//! Exposes the 5 fdars-core 0.17.0 Simpson-integrated scalar metrics for scoring
//! predicted-vs-true functional curves. Each metric integrates the pointwise error
//! function over `argvals` and averages over all curves.
//!
//! Fallible inputs (MAPE: near-zero true values; MSLE: values ≤ −1) surface as
//! Python `ValueError` via `to_pyresult()` — no `.unwrap()` on any `Result`.

use crate::convert::*;
use numpy::{PyReadonlyArray1, PyReadonlyArray2};
use pyo3::prelude::*;

/// Functional Mean Absolute Error integrated over `argvals`.
///
/// Parameters
/// ----------
/// y_true : numpy.ndarray
///     True functional data matrix, shape (n, m). Rows are observations.
/// y_pred : numpy.ndarray
///     Predicted functional data matrix, shape (n, m). Must match `y_true` shape.
/// argvals : numpy.ndarray
///     Evaluation points, length m. Must be sorted.
///
/// Returns
/// -------
/// float
///     ``(1/n) * sum_i ∫ |y_true_i(t) - y_pred_i(t)| dt`` approximated by
///     Simpson's rule.
///
/// Raises
/// ------
/// ValueError
///     If shapes of `y_true`, `y_pred`, or `argvals` are inconsistent, or
///     ``n < 1`` / ``m < 2``.
#[pyfunction]
pub fn functional_mae<'py>(
    _py: Python<'py>,
    y_true: PyReadonlyArray2<'py, f64>,
    y_pred: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
) -> PyResult<f64> {
    let yt = numpy2d_to_fdmatrix(y_true)?;
    let yp = numpy2d_to_fdmatrix(y_pred)?;
    let av = numpy1d_to_vec(argvals);
    to_pyresult(fdars_core::functional_mae(&yt, &yp, &av))
}

/// Functional Mean Squared Error integrated over `argvals`.
///
/// Parameters
/// ----------
/// y_true : numpy.ndarray
///     True functional data matrix, shape (n, m). Rows are observations.
/// y_pred : numpy.ndarray
///     Predicted functional data matrix, shape (n, m). Must match `y_true` shape.
/// argvals : numpy.ndarray
///     Evaluation points, length m. Must be sorted.
///
/// Returns
/// -------
/// float
///     ``(1/n) * sum_i ∫ (y_true_i(t) - y_pred_i(t))^2 dt`` approximated by
///     Simpson's rule.
///
/// Raises
/// ------
/// ValueError
///     If shapes of `y_true`, `y_pred`, or `argvals` are inconsistent, or
///     ``n < 1`` / ``m < 2``.
#[pyfunction]
pub fn functional_mse<'py>(
    _py: Python<'py>,
    y_true: PyReadonlyArray2<'py, f64>,
    y_pred: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
) -> PyResult<f64> {
    let yt = numpy2d_to_fdmatrix(y_true)?;
    let yp = numpy2d_to_fdmatrix(y_pred)?;
    let av = numpy1d_to_vec(argvals);
    to_pyresult(fdars_core::functional_mse(&yt, &yp, &av))
}

/// Functional Mean Absolute Percentage Error integrated over `argvals`.
///
/// Parameters
/// ----------
/// y_true : numpy.ndarray
///     True functional data matrix, shape (n, m). Rows are observations.
///     Must not contain values near zero (``|y_true| < NUMERICAL_EPS``).
/// y_pred : numpy.ndarray
///     Predicted functional data matrix, shape (n, m). Must match `y_true` shape.
/// argvals : numpy.ndarray
///     Evaluation points, length m. Must be sorted.
///
/// Returns
/// -------
/// float
///     ``(1/n) * sum_i ∫ |y_true_i(t) - y_pred_i(t)| / |y_true_i(t)| dt``
///     approximated by Simpson's rule.
///
/// Raises
/// ------
/// ValueError
///     If shapes are inconsistent, ``n < 1`` / ``m < 2``, or any value of
///     ``y_true`` is near zero (MAPE is undefined when dividing by ~0).
#[pyfunction]
pub fn functional_mape<'py>(
    _py: Python<'py>,
    y_true: PyReadonlyArray2<'py, f64>,
    y_pred: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
) -> PyResult<f64> {
    let yt = numpy2d_to_fdmatrix(y_true)?;
    let yp = numpy2d_to_fdmatrix(y_pred)?;
    let av = numpy1d_to_vec(argvals);
    to_pyresult(fdars_core::functional_mape(&yt, &yp, &av))
}

/// Functional Mean Squared Logarithmic Error integrated over `argvals`.
///
/// Parameters
/// ----------
/// y_true : numpy.ndarray
///     True functional data matrix, shape (n, m). Rows are observations.
///     All values must be ``> -1`` (so that ``ln(1 + y_true)`` is defined).
/// y_pred : numpy.ndarray
///     Predicted functional data matrix, shape (n, m). Must match `y_true` shape.
///     All values must be ``> -1``.
/// argvals : numpy.ndarray
///     Evaluation points, length m. Must be sorted.
///
/// Returns
/// -------
/// float
///     ``(1/n) * sum_i ∫ (ln(1+y_true_i(t)) - ln(1+y_pred_i(t)))^2 dt``
///     approximated by Simpson's rule.
///
/// Raises
/// ------
/// ValueError
///     If shapes are inconsistent, ``n < 1`` / ``m < 2``, or any value of
///     ``y_true`` or ``y_pred`` is ``<= -1`` (undefined logarithm domain).
#[pyfunction]
pub fn functional_msle<'py>(
    _py: Python<'py>,
    y_true: PyReadonlyArray2<'py, f64>,
    y_pred: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
) -> PyResult<f64> {
    let yt = numpy2d_to_fdmatrix(y_true)?;
    let yp = numpy2d_to_fdmatrix(y_pred)?;
    let av = numpy1d_to_vec(argvals);
    to_pyresult(fdars_core::functional_msle(&yt, &yp, &av))
}

/// Functional Explained Variance Score integrated over `argvals`.
///
/// Computes the explained variance per curve as
/// ``EV_i = 1 - SS_res_i / SS_tot_i`` where the sums of squares are
/// Simpson-integrated, then averages over all curves. Returns 1.0 for
/// perfect prediction, 0.0 when prediction equals the mean of ``y_true``,
/// and can be negative for predictions worse than the mean baseline.
///
/// Parameters
/// ----------
/// y_true : numpy.ndarray
///     True functional data matrix, shape (n, m). Rows are observations.
/// y_pred : numpy.ndarray
///     Predicted functional data matrix, shape (n, m). Must match `y_true` shape.
/// argvals : numpy.ndarray
///     Evaluation points, length m. Must be sorted.
///
/// Returns
/// -------
/// float
///     Explained variance score averaged over all curves; ≤ 1.0.
///
/// Raises
/// ------
/// ValueError
///     If shapes of `y_true`, `y_pred`, or `argvals` are inconsistent, or
///     ``n < 1`` / ``m < 2``.
#[pyfunction]
pub fn functional_explained_variance<'py>(
    _py: Python<'py>,
    y_true: PyReadonlyArray2<'py, f64>,
    y_pred: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
) -> PyResult<f64> {
    let yt = numpy2d_to_fdmatrix(y_true)?;
    let yp = numpy2d_to_fdmatrix(y_pred)?;
    let av = numpy1d_to_vec(argvals);
    to_pyresult(fdars_core::functional_explained_variance(&yt, &yp, &av))
}

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(functional_mae, m)?)?;
    m.add_function(wrap_pyfunction!(functional_mse, m)?)?;
    m.add_function(wrap_pyfunction!(functional_mape, m)?)?;
    m.add_function(wrap_pyfunction!(functional_msle, m)?)?;
    m.add_function(wrap_pyfunction!(functional_explained_variance, m)?)?;
    Ok(())
}
