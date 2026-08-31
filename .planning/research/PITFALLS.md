# Pitfalls Research

**Domain:** scikit-learn-compatible estimator layer over a PyO3 functional-data library (fdars v9.0)
**Researched:** 2026-08-31
**Confidence:** MEDIUM — derived from sklearn source, official developer docs, sklearn 1.3–1.6 changelogs,
scikit-fda library analysis, and cross-checked against `check_estimator` issue tracker.

---

## Scope

This file covers pitfalls specific to v9.0's constraint: every wrapped fdars estimator must pass the
**full** `check_estimator` battery with **no exemptions**. Methods that cannot comply are excluded from
the sklearn layer (not exempted). The roadmap should sequence a compliance-triage phase first.

---

## Critical Pitfalls

### Pitfall 1: Mutating Constructor Parameters in `fit` — Breaks `clone` and `get_params` Round-Trip

**What goes wrong:**
`check_estimator` calls `clone(estimator)` before each test. `clone` works by calling `get_params()`
and passing the returned dict back into the constructor. If `__init__` stores its arguments verbatim
but `fit()` modifies them (e.g. derives `self.argvals_` from the constructor's `self.argvals` by
appending, normalising, or replacing it with a computed value), the round-trip breaks: `clone()` of
the fitted estimator re-runs `__init__` with the MODIFIED value, not the original.

Concrete case: `FdarsSmoother(argvals=None)` stores `self.argvals = None`. In `fit(X)`, the code does
`self.argvals = np.linspace(0, 1, X.shape[1])`. Now `get_params()` returns `{"argvals": array([...])}`.
`clone()` passes that array back into `__init__`, which stores the array — but the constructor default
was `None`. The `check_estimator` test `check_get_params_invariance` catches this because the cloned
estimator has different constructor state than the original.

Second case: mutable default — `FdarsEstimator(argvals=np.arange(10))`. Multiple instances share
the same default array object. If any instance modifies `self.argvals` in-place during `fit`, all
instances are corrupted.

**Why it happens:**
FDA estimators naturally compute an effective grid in `fit` (because the input array dimension
determines it). Developers store this computed grid on `self.argvals` (overwriting the constructor
value) for reuse in `transform`/`predict`, not realising this corrupts the `get_params` round-trip.

**How to avoid:**
- The rule: constructor arguments are stored verbatim in `__init__`, never modified. The rule holds
  even for `None`-defaulted arguments.
- In `fit(X)`, derive the effective grid and store it with a TRAILING UNDERSCORE:
  `self.argvals_ = self.argvals if self.argvals is not None else np.arange(X.shape[1])`.
- `transform`/`predict` use `self.argvals_` (fitted attribute), never `self.argvals` (constructor param).
- For mutable defaults, use `None` as the default and build the actual value in `fit`. Never use a
  numpy array or list as a default argument value.
- After `fit`, `get_params()` must still return `{"argvals": None}` (or the original user-supplied
  value), not the derived array.

**Warning signs:**
- `fit()` contains `self.argvals = ...` (no trailing underscore).
- Constructor default is a list or numpy array literal (e.g. `def __init__(self, argvals=np.arange(100))`).
- `check_get_params_invariance` or `check_estimators_pickle` fails.

**Phase to address:**
Compliance-triage phase (phase 1) — establish the trailing-underscore / constructor-verbatim pattern
in the base class or a shared mixin before any individual estimator is written.

---

### Pitfall 2: Missing or Wrong `n_features_in_` — Breaks All Feature-Count Checks

**What goes wrong:**
Every `check_estimator` run exercises `check_n_features_in`, which calls `fit(X_train)` and then
`predict(X_test_wrong_shape)` expecting a `ValueError` with a specific message. If `n_features_in_`
is not set during `fit`, or if it is set to the wrong value (e.g. number of argvals instead of
`X.shape[1]`), the check either raises `AttributeError` or fails to raise the expected error on
mismatched input.

For fdars estimators where `argvals` is a constructor parameter and `X` is `(n_obs, n_points)`:
`n_features_in_` must equal `n_points` — the second dimension of `X`. This is always `X.shape[1]`,
regardless of whether `argvals` is supplied.

**Why it happens:**
FDA estimators think of "features" as "grid points" and may store `len(self.argvals_)` separately.
Developers forget that sklearn's `n_features_in_` must be set via `validate_data()` (which reads
`X.shape[1]`), not manually.

**How to avoid:**
- Call `validate_data(self, X, ...)` at the start of `fit`. This automatically sets `n_features_in_`.
  Use `sklearn.utils.validation.validate_data` (the public function introduced in sklearn 1.6;
  `self._validate_data(X)` works but is deprecated on the path to 1.8).
- In `transform`/`predict`, call `validate_data(self, X, reset=False)` to trigger the feature-count
  consistency check automatically.
- Never set `self.n_features_in_` manually — use `validate_data()` and let sklearn set it.

**Warning signs:**
- `fit()` sets `self.n_features_in_` manually.
- `transform()` calls `check_array(X)` but not `validate_data(self, X, reset=False)`.
- `check_n_features_in` raises `AttributeError: 'FdarsSmoother' object has no attribute 'n_features_in_'`.

**Phase to address:**
Compliance-triage phase (phase 1) — build into the base class `fit` skeleton so all estimators
inherit the correct pattern.

---

### Pitfall 3: Missing Trailing-Underscore Fitted Attributes — `check_is_fitted` Fails

**What goes wrong:**
`check_estimator` calls `check_is_fitted()` on unfitted instances and expects `NotFittedError`.
Then it fits the estimator and calls `check_is_fitted()` again expecting no error. By default,
`check_is_fitted` detects fitted state by scanning for any attribute ending in `_`. If `fit()`
stores results in attributes WITHOUT trailing underscores (e.g. `self.components`, `self.mean`,
`self.bandwidth`), the estimator appears unfitted even after `fit`, and `predict`/`transform`
calls raise `NotFittedError` unexpectedly.

**Why it happens:**
fdars result dicts use names like `components`, `eigenvalues`, `scores` without trailing underscores.
It is natural to copy the key name from the dict directly into a `self` attribute.

**How to avoid:**
- All attributes learned during `fit` must end with `_`: `self.components_`, `self.eigenvalues_`,
  `self.bandwidth_`, `self.labels_`, etc.
- Constructor parameters are stored without underscore (`self.n_components`, `self.argvals`).
- If using a custom `__sklearn_is_fitted__` method, implement it explicitly and test it separately.
- Add a lint/convention check: grep for `self\.\w[^_\s]+ =` inside `fit()` methods to catch
  non-underscore-suffixed assignments.

**Warning signs:**
- `check_is_fitted(estimator)` raises `NotFittedError` after `fit(X)` has been called.
- `predict` or `transform` raises `NotFittedError` in production even after fitting.
- `estimator_checks.check_estimators_pickle` fails because pickle state is incomplete.

**Phase to address:**
Compliance-triage phase (phase 1) — enforce in the base class and in code review.

---

### Pitfall 4: `check_fit2d_1sample` and `check_fit2d_1feature` — Error Message Substring Contract

**What goes wrong:**
`check_estimator` feeds the estimator a `(1, n_features)` array (one sample) and a `(n_samples, 1)`
array (one feature). If the estimator cannot handle these inputs, it MUST raise `ValueError` with
a message containing specific substrings — or the check fails even if the error is legitimate.

Required substrings for 1-sample rejection: `"1 sample"`, `"n_samples = 1"`, `"n_samples=1"`,
`"one sample"`, `"1 class"`, or `"one class"`.

Required substrings for 1-feature rejection: `"1 feature(s)"`, `"n_features = 1"`, or `"n_features=1"`.

If the estimator raises a different error (e.g. Rust panic, `LinAlgError`, or a generic "cannot
compute" message), the check fails. If the estimator silently produces garbage output (e.g.
all-zeros components), the check may pass but correctness is violated.

For functional data, ALL estimators have a minimum sample requirement (you need at least as many
samples as components/clusters/basis functions), and the 1-sample / 1-feature case almost always
falls below the minimum. This means these checks will exercise the error-message contract
frequently.

**Why it happens:**
fdars-core raises `FdarError` with domain-specific messages ("matrix is singular", "not enough
curves for FPCA"). The PyO3 wrapper converts these to `PyValueError` but with the fdars-core
message text, which does not match the sklearn substring requirements.

**How to avoid:**
- In the Python wrapper's `fit()`, validate `n_samples` and `n_features` BEFORE calling fdars-core,
  and raise `ValueError` with sklearn-compliant messages:
  ```python
  if X.shape[0] < self._min_samples:
      raise ValueError(
          f"n_samples={X.shape[0]} is too small; this estimator requires "
          f"at least {self._min_samples} samples."
      )
  ```
- Define `_min_samples` as a class-level property so each estimator can declare its minimum.
- For FPCA/basis estimators: `_min_samples = self.n_components + 1` (must exceed component count).
- For clustering: `_min_samples = self.n_clusters * 2` (need enough samples per cluster).
- These Python-layer guards run BEFORE the fdars-core call, preventing the harder-to-interpret
  Rust error from propagating.

**Warning signs:**
- `check_fit2d_1sample` fails with "AssertionError: expected ValueError with '1 sample' substring".
- The error message that appears is in German or uses fdars-internal terminology.
- Any `ValueError` from fdars-core that propagates with the raw Rust error text.

**Phase to address:**
Compliance-triage phase (phase 1) and per-estimator implementation. Every estimator needs explicit
input guards. The minimum-sample logic determines which methods can be compliant vs. excluded.

---

### Pitfall 5: `check_fit_idempotent` — SVD Sign Ambiguity in FPCA

**What goes wrong:**
`check_estimator` runs `fit(X)` twice and checks that the results are identical (comparing
`transform(X)` output). Truncated SVD (used in FPCA/PCA variants) has sign ambiguity: each
singular vector can be negated without changing the mathematical result. If the SVD implementation
returns different sign conventions across runs (common when using LAPACK with different random
seeding or thread scheduling), `components_[0]` may be `[+0.7, +0.3]` in the first fit and
`[-0.7, -0.3]` in the second. The test sees different `transform(X)` values and fails.

fdars-core's `fpca_1d` and related functions use SVD internally. The sign convention is not
guaranteed to be deterministic across fits unless explicitly enforced.

**Why it happens:**
FPCA over Rust/LAPACK does not canonicalise sign by default. The rayon parallel feature makes
this more likely because thread scheduling affects numerical precision of intermediate sums.

**How to avoid:**
- After extracting components from fdars-core, apply a deterministic sign convention in the
  Python wrapper: flip each component so its element with the largest absolute value is positive.
  This is the same approach used in sklearn's `PCA._fit_full`.
  ```python
  max_abs_cols = np.argmax(np.abs(self.components_), axis=1)
  signs = np.sign(self.components_[range(n_comp), max_abs_cols])
  self.components_ *= signs[:, np.newaxis]
  ```
- Apply the same sign flip to `self.scores_` (the projected data) so `transform` is consistent.
- Test with two consecutive `fit(X)` calls and assert `np.allclose(t1, t2)`.

**Warning signs:**
- `check_fit_idempotent` fails intermittently (sign ambiguity is non-deterministic by nature).
- The test passes on one machine but fails on another (different LAPACK implementation).
- `fit` twice produces `components_` that differ only in sign.

**Phase to address:**
Per-estimator implementation phase for FPCA transformers. Sign canonicalisation must be in the
initial implementation, not added later.

---

### Pitfall 6: Grid-Changing Transformers Break Downstream `n_features_in_` in Pipeline

**What goes wrong:**
A smoothing or FPCA transformer changes the number of "features" that downstream estimators see:

- `FdarsSmoother.transform(X)` may return `X_smoothed` with the same shape `(n_obs, n_points)` —
  the grid is unchanged, so `n_features_in_` flows through correctly.
- `FdarsFPCA.transform(X)` returns scores `(n_obs, n_components)` — the grid is gone, replaced
  by component indices. A downstream sklearn estimator (e.g. `LogisticRegression`) fits on the
  scores and its `n_features_in_` is `n_components`, not `n_points`.
- `FdarsBasisTransformer.transform(X)` returns basis coefficients `(n_obs, n_basis)` — again, the
  grid is replaced.

The `check_estimator` Pipeline tests (`check_pipeline_consistency`) fit a
`Pipeline([('transform', estimator), ('final', LinearRegression())])` and verify that the pipeline
survives `clone`, `fit`, `predict`. If the transformer's `transform` output has a different number
of columns than the input, and the pipeline's clone tries to re-validate with the original input
shape, the downstream `LinearRegression` may reject the input.

More subtly: the `argvals` constructor parameter of the DOWNSTREAM fdars estimator in a pipeline
is derived from the upstream transformer's OUTPUT — but the user may supply `argvals` expecting
the original grid. After `fit`, the downstream estimator's `argvals_` is `np.arange(n_components)`,
not the user-supplied grid.

**Why it happens:**
Standard sklearn transformers (PCA, StandardScaler) either preserve shape or reduce features in a
well-understood way that sklearn pipelines handle. FDA transformers add a conceptual layer where
"grid" and "features" are the same thing — but after FPCA, the "features" are component indices,
not grid points. Users expect `argvals` to mean grid points throughout, but FPCA destroys the grid.

**How to avoid:**
- Shape-preserving transformers (smoothers, interpolation, imputation) are safe in pipelines.
  Their `transform` output has the same `n_features` as input.
- Dimensionality-reducing transformers (FPCA, basis expansion) must document explicitly that they
  change `n_features`. Their output is NOT functional data — it is a score matrix suitable for
  downstream sklearn estimators, not for downstream fdars estimators.
- Do NOT wrap FPCA as a `TransformerMixin` that outputs scores AND claim the output is still
  functional data with grid interpretation. Instead, clearly name it `FdarsFPCAScores` or similar
  to signal that downstream estimators receive score matrices, not functional data.
- For Pipeline compatibility: the FPCA transformer's `transform` output must be a plain numpy array
  with no `argvals` metadata attached (sklearn does not pass metadata through pipeline steps unless
  using the metadata routing API).

**Warning signs:**
- A `Pipeline([FdarsFPCA(), FdarsSmoother()])` fails because `FdarsSmoother` checks `argvals` length
  against `n_features_in_` which is now `n_components`, not `n_points`.
- Users report that `Pipeline([FdarsFPCA(), LinearRegression()])` works but
  `Pipeline([FdarsFPCA(), FdarsBasisTransformer()])` fails with a shape mismatch.
- `check_pipeline_consistency` fails on any fdars transformer that changes output shape.

**Phase to address:**
Compliance-triage phase (phase 1) — categorise transformers as shape-preserving vs. dimensionality-
reducing during the triage scan. This determines which can be composed in pipelines with other
fdars estimators vs. only with standard sklearn estimators.

---

### Pitfall 7: Sklearn Version Drift — `_get_tags` / `_more_tags` → `__sklearn_tags__` Migration

**What goes wrong:**
The sklearn estimator tags API changed significantly across the 1.3–1.6 range:

- **sklearn 1.3–1.5**: Tags set via `_more_tags()` returning a dict; `_get_tags()` aggregates.
  Tags like `"no_validation"`, `"poor_score"`, `"non_deterministic"` are dict string keys.
- **sklearn 1.6**: `__sklearn_tags__()` introduced as the public API, returns a `Tags` dataclass.
  `_more_tags`, `_get_tags`, `_safe_tags` raise `DeprecationWarning` (to be removed in 1.8).
  `_estimator_type` class attribute deprecated — use `ClassifierMixin`/`RegressorMixin` etc.
  `_xfail_checks` tag deprecated — use `expected_failed_checks` parameter in `check_estimator()`.
  `_validate_data()` deprecated in favour of `validate_data()` (public function).
  `assert_all_finite` parameter renamed to `ensure_all_finite`.
- **sklearn 1.7**: Python 3.10 minimum. Python 3.9 support dropped.
- **sklearn 1.8**: Removal of `_more_tags`, `_get_tags`, `_safe_tags`, `_estimator_type`,
  `_xfail_checks`, `assert_all_finite`.
- **sklearn 1.9**: Python 3.11 minimum.

The fdars [sklearn] extra must declare a minimum sklearn version. If it targets `sklearn>=1.3` (to
support Python 3.9), it cannot use `__sklearn_tags__` (1.6+) exclusively. If it targets `sklearn>=1.6`,
Python 3.9 with only sklearn 1.5 available cannot install the extra.

**Why it happens:**
The sklearn developer API changes faster than user expectations. Third-party libraries (catboost,
xgboost) have been caught by this exact transition; catboost hit AttributeError on `__sklearn_tags__`
in sklearn 1.8.x (confirmed from GitHub issues). Libraries that support a wide Python/sklearn matrix
must handle both the old and new API.

**How to avoid:**
- Set `scikit-learn>=1.4` as the minimum for the `[sklearn]` extra. This covers Python 3.9–3.12
  (sklearn 1.4–1.5 support Python 3.9+). sklearn 1.7 drops Python 3.9, so the extra must work
  across sklearn 1.4–1.9 (the realistic range for Python 3.9–3.14).
- For cross-version compatibility, implement BOTH `_more_tags` (for sklearn 1.3–1.5 compat) AND
  `__sklearn_tags__` (for 1.6+). Use a try/import to detect which API is present:
  ```python
  try:
      from sklearn.utils import Tags  # sklearn 1.6+
      def __sklearn_tags__(self):
          tags = super().__sklearn_tags__()
          tags.non_deterministic = True
          return tags
  except ImportError:
      def _more_tags(self):
          return {"non_deterministic": True}
  ```
  The `sklearn-compat` PyPI package (noted in search results) provides a compatibility shim.
- In CI: test with BOTH sklearn 1.4 (Python 3.9) and sklearn 1.6+ (Python 3.10+) to catch both
  API paths. The `[sklearn]` optional extra tests must run on the full Python 3.9–3.14 matrix.
- For `check_estimator()`: in sklearn 1.6+, use `expected_failed_checks={}` parameter; in 1.3–1.5,
  use `_xfail_checks` tag. The compliance goal is NO expected failures — but the mechanism for
  running the suite must be version-aware.

**Warning signs:**
- CI runs only one sklearn version.
- `DeprecationWarning: _more_tags is deprecated` appears on sklearn 1.6.
- `AttributeError: 'FdarsFPCA' object has no attribute '__sklearn_tags__'` appears on sklearn 1.8.
- The `[sklearn]` extra declares `scikit-learn>=1.6` but the fdars base supports Python 3.9 (which
  can only install sklearn up to 1.6 while sklearn 1.7+ requires Python 3.10).

**Phase to address:**
Compliance-triage phase (phase 1) — establish the version compatibility strategy before writing
any estimator code. This is a cross-cutting concern affecting every estimator.

---

### Pitfall 8: Stochastic Estimators — `check_methods_sample_order_invariance` Fails Without Proper Seeding

**What goes wrong:**
`check_estimator` includes `check_methods_sample_order_invariance` and `check_methods_subset_invariance`.
These checks shuffle the input data and verify that `fit(X).transform(X)` and
`fit(X_shuffled).transform(X_shuffled_back)` yield the same result. Any estimator whose result
depends on sample order (e.g. K-means initialisation, greedy clustering, elastic alignment order)
will fail this check.

For fdars clustering estimators that wrap `fdars.clustering.cluster_kmeans`: the Rust code uses
rayon for parallelism. Even with a fixed `random_state` in the Python wrapper, if rayon's thread
scheduling affects the result, the estimator is effectively non-deterministic regardless of
`random_state`. This would make the check fail.

For FPCA: the SVD is deterministic given the same input, so order invariance holds IF sign
canonicalisation is applied (see Pitfall 5). Without sign canonicalisation, FPCA also fails.

**Why it happens:**
Clustering is inherently sensitive to initialisation. fdars-core's clustering may use a seed
internally but the parallelism makes the seed insufficient for full order invariance.

**How to avoid:**
- For estimators with `random_state` that can be made fully deterministic: accept `random_state`
  as a constructor parameter, use `sklearn.utils.check_random_state(self.random_state)` to get
  a `RandomState` instance, and pass a derived seed to the fdars function. Verify with a test
  that `random_state=42` produces identical results on two calls with different sample ordering.
- If full order invariance CANNOT be achieved (e.g. rayon non-determinism persists despite seeding):
  set `non_deterministic=True` in tags. This skips both order/subset invariance checks. But this
  means the estimator will be tagged as non-deterministic, which is visible to users.
- Recommendation: functional clustering (k-means on curves) should expose `random_state` and use
  it to seed the Rust random state. If rayon still causes non-determinism, disable parallelism
  during sklearn-wrapped fitting (add a `parallel=False` path in fdars-core binding) OR set the
  non_deterministic tag.
- Elastic alignment (registration) is inherently order-sensitive. If wrapping as a transformer,
  test whether order invariance holds. If it does not, either exclude it or set non_deterministic.

**Warning signs:**
- `check_methods_sample_order_invariance` fails intermittently.
- The estimator passes the check with `random_state=42` but fails without it.
- rayon thread count changes affect the result.

**Phase to address:**
Per-estimator implementation phase for stochastic methods (clustering, elastic alignment).
Determinism testing must be done as part of compliance-triage.

---

### Pitfall 9: Minimum Sample / Grid-Point Requirements — The Category That Forces Exclusion

**What goes wrong:**
`check_estimator` uses test data of approximately 40 samples and 3–10 features by default for most
checks. The `check_fit2d_1sample` check uses 1 sample. The `check_fit2d_1feature` check uses 1
feature (grid point). Many fdars methods have HARD minimum requirements that cannot be satisfied
by these small inputs:

| Method Category | Minimum Requirement | check_estimator Behavior |
|-----------------|--------------------|--------------------|
| FPCA (n_components=k) | n_samples > n_components; n_points > n_components | Auto-adjusts n_components=1; passes IF 1-component FPCA works on 3-point grid |
| Smoothing (df parameter) | n_points >> df (spline degrees of freedom) | May fail on 1-feature (1-point grid cannot be smoothed) |
| Clustering (n_clusters=k) | n_samples >= n_clusters | Auto-adjusts n_clusters=1; passes if 1-cluster trivially assigns all samples to 1 cluster |
| Basis expansion (n_basis) | n_points >= n_basis | May fail on 1-feature grid |
| Elastic alignment | n_samples >= 2 (need at least two curves to align) | check_fit2d_1sample will fail if n_samples=1 raises wrong error |
| Functional depth (reference set) | n_reference >= 2 | Fails on 1-sample reference |
| Functional regression (FLM) | n_samples > n_basis | Underdetermined system on tiny samples |

`check_estimator` automatically adjusts `n_components` to 1 and `n_clusters` to 1 before running
checks (confirmed from sklearn source: the checking framework inspects the estimator's parameters
and sets them to minimum-safe values). This means estimators with `n_components` attribute may
survive the tiny-sample checks IF 1-component operation is valid.

The FPCA case: `check_estimator` sets `n_components=1`. With 1 component and ~40 samples, standard
FPCA should work. With `check_fit2d_1sample` (1 sample, n_components=1), FPCA must raise a
sklearn-compliant `ValueError`. With `check_fit2d_1feature` (1 feature, n_components=1), a 1-point
grid cannot be smoothed to extract a component — this likely raises a hard Rust error.

Methods that predictably FAIL full check_estimator and should be EXCLUDED from the sklearn layer:
- **Elastic alignment / registration**: requires n_samples >= 2; `check_fit2d_1sample` is
  unpassable without special-casing that makes the result meaningless.
- **Functional depth (as transformer outputting scalar depth values)**: the OutlierMixin contract
  requires `predict` to return +1/-1 integers. fdars depth functions return float depth values,
  not binary labels. Wrapping as `OutlierMixin` requires a thresholding step, which is stateful
  and complicates the contract significantly.
- **Basis smoothing with cross-validated df**: the CV process requires enough samples for
  cross-validation folds; 1-sample input is structurally impossible for CV. The error path is
  not trivially sklearn-compliant.
- **Functional GLM (exponential family)**: requires n_samples >> n_parameters; 1-feature check
  creates a degenerate system that triggers hard Rust-level linear algebra errors.
- **Elastic multinomial classification**: multi-class check needs >= 3 classes; with tiny samples
  this is structurally infeasible.

Methods that predictably PASS full check_estimator with correct implementation:
- **FdarsSmoother (fixed bandwidth)**: shape-preserving, works on any n_points >= 1 (kernel
  smoothing with bandwidth handles edge cases gracefully), returns same shape.
- **FdarsFPCA (scores transformer)**: passes IF sign canonicalisation applied and n_components=1
  works on small grids.
- **FdarsBasisTransformer (fixed basis)**: shape-changing but predictable; n_basis=1 (auto-adjusted)
  should work.
- **FdarsMean (as transformer that centers)**: shape-preserving, trivially handles 1 sample.
- **FdarsFunctionalRegressor (scalar-on-function)**: RegressorMixin; with n_components=1 and ~40
  samples, should pass. Needs explicit 1-sample guard.
- **FdarsFunctionalClassifier (supervised classification)**: ClassifierMixin; with n_clusters=1 and
  2 classes, should pass with correct guards.

**How to avoid:**
- Run compliance triage BEFORE building the full estimator layer. For each candidate method:
  1. Write a minimal wrapper with the correct Mixin.
  2. Run `check_estimator()` and record which checks pass and which fail.
  3. Classify as PASS, PASS-WITH-FIXES (guards needed), or EXCLUDE.
- The earliest detection strategy: a triage script that runs `check_estimator()` on skeleton
  estimators (minimal `fit`/`transform` calling fdars) and captures the failing check names.
  This can be done in 1–2 days and determines the entire scope of the sklearn layer.
- For the EXCLUDE list: document the specific failing check name and reason in the coverage list
  (a required v9.0 deliverable).

**Warning signs:**
- A method's `fit` raises `ValueError` or `LinAlgError` when called with n_samples=40 (the
  standard test size) during initial triage — it will certainly fail on 1-sample check.
- The method has a non-trivial "minimum samples" requirement that cannot be expressed as a
  simple `n_samples=1` guard with a compliant error message.

**Phase to address:**
Phase 1 MUST be a compliance-triage phase. Do NOT build all estimators and then discover exclusions
late. The triage determines which methods are in scope for implementation phases.

---

### Pitfall 10: `check_estimators_nan_inf` — Non-Finite Input Rejection Without Compliant Path

**What goes wrong:**
`check_estimator` feeds `X` arrays containing `np.inf` and `np.nan` to `fit()`. By default, the
check expects the estimator to REJECT non-finite input with a `ValueError`. If the estimator
passes non-finite data to fdars-core, the Rust code may panic, produce NaN outputs silently, or
raise an opaque error. None of these are compliant — only a `ValueError` is.

If an estimator sets `allow_nan=True` in tags (to indicate it handles NaN), then the check tests
that it actually handles NaN without raising an error. For fdars methods, imputation is the only
category that legitimately handles NaN (by design).

**Why it happens:**
fdars-core assumes well-formed input. The PyO3 bindings do not validate for non-finite values
before passing arrays to Rust. A panic in Rust code propagates as a Python `RuntimeError`
(not `ValueError`) or as a process abort in some configurations.

**How to avoid:**
- In the Python-layer `fit()`, call `validate_data(self, X, ensure_all_finite=True)` (not
  `assert_all_finite` — that parameter name was deprecated in sklearn 1.6). This raises a
  compliant `ValueError` with the standard message before any fdars-core call.
- The FdarsImputer/FdarsMissingValueTransformer should set `allow_nan=True` in its tags AND
  implement NaN handling correctly. All other estimators should NOT set `allow_nan=True`.
- Use `ensure_all_finite` not `force_all_finite` (the newer parameter name from sklearn 1.6+).

**Warning signs:**
- `check_estimators_nan_inf` fails with `RuntimeError` or process abort (Rust panic propagation).
- An estimator sets `allow_nan=True` but silently ignores NaN in computation instead of handling it.
- `validate_data(self, X, ensure_all_finite=True)` is not called before fdars-core dispatch.

**Phase to address:**
Compliance-triage phase (phase 1) — add the `validate_data(ensure_all_finite=True)` call to the
base class `fit` skeleton so all estimators inherit it. The imputer is the only exception.

---

### Pitfall 11: `check_dtype_object` and Float32/Float64 Casting

**What goes wrong:**
`check_estimator` runs `check_dtype_object` which passes `X` with dtype `object` (Python objects
array) and expects a `ValueError`. It also runs dtype-casting checks with `float32` input.
fdars-core expects `float64` arrays. If the PyO3 binding receives `float32` input, it may:
1. Accept it silently and produce wrong results (silent precision loss), or
2. Raise a Rust `TypeError` that propagates as a non-compliant Python error.

The sklearn convention is that `float32` input should be preserved as `float32` if the estimator
supports it. If the estimator only supports `float64`, `validate_data` with `dtype="numeric"`
will cast `float32` to `float64` automatically — BUT this means the estimator accepts `float32`
input and silently upcasts it, which is the CORRECT behavior (not a failure).

Object-dtype arrays must raise `ValueError`. The fdars-core binding will raise some error, but it
may not be a `ValueError` with the right message.

**How to avoid:**
- Use `validate_data(self, X, dtype="numeric")` which handles both object-dtype rejection (raises
  `ValueError`) and float32/float64 casting (upcasts float32 to float64 if needed).
- Do NOT use `dtype=np.float64` explicitly — this rejects float32 input with a non-compliant error
  instead of upcasting it.
- After `validate_data`, the array is guaranteed to be numeric and contiguous — safe to pass to fdars.

**Warning signs:**
- `check_dtype_object` fails with a Rust `TypeError` instead of `ValueError`.
- Passing `float32` arrays to an fdars estimator raises `TypeError` instead of silently upcasting.
- Tests pass with `float64` input only.

**Phase to address:**
Compliance-triage phase (phase 1) — add `dtype="numeric"` to `validate_data` in the base class skeleton.

---

### Pitfall 12: `OutlierMixin` — `predict` Must Return +1/-1, Not Float Depths

**What goes wrong:**
fdars outlier detection methods (`tvdmss`, `muod`, `sequential_transform`, depthgram) return
outlier INDICES or depth-based scores, not binary +1/-1 arrays. The `OutlierMixin` contract
requires:
- `predict(X)` returns `ndarray` of shape `(n_samples,)` with values in `{-1, +1}` only
  (-1 = outlier, +1 = inlier).
- `fit_predict(X)` does the same (provided by `OutlierMixin.fit_predict` which calls `fit` then
  `predict`).
- `score_samples(X)` may return a float score (lower = more anomalous) — but only if implemented.

If `predict()` returns a float array (depth scores), the check `check_outliers_train` fails
because it asserts the values are in `{-1, +1}`.

**Why it happens:**
fdars outlier methods return indices of outliers, not binary membership. Converting to +1/-1
requires choosing a threshold, which is a stateful decision made during `fit`. Developers may
expose the raw fdars output directly.

**How to avoid:**
- During `fit(X)`: compute outlier flags (using the fdars method) and store the THRESHOLD
  or decision boundary as `self.threshold_` (a fitted attribute).
- During `predict(X)`: compute outlier scores for new data, apply `self.threshold_`, and return
  `np.where(scores < self.threshold_, -1, +1)`.
- The `decision_function(X)` method can return float scores.
- Verify: `np.unique(estimator.predict(X))` must be a subset of `[-1, 1]`.
- Note: this requires fdars outlier methods to produce a continuous score for NEW data (not
  just flags on training data). Methods that only flag training outliers (non-transductive)
  cannot implement `predict(X_new)` — these must be EXCLUDED from the OutlierMixin layer.

**Warning signs:**
- `check_outliers_train` fails with "ValueError: predict did not return +1/-1 labels".
- `predict(X)` returns a float array (depth values or distance scores).
- The method only flags training outliers and cannot score new samples.

**Phase to address:**
Compliance-triage phase (phase 1) — check whether each fdars outlier method supports scoring
new samples vs. only flagging training samples. Non-transductive methods are EXCLUDED.

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Using `_more_tags()` only (no `__sklearn_tags__`) | Works on sklearn 1.3–1.5, less code | DeprecationWarning on 1.6, AttributeError on 1.8 | Never — implement both or use sklearn-compat shim |
| Setting `n_features_in_` manually instead of via `validate_data` | Avoids sklearn import in `fit` | Breaks `check_n_features_in`; inconsistent with feature name tracking | Never |
| Not applying SVD sign canonicalisation | Simpler code | `check_fit_idempotent` fails intermittently | Never for FPCA transformers |
| Skipping `check_fit2d_1sample` guard | Less boilerplate | Propagates Rust panics or non-compliant errors; test fails | Never |
| Wrapping every fdars method regardless of compliance | Maximum API surface | Compliance failures cascade; excluded methods poison the battery for the whole module | Never — triage first, implement only compliant subset |
| Using `np.arange(n_features)` as default `argvals` without None sentinel | Fewer conditionals | Constructor parameter is computed, not verbatim; breaks `clone` round-trip | Never — use `None` as default, derive in `fit` |

---

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| `validate_data()` in sklearn 1.3 vs 1.6+ | `validate_data(self, X)` is public in 1.6; `self._validate_data(X)` works in 1.3–1.5 but is deprecated | Use `validate_data(self, X)` from `sklearn.utils.validation` in 1.6+; fall back to `self._validate_data(X)` if not available |
| `check_estimator` with `expected_failed_checks` | Available in sklearn 1.6+; using it in 1.5 raises TypeError | Use `try/except` around the parameter or version-check `sklearn.__version__` |
| `ensure_all_finite` vs `force_all_finite` vs `assert_all_finite` | Three different parameter names across versions | Use `ensure_all_finite` (valid 1.6+); `force_all_finite` for 1.0–1.5 compatibility |
| `_validate_data` deprecation | Calling `self._validate_data()` on sklearn 1.6+ raises DeprecationWarning | Import and use `sklearn.utils.validation.validate_data(self, X)` |
| sklearn `Tags` dataclass fields | Tags fields changed between pre-1.6 dict keys and 1.6+ dataclass fields | Never hard-code field names; always call `super().__sklearn_tags__()` first and modify fields |
| fdars PyO3 numpy array dtype | fdars-core expects `float64`; passing `float32` may succeed silently or cause type mismatch in Rust | Always call `validate_data(self, X, dtype="numeric")` which upcasts; never pass raw arrays to fdars before validation |

---

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| Calling `validate_data` then converting to fdars format (two copies) | Slow fit for large n_obs | Accept the two copies as necessary; document the copy overhead in docstring | Above n_obs=10,000 (measurable overhead) |
| Re-deriving argvals in every `transform` call | Redundant work per call | Derive in `fit`, store as `self.argvals_`, reuse in `transform` | On any repeated `transform` call |
| sklearn cross-validation with fdars estimator that has high per-fit cost | CV with 5 folds × GridSearchCV × parameter grid is very slow | Provide fast `__init__` defaults; warn in docs that CV on large grids is expensive | With n_obs > 1000, grid > 100 points |

---

## "Looks Done But Isn't" Checklist

- [ ] **Constructor verbatim storage:** Every constructor parameter is stored verbatim as `self.param = param` in `__init__` with NO computation — verify that `estimator.get_params() == constructor_kwargs` after `__init__` (before `fit`).
- [ ] **Trailing underscore discipline:** Every attribute set in `fit()` ends with `_` — grep for `self\.\w+[^_] =` inside all `fit` methods.
- [ ] **`n_features_in_` via validate_data:** All `fit()` methods call `validate_data(self, X, ...)` not `self.n_features_in_ = X.shape[1]` — grep for `self.n_features_in_` to catch manual sets.
- [ ] **Sign canonicalisation for FPCA:** After extracting components, the sign-flip step (`components_ *= signs[:, np.newaxis]`) is applied — run `fit(X); fit(X)` twice and assert `np.allclose(transform(X_v1), transform(X_v2))`.
- [ ] **Error message substrings:** Every `n_samples` guard raises `ValueError` with "1 sample" or "n_samples=N" — run `check_estimator` on a minimal instance and check that `check_fit2d_1sample` passes.
- [ ] **Non-finite rejection:** `validate_data(ensure_all_finite=True)` is called before fdars dispatch — pass `np.array([[np.inf, 1.0]])` to `fit` and verify `ValueError` (not `RuntimeError` or panic).
- [ ] **Tags dual-API:** Both `_more_tags()` (for sklearn 1.3–1.5) and `__sklearn_tags__()` (for 1.6+) are implemented or a compat shim is used — test with both sklearn versions in CI.
- [ ] **OutlierMixin predict returns +1/-1:** `np.unique(estimator.fit(X).predict(X))` is a subset of `[-1, 1]` with integer dtype.
- [ ] **Pipeline n_features flow:** A `Pipeline([FdarsSmoother(), LinearRegression()])` survives `clone(pipeline)`, `pipeline.fit(X, y)`, `pipeline.predict(X)` end-to-end.
- [ ] **Exclusion list documented:** Every fdars method that fails compliance triage is recorded in `python/fdars/sklearn/COVERAGE.md` with the failing check name — verified by the triage phase's acceptance criterion.

---

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Constructor mutation discovered after estimators are built | HIGH | Rename derived attributes to trailing-underscore variants across all estimators; audit all `get_params` round-trips |
| Tags API mismatch on sklearn upgrade | MEDIUM | Add `__sklearn_tags__` alongside `_more_tags`; test on new sklearn version; release patch |
| SVD sign ambiguity discovered in production | MEDIUM | Add sign canonicalisation step; bump minor version; the fix is isolated to FPCA estimator |
| Exclusion of a method discovered late (after docs are written) | HIGH | Revise coverage list, docs, and tests; cost scales with how much surrounding code was built for the excluded method |
| `check_fit2d_1sample` fails with Rust panic | LOW | Add Python-layer guard before fdars-core call; Rust error never reaches check |

---

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| P1: Constructor mutation | Phase 1 (compliance-triage): base class pattern | `get_params()` round-trip test before any other estimator |
| P2: Missing `n_features_in_` | Phase 1: base class fit skeleton | `check_n_features_in` passes on all estimators |
| P3: Missing trailing underscore | Phase 1: base class + code review | `check_is_fitted` passes on unfitted and fitted instances |
| P4: Error message substring contract | Phase 1 (triage) + per-estimator | `check_fit2d_1sample` and `check_fit2d_1feature` pass |
| P5: SVD sign ambiguity | Per-estimator (FPCA phase) | `check_fit_idempotent` passes; two consecutive fits give identical transform output |
| P6: Grid-changing transformers in Pipeline | Phase 1 (triage): categorise as shape-preserving vs. reducing | `check_pipeline_consistency` passes for shape-preserving; documented as "not pipeline-composable" for reducing |
| P7: Sklearn version drift | Phase 1: version compat strategy | CI runs sklearn 1.4 (Python 3.9) AND sklearn 1.6+ (Python 3.10+) |
| P8: Stochastic estimator order invariance | Per-estimator (clustering/alignment phase) | `check_methods_sample_order_invariance` passes OR `non_deterministic=True` tag set |
| P9: Minimum sample/grid exclusions | Phase 1 (triage): compliance scan | Triage script produces PASS/EXCLUDE list before implementation begins |
| P10: Non-finite rejection | Phase 1: base class validation | `check_estimators_nan_inf` passes |
| P11: Object dtype / float32 casting | Phase 1: `dtype="numeric"` in base | `check_dtype_object` passes |
| P12: OutlierMixin +1/-1 contract | Phase 1 (triage) + per-estimator | `check_outliers_train` passes; `np.unique(predict(X))` subset of `[-1, 1]` |

---

## Predictable PASS vs. EXCLUDE Classification

Based on research against sklearn source, scikit-fda patterns, and fdars method categories:

### Predictable PASS (with correct implementation)

| Method Category | Key Implementation Requirements |
|-----------------|----------------------------------|
| Functional smoother (fixed bandwidth/lambda) | Shape-preserving; `validate_data` handles 1-feature; compliant ValueError for 1-sample |
| FPCA scorer (outputs scores, not functional data) | Sign canonicalisation; n_components=1 must work; 1-sample guard with compliant message |
| Basis representation (fixed basis, fixed n_basis) | n_basis=1 auto-adjust; 1-sample guard; shape-change documented |
| Functional normalisation / centering (mean subtraction) | Shape-preserving; trivially handles 1 sample |
| Interpolation / imputation | `allow_nan=True` tag for imputer; shape-preserving |
| Scalar-on-function regression (FPC-LM, PLS) | RegressorMixin; n_components=1; compliant guards |
| Functional classifier (supervised) | ClassifierMixin; n_clusters=1 equiv; multi-class tag set correctly |

### Predictable EXCLUDE (with expected failing check)

| Method Category | Failing Check | Reason |
|-----------------|--------------|--------|
| Elastic alignment / registration | `check_fit2d_1sample` | Requires n_samples >= 2; 1-sample fit is structurally impossible and cannot be made compliant without making the method meaningless |
| Basis smoothing with CV (AIC/GCV selection) | `check_fit2d_1sample` | CV requires multiple samples; 1-sample path is not implementable with compliant error |
| Functional depth as OutlierMixin | `check_outliers_train` | fdars depth methods return float scores, not +1/-1; transductive-only methods cannot `predict(X_new)` |
| Functional GLM (exponential family) | `check_fit2d_1sample` | Degenerate linear system; Rust-level error on tiny inputs; non-compliant error path |
| Elastic multinomial classifier | `check_estimators_nan_inf` OR `check_fit2d_1sample` | Multi-class requires >= 3 classes; tiny sample path triggers hard numerical failures |
| Inference tests (t_perm_test, ANOVA) | Does not fit the fit/predict/transform paradigm | These are statistical tests, not estimators; excluded by design |
| SPM monitoring | Does not fit fit/predict paradigm | Monitoring is sequential, not batch; excluded by design |

---

## Sources

- [scikit-learn Developer Guide — Developing Estimators](https://scikit-learn.org/stable/developers/develop.html) — contracts for get_params, n_features_in_, Tags, clone
- [scikit-learn 1.6 Changelog](https://scikit-learn.org/stable/whats_new/v1.6.html) — __sklearn_tags__ introduction, _more_tags deprecation, _xfail_checks deprecation, validate_data public API
- [sklearn Tags documentation](https://scikit-learn.org/stable/modules/generated/sklearn.utils.Tags.html) — Tags dataclass fields
- [check_estimator documentation](https://scikit-learn.org/stable/modules/generated/sklearn.utils.estimator_checks.check_estimator.html) — expected_failed_checks parameter
- [sklearn issue #12734 — check_fit2d_1sample error message substrings](https://github.com/scikit-learn/scikit-learn/issues/12734) — exact substring requirements
- [sklearn PR #12328 — check_fit_idempotent](https://github.com/scikit-learn/scikit-learn/pull/12328) — idempotency check rationale
- [sklearn PR #17598 — check_methods_sample_order_invariance](https://github.com/scikit-learn/scikit-learn/pull/17598) — order invariance check
- [sklearn PR #29677 — __sklearn_tags__ API revamp](https://github.com/scikit-learn/scikit-learn/pull/29677) — tags migration rationale
- [catboost issue #2955 — __sklearn_tags__ AttributeError on sklearn 1.8](https://github.com/catboost/catboost/issues/2955) — real-world version drift failure
- [scikit-fda GitHub — functional data sklearn compatibility](https://github.com/GAA-UAM/scikit-fda) — reference implementation for FDA+sklearn
- [sklearn SLEP010 — n_features_in_ attribute](https://scikit-learn-enhancement-proposals.readthedocs.io/en/latest/slep010/proposal.html) — n_features_in_ specification
- [sklearn SLEP018 — set_output API](https://scikit-learn-enhancement-proposals.readthedocs.io/en/latest/slep018/proposal.html) — DataFrame output requirements

---
*Pitfalls research for: fdars v9.0 scikit-learn API Compatibility (sklearn estimator layer over PyO3 functional-data bindings)*
*Researched: 2026-08-31*
