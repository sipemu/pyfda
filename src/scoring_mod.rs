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

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(functional_mse, m)?)?;
    Ok(())
}
