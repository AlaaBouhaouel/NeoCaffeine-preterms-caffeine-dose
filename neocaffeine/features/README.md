# features

## Purpose
Turns raw signals into what the rest of the system uses. Detects apnea, bradycardia and desaturation events (criteria from the registry), computes valid observation time and a data quality score, groups events into hourly records by onset time, computes the pre-dose baseline apnea rate, the hourly SpO2 summary from stable periods, and the hourly FiO2 and support-mode values. The estimator never sees raw signals.

## Contents
No files yet.

## Inputs/Outputs
- Inputs: raw-signal references and the context log from the patient object; event definitions from the registry.
- Outputs: event list, hourly records (N_k, bradycardia and desaturation counts, dt_valid, quality score, event-definition version), baseline record, hourly SpO2 and context values.

## Depends on
- `neocaffeine/patient/`, `neocaffeine/registry/`

## Used by
- `neocaffeine/maturity/`, `neocaffeine/runner/`
