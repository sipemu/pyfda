//! Basis representations and smoothing for functional data.

use crate::convert::*;
use numpy::{PyArray2, PyReadonlyArray1, PyReadonlyArray2};
use pyo3::prelude::*;

/// Project functional data onto a B-spline or Fourier basis.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Data, shape (n, m).
/// argvals : numpy.ndarray
///     Evaluation points, length m.
/// n_basis : int
///     Number of basis functions.
/// basis_type : str, optional
///     "bspline" (default) or "fourier".
///
/// Returns
/// -------
/// tuple
///     (coefficients (n, n_basis), actual_n_basis)
#[pyfunction]
#[pyo3(signature = (data, argvals, n_basis, basis_type="bspline"))]
pub fn fdata_to_basis_1d<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    n_basis: usize,
    basis_type: &str,
) -> PyResult<(Bound<'py, PyArray2<f64>>, usize)> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let bt = match basis_type {
        "bspline" => 0,
        "fourier" => 1,
        _ => {
            return Err(pyo3::exceptions::PyValueError::new_err(
                "basis_type must be 'bspline' or 'fourier'",
            ))
        }
    };
    let result = fdars_core::basis::fdata_to_basis_1d(&mat, &av, n_basis, bt).ok_or_else(|| {
        pyo3::exceptions::PyValueError::new_err("fdata_to_basis_1d failed")
    })?;
    Ok((
        fdmatrix_to_numpy2d(py, &result.coefficients),
        result.n_basis,
    ))
}

/// Reconstruct functional data from basis coefficients.
///
/// Parameters
/// ----------
/// coefficients : numpy.ndarray
///     Coefficients, shape (n, n_basis).
/// argvals : numpy.ndarray
///     Evaluation points, length m.
/// n_basis : int
///     Number of basis functions.
/// basis_type : str, optional
///     "bspline" (default) or "fourier".
///
/// Returns
/// -------
/// numpy.ndarray
///     Reconstructed data, shape (n, m).
#[pyfunction]
#[pyo3(signature = (coefficients, argvals, n_basis, basis_type="bspline"))]
pub fn basis_to_fdata_1d<'py>(
    py: Python<'py>,
    coefficients: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    n_basis: usize,
    basis_type: &str,
) -> PyResult<Bound<'py, PyArray2<f64>>> {
    let coef = numpy2d_to_fdmatrix(coefficients)?;
    let av = numpy1d_to_vec(argvals);
    let bt = match basis_type {
        "bspline" => 0,
        "fourier" => 1,
        _ => {
            return Err(pyo3::exceptions::PyValueError::new_err(
                "basis_type must be 'bspline' or 'fourier'",
            ))
        }
    };
    let result = fdars_core::basis::basis_to_fdata_1d(&coef, &av, n_basis, bt);
    Ok(fdmatrix_to_numpy2d(py, &result))
}

/// Fit P-splines to 1D functional data.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Data, shape (n, m).
/// argvals : numpy.ndarray
///     Evaluation points, length m.
/// n_basis : int
///     Number of B-spline basis functions.
/// lambda_ : float
///     Smoothing penalty parameter.
/// order : int, optional
///     Penalty difference order (default 2).
///
/// Returns
/// -------
/// dict
///     Dictionary with keys: fitted (n, m), coefficients (n, n_basis),
///     edf, rss, gcv, aic, bic
#[pyfunction]
#[pyo3(signature = (data, argvals, n_basis, lambda_, order=2))]
pub fn pspline_fit_1d<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    n_basis: usize,
    lambda_: f64,
    order: usize,
) -> PyResult<Bound<'py, PyAny>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let result = fdars_core::basis::pspline_fit_1d(&mat, &av, n_basis, lambda_, order)
        .ok_or_else(|| pyo3::exceptions::PyValueError::new_err("pspline_fit_1d failed"))?;
    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("fitted", fdmatrix_to_numpy2d(py, &result.fitted))?;
    dict.set_item("coefficients", fdmatrix_to_numpy2d(py, &result.coefficients))?;
    dict.set_item("edf", result.edf)?;
    dict.set_item("rss", result.rss)?;
    dict.set_item("gcv", result.gcv)?;
    dict.set_item("aic", result.aic)?;
    dict.set_item("bic", result.bic)?;
    Ok(dict.into_any())
}

/// P-spline fit with GCV-selected smoothing parameter.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Data, shape (n, m).
/// argvals : numpy.ndarray
///     Evaluation points, length m.
/// n_basis : int
///     Number of B-spline basis functions.
/// order : int, optional
///     Penalty difference order (default 2).
///
/// Returns
/// -------
/// dict
///     Dictionary with keys: fitted (n, m), coefficients (n, n_basis),
///     edf, rss, gcv, aic, bic
#[pyfunction]
#[pyo3(signature = (data, argvals, n_basis, order=2))]
pub fn pspline_fit_gcv<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    n_basis: usize,
    order: usize,
) -> PyResult<Bound<'py, PyAny>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let result = fdars_core::basis::pspline_fit_gcv(&mat, &av, n_basis, order)
        .ok_or_else(|| pyo3::exceptions::PyValueError::new_err("pspline_fit_gcv failed"))?;
    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("fitted", fdmatrix_to_numpy2d(py, &result.fitted))?;
    dict.set_item("coefficients", fdmatrix_to_numpy2d(py, &result.coefficients))?;
    dict.set_item("edf", result.edf)?;
    dict.set_item("rss", result.rss)?;
    dict.set_item("gcv", result.gcv)?;
    dict.set_item("aic", result.aic)?;
    dict.set_item("bic", result.bic)?;
    Ok(dict.into_any())
}

/// Automatic basis selection (GCV/AIC/BIC) for 1D data.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Data, shape (n, m).
/// argvals : numpy.ndarray
///     Evaluation points, length m.
/// criterion : str, optional
///     "gcv" (default), "aic", or "bic".
/// nbasis_min : int, optional
///     Minimum number of basis functions (0 for auto).
/// nbasis_max : int, optional
///     Maximum number of basis functions (0 for auto).
/// lambda_pspline : float, optional
///     Smoothing parameter for P-spline (negative for auto-select).
/// use_seasonal_hint : bool, optional
///     Whether to use FFT to detect seasonality (default True).
///
/// Returns
/// -------
/// list[dict]
///     List of per-curve selection results, each with keys:
///     basis_type, nbasis, score, coefficients, fitted, edf, seasonal_detected, lambda_val
#[pyfunction]
#[pyo3(signature = (data, argvals, criterion="gcv", nbasis_min=0, nbasis_max=0, lambda_pspline=-1.0, use_seasonal_hint=true))]
pub fn select_basis_auto_1d<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    criterion: &str,
    nbasis_min: usize,
    nbasis_max: usize,
    lambda_pspline: f64,
    use_seasonal_hint: bool,
) -> PyResult<Bound<'py, PyAny>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let crit = match criterion {
        "gcv" => 0,
        "aic" => 1,
        "bic" => 2,
        _ => {
            return Err(pyo3::exceptions::PyValueError::new_err(
                "criterion must be 'gcv', 'aic', or 'bic'",
            ))
        }
    };
    let result = fdars_core::basis::select_basis_auto_1d(
        &mat,
        &av,
        crit,
        nbasis_min,
        nbasis_max,
        lambda_pspline,
        use_seasonal_hint,
    );
    let list = pyo3::types::PyList::empty(py);
    for sel in &result.selections {
        let dict = pyo3::types::PyDict::new(py);
        let btype = match sel.basis_type {
            fdars_core::basis::ProjectionBasisType::Bspline => "bspline",
            fdars_core::basis::ProjectionBasisType::Fourier => "fourier",
            _ => "unknown",
        };
        dict.set_item("basis_type", btype)?;
        dict.set_item("nbasis", sel.nbasis)?;
        dict.set_item("score", sel.score)?;
        dict.set_item("coefficients", vec_to_numpy1d(py, sel.coefficients.clone()))?;
        dict.set_item("fitted", vec_to_numpy1d(py, sel.fitted.clone()))?;
        dict.set_item("edf", sel.edf)?;
        dict.set_item("seasonal_detected", sel.seasonal_detected)?;
        dict.set_item("lambda_val", sel.lambda)?;
        list.append(dict)?;
    }
    Ok(list.into_any())
}

/// Evaluate a B-spline basis at given points.
///
/// Parameters
/// ----------
/// argvals : numpy.ndarray
///     Evaluation points.
/// nknots : int
///     Number of interior knots.
/// order : int, optional
///     Spline order (default 4 = cubic).
///
/// Returns
/// -------
/// numpy.ndarray
///     Basis matrix of shape (len(argvals), nbasis) where nbasis = nknots + order.
#[pyfunction]
#[pyo3(signature = (argvals, nknots, order=4))]
pub fn bspline_basis<'py>(
    py: Python<'py>,
    argvals: PyReadonlyArray1<'py, f64>,
    nknots: usize,
    order: usize,
) -> PyResult<Bound<'py, PyArray2<f64>>> {
    let av = numpy1d_to_vec(argvals);
    let m = av.len();
    let flat = fdars_core::basis::bspline_basis(&av, nknots, order);
    let nbasis = if m > 0 { flat.len() / m } else { 0 };
    // flat is column-major (m x nbasis) — convert to row-major for numpy
    let row_major: Vec<Vec<f64>> = (0..m)
        .map(|i| (0..nbasis).map(|j| flat[i + j * m]).collect())
        .collect();
    Ok(PyArray2::from_vec2(py, &row_major).unwrap())
}

/// Evaluate a Fourier basis at given points.
///
/// Parameters
/// ----------
/// argvals : numpy.ndarray
///     Evaluation points.
/// n_basis : int
///     Number of basis functions (should be odd).
///
/// Returns
/// -------
/// numpy.ndarray
///     Basis matrix of shape (len(argvals), n_basis).
#[pyfunction]
pub fn fourier_basis<'py>(
    py: Python<'py>,
    argvals: PyReadonlyArray1<'py, f64>,
    n_basis: usize,
) -> PyResult<Bound<'py, PyArray2<f64>>> {
    let av = numpy1d_to_vec(argvals);
    let m = av.len();
    let flat = fdars_core::basis::fourier_basis(&av, n_basis);
    let actual_nbasis = if m > 0 { flat.len() / m } else { 0 };
    // flat is column-major (m x actual_nbasis) — convert to row-major for numpy
    let row_major: Vec<Vec<f64>> = (0..m)
        .map(|i| (0..actual_nbasis).map(|j| flat[i + j * m]).collect())
        .collect();
    Ok(PyArray2::from_vec2(py, &row_major).unwrap())
}

/// Smooth functional data using basis expansion with GCV.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Data, shape (n, m).
/// argvals : numpy.ndarray
///     Evaluation points, length m.
/// n_basis : int
///     Number of basis functions.
/// basis_type : str, optional
///     "bspline" (default) or "fourier".
/// lfd_order : int, optional
///     Derivative order for the penalty (default 2).
/// log_lambda_min : float, optional
///     Minimum log10(lambda) for search (default -8.0).
/// log_lambda_max : float, optional
///     Maximum log10(lambda) for search (default 4.0).
/// n_grid : int, optional
///     Number of grid points for lambda search (default 25).
///
/// Returns
/// -------
/// dict
///     Dictionary with keys: fitted (n, m), coefficients (n, nbasis),
///     edf, gcv, aic, bic, nbasis
#[pyfunction]
#[pyo3(signature = (data, argvals, n_basis, basis_type="bspline", lfd_order=2, log_lambda_min=-8.0, log_lambda_max=4.0, n_grid=25))]
pub fn smooth_basis_gcv<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    n_basis: usize,
    basis_type: &str,
    lfd_order: usize,
    log_lambda_min: f64,
    log_lambda_max: f64,
    n_grid: usize,
) -> PyResult<Bound<'py, PyAny>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let bt = parse_smooth_basis_type(basis_type, &av)?;
    let result = fdars_core::smooth_basis::smooth_basis_gcv(
        &mat,
        &av,
        &bt,
        n_basis,
        lfd_order,
        (log_lambda_min, log_lambda_max),
        n_grid,
    )
    .ok_or_else(|| pyo3::exceptions::PyValueError::new_err("smooth_basis_gcv failed"))?;
    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("fitted", fdmatrix_to_numpy2d(py, &result.fitted))?;
    dict.set_item("coefficients", fdmatrix_to_numpy2d(py, &result.coefficients))?;
    dict.set_item("edf", result.edf)?;
    dict.set_item("gcv", result.gcv)?;
    dict.set_item("aic", result.aic)?;
    dict.set_item("bic", result.bic)?;
    dict.set_item("nbasis", result.nbasis)?;
    Ok(dict.into_any())
}

/// Cross-validated selection of number of basis functions.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Data, shape (n, m).
/// argvals : numpy.ndarray
///     Evaluation points, length m.
/// nbasis_min : int, optional
///     Minimum nbasis to test (default 4).
/// nbasis_max : int, optional
///     Maximum nbasis to test (default 20).
/// basis_type : str, optional
///     "bspline" (default) or "fourier".
/// criterion : str, optional
///     "gcv" (default), "cv", "aic", or "bic".
/// n_folds : int, optional
///     Number of folds for CV criterion (default 5).
/// lambda_ : float, optional
///     Smoothing parameter (default 1.0).
///
/// Returns
/// -------
/// dict
///     Dictionary with keys: optimal_nbasis, scores, nbasis_range, criterion
#[pyfunction]
#[pyo3(signature = (data, argvals, nbasis_min=4, nbasis_max=20, basis_type="bspline", criterion="gcv", n_folds=5, lambda_=1.0))]
pub fn basis_nbasis_cv<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    nbasis_min: usize,
    nbasis_max: usize,
    basis_type: &str,
    criterion: &str,
    n_folds: usize,
    lambda_: f64,
) -> PyResult<Bound<'py, PyAny>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let bt = parse_smooth_basis_type(basis_type, &av)?;
    let crit = match criterion {
        "gcv" => fdars_core::smooth_basis::BasisCriterion::Gcv,
        "cv" => fdars_core::smooth_basis::BasisCriterion::Cv,
        "aic" => fdars_core::smooth_basis::BasisCriterion::Aic,
        "bic" => fdars_core::smooth_basis::BasisCriterion::Bic,
        _ => {
            return Err(pyo3::exceptions::PyValueError::new_err(
                "criterion must be 'gcv', 'cv', 'aic', or 'bic'",
            ))
        }
    };
    let nbasis_range: Vec<usize> = (nbasis_min..=nbasis_max).collect();
    let result = fdars_core::smooth_basis::basis_nbasis_cv(
        &mat,
        &av,
        &nbasis_range,
        &bt,
        crit,
        n_folds,
        lambda_,
    )
    .ok_or_else(|| pyo3::exceptions::PyValueError::new_err("basis_nbasis_cv failed"))?;
    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("optimal_nbasis", result.optimal_nbasis)?;
    dict.set_item("scores", vec_to_numpy1d(py, result.scores))?;
    dict.set_item(
        "nbasis_range",
        usize_vec_to_numpy1d(py, result.nbasis_range),
    )?;
    let crit_str = match result.criterion {
        fdars_core::smooth_basis::BasisCriterion::Gcv => "gcv",
        fdars_core::smooth_basis::BasisCriterion::Cv => "cv",
        fdars_core::smooth_basis::BasisCriterion::Aic => "aic",
        fdars_core::smooth_basis::BasisCriterion::Bic => "bic",
    };
    dict.set_item("criterion", crit_str)?;
    Ok(dict.into_any())
}

/// Helper to parse basis_type string into smooth_basis::BasisType.
fn parse_smooth_basis_type(
    basis_type: &str,
    argvals: &[f64],
) -> PyResult<fdars_core::smooth_basis::BasisType> {
    match basis_type {
        "bspline" => Ok(fdars_core::smooth_basis::BasisType::Bspline { order: 4 }),
        "fourier" => {
            let t_min = argvals.iter().copied().fold(f64::INFINITY, f64::min);
            let t_max = argvals.iter().copied().fold(f64::NEG_INFINITY, f64::max);
            let period = t_max - t_min;
            Ok(fdars_core::smooth_basis::BasisType::Fourier { period })
        }
        _ => Err(pyo3::exceptions::PyValueError::new_err(
            "basis_type must be 'bspline' or 'fourier'",
        )),
    }
}

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(fdata_to_basis_1d, m)?)?;
    m.add_function(wrap_pyfunction!(basis_to_fdata_1d, m)?)?;
    m.add_function(wrap_pyfunction!(pspline_fit_1d, m)?)?;
    m.add_function(wrap_pyfunction!(pspline_fit_gcv, m)?)?;
    m.add_function(wrap_pyfunction!(select_basis_auto_1d, m)?)?;
    m.add_function(wrap_pyfunction!(bspline_basis, m)?)?;
    m.add_function(wrap_pyfunction!(fourier_basis, m)?)?;
    m.add_function(wrap_pyfunction!(smooth_basis_gcv, m)?)?;
    m.add_function(wrap_pyfunction!(basis_nbasis_cv, m)?)?;
    Ok(())
}
