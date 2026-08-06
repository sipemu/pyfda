"""Covariance kernels and Gaussian-process samplers (R ``covariance.R``).

Mirrors R's kernel-constructor family. A *kernel* here is a callable
``k(s, t) -> ndarray`` that, given two 1-D grids of length ``p`` and ``q``, returns
the ``(p, q)`` covariance matrix. Kernels compose with :func:`kernel_add` /
:func:`kernel_mult`, and :func:`make_gaussian_process` samples curves from one.

These are pure-NumPy reimplementations (R's kernels are closures, not Rust code).
"""

from __future__ import annotations

import numpy as np

__all__ = [
    "kernel_gaussian",
    "kernel_exponential",
    "kernel_matern",
    "kernel_brownian",
    "kernel_linear",
    "kernel_polynomial",
    "kernel_whitenoise",
    "kernel_periodic",
    "kernel_add",
    "kernel_mult",
    "make_gaussian_process",
    "r_brownian",
    "r_bridge",
    "r_ou",
]


def _grids(s, t):
    s = np.asarray(s, dtype=float).ravel()
    t = np.asarray(t, dtype=float).ravel()
    # (p, q) difference matrices
    return s, t, s[:, None], t[None, :]


def kernel_gaussian(lengthscale: float = 1.0, variance: float = 1.0):
    """Squared-exponential (RBF) kernel: ``variance * exp(-(s-t)^2 / (2 l^2))``."""

    def k(s, t):
        _, _, S, T = _grids(s, t)
        return variance * np.exp(-((S - T) ** 2) / (2.0 * lengthscale ** 2))

    return k


def kernel_exponential(lengthscale: float = 1.0, variance: float = 1.0):
    """Exponential kernel (Matern nu=1/2): ``variance * exp(-|s-t| / l)``."""

    def k(s, t):
        _, _, S, T = _grids(s, t)
        return variance * np.exp(-np.abs(S - T) / lengthscale)

    return k


def kernel_matern(lengthscale: float = 1.0, nu: float = 1.5, variance: float = 1.0):
    """Matern kernel for ``nu`` in {0.5, 1.5, 2.5} (closed forms)."""

    def k(s, t):
        _, _, S, T = _grids(s, t)
        d = np.abs(S - T)
        if nu == 0.5:
            return variance * np.exp(-d / lengthscale)
        if nu == 1.5:
            r = np.sqrt(3.0) * d / lengthscale
            return variance * (1.0 + r) * np.exp(-r)
        if nu == 2.5:
            r = np.sqrt(5.0) * d / lengthscale
            return variance * (1.0 + r + r ** 2 / 3.0) * np.exp(-r)
        raise ValueError("kernel_matern supports nu in {0.5, 1.5, 2.5}")

    return k


def kernel_brownian(variance: float = 1.0):
    """Brownian-motion (Wiener) kernel: ``variance * min(s, t)``."""

    def k(s, t):
        _, _, S, T = _grids(s, t)
        return variance * np.minimum(S, T)

    return k


def kernel_linear(variance: float = 1.0, center: float = 0.0):
    """Linear kernel: ``variance * (s-c) * (t-c)``."""

    def k(s, t):
        _, _, S, T = _grids(s, t)
        return variance * (S - center) * (T - center)

    return k


def kernel_polynomial(degree: int = 2, variance: float = 1.0, offset: float = 1.0):
    """Polynomial kernel: ``variance * (s*t + offset)^degree``."""

    def k(s, t):
        _, _, S, T = _grids(s, t)
        return variance * (S * T + offset) ** degree

    return k


def kernel_whitenoise(variance: float = 1.0):
    """White-noise kernel: ``variance`` on the diagonal (s == t), else 0."""

    def k(s, t):
        s, t, _, _ = _grids(s, t)
        return variance * (np.abs(s[:, None] - t[None, :]) == 0.0)

    return k


def kernel_periodic(lengthscale: float = 1.0, period: float = 1.0, variance: float = 1.0):
    """Periodic kernel: ``variance * exp(-2 sin^2(pi|s-t|/p) / l^2)``."""

    def k(s, t):
        _, _, S, T = _grids(s, t)
        arg = np.pi * np.abs(S - T) / period
        return variance * np.exp(-2.0 * np.sin(arg) ** 2 / lengthscale ** 2)

    return k


def kernel_add(k1, k2):
    """Sum of two kernels."""
    return lambda s, t: k1(s, t) + k2(s, t)


def kernel_mult(k1, k2):
    """Product of two kernels."""
    return lambda s, t: k1(s, t) * k2(s, t)


def make_gaussian_process(argvals, kernel, n: int = 1, mean=0.0, jitter: float = 1e-8,
                          seed: int | None = None):
    """Sample ``n`` Gaussian-process curves from ``kernel`` on ``argvals``.

    Parameters
    ----------
    argvals : array-like
        Evaluation grid, length m.
    kernel : callable
        A kernel ``k(s, t) -> (p, q)`` matrix (e.g. from :func:`kernel_gaussian`).
    n : int
        Number of curves to sample.
    mean : float or array-like or callable
        Mean function: a scalar, a length-m array, or ``f(argvals) -> length-m``.
    jitter : float
        Added to the diagonal for numerical stability.
    seed : int, optional
        RNG seed.

    Returns
    -------
    numpy.ndarray
        Samples, shape (n, m).
    """
    t = np.asarray(argvals, dtype=float).ravel()
    m = t.size
    K = np.asarray(kernel(t, t), dtype=float)
    K = 0.5 * (K + K.T) + jitter * np.eye(m)
    L = np.linalg.cholesky(K)
    if callable(mean):
        mu = np.asarray(mean(t), dtype=float).ravel()
    else:
        mu = np.broadcast_to(np.asarray(mean, dtype=float), (m,))
    rng = np.random.default_rng(seed)
    z = rng.standard_normal((m, n))
    return (mu[:, None] + L @ z).T


def _time_grid(argvals, n_points):
    if argvals is not None:
        return np.asarray(argvals, dtype=float).ravel()
    if n_points is None:
        raise ValueError("provide either argvals or n_points")
    return np.linspace(0.0, 1.0, int(n_points))


def r_brownian(n: int = 1, argvals=None, n_points: int | None = None,
               sigma: float = 1.0, seed: int | None = None):
    """Sample ``n`` standard Brownian-motion paths (R ``r.brownian``)."""
    t = _time_grid(argvals, n_points)
    dt = np.diff(t, prepend=t[0])
    rng = np.random.default_rng(seed)
    incr = rng.standard_normal((n, t.size)) * sigma * np.sqrt(np.maximum(dt, 0.0))
    incr[:, 0] = 0.0
    return np.cumsum(incr, axis=1)


def r_bridge(n: int = 1, argvals=None, n_points: int | None = None,
             sigma: float = 1.0, seed: int | None = None):
    """Sample ``n`` Brownian-bridge paths B(t) - (t/T) B(T) (R ``r.bridge``)."""
    t = _time_grid(argvals, n_points)
    w = r_brownian(n, argvals=t, sigma=sigma, seed=seed)
    span = t[-1] - t[0]
    frac = (t - t[0]) / span if span != 0 else np.zeros_like(t)
    return w - frac[None, :] * w[:, -1][:, None]


def r_ou(n: int = 1, argvals=None, n_points: int | None = None, theta: float = 1.0,
         mu: float = 0.0, sigma: float = 1.0, x0: float | None = None,
         seed: int | None = None):
    """Sample ``n`` Ornstein-Uhlenbeck paths (R ``r.ou``).

    dX = theta (mu - X) dt + sigma dW, integrated with the exact Gaussian
    transition so the step size need not be small.
    """
    t = _time_grid(argvals, n_points)
    rng = np.random.default_rng(seed)
    start = mu if x0 is None else x0
    x = np.empty((n, t.size))
    x[:, 0] = start
    for j in range(1, t.size):
        dt = t[j] - t[j - 1]
        e = np.exp(-theta * dt)
        var = (sigma ** 2) / (2.0 * theta) * (1.0 - e ** 2) if theta > 0 else sigma ** 2 * dt
        mean = mu + (x[:, j - 1] - mu) * e
        x[:, j] = mean + np.sqrt(max(var, 0.0)) * rng.standard_normal(n)
    return x
