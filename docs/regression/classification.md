# Classification

Functional classification assigns a class label $g_i \in \{0, 1, \dots, K-1\}$ to each functional observation $x_i(t)$. `pyfda` provides discriminant analysis, nearest-neighbor, and kernel-based classifiers, all operating on FPC score representations, plus functional logistic regression and cross-validated model comparison.

---

## Discriminant analysis

### LDA (Linear Discriminant Analysis)

Projects FPC scores onto the direction that maximizes the between-class to within-class variance ratio, assuming equal covariance across classes.

```python
import numpy as np
from pyfda import Fdata
from pyfda.classification import fclassif_lda

# --- Simulate two-class functional data ---
np.random.seed(0)
n, m = 80, 101
t = np.linspace(0, 1, m)

raw = np.zeros((n, m))
labels = np.zeros(n, dtype=np.int64)
for i in range(n):
    if i < n // 2:
        raw[i] = np.sin(2 * np.pi * t) + 0.3 * np.random.randn(m)
        labels[i] = 0
    else:
        raw[i] = np.cos(2 * np.pi * t) + 0.3 * np.random.randn(m)
        labels[i] = 1
fd = Fdata(raw, argvals=t)

result = fclassif_lda(fd.data, labels, ncomp=3)
print(f"LDA accuracy: {result['accuracy']:.2%}")
print(f"Predictions:  {result['predicted'][:10]}")
```

| Key | Type | Description |
|-----|------|-------------|
| `predicted` | `ndarray (n,)` | Predicted class labels |
| `accuracy` | `float` | Resubstitution accuracy |

### QDA (Quadratic Discriminant Analysis)

Relaxes the equal-covariance assumption of LDA, estimating a separate covariance matrix for each class.

```python
from pyfda.classification import fclassif_qda

result = fclassif_qda(fd.data, labels, ncomp=3)
print(f"QDA accuracy: {result['accuracy']:.2%}")
```

!!! tip "LDA vs. QDA"
    Use LDA when classes share similar covariance structure and sample sizes are small. Use QDA when class covariances differ substantially and you have enough observations per class ($\geq 2 \times$ the number of components).

---

## k-Nearest Neighbors

Classifies each observation by a majority vote among its $k$ nearest neighbors in FPC score space.

```python
from pyfda.classification import fclassif_knn

result = fclassif_knn(fd.data, labels, ncomp=3, k=5)
print(f"k-NN accuracy (k=5): {result['accuracy']:.2%}")
```

The `k` parameter controls the smoothness of the decision boundary.

---

## Kernel classifier

A nonparametric classifier using kernel density estimation in the functional space. Unlike the FPC-based methods above, this operates directly on the curves via a functional semi-metric.

```python
from pyfda.classification import fclassif_kernel

result = fclassif_kernel(fd.data, fd.argvals, labels, h_func=1.0, h_scalar=1.0)
print(f"Kernel accuracy: {result['accuracy']:.2%}")
```

| Parameter | Description |
|-----------|-------------|
| `h_func` | Bandwidth for the functional distance kernel |
| `h_scalar` | Bandwidth for the scalar kernel |

---

## Cross-validated classification

Compare classifiers and select the best number of components via $k$-fold cross-validation.

```python
from pyfda.classification import fclassif_cv

# Compare methods
for method in ["lda", "qda", "knn"]:
    result = fclassif_cv(
        fd.data, fd.argvals, labels,
        method=method,
        ncomp=5,
        nfold=5,
    )
    print(f"{method.upper():>6s}: error rate = {result['error_rate']:.2%}, "
          f"best_ncomp = {result['best_ncomp']}")
```

| Key | Type | Description |
|-----|------|-------------|
| `error_rate` | `float` | Cross-validated error rate |
| `fold_errors` | `ndarray (nfold,)` | Error rate for each fold |
| `best_ncomp` | `int` | Optimal number of components |

!!! info "Automatic component selection"
    `fclassif_cv` searches over component counts from 1 to `ncomp` and reports the `best_ncomp` that minimizes the CV error rate.

---

## Functional logistic regression

For binary classification, **functional logistic regression** models the log-odds as a linear functional of the predictor:

$$
\log\frac{P(G=1 \mid x)}{P(G=0 \mid x)} = \alpha + \int_{\mathcal{T}} x(t)\,\beta(t)\,dt
$$

```python
from pyfda.regression import functional_logistic

result = functional_logistic(fd.data, labels.astype(np.float64), n_comp=3)

probs     = result["probabilities"]      # (n,) -- P(G=1 | x)
predicted = result["predicted_classes"]   # (n,)
beta_t    = result["beta_t"]             # (m,) -- coefficient function
intercept = result["intercept"]          # scalar
coefs     = result["coefficients"]       # FPC coefficients

accuracy = np.mean(predicted == labels)
print(f"Logistic accuracy: {accuracy:.2%}")
print(f"Intercept: {intercept:.4f}")
```

| Key | Type | Description |
|-----|------|-------------|
| `probabilities` | `ndarray (n,)` | Predicted probabilities for class 1 |
| `predicted_classes` | `ndarray (n,)` | Predicted labels |
| `beta_t` | `ndarray (m,)` | Coefficient function $\hat{\beta}(t)$ |
| `intercept` | `float` | Intercept $\hat{\alpha}$ |
| `coefficients` | `ndarray (k,)` | Coefficients on FPC scores |

---

## Full example: classifying ECG-like waveforms

```python
import numpy as np
from pyfda import Fdata
from pyfda.classification import fclassif_lda, fclassif_qda, fclassif_knn, fclassif_cv
from pyfda.regression import functional_logistic

np.random.seed(42)
n_per_class = 50
n = 2 * n_per_class
m = 151
t = np.linspace(0, 1, m)

# Class 0: normal waveform
# Class 1: abnormal waveform (extra peak)
raw = np.zeros((n, m))
labels = np.zeros(n, dtype=np.int64)

for i in range(n):
    noise = 0.2 * np.random.randn(m)
    if i < n_per_class:
        # Normal: single peak
        raw[i] = np.exp(-((t - 0.5)**2) / 0.01) + noise
        labels[i] = 0
    else:
        # Abnormal: double peak
        raw[i] = (
            np.exp(-((t - 0.35)**2) / 0.008)
            + 0.7 * np.exp(-((t - 0.65)**2) / 0.008)
            + noise
        )
        labels[i] = 1
fd = Fdata(raw, argvals=t)

# --- Compare classifiers ---
print("Resubstitution accuracy:")
for name, fn in [("LDA", fclassif_lda), ("QDA", fclassif_qda)]:
    r = fn(fd.data, labels, ncomp=4)
    print(f"  {name}: {r['accuracy']:.2%}")

r = fclassif_knn(fd.data, labels, ncomp=4, k=5)
print(f"  k-NN: {r['accuracy']:.2%}")

# --- Cross-validated comparison ---
print("\nCross-validated error rates:")
for method in ["lda", "qda", "knn"]:
    cv = fclassif_cv(fd.data, fd.argvals, labels, method=method, ncomp=6, nfold=5)
    print(f"  {method.upper()}: {cv['error_rate']:.2%} (best k={cv['best_ncomp']})")

# --- Functional logistic regression ---
logit = functional_logistic(fd.data, labels.astype(np.float64), n_comp=4)
acc = np.mean(logit["predicted_classes"] == labels)
print(f"\nLogistic regression accuracy: {acc:.2%}")
print(f"Most influential time point: t = {fd.argvals[np.argmax(np.abs(logit['beta_t']))]:.2f}")
```
