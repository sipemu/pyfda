//! Shared builders that turn flat Python kwargs into fdars-core option types.
//!
//! Not a Python submodule: these helpers are used by several `*_mod.rs` files
//! so every binding spells the same option the same way.

use fdars_core::metric::DtwWindow;
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;

/// Build a `DtwWindow` from the `window=, radius=, window_fraction=, max_slope=` kwargs.
///
/// `window` is one of `"none"`, `"sakoe_chiba"` (needs `radius`), `"itakura"`
/// (needs `max_slope`), `"sakoe_chiba_fraction"` (needs `window_fraction`) or
/// `"itakura_fraction"` (needs `max_slope`). A missing required parameter or
/// an unknown name raises `ValueError`; range checks are left to fdars-core.
pub fn dtw_window(
    window: &str,
    radius: Option<usize>,
    window_fraction: Option<f64>,
    max_slope: Option<f64>,
) -> PyResult<DtwWindow> {
    let missing = |param: &str| {
        PyValueError::new_err(format!("window='{window}' requires the '{param}' argument"))
    };
    match window {
        "none" => Ok(DtwWindow::None),
        "sakoe_chiba" => Ok(DtwWindow::SakoeChiba {
            radius: radius.ok_or_else(|| missing("radius"))?,
        }),
        "itakura" => Ok(DtwWindow::Itakura {
            max_slope: max_slope.ok_or_else(|| missing("max_slope"))?,
        }),
        "sakoe_chiba_fraction" => Ok(DtwWindow::SakoeChibaFraction {
            window: window_fraction.ok_or_else(|| missing("window_fraction"))?,
        }),
        "itakura_fraction" => Ok(DtwWindow::ItakuraFraction {
            max_slope: max_slope.ok_or_else(|| missing("max_slope"))?,
        }),
        _ => Err(PyValueError::new_err(format!(
            "window must be one of 'none', 'sakoe_chiba', 'itakura', \
             'sakoe_chiba_fraction', 'itakura_fraction', got '{window}'"
        ))),
    }
}
