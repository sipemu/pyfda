# pyfda.simulation

Simulation of functional data: Karhunen-Loeve expansion, Gaussian processes, and covariance matrices.

## Functions

| Function | Description |
|----------|-------------|
| [`simulate`](#simulate) | Simulate via Karhunen-Loeve expansion |
| [`gaussian_process`](#gaussian_process) | Generate Gaussian process samples |
| [`covariance_matrix`](#covariance_matrix) | Compute covariance matrix from a kernel |

---

### `simulate`

```python
pyfda.simulate(n, argvals, n_basis=5, efun_type="fourier",
               eval_type="linear", seed=None)
```

Simulate functional data using a Karhunen-Loeve expansion with configurable eigenfunctions and eigenvalue decay.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `n` | `int` | | Number of curves to generate |
| `argvals` | `ndarray (m,)` | | Evaluation points |
| `n_basis` | `int` | `5` | Number of basis functions |
| `efun_type` | `str` | `"fourier"` | Eigenfunction type: `"fourier"`, `"poly"`, `"poly_high"`, `"wiener"` |
| `eval_type` | `str` | `"linear"` | Eigenvalue decay: `"linear"`, `"exponential"`, `"wiener"` |
| `seed` | `int` or `None` | `None` | Random seed for reproducibility |

| Returns | Type | Description |
|---------|------|-------------|
| data | `ndarray (n, m)` | Simulated functional data |

```python
t = np.linspace(0, 1, 100)
data = pyfda.simulate(50, t, n_basis=5, efun_type="fourier", seed=42)
```

---

### `gaussian_process`

```python
pyfda.gaussian_process(n, argvals, kernel="gaussian", length_scale=0.2,
                       variance=1.0, seed=None)
```

Generate samples from a Gaussian process with a specified kernel.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `n` | `int` | | Number of curves |
| `argvals` | `ndarray (m,)` | | Evaluation points |
| `kernel` | `str` | `"gaussian"` | Kernel: `"gaussian"`, `"exponential"`, `"matern"`, `"periodic"` |
| `length_scale` | `float` | `0.2` | Kernel length scale |
| `variance` | `float` | `1.0` | Kernel variance (signal variance) |
| `seed` | `int` or `None` | `None` | Random seed |

| Returns | Type | Description |
|---------|------|-------------|
| samples | `ndarray (n, m)` | Gaussian process samples |

```python
t = np.linspace(0, 1, 200)
gp = pyfda.gaussian_process(30, t, kernel="matern", length_scale=0.1, seed=42)
```

---

### `covariance_matrix`

```python
pyfda.covariance_matrix(argvals, kernel="gaussian", length_scale=0.2, variance=1.0)
```

Compute a covariance matrix from a specified kernel function.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `argvals` | `ndarray (m,)` | | Evaluation points |
| `kernel` | `str` | `"gaussian"` | Kernel: `"gaussian"` or `"exponential"` |
| `length_scale` | `float` | `0.2` | Kernel length scale |
| `variance` | `float` | `1.0` | Kernel variance |

| Returns | Type | Description |
|---------|------|-------------|
| cov | `ndarray (m, m)` | Covariance matrix |

```python
t = np.linspace(0, 1, 100)
C = pyfda.covariance_matrix(t, kernel="gaussian", length_scale=0.2)
```
