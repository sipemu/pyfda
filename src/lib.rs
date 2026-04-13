//! fdars – Python bindings for fdars-core (Functional Data Analysis in Rust).

#![allow(clippy::too_many_arguments)]
#![allow(clippy::type_complexity)]

use pyo3::prelude::*;

mod convert;

mod alignment_mod;
mod basis_mod;
mod classification_mod;
mod clustering_mod;
mod conformal_mod;
mod depth_mod;
mod explain_mod;
mod fdata_mod;
mod metric_mod;
mod outliers_mod;
mod regression_mod;
mod seasonal_mod;
mod simulation_mod;
mod smoothing_mod;
mod spm_mod;
mod tolerance_mod;

/// Create a submodule, register its contents, and attach it to a parent module.
macro_rules! register_submodule {
    ($parent:expr, $name:expr, $register_fn:path) => {{
        let sub = pyo3::types::PyModule::new($parent.py(), $name)?;
        $register_fn(&sub)?;
        $parent.add_submodule(&sub)?;
    }};
}

/// fdars – Functional Data Analysis for Python, powered by Rust.
#[pymodule]
fn _native(m: &Bound<'_, PyModule>) -> PyResult<()> {
    register_submodule!(m, "fdata", fdata_mod::register);
    register_submodule!(m, "depth", depth_mod::register);
    register_submodule!(m, "metric", metric_mod::register);
    register_submodule!(m, "basis", basis_mod::register);
    register_submodule!(m, "smoothing", smoothing_mod::register);
    register_submodule!(m, "clustering", clustering_mod::register);
    register_submodule!(m, "regression", regression_mod::register);
    register_submodule!(m, "alignment", alignment_mod::register);
    register_submodule!(m, "outliers", outliers_mod::register);
    register_submodule!(m, "seasonal", seasonal_mod::register);
    register_submodule!(m, "spm", spm_mod::register);
    register_submodule!(m, "classification", classification_mod::register);
    register_submodule!(m, "tolerance", tolerance_mod::register);
    register_submodule!(m, "conformal", conformal_mod::register);
    register_submodule!(m, "simulation", simulation_mod::register);
    register_submodule!(m, "explain", explain_mod::register);

    Ok(())
}
