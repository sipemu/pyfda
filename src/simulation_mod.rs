//! Simulation of functional data.

use crate::convert::*;
use numpy::{PyArray2, PyReadonlyArray1};
use pyo3::prelude::*;

/// Simulate functional data via Karhunen-Loeve expansion.
///
/// Parameters
/// ----------
/// n : int
///     Number of curves to generate.
/// argvals : numpy.ndarray
///     Evaluation points, length m.
/// n_basis : int, optional
///     Number of basis functions (default 5).
/// efun_type : str, optional
///     Eigenfunction type: "fourier" (default), "poly", "poly_high", "wiener".
/// eval_type : str, optional
///     Eigenvalue decay: "linear" (default), "exponential", "wiener".
/// seed : int, optional
///     Random seed for reproducibility (default None).
///
/// Returns
/// -------
/// numpy.ndarray
///     Simulated data of shape (n, m).
#[pyfunction]
#[pyo3(signature = (n, argvals, n_basis=5, efun_type="fourier", eval_type="linear", seed=None))]
pub fn simulate<'py>(
    py: Python<'py>,
    n: usize,
    argvals: PyReadonlyArray1<'py, f64>,
    n_basis: usize,
    efun_type: &str,
    eval_type: &str,
    seed: Option<u64>,
) -> PyResult<Bound<'py, PyArray2<f64>>> {
    let av = numpy1d_to_vec(argvals);
    let efun = match efun_type {
        "fourier" => fdars_core::simulation::EFunType::Fourier,
        "poly" => fdars_core::simulation::EFunType::Poly,
        "poly_high" => fdars_core::simulation::EFunType::PolyHigh,
        "wiener" => fdars_core::simulation::EFunType::Wiener,
        _ => {
            return Err(pyo3::exceptions::PyValueError::new_err(
                "efun_type must be 'fourier', 'poly', 'poly_high', or 'wiener'",
            ))
        }
    };
    let eval_ = match eval_type {
        "linear" => fdars_core::simulation::EValType::Linear,
        "exponential" => fdars_core::simulation::EValType::Exponential,
        "wiener" => fdars_core::simulation::EValType::Wiener,
        _ => {
            return Err(pyo3::exceptions::PyValueError::new_err(
                "eval_type must be 'linear', 'exponential', or 'wiener'",
            ))
        }
    };
    let result = fdars_core::simulation::sim_fundata(n, &av, n_basis, efun, eval_, seed);
    Ok(fdmatrix_to_numpy2d(py, &result))
}

/// Generate Gaussian process samples.
///
/// Parameters
/// ----------
/// n : int
///     Number of curves.
/// argvals : numpy.ndarray
///     Evaluation points, length m.
/// kernel : str, optional
///     Kernel type: "gaussian" (default), "exponential", "matern", "periodic".
/// length_scale : float, optional
///     Kernel length scale (default 0.2).
/// variance : float, optional
///     Kernel variance (default 1.0).
/// seed : int, optional
///     Random seed (default None).
///
/// Returns
/// -------
/// numpy.ndarray
///     GP samples of shape (n, m).
#[pyfunction]
#[pyo3(signature = (n, argvals, kernel="gaussian", length_scale=0.2, variance=1.0, seed=None))]
pub fn gaussian_process<'py>(
    py: Python<'py>,
    n: usize,
    argvals: PyReadonlyArray1<'py, f64>,
    kernel: &str,
    length_scale: f64,
    variance: f64,
    seed: Option<u64>,
) -> PyResult<Bound<'py, PyArray2<f64>>> {
    let av = numpy1d_to_vec(argvals);
    let kern = match kernel {
        "gaussian" => fdars_core::covariance::CovKernel::Gaussian {
            length_scale,
            variance,
        },
        "exponential" => fdars_core::covariance::CovKernel::Exponential {
            length_scale,
            variance,
        },
        "matern" => fdars_core::covariance::CovKernel::Matern {
            length_scale,
            variance,
            nu: 1.5,
        },
        "periodic" => fdars_core::covariance::CovKernel::Periodic {
            length_scale,
            variance,
            period: 1.0,
        },
        _ => {
            return Err(pyo3::exceptions::PyValueError::new_err(
                "kernel must be 'gaussian', 'exponential', 'matern', or 'periodic'",
            ))
        }
    };
    let result = to_pyresult(fdars_core::covariance::generate_gaussian_process(
        n, &kern, &av, None, seed,
    ))?;
    Ok(fdmatrix_to_numpy2d(py, &result.samples))
}

/// Compute covariance matrix from a kernel.
///
/// Parameters
/// ----------
/// argvals : numpy.ndarray
///     Evaluation points, length m.
/// kernel : str, optional
///     Kernel type: "gaussian" (default), "exponential".
/// length_scale : float, optional
///     (default 0.2).
/// variance : float, optional
///     (default 1.0).
///
/// Returns
/// -------
/// numpy.ndarray
///     Covariance matrix of shape (m, m).
#[pyfunction]
#[pyo3(signature = (argvals, kernel="gaussian", length_scale=0.2, variance=1.0))]
pub fn covariance_matrix<'py>(
    py: Python<'py>,
    argvals: PyReadonlyArray1<'py, f64>,
    kernel: &str,
    length_scale: f64,
    variance: f64,
) -> PyResult<Bound<'py, PyArray2<f64>>> {
    let av = numpy1d_to_vec(argvals);
    let kern = match kernel {
        "gaussian" => fdars_core::covariance::CovKernel::Gaussian {
            length_scale,
            variance,
        },
        "exponential" => fdars_core::covariance::CovKernel::Exponential {
            length_scale,
            variance,
        },
        _ => {
            return Err(pyo3::exceptions::PyValueError::new_err(
                "kernel must be 'gaussian' or 'exponential'",
            ))
        }
    };
    let result = to_pyresult(fdars_core::covariance::covariance_matrix(&kern, &av))?;
    Ok(fdmatrix_to_numpy2d(py, &result))
}

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(simulate, m)?)?;
    m.add_function(wrap_pyfunction!(gaussian_process, m)?)?;
    m.add_function(wrap_pyfunction!(covariance_matrix, m)?)?;
    Ok(())
}
