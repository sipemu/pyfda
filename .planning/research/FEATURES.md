# Feature Research

**Domain:** Provider-agnostic fdars AI advisor + full-library advisor coverage
**Researched:** 2026-08-12
**Confidence:** HIGH

> Scope: v3.0 new features only. Existing v2.0 features (build_diagnostics core,
> advise(), clustering/smoothing/FPCA/alignment/basis advisors, MCP surface, Agent
> Skill) are already shipped. This document covers (A) provider-agnostic layer and
> (B) per-aspect advisors for the remaining fdars analysis aspects.

---

## Part A — Provider-Agnostic Advisor Layer

### Table Stakes (Users Expect These)

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| `Provider` protocol + `AnthropicProvider` refactor | Existing code is tightly coupled to `anthropic` SDK; any provider work requires this first | MEDIUM | Keep `anthropic` first-class; refactor `advise()` to call `provider.complete(messages, schema)` instead of `client.messages.parse`. Existing tests must not regress. |
| `OpenAIProvider` (openai package, `base_url` param) | OpenAI is the most common secondary LLM target; `base_url` covers vLLM, LM Studio, LocalAI — the same adapter handles all three | MEDIUM | Structured outputs via `response_format={"type":"json_schema",...}` (openai >=1.40). Fall through to JSON-mode + validate/retry if model doesn't support native structured outputs. |
| `OllamaProvider` (local, no API key) | Offline/local-first path — the grounding invariant must hold even when there is no network | MEDIUM | `base_url` defaults to `http://localhost:11434`; uses Ollama's OpenAI-compatible `/v1/chat/completions`; no key required. Reuse OpenAI adapter with `api_key="ollama"` sentinel or a thin wrapper. |
| Provider + model selection via params first, env vars as fallback | Users expect `advise(provider="openai", model="gpt-4o")` to work; env vars (`FDARS_ADVISOR_PROVIDER`, `FDARS_ADVISOR_MODEL`, `FDARS_ADVISOR_BASE_URL`) as default resolution | LOW | Document resolution order: explicit param > env var > built-in default. Default provider = `anthropic` when `ANTHROPIC_API_KEY` present; else `ollama` (offline-capable). |
| Per-provider API key env vars | Each provider has its own key var (`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GOOGLE_API_KEY`); Ollama needs none | LOW | Key vars are standard in the ecosystem. The `[advisor]`, `[openai]`, `[gemini]`, `[ollama]` extras declare only the package dependency, not the key. |
| Validate-and-retry / repair contract for JSON-schema output | Local and weaker models often emit malformed JSON or miss required fields; without repair the grounding invariant breaks silently | MEDIUM | Up to 2 retries: first retry appends the validation error to the prompt; second retry escalates to a minimal repair prompt. Raise `ValueError` after exhausting retries rather than returning partial output. |
| Per-provider optional extras in `pyproject.toml` | Users expect `pip install fdars[openai]` to install the right SDK | LOW | `[openai]` -> `openai>=1.40`; `[gemini]` -> `google-generativeai>=0.8` or `google-genai>=1.0`; `[ollama]` -> no extra package (uses `openai` or `requests`); `[advisor]` keeps `anthropic>=0.72`. |
| Refactor existing advisors onto provider layer | Smoothing, FPCA, alignment, basis advisors (already shipped) must route through the new `Provider` protocol without breaking offline paths | MEDIUM | `build_diagnostics` is unaffected (offline, no provider). Only `advise()` changes. Offline CI tests remain: mock provider returns fixed `Advice`. |

### Differentiators (Competitive Advantage)

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| `GeminiProvider` (Google Generative AI) | Gemini 1.5/2.0 models have strong structured-output support and are attractive for users already in GCP | MEDIUM | Use `google-generativeai` SDK's `generation_config=GenerationConfig(response_schema=..., response_mime_type="application/json")`. Schema must be translated from Pydantic to Gemini schema format (dict conversion, not native Pydantic). |
| Offline-first default (Ollama path, no key needed) | Distinguishes fdars from tools that silently require a cloud key; users can get grounded advice in air-gapped environments | LOW | When no key env vars are set and no provider param given, resolve to `ollama` with a clear error if Ollama is not running. Document the offline path prominently. |
| Native structured outputs vs JSON-mode vs prompt-only — transparent capability detection | Users should not need to know which path is taken; the grounding contract is the same on all paths | MEDIUM | Provider adapter exposes `supports_native_structured_output() -> bool`; `advise()` picks the right call path. Log the chosen path at DEBUG level only; do not expose it in `Advice`. |

### Anti-Features (Commonly Requested, Often Problematic)

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| LiteLLM / pydantic-ai as unified provider abstraction | "One dependency handles all providers" | Adds a heavy transitive dependency with its own versioning churn; loses control over the validate-and-retry contract; pydantic-ai's agent model is not aligned with fdars's grounding-invariant pattern | Custom `Provider` protocol (3 methods) + thin per-SDK adapters. Each adapter is ~50 lines. Total code is smaller than LiteLLM's surface area. |
| Streaming responses | "Faster UX for long outputs" | `Advice` is a structured Pydantic object — streaming JSON schema output requires buffering the entire stream before validation anyway; there is no incremental `Advice` to surface | Return the full `Advice` synchronously. If latency is a concern, the offline `build_diagnostics` is instant; the LLM call is the only network hop. |
| Allowing LLM to generate diagnostic numbers | "Richer interpretation" | Violates the grounding invariant — the core hard constraint of the entire advisor system. A hallucinated GCV value or R-squared is worse than no value. | fdars computes every number; the LLM interprets values that are explicitly present in `diagnostics`. Evidence must cite a value from the dict. |
| Auto-selecting the cheapest available model | "Cost optimization" | Users need reproducible advice; model auto-switching makes advice non-reproducible and breaks offline tests | Explicit model param + env var default. Document model cost/capability tradeoffs in docs. |
| HTTP/SSE transport for MCP server | "Remote access" | Deferred in v2.0 for good reason — stdio covers all local/CI usage; HTTP adds auth surface | Keep stdio. HTTP deferred to a future milestone. |

---

## Part B — Per-Aspect Advisor Coverage

Each fdars analysis aspect below needs: (1) a `build_diagnostics` branch (offline, deterministic, fdars-computed values only) and (2) grounded task families for `advise()` (interpretation / parameter / method). The existing code already ships clustering, smoothing, FPCA, alignment, and basis. The following covers the remaining aspects.

### Table Stakes (Users Expect These)

#### depth / outliers

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| `build_diagnostics(result, "depth")` | Depth is the most common exploratory FDA step; users need interpretation of depth score distributions | MEDIUM | Inputs: depth scores array (n,), method name (fraiman_muniz/modal/random_projection/band/rpd), ref_data shape. Compute: `n_obs`, `depth_min`, `depth_max`, `depth_mean`, `depth_median`, `depth_q10`, `depth_q90`, depth histogram bucket counts (10 buckets, plain list). No fdars call needed — pure NumPy over the score array. |
| `build_diagnostics(result, "outliers")` | Outlier detection produces flags + thresholds; users need to understand what fraction is flagged and why | MEDIUM | Inputs: dict with `outliers` (bool array), `threshold` (scalar), optional `magnitude`/`shape` arrays (from `magnitude_shape`), optional `mei`/`mbd` (from `outliergram`). Compute: `n_obs`, `n_outliers`, `outlier_fraction`, `threshold`, `method` (lrt/magnitude_shape/outliergram inferred from keys present), `has_magnitude_shape` flag, `magnitude_range`/`shape_range` when present. |
| Interpretation task family for depth | "What does this depth distribution tell me about the dataset?" | LOW | System prompt extension: low bottom decile = heavy-tailed depth (many peripheral curves); bimodal depth = two functional groups. Cite `depth_q10`, `depth_mean`. |
| Parameter guidance for outlier detection | "Is my threshold/alpha too aggressive?" | LOW | Cite `outlier_fraction`: if > 20% flagged, suggest increasing alpha or trimming; if 0 flagged, suggest decreasing alpha. |
| Method guidance for depth | "When should I switch from Fraiman-Muniz to RPD?" | LOW | If data is derivative-rich (inferred from user context), recommend RPD (`random_projection_deriv_1d`); if data is 2D, check method variant. |

#### regression / FPCA regression

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| `build_diagnostics(result, "regression")` | Regression is a primary analysis output; users need R-squared, residual stats, and component count guidance | MEDIUM | Inputs: dict with `fitted_values`, `residuals`, `r_squared`, optional `beta_t` (m,), optional `coefficients`. Compute: `n_obs`, `r_squared`, `residual_mean`, `residual_std`, `residual_max_abs`, `residual_skew` (via NumPy), `beta_t_range` (min/max of beta_t when present), `method` (lm/pls/l1/huber/np/fosr inferred from keys). |
| `build_diagnostics(result, "regression_cv")` | `fregre_cv` and `model_selection_ncomp` return CV curves; users need to interpret optimal_k and the error landscape | MEDIUM | Inputs: dict with `optimal_k`, `cv_errors` (list), `k_values` (list), optional `min_cv_error`. Compute: `optimal_k`, `min_cv_error`, `cv_curve` (list), `k_values` (list), `cv_curve_range` (min/max), `elbow_present` (bool: True if the curve has a local minimum that is not at the boundary). |
| Interpretation task family for regression | "What does R-squared=0.71 with these residuals mean?" | LOW | Cite `r_squared`, `residual_std`. Flag high residual skew as sign of outliers or nonlinearity. |
| Parameter guidance for regression | "Should I increase n_comp?" | MEDIUM | Needs CV result: cite `optimal_k` from `fregre_cv`. If `optimal_k` is at `k_max` boundary, recommend increasing `k_max`. |
| Method guidance for regression | "Switch from lm to robust?" | LOW | Cite `residual_skew` and `residual_max_abs`: high skew or extreme residuals recommend `fregre_l1` or `fregre_huber`. |

#### monitoring / SPM

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| `build_diagnostics(result, "spm")` | SPM Phase I produces T2/SPE statistics and control limits; users need to interpret alarm rates and limit calibration | HIGH | Inputs: dict with `t2` (n,), `spe` (n,), `t2_limit`, `spe_limit`, optional `eigenvalues`, optional `ncomp`. Compute: `n_obs`, `ncomp`, `t2_limit`, `spe_limit`, `t2_max`, `t2_mean`, `t2_exceedance_rate` (fraction above limit in Phase I — should be ~alpha), `spe_max`, `spe_mean`, `spe_exceedance_rate`, `eigenvalues` (list, cast), `variance_explained_cumulative` (list from eigenvalues, same logic as FPCA branch), `spe_kurtosis_excess` (from `spe_moment_match_diagnostic` when eigenvalues present — already a native fdars call returning `excess_kurtosis`). |
| Interpretation task family for SPM | "Is my Phase I calibration reasonable?" | MEDIUM | Cite `t2_exceedance_rate` vs alpha: if >> alpha, Phase I data may contain outliers or too few in-control samples. Cite `spe_kurtosis_excess` from `spe_moment_match_diagnostic`. |
| Parameter guidance for SPM | "Should I use more components?" | MEDIUM | Cite `variance_explained_cumulative`: if <90% at `ncomp`, recommend increasing. If `t2_exceedance_rate` >> alpha, recommend robust limit (`t2_limit_robust`). |
| Method guidance for SPM | "When to use CUSUM/EWMA over T2?" | LOW | If user context mentions sequential/streaming data, recommend `spm_cusum` or `spm_ewma` over `spm_phase1`+`spm_monitor`. Cite the chart type from keys present (`cusum_statistic` for CUSUM path, `smoothed_scores` for EWMA path). |

### Differentiators (Competitive Advantage)

#### represent / basis (new aspect advisor)

Note: `build_diagnostics(result, "basis")` already ships in v2.0. What is missing for the represent aspect is a dedicated advisor for the `Fdata` representation itself — grid density, range coverage, and component count choice before any analysis.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| `build_diagnostics(result, "represent")` | Represent is the first step in every FDA workflow; catching grid/range problems early prevents downstream errors | MEDIUM | Inputs: Fdata-like object or dict with `data` (n, m), `argvals` (m,), optional `rangeval`. Compute: `n_obs`, `n_points`, `argvals_min`, `argvals_max`, `argvals_spacing_mean`, `argvals_spacing_std`, `is_uniform_grid` (bool: spacing_std / spacing_mean < 0.01), `data_range_min`, `data_range_max`, `data_range_mean`. No fdars call needed — pure NumPy. |
| Interpretation task for represent | "Is my functional data grid adequate?" | LOW | Cite `n_points`, `is_uniform_grid`. Flag sparse grids (n_points < 20) as requiring pre-smoothing before group analysis. |
| Parameter guidance for represent | "How many basis functions / FPCA components does this grid support?" | LOW | Cite `n_points`: recommend `n_basis` <= n_points/3 as a rule of thumb; recommend `n_comp` <= min(n_obs-1, n_points//5). |

#### classification

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| `build_diagnostics(result, "classification")` | Classification outputs accuracy + predictions; advisor can guide method and ncomp choice | MEDIUM | Inputs: dict with `accuracy` (float), `predicted` (array), optional `error_rate` (from `fclassif_cv`), optional `fold_errors` (from CV), optional `best_ncomp`. Compute: `n_obs`, `accuracy`, `error_rate` (= 1 - accuracy), `n_classes` (inferred from unique labels when labels passed via kwargs; else `None`), `cv_error_rate` (from `error_rate` key when from CV), `fold_error_std` (std of `fold_errors` when present), `best_ncomp` (pass-through). |
| Interpretation task for classification | "Is 87% accuracy good for this problem?" | LOW | Cite `accuracy`, `error_rate`. Flag high `fold_error_std` as instability. |
| Parameter guidance for classification | "Should I increase ncomp for LDA/QDA?" | LOW | Cite `best_ncomp` from CV. If `best_ncomp` is at the boundary, recommend expanding search range. |
| Method guidance for classification | "Switch from LDA to DD-classifier?" | LOW | Flag when `accuracy` is low with LDA/QDA (cite value): recommend DD-classifier (`fclassif_dd`) for heavy-tailed or non-Gaussian functional distributions. Recommend kernel classifier when sample sizes are small. |

### Anti-Features (Commonly Requested, Often Problematic)

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| LLM-computed diagnostic summaries | "The model can compute mean/std itself from raw data" | Breaks the grounding invariant — any number the model produces is unverifiable and may be fabricated. The invariant requires fdars to compute every number | `build_diagnostics` computes all statistics deterministically from fdars/NumPy; `advise()` only interprets values present in that dict |
| Unified "auto-detect aspect" from result keys | "Convenience: just pass any result dict" | Key collisions across aspects (e.g., `r_squared` appears in regression and SPM-adjacent methods; `edf` appears in smoothing and basis); auto-detection would be unreliable and would make the API opaque | Require explicit `method=` parameter in `build_diagnostics`. The cost is one extra parameter; the benefit is deterministic routing and clear error messages. |
| Cross-aspect advice ("Given my smoothing and my clustering...") | "Holistic workflow advice" | Requires combining diagnostics from multiple aspects into one LLM call; the schema becomes unbounded; evidence citation becomes ambiguous | Users compose advisors: run `build_diagnostics` + `advise()` per aspect, read each `Advice`, then decide. The MCP tool loop already supports iterative re-run. |
| Streaming partial advice | "See recommendations as they arrive" | The validate-and-retry contract requires the full response before schema validation; a partial JSON object fails validation | Return full `Advice` synchronously. The offline `build_diagnostics` phase completes instantly; the LLM phase is the only latency. |
| ARL simulation as a `build_diagnostics` input path | "Include ARL0 in the SPM advisor" | `arl0_t2` is stochastic (seed-dependent) — including it in `build_diagnostics` would break the determinism guarantee | ARL is a design-time concern; users run `arl0_t2` separately. The SPM advisor uses only deterministic Phase I outputs (T2, SPE, limits, eigenvalues). |

---

## Feature Dependencies

```
Provider protocol (custom)
    required by -> AnthropicProvider refactor
    required by -> OpenAIProvider (+ base_url for OpenAI-compatible)
    required by -> GeminiProvider
    required by -> OllamaProvider
    required by -> all per-aspect advise() calls

validate-and-retry contract
    required by -> JSON-mode path (OpenAI, Ollama, Gemini fallback)
    enhances -> grounding invariant (prevents silent schema violations)

build_diagnostics per aspect (offline, deterministic)
    required by -> advise() per aspect (grounded LLM call)
    required by -> MCP tool fdars_build_diagnostics (extended to new aspects)
    independent of -> Provider protocol (no network, no LLM)

Existing: build_diagnostics(clustering/smoothing/fpca/alignment/basis) [shipped v2.0]
    refactored onto -> Provider protocol (advise() side only)

New: build_diagnostics(depth/outliers/regression/regression_cv/spm/represent/classification)
    follows same pattern as -> existing branches

pyproject.toml extras ([openai], [gemini], [ollama])
    required by -> respective provider adapters
    independent of -> [advisor] extra (Anthropic)

MCP runner run_method
    needs extension for new aspects -> new method names in _SUPPORTED_METHODS
    requires -> new fdars function mappings per aspect

Agent Skill (fdars-advisor)
    benefits from -> new aspect advisors (no code change; skill docs update)
    benefits from -> provider selection (env var FDARS_ADVISOR_PROVIDER)
```

### Dependency Notes

- **Provider protocol required before all provider adapters:** The `Provider` protocol (a Python `Protocol` class with `complete(messages, schema) -> Advice`) must be defined before any adapter can be written. All per-aspect `advise()` refactoring blocks on this.
- **validate-and-retry required by non-Anthropic providers:** Anthropic's `client.messages.parse` handles schema enforcement natively. OpenAI structured outputs are reliable for `gpt-4o` but not guaranteed for all models. Ollama and Gemini fallback paths always need the retry contract.
- **`build_diagnostics` branches are independent:** Each new branch (depth, outliers, regression, spm, represent, classification) can be developed and tested offline without any provider work. This means provider work and new-aspect `build_diagnostics` work can be parallelized.
- **MCP runner extension blocks on new `build_diagnostics` branches:** `run_method` maps method names to fdars functions. New method names (`"depth"`, `"classification"`, etc.) cannot be added to `_SUPPORTED_METHODS` until the corresponding `build_diagnostics` branch exists and the fdars function signature is confirmed.

---

## MVP Definition

### Launch With (v3.0)

- [x] `Provider` protocol + `AnthropicProvider` refactor — required to unblock all other provider work
- [x] `OpenAIProvider` with `base_url` — covers OpenAI + all OpenAI-compatible local endpoints; highest user demand after Anthropic
- [x] `OllamaProvider` — local/offline path; no API key; validates the grounding invariant on constrained models
- [x] validate-and-retry contract — required for all non-Anthropic providers to maintain grounding
- [x] per-provider optional extras (`[openai]`, `[gemini]`, `[ollama]`) — packaging correctness
- [x] `build_diagnostics` + task families for depth/outliers — most commonly used after clustering
- [x] `build_diagnostics` + task families for regression/regression_cv — primary analysis output
- [x] `build_diagnostics` + task families for monitoring/SPM — highest diagnostic complexity, highest user value
- [x] `build_diagnostics` for represent — first-step advisor, low complexity, high onboarding value
- [x] `build_diagnostics` + task families for classification — completes full-library coverage
- [x] `GeminiProvider` — third major cloud provider; completes the cloud triad
- [x] MCP runner extension to new aspects — required to expose new advisors via Tool surface
- [x] Refactor existing advisors (clustering/smoothing/FPCA/alignment/basis) onto provider layer

### Add After Validation (v3.x)

- [ ] HTTP/SSE transport for MCP — when remote/multi-user access is requested
- [ ] ARL-aware SPM advisor — when users request run-length design guidance (stochastic, separate from `build_diagnostics`)
- [ ] Cross-aspect compound diagnostics — if users request workflow-level advice (needs schema design first)

### Future Consideration (v4+)

- [ ] Async `advise()` — if long-running LLM calls block interactive usage
- [ ] Fine-tuned domain-specific model support — if users run private FDA-expert models
- [ ] Multi-turn conversation mode — if agentic workflows need persistent context across re-runs

---

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| Provider protocol + AnthropicProvider refactor | HIGH | MEDIUM | P1 |
| OpenAIProvider (+ base_url) | HIGH | MEDIUM | P1 |
| OllamaProvider (offline-capable) | HIGH | LOW | P1 |
| validate-and-retry contract | HIGH | MEDIUM | P1 |
| build_diagnostics: depth + outliers | HIGH | MEDIUM | P1 |
| build_diagnostics: regression + regression_cv | HIGH | MEDIUM | P1 |
| build_diagnostics: SPM / monitoring | HIGH | HIGH | P1 |
| build_diagnostics: represent | MEDIUM | LOW | P1 |
| build_diagnostics: classification | MEDIUM | MEDIUM | P1 |
| GeminiProvider | MEDIUM | MEDIUM | P2 |
| MCP runner extension (new aspects) | MEDIUM | LOW | P2 |
| per-provider pyproject.toml extras | HIGH | LOW | P1 |
| Refactor existing advisors onto provider layer | HIGH | MEDIUM | P1 |

**Priority key:**
- P1: Must have for v3.0 — grounding invariant + full-library coverage depend on it
- P2: Should have in v3.0, can be last phase if time-constrained
- P3: Defer to v3.x

---

## Per-Aspect Diagnostics Reference

This table is the canonical grounding reference for roadmap planning. Each row
defines what `build_diagnostics` must compute (no LLM, no network) and what task
families `advise()` must cover. Complexity is relative to the existing clustering
branch (which sets the HIGH bar).

| Aspect | `build_diagnostics` key outputs | Task families | Complexity | Depends on existing code |
|--------|--------------------------------|---------------|------------|--------------------------|
| **represent** | n_obs, n_points, argvals_min/max, spacing_mean/std, is_uniform_grid, data_range_min/max/mean | interpretation, parameter | LOW | Pure NumPy only; no fdars call needed |
| **smoothing** | lambda_values, gcv_curve, edf, optimal_lambda, optimal_gcv, optimal_edf, gcv_aic/bic_approx | interpretation, parameter, method | MEDIUM | Already shipped (v2.0) — `_build_smoothing_diagnostics` |
| **basis** | n_basis_values, gcv_curve, edf, optimal_n_basis, optimal_gcv, optimal_edf, gcv_aic/bic_approx | interpretation, parameter, method | MEDIUM | Already shipped (v2.0) — `_build_basis_diagnostics` |
| **alignment** | n_obs, mean_min/max/avg, amplitude_mean/max, phase_mean/max, converged, n_iter | interpretation, parameter, method | MEDIUM | Already shipped (v2.0) — `_build_alignment_diagnostics` |
| **fpca** | n_components, eigenvalues, explained_variance_ratio, cumulative_variance_explained, phase_leakage_indicator | interpretation, parameter, method | MEDIUM | Already shipped (v2.0) — `_build_fpca_diagnostics` |
| **clustering** | k, cluster_means, cluster_sizes, pairwise_amplitude/phase_distance, mean_amplitude/phase_separation | interpretation, parameter, method | HIGH | Already shipped (v2.0) — `_build_clustering_diagnostics` |
| **depth** | n_obs, depth_min/max/mean/median/q10/q90, depth_histogram (10 buckets), method | interpretation, parameter, method | LOW | Pure NumPy over score array; `fdars.depth.*` called by user before advisor |
| **outliers** | n_obs, n_outliers, outlier_fraction, threshold, method, has_magnitude_shape, magnitude_range, shape_range | interpretation, parameter | LOW | Pure NumPy over result dict keys; reads what `detect_outliers_lrt` / `outliergram` / `magnitude_shape` returned |
| **classification** | n_obs, accuracy, error_rate, n_classes, cv_error_rate, fold_error_std, best_ncomp | interpretation, parameter, method | LOW | Pure NumPy; reads what `fclassif_*` / `fclassif_cv` returned |
| **regression** | n_obs, r_squared, residual_mean/std/max_abs/skew, beta_t_range, method | interpretation, parameter, method | MEDIUM | Pure NumPy over result dict; reads what `fregre_lm`/`fregre_pls`/etc. returned |
| **regression_cv** | optimal_k, min_cv_error, cv_curve, k_values, cv_curve_range, elbow_present | interpretation, parameter | MEDIUM | Pure NumPy; reads `fregre_cv` / `model_selection_ncomp` result |
| **spm** | n_obs, ncomp, t2_limit, spe_limit, t2_max/mean, t2_exceedance_rate, spe_max/mean, spe_exceedance_rate, variance_explained_cumulative, spe_kurtosis_excess | interpretation, parameter, method | HIGH | Reads `spm_phase1` result; calls `spe_moment_match_diagnostic` (existing fdars function) for kurtosis |

---

## Sources

- Codebase: `/home/simonm/projects/rust/pyfda/python/fdars/advisor.py` (existing build_diagnostics branches, schema, grounding invariant, advise() implementation)
- Codebase: `/home/simonm/projects/rust/pyfda/python/fdars/mcp/_runner.py` (existing method dispatch, _SUPPORTED_METHODS)
- Codebase: `/home/simonm/projects/rust/pyfda/python/fdars/mcp/_registry.py` (HandleRegistry pattern)
- Codebase: `/home/simonm/projects/rust/pyfda/src/depth_mod.rs` (depth methods: fraiman_muniz, modal, random_projection, band, modified_band, rpd, functional_spatial)
- Codebase: `/home/simonm/projects/rust/pyfda/src/regression_mod.rs` (fpca, fregre_lm, fregre_pls, fregre_np, fregre_l1, fregre_huber, fregre_cv, model_selection_ncomp, fosr, fanova)
- Codebase: `/home/simonm/projects/rust/pyfda/src/outliers_mod.rs` (detect_outliers_lrt, outliergram, magnitude_shape)
- Codebase: `/home/simonm/projects/rust/pyfda/src/spm_mod.rs` (spm_phase1, spm_monitor, spe_moment_match_diagnostic, t2_pc_contributions, spm_cusum, spm_ewma, t2_limit_robust, spe_limit_robust)
- Codebase: `/home/simonm/projects/rust/pyfda/src/classification_mod.rs` (fclassif_lda, fclassif_qda, fclassif_knn, fclassif_kernel, fclassif_cv, fclassif_dd)
- Codebase: `/home/simonm/projects/rust/pyfda/.planning/PROJECT.md` (v3.0 milestone scope, grounding invariant, key decisions)

---
*Feature research for: fdars v3.0 — provider-agnostic AI advisor + full-library coverage*
*Researched: 2026-08-12*
