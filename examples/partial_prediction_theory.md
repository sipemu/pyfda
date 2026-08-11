# Partial-Domain Functional Prediction

## Problem Setting

We observe $n$ training samples, each consisting of $p$ functional predictors
$X_i^{(1)}(t), \ldots, X_i^{(p)}(t)$ and a functional response $Y_i(t)$, all
defined on a common domain $[a, b]$.

At prediction time we observe a new set of predictors $X^{*(j)}(t)$ only on the
subdomain $[a, c]$ with $c < b$ (the same cutoff for all $p$ features), and want
to predict $Y^*(t)$ for **all** $t \in [a, b]$ together with prediction
intervals.

---

## Step 1: Multivariate Functional PCA

### Per-feature centering and scaling

Compute the sample mean for each feature $j = 1, \ldots, p$:

$$\hat{\mu}^{(j)}(t) = \frac{1}{n} \sum_{i=1}^n X_i^{(j)}(t)$$

and a scaling weight $w_j > 0$ that normalizes the average energy of each
feature so that no single feature dominates:

$$w_j = \left( \frac{1}{n} \sum_{i=1}^n \int_a^b \bigl(X_i^{(j)}(t) - \hat{\mu}^{(j)}(t)\bigr)^2 \, dt \right)^{-1/2}$$

Define the centered and scaled curves

$$\tilde{X}_i^{(j)}(t) = w_j \bigl(X_i^{(j)}(t) - \hat{\mu}^{(j)}(t)\bigr)$$

### Stacking into a vector-valued function

Concatenate the $p$ features into a single vector-valued function:

$$\mathbf{Z}_i(t) = \begin{pmatrix} \tilde{X}_i^{(1)}(t) \\ \vdots \\ \tilde{X}_i^{(p)}(t) \end{pmatrix} \in \mathbb{R}^p$$

In the discretized setting, if each feature is observed on an $m$-point grid,
$\mathbf{Z}_i$ becomes a vector of length $pm$.

### Cross-covariance operator

The covariance operator of $\mathbf{Z}$ has kernel

$$\mathbf{C}(s, t) = \frac{1}{n-1} \sum_{i=1}^n \mathbf{Z}_i(s) \, \mathbf{Z}_i(t)^\top \in \mathbb{R}^{p \times p}$$

with blocks $C^{(jl)}(s, t) = \text{Cov}\!\bigl(\tilde{X}^{(j)}(s),\, \tilde{X}^{(l)}(t)\bigr)$.

### Eigendecomposition

Solve the eigenvalue problem

$$\int_a^b \mathbf{C}(s, t) \, \boldsymbol{\varphi}_k(s) \, ds = \lambda_k \, \boldsymbol{\varphi}_k(t)$$

to obtain multivariate eigenfunctions $\boldsymbol{\varphi}_k(t) = \bigl(\varphi_k^{(1)}(t), \ldots, \varphi_k^{(p)}(t)\bigr)^\top$
and eigenvalues $\lambda_1 \geq \lambda_2 \geq \cdots > 0$.

In practice, we use the **dual trick**: form the $n \times n$ Gram matrix

$$G_{ij} = \int_a^b \mathbf{Z}_i(t)^\top \mathbf{Z}_j(t) \, dt \approx \sum_{r=1}^{pm} Z_{ir} \, Z_{jr} \, \omega_r$$

where $\omega_r$ are trapezoidal quadrature weights tiled across $p$ features.
The eigenvectors $\mathbf{v}_k$ of $\frac{1}{n-1} G$ with eigenvalues $\lambda_k$
yield the eigenfunctions via

$$\boldsymbol{\varphi}_k = \frac{1}{\sqrt{\lambda_k (n-1)}} \sum_{i=1}^n v_{ik} \, \mathbf{Z}_i$$

### Scores

The FPC scores on the full domain are

$$\xi_{ik} = \int_a^b \mathbf{Z}_i(t)^\top \boldsymbol{\varphi}_k(t) \, dt = \sum_{j=1}^p \int_a^b \tilde{X}_i^{(j)}(t) \, \varphi_k^{(j)}(t) \, dt$$

Retain $K$ components (chosen by cumulative variance threshold, elbow, or
cross-validation).

---

## Step 2: Regression from Scores to $Y(t)$

### Model

$$Y_i(t) = \hat{\mu}_Y(t) + \sum_{k=1}^K \xi_{ik} \, \beta_k(t) + \varepsilon_i(t)$$

where $\hat{\mu}_Y(t) = \frac{1}{n} \sum_i Y_i(t)$ and $\beta_k(t)$ is a
coefficient function estimated by pointwise OLS:

$$\hat{\boldsymbol{\beta}}(t) = \bigl(\boldsymbol{\Xi}^\top \boldsymbol{\Xi}\bigr)^{-1} \boldsymbol{\Xi}^\top \, \bigl(\mathbf{Y}(t) - \hat{\mu}_Y(t)\bigr)$$

with $\boldsymbol{\Xi} \in \mathbb{R}^{n \times K}$ the score matrix and
$\mathbf{Y}(t) \in \mathbb{R}^n$ the response values at grid point $t$.

### Residual variance

$$\hat{\sigma}_Y^2(t) = \frac{1}{n - K - 1} \sum_{i=1}^n \bigl(Y_i(t) - \hat{Y}_i(t)\bigr)^2$$

---

## Step 3a: Score Estimation — Truncated Projection (Approach 1)

### Idea

Given $X^{*(j)}(t)$ only on $[a, c]$, estimate the scores by integrating the
eigenfunctions only over the observed subdomain and renormalizing.

### Formula

$$\hat{\xi}_k^* = \frac{\displaystyle\sum_{j=1}^p \int_a^c \tilde{X}^{*(j)}(t) \, \varphi_k^{(j)}(t) \, dt}{\displaystyle\sum_{j=1}^p \int_a^c \bigl(\varphi_k^{(j)}(t)\bigr)^2 \, dt}$$

where $\tilde{X}^{*(j)}(t) = w_j \bigl(X^{*(j)}(t) - \hat{\mu}^{(j)}(t)\bigr)$.

### Interpretation

This is the **least-squares projection** of the partial observation onto the
truncated eigenfunctions. Equivalently, it minimizes

$$\sum_{j=1}^p \int_a^c \left( \tilde{X}^{*(j)}(t) - \sum_{k=1}^K \hat{\xi}_k^* \, \varphi_k^{(j)}(t) \right)^2 dt$$

### Properties

- **Consistency**: as $c \to b$, $\hat{\xi}_k^* \to \xi_k^*$ (recovers the
  full-domain score).
- **Degradation**: as $c \to a$, the denominator shrinks and the estimate
  becomes noisy.
- **No distributional assumptions** required.
- **Fast**: $O(K \cdot p \cdot m_c)$ per observation.

### Limitations

- Does not use the covariance structure between observed and unobserved portions.
- Does not account for measurement noise.
- No natural uncertainty quantification for the scores themselves.

---

## Step 3b: Score Estimation — PACE (Approach 2)

### Model assumptions

Assume a Gaussian model for the scores and observations:

$$X_i^{(j)}(t) = \mu^{(j)}(t) + \sum_{k=1}^K \xi_{ik} \, \varphi_k^{(j)}(t) + \sigma_j \, e_i^{(j)}(t)$$

where:

- $\xi_{ik} \sim \mathcal{N}(0, \lambda_k)$, mutually uncorrelated
- $e_i^{(j)}(t) \sim \mathcal{N}(0, 1)$ is measurement noise, independent of
  the scores
- $\sigma_j^2$ is the noise variance for feature $j$

### Noise variance estimation

$$\hat{\sigma}_j^2 = \max\!\left(0,\; \frac{1}{b - a} \int_a^b \widehat{\text{Var}}\!\bigl[\tilde{X}^{(j)}(t)\bigr] \, dt \;-\; \frac{1}{b - a} \sum_{k=1}^K \lambda_k \int_a^b \bigl(\varphi_k^{(j)}(t)\bigr)^2 \, dt \right)$$

This is the difference between total variance and variance explained by $K$
components — the residual is attributed to noise.

### Stacked observation vector

At prediction time, we observe $X^{*(j)}(t)$ on a grid $t_1, \ldots, t_{m_c}$
in $[a, c]$. Stack all $p$ features:

$$\mathbf{X}_{\text{obs}}^* = \begin{pmatrix} w_1 \bigl(X^{*(1)}(t_1) - \mu^{(1)}(t_1)\bigr) \\ \vdots \\ w_1 \bigl(X^{*(1)}(t_{m_c}) - \mu^{(1)}(t_{m_c})\bigr) \\ w_2 \bigl(X^{*(2)}(t_1) - \mu^{(2)}(t_1)\bigr) \\ \vdots \\ w_p \bigl(X^{*(p)}(t_{m_c}) - \mu^{(p)}(t_{m_c})\bigr) \end{pmatrix} \in \mathbb{R}^{p \cdot m_c}$$

### Covariance of the observation

$$\boldsymbol{\Sigma}_{\text{obs}} = \sum_{k=1}^K \lambda_k \, \boldsymbol{\phi}_k \boldsymbol{\phi}_k^\top + \text{diag}(\sigma_1^2 \mathbf{I}_{m_c}, \ldots, \sigma_p^2 \mathbf{I}_{m_c})$$

where $\boldsymbol{\phi}_k \in \mathbb{R}^{p \cdot m_c}$ stacks the
eigenfunction values on the observed grid:

$$\boldsymbol{\phi}_k = \begin{pmatrix} \varphi_k^{(1)}(t_1) \\ \vdots \\ \varphi_k^{(1)}(t_{m_c}) \\ \varphi_k^{(2)}(t_1) \\ \vdots \\ \varphi_k^{(p)}(t_{m_c}) \end{pmatrix}$$

### BLUP (Best Linear Unbiased Predictor)

The conditional expectation of the $k$-th score given the partial observation is:

$$\boxed{\tilde{\xi}_k^* = \lambda_k \, \boldsymbol{\phi}_k^\top \, \boldsymbol{\Sigma}_{\text{obs}}^{-1} \, \mathbf{X}_{\text{obs}}^*}$$

This is the **optimal** linear estimator under the Gaussian model: it minimizes
$\mathbb{E}\bigl[(\xi_k - \hat{\xi}_k)^2 \mid \mathbf{X}_{\text{obs}}^*\bigr]$.

### Conditional variance

$$\text{Var}\bigl[\xi_k^* \mid \mathbf{X}_{\text{obs}}^*\bigr] = \lambda_k - \lambda_k^2 \, \boldsymbol{\phi}_k^\top \, \boldsymbol{\Sigma}_{\text{obs}}^{-1} \, \boldsymbol{\phi}_k$$

This quantifies how much uncertainty remains about each score after observing the
partial data.

### Key properties

- **Optimality**: BLUP minimizes the mean squared error among all linear
  unbiased estimators.
- **Cross-feature borrowing**: if feature $j$ is informative about score $k$
  (i.e., $\varphi_k^{(j)}$ has large mass on $[a, c]$), it helps estimate
  $\xi_k$ even if other features contribute little on $[a, c]$.
- **Noise handling**: the $\sigma_j^2$ terms in $\boldsymbol{\Sigma}_{\text{obs}}$
  down-weight noisy features automatically.
- **Graceful degradation**: as $c \to a$, the conditional variance approaches
  $\lambda_k$ (the prior variance) — we learn nothing. As $c \to b$, it
  approaches $\sigma_\epsilon^2 \lambda_k / (\lambda_k + \sigma_\epsilon^2)$ —
  only measurement noise limits the estimate.
- **Computational cost**: $O((pm_c)^3)$ for the Cholesky factorization of
  $\boldsymbol{\Sigma}_{\text{obs}}$, then $O(K \cdot (pm_c)^2)$ for the
  solves. This is done once per cutoff $c$, not per observation.

### Connection to Approach 1

When $\sigma_j = 0$ for all $j$ (no measurement noise) and the grid is dense,
the PACE estimator converges to the truncated projection. PACE is strictly
better when noise is present or the eigenfunctions have significant mass outside
$[a, c]$.

---

## Step 4: Prediction

Given estimated scores $\hat{\xi}_1^*, \ldots, \hat{\xi}_K^*$ (from either
approach), predict:

$$\hat{Y}^*(t) = \hat{\mu}_Y(t) + \sum_{k=1}^K \hat{\xi}_k^* \, \hat{\beta}_k(t), \quad t \in [a, b]$$

---

## Step 5: Prediction Intervals

### Option A: Conformal prediction band (distribution-free)

Split the training data into a proper training set $\mathcal{I}_1$ ($n_1$
curves) and a calibration set $\mathcal{I}_2$ ($n_2$ curves).

**Step 1.** Fit the full pipeline (MFPCA + regression) on $\mathcal{I}_1$.

**Step 2.** On $\mathcal{I}_2$, compute prediction residuals:

$$R_i(t) = Y_i(t) - \hat{Y}_i(t), \quad i \in \mathcal{I}_2$$

**Step 3.** Estimate local scale (for adaptive band width):

$$\hat{\sigma}(t) = 1.4826 \cdot \text{median}_{i \in \mathcal{I}_2} |R_i(t)|$$

This is the MAD (median absolute deviation), a robust scale estimator.
The factor 1.4826 makes it consistent for Gaussian data.

**Step 4.** Compute normalized nonconformity scores:

$$S_i = \sup_{t \in [a,b]} \frac{|R_i(t)|}{\hat{\sigma}(t)}, \quad i \in \mathcal{I}_2$$

**Step 5.** The conformal quantile is:

$$\hat{q}_{1-\alpha} = \text{Quantile}\!\left(\{S_i\}_{i \in \mathcal{I}_2},\; \frac{\lceil (1-\alpha)(n_2 + 1) \rceil}{n_2}\right)$$

**Step 6.** The simultaneous prediction band for a new observation is:

$$\boxed{\hat{Y}^*(t) \pm \hat{q}_{1-\alpha} \cdot \hat{\sigma}(t)}$$

**Coverage guarantee** (Vovk et al., 2005):

$$P\!\left(Y^*(t) \in \bigl[\hat{Y}^*(t) \pm \hat{q}_{1-\alpha} \cdot \hat{\sigma}(t)\bigr] \;\text{for all } t \in [a,b]\right) \geq 1 - \alpha$$

under the sole assumption that $(X_i, Y_i)$ are exchangeable.

**Adaptive width**: the band is wider at grid points where the model is less
accurate (larger $\hat{\sigma}(t)$) and narrower where it is more accurate.
This arises naturally from using the supremum of normalized residuals.

**Connection to partial observation**: the calibration residuals $R_i(t)$ are
computed using the same partial-domain predictor that will be used at test time.
If the predictor is worse (smaller $c$), the residuals are larger, $\hat{q}$
is larger, and the bands automatically widen. No explicit modeling of
partial-observation uncertainty is needed.

### Option B: Parametric prediction band (PACE only)

Under the Gaussian model, the pointwise prediction variance is:

$$\text{Var}\!\bigl[\hat{Y}^*(t) \mid \mathbf{X}_{\text{obs}}^*\bigr] = \underbrace{\sum_{k=1}^K \hat{\beta}_k^2(t) \, \text{Var}\!\bigl[\xi_k^* \mid \mathbf{X}_{\text{obs}}^*\bigr]}_{\text{score estimation uncertainty}} + \underbrace{\hat{\sigma}_Y^2(t)}_{\text{residual variance}}$$

The first term comes from the PACE conditional variance (Step 3b). The second
from the regression residuals (Step 2).

The pointwise $(1-\alpha)$ prediction interval is:

$$\boxed{\hat{Y}^*(t) \pm z_{1-\alpha/2} \sqrt{\text{Var}\!\bigl[\hat{Y}^*(t) \mid \mathbf{X}_{\text{obs}}^*\bigr]}}$$

**Properties**:

- Tighter than conformal (exploits the Gaussian assumption).
- The band width **varies with $c$**: smaller $c$ increases
  $\text{Var}[\xi_k^* \mid \mathbf{X}_{\text{obs}}^*]$ and widens the band.
- Gives **pointwise** coverage. For simultaneous coverage, apply a Bonferroni
  or Scheffe correction, or use the conformal approach.
- Useful as a diagnostic: shows where the model is most uncertain about the
  response, decomposed into score uncertainty vs. residual noise.

---

## Method Comparison

| Property | Truncated + Conformal | PACE + Conformal | PACE + Parametric |
|---|---|---|---|
| **Assumptions** | None | Gaussian scores + noise | Gaussian scores + noise |
| **Score estimation** | Renormalized integral | Conditional expectation (BLUP) | Conditional expectation (BLUP) |
| **Cross-feature borrowing** | No | Yes | Yes |
| **Noise robustness** | No (ignores noise) | Yes ($\sigma_j^2$ modeled) | Yes ($\sigma_j^2$ modeled) |
| **Coverage type** | Simultaneous, guaranteed | Simultaneous, guaranteed | Pointwise, approximate |
| **Coverage guarantee** | Distribution-free | Distribution-free | Requires Gaussian model |
| **Band width** | Adaptive (via MAD) | Adaptive (via MAD) | Adaptive (via $\text{Var}[\xi_k \mid X_{\text{obs}}]$) |
| **Band tightness** | Conservative | Conservative | Tight |
| **Computational cost** | $O(Kpm_c)$ per obs | $O((pm_c)^3)$ once + $O(Kpm_c)$ per obs | Same as PACE + Conformal |
| **Degradation at small $c$** | Poor (RMSE increases) | Graceful (borrows strength) | Graceful + uncertainty quantified |

### Recommended combination

Use **PACE for point prediction** (optimal MSE under the Gaussian model) with
**conformal calibration for prediction intervals** (valid coverage without
distributional assumptions). The PACE conditional variances remain available
as a diagnostic for understanding where uncertainty comes from.

---

## References

- Yao, F., Muller, H.-G. and Wang, J.-L. (2005). Functional data analysis
  for sparse longitudinal data. *Journal of the American Statistical
  Association*, 100(470), 577-590.

- Happ, C. and Greven, S. (2018). Multivariate functional principal component
  analysis for data observed on different (dimensional) domains.
  *Journal of the American Statistical Association*, 113(522), 649-659.

- Vovk, V., Gammerman, A. and Shafer, G. (2005). *Algorithmic Learning in a
  Random World*. Springer.

- Lei, J., G'Sell, M., Rinaldo, A., Tibshirani, R.J. and Wasserman, L. (2018).
  Distribution-free predictive inference for regression. *Journal of the
  American Statistical Association*, 113(523), 1094-1111.

- Ramsay, J.O. and Silverman, B.W. (2005). *Functional Data Analysis*.
  Springer, 2nd edition.
