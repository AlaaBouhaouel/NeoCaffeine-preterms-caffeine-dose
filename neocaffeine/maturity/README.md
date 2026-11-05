# maturity

## Purpose
Independent maturity module. Combines functional brain age, brain recording features, the SpO2/FiO2 ratio and breathing continuity into one maturity value M(t) per hour, in weeks. The estimator treats M(t) as given. How the inputs are combined is specified separately.

## Contents
No files yet.

## Inputs/Outputs
- Inputs: outputs of the features layer; registry entries.
- Outputs: M(t), one value per hour, in weeks.

## Depends on
- `neocaffeine/features/`, `neocaffeine/registry/`

## Used by
- `neocaffeine/models/`, `neocaffeine/runner/`
