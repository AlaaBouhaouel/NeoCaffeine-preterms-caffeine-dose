# estimator

## Purpose
Recursive maximum a posteriori estimation, every hour. Builds the loss (Poisson apnea term, blood level term in log space, memory term, barrier term), loosens the memory for clearance drift, minimizes with Newton's method using JAX automatic differentiation, and takes the new uncertainty from the Hessian at the minimum (Laplace approximation).

## Contents
No files yet.

## Inputs/Outputs
- Inputs: hourly record, blood levels, previous estimate and uncertainty, registry priors and variabilities, run configuration (Newton and barrier settings).
- Outputs: theta_k and Sigma_k.

## Depends on
- `neocaffeine/models/`, `neocaffeine/registry/`
- jax

## Used by
- `neocaffeine/decision/`, `neocaffeine/runner/`, `neocaffeine/evaluation/`
