//! jfPCA fit/transform seam (fdars-core 0.48 `jfpca_model`).
//!
//! `jfpca_fit` and the `PyJfpcaModel` handle register into the existing
//! `fdars.alignment` submodule (called from `alignment_mod::register`). The
//! dict helpers are shared with `explain_mod` (`elastic_pfi`, `veesa_pipeline`).

use crate::convert::*;
use fdars_core::jfpca_model::{JfpcaModel, JfpcaTransform};
use numpy::{PyArray1, PyReadonlyArray1, PyReadonlyArray2};
use pyo3::prelude::*;
use pyo3::types::PyDict;

/// Trained joint (amplitude + phase) FPCA model (from `jfpca_fit`).
///
/// Projects new curves onto the trained basis (`transform`), reproduces the
/// training scores exactly (`score_training`) and reconstructs principal
/// directions (`principal_directions`).
#[pyclass(name = "PyJfpcaModel")]
pub struct PyJfpcaModel {
    pub inner: JfpcaModel,
}

#[pymethods]
impl PyJfpcaModel {
    /// Number of components (clamped to n - 1 at fit time).
    #[getter]
    pub fn ncomp(&self) -> usize {
        self.inner.ncomp
    }

    /// Eigenvalues (variance explained), length ncomp.
    #[getter]
    pub fn eigenvalues<'py>(&self, py: Python<'py>) -> Bound<'py, PyArray1<f64>> {
        vec_to_numpy1d(py, self.inner.eigenvalues.clone())
    }

    /// Karcher-mean template curve, length m.
    #[getter]
    pub fn karcher_mean<'py>(&self, py: Python<'py>) -> Bound<'py, PyArray1<f64>> {
        vec_to_numpy1d(py, self.inner.karcher_mean.clone())
    }

    /// Evaluation grid, length m.
    #[getter]
    pub fn argvals<'py>(&self, py: Python<'py>) -> Bound<'py, PyArray1<f64>> {
        vec_to_numpy1d(py, self.inner.argvals.clone())
    }

    /// Phase-vs-amplitude balance weight used at fit time.
    #[getter]
    pub fn balance_c(&self) -> f64 {
        self.inner.balance_c
    }

    /// Warp penalty used at fit time.
    #[getter]
    pub fn lambda_(&self) -> f64 {
        self.inner.lambda
    }

    /// Project new curves onto the trained joint-FPCA basis.
    ///
    /// Each curve is aligned to the trained Karcher-mean template and scored
    /// with the trained centring and eigenvectors (no refit).
    ///
    /// Parameters
    /// ----------
    /// new_curves : numpy.ndarray
    ///     Curves, shape (k, m), on the training grid.
    ///
    /// Returns
    /// -------
    /// dict
    ///     ``scores`` (k, ncomp), ``aligned`` (k, m), ``warping`` (k, m).
    ///     For the training curves the scores match the training scores up to
    ///     the alignment tolerance; use ``score_training`` for an exact
    ///     round trip.
    pub fn transform<'py>(
        &self,
        py: Python<'py>,
        new_curves: PyReadonlyArray2<'py, f64>,
    ) -> PyResult<Bound<'py, PyDict>> {
        let mat = numpy2d_to_fdmatrix(new_curves)?;
        let t = to_pyresult(self.inner.transform(&mat))?;
        jfpca_transform_dict(py, &t)
    }

    /// Score the training curves from the stored training alignment (exact round trip).
    ///
    /// Returns
    /// -------
    /// dict
    ///     ``scores`` (n, ncomp), ``aligned`` (n, m), ``warping`` (n, m).
    pub fn score_training<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyDict>> {
        let t = to_pyresult(self.inner.score_training())?;
        jfpca_transform_dict(py, &t)
    }

    /// Amplitude and phase curves at mean +/- c * sigma_j along one joint component.
    ///
    /// Parameters
    /// ----------
    /// pc_index : int
    ///     0-based component index, < ncomp.
    /// c_values : array-like
    ///     Multipliers of the component standard deviation, e.g. [-2, -1, 0, 1, 2].
    ///
    /// Returns
    /// -------
    /// dict
    ///     ``pc_index``, ``c_values``, ``amplitude_curves`` (n_c, m) and
    ///     ``phase_curves`` (n_c, m, warps on the argvals domain). At c = 0
    ///     the amplitude curve is the Karcher mean and the phase curve the
    ///     identity warp.
    #[pyo3(signature = (pc_index, c_values))]
    pub fn principal_directions<'py>(
        &self,
        py: Python<'py>,
        pc_index: usize,
        c_values: Vec<f64>,
    ) -> PyResult<Bound<'py, PyDict>> {
        let pd = to_pyresult(self.inner.principal_directions(pc_index, &c_values))?;
        let dict = PyDict::new(py);
        dict.set_item("pc_index", pd.pc_index)?;
        dict.set_item("c_values", vec_to_numpy1d(py, pd.c_values.clone()))?;
        dict.set_item(
            "amplitude_curves",
            fdmatrix_to_numpy2d(py, &pd.amplitude_curves),
        )?;
        dict.set_item("phase_curves", fdmatrix_to_numpy2d(py, &pd.phase_curves))?;
        Ok(dict)
    }

    /// All fitted model fields as a plain dict (the keys of ``jfpca_fit`` minus ``model``).
    pub fn to_dict<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyDict>> {
        jfpca_model_dict(py, &self.inner)
    }
}

/// `JfpcaTransform` → `{scores, aligned, warping}`.
pub(crate) fn jfpca_transform_dict<'py>(
    py: Python<'py>,
    t: &JfpcaTransform,
) -> PyResult<Bound<'py, PyDict>> {
    let dict = PyDict::new(py);
    dict.set_item("scores", fdmatrix_to_numpy2d(py, &t.scores))?;
    dict.set_item("aligned", fdmatrix_to_numpy2d(py, &t.aligned))?;
    dict.set_item("warping", fdmatrix_to_numpy2d(py, &t.warping))?;
    Ok(dict)
}

/// Every public `JfpcaModel` field as a dict; the joint result is flattened.
pub(crate) fn jfpca_model_dict<'py>(
    py: Python<'py>,
    m: &JfpcaModel,
) -> PyResult<Bound<'py, PyDict>> {
    let dict = PyDict::new(py);
    dict.set_item("scores", fdmatrix_to_numpy2d(py, &m.joint_result.scores))?;
    dict.set_item("eigenvalues", vec_to_numpy1d(py, m.eigenvalues.clone()))?;
    dict.set_item(
        "cumulative_variance",
        vec_to_numpy1d(py, m.joint_result.cumulative_variance.clone()),
    )?;
    dict.set_item("ncomp", m.ncomp)?;
    dict.set_item("balance_c", m.balance_c)?;
    dict.set_item("lambda_", m.lambda)?;
    dict.set_item("karcher_mean", vec_to_numpy1d(py, m.karcher_mean.clone()))?;
    dict.set_item("mean_srsf", vec_to_numpy1d(py, m.mean_srsf.clone()))?;
    dict.set_item("mean_q", vec_to_numpy1d(py, m.mean_q.clone()))?;
    dict.set_item("mean_psi", vec_to_numpy1d(py, m.mean_psi.clone()))?;
    dict.set_item("vert_component", fdmatrix_to_numpy2d(py, &m.vert_component))?;
    dict.set_item(
        "horiz_component",
        fdmatrix_to_numpy2d(py, &m.horiz_component),
    )?;
    dict.set_item("argvals", vec_to_numpy1d(py, m.argvals.clone()))?;
    dict.set_item(
        "training_gammas",
        fdmatrix_to_numpy2d(py, &m.training_gammas),
    )?;
    dict.set_item(
        "training_aligned",
        fdmatrix_to_numpy2d(py, &m.training_aligned),
    )?;
    Ok(dict)
}

/// Fit a reusable joint amplitude + phase FPCA (jfPCA) model for out-of-sample projection.
///
/// Runs a Karcher-mean elastic alignment, joint FPCA, and stores everything
/// needed to project new curves (`model.transform`). The training scores are
/// those of ``joint_fpca`` with the same arguments.
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     Curves, shape (n, m), n >= 2, m >= 2.
/// argvals : numpy.ndarray
///     Evaluation grid, length m.
/// ncomp : int, optional
///     Number of joint components (default 3; clamped to n - 1).
/// balance_c : float, optional
///     Phase-vs-amplitude weight; None (default) picks it by golden-section search.
/// lambda_ : float, optional
///     Warp penalty of the Karcher alignment (default 0.0).
/// max_iter : int, optional
///     Maximum Karcher-mean iterations (default 20).
///
/// Returns
/// -------
/// dict
///     ``scores`` (n, ncomp), ``eigenvalues``, ``cumulative_variance``,
///     ``ncomp``, ``balance_c``, ``lambda_``, ``karcher_mean`` (m,),
///     ``mean_srsf`` (m,), ``mean_q`` (m+1,), ``mean_psi`` (m,),
///     ``vert_component`` (ncomp, m+1), ``horiz_component`` (ncomp, m),
///     ``argvals``, ``training_gammas`` (n, m), ``training_aligned`` (n, m)
///     and ``model`` (``PyJfpcaModel``).
///
/// Raises
/// ------
/// ValueError
///     If n < 2, m < 2, ncomp < 1, max_iter < 1 or ``len(argvals) != m``.
#[pyfunction]
#[pyo3(signature = (data, argvals, ncomp=3, balance_c=None, lambda_=0.0, max_iter=20))]
pub fn jfpca_fit<'py>(
    py: Python<'py>,
    data: PyReadonlyArray2<'py, f64>,
    argvals: PyReadonlyArray1<'py, f64>,
    ncomp: usize,
    balance_c: Option<f64>,
    lambda_: f64,
    max_iter: usize,
) -> PyResult<Bound<'py, PyDict>> {
    let mat = numpy2d_to_fdmatrix(data)?;
    let av = numpy1d_to_vec(argvals);
    let model = to_pyresult(fdars_core::jfpca_model::jfpca_fit(
        &mat, &av, ncomp, balance_c, lambda_, max_iter,
    ))?;
    let dict = jfpca_model_dict(py, &model)?;
    dict.set_item("model", Py::new(py, PyJfpcaModel { inner: model })?)?;
    Ok(dict)
}

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyJfpcaModel>()?;
    m.add_function(wrap_pyfunction!(jfpca_fit, m)?)?;
    Ok(())
}
