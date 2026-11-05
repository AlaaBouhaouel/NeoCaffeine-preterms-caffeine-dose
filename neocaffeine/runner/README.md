# runner

## Purpose
The hourly loop, for both virtual-infant and real-data modes: for each new hour, runs features, maturity and the estimator, and at dosing times the decision. Checks the registry is complete before starting and records the registry version with every run.

## Contents
No files yet.

## Inputs/Outputs
- Inputs: run configuration, a patient object (from ingest or the simulator).
- Outputs: stored estimates, dose suggestions, run records.

## Depends on
- `neocaffeine/clock/`, `neocaffeine/registry/`, `neocaffeine/patient/`, `neocaffeine/ingest/`, `neocaffeine/features/`, `neocaffeine/maturity/`, `neocaffeine/models/`, `neocaffeine/estimator/`, `neocaffeine/decision/`, `neocaffeine/simulator/`
- `config/`

## Used by
- `neocaffeine/evaluation/`
- `webapp/`
