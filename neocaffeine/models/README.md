# models

## Purpose
The forward model chain. From the dose log and the current parameters, computes the caffeine amount A(t) (one-compartment, closed form), the concentration C(t) = A/V, the maturity-adjusted baseline apnea rate lambda0(t), the Hill effect, the expected apnea count mu_k over the valid time of hour k, and the predicted blood level.

## Contents
No files yet.

## Inputs/Outputs
- Inputs: dose log, theta, M(t), baseline record, registry constants.
- Outputs: A(t), C(t), mu_k, predicted blood concentration.

## Depends on
- `neocaffeine/registry/`
- jax

## Used by
- `neocaffeine/estimator/`, `neocaffeine/decision/`, `neocaffeine/simulator/`
