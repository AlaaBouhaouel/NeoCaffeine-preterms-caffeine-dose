# neocaffeine

## Purpose
The Python package. Each subfolder has one responsibility in the chain from raw data to a dose suggestion for clinician review.

## Contents
- `clock/`: data clock and simulation clock; conversion between UTC timestamps and hours since birth.
- `registry/`: parameter registry data files, loader and validator.
- `patient/`: patient object, dose log, observation logs.
- `ingest/`: loading real patient records.
- `features/`: event detection, valid time, hourly records, pre-dose baseline.
- `maturity/`: independent maturity module producing M(t).
- `models/`: pharmacokinetics, maturity-adjusted baseline, Hill effect, expected apneas.
- `estimator/`: loss terms, Newton steps, recursive update.
- `decision/`: target concentration, dose, safety check.
- `simulator/`: virtual infants.
- `runner/`: the hourly loop for both modes.
- `evaluation/`: convergence, coverage, identifiability, dose quality.

## Inputs/Outputs
- Inputs: run configuration (`config/`), registry entries, patient records or virtual infants.
- Outputs: hourly parameter estimates with uncertainty, and dose suggestions with flags.

## Depends on
jax, ruamel.yaml, pint.

## Used by
- `tests/`
- `webapp/`
