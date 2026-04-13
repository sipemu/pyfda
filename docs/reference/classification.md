# fdars.classification

Classification methods for functional data via FPC score projection.

## Functions

| Function | Description |
|----------|-------------|
| [`fclassif_lda`](#fclassif_lda) | Linear discriminant analysis |
| [`fclassif_qda`](#fclassif_qda) | Quadratic discriminant analysis |
| [`fclassif_knn`](#fclassif_knn) | K-nearest neighbors classification |
| [`fclassif_kernel`](#fclassif_kernel) | Kernel classification |
| [`fclassif_cv`](#fclassif_cv) | Cross-validated classification |

---

### `fclassif_lda`

```python
fdars.fclassif_lda(data, labels, ncomp=3)
```

LDA classification for functional data. Projects onto FPC scores, then applies linear discriminant analysis.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data` | `ndarray (n, m)` | | Functional data |
| `labels` | `ndarray (n,)` of `int64` | | Class labels |
| `ncomp` | `int` | `3` | Number of FPC components |

| Returns | Type | Description |
|---------|------|-------------|
| result | `dict` | Keys: `predicted` (n,), `accuracy` |

```python
result = fdars.fclassif_lda(data, labels, ncomp=5)
print(f"Accuracy: {result['accuracy']:.3f}")
```

---

### `fclassif_qda`

```python
fdars.fclassif_qda(data, labels, ncomp=3)
```

QDA classification for functional data. Uses class-specific covariance matrices.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data` | `ndarray (n, m)` | | Functional data |
| `labels` | `ndarray (n,)` of `int64` | | Class labels |
| `ncomp` | `int` | `3` | Number of FPC components |

| Returns | Type | Description |
|---------|------|-------------|
| result | `dict` | Keys: `predicted` (n,), `accuracy` |

```python
result = fdars.fclassif_qda(data, labels, ncomp=5)
```

---

### `fclassif_knn`

```python
fdars.fclassif_knn(data, labels, ncomp=3, k=5)
```

K-nearest neighbors classification in FPC score space.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data` | `ndarray (n, m)` | | Functional data |
| `labels` | `ndarray (n,)` of `int64` | | Class labels |
| `ncomp` | `int` | `3` | Number of FPC components |
| `k` | `int` | `5` | Number of nearest neighbors |

| Returns | Type | Description |
|---------|------|-------------|
| result | `dict` | Keys: `predicted` (n,), `accuracy` |

```python
result = fdars.fclassif_knn(data, labels, ncomp=5, k=7)
```

---

### `fclassif_kernel`

```python
fdars.fclassif_kernel(data, argvals, labels, h_func=1.0, h_scalar=1.0)
```

Kernel classification directly on functional data using functional and scalar bandwidths.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data` | `ndarray (n, m)` | | Functional data |
| `argvals` | `ndarray (m,)` | | Evaluation points |
| `labels` | `ndarray (n,)` of `int64` | | Class labels |
| `h_func` | `float` | `1.0` | Functional bandwidth |
| `h_scalar` | `float` | `1.0` | Scalar bandwidth |

| Returns | Type | Description |
|---------|------|-------------|
| result | `dict` | Keys: `predicted` (n,), `accuracy` |

```python
result = fdars.fclassif_kernel(data, t, labels, h_func=0.5, h_scalar=0.5)
```

---

### `fclassif_cv`

```python
fdars.fclassif_cv(data, argvals, labels, method="lda", ncomp=3, nfold=5)
```

Cross-validated classification with error rate estimation.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data` | `ndarray (n, m)` | | Functional data |
| `argvals` | `ndarray (m,)` | | Evaluation points |
| `labels` | `ndarray (n,)` of `int64` | | Class labels |
| `method` | `str` | `"lda"` | `"lda"`, `"qda"`, `"knn"`, or `"kernel"` |
| `ncomp` | `int` | `3` | Number of FPC components |
| `nfold` | `int` | `5` | Number of CV folds |

| Returns | Type | Description |
|---------|------|-------------|
| result | `dict` | Keys: `error_rate`, `fold_errors` (nfold,), `best_ncomp` |

```python
result = fdars.fclassif_cv(data, t, labels, method="knn", ncomp=5, nfold=10)
print(f"CV error rate: {result['error_rate']:.3f}")
```
