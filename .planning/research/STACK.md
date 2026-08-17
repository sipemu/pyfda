# Stack Research

**Domain:** PyO3 binding library upgrade — fdars-core 0.17.0 → 0.20.0 (functional inference + depth/boxplot + basis/smoothing)
**Researched:** 2026-08-17
**Confidence:** HIGH — all version, MSRV, dependency, and feature data verified directly against crates.io API and docs.rs/crate source for 0.17.0, 0.19.0, and 0.20.0.

---

## Decision Summary

The 0.17.0 → 0.20.0 upgrade requires **exactly one change** to the existing stack: bump the fdars-core version string in `Cargo.toml`. No new Rust dependencies, no new Python dependencies, no PyO3/numpy/maturin version changes, and no CI matrix changes are required. The `parallel` feature stays; the `linalg` feature must NOT be enabled. The existing `convert.rs` layer handles all new binding types without modification.

**Note on version history:** 0.18.0 was never published to crates.io. The registry jumps from 0.17.0 (2026-08-12) to 0.19.0 (2026-08-16) to 0.20.0 (2026-08-16). The "0.18 = audit-only" description in PROJECT.md refers to an internal increment that was never released as a public crate. The practical upgrade path is 0.17.0 → 0.20.0 directly.

---

## 1. Cargo.toml Change — Exact Line

**Current (`Cargo.toml` line 18):**
```toml
fdars-core = { version = "0.17.0", features = ["parallel"] }
```

**Required change:**
```toml
fdars-core = { version = "0.20.0", features = ["parallel"] }
```

### Caret semantics — why this pin is appropriate

Cargo's default caret requirement `"0.20.0"` is equivalent to `^0.20.0`, which resolves to `>=0.20.0, <0.21.0`. This is the correct pin: it accepts only 0.20.x patch releases, keeping the minor version locked. There is no reason to use `=` exact pinning — the upstream author (same person, sipemu) follows semver, and patch releases within 0.20.x are safe to accept. After the change, run `cargo update -p fdars-core` to regenerate `Cargo.lock` — the existing 0.17.0 checksum entry will be replaced by the 0.20.0 checksum. Commit the updated `Cargo.lock`.

### The `parallel` feature — keep it

The `parallel` feature enables rayon-based parallelism throughout fdars-core and has been the only enabled feature since 0.14.0. It is defined identically across 0.17.0, 0.19.0, and 0.20.0.

### The `linalg` feature — do NOT enable

Do not enable `linalg` for three reasons:

1. **MSRV conflict.** The docs.rs documentation for fdars-core 0.20.0 states explicitly: "`linalg` requires Rust 1.84+." pyfda's declared MSRV is `rust-version = "1.83"`. Enabling `linalg` would break the MSRV.
2. **New transitive dependencies.** `linalg` pulls in `faer` and `anofox-regression` as non-optional transitive dependencies. Keeping `linalg` disabled means no new crate entries appear in `Cargo.lock`.
3. **Not required by v5.0 targets.** None of Groups A, B, or C (inference, depth/boxplot, basis/smoothing quick wins) require ridge regression or the faer SVD path that `linalg` gates.

---

## 2. MSRV Safety — Verified

| Version | fdars-core declared MSRV | pyfda MSRV | Compatible? |
|---------|--------------------------|------------|-------------|
| 0.17.0 | 1.81 (verified via docs.rs Cargo.toml) | 1.83 | YES — pyfda demands more of the toolchain than upstream requires |
| 0.19.0 | 1.81 (verified via docs.rs Cargo.toml) | 1.83 | YES |
| 0.20.0 | 1.81 (verified via docs.rs Cargo.toml) | 1.83 | YES |

pyfda's MSRV (1.83) is strictly higher than fdars-core 0.20.0's MSRV (1.81). The bump introduces no MSRV risk. The `linalg` feature's 1.84 requirement is fully isolated behind the feature gate — it is never triggered when using `features = ["parallel"]` only.

---

## 3. No New Dependencies — Verified

Cross-referencing Cargo.toml from docs.rs/crate source for all three versions:

| Dependency | 0.17.0 | 0.19.0 | 0.20.0 | Notes |
|------------|--------|--------|--------|-------|
| nalgebra | 0.33 | 0.33 | 0.33 | Unchanged |
| rand | 0.8 | 0.8 | 0.8 | Unchanged |
| rand_distr | 0.4 | 0.4 | 0.4 | Unchanged |
| rustfft | 6.2 | 6.2 | 6.2 | Unchanged |
| num-complex | 0.4 | 0.4 | 0.4 | Unchanged |
| rayon | 1.10 (optional, parallel) | 1.10 (optional, parallel) | 1.10 (optional, parallel) | Unchanged; the one enabled optional dep |
| faer | 0.23 (optional, linalg only) | 0.23 (optional, linalg only) | 0.23 (optional, linalg only) | Unchanged; gated, not enabled |
| anofox-regression | 0.4 (optional, linalg only) | 0.4 (optional, linalg only) | 0.4 (optional, linalg only) | Unchanged; gated, not enabled |
| serde | optional | optional | optional | Unchanged; not enabled |
| serde_json | optional | optional | optional | Unchanged; not enabled |
| getrandom | optional | optional | optional | Unchanged; not enabled |

**Conclusion:** The dependency tree for `features = ["parallel"]` is byte-for-byte identical across 0.17.0, 0.19.0, and 0.20.0. No new transitive Rust dependencies are introduced by the bump.

---

## 4. Feature Flags — Verified Against docs.rs/crate/fdars-core/0.20.0/source/Cargo.toml

```toml
[features]
default = ["parallel"]
dhat-heap = []
js = ["getrandom/js"]
linalg = ["faer", "anofox-regression"]
parallel = ["rayon"]
serde = ["dep:serde", "dep:serde_json"]
```

| Feature | Enable? | Reason |
|---------|---------|--------|
| `parallel` | YES | Required; rayon parallelism; unchanged from 0.17.0 |
| `linalg` | NO | Requires Rust 1.84 > pyfda MSRV 1.83; adds faer + anofox-regression; not needed for v5.0 |
| `serde` | NO | Not needed for PyO3 bindings |
| `js` | NO | WebAssembly target; not applicable |
| `dhat-heap` | NO | Heap profiling dev tool; not applicable |

This feature set is identical to the feature set used in the 0.17.0 pin.

---

## 5. No New Python Dependencies

Groups A (inference), B (depth/boxplot), and C (basis/smoothing quick wins) are pure PyO3 bindings over existing numpy/PyO3 machinery:

- `TestResult` and `FunctionalBoxplotResult` return types map to PyDict — the same pattern used for `ShiftRegistrationResult` and `KarcherMeanResult` in 0.17.0.
- No new Python package is required in `pyproject.toml` `[project.dependencies]` or any optional extra.
- The advisor extension for inference/boxplot diagnostics uses the existing `anthropic`/`openai`/`gemini`/`ollama` optional extras — no new extras are added.

The existing extras in `pyproject.toml` are unchanged:
```toml
plot          = ["matplotlib>=3.6"]
dev           = ["pytest", "matplotlib>=3.6"]
advisor       = ["anthropic>=0.72.0", "pydantic>=2.0"]
mcp           = ["mcp>=2.0.0"]
openai        = ["openai>=1.40,<2.0", "pydantic>=2.0"]
gemini        = ["google-genai>=1.0,<3.0", "pydantic>=2.0"]
ollama        = ["ollama>=0.6.2", "pydantic>=2.0"]
all-providers = [...]
```

---

## 6. Cargo.lock and Build Implications

After editing `Cargo.toml`:

```bash
cargo update -p fdars-core
```

This updates only the fdars-core entry in `Cargo.lock` without touching other locked dependencies. Since no transitive deps changed names or versions, the lock file diff will be minimal: one crate entry updated (name, version, checksum). Commit the updated `Cargo.lock` alongside the `Cargo.toml` change in the same atomic commit (Phase 30 — crate bump).

After regenerating the lock file, rebuild via maturin and run the full suite:

```bash
maturin develop
pytest
```

The ~426-test suite (426 passed / 4 skipped at v4.0 end state) is the regression gate. Zero test changes are expected from the bump itself — this matches the v4.0 pattern where the 0.14→0.17 bump required zero test changes. The new APIs in 0.20.0 are strictly additive; no existing signatures changed.

---

## 7. CvCriterion Non-Exhaustive — Binding Implication

The upstream release notes for 0.20.0 (as described in PROJECT.md) state that `CvCriterion` is now `#[non_exhaustive]`. This affects the Group C basis/smoothing bindings where `CvCriterion::Aic` is consumed. The binding wrapper must include a forward-compatible fallback arm:

```rust
match criterion_str {
    "cv" => CvCriterion::Cv,
    "aic" => CvCriterion::Aic,
    _ => return Err(PyValueError::new_err(format!("Unknown CvCriterion: {}", criterion_str))),
}
```

This is the same pattern already used for `InterpolationMethod` and `ExtrapolationPolicy` in the 0.17.0 bindings.

---

## 8. Recommended Stack (Unchanged Except Crate Version)

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| fdars-core | **0.20.0** | Rust FDA compute engine | Target of this upgrade; all new inference/depth/basis features live here |
| PyO3 | 0.28 | Rust-to-Python bindings with ABI3 stable interface | Already in place; no change required |
| numpy (pyo3) | 0.28 | Zero-copy NumPy ↔ Rust array exchange | Already in place; no change required |
| maturin | 1.x | Build backend — compiles PyO3 extension, produces wheels | Already in place; no change required |
| Rust toolchain | 1.83 (pyfda MSRV) | Compilation | Safe — upstream MSRV is 1.81 |

### Supporting Libraries (Python, Unchanged)

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| matplotlib | 3.6+ | Plotting for docs examples | All visual worked examples |
| scipy | 1.10+ | Numerical reference (docs examples) | Signal processing, stats in docs |
| scikit-learn | 1.3+ | ML utilities (docs examples) | Clustering/classification examples |
| pandas | current | Metadata handling in Fdata class | DataFrame metadata support |
| pytest | current | Test runner | All 426+ tests |

### Development Tools (Unchanged)

| Tool | Purpose | Notes |
|------|---------|-------|
| maturin develop | Build extension in-place for dev | Run after Cargo.toml bump |
| cargo update -p fdars-core | Refresh Cargo.lock after version bump | Required after version change |
| MkDocs Material 9.5+ | Docs site | No change |
| markdown-exec 1.8+ | Live code execution in docs | No change |

---

## 9. Existing convert.rs Layer — No Changes Required

The existing `src/convert.rs` provides every primitive needed for the new bindings in Groups A, B, and C:

| Converter | Used by new v5.0 bindings |
|-----------|--------------------------|
| `numpy2d_to_fdmatrix` | All new FdMatrix inputs (inference tests, functional_boxplot, basis/smoothing) |
| `fdmatrix_to_numpy2d` | FunctionalBoxplotResult region matrices, smoothed output |
| `numpy1d_to_vec` | `argvals` inputs throughout |
| `vec_to_numpy1d` | Outlier flag vectors, boxplot components |
| `to_pyresult` | All `Result<T, FdarError>` conversions (inference functions are fallible) |
| `to_pyerr` | Direct error wrapping where needed |

`TestResult` and `FunctionalBoxplotResult` will decompose to PyDict using the same pattern as `ShiftRegistrationResult` — no new converter primitives needed.

---

## 10. What NOT to Change

| Item | Why Not |
|------|---------|
| `linalg` feature | Requires Rust 1.84; breaks MSRV; not needed for v5.0 targets |
| PyO3 version | 0.28 is current and correct; no upstream requirement for a newer version |
| numpy (pyo3) version | 0.28 matches PyO3 0.28; no change needed |
| pyproject.toml extras | No new Python dependencies for Groups A/B/C |
| Python CI matrix | 3.9–3.14 unchanged |
| maturin version | No build system change required |
| CI workflows | No changes to `.github/workflows/` needed |

---

## 11. Alternatives Considered

| Item | Recommended | Alternative | When Alternative Makes Sense |
|------|-------------|-------------|------------------------------|
| Version pin style | `"0.20.0"` (caret `^0.20.0`) | `"=0.20.0"` (exact) | Only if upstream has broken semver discipline — not the case here |
| Feature set | `["parallel"]` | `["parallel", "linalg"]` | Only if ridge regression bindings or faer SVD are a v5.0 target — they are not; also breaks MSRV |

---

## Sources

- `https://crates.io/api/v1/crates/fdars-core/0.20.0` — version ID 3012586, publish date 2026-08-16, MSRV 1.81, yanked: No — **HIGH confidence** (crates.io registry API)
- `https://docs.rs/crate/fdars-core/0.20.0/source/Cargo.toml` — complete feature flags, all dependency names+versions, MSRV 1.81 — **HIGH confidence** (docs.rs crate source)
- `https://docs.rs/fdars-core/0.20.0` — feature flag descriptions including explicit "linalg requires Rust 1.84+" statement — **HIGH confidence** (docs.rs generated docs)
- `https://docs.rs/crate/fdars-core/0.17.0/source/Cargo.toml` — baseline dependency set for diff — **HIGH confidence** (docs.rs crate source)
- `https://crates.io/api/v1/crates/fdars-core/0.17.0` — MSRV 1.81, publish date 2026-08-12 — **HIGH confidence** (crates.io registry API)
- `https://docs.rs/crate/fdars-core/0.19.0/source/Cargo.toml` — intermediate version dependency set for diff — **HIGH confidence** (docs.rs crate source)
- `https://crates.io/api/v1/crates/fdars-core/versions` — full version history confirming 0.18.0 was never published; jump is 0.17.0 → 0.19.0 → 0.20.0 — **HIGH confidence** (crates.io registry API)
- `/home/simonm/projects/rust/pyfda/Cargo.toml` — current pin `= "0.17.0"`, MSRV `rust-version = "1.83"` — **HIGH confidence** (local source)

---

*Stack research for: pyfda v5.0 — fdars-core 0.17.0 → 0.20.0 upgrade*
*Researched: 2026-08-17*
