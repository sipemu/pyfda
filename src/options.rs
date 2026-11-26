//! Shared builders that turn flat Python kwargs into fdars-core option types.
//!
//! Not a Python submodule: these helpers are used by several `*_mod.rs` files
//! so every binding spells the same option the same way.

use fdars_core::alignment::{
    AffineDomain, AffineMetric, AffineRegistrationConfig, DpEdgeCost, LinearWarpClass,
    OutlierThreshold, ShiftExtrapolation, WarpLambdaScale, WarpObjectivePenalty, WarpOptimConfig,
    WarpOptimMethod,
};
use fdars_core::metric::DtwWindow;
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::PyDict;

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

/// Build a `WarpOptimConfig` from the flat elastic-engine kwargs.
///
/// `method` is `"dp"` or `"rbfgs"`; `penalty` is `"l2gam"`, `"l2psi"`,
/// `"roughness"` or `"geodesic"`; `dp_cost` is `"piecewise_constant"` or
/// `"piecewise_linear"`; `lambda_scale` is `"native"`, `"dp"` or `"fdasrsf"`.
/// Unknown names raise `ValueError`; range checks are left to fdars-core.
pub fn warp_optim(
    method: &str,
    lambda: f64,
    penalty: &str,
    max_iter: usize,
    scl: usize,
    nbhd_dim: usize,
    dp_scl: usize,
    dp_cost: &str,
    dp_prune: bool,
    band_frac: f64,
    lambda_scale: &str,
) -> PyResult<WarpOptimConfig> {
    let mut cfg = WarpOptimConfig::default();
    cfg.method = match method {
        "dp" => WarpOptimMethod::Dp,
        "rbfgs" => WarpOptimMethod::Rbfgs,
        _ => return Err(unknown("method", method, "'dp', 'rbfgs'")),
    };
    cfg.penalty = match penalty {
        "l2gam" => WarpObjectivePenalty::L2Gam,
        "l2psi" => WarpObjectivePenalty::L2Psi,
        "roughness" => WarpObjectivePenalty::Roughness,
        "geodesic" => WarpObjectivePenalty::Geodesic,
        _ => {
            return Err(unknown(
                "penalty",
                penalty,
                "'l2gam', 'l2psi', 'roughness', 'geodesic'",
            ))
        }
    };
    cfg.dp_cost = match dp_cost {
        "piecewise_constant" => DpEdgeCost::PiecewiseConstant,
        "piecewise_linear" => DpEdgeCost::PiecewiseLinear,
        _ => {
            return Err(unknown(
                "dp_cost",
                dp_cost,
                "'piecewise_constant', 'piecewise_linear'",
            ))
        }
    };
    cfg.lambda_scale = match lambda_scale {
        "native" => WarpLambdaScale::Native,
        "dp" => WarpLambdaScale::Dp,
        "fdasrsf" => WarpLambdaScale::Fdasrsf,
        _ => {
            return Err(unknown(
                "lambda_scale",
                lambda_scale,
                "'native', 'dp', 'fdasrsf'",
            ))
        }
    };
    cfg.lambda = lambda;
    cfg.max_iter = max_iter;
    cfg.scl = scl;
    cfg.nbhd_dim = nbhd_dim;
    cfg.dp_scl = dp_scl;
    cfg.dp_prune = dp_prune;
    cfg.band_frac = band_frac;
    Ok(cfg)
}

/// Build a `WarpOptimConfig` from an optional dict holding the flat keys of
/// [`warp_optim`]: `method`, `lambda_`, `penalty`, `optim_max_iter`, `scl`,
/// `nbhd_dim`, `dp_scl`, `dp_cost`, `dp_prune`, `band_frac`, `lambda_scale`.
///
/// Missing keys take the core defaults; `None` gives `WarpOptimConfig::default()`.
/// An unknown key raises `ValueError` listing the valid ones.
pub fn warp_optim_from_dict(dict: Option<&Bound<'_, PyDict>>) -> PyResult<WarpOptimConfig> {
    const KEYS: [&str; 11] = [
        "method",
        "lambda_",
        "penalty",
        "optim_max_iter",
        "scl",
        "nbhd_dim",
        "dp_scl",
        "dp_cost",
        "dp_prune",
        "band_frac",
        "lambda_scale",
    ];
    let Some(dict) = dict else {
        return Ok(WarpOptimConfig::default());
    };
    for key in dict.keys() {
        let key: String = key.extract()?;
        if !KEYS.contains(&key.as_str()) {
            return Err(PyValueError::new_err(format!(
                "warp_optim: unknown key '{key}'; valid keys are {}",
                KEYS.join(", ")
            )));
        }
    }
    fn get<'py, T: pyo3::conversion::FromPyObjectOwned<'py>>(
        dict: &Bound<'py, PyDict>,
        key: &str,
        default: T,
    ) -> PyResult<T> {
        match dict.get_item(key)? {
            Some(v) => v.extract::<T>().map_err(|e| {
                let e: PyErr = e.into();
                PyValueError::new_err(format!("warp_optim['{key}']: {e}"))
            }),
            None => Ok(default),
        }
    }
    warp_optim(
        &get(dict, "method", "dp".to_string())?,
        get(dict, "lambda_", 0.0)?,
        &get(dict, "penalty", "l2gam".to_string())?,
        get(dict, "optim_max_iter", 30)?,
        get(dict, "scl", 3)?,
        get(dict, "nbhd_dim", 7)?,
        get(dict, "dp_scl", 1)?,
        &get(dict, "dp_cost", "piecewise_constant".to_string())?,
        get(dict, "dp_prune", true)?,
        get(dict, "band_frac", 0.0)?,
        &get(dict, "lambda_scale", "native".to_string())?,
    )
}

/// Parse a shift extrapolation mode: `"boundary"`, `"linear"`, `"periodic"`
/// or `"zeros"`.
pub fn shift_extrapolation(name: &str) -> PyResult<ShiftExtrapolation> {
    match name {
        "boundary" => Ok(ShiftExtrapolation::Boundary),
        "linear" => Ok(ShiftExtrapolation::Linear),
        "periodic" => Ok(ShiftExtrapolation::Periodic),
        "zeros" => Ok(ShiftExtrapolation::Zeros),
        _ => Err(unknown(
            "extrapolation",
            name,
            "'boundary', 'linear', 'periodic', 'zeros'",
        )),
    }
}

/// Parse an elastic outlier threshold rule: `"tukey"` (fence `Q3 + k·IQR`
/// with `k = tukey_k`) or `"quantile"` (the `(1 − alpha)` quantile).
pub fn outlier_threshold(method: &str, tukey_k: f64) -> PyResult<OutlierThreshold> {
    match method {
        "tukey" => Ok(OutlierThreshold::TukeyFence { k: tukey_k }),
        "quantile" => Ok(OutlierThreshold::Quantile),
        _ => Err(unknown("threshold_method", method, "'tukey', 'quantile'")),
    }
}

/// Parse a linear warp class: `"none"`, `"shift"`, `"dilation"` or `"affine"`.
pub fn linear_warp_class(name: &str) -> PyResult<LinearWarpClass> {
    match name {
        "none" => Ok(LinearWarpClass::None),
        "shift" => Ok(LinearWarpClass::Shift),
        "dilation" => Ok(LinearWarpClass::Dilation),
        "affine" => Ok(LinearWarpClass::Affine),
        _ => Err(unknown(
            "warp_class",
            name,
            "'none', 'shift', 'dilation', 'affine'",
        )),
    }
}

/// Build an `AffineRegistrationConfig` from flat kwargs.
///
/// `metric` is `"l2"`, `"normalized_l2"` or `"pearson"`; `domain` is
/// `"full"` or `"overlap"`; `extrapolation` as in [`shift_extrapolation`].
pub fn affine_config(
    metric: &str,
    domain: &str,
    extrapolation: &str,
    max_dilation: f64,
    max_shift: f64,
    grid_size: usize,
    max_iter: usize,
    tol: f64,
    center_warps: bool,
    optim_tol: f64,
) -> PyResult<AffineRegistrationConfig> {
    let mut cfg = AffineRegistrationConfig::default();
    cfg.metric = match metric {
        "l2" => AffineMetric::L2,
        "normalized_l2" => AffineMetric::NormalizedL2,
        "pearson" => AffineMetric::Pearson,
        _ => {
            return Err(unknown(
                "metric",
                metric,
                "'l2', 'normalized_l2', 'pearson'",
            ))
        }
    };
    cfg.domain = match domain {
        "full" => AffineDomain::Full,
        "overlap" => AffineDomain::Overlap,
        _ => return Err(unknown("domain", domain, "'full', 'overlap'")),
    };
    cfg.extrapolation = shift_extrapolation(extrapolation)?;
    cfg.max_dilation = max_dilation;
    cfg.max_shift = max_shift;
    cfg.grid_size = grid_size;
    cfg.max_iter = max_iter;
    cfg.tol = tol;
    cfg.center_warps = center_warps;
    cfg.optim_tol = optim_tol;
    Ok(cfg)
}

fn unknown(param: &str, got: &str, valid: &str) -> PyErr {
    PyValueError::new_err(format!("{param} must be one of {valid}, got '{got}'"))
}
