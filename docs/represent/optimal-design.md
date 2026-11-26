# Optimal Sampling Design

In a sparse longitudinal study each subject is measured only a few times. If a pilot study has already been fitted with [PACE](pace-fpca.md), the fitted model can tell you **when** to measure the next subject: which few time points best pin down that subject's whole trajectory, or its FPC scores. `fdars.pace_fpca` implements the criteria of Ji & Müller (2017) and a greedy search over candidate time points.

## The criteria

Under the PACE model a subject's trajectory is $x(t) = \mu(t) + \sum_k \xi_k \phi_k(t)$ with $\xi_k \sim N(0, \lambda_k)$, observed with noise $\sigma^2$. Suppose the subject is measured at a design $S = \{s_1, \dots, s_p\}$. The best linear predictor of the scores given those measurements (the PACE conditional expectation) has posterior covariance

$$
\operatorname{Cov}(\xi \mid Y_S) = \Lambda - \Lambda \Phi_S^\top \big(\Phi_S \Lambda \Phi_S^\top + \sigma^2 I\big)^{-1} \Phi_S \Lambda ,
$$

where $\Phi_S$ holds the eigenfunctions at the design points. A good design makes this covariance small:

| `criterion=` | Value | Use when you care about |
|---|---|---|
| `"trajectory"` (default) | $\int \operatorname{Var}\big(x(t) \mid Y_S\big)\,dt$, the expected integrated reconstruction error | the whole curve |
| `"a"` | $\operatorname{tr} \operatorname{Cov}(\xi \mid Y_S)$ (A-optimality) | the scores, all equally |
| `"d"` | $\log\det \operatorname{Cov}(\xi \mid Y_S)$ (D-optimality) | the scores jointly, e.g. as regressors later |

All three are minimised and never increase when a point is added. Because the eigenfunctions are orthonormal, $\int \operatorname{Var}(x(t) \mid Y_S)\,dt = \operatorname{tr}\operatorname{Cov}(\xi \mid Y_S)$, so `"trajectory"` and `"a"` give the same values and the same designs. With no measurements the trajectory and A criteria equal $\sum_k \lambda_k$, and D equals $\sum_k \log \lambda_k$.

## The API

1. Fit the pilot data with `pace_fpca_fit(data, ncomp, bandwidth, sigma2, work_grid, alpha)`. It takes the same arguments as `pace_fpca` but returns a reusable model handle with `ncomp`, `argvals` (the work grid), `eigenvalues`, `sigma2` and `to_dict()` (the usual `pace_fpca` result).
2. Score a design you have in mind with `design_criterion(model, selected, criterion)`. `selected` holds 0-based indices into `model.argvals`.
3. Search for a design with `optimal_design(model, budget, candidate_grid=None, criterion)`. It adds one point at a time, always the one that lowers the criterion most (deterministic; ties go to the earliest grid point). It returns `selected_indices` (in selection order), `selected_argvals` and `criterion_trace`, the criterion after each step. `candidate_grid` restricts the search to feasible times, each of which must lie on `model.argvals`.

The work grid defines the possible measurement times, so set `work_grid` to the times at which visits can actually be scheduled.

## Example

Thirty pilot subjects were each measured 4 to 7 times on a 21-point grid. Where should the three visits of a new subject go?

```python exec="1" html="1" source="above"
import numpy as np
from docs_fig import fig, render
import fdars.pace_fpca as pf

rng = np.random.default_rng(9)
grid = np.linspace(0, 1, 21)                 # visits can only happen on this grid
argvals_list, values_list = [], []
for _ in range(30):                           # 30 pilot subjects, 4-7 visits each
    idx = np.sort(rng.choice(21, size=rng.integers(4, 8), replace=False))
    tt = grid[idx]
    xi = rng.normal(0, [1.5, 0.7])
    x = 1 + xi[0] * np.sqrt(2) * np.sin(np.pi * tt) + xi[1] * np.sqrt(2) * np.cos(2 * np.pi * tt)
    argvals_list.append(tt)
    values_list.append(x + rng.normal(0, 0.2, len(tt)))

model = pf.pace_fpca_fit(pf.irreg_fdata_from_lists(argvals_list, values_list),
                         ncomp=2, bandwidth=0.2, sigma2=0.04, work_grid=list(grid))
design = pf.optimal_design(model, budget=3)
random_designs = [pf.design_criterion(model, rng.choice(21, 3, replace=False)) for _ in range(300)]

ef = np.asarray(model.to_dict()["eigenfunctions"])
f, (a0, a1) = fig(1, 2, figsize=(12, 3.6))
a0.plot(grid, ef[:, 0], color="#3f51b5", lw=2.2, label=f"PC 1 (eigenvalue {model.eigenvalues[0]:.2f})")
a0.plot(grid, ef[:, 1], color="#e8710a", lw=2.2, label=f"PC 2 (eigenvalue {model.eigenvalues[1]:.2f})")
for step, tt in enumerate(design["selected_argvals"], start=1):
    a0.axvline(tt, color="#dc3545", lw=1.4, ls="--")
    a0.text(tt, a0.get_ylim()[1] * 0.92, f" {step}", color="#dc3545", fontsize=10)
a0.set(title="Greedy 3-point design (red, in selection order)", xlabel="t")
a0.legend(fontsize=8.5, loc="lower left")
a1.hist(random_designs, bins=30, color="#6c757d", alpha=0.6, label="300 random 3-point designs")
a1.axvline(design["criterion_trace"][-1], color="#dc3545", lw=2.2, label="greedy design")
a1.set(title="Trajectory criterion (lower is better)", xlabel="expected reconstruction MSE")
a1.legend(fontsize=8.5)
print(render(f))
better = np.mean(np.asarray(random_designs) > design["criterion_trace"][-1])
print(f"<p>selected t = {np.round(design['selected_argvals'], 2).tolist()}; criterion after each step "
      f"{np.round(design['criterion_trace'], 4).tolist()} (no visits: {pf.design_criterion(model, []):.3f}); "
      f"greedy beats {better:.0%} of random designs</p>")
print("FDARS_FENCE_OK")
```

The fitted model has one dominant component. The first visit therefore goes where PC 1 is large but PC 2 is small ($t = 0.75$), not to the peak of PC 1 at $t \approx 0.55$, where PC 2 variation would blur the information about the dominant score. The second visit at $t = 1$ resolves PC 2 at its extreme, and the third adds the PC 1 peak. Three well-placed visits reduce the expected reconstruction error from 2.25 (no data, the prior variance) to 0.019, better than 99% of random 3-visit schedules.

## Restricting the candidates and comparing criteria

In practice not every time is feasible, e.g. visits on even grid days only. Pass those times as `candidate_grid`. Different criteria can also prefer different designs:

```python exec="1" source="above" result="text"
import numpy as np
import fdars.pace_fpca as pf

rng = np.random.default_rng(9)
grid = np.linspace(0, 1, 21)
argvals_list, values_list = [], []
for _ in range(30):
    idx = np.sort(rng.choice(21, size=rng.integers(4, 8), replace=False))
    tt = grid[idx]
    xi = rng.normal(0, [1.5, 0.7])
    x = 1 + xi[0] * np.sqrt(2) * np.sin(np.pi * tt) + xi[1] * np.sqrt(2) * np.cos(2 * np.pi * tt)
    argvals_list.append(tt)
    values_list.append(x + rng.normal(0, 0.2, len(tt)))
model = pf.pace_fpca_fit(pf.irreg_fdata_from_lists(argvals_list, values_list),
                         ncomp=2, bandwidth=0.2, sigma2=0.04, work_grid=list(grid))

for crit in ("trajectory", "a", "d"):
    d = pf.optimal_design(model, budget=3, criterion=crit)
    print(f"{crit:10s} t = {np.round(d['selected_argvals'], 2).tolist()}  trace {np.round(d['criterion_trace'], 3).tolist()}")

even_days = grid[::2]                                    # feasible visit times only
d = pf.optimal_design(model, budget=3, candidate_grid=list(even_days))
print(f"even days  t = {np.round(d['selected_argvals'], 2).tolist()}  trace {np.round(d['criterion_trace'], 3).tolist()}")
print("score a hand-picked design [0, 0.5, 1]:",
      round(pf.design_criterion(model, [0, 10, 20]), 4))
print("FDARS_FENCE_OK")
```

The trajectory and A criteria agree, as explained above. The D-criterion works on a log scale, so a relative reduction of the small PC 2 variance counts as much as one of the large PC 1 variance; it starts at the PC 1 peak and ends with a different design. A hand-picked "start, middle, end" schedule is about 20% worse than the greedy one here.

## Caveats

- The design is only as good as the pilot model. Eigenfunctions and eigenvalues estimated from few subjects are noisy, so check the PACE fit first (`bandwidth`, `sigma2`; see [PACE FPCA](pace-fpca.md)). The selection treats the fitted model as known and does not re-estimate it.
- Greedy forward selection is not guaranteed to find the best design of a given size. It is fast and usually close; compare with a few random or hand-picked designs using `design_criterion`, as above.
- The criteria are about a **new** subject from the same population. They say nothing about how to schedule visits for estimating the mean or covariance themselves.

## References

1. Ji, H. & Müller, H.-G. (2017). Optimal designs for longitudinal and functional data. *Journal of the Royal Statistical Society: Series B*, 79(3), 859–876.
2. Yao, F., Müller, H.-G. & Wang, J.-L. (2005). Functional data analysis for sparse longitudinal data. *Journal of the American Statistical Association*, 100(470), 577–590.
