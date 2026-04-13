---
title: Learn
---

# Learn

Welcome to the **fdars** learning hub. These guides walk you through the core
ideas of functional data analysis and show you how to apply them with fdars's
Python API.

!!! tip "Where to start"
    If you are new to FDA or fdars, begin with the **Introduction** -- it covers
    the mental model, data layout, and a complete first analysis.

---

## Guides

<div class="fdars-gallery" markdown>
<a class="fdars-gallery-item" href="introduction/">
<div class="fdars-gallery-title">Introduction to fdars</div>
<div class="fdars-gallery-desc">What is functional data analysis? Understand the core concepts, learn how
fdars represents curves as NumPy arrays, and run your first end-to-end
analysis.</div>
</a>
<a class="fdars-gallery-item" href="simulation/">
<div class="fdars-gallery-title">Simulation Toolbox</div>
<div class="fdars-gallery-desc">Generate realistic synthetic curves with Karhunen-Loeve expansions
(Fourier, polynomial, Wiener eigenfunctions) and Gaussian processes
(Gaussian, exponential, Matern, periodic kernels).</div>
</a>
<a class="fdars-gallery-item" href="smoothing/">
<div class="fdars-gallery-title">Smoothing</div>
<div class="fdars-gallery-desc">Remove noise while preserving structure. Covers Nadaraya-Watson,
local polynomial regression, k-NN smoothing, bandwidth selection via
cross-validation, and basis smoothing with P-splines.</div>
</a>
<a class="fdars-gallery-item" href="derivatives/">
<div class="fdars-gallery-title">Working with Derivatives</div>
<div class="fdars-gallery-desc">Compute first, second, and higher-order derivatives for 1D and 2D
functional data. Learn how to combine differentiation with smoothing
for stable estimates.</div>
</a>
</div>

---

## Suggested Reading Order

1. [Introduction to fdars](introduction.md) -- concepts and first steps
2. [Simulation Toolbox](simulation.md) -- generate data for experiments
3. [Smoothing](smoothing.md) -- prepare raw data for analysis
4. [Working with Derivatives](derivatives.md) -- extract rate-of-change information

After completing the Learn guides, explore the topic-specific sections:
**Represent**, **Align**, **Regression**, **Monitoring**, and **Analyze**.
