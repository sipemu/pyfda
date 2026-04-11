# Conformal Prediction

Conformal prediction provides **distribution-free, finite-sample prediction intervals** (for regression) and **prediction sets** (for classification). Unlike asymptotic confidence intervals, conformal guarantees hold for any sample size and any data distribution:

$$
P\bigl(Y_{\text{new}} \in \hat{C}(X_{\text{new}})\bigr) \geq 1 - \alpha
$$

`pyfda` implements split conformal methods for functional regression and classification.

---

## How split conformal works

1. **Split** the training data into a *proper training set* and a *calibration set*.
2. **Fit** the model on the proper training set.
3. **Compute residuals** (nonconformity scores) on the calibration set.
4. **Construct** prediction intervals/sets for new observations using the calibration quantile.

!!! info "Coverage guarantee"
    For a calibration set of size $n_{\text{cal}}$ and miscoverage level $\alpha$, the coverage guarantee is:

    $$
    P\bigl(Y_{\text{new}} \in \hat{C}(X_{\text{new}})\bigr) \geq 1 - \alpha
    $$

    This holds marginally (over both the calibration set and new data) without any distributional assumptions.

---

## Conformal FPC regression

Wraps `fregre_lm` with split conformal calibration to produce prediction intervals.

```python
import numpy as np
from pyfda.conformal import conformal_fregre_lm

# --- Simulate data ---
np.random.seed(42)
n_train, n_test, m = 200, 50, 81
t = np.linspace(0, 1, m)
beta_true = np.sin(4 * np.pi * t)

def make_data(n):
    data = np.zeros((n, m))
    for i in range(n):
        data[i] = (
            np.random.randn() * np.sin(2 * np.pi * t)
            + np.random.randn() * np.cos(2 * np.pi * t)
            + 0.3 * np.random.randn(m)
        )
    response = np.trapz(data * beta_true, t, axis=1) + 0.5 * np.random.randn(n)
    return data, response

train_data, train_response = make_data(n_train)
test_data, test_response = make_data(n_test)

# --- Conformal prediction ---
result = conformal_fregre_lm(
    train_data, train_response, test_data,
    ncomp=3,
    cal_fraction=0.25,   # 25% of training data for calibration
    alpha=0.1,           # 90% prediction intervals
    seed=42,
)

lower       = result["lower"]        # (n_test,)
upper       = result["upper"]        # (n_test,)
predictions = result["predictions"]  # (n_test,)
coverage    = result["coverage"]     # empirical coverage (if test labels provided)

# Check coverage on test set
actual_coverage = np.mean((test_response >= lower) & (test_response <= upper))
print(f"Target coverage:  {1 - 0.1:.0%}")
print(f"Empirical coverage: {actual_coverage:.0%}")
print(f"Mean interval width: {np.mean(upper - lower):.4f}")
```

| Key | Type | Description |
|-----|------|-------------|
| `lower` | `ndarray (n_test,)` | Lower bounds of prediction intervals |
| `upper` | `ndarray (n_test,)` | Upper bounds of prediction intervals |
| `predictions` | `ndarray (n_test,)` | Point predictions |
| `coverage` | `float` | Reported coverage |

| Parameter | Default | Description |
|-----------|---------|-------------|
| `ncomp` | 3 | Number of FPC components |
| `cal_fraction` | 0.25 | Fraction of training data reserved for calibration |
| `alpha` | 0.1 | Miscoverage level ($1 - \alpha$ = coverage target) |
| `seed` | 42 | Random seed for the train/calibration split |

---

## Conformal nonparametric regression

Uses kernel regression (`fregre_np`) as the base model, with conformal calibration on top.

```python
from pyfda.conformal import conformal_fregre_np

result = conformal_fregre_np(
    train_data, train_response, test_data, t,
    cal_fraction=0.25,
    alpha=0.1,
    h_func=1.0,
    h_scalar=1.0,
    seed=42,
)

actual_coverage = np.mean((test_response >= result["lower"]) &
                          (test_response <= result["upper"]))
print(f"NP conformal coverage: {actual_coverage:.0%}")
print(f"Mean interval width:   {np.mean(result['upper'] - result['lower']):.4f}")
```

| Parameter | Default | Description |
|-----------|---------|-------------|
| `h_func` | 1.0 | Functional bandwidth |
| `h_scalar` | 1.0 | Scalar bandwidth |
| `cal_fraction` | 0.25 | Calibration fraction |
| `alpha` | 0.1 | Miscoverage level |

---

## Conformal classification

Produces **prediction sets** for classification: a set of possible labels for each test observation, with guaranteed marginal coverage.

```python
import numpy as np
from pyfda.conformal import conformal_classif

# --- Simulate three-class data ---
np.random.seed(7)
n_train, n_test = 150, 30
m = 101
t = np.linspace(0, 1, m)

templates = [
    np.sin(2 * np.pi * t),
    np.cos(2 * np.pi * t),
    np.sin(4 * np.pi * t),
]

def make_classif_data(n):
    data = np.zeros((n, m))
    labels = np.zeros(n, dtype=np.int64)
    for i in range(n):
        k = i % 3
        data[i] = templates[k] + 0.4 * np.random.randn(m)
        labels[i] = k
    return data, labels

train_data, train_labels = make_classif_data(n_train)
test_data, test_labels = make_classif_data(n_test)

result = conformal_classif(
    train_data, train_labels, test_data,
    ncomp=3,
    classifier="lda",
    cal_fraction=0.25,
    alpha=0.1,
    seed=42,
)

pred_sets = result["prediction_sets"]  # list of lists
coverage  = result["coverage"]

# Inspect prediction sets
for i in range(min(5, n_test)):
    correct = test_labels[i] in pred_sets[i]
    print(f"  Test {i}: set={pred_sets[i]}, true={test_labels[i]}, "
          f"covered={'yes' if correct else 'NO'}")

actual_coverage = np.mean([test_labels[i] in pred_sets[i] for i in range(n_test)])
print(f"\nTarget coverage:   {1 - 0.1:.0%}")
print(f"Empirical coverage: {actual_coverage:.0%}")
print(f"Mean set size:      {np.mean([len(s) for s in pred_sets]):.2f}")
```

| Key | Type | Description |
|-----|------|-------------|
| `prediction_sets` | `list[list[int]]` | Prediction set for each test observation |
| `coverage` | `float` | Reported coverage |

| Parameter | Default | Description |
|-----------|---------|-------------|
| `classifier` | `"lda"` | Base classifier: `"lda"`, `"qda"`, or `"knn"` |
| `ncomp` | 3 | Number of FPC components |
| `cal_fraction` | 0.25 | Calibration fraction |
| `alpha` | 0.1 | Miscoverage level |

!!! tip "Interpreting prediction set sizes"
    - **Set size = 1**: the model is confident about a single class.
    - **Set size > 1**: ambiguity -- multiple classes are plausible at the specified confidence level.
    - **Empty set**: can occur in rare edge cases; indicates the calibration set was too small.

---

## Practical considerations

### Choosing `cal_fraction`

The calibration fraction controls the bias-variance trade-off:

- **Larger** calibration set (e.g., 0.3--0.5): tighter, more accurate coverage but the model is trained on less data.
- **Smaller** calibration set (e.g., 0.1--0.2): more training data but wider intervals and noisier coverage.

A common choice is `cal_fraction=0.25`.

### Choosing `alpha`

| `alpha` | Coverage target | Typical use case |
|---------|-----------------|------------------|
| 0.01 | 99% | Safety-critical applications |
| 0.05 | 95% | Standard scientific inference |
| 0.10 | 90% | Exploratory analysis |
| 0.20 | 80% | Screening / ranking |

---

## Full example: comparing conformal methods

```python
import numpy as np
from pyfda.conformal import conformal_fregre_lm, conformal_fregre_np

np.random.seed(123)
n_train, n_test, m = 300, 100, 81
t = np.linspace(0, 1, m)
beta_true = np.exp(-((t - 0.5)**2) / 0.02)

def make_data(n):
    data = np.zeros((n, m))
    for i in range(n):
        data[i] = sum(
            np.random.randn() * np.sin((2*k+1) * np.pi * t)
            for k in range(4)
        ) + 0.2 * np.random.randn(m)
    resp = np.trapz(data * beta_true, t, axis=1) + 0.4 * np.random.randn(n)
    return data, resp

train_data, train_resp = make_data(n_train)
test_data, test_resp = make_data(n_test)

for alpha in [0.05, 0.10, 0.20]:
    # Linear conformal
    lm = conformal_fregre_lm(
        train_data, train_resp, test_data,
        ncomp=4, cal_fraction=0.25, alpha=alpha,
    )
    cov_lm = np.mean((test_resp >= lm["lower"]) & (test_resp <= lm["upper"]))
    width_lm = np.mean(lm["upper"] - lm["lower"])

    # Nonparametric conformal
    np_r = conformal_fregre_np(
        train_data, train_resp, test_data, t,
        cal_fraction=0.25, alpha=alpha,
    )
    cov_np = np.mean((test_resp >= np_r["lower"]) & (test_resp <= np_r["upper"]))
    width_np = np.mean(np_r["upper"] - np_r["lower"])

    print(f"alpha={alpha:.2f} | LM: cov={cov_lm:.0%} width={width_lm:.3f} | "
          f"NP: cov={cov_np:.0%} width={width_np:.3f}")
```
