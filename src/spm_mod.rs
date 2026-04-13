//! Statistical Process Monitoring for functional data.

use crate::convert::*;
use numpy::{PyArray1, PyArray2, PyReadonlyArray1, PyReadonlyArray2};
use pyo3::prelude::*;

/// SPM Phase I estimation.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     In-control data, shape (n, m).
/// argvals : numpy.ndarray
///     Evaluation points, length m.
/// ncomp : int, optional
///     Number of FPC components (default 3).
/// alpha : float, optional
///     Significance level (default 0.05).
///
/// Returns
/// -------
/// dict
///     t2 (n,), spe (n,), t2_limit, spe_limit,
///     mean (m,), loadings (m, ncomp), eigenvalues (ncomp,).
#[pyfunction]
#[pyo3(signature = (data, argvals, ncomp=3, alpha=0.05))]
pub fn spm_phase1<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    ncomp: usize,
    alpha: f64,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let config = fdars_core::spm::SpmConfig {
        ncomp,
        alpha,
        ..Default::default()
    };
    let result = to_pyresult(fdars_core::spm::spm_phase1(&mat, &av, &config))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("t2", vec_to_numpy1d(py, result.t2_phase1))?;
    dict.set_item("spe", vec_to_numpy1d(py, result.spe_phase1))?;
    dict.set_item("t2_limit", result.t2_limit.ucl)?;
    dict.set_item("spe_limit", result.spe_limit.ucl)?;
    dict.set_item("mean", vec_to_numpy1d(py, result.fpca.mean.clone()))?;
    dict.set_item("loadings", fdmatrix_to_numpy2d(py, &result.fpca.rotation))?;
    dict.set_item("weights", vec_to_numpy1d(py, result.fpca.weights.clone()))?;
    dict.set_item(
        "eigenvalues",
        vec_to_numpy1d(py, result.eigenvalues.clone()),
    )?;
    Ok(dict)
}

/// SPM Phase II monitoring.
///
/// Parameters
/// ----------
/// mean : numpy.ndarray
///     FPCA mean function, length m.
/// loadings : numpy.ndarray
///     FPCA rotation matrix, shape (m, ncomp).
/// weights : numpy.ndarray
///     FPCA integration weights, length m.
/// eigenvalues : numpy.ndarray
///     Eigenvalues, length ncomp.
/// t2_limit : float
///     T-squared upper control limit.
/// spe_limit : float
///     SPE upper control limit.
/// new_data : numpy.ndarray
///     New observations, shape (n_new, m).
/// argvals : numpy.ndarray
///     Evaluation points, length m.
///
/// Returns
/// -------
/// dict
///     t2 (n_new,), spe (n_new,),
///     t2_alarm (bool array), spe_alarm (bool array).
#[pyfunction]
pub fn spm_monitor<'py>(
    py: Python<'py>,
    mean: PyReadonlyArray1<'py, f64>,
    loadings: PyReadonlyArray2<'py, f64>,
    weights: PyReadonlyArray1<'py, f64>,
    eigenvalues: PyReadonlyArray1<'py, f64>,
    t2_limit: f64,
    spe_limit: f64,
    new_data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let mn = numpy1d_to_vec(mean);
    let ld = numpy2d_to_fdmatrix(loadings)?;
    let wt = numpy1d_to_vec(weights);
    let ev = numpy1d_to_vec(eigenvalues);
    let nd = numpy2d_to_fdmatrix(new_data)?;
    let av = numpy1d_to_vec(argvals);

    let result = to_pyresult(fdars_core::spm::spm_monitor_from_fields(
        &mn, &ld, &wt, &ev, t2_limit, spe_limit, &nd, &av,
    ))?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("t2", vec_to_numpy1d(py, result.t2))?;
    dict.set_item("spe", vec_to_numpy1d(py, result.spe))?;
    dict.set_item("t2_alarm", bool_vec_to_numpy1d(py, result.t2_alarm))?;
    dict.set_item("spe_alarm", bool_vec_to_numpy1d(py, result.spe_alarm))?;
    Ok(dict)
}

/// Hotelling T^2 statistic.
///
/// Parameters
/// ----------
/// scores : numpy.ndarray
///     FPC scores, shape (n, p).
/// eigenvalues : numpy.ndarray
///     Eigenvalues, length p.
///
/// Returns
/// -------
/// numpy.ndarray
///     T^2 statistics, length n.
#[pyfunction]
pub fn hotelling_t2<'py>(
    py: Python<'py>,
    scores: PyReadonlyArray2<'py, f64>,
    eigenvalues: PyReadonlyArray1<'py, f64>,
) -> PyResult<Bound<'py, PyArray1<f64>>> {
    let sc = numpy2d_to_fdmatrix(scores)?;
    let ev = numpy1d_to_vec(eigenvalues);
    let result = to_pyresult(fdars_core::spm::hotelling_t2(&sc, &ev))?;
    Ok(vec_to_numpy1d(py, result))
}

/// Hotelling T^2 with eigenvalue regularization.
///
/// Parameters
/// ----------
/// scores : numpy.ndarray
///     FPC scores, shape (n, p).
/// eigenvalues : numpy.ndarray
///     Eigenvalues, length p.
/// epsilon : float
///     Minimum eigenvalue floor.
///
/// Returns
/// -------
/// numpy.ndarray
///     T^2 statistics, length n.
#[pyfunction]
pub fn hotelling_t2_regularized<'py>(
    py: Python<'py>,
    scores: PyReadonlyArray2<'py, f64>,
    eigenvalues: PyReadonlyArray1<'py, f64>,
    epsilon: f64,
) -> PyResult<Bound<'py, PyArray1<f64>>> {
    let sc = numpy2d_to_fdmatrix(scores)?;
    let ev = numpy1d_to_vec(eigenvalues);
    let result = to_pyresult(fdars_core::spm::hotelling_t2_regularized(&sc, &ev, epsilon))?;
    Ok(vec_to_numpy1d(py, result))
}

/// Compute T-squared control limit from chi-squared distribution.
///
/// Parameters
/// ----------
/// ncomp : int
///     Number of principal components.
/// alpha : float
///     Significance level.
///
/// Returns
/// -------
/// dict
///     ucl, alpha, description.
#[pyfunction]
pub fn t2_control_limit<'py>(
    py: Python<'py>,
    ncomp: usize,
    alpha: f64,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let result = to_pyresult(fdars_core::spm::t2_control_limit(ncomp, alpha))?;
    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("ucl", result.ucl)?;
    dict.set_item("alpha", result.alpha)?;
    dict.set_item("description", result.description)?;
    Ok(dict)
}

/// Compute SPE control limit using moment-matched chi-squared approximation.
///
/// Parameters
/// ----------
/// spe_values : numpy.ndarray
///     In-control SPE values, length n.
/// alpha : float
///     Significance level.
///
/// Returns
/// -------
/// dict
///     ucl, alpha, description.
#[pyfunction]
pub fn spe_control_limit<'py>(
    py: Python<'py>,
    spe_values: PyReadonlyArray1<'py, f64>,
    alpha: f64,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let sv = numpy1d_to_vec(spe_values);
    let result = to_pyresult(fdars_core::spm::spe_control_limit(&sv, alpha))?;
    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("ucl", result.ucl)?;
    dict.set_item("alpha", result.alpha)?;
    dict.set_item("description", result.description)?;
    Ok(dict)
}

/// Diagnostic for SPE moment-match chi-squared approximation.
///
/// Parameters
/// ----------
/// spe_values : numpy.ndarray
///     In-control SPE values.
///
/// Returns
/// -------
/// dict
///     excess_kurtosis, theoretical_kurtosis, is_adequate.
#[pyfunction]
pub fn spe_moment_match_diagnostic<'py>(
    py: Python<'py>,
    spe_values: PyReadonlyArray1<'py, f64>,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let sv = numpy1d_to_vec(spe_values);
    let (excess_kurtosis, theoretical_kurtosis, is_adequate) =
        to_pyresult(fdars_core::spm::spe_moment_match_diagnostic(&sv))?;
    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("excess_kurtosis", excess_kurtosis)?;
    dict.set_item("theoretical_kurtosis", theoretical_kurtosis)?;
    dict.set_item("is_adequate", is_adequate)?;
    Ok(dict)
}

/// Select the number of principal components.
///
/// Parameters
/// ----------
/// eigenvalues : numpy.ndarray
///     Eigenvalues in decreasing order.
/// method : str
///     "cumulative_variance", "elbow", "kaiser", or "fixed".
/// threshold : float, optional
///     Threshold for cumulative_variance (default 0.95) or fixed count.
///
/// Returns
/// -------
/// int
///     Selected number of components.
#[pyfunction]
#[pyo3(signature = (eigenvalues, method="cumulative_variance", threshold=0.95))]
pub fn select_ncomp(
    _py: Python<'_>,
    eigenvalues: PyReadonlyArray1<'_, f64>,
    method: &str,
    threshold: f64,
) -> PyResult<usize> {
    let ev = numpy1d_to_vec(eigenvalues);
    let m = match method {
        "cumulative_variance" => fdars_core::spm::NcompMethod::CumulativeVariance(threshold),
        "elbow" => fdars_core::spm::NcompMethod::Elbow,
        "kaiser" => fdars_core::spm::NcompMethod::Kaiser,
        "fixed" => fdars_core::spm::NcompMethod::Fixed(threshold as usize),
        _ => {
            return Err(pyo3::exceptions::PyValueError::new_err(
                "method must be 'cumulative_variance', 'elbow', 'kaiser', or 'fixed'",
            ))
        }
    };
    to_pyresult(fdars_core::spm::select_ncomp(&ev, &m))
}

/// EWMA smoothing of FPC scores.
///
/// Parameters
/// ----------
/// scores : numpy.ndarray
///     Score matrix, shape (n, ncomp).
/// lambda_ : float
///     Smoothing parameter in (0, 1].
///
/// Returns
/// -------
/// numpy.ndarray
///     Smoothed scores, shape (n, ncomp).
#[pyfunction]
pub fn ewma_scores<'py>(
    py: Python<'py>,
    scores: PyReadonlyArray2<'py, f64>,
    lambda_: f64,
) -> PyResult<Bound<'py, PyArray2<f64>>> {
    let sc = numpy2d_to_fdmatrix(scores)?;
    let result = to_pyresult(fdars_core::spm::ewma_scores(&sc, lambda_))?;
    Ok(fdmatrix_to_numpy2d(py, &result))
}

/// Per-PC T-squared contributions.
///
/// Parameters
/// ----------
/// scores : numpy.ndarray
///     Score matrix, shape (n, ncomp).
/// eigenvalues : numpy.ndarray
///     Eigenvalues, length ncomp.
///
/// Returns
/// -------
/// numpy.ndarray
///     Contributions, shape (n, ncomp).
#[pyfunction]
pub fn t2_pc_contributions<'py>(
    py: Python<'py>,
    scores: PyReadonlyArray2<'py, f64>,
    eigenvalues: PyReadonlyArray1<'py, f64>,
) -> PyResult<Bound<'py, PyArray2<f64>>> {
    let sc = numpy2d_to_fdmatrix(scores)?;
    let ev = numpy1d_to_vec(eigenvalues);
    let result = to_pyresult(fdars_core::spm::t2_pc_contributions(&sc, &ev))?;
    Ok(fdmatrix_to_numpy2d(py, &result))
}

/// Test per-PC T-squared contributions for Bonferroni-adjusted significance.
///
/// Parameters
/// ----------
/// contributions : numpy.ndarray
///     Per-PC contributions, shape (n, ncomp).
/// alpha : float
///     Family-wise significance level.
///
/// Returns
/// -------
/// numpy.ndarray
///     Significance flags (0.0/1.0), shape (n, ncomp).
#[pyfunction]
pub fn t2_pc_significance<'py>(
    py: Python<'py>,
    contributions: PyReadonlyArray2<'py, f64>,
    alpha: f64,
) -> PyResult<Bound<'py, PyArray2<f64>>> {
    let ct = numpy2d_to_fdmatrix(contributions)?;
    let result = to_pyresult(fdars_core::spm::t2_pc_significance(&ct, alpha))?;
    Ok(fdmatrix_to_numpy2d(py, &result))
}

/// In-control ARL for T-squared chart (ARL0).
///
/// Parameters
/// ----------
/// eigenvalues : numpy.ndarray
///     Eigenvalues, length ncomp.
/// ucl : float
///     Upper control limit.
/// n_simulations : int, optional
///     Number of simulations (default 10000).
/// max_run_length : int, optional
///     Max run length before truncation (default 5000).
/// seed : int, optional
///     Random seed (default 42).
///
/// Returns
/// -------
/// dict
///     arl, std_dev, median_rl.
#[pyfunction]
#[pyo3(signature = (eigenvalues, ucl, n_simulations=10000, max_run_length=5000, seed=42))]
pub fn arl0_t2<'py>(
    py: Python<'py>,
    eigenvalues: PyReadonlyArray1<'py, f64>,
    ucl: f64,
    n_simulations: usize,
    max_run_length: usize,
    seed: u64,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let ev = numpy1d_to_vec(eigenvalues);
    let config = fdars_core::spm::ArlConfig {
        n_simulations,
        max_run_length,
        seed,
    };
    let result = to_pyresult(fdars_core::spm::arl0_t2(&ev, ucl, &config))?;
    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("arl", result.arl)?;
    dict.set_item("std_dev", result.std_dev)?;
    dict.set_item("median_rl", result.median_rl)?;
    Ok(dict)
}

/// Out-of-control ARL for T-squared chart (ARL1).
///
/// Parameters
/// ----------
/// eigenvalues : numpy.ndarray
///     Eigenvalues, length ncomp.
/// ucl : float
///     Upper control limit.
/// shift : numpy.ndarray
///     Mean shift vector, length ncomp.
/// n_simulations : int, optional
///     Number of simulations (default 10000).
/// max_run_length : int, optional
///     Max run length (default 5000).
/// seed : int, optional
///     Random seed (default 42).
///
/// Returns
/// -------
/// dict
///     arl, std_dev, median_rl.
#[pyfunction]
#[pyo3(signature = (eigenvalues, ucl, shift, n_simulations=10000, max_run_length=5000, seed=42))]
pub fn arl1_t2<'py>(
    py: Python<'py>,
    eigenvalues: PyReadonlyArray1<'py, f64>,
    ucl: f64,
    shift: PyReadonlyArray1<'py, f64>,
    n_simulations: usize,
    max_run_length: usize,
    seed: u64,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let ev = numpy1d_to_vec(eigenvalues);
    let sh = numpy1d_to_vec(shift);
    let config = fdars_core::spm::ArlConfig {
        n_simulations,
        max_run_length,
        seed,
    };
    let result = to_pyresult(fdars_core::spm::arl1_t2(&ev, ucl, &sh, &config))?;
    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("arl", result.arl)?;
    dict.set_item("std_dev", result.std_dev)?;
    dict.set_item("median_rl", result.median_rl)?;
    Ok(dict)
}

/// In-control ARL for EWMA T-squared chart.
///
/// Parameters
/// ----------
/// eigenvalues : numpy.ndarray
///     Eigenvalues, length ncomp.
/// ucl : float
///     Upper control limit.
/// lambda_ : float
///     EWMA smoothing parameter in (0, 1].
/// n_simulations : int, optional
///     Number of simulations (default 10000).
/// max_run_length : int, optional
///     Max run length (default 5000).
/// seed : int, optional
///     Random seed (default 42).
///
/// Returns
/// -------
/// dict
///     arl, std_dev, median_rl.
#[pyfunction]
#[pyo3(signature = (eigenvalues, ucl, lambda_, n_simulations=10000, max_run_length=5000, seed=42))]
pub fn arl0_ewma_t2<'py>(
    py: Python<'py>,
    eigenvalues: PyReadonlyArray1<'py, f64>,
    ucl: f64,
    lambda_: f64,
    n_simulations: usize,
    max_run_length: usize,
    seed: u64,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let ev = numpy1d_to_vec(eigenvalues);
    let config = fdars_core::spm::ArlConfig {
        n_simulations,
        max_run_length,
        seed,
    };
    let result = to_pyresult(fdars_core::spm::arl0_ewma_t2(&ev, ucl, lambda_, &config))?;
    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("arl", result.arl)?;
    dict.set_item("std_dev", result.std_dev)?;
    dict.set_item("median_rl", result.median_rl)?;
    Ok(dict)
}

/// In-control ARL for SPE chart.
///
/// Parameters
/// ----------
/// spe_df : float
///     Degrees of freedom for SPE distribution.
/// spe_scale : float
///     Scale for SPE distribution.
/// ucl : float
///     Upper control limit.
/// n_simulations : int, optional
///     Number of simulations (default 10000).
/// max_run_length : int, optional
///     Max run length (default 5000).
/// seed : int, optional
///     Random seed (default 42).
///
/// Returns
/// -------
/// dict
///     arl, std_dev, median_rl.
#[pyfunction]
#[pyo3(signature = (spe_df, spe_scale, ucl, n_simulations=10000, max_run_length=5000, seed=42))]
pub fn arl0_spe<'py>(
    py: Python<'py>,
    spe_df: f64,
    spe_scale: f64,
    ucl: f64,
    n_simulations: usize,
    max_run_length: usize,
    seed: u64,
) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
    let config = fdars_core::spm::ArlConfig {
        n_simulations,
        max_run_length,
        seed,
    };
    let result = to_pyresult(fdars_core::spm::arl0_spe(spe_df, spe_scale, ucl, &config))?;
    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("arl", result.arl)?;
    dict.set_item("std_dev", result.std_dev)?;
    dict.set_item("median_rl", result.median_rl)?;
    Ok(dict)
}

/// Apply Western Electric rules to monitoring data.
///
/// Parameters
/// ----------
/// values : numpy.ndarray
///     Monitoring statistic values.
/// center : float
///     Center line value.
/// sigma : float
///     Standard deviation estimate.
///
/// Returns
/// -------
/// list[dict]
///     List of violations, each with 'rule' and 'indices'.
#[pyfunction]
pub fn western_electric_rules<'py>(
    py: Python<'py>,
    values: PyReadonlyArray1<'py, f64>,
    center: f64,
    sigma: f64,
) -> PyResult<Bound<'py, pyo3::types::PyList>> {
    let vals = numpy1d_to_vec(values);
    let violations = to_pyresult(fdars_core::spm::western_electric_rules(
        &vals, center, sigma,
    ))?;
    let list = pyo3::types::PyList::empty(py);
    for v in violations {
        let dict = pyo3::types::PyDict::new(py);
        dict.set_item("rule", format!("{:?}", v.rule))?;
        dict.set_item(
            "indices",
            v.indices.into_iter().map(|i| i as i64).collect::<Vec<_>>(),
        )?;
        list.append(dict)?;
    }
    Ok(list)
}

/// Apply Nelson rules to monitoring data.
///
/// Parameters
/// ----------
/// values : numpy.ndarray
///     Monitoring statistic values.
/// center : float
///     Center line value.
/// sigma : float
///     Standard deviation estimate.
///
/// Returns
/// -------
/// list[dict]
///     List of violations, each with 'rule' and 'indices'.
#[pyfunction]
pub fn nelson_rules<'py>(
    py: Python<'py>,
    values: PyReadonlyArray1<'py, f64>,
    center: f64,
    sigma: f64,
) -> PyResult<Bound<'py, pyo3::types::PyList>> {
    let vals = numpy1d_to_vec(values);
    let violations = to_pyresult(fdars_core::spm::nelson_rules(&vals, center, sigma))?;
    let list = pyo3::types::PyList::empty(py);
    for v in violations {
        let dict = pyo3::types::PyDict::new(py);
        dict.set_item("rule", format!("{:?}", v.rule))?;
        dict.set_item(
            "indices",
            v.indices.into_iter().map(|i| i as i64).collect::<Vec<_>>(),
        )?;
        list.append(dict)?;
    }
    Ok(list)
}

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(spm_phase1, m)?)?;
    m.add_function(wrap_pyfunction!(spm_monitor, m)?)?;
    m.add_function(wrap_pyfunction!(hotelling_t2, m)?)?;
    m.add_function(wrap_pyfunction!(hotelling_t2_regularized, m)?)?;
    m.add_function(wrap_pyfunction!(t2_control_limit, m)?)?;
    m.add_function(wrap_pyfunction!(spe_control_limit, m)?)?;
    m.add_function(wrap_pyfunction!(spe_moment_match_diagnostic, m)?)?;
    m.add_function(wrap_pyfunction!(select_ncomp, m)?)?;
    m.add_function(wrap_pyfunction!(ewma_scores, m)?)?;
    m.add_function(wrap_pyfunction!(t2_pc_contributions, m)?)?;
    m.add_function(wrap_pyfunction!(t2_pc_significance, m)?)?;
    m.add_function(wrap_pyfunction!(arl0_t2, m)?)?;
    m.add_function(wrap_pyfunction!(arl1_t2, m)?)?;
    m.add_function(wrap_pyfunction!(arl0_ewma_t2, m)?)?;
    m.add_function(wrap_pyfunction!(arl0_spe, m)?)?;
    m.add_function(wrap_pyfunction!(western_electric_rules, m)?)?;
    m.add_function(wrap_pyfunction!(nelson_rules, m)?)?;
    Ok(())
}
