//! Basis representations and smoothing for functional data.

use crate::convert::*;
use crate::options::{boundary_mode, boundary_mode_name, wavelet_family, wavelet_family_name};
use fdars_core::wavelet::WaveletCoeffs;
use numpy::{PyArray1, PyArray2, PyReadonlyArray1, PyReadonlyArray2};
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};

/// Evaluate the constant (intercept) basis on a grid of evaluation points.
///
/// Returns a 1-D ndarray of ones with the same length as `argvals`.
/// This is the intercept column of a regression design matrix — the single
/// basis function is the constant ``f(t) = 1``.
///
/// Parameters
/// ----------
/// argvals : numpy.ndarray
///     Evaluation points, length m.
///
/// Returns
/// -------
/// numpy.ndarray
///     1-D float64 ndarray of shape (m,) with every entry equal to 1.0.
///     An empty input grid returns a length-0 array without panicking.
#[pyfunction]
pub fn constant_basis<'py>(
    py: Python<'py>,
    argvals: PyReadonlyArray1<'py, f64>,
) -> PyResult<Bound<'py, PyArray1<f64>>> {
    let av = numpy1d_to_vec(argvals);
    let result = fdars_core::basis::constant_basis(&av);
    Ok(vec_to_numpy1d(py, result))
}

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
    let result = fdars_core::basis::fdata_to_basis_1d(&mat, &av, n_basis, bt)
        .ok_or_else(|| pyo3::exceptions::PyValueError::new_err("fdata_to_basis_1d failed"))?;
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
    let result = fdars_core::basis::pspline_fit(&mat, &av, n_basis, lambda_, order)
        .ok_or_else(|| pyo3::exceptions::PyValueError::new_err("pspline_fit_1d failed"))?;
    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("fitted", fdmatrix_to_numpy2d(py, &result.fitted))?;
    dict.set_item(
        "coefficients",
        fdmatrix_to_numpy2d(py, &result.coefficients),
    )?;
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
    dict.set_item(
        "coefficients",
        fdmatrix_to_numpy2d(py, &result.coefficients),
    )?;
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
    let result = fdars_core::basis::select_basis_auto(
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
    let nbasis = flat.len().checked_div(m).unwrap_or(0);
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
    let actual_nbasis = flat.len().checked_div(m).unwrap_or(0);
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
    dict.set_item(
        "coefficients",
        fdmatrix_to_numpy2d(py, &result.coefficients),
    )?;
    dict.set_item("edf", result.edf)?;
    dict.set_item("gcv", result.gcv)?;
    dict.set_item("aic", result.aic)?;
    dict.set_item("bic", result.bic)?;
    dict.set_item("nbasis", result.nbasis)?;
    Ok(dict.into_any())
}

/// Smooth functional data using basis expansion with AIC-optimal lambda.
///
/// Identical parameter set to `smooth_basis_gcv`; selects the roughness
/// penalty parameter lambda by minimising AIC rather than GCV.
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
///     edf, gcv, aic, bic, nbasis. Selection minimizes AIC; the `gcv`, `bic`,
///     and `aic` keys are the respective scores evaluated at the AIC-optimal
///     lambda (i.e. `gcv` is reported for reference, not used for selection).
#[pyfunction]
#[pyo3(signature = (data, argvals, n_basis, basis_type="bspline", lfd_order=2, log_lambda_min=-8.0, log_lambda_max=4.0, n_grid=25))]
pub fn smooth_basis_aic<'py>(
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
    let result = fdars_core::smooth_basis::smooth_basis_aic(
        &mat,
        &av,
        &bt,
        n_basis,
        lfd_order,
        (log_lambda_min, log_lambda_max),
        n_grid,
    )
    .ok_or_else(|| pyo3::exceptions::PyValueError::new_err("smooth_basis_aic failed"))?;
    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("fitted", fdmatrix_to_numpy2d(py, &result.fitted))?;
    dict.set_item(
        "coefficients",
        fdmatrix_to_numpy2d(py, &result.coefficients),
    )?;
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
// `lambda_` defaults to 0.0: selecting the basis *dimension* (nbasis) must NOT apply a
// roughness penalty. A positive lambda saturates the effective df, flattens the
// GCV/AIC/BIC curve, and makes the criterion always pick the largest nbasis
// (sipemu/fdars#37). Use `pspline_fit_gcv` for penalised smoothing at a fixed nbasis.
#[pyo3(signature = (data, argvals, nbasis_min=4, nbasis_max=20, basis_type="bspline", criterion="gcv", n_folds=5, lambda_=0.0))]
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
        _ => "unknown",
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

/// Evaluate a Fourier basis with specified period at given points.
///
/// Parameters
/// ----------
/// argvals : numpy.ndarray
///     Evaluation points.
/// n_basis : int
///     Number of basis functions (should be odd).
/// period : float
///     Fourier period.
///
/// Returns
/// -------
/// numpy.ndarray
///     Basis matrix of shape (len(argvals), n_basis).
#[pyfunction]
pub fn fourier_basis_with_period<'py>(
    py: Python<'py>,
    argvals: PyReadonlyArray1<'py, f64>,
    n_basis: usize,
    period: f64,
) -> PyResult<Bound<'py, PyArray2<f64>>> {
    let av = numpy1d_to_vec(argvals);
    let m = av.len();
    let flat = fdars_core::basis::fourier_basis_with_period(&av, n_basis, period);
    let actual_nbasis = flat.len().checked_div(m).unwrap_or(0);
    let row_major: Vec<Vec<f64>> = (0..m)
        .map(|i| (0..actual_nbasis).map(|j| flat[i + j * m]).collect())
        .collect();
    Ok(PyArray2::from_vec2(py, &row_major).unwrap())
}

/// Evaluate a B-spline basis from a given knot vector.
///
/// Parameters
/// ----------
/// argvals : numpy.ndarray
///     Evaluation points.
/// knots : numpy.ndarray
///     Full knot vector (including boundary knots).
/// order : int, optional
///     Spline order (default 4 = cubic).
///
/// Returns
/// -------
/// numpy.ndarray
///     Basis matrix of shape (len(argvals), nbasis).
#[pyfunction]
#[pyo3(signature = (argvals, knots, order=4))]
pub fn bspline_basis_from_knots<'py>(
    py: Python<'py>,
    argvals: PyReadonlyArray1<'py, f64>,
    knots: PyReadonlyArray1<'py, f64>,
    order: usize,
) -> PyResult<Bound<'py, PyArray2<f64>>> {
    let av = numpy1d_to_vec(argvals);
    let kn = numpy1d_to_vec(knots);
    let m = av.len();
    let flat = fdars_core::basis::bspline_basis_from_knots(&av, &kn, order);
    let nbasis = flat.len().checked_div(m).unwrap_or(0);
    let row_major: Vec<Vec<f64>> = (0..m)
        .map(|i| (0..nbasis).map(|j| flat[i + j * m]).collect())
        .collect();
    Ok(PyArray2::from_vec2(py, &row_major).unwrap())
}

/// Construct B-spline knot vector.
///
/// Parameters
/// ----------
/// t_min : float
///     Left boundary of domain.
/// t_max : float
///     Right boundary of domain.
/// nknots : int
///     Number of interior knots.
/// order : int, optional
///     Spline order (default 4 = cubic).
///
/// Returns
/// -------
/// numpy.ndarray
///     Full knot vector.
#[pyfunction]
#[pyo3(signature = (t_min, t_max, nknots, order=4))]
pub fn construct_bspline_knots<'py>(
    py: Python<'py>,
    t_min: f64,
    t_max: f64,
    nknots: usize,
    order: usize,
) -> PyResult<Bound<'py, numpy::PyArray1<f64>>> {
    let knots = fdars_core::basis::construct_bspline_knots(t_min, t_max, nknots, order);
    Ok(vec_to_numpy1d(py, knots))
}

/// Fit Fourier basis to functional data using least squares.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Data, shape (n, m).
/// argvals : numpy.ndarray
///     Evaluation points, length m.
/// nbasis : int
///     Number of Fourier basis functions (should be odd).
///
/// Returns
/// -------
/// dict
///     fitted (n, m), coefficients (n, nbasis),
///     edf, rss, gcv, aic, bic, n_basis.
#[pyfunction]
pub fn fourier_fit_1d<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    nbasis: usize,
) -> PyResult<Bound<'py, PyAny>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let result = to_pyresult(fdars_core::basis::fourier_fit(&mat, &av, nbasis))?;
    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("fitted", fdmatrix_to_numpy2d(py, &result.fitted))?;
    dict.set_item(
        "coefficients",
        fdmatrix_to_numpy2d(py, &result.coefficients),
    )?;
    dict.set_item("edf", result.edf)?;
    dict.set_item("rss", result.rss)?;
    dict.set_item("gcv", result.gcv)?;
    dict.set_item("aic", result.aic)?;
    dict.set_item("bic", result.bic)?;
    dict.set_item("n_basis", result.n_basis)?;
    Ok(dict.into_any())
}

/// Select optimal number of Fourier basis functions via GCV.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Data, shape (n, m).
/// argvals : numpy.ndarray
///     Evaluation points, length m.
/// min_nbasis : int
///     Minimum number of basis functions to try.
/// max_nbasis : int
///     Maximum number of basis functions to try.
///
/// Returns
/// -------
/// int
///     Optimal number of basis functions.
#[pyfunction]
pub fn select_fourier_nbasis_gcv(
    _py: Python<'_>,
    data: PyReadonlyArray2<'_, f64>,
    argvals: PyReadonlyArray1<'_, f64>,
    min_nbasis: usize,
    max_nbasis: usize,
) -> PyResult<usize> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    Ok(fdars_core::basis::select_fourier_nbasis_gcv(
        &mat, &av, min_nbasis, max_nbasis,
    ))
}

// ---------------------------------------------------------------------------
// Wavelet DWT primitive
// ---------------------------------------------------------------------------

/// Opaque handle holding one multi-level DWT coefficient pyramid.
///
/// Produced by `wavelet_decompose` / `wavelet_decompose_matrix`; inverted by
/// `wavelet_reconstruct`. The handle keeps the per-level bookkeeping the
/// inverse transform needs, which plain arrays cannot carry.
#[pyclass(name = "PyWaveletCoeffs")]
pub struct PyWaveletCoeffs {
    pub inner: WaveletCoeffs,
}

#[pymethods]
impl PyWaveletCoeffs {
    /// Final coarse approximation band.
    #[getter]
    pub fn approx<'py>(&self, py: Python<'py>) -> Bound<'py, PyArray1<f64>> {
        vec_to_numpy1d(py, self.inner.approx().to_vec())
    }

    /// Detail bands, finest-first (``details[0]`` is level 1).
    #[getter]
    pub fn details<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyList>> {
        details_list(py, &self.inner)
    }

    /// Number of decomposition levels.
    #[getter]
    pub fn levels(&self) -> usize {
        self.inner.levels()
    }

    /// Length of the original signal.
    #[getter]
    pub fn signal_len(&self) -> usize {
        self.inner.signal_len()
    }

    /// Wavelet family name (``"haar"`` or ``"dbN"``).
    #[getter]
    pub fn wavelet(&self) -> String {
        wavelet_family_name(self.inner.family())
    }

    /// Boundary mode name (``"periodic"`` or ``"symmetric"``).
    #[getter]
    pub fn mode(&self) -> &'static str {
        boundary_mode_name(self.inner.mode())
    }
}

fn details_list<'py>(py: Python<'py>, c: &WaveletCoeffs) -> PyResult<Bound<'py, PyList>> {
    let list = PyList::empty(py);
    for level in 0..c.levels() {
        let band = c.detail(level).unwrap_or(&[]).to_vec();
        list.append(vec_to_numpy1d(py, band))?;
    }
    Ok(list)
}

fn wavelet_coeffs_dict<'py>(py: Python<'py>, c: WaveletCoeffs) -> PyResult<Bound<'py, PyDict>> {
    let dict = PyDict::new(py);
    dict.set_item("approx", vec_to_numpy1d(py, c.approx().to_vec()))?;
    dict.set_item("details", details_list(py, &c)?)?;
    dict.set_item("levels", c.levels())?;
    dict.set_item("signal_len", c.signal_len())?;
    dict.set_item("wavelet", wavelet_family_name(c.family()))?;
    dict.set_item("mode", boundary_mode_name(c.mode()))?;
    dict.set_item("coeffs", Py::new(py, PyWaveletCoeffs { inner: c })?)?;
    Ok(dict)
}

/// Multi-level orthogonal discrete wavelet transform (Mallat pyramid) of one signal.
///
/// Parameters
/// ----------
/// signal : numpy.ndarray
///     Signal, length n (any length; odd lengths are handled by the boundary mode).
/// wavelet : str, optional
///     ``"haar"`` or ``"db1"`` .. ``"db10"`` (default ``"db4"``; ``"db1"`` is Haar).
/// mode : str, optional
///     Boundary extension: ``"periodic"`` (default) or ``"symmetric"``.
/// level : int, optional
///     Decomposition depth in ``1..=wavelet_max_level(n, wavelet)``;
///     None (default) uses the maximum useful level.
///
/// Returns
/// -------
/// dict
///     ``approx`` (coarsest approximation band), ``details`` (list of detail
///     bands, finest-first: ``details[0]`` is level 1), ``levels``,
///     ``signal_len``, ``wavelet``, ``mode`` and ``coeffs`` (a
///     ``PyWaveletCoeffs`` handle for ``wavelet_reconstruct``).
///
/// Raises
/// ------
/// ValueError
///     For an empty signal, an unknown wavelet / mode, or an invalid level.
#[pyfunction]
#[pyo3(signature = (signal, wavelet="db4", mode="periodic", level=None))]
pub fn wavelet_decompose<'py>(
    py: Python<'py>,
    signal: PyReadonlyArray1<'py, f64>,
    wavelet: &str,
    mode: &str,
    level: Option<usize>,
) -> PyResult<Bound<'py, PyDict>> {
    let family = wavelet_family(wavelet)?;
    let mode = boundary_mode(mode)?;
    let sig = numpy1d_to_vec(signal);
    let c = to_pyresult(fdars_core::wavelet::decompose(&sig, family, mode, level))?;
    wavelet_coeffs_dict(py, c)
}

/// Multi-level discrete wavelet transform of every row (curve) of a matrix.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Curves, shape (n, m); each row is transformed independently.
/// wavelet : str, optional
///     ``"haar"`` or ``"db1"`` .. ``"db10"`` (default ``"db4"``).
/// mode : str, optional
///     ``"periodic"`` (default) or ``"symmetric"``.
/// level : int, optional
///     Decomposition depth; None (default) uses the maximum useful level.
///
/// Returns
/// -------
/// list of dict
///     One dict per row, with the keys of ``wavelet_decompose``.
///
/// Raises
/// ------
/// ValueError
///     For an empty matrix, an unknown wavelet / mode, or an invalid level.
#[pyfunction]
#[pyo3(signature = (data, wavelet="db4", mode="periodic", level=None))]
pub fn wavelet_decompose_matrix<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    wavelet: &str,
    mode: &str,
    level: Option<usize>,
) -> PyResult<Bound<'py, PyList>> {
    let family = wavelet_family(wavelet)?;
    let mode = boundary_mode(mode)?;
    let mat = numpy2d_to_fdmatrix(data)?;
    let all = to_pyresult(fdars_core::wavelet::decompose_matrix(
        &mat, family, mode, level,
    ))?;
    let list = PyList::empty(py);
    for c in all {
        list.append(wavelet_coeffs_dict(py, c)?)?;
    }
    Ok(list)
}

/// Inverse discrete wavelet transform: rebuild a signal from its coefficient pyramid.
///
/// Parameters
/// ----------
/// coeffs : PyWaveletCoeffs
///     Handle from ``wavelet_decompose`` (``result["coeffs"]``).
/// approx : numpy.ndarray, optional
///     Replacement approximation band (same length as ``coeffs.approx``).
///     None (default) keeps the stored band.
/// details : list of numpy.ndarray, optional
///     Replacement detail bands, finest-first, one per level with the stored
///     lengths (e.g. thresholded bands for wavelet denoising). None (default)
///     keeps the stored bands.
///
/// Returns
/// -------
/// numpy.ndarray
///     Reconstructed signal, length ``coeffs.signal_len``. Without replacements
///     this reproduces the decomposed signal to rounding error.
///
/// Raises
/// ------
/// ValueError
///     If a replacement band has the wrong count or length.
#[pyfunction]
#[pyo3(signature = (coeffs, approx=None, details=None))]
pub fn wavelet_reconstruct<'py>(
    py: Python<'py>,
    coeffs: &PyWaveletCoeffs,
    approx: Option<PyReadonlyArray1<'py, f64>>,
    details: Option<Vec<PyReadonlyArray1<'py, f64>>>,
) -> PyResult<Bound<'py, PyArray1<f64>>> {
    let mut c = coeffs.inner.clone();
    if let Some(a) = approx {
        let a = numpy1d_to_vec(a);
        if a.len() != c.approx.len() {
            return Err(PyValueError::new_err(format!(
                "approx must have length {}, got {}",
                c.approx.len(),
                a.len()
            )));
        }
        c.approx = a;
    }
    if let Some(d) = details {
        if d.len() != c.details.len() {
            return Err(PyValueError::new_err(format!(
                "details must hold {} bands (one per level), got {}",
                c.details.len(),
                d.len()
            )));
        }
        for (level, band) in d.into_iter().enumerate() {
            let band = numpy1d_to_vec(band);
            if band.len() != c.details[level].len() {
                return Err(PyValueError::new_err(format!(
                    "details[{level}] must have length {}, got {}",
                    c.details[level].len(),
                    band.len()
                )));
            }
            c.details[level] = band;
        }
    }
    let signal = to_pyresult(fdars_core::wavelet::reconstruct(&c))?;
    Ok(vec_to_numpy1d(py, signal))
}

/// Maximum useful DWT depth for a signal length and wavelet family.
///
/// Parameters
/// ----------
/// signal_len : int
///     Signal length n.
/// wavelet : str, optional
///     ``"haar"`` or ``"db1"`` .. ``"db10"`` (default ``"db4"``).
///
/// Returns
/// -------
/// int
///     ``floor(log2(n / (filter_len - 1)))``; for Haar ``floor(log2(n))``.
///
/// Raises
/// ------
/// ValueError
///     If the signal is too short for one level or the wavelet is unknown.
#[pyfunction]
#[pyo3(signature = (signal_len, wavelet="db4"))]
pub fn wavelet_max_level(signal_len: usize, wavelet: &str) -> PyResult<usize> {
    let family = wavelet_family(wavelet)?;
    to_pyresult(fdars_core::wavelet::max_level(signal_len, &family))
}

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(constant_basis, m)?)?;
    m.add_function(wrap_pyfunction!(fdata_to_basis_1d, m)?)?;
    m.add_function(wrap_pyfunction!(basis_to_fdata_1d, m)?)?;
    m.add_function(wrap_pyfunction!(pspline_fit_1d, m)?)?;
    m.add_function(wrap_pyfunction!(pspline_fit_gcv, m)?)?;
    m.add_function(wrap_pyfunction!(select_basis_auto_1d, m)?)?;
    m.add_function(wrap_pyfunction!(bspline_basis, m)?)?;
    m.add_function(wrap_pyfunction!(fourier_basis, m)?)?;
    m.add_function(wrap_pyfunction!(smooth_basis_gcv, m)?)?;
    m.add_function(wrap_pyfunction!(smooth_basis_aic, m)?)?;
    m.add_function(wrap_pyfunction!(basis_nbasis_cv, m)?)?;
    m.add_function(wrap_pyfunction!(fourier_basis_with_period, m)?)?;
    m.add_function(wrap_pyfunction!(bspline_basis_from_knots, m)?)?;
    m.add_function(wrap_pyfunction!(construct_bspline_knots, m)?)?;
    m.add_function(wrap_pyfunction!(fourier_fit_1d, m)?)?;
    m.add_function(wrap_pyfunction!(select_fourier_nbasis_gcv, m)?)?;
    m.add_class::<PyWaveletCoeffs>()?;
    m.add_function(wrap_pyfunction!(wavelet_decompose, m)?)?;
    m.add_function(wrap_pyfunction!(wavelet_decompose_matrix, m)?)?;
    m.add_function(wrap_pyfunction!(wavelet_reconstruct, m)?)?;
    m.add_function(wrap_pyfunction!(wavelet_max_level, m)?)?;
    Ok(())
}
